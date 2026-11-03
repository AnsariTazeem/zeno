"""Run reviewed public calibration references with project-local ngspice.

Upstream measurement code stays byte-exact. Our adapter changes path/transport,
rejects failed/incomplete simulations, and adds separately labelled tracking checks.
Only reviewed calibration netlists are accepted by this development entrypoint.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
sys.path[:0] = [str(BASE/"deps/python"), str(BASE/"upstream/benchmark")]
import config
import evaluate
from sim import SimError
from strict_measure import follower_metrics

SIM = ROOT / "tmp/ngspice47/ubuntu-local"
BINARY = SIM / "usr/bin/ngspice"
EXPECTED_BINARY_SHA = "820658317b0b54035208da41936fd6871ce924036e5ea4113a4168b821b7fc45"
CURRENT_SIMULATOR = None
NUMERICS = "upstream"
BAD_LOG = re.compile(r"(?im)^\s*error|timestep too small|doAnalyses:.*(?:failed|timestep)|convergence problem|fatal error|simulation interrupted|simulation aborted|segmentation fault")


def linux(path):
    text = Path(path).resolve().as_posix()
    match = re.fullmatch(r"([A-Za-z]):/(.*)", text)
    if not match:
        raise ValueError("This adapter requires an observed Windows workspace path")
    return f"/mnt/{match[1].lower()}/{match[2]}"


def run_solver(netlist, run_dir, name="tb", spiceinit=None, timeout=120):
    run_dir = Path(run_dir)
    if name not in ("opamp_loop", "opamp_tran"):
        raise SimError("Unreviewed testbench requested")
    if spiceinit != "set ngbehavior=hsa\nset ng_nomodcheck\n":
        raise SimError("Unexpected upstream startup configuration")
    run_dir.mkdir(parents=True, exist_ok=False)
    library = BASE/"deps/pdk/sky130A/libs.tech/combined/sky130.lib.spice"
    # This ngspice compatibility parser splits even quoted absolute .lib paths
    # at spaces. Keep all model lookup relative within this isolated workspace.
    relative_library = os.path.relpath(library, run_dir).replace("\\", "/")
    marker = '"__PUBLIC_SKY130_LIBRARY__"'
    if netlist.count(marker) != 1 or " " in relative_library:
        raise SimError("Unexpected model path marker")
    netlist = netlist.replace(marker, relative_library)
    if NUMERICS == "refined":
        # Refine only numerical settings, not the DUT or PDK. Preserve the
        # byte-exact upstream templates and retain the rendered deck per run.
        replacements = {".options reltol=1e-3 gmin=1e-12 vntol=1e-6 abstol=1e-12":
                        ".options reltol=1e-4 gmin=1e-12 vntol=1e-7 abstol=1e-13",
                        "option numdgt=7": "option numdgt=10"}
        replacements.update({"tran 10p 200n 0 10p": "tran 5p 200n 0 5p"} if name == "opamp_tran"
                            else {"ac dec 50 10 10G": "ac dec 100 10 10G"})
        for before, after in replacements.items():
            expected_count = 2 if before.startswith("ac dec") else 1
            if netlist.count(before) != expected_count:
                raise SimError("Unexpected testbench numerical configuration")
            netlist = netlist.replace(before, after)
    deck = run_dir / f"{name}.cir"
    deck.write_text(netlist, encoding="utf-8", newline="\n")
    # -n excludes user .spiceinit; the two reviewed upstream variables are explicit.
    if CURRENT_SIMULATOR is None:
        raise SimError("Simulator identity not selected")
    environment = os.environ.copy()
    if CURRENT_SIMULATOR['kind'] == 'windows41':
        command = [str(CURRENT_SIMULATOR['exe']), '-n', '-b', '-D', 'ngbehavior=hsa', '-D', 'ng_nomodcheck', deck.name]
        environment['SPICE_SCRIPTS'] = str(BASE/'sim_scripts')
    else:
        command = ["wsl.exe", "-d", "Ubuntu", "--cd", linux(run_dir), "--exec", "env",
                   "LD_LIBRARY_PATH="+linux(SIM/"usr/lib/x86_64-linux-gnu"),
                   "SPICE_SCRIPTS="+linux(BASE/"sim_scripts"), linux(BINARY),
                   "-n", "-b", "-D", "ngbehavior=hsa", "-D", "ng_nomodcheck", deck.name]
    launch = {"started_at_utc": datetime.now(timezone.utc).isoformat(), "command": command,
              "deck_sha256": hashlib.sha256(deck.read_bytes()).hexdigest(),
              "simulator_sha256": CURRENT_SIMULATOR['sha256'], "simulator_version": CURRENT_SIMULATOR['version'], "requested_spiceinit": spiceinit,
              "numerical_profile": NUMERICS,
              "startup_translation": "Reviewed hsa and ng_nomodcheck variables passed on CLI; local spinit sets one thread"}
    (run_dir/"launch.json").write_text(json.dumps(launch, indent=2)+"\n", encoding="utf-8")
    timed_out = False
    started = time.monotonic()
    with (run_dir/'stdout.txt').open('w',encoding='utf-8',newline='\n') as stdout, (run_dir/'stderr.txt').open('w',encoding='utf-8',newline='\n') as stderr:
        process = subprocess.Popen(command,cwd=run_dir,stdout=stdout,stderr=stderr,env=environment,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            process.wait(timeout=10)
    log = (run_dir/'stdout.txt').read_text(encoding='utf-8',errors='replace')+(run_dir/'stderr.txt').read_text(encoding='utf-8',errors='replace')
    (run_dir/f"{name}.log").write_text(log, encoding="utf-8", newline="\n")
    (run_dir/"completion.json").write_text(json.dumps({"returncode":process.returncode,"timed_out":timed_out,"fatal_log_match":bool(BAD_LOG.search(log)),"elapsed_seconds":time.monotonic()-started,"finished_at_utc":datetime.now(timezone.utc).isoformat()},indent=2)+"\n",encoding="utf-8")
    if timed_out or process.returncode != 0 or BAD_LOG.search(log):
        raise SimError(f"Failed simulation; inspect {run_dir}")
    if name == "opamp_tran":
        follower_metrics(run_dir/"tran.txt")  # coverage and command-tracking data validation
    else:
        import numpy as np
        data = np.loadtxt(run_dir/"stb.txt", skiprows=1, ndmin=2)
        if data.shape[1] != 3 or not np.isfinite(data).all() or np.any(np.diff(data[:,0]) <= 0):
            raise SimError("Invalid loop-gain export")
        if data[0,0] > 10.0001 or data[-1,0] < 1e10*(1-1e-6):
            raise SimError("Incomplete loop frequency sweep")
    return log


def main():
    global CURRENT_SIMULATOR, NUMERICS
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--reference", choices=("1v2","1v8","broken"), default="1v2")
    parser.add_argument("--vdd", type=float, default=1.2)
    parser.add_argument("--corner", choices=("tt","ff","ss","sf","fs"), default="tt")
    parser.add_argument('--simulator',choices=('windows41','wsl42'),default='windows41')
    parser.add_argument('--numerics',choices=('upstream','refined'),default='upstream')
    args = parser.parse_args()
    NUMERICS = args.numerics
    if not re.fullmatch(r"[A-Za-z0-9_]+", args.label):
        raise ValueError("Invalid run label")
    if args.simulator == 'windows41':
        sm=json.loads((BASE/'windows_simulator_manifest.json').read_text())
        executable=BASE/sm['exe']
        CURRENT_SIMULATOR={'kind':'windows41','version':'ngspice 41 (conda-forge Windows h295a5eb_0)','exe':executable,'sha256':sm['exe_sha256']}
    else:
        CURRENT_SIMULATOR={'kind':'wsl42','version':'ngspice 42 (Ubuntu 42+ds-3build1)','exe':BINARY,'sha256':EXPECTED_BINARY_SHA}
    if hashlib.sha256(CURRENT_SIMULATOR['exe'].read_bytes()).hexdigest() != CURRENT_SIMULATOR['sha256']:
        raise ValueError('Simulator binary changed')
    manifest = json.loads((BASE/"upstream_manifest.json").read_text())
    for item in manifest["files"]:
        if hashlib.sha256((BASE/"upstream"/item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Upstream snapshot changed")
    model_manifest = json.loads((BASE/"model_manifest.json").read_text())
    for item in model_manifest["files"]:
        if hashlib.sha256((BASE/"deps/pdk"/item["file"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Pinned public device model changed")
    build = BASE/"runs"/args.label
    if build.exists():
        raise FileExistsError("Use a fresh run label; never reuse old artifacts")
    build.mkdir(parents=True)
    identity = {"arguments": vars(args), "started_at_utc":datetime.now(timezone.utc).isoformat(),
                "python":sys.version,"simulator":{k:str(v) for k,v in CURRENT_SIMULATOR.items()},
                "own_code_sha256":{name:hashlib.sha256((BASE/name).read_bytes()).hexdigest()
                                   for name in ("run_reference.py","strict_measure.py")},
                "upstream_commit":manifest.get("commit"),
                "model_manifest_sha256":hashlib.sha256((BASE/"model_manifest.json").read_bytes()).hexdigest(),
                "models_verified":len(model_manifest["files"]),"ai_trials":0}
    (build/"run_identity.json").write_text(json.dumps(identity,indent=2)+"\n",encoding="utf-8")
    config.BUILD = build
    library = BASE/"deps/pdk/sky130A/libs.tech/combined/sky130.lib.spice"
    evaluate.TECHS["sky130_lvt"]["header"] = lambda corner: f'.lib "__PUBLIC_SKY130_LIBRARY__" {corner}'
    evaluate.run_ngspice = run_solver
    if args.reference == "broken":
        dut = BASE/"controls/broken.sp"
    else:
        dut = BASE/f"upstream/benchmark/golden/opamp_2stg_{args.reference}.sp"
    result = evaluate.evaluate("opamp_2stg", dut, "sky130_lvt", args.vdd, args.corner, label="reference")
    result["qualification_scope"] = "Public reference apparatus check, not an original task or AI trial"
    trace = Path(result["out_dir"])/"opamp_tran/tran.txt"
    if trace.exists() and not result["errors"]:
        strict = follower_metrics(trace)
        rules={"rise_settle_ns":12.24,"fall_settle_ns":26.73}
        strict["tracking_checks"]={name:strict[name] is not None and strict[name]<=limit for name,limit in rules.items()}
        result["independent_tracking_checks"] = strict
        result["strict_pass"] = result["pass"] and all(strict["tracking_checks"].values())
    else:
        result["strict_pass"] = False
    (build/"summary.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"label":args.label,"upstream_pass":result.get("pass"),"strict_pass":result["strict_pass"],"metrics":result["metrics"],"errors":result["errors"],"tracking":result.get("independent_tracking_checks")},indent=2))


if __name__ == "__main__":
    main()
