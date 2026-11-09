"""Run frozen grading tests and native controls in a prepared source kit."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "qualification"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    body = json.dumps(data, indent=2, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8") as handle:
        handle.write(body)


def run(label, command, timeout=1000):
    started = time.monotonic()
    with (OUT / (label + "_stdout.txt")).open("xb") as stdout, (
        OUT / (label + "_stderr.txt")
    ).open("xb") as stderr:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=stdout,
            stderr=stderr,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                timeout=20,
            )
            process.wait(timeout=20)
            raise RuntimeError(label + " timed out; retained as infrastructure failure")
    return {
        "label": label,
        "returncode": code,
        "elapsed_seconds": time.monotonic() - started,
        "command": command,
    }


def compare_measurements(actual, expected):
    """Compare classification and every reported check value, including lists/nulls."""
    if len(actual) != len(expected):
        raise ValueError("Operating-point counts differ")
    deltas = []

    def compare_value(value, reference, location):
        if isinstance(reference, list):
            if not isinstance(value, list) or len(value) != len(reference):
                raise ValueError("Measurement shape differs: " + location)
            for index, (child, original) in enumerate(zip(value, reference)):
                compare_value(child, original, location + "[" + str(index) + "]")
        elif isinstance(reference, (int, float)) and (not isinstance(reference, bool)):
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or (not math.isfinite(value))
                or (not math.isfinite(reference))
                or (not math.isclose(value, reference, rel_tol=1e-06, abs_tol=1e-09))
            ):
                raise ValueError("Measurement differs beyond tolerance: " + location)
            deltas.append(
                {"metric": location, "absolute_delta": abs(value - reference)}
            )
        elif type(value) is not type(reference) or value != reference:
            raise ValueError("Measurement differs: " + location)

    for point, original in zip(actual, expected):
        if (
            point["condition"] != original["condition"]
            or point["pass"] != original["pass"]
        ):
            raise ValueError("Operating-point classification differs")
        if len(point["checks"]) != len(original["checks"]):
            raise ValueError("Check counts differ")
        for check, old in zip(point["checks"], original["checks"]):
            if any(
                (
                    check.get(key) != old.get(key)
                    for key in ("metric", "operator", "limit", "pass", "reason")
                )
            ):
                raise ValueError("Check classification differs")
            compare_value(
                check["value"], old["value"], point["condition"] + "/" + check["metric"]
            )
    return deltas


def main():
    if sys.flags.optimize:
        raise RuntimeError("Run qualification without Python optimization")
    OUT.mkdir(exist_ok=False)
    result = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "outcome": "incomplete",
        "model_calls": 0,
        "runs": [],
        "scope": "Fresh venv/download test on this Windows host; not a fresh OS or independent machine",
    }
    try:
        if not Path(sys.prefix).resolve() == (ROOT / ".venv").resolve():
            raise ValueError("Use the new environment Python")
        if (
            not "include-system-site-packages = false"
            in (ROOT / ".venv/pyvenv.cfg").read_text()
        ):
            raise ValueError("Qualification validation failed")
        import numpy

        if not numpy.__version__ == "2.3.5":
            raise ValueError("Qualification validation failed")
        if not Path(numpy.__file__).resolve().is_relative_to(ROOT / ".venv"):
            raise ValueError("Qualification validation failed")
        result["environment"] = {
            "python": sys.version,
            "executable": sys.executable,
            "isolated": bool(sys.flags.isolated),
            "numpy_origin": numpy.__file__,
            "numpy_version": numpy.__version__,
            "venv_configuration": (ROOT / ".venv/pyvenv.cfg").read_text(),
        }
        if not sys.flags.isolated:
            raise ValueError("Qualification validation failed")
        spec = importlib.util.spec_from_file_location(
            "qualified_core", ROOT / "eval_core_v6/run_eval.py"
        )
        core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core)
        core.verify()
        for label, script in [
            ("bootstrap_adversarial", ROOT / "checks/test_bootstrap.py"),
            ("frozen_regressions", ROOT / "eval_core_v6/test_core.py"),
            (
                "supply_evidence_regressions",
                ROOT / "eval_core_v6/test_supply_evidence.py",
            ),
        ]:
            launcher = "import sys,runpy; sys.path.insert(0,sys.argv[1]); script=sys.argv[2]; sys.argv=[script]; runpy.run_path(script,run_name='__main__')"
            entry = run(
                label,
                [
                    sys.executable,
                    "-I",
                    "-B",
                    "-c",
                    launcher,
                    str(script.parent),
                    str(script),
                ],
                120,
            )
            result["runs"].append(entry)
            if not entry["returncode"] == 0:
                raise ValueError(label)
        print("Bootstrap adversarial and frozen grading tests passed", flush=True)
        cases = read(ROOT / "checks/controls.json")["controls"]
        if not len({(c["task"], c["label"]) for c in cases}) == len(cases):
            raise ValueError("Duplicate task/run identifier")

        def native(case):
            label = case["label"]
            log_label = case["task"] + "_" + label
            print("Starting native control: " + log_label, flush=True)
            command = [
                sys.executable,
                "-I",
                "-B",
                str(ROOT / "eval_core_v6/run_eval.py"),
                "evaluate",
                "--task",
                case["task"],
                "--candidate",
                str(ROOT / case["candidate"]),
                "--run-id",
                label,
            ]
            entry = run(log_label, command)
            folder = ROOT / "eval_core_v6/runs" / case["task"] / label
            common = read(folder / "result.json")
            if not (
                entry["returncode"] == 0 and common["category"] == case["category"]
            ):
                raise ValueError(label)
            if not (
                common["model_calls"] == 0
                and common["evidence_mode"] == "fresh_native_simulation"
            ):
                raise ValueError("Qualification validation failed")
            expected = core.assess(
                case["task"],
                read(ROOT / case["expected_native"]),
                read(ROOT / core.TASKS[case["task"]]["public"] / "contract.json"),
                native_dir=(
                    ROOT / case["expected_native_directory"]
                    if case.get("expected_native_directory")
                    else None
                ),
            )
            if not expected["category"] == common["category"]:
                raise ValueError("Qualification validation failed")
            if (
                not len(common["points"])
                == len(expected["points"])
                == case["conditions"]
            ):
                raise ValueError("Qualification validation failed")
            deltas = compare_measurements(common["points"], expected["points"])
            completions = list((folder / "native").rglob("completion.json"))
            if not len(completions) == case["native_processes"]:
                raise ValueError("Qualification validation failed")
            for path in completions:
                done = read(path)
                if not (
                    done["returncode"] == 0
                    and (not done["timed_out"])
                    and (not done["fatal_log_match"])
                ):
                    raise ValueError("Qualification validation failed")
            for row in read(folder / "manifest.json")["files"]:
                if not sha(folder / row["path"]) == row["sha256"]:
                    raise ValueError("Qualification validation failed")
            entry.update(
                {
                    "category": common["category"],
                    "conditions": len(common["points"]),
                    "passing_conditions": sum((p["pass"] for p in common["points"])),
                    "native_processes": len(completions),
                    "all_check_classifications_reproduced": True,
                    "metric_deltas": deltas,
                    "numeric_relative_tolerance": 1e-06,
                    "numeric_absolute_tolerance": 1e-09,
                    "candidate_sha256": common["candidate_sha256"],
                    "result_sha256": sha(folder / "result.json"),
                }
            )
            write(OUT / (log_label + "_comparison.json"), entry)
            print(
                "Completed native control: " + log_label + " -> " + common["category"],
                flush=True,
            )
            return entry

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(native, case) for case in cases]
            errors = []
            for future in as_completed(futures):
                try:
                    result["runs"].append(future.result())
                except Exception as error:
                    errors.append(type(error).__name__ + ": " + str(error))
            if errors:
                raise RuntimeError("; ".join(errors))
        result["verified_runtime_files_after_runs"] = core.verify()
        result["outcome"] = "fresh_venv_controls_reproduced_on_existing_host"
    except Exception as error:
        result["outcome"] = "qualification_incomplete"
        result["error"] = type(error).__name__ + ": " + str(error)
    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    write(OUT / "result.json", result)
    files = []
    for folder in [OUT, ROOT / "eval_core_v6/runs"]:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                files.append(
                    {
                        "path": str(path.relative_to(ROOT)),
                        "bytes": path.stat().st_size,
                        "sha256": sha(path),
                    }
                )
    write(OUT / "artifact_manifest.json", {"files": files})
    print(
        json.dumps(
            {k: v for k, v in result.items() if k not in ["runs", "environment"]},
            indent=2,
        ),
        flush=True,
    )
    return (
        0
        if result["outcome"] == "fresh_venv_controls_reproduced_on_existing_host"
        else 3
    )


if __name__ == "__main__":
    raise SystemExit(main())
