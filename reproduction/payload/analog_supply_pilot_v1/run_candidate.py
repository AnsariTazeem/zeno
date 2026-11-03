"""Score a safely compiled candidate at the three disclosed supply points.

No inference calls. Candidate text never reaches ngspice without compilation.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import sys

BASE=Path(__file__).resolve().parent
APPARATUS=BASE.parent/"analog_public_v1"
sys.path.insert(0,str(APPARATUS))
import run_reference as ref
from strict_measure import follower_metrics
from circuit_input import compile_dut


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("candidate",type=Path)
    parser.add_argument("--label",required=True)
    parser.add_argument("--numerics",choices=("upstream","refined"),default="upstream")
    args=parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_]+",args.label):
        raise ValueError("Invalid label")
    out=BASE/"runs"/args.label
    if out.exists():
        raise FileExistsError("Use a fresh run label")
    compiled,counts=compile_dut(args.candidate.read_text(encoding="utf-8"))
    for manifest_name,root,key in (("upstream_manifest.json",APPARATUS/"upstream","path"),
                                    ("model_manifest.json",APPARATUS/"deps/pdk","file")):
        for item in json.loads((APPARATUS/manifest_name).read_text())["files"]:
            if sha(root/item[key])!=item["sha256"]:
                raise ValueError("Reference apparatus identity mismatch")
    sm=json.loads((APPARATUS/"windows_simulator_manifest.json").read_text())
    exe=APPARATUS/sm["exe"]
    if sha(exe)!=sm["exe_sha256"]:
        raise ValueError("Simulator identity mismatch")
    ref.CURRENT_SIMULATOR={"kind":"windows41","version":"ngspice 41 (conda-forge Windows h295a5eb_0)","exe":exe,"sha256":sm["exe_sha256"]}
    ref.NUMERICS=args.numerics
    out.mkdir(parents=True)
    (out/"candidate_original.sp").write_bytes(args.candidate.read_bytes())
    dut=out/"candidate_compiled.sp"
    dut.write_text(compiled,encoding="utf-8",newline="\n")
    identity={"started_at_utc":datetime.now(timezone.utc).isoformat(),"source_name":args.candidate.name,
              "original_sha256":sha(args.candidate),"compiled_sha256":sha(dut),"components":counts,
              "numerics":args.numerics,"simulator_sha256":sm["exe_sha256"],
              "code_sha256":{p.name:sha(p) for p in (Path(__file__),BASE/"circuit_input.py",APPARATUS/"run_reference.py",APPARATUS/"strict_measure.py")},
              "scope":"Development electrical verification; not automatically an AI trial"}
    (out/"identity.json").write_text(json.dumps(identity,indent=2)+"\n",encoding="utf-8")
    ref.config.BUILD=out
    ref.evaluate.TECHS["sky130_lvt"]["header"]=lambda corner: '.lib "__PUBLIC_SKY130_LIBRARY__" '+corner
    ref.evaluate.run_ngspice=ref.run_solver
    results=[]
    for label,vdd in (("v115",1.15),("v120",1.2),("v125",1.25)):
        result=ref.evaluate.evaluate("opamp_2stg",dut,"sky130_lvt",vdd,"tt",label=label)
        point={"vdd":vdd,"upstream_pass":result["pass"],"metrics":result["metrics"],"errors":result["errors"],
               "failed_checks":[c for c in result["checks"] if not c["pass"]]}
        trace=Path(result["out_dir"])/"opamp_tran/tran.txt"
        tracking=None
        try:
            if trace.exists():
                tracking=follower_metrics(trace)
        except ValueError as exc:
            point["trace_error"]=str(exc)
        point["command_tracking"]=tracking
        point["pass"]=(not result["errors"] and result["pass"] and tracking is not None and
                       all(tracking[k] is not None and tracking[k]<=bound for k,bound in
                           (("rise_settle_ns",12.24),("fall_settle_ns",26.73))) and
                       result["metrics"].get("input_current_uA",float("inf"))<=0.01)
        point["outcome_category"]="simulation_or_measurement_invalid" if result["errors"] else ("pass" if point["pass"] else "electrical_specification_failure")
        results.append(point)
        (out/"progress.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"completed_vdd":vdd,"pass":point["pass"],"category":point["outcome_category"]}),flush=True)
    report={"candidate":args.candidate.name,"all_points_pass":all(r["pass"] for r in results),
            "conditions":"TT, 27 C, VCM=0.9 V, CL=1 pF, Iref=20 uA, 0.2 V step",
            "points":results,"finished_at_utc":datetime.now(timezone.utc).isoformat()}
    (out/"result.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"all_points_pass":report["all_points_pass"],"label":args.label}),flush=True)


if __name__=="__main__":
    main()
