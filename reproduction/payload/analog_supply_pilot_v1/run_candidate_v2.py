"""Future-task entrypoint: geometry preflight before the unchanged simulator runner."""
from datetime import datetime,timezone
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from circuit_input import InvalidCircuit
from geometry_domain_v2 import compile_supported_dut

BASE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument("candidate",type=Path)
parser.add_argument("--label",required=True)
parser.add_argument("--numerics",choices=("upstream","refined"),default="upstream")
args=parser.parse_args()
if not re.fullmatch(r"[A-Za-z0-9_]+",args.label):
    raise ValueError("Invalid label")
receipt=BASE/"geometry_checks"/(args.label+".json")
if receipt.exists() or (BASE/"runs"/args.label).exists():
    raise FileExistsError("Preserve prior run")
body=args.candidate.read_bytes()
record={"started_at_utc":datetime.now(timezone.utc).isoformat(),
        "candidate_sha256":hashlib.sha256(body).hexdigest(),
        "guard_sha256":hashlib.sha256((BASE/"geometry_domain_v2.py").read_bytes()).hexdigest(),
        "domain_manifest_sha256":hashlib.sha256((BASE/"model_domain_v2.json").read_bytes()).hexdigest()}
try:
    compile_supported_dut(body.decode("utf-8"))
    record["geometry_supported"]=True
except InvalidCircuit as exc:
    record.update({"geometry_supported":False,"input_error":str(exc),"simulator_launched":False})
receipt.parent.mkdir(exist_ok=True)
receipt.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
if not record["geometry_supported"]:
    print(json.dumps(record,indent=2))
    raise SystemExit(2)
# The unchanged runner records its own simulator/model/code identities and data.
command=[sys.executable,"-X","utf8",str(BASE/"run_candidate.py"),str(args.candidate.resolve()),
         "--label",args.label,"--numerics",args.numerics]
result=subprocess.run(command,creationflags=subprocess.CREATE_NO_WINDOW)
raise SystemExit(result.returncode)
