"""Prepare a separately versioned public packet; never alter trial02's task."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
OUT=BASE/"public_v2"
if OUT.exists():
    raise FileExistsError("Preserve prepared packet")
old=json.loads((BASE/"trials/trial02/freeze.json").read_text())
for entry in old["files"]:
    assert hashlib.sha256((ROOT/entry["path"]).read_bytes()).hexdigest()==entry["sha256"]
needle="W/L are literal numbers in micrometres, W=1..1000, L=0.15..10; nf=1 and integer m=1..100."
replacement=("W/L are literal numbers in micrometres. For both models W=1..1000; "
             "NMOS L=0.15..10 and PMOS L=0.35..10, inclusive; nf=1 and integer m=1..100. "
             "These model-specific length limits are required by the pinned simulation model bins. "
             "Unsupported geometry is rejected by preflight before electrical simulation.")
prepared={}
for name in ("TASK.md","PROMPT.txt"):
    text=(BASE/"public"/name).read_text(encoding="utf-8")
    assert text.count(needle)==1
    text=text.replace(needle,replacement)
    text=text.replace("# SUPPLY-P01: repair an amplifier for three supply conditions",
                      "# SUPPLY-P01 development-2: repair an amplifier for three supply conditions",1)
    prepared[name]=text.encode("utf-8")
for name in ("starter.sp","LICENSE_UPSTREAM.txt"):
    prepared[name]=(BASE/"public"/name).read_bytes()
contract=json.loads((BASE/"public/contract.json").read_text())
contract["version"]="development-2-model-domain-corrected"
contract["geometry"]=json.loads((BASE/"model_domain_v2.json").read_text())["corrected_bounds"]
contract["geometry_preflight"]="run_candidate_v2.py; source-bound model_domain_v2.json"
prepared["contract.json"]=(json.dumps(contract,indent=2)+"\n").encode("utf-8")
OUT.mkdir()
for name,body in prepared.items():
    (OUT/name).write_bytes(body)
paths=[*sorted(OUT.iterdir()),BASE/"run_candidate_v2.py",BASE/"geometry_domain_v2.py",
       BASE/"model_domain_v2.json",BASE/"test_geometry_domain_v2.py",BASE/"prepare_domain_v2.py",
       *[ROOT/e["path"] for e in old["files"] if not e["path"].startswith("analog_supply_pilot_v1/public/")]]
records=[{"path":p.relative_to(ROOT).as_posix(),"bytes":p.stat().st_size,
          "sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
freeze={"frozen_at_utc":datetime.now(timezone.utc).isoformat(),"task_id":"SUPPLY-P01",
        "version":contract["version"],"files":records,
        "source_trial02_unchanged":True,"electrical_requirements_unchanged":True,
        "new_model_trial_started":False,"previous_proposal03_repaired":False,
        "future_protocol":"Fresh conversation and separate denominator; at most three complete proposals; stop on verified pass"}
(BASE/"domain_v2_freeze.json").write_text(json.dumps(freeze,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"prepared":str(OUT),"files_frozen":len(records),"model_calls":0},indent=2))
