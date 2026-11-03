"""Future candidate entrypoint: verify the qualification seal, then compile/evaluate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('--label',required=True);p.add_argument('--refined',action='store_true')
a=p.parse_args()
freeze=json.loads((BASE/'qualification_freeze.json').read_text())
for item in freeze['files']:
    assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
command=[sys.executable,'-X','utf8',str(BASE/'qualify.py'),'evaluate','--candidate',str(a.candidate.resolve()),'--label',a.label]
if a.refined:
    command.append('--refined')
raise SystemExit(subprocess.run(command,creationflags=subprocess.CREATE_NO_WINDOW).returncode)
