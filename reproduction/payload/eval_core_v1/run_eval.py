"""Common offline entry point for the first integrated analog task.

Does not call a model or download dependencies. The prepared Windows apparatus
is copied into a fresh verifier workspace; previous experiments are read-only.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, math, os, re, shutil, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SUPPLY = ROOT/'analog_supply_pilot_v1'
LOCK = ROOT/'supply_portability_v2/dependency_lock.json'
PUBLIC_FILES = ('PROMPT.txt','TASK.md','starter.sp','contract.json','LICENSE_UPSTREAM.txt')
sys.dont_write_bytecode = True

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, value):
    with p.open('x',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps(value,indent=2,allow_nan=False)+'\n')

def safe_relative(root, name):
    name=name.replace('\\','/')
    if ':' in name or name.startswith('/') or '..' in name.split('/'):
        raise ValueError('Unsafe dependency path')
    p=(root/name).resolve()
    if not p.is_relative_to(root.resolve()):raise ValueError('Dependency escapes root')
    return p

def verify_inputs():
    data=read(LOCK)
    for e in data['files']:
        p=safe_relative(ROOT,e['path'])
        if not p.is_file() or p.stat().st_size!=e['bytes'] or sha(p)!=e['sha256']:
            raise ValueError('Dependency identity mismatch: '+e['path'])
    return data

def finite(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def assess(data, contract):
    """Recompute stated acceptance checks; never trust aggregate pass flags."""
    points=data.get('points')
    if not isinstance(points,list) or len(points)!=len(contract['supplies_V']):
        return {'category':'infrastructure_error','score':None,'success':None,'error':'Incomplete operating grid'}
    if any(not isinstance(p,dict) or not finite(p.get('vdd')) for p in points):
        return {'category':'infrastructure_error','score':None,'success':None,'error':'Malformed operating grid'}
    by_supply={p['vdd']:p for p in points}
    if len(by_supply)!=len(points) or set(by_supply)!=set(contract['supplies_V']):
        return {'category':'infrastructure_error','score':None,'success':None,'error':'Unexpected/duplicate operating grid'}
    results=[]
    for vdd in contract['supplies_V']:
        p=by_supply[vdd]
        if not isinstance(p.get('errors'),list) or p['errors'] or p.get('trace_error') or p.get('outcome_category')=='simulation_or_measurement_invalid':
            return {'category':'infrastructure_error','score':None,'success':None,'error':'Invalid operating-point measurements'}
        metrics=p.get('metrics');tracking=p.get('command_tracking')
        if not isinstance(metrics,dict) or not isinstance(tracking,dict):
            return {'category':'infrastructure_error','score':None,'success':None,'error':'Missing measurement section'}
        coverage=('observed_stop_s','max_retained_step_s','measured_rows')
        if (not all(finite(tracking.get(k)) for k in coverage)
            or tracking['observed_stop_s']<contract['observation_s']-1e-15
            or not 0<tracking['max_retained_step_s']<=10e-12+10e-15+1e-18
            or tracking['measured_rows']<4):
            return {'category':'infrastructure_error','score':None,'success':None,'error':'Invalid retained trace coverage'}
        checks=[]
        for metric,rule in contract['limits'].items():
            is_tracking=metric.startswith('command_')
            key=metric.removeprefix('command_') if is_tracking else metric
            value=(tracking if is_tracking else metrics).get(key)
            # None in a present settling field means a complete trace did not
            # settle. A missing field is an invalid measurement, never a pass.
            source=tracking if is_tracking else metrics
            if key not in source or (not finite(value) and not (is_tracking and value is None)):
                return {'category':'infrastructure_error','score':None,'success':None,'error':'Missing/nonfinite measurement: '+metric}
            op,limit=next(iter(rule.items()))
            ok=value is not None and (value>=limit if op=='>=' else value<=limit)
            checks.append({'metric':metric,'value':value,'operator':op,'limit':limit,'pass':ok})
        results.append({'vdd':vdd,'pass':all(c['pass'] for c in checks),'checks':checks,
                        'metrics':metrics,'command_tracking':tracking})
    success=all(p['pass'] for p in results)
    return {'category':'pass' if success else 'specification_failure','success':success,
            'score':100 if success else 0,'points':results}

def compile_candidate(text):
    sys.path.insert(0,str(SUPPLY))
    from geometry_domain_v2 import compile_supported_dut
    return compile_supported_dut(text)

def stage_runtime(lock):
    # A short root avoids the native parser/path-budget issues in the old pilots.
    stage=Path(tempfile.mkdtemp(prefix='me_')).resolve()
    for e in lock['files']:
        src=safe_relative(ROOT,e['path']);dest=safe_relative(stage,e['path'])
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
        if sha(dest)!=e['sha256']:raise ValueError('Staged dependency changed')
    helper=stage/'supply_portability_v2';helper.mkdir(exist_ok=True)
    for name in ('preflight.py','run_checked.py','dependency_lock.json'):
        shutil.copyfile(ROOT/'supply_portability_v2'/name,helper/name)
    return stage

def write_outputs(out, outcome, proposal, native=None):
    outcome.update({'schema_version':1,'task_id':'SUPPLY-P01-v2','model_calls':0,
                    'finished_at_utc':datetime.now(timezone.utc).isoformat()})
    save(out/'result.json',outcome)
    lines=[f"Measured evaluation for proposal {proposal} of 3.",
           'Outcome: '+outcome['category'], 'Score: '+str(outcome.get('score'))]
    for p in outcome.get('points',[]):
        lines.append(f"Supply {p['vdd']} V: {'PASS' if p['pass'] else 'FAIL'}")
        for c in p['checks']:
            lines.append(f"{c['metric']}: {c['value']} (required {c['operator']} {c['limit']}); pass={c['pass']}")
    if outcome.get('success') is True:lines.append('All disclosed requirements pass. Stop; no further proposal is requested.')
    elif outcome['category'] in ('specification_failure','invalid_candidate'):
        lines.append(f'{3-proposal} proposal(s) remain.' if proposal<3 else 'The three-proposal allowance is complete.')
    else:lines.append('Infrastructure/measurement outcome: no electrical capability conclusion is supported.')
    if outcome.get('error'):
        # Feedback contains no verifier workspace paths or reference material.
        error=str(outcome['error']).replace(str(ROOT),'<workspace>')
        if outcome.get('verifier_workspace'):error=error.replace(outcome['verifier_workspace'],'<verifier>')
        lines.append(error)
    (out/'feedback.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    report=['# SUPPLY-P01-v2 evaluation','',f"Outcome: **{outcome['category']}**; score: {outcome.get('score')}",
            '',f"Evidence mode: {outcome['evidence_mode']}. Model calls: 0.",'',
            '| Supply V | Pass | Failed requirements |','|---:|---|---|']
    for p in outcome.get('points',[]):
        report.append(f"| {p['vdd']} | {p['pass']} | "+', '.join(c['metric'] for c in p['checks'] if not c['pass'])+' |')
    report+=['','This is an evaluation of a supplied circuit or retained measurements, not a fresh AI trial.',
             'The local verifier boundary is organizational; no OS-level confidentiality guarantee is claimed.','']
    (out/'report.md').write_text('\n'.join(report),encoding='utf-8')
    files=[{'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':sha(p)}
           for p in sorted(out.rglob('*')) if p.is_file()]
    save(out/'manifest.json',{'files':files})
    print(json.dumps({'run_directory':str(out),'category':outcome['category'],'score':outcome.get('score'),
                      'success':outcome.get('success'),'model_calls':0},indent=2),flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('inspect',help='Verify prepared dependencies; no simulator/model call')
    export=sub.add_parser('export-task',help='Export ONLY the public task packet')
    export.add_argument('--out',type=Path,required=True)
    for cmd in ('evaluate','replay'):
        p=sub.add_parser(cmd)
        p.add_argument('--run-id',required=True)
        p.add_argument('--proposal',type=int,choices=(1,2,3),default=1)
        if cmd=='evaluate':
            p.add_argument('--candidate',type=Path,required=True)
            p.add_argument('--numerics',choices=('upstream','refined'),default='upstream')
        else:p.add_argument('--source',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='inspect':
        lock=verify_inputs()
        print(json.dumps({'task':'SUPPLY-P01-v2','verified_dependency_files':len(lock['files']),
                          'dependency_bytes':sum(x['bytes'] for x in lock['files']),
                          'dependency_lock_sha256':sha(LOCK),'model_calls':0,
                          'scope':'Prepared local workspace; clean installation not yet qualified'},indent=2));return 0
    if args.command=='export-task':
        verify_inputs();out=args.out.resolve()
        try:out.mkdir(parents=True,exist_ok=False)
        except FileExistsError:parser.error('Export directory already exists; use a fresh path')
        for name in PUBLIC_FILES:shutil.copyfile(SUPPLY/'public_v2'/name,out/name)
        print(json.dumps({'public_directory':str(out),'files':list(PUBLIC_FILES),'reference_files_exported':0},indent=2));return 0
    if not re.fullmatch(r'[A-Za-z0-9_]{1,32}',args.run_id):parser.error('run-id must have 1..32 letters/digits/underscores')
    out=HERE/'runs'/args.run_id
    try:out.mkdir(parents=True,exist_ok=False)
    except FileExistsError:parser.error('Run ID already exists; earlier evidence was preserved')
    outcome={'run_id':args.run_id,'evidence_mode':'retained_measurement_replay' if args.command=='replay' else 'fresh_native_simulation',
             'category':'infrastructure_error','success':None,'score':None,'runner_sha256':sha(Path(__file__)),
             'dependency_lock_sha256':sha(LOCK),'native_evaluator_launched':False}
    try:
        lock=verify_inputs();outcome['verified_dependency_files']=len(lock['files'])
        contract=read(SUPPLY/'public_v2/contract.json')
        if args.command=='replay':
            source=args.source.resolve();data=read(source)
            shutil.copyfile(source,out/'measurements.json')
            outcome['source_result_sha256']=sha(source)
            outcome.update(assess(data,contract))
        else:
            body=args.candidate.read_bytes()
            if len(body)>1024*1024:raise ValueError('Candidate exceeds the 1 MiB input budget')
            (out/'candidate_original.sp').write_bytes(body)
            try:compiled,counts=compile_candidate(body.decode('utf-8'))
            except (ValueError,UnicodeError) as exc:
                outcome.update({'category':'invalid_candidate','success':False,'score':0,'error':str(exc)})
                write_outputs(out,outcome,args.proposal);return 2
            outcome.update({'candidate_sha256':sha(out/'candidate_original.sp'),'components':counts,'numerics':args.numerics})
            (out/'candidate_compiled.sp').write_text(compiled,encoding='utf-8',newline='\n')
            stage=stage_runtime(lock);outcome['verifier_workspace']=str(stage)
            candidate=stage/'candidate.sp';candidate.write_bytes(body)
            command=[sys.executable,'-E','-X','utf8',str(stage/'supply_portability_v2/run_checked.py'),
                     '--root',str(stage),'--label','s','--candidate',str(candidate),'--numerics',args.numerics]
            save(out/'launch.json',{'command':command,'at_utc':datetime.now(timezone.utc).isoformat(),
                                    'staged_helper_sha256':{name:sha(stage/'supply_portability_v2'/name) for name in ('preflight.py','run_checked.py')}})
            env=os.environ.copy();env.pop('PYTHONHOME',None);env.pop('PYTHONPATH',None)
            outcome['verifier_wrapper_launched']=True
            with (out/'stdout.txt').open('wb') as so,(out/'stderr.txt').open('wb') as se:
                proc=subprocess.Popen(command,cwd=stage,env=env,stdout=so,stderr=se,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                try:proc.wait(timeout=900)
                except subprocess.TimeoutExpired:
                    if proc.poll() is None:subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True,timeout=20)
                    proc.wait(timeout=20);raise RuntimeError('Evaluator process-tree timeout')
            outcome['evaluator_returncode']=proc.returncode
            native=stage/'analog_supply_pilot_v1/runs/s'
            if native.is_dir():
                outcome['native_evaluator_launched']=True
                shutil.copytree(native,out/'native')
            # Include the path/startup preflight, including any failure receipt.
            checked=stage/'supply_portability_v2/checked_runs'
            if checked.exists():shutil.copytree(checked,out/'preflight')
            if proc.returncode or not (out/'native/result.json').is_file():
                raise RuntimeError('Evaluator/preflight did not produce a complete result; inspect retained logs')
            data=read(out/'native/result.json');outcome['native_result_sha256']=sha(out/'native/result.json')
            outcome.update(assess(data,contract))
    except Exception as exc:
        outcome.update({'category':'infrastructure_error','success':None,'score':None,'error':type(exc).__name__+': '+str(exc)})
    write_outputs(out,outcome,args.proposal)
    return 3 if outcome['category']=='infrastructure_error' else 0

if __name__=='__main__':raise SystemExit(main())
