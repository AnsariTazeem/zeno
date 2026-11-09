"""Evidence-aware supply grading: absent crossover is not missing trace data."""

from pathlib import Path
import hashlib
import json
import math
import sys
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analog_public_v1"))
from strict_measure import follower_metrics


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite(value):
    return (
        isinstance(value, (int, float))
        and (not isinstance(value, bool))
        and math.isfinite(value)
    )


def invalid(message):
    return {
        "category": "infrastructure_error",
        "score": None,
        "success": None,
        "error": message,
    }


def raw_witnesses(data, native, contract):
    """Verify complete native artifacts, then certify a narrow no-gain case.

    No invented numerical substitute for undefined UGF/PM/GM is returned.
    A complete sweep with a unity crossing but no -180 crossing certifies
    gm_dB as no_finite_crossover_in_sweep (pass). Other undefined-crossing
    cases remain unresolved by this version.
    """
    if not read(native / "result.json") == data:
        raise ValueError("Native result/input mismatch")
    identity = read(native / "identity.json")
    if not sha(native / "candidate_original.sp") == identity["original_sha256"]:
        raise ValueError("Candidate identity mismatch")
    expected_simulator = read(
        ROOT / "analog_public_v1/windows_simulator_manifest.json"
    )["exe_sha256"]
    points = data.get("points")
    if not (isinstance(points, list) and len(points) == len(contract["supplies_V"])):
        raise ValueError("Incomplete grid")
    if not all((isinstance(p, dict) and finite(p.get("vdd")) for p in points)):
        raise ValueError("Invalid grid")
    if not len({p["vdd"] for p in points}) == len(points):
        raise ValueError("Duplicate grid")
    if not {p["vdd"] for p in points} == set(contract["supplies_V"]):
        raise ValueError("Wrong grid")
    witnesses = {}
    for point in points:
        vdd = point["vdd"]
        label = {1.15: "v115", 1.2: "v120", 1.25: "v125"}[vdd]
        base = native / "eval/opamp_2stg" / label
        for bench in ["opamp_loop", "opamp_tran"]:
            folder = base / bench
            completion = read(folder / "completion.json")
            if not (
                completion["returncode"] == 0
                and (not completion["timed_out"])
                and (not completion["fatal_log_match"])
            ):
                raise ValueError("Failed native process")
            launch = read(folder / "launch.json")
            if not launch["simulator_sha256"] == expected_simulator:
                raise ValueError("Wrong simulator")
            if not sha(folder / (bench + ".cir")) == launch["deck_sha256"]:
                raise ValueError("Deck identity mismatch")
        if not (point.get("errors") == [] and (not point.get("trace_error"))):
            raise ValueError("Native measurement errors")
        if (
            not follower_metrics(base / "opamp_tran/tran.txt")
            == point["command_tracking"]
        ):
            raise ValueError("Transient extraction mismatch")
        loop = base / "opamp_loop"
        with (loop / "stb.txt").open(encoding="utf-8") as handle:
            header = handle.readline().split()
        if not header == ["frequency", "lg_db", "lg_ph"]:
            raise ValueError("Wrong loop columns")
        values = np.loadtxt(loop / "stb.txt", skiprows=1, ndmin=2)
        if not (values.shape[1] == 3 and np.isfinite(values).all()):
            raise ValueError("Invalid loop array")
        f, db, phase = values.T
        profile = read(loop / "launch.json")["numerical_profile"]
        count = {"upstream": 451, "refined": 901}[profile]
        if not (len(f) == count and np.all(f > 0) and np.all(np.diff(f) > 0)):
            raise ValueError("Incomplete loop sweep")
        if not np.allclose(np.log10(f), np.linspace(1, 10, count), rtol=0, atol=1e-07):
            raise ValueError("Wrong frequency coverage")
        m = point["metrics"]
        if not (
            finite(m.get("dc_gain_dB"))
            and abs(float(db[0]) - m["dc_gain_dB"]) <= 0.00501
        ):
            raise ValueError("Gain extraction mismatch")
        unity = bool(np.any((db[:-1] > 0) & (db[1:] <= 0)))
        relative_phase = phase - phase[0]
        phase180 = bool(
            np.any((relative_phase[:-1] > -180) & (relative_phase[1:] <= -180))
        )
        certified = float(np.max(db)) < -0.001 and (not unity)
        gm_no_finite_crossover = bool(unity and (not phase180))
        if certified:
            if not (
                m.get("ugf_Hz", "missing") is None
                and m.get("pm_deg", "missing") is None
            ):
                raise ValueError("Unexpected crossover metadata")
            if not m.get("gm_dB", "missing") is None:
                raise ValueError("Unexpected upstream GM metadata")
        witnesses[vdd] = {
            "all_loop_gain_below_zero_certified": bool(certified),
            "gm_no_finite_crossover": bool(gm_no_finite_crossover),
            "observed_rows": len(f),
            "minimum_loop_gain_dB": float(np.min(db)),
            "maximum_loop_gain_dB": float(np.max(db)),
            "unity_downward_crossing_present": unity,
            "relative_phase180_downward_crossing_present": phase180,
            "raw_loop_sha256": sha(loop / "stb.txt"),
            "raw_transient_sha256": sha(base / "opamp_tran/tran.txt"),
            "method": "Complete finite pinned native sweeps plus unchanged tracking re-extraction",
        }
    return witnesses


