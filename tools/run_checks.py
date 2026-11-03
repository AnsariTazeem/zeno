"""Verify the frozen kit and run offline regressions; no inference/simulation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT / 'reproduction'
PAYLOAD = KIT / 'payload'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError('Use Windows x64 Python 3.12 as documented')
    import numpy
    if numpy.__version__ != '2.3.5':
        raise RuntimeError('Use the pinned NumPy 2.3.5 environment')
    import zstandard
    if zstandard.__version__ != '0.25.0':
        raise RuntimeError('Use the pinned zstandard 0.25.0 environment')
    records = read(KIT / 'kit_manifest.json')['files']
    for row in records:
        path = (KIT / row['path']).resolve()
        if not path.is_relative_to(KIT.resolve()):
            raise ValueError('Manifest path escapes source kit')
        if path.stat().st_size != row['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Frozen file changed: '+row['path'])
    log_parent = ROOT / '.local-checks'
    log_parent.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='offline_', dir=log_parent))
    suites = [('bootstrap_boundaries',PAYLOAD/'checks/test_bootstrap.py',8),
              ('grading_regressions',PAYLOAD/'eval_core_v4/test_core.py',30),
              ('supply_evidence',PAYLOAD/'eval_core_v4/test_supply_evidence.py',12),
              ('repository_layout',ROOT/'tests/test_repository_layout.py',7)]
    checks=[]
    for label, path, count in suites:
        command = [sys.executable,'-I','-B','-c',
            "import runpy,sys; sys.path.insert(0,sys.argv[1]); p=sys.argv[2]; sys.argv=[p]; runpy.run_path(p,run_name='__main__')",
            str(path.parent),str(path)]
        result = subprocess.run(command,cwd=ROOT,capture_output=True,timeout=120)
        (output/(label+'_stdout.txt')).write_bytes(result.stdout)
        (output/(label+'_stderr.txt')).write_bytes(result.stderr)
        stderr=result.stderr.decode('utf-8',errors='replace')
        match=re.search(r'Ran (\d+) tests? in ',stderr)
        observed=int(match.group(1)) if match else None
        passed=result.returncode==0 and observed==count and stderr.rstrip().endswith('OK')
        checks.append({'suite':label,'returncode':result.returncode,'expected_tests':count,
                       'observed_tests':observed,'passed':passed})
    report={'at_utc':datetime.now(timezone.utc).isoformat(),
            'outcome':'passed' if all(c['passed'] for c in checks) else 'failed',
            'verified_frozen_files':len(records),'tests_passed':sum(c['observed_tests'] for c in checks if c['passed']),
            'checks':checks,'model_calls':0,'simulator_calls':0,
            'scope':'Offline regression checks on existing host; not native or independent-machine qualification'}
    (output/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({**report,'logs':str(output)},indent=2))
    return 0 if report['outcome']=='passed' else 1


if __name__=='__main__':
    raise SystemExit(main())
