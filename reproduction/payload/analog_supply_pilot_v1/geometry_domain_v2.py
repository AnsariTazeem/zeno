"""Source-bound device-geometry guard for future corrected task versions."""
import hashlib
import json
from pathlib import Path
from circuit_input import compile_dut,InvalidCircuit

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
MANIFEST=BASE/"model_domain_v2.json"

def compile_supported_dut(text):
    compiled,counts=compile_dut(text)
    domain=json.loads(MANIFEST.read_text())
    models=domain["models"]
    for entry in models.values():
        if hashlib.sha256((ROOT/entry["source"]).read_bytes()).hexdigest()!=entry["sha256"]:
            raise InvalidCircuit("Pinned geometry-model source changed")
    unsupported=[]
    for line in compiled.splitlines():
        t=line.lower().split()
        if not t or not t[0].startswith("x"):
            continue
        p=dict(token.split("=",1) for token in t[6:])
        w,l=float(p["w"]),float(p["l"])
        bins=models[t[5]]["bins"]
        eps=1e-10
        if not any(b["wmin_um"]-eps<=w<=b["wmax_um"]+eps and b["lmin_um"]-eps<=l<=b["lmax_um"]+eps for b in bins):
            unsupported.append(f"{t[0]} ({t[5]}, W={w:g}, L={l:g} um)")
    if unsupported:
        raise InvalidCircuit("No supported pinned-model geometry bin: "+", ".join(unsupported)+
                             ". Corrected task requires NMOS L>=0.15 um and PMOS L>=0.35 um.")
    return compiled,counts
