"""Fail-closed transient checks for our declared follower task contract."""
from pathlib import Path
import numpy as np


class InvalidTrace(ValueError):
    pass


def load_trace(path, stop_s=200e-9):
    path = Path(path)
    with path.open(encoding="utf-8") as f:
        names = f.readline().lower().split()
    required = ("time", "v(nin)", "v(nout)", "i(vsup)")
    if tuple(names) != required:
        raise InvalidTrace(f"Unexpected transient columns: {names}")
    data = np.loadtxt(path, skiprows=1, ndmin=2)
    if data.shape[1] != len(names) or len(data) < 4 or not np.isfinite(data).all():
        raise InvalidTrace("Missing, malformed or nonfinite transient data")
    t = data[:, 0]
    if np.any(np.diff(t) <= 0):
        raise InvalidTrace("Transient time must increase strictly")
    # At the reviewed 7-decimal scientific export precision, timestamps near
    # 200 ns round in 10 fs units. Two rounded endpoints can therefore make a
    # true 10 ps solver step appear up to 10 fs larger. This allowance concerns
    # text quantization only; the simulator's physical maximum stays 10 ps.
    if np.diff(t).max() > 10e-12 + 10e-15 + 1e-18:
        raise InvalidTrace("Transient gap exceeds 10 ps plus the 10 fs export-rounding allowance")
    if abs(t[0]) > 1e-15 or t[-1] < stop_s - 1e-15:
        raise InvalidTrace(f"Incomplete transient: {t[0]} to {t[-1]}, expected 0 to {stop_s}")
    return {name: data[:, i] for i, name in enumerate(names)}


def follower_metrics(path, vcm=0.9, step=0.2, stop_s=200e-9):
    d = load_trace(path, stop_s)
    t, vin, out = d["time"], d["v(nin)"], d["v(nout)"]
    result = {}
    for label, t0, t1, target in (("rise", 5e-9, 55e-9, vcm+step/2), ("fall", 55e-9, 105e-9, vcm-step/2)):
        # Exclude the next edge despite sub-femtosecond text/float rounding.
        mask = (t >= t0-1e-15) & (t < t1-1e-15)
        tt, vi, yy = t[mask], vin[mask], out[mask]
        if len(tt) < 3 or tt[0]-t0 > 11e-12 or t1-tt[-1] > 11e-12:
            raise InvalidTrace(f"{label}: incomplete measurement window")
        if abs(vi[-1]-target) > 1e-7:
            raise InvalidTrace(f"{label}: source does not reach declared command")
        outside = np.flatnonzero(np.abs(yy-target) > 0.01*abs(step))
        if not len(outside):
            settled = 0.0
        elif outside[-1]+1 >= len(tt):
            settled = None
        else:
            settled = float((tt[outside[-1]+1]-t0)*1e9)
        result[f"{label}_settle_ns"] = settled
        result[f"{label}_endpoint_error_V"] = float(yy[-1]-target)
    result["observed_stop_s"] = float(t[-1])
    result["max_retained_step_s"] = float(np.diff(t).max())
    result["measured_rows"] = len(t)
    return result
