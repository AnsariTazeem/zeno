"""Contract-driven TIA acceptance; raw measurement validation stays in apparatus."""

import math


def finite(x):
    return isinstance(x, (float, int)) and not isinstance(x, bool) and math.isfinite(x)


def invalid(s):
    return {
        "category": "infrastructure_error",
        "success": None,
        "score": None,
        "error": s,
    }


def assess(data, contract):
    rows = data.get("cases")
    grid = {
        (x, y)
        for x in contract["sensor_capacitances_pF"]
        for y in contract["wire_capacitances_pF"]
    }
    if (
        data.get("outcome") == "simulation_or_measurement_invalid"
        or not isinstance(rows, list)
        or len(rows) != len(grid)
    ):
        return invalid("Incomplete/invalid TIA measurements")
    indexed = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("case"), dict):
            return invalid("Malformed sensor condition")
        key = (row["case"].get("sensor_pF"), row["case"].get("wire_pF"))
        if not all(finite(x) for x in key) or key not in grid or key in indexed:
            return invalid("Unexpected/duplicate sensor grid")
        indexed[key] = row
    result = []
    lim = contract["limits"]
    for key in sorted(grid):
        row = indexed[key]
        ac = row.get("ac")
        tr = row.get("transient")
        if not isinstance(ac, dict) or not isinstance(tr, dict):
            return invalid("Missing AC/transient section")
        names = [
            "dc_transimpedance_real_ohm",
            "dc_transimpedance_imag_ohm",
            "first_minus_3dB_Hz",
            "phase_at_low_frequency_deg",
            "low_frequency_loop_gain_dB",
            "dc_delivered_power_uW",
        ]
        if not all(finite(ac.get(k)) for k in names):
            return invalid("Missing/nonfinite AC metric")
        if ac["first_minus_3dB_Hz"] <= 0:
            return invalid("Invalid bandwidth crossing")
        f = ac.get("unity_downward_crossings_Hz")
        pm = ac.get("phase_margins_deg")
        if (
            not isinstance(f, list)
            or not isinstance(pm, list)
            or len(f) != len(pm)
            or not all(finite(x) and x > 0 for x in f)
            or not all(finite(x) for x in pm)
            or any(b <= a for a, b in zip(f, f[1:]))
        ):
            return invalid("Invalid loop crossing records")
        if not all(
            finite(tr.get(k))
            for k in ["initial_error_V", "rows", "stop_s", "max_retained_step_s"]
        ):
            return invalid("Missing/nonfinite transient metadata")
        if (
            tr["rows"] <= 100
            or tr["stop_s"] < contract["stop_s"] - 1e-15
            or not 0
            < tr["max_retained_step_s"]
            <= contract["numerics"]["baseline"]["maximum_transient_step_s"] + 2e-16
        ):
            return invalid("Truncated/invalid transient coverage")
        edges = tr.get("edges")
        if (
            not isinstance(edges, list)
            or len(edges) != 4
            or any(
                not isinstance(e, dict) or type(e.get("edge")) is not int for e in edges
            )
        ):
            return invalid("Expected four complete edge records")
        ordered = {e["edge"]: e for e in edges}
        if set(ordered) != {1, 2, 3, 4}:
            return invalid("Missing/duplicate edge")
        checks = []

        def add(name, value, op, limit, ok):
            checks.append(
                {
                    "metric": name,
                    "value": value,
                    "operator": op,
                    "limit": limit,
                    "pass": bool(ok),
                }
            )

        lo, hi = lim["transimpedance_real_at_10Hz_ohm"]
        add(
            "real_transimpedance_ohm",
            ac["dc_transimpedance_real_ohm"],
            "within",
            [lo, hi],
            lo <= ac["dc_transimpedance_real_ohm"] <= hi,
        )
        bound = lim["transimpedance_imag_at_10Hz_abs_max_ohm"]
        add(
            "imag_transimpedance_ohm",
            ac["dc_transimpedance_imag_ohm"],
            "absolute <=",
            bound,
            abs(ac["dc_transimpedance_imag_ohm"]) <= bound,
        )
        bound = lim["first_minus_3dB_bandwidth_min_Hz"]
        add(
            "first_minus_3dB_Hz",
            ac["first_minus_3dB_Hz"],
            ">=",
            bound,
            ac["first_minus_3dB_Hz"] >= bound,
        )
        bound = lim["loop_phase_at_10Hz_abs_less_than_deg"]
        add(
            "loop_phase_deg",
            ac["phase_at_low_frequency_deg"],
            "absolute <",
            bound,
            abs(ac["phase_at_low_frequency_deg"]) < bound and bool(f),
        )
        bound = lim["loop_gain_at_10Hz_greater_than_dB"]
        add(
            "loop_gain_dB",
            ac["low_frequency_loop_gain_dB"],
            ">",
            bound,
            ac["low_frequency_loop_gain_dB"] > bound,
        )
        bound = lim["all_downward_unity_crossing_phase_margins_min_deg"]
        add("all_phase_margins_deg", pm, "all >=", bound, bool(pm) and min(pm) >= bound)
        bound = lim["dc_positive_delivered_supply_and_reference_power_max_uW"]
        add(
            "delivered_power_uW",
            ac["dc_delivered_power_uW"],
            "0 < value <=",
            bound,
            0 < ac["dc_delivered_power_uW"] <= bound,
        )
        bound = lim["command_error_band_V"]
        add(
            "initial_error_V",
            tr["initial_error_V"],
            "absolute <=",
            bound,
            abs(tr["initial_error_V"]) <= bound,
        )
        for i, e in sorted(ordered.items()):
            expected = 0.7 if i % 2 else 0.9
            if e.get("target_V") != expected or "settle_ns" not in e:
                return invalid("Wrong target/missing settling field")
            s = e["settle_ns"]
            o = e.get("overshoot_V")
            if (
                (s is not None and (not finite(s) or s < 0))
                or not finite(o)
                or o < 0
                or not finite(e.get("endpoint_error_V"))
            ):
                return invalid("Invalid edge metric")
            bound = lim["each_edge_settle_max_ns"]
            add(f"edge{i}_settle_ns", s, "<=", bound, s is not None and s <= bound)
            bound = lim["each_edge_overshoot_max_V"]
            add(f"edge{i}_overshoot_V", o, "<=", bound, o <= bound)
        result.append(
            {
                "condition": f"Csensor={key[0]}pF, Cwire={key[1]}pF",
                "case": row["case"],
                "checks": checks,
                "pass": all(c["pass"] for c in checks),
            }
        )
    success = all(p["pass"] for p in result)
    return {
        "category": "pass" if success else "specification_failure",
        "score": 100 if success else 0,
        "success": success,
        "points": result,
    }
