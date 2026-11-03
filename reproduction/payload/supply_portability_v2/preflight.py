"""Windows-only fail-fast checks around the unchanged SUPPLY development runner.

No inference, installer, network access or task/grader modification. The 140
character run-directory budget is conservative local policy, not a Windows
API limit or proof of universal compatibility. Native parsing is also tested.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import struct
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
MAX_RUN_DIR_CHARS=140
BAD_LOG=re.compile(r"(?im)^\s*error|timestep too small|doAnalyses:.*(?:failed|timestep)|convergence problem|fatal error|simulation interrupted|simulation aborted|segmentation fault")

class PreflightError(Exception):
    def __init__(self,category,message):
        self.category=category
        super().__init__(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def safe_path(root,relative):
    rel=PurePosixPath(relative.replace('\\','/'))
    if rel.is_absolute() or not rel.parts or '..' in rel.parts or ':' in relative:
        raise PreflightError('unsafe_dependency_path','Unsafe path in dependency lock')
    target=(root/Path(*rel.parts)).resolve()
    if not target.is_relative_to(root.resolve()):
        raise PreflightError('unsafe_dependency_path','Dependency escapes workspace')
    return target

def validate_label(label):
    if not re.fullmatch(r'[A-Za-z0-9_]{1,32}',label):
        raise PreflightError('invalid_run_label','Use 1-32 letters, digits or underscores')

def planned_directory(root,label,namespace='runs'):
    validate_label(label)
    return root/'analog_supply_pilot_v1'/namespace/label/'eval/opamp_2stg/v115/opamp_loop'

def validate_layout(root,label):
    planned=planned_directory(root,label)
    if len(str(planned))>MAX_RUN_DIR_CHARS:
        raise PreflightError('path_budget_exceeded',
            f'Planned native run directory has {len(str(planned))} characters; '
            f'local conservative budget is {MAX_RUN_DIR_CHARS}. Use a shorter root/label.')
    if (root/'analog_supply_pilot_v1/runs'/label).exists():
        raise PreflightError('existing_run','Run label already exists; preserve earlier evidence')
    return planned

def verify_files(root,lock):
    for row in lock['files']:
        path=safe_path(root,row['path'])
        if not path.is_file() or path.stat().st_size!=row['bytes'] or sha(path)!=row['sha256']:
            raise PreflightError('dependency_identity_mismatch',row['path'])
    return len(lock['files'])

def check_log_and_witness(returncode,log,witness):
    if returncode!=0 or BAD_LOG.search(log):
        raise PreflightError('native_include_or_startup_error',
                             'Native smoke test reported an error; inspect retained logs')
    if not witness.is_file():
        raise PreflightError('missing_smoke_witness','Native smoke witness is missing')
    rows=[line.split() for line in witness.read_text(encoding='utf-8').splitlines() if line.strip()]
    if len(rows)!=1 or len(rows[0])!=2:
        raise PreflightError('invalid_smoke_witness','Expected one two-column operating-point row')
    try:
        vals=[float(x) for x in rows[0]]
    except ValueError:
        raise PreflightError('invalid_smoke_witness','Non-numeric operating-point witness')
    if not all(math.isfinite(x) and abs(x-1.0)<=1e-9 for x in vals):
        raise PreflightError('invalid_smoke_witness','Operating-point witness is not finite unity')
    return vals

def run(root,label,report_dir):
    root=root.resolve();report_dir=report_dir.resolve()
    report_dir.mkdir(parents=True,exist_ok=False)
    report={'started_at_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Prepared Windows environment preflight; not clean installation or an electrical grade',
        'root':str(root),'label':label,'model_calls':0,'native_smoke_launched':False,
        'candidate_evaluator_launched':False,'path_budget_characters':MAX_RUN_DIR_CHARS,
        'preflight_source_sha256':sha(Path(__file__)),
        'lock_sha256':sha(HERE/'dependency_lock.json')}
    started=time.monotonic()
    try:
        if os.name!='nt' or struct.calcsize('P')!=8 or sys.version_info[:2]!=(3,12):
            raise PreflightError('unsupported_python_platform','Use 64-bit Windows Python 3.12')
        planned=validate_layout(root,label)
        report['planned_native_directory']=str(planned)
        report['planned_native_directory_characters']=len(str(planned))
        lock=json.loads((HERE/'dependency_lock.json').read_text(encoding='utf-8'))
        report['verified_input_files']=verify_files(root,lock)
        try:
            numpy_version=importlib.metadata.version('numpy')
        except importlib.metadata.PackageNotFoundError:
            raise PreflightError('missing_python_dependency','NumPy 2.3.5 is required')
        if numpy_version!='2.3.5':
            raise PreflightError('python_dependency_version','NumPy 2.3.5 is required')
        report['python']={'version':sys.version,'executable':sys.executable,'numpy':numpy_version}
        # pf__ and runs have the same length. The relative depth and planned
        # directory length match the real first testbench without occupying it.
        probe=planned_directory(root,label,'pf__')
        if probe.exists():
            raise PreflightError('existing_probe','Probe label already exists; preserve earlier evidence')
        assert len(str(probe))==len(str(planned))
        probe.mkdir(parents=True)
        library=root/'analog_public_v1/deps/pdk/sky130A/libs.tech/combined/sky130.lib.spice'
        relative_library=os.path.relpath(library,probe).replace('\\','/')
        if ' ' in relative_library:
            raise PreflightError('unsafe_model_lookup','Relative model path contains a space')
        deck=("* Native library/include preflight, not a circuit score\n"
              f'.lib "{relative_library}" tt\n'
              'Vprobe witness 0 1\nRprobe witness 0 1000\n'
              '.control\nset numdgt=15\nop\nwrdata smoke.txt v(witness)\nquit\n.endc\n.end\n')
        deck_path=probe/'smoke.cir';deck_path.write_text(deck,encoding='utf-8',newline='\n')
        simulator=root/'analog_public_v1/deps/ngspice_win41/runtime/Library/bin/ngspice_con.exe'
        env=os.environ.copy();env['SPICE_SCRIPTS']=str(root/'analog_public_v1/sim_scripts')
        command=[str(simulator),'-n','-b','-D','ngbehavior=hsa','-D','ng_nomodcheck',deck_path.name]
        report.update({'native_smoke_launched':True,'native_command':command,
                       'smoke_directory':str(probe),'deck_sha256':sha(deck_path)})
        try:
            result=subprocess.run(command,cwd=probe,env=env,capture_output=True,
                                  timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        except subprocess.TimeoutExpired as exc:
            (probe/'stdout.txt').write_bytes(exc.stdout or b'')
            (probe/'stderr.txt').write_bytes(exc.stderr or b'')
            raise PreflightError('native_smoke_timeout','Native preflight exceeded 120 seconds')
        (probe/'stdout.txt').write_bytes(result.stdout)
        (probe/'stderr.txt').write_bytes(result.stderr)
        report['native_returncode']=result.returncode
        log=(result.stdout+result.stderr).decode('utf-8',errors='replace')
        report['witness']=check_log_and_witness(result.returncode,log,probe/'smoke.txt')
        report['outcome']='preflight_pass'
        report['limits']='Library parsing and trivial operating point only; not numerical qualification, hardware validation or a clean environment.'
        code=0
    except PreflightError as exc:
        report.update({'outcome':'preflight_blocked','category':exc.category,'message':str(exc)})
        code=2
    except Exception as exc:
        report.update({'outcome':'preflight_error','category':type(exc).__name__,'message':str(exc)})
        code=3
    report['elapsed_seconds']=time.monotonic()-started
    report['finished_at_utc']=datetime.now(timezone.utc).isoformat()
    (report_dir/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return code,report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--label',required=True)
    args=parser.parse_args()
    key=hashlib.sha256(str(args.root.resolve()).encode('utf-8')).hexdigest()[:10]
    validate_label(args.label)
    code,report=run(args.root,args.label,HERE/'checks'/f'{key}_{args.label}')
    print(json.dumps(report,indent=2))
    return code

if __name__=='__main__':
    raise SystemExit(main())