def assess(data, contract, native_dir=None):
    witnesses = {}
    if native_dir is not None:
        try:
            witnesses = raw_witnesses(data, Path(native_dir), contract)
        except Exception as error:
            return invalid(
                "Raw-evidence validation: " + type(error).__name__ + ": " + str(error)
            )
    points = data.get("points")
    if not isinstance(points, list) or len(points) != len(contract["supplies_V"]):
        return invalid("Incomplete operating grid")
    if any((not isinstance(p, dict) or not finite(p.get("vdd")) for p in points)):
        return invalid("Malformed operating grid")
    by_supply = {p["vdd"]: p for p in points}
    if len(by_supply) != len(points) or set(by_supply) != set(contract["supplies_V"]):
        return invalid("Unexpected/duplicate operating grid")
    results = []
    for vdd in contract["supplies_V"]:
        point = by_supply[vdd]
        if (
            not isinstance(point.get("errors"), list)
            or point["errors"]
            or point.get("trace_error")
            or (point.get("outcome_category") == "simulation_or_measurement_invalid")
        ):
            return invalid("Invalid operating-point measurements")
        metrics, tracking = (point.get("metrics"), point.get("command_tracking"))
        if not isinstance(metrics, dict) or not isinstance(tracking, dict):
            return invalid("Missing measurement section")
        coverage = ["observed_stop_s", "max_retained_step_s", "measured_rows"]
        if (
            not all((finite(tracking.get(k)) for k in coverage))
            or tracking["observed_stop_s"] < contract["observation_s"] - 1e-15
            or (not 0 < tracking["max_retained_step_s"] <= 1e-11 + 1e-14 + 1e-18)
            or (tracking["measured_rows"] < 4)
        ):
            return invalid("Invalid retained trace coverage")
        certified = witnesses.get(vdd, {}).get(
            "all_loop_gain_below_zero_certified", False
        )
        gm_no_finite_crossover = witnesses.get(vdd, {}).get(
            "gm_no_finite_crossover", False
        )
        checks = []
        for metric, rule in contract["limits"].items():
            is_tracking = metric.startswith("command_")
            key = metric.removeprefix("command_") if is_tracking else metric
            source = tracking if is_tracking else metrics
            value = source.get(key)
            undefined_failure = value is None and (
                is_tracking
                or (certified and metric in ["ugf_Hz", "pm_deg", "gm_dB"])
                or (metric == "gm_dB" and gm_no_finite_crossover)
            )
            if key not in source or (not finite(value) and (not undefined_failure)):
                return invalid("Missing/nonfinite measurement: " + metric)
            op, limit = next(iter(rule.items()))
            if metric == "gm_dB" and value is None and gm_no_finite_crossover:
                ok = True
                gm_reason = "no_finite_crossover_in_sweep"
            else:
                ok = value is not None and (
                    value >= limit if op == ">=" else value <= limit
                )
                gm_reason = None
            check = {
                "metric": metric,
                "value": value,
                "operator": op,
                "limit": limit,
                "pass": ok,
            }
            if certified and value is None and (not is_tracking):
                check["reason"] = (
                    "Undefined crossing metric with complete raw evidence of loop gain below unity; required measurement does not pass"
                )
            elif gm_reason is not None:
                check["reason"] = gm_reason
            checks.append(check)
        results.append(
            {
                "vdd": vdd,
                "condition": f"VDD={vdd}V",
                "pass": all((c["pass"] for c in checks)),
                "checks": checks,
                "metrics": metrics,
                "command_tracking": tracking,
                "raw_witness": witnesses.get(vdd),
            }
        )
    success = all((point["pass"] for point in results))
    return {
        "category": "pass" if success else "specification_failure",
        "success": success,
        "score": 100 if success else 0,
        "points": results,
        "raw_evidence_checked": native_dir is not None,
    }
