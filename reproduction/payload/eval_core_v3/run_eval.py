"""Three-task offline analog evaluation interface. No model or network calls."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,math,os,re,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.dont_write_bytecode=True
TASKS={
 'supply':{'id':'SUPPLY-P01-v2','public':'analog_supply_pilot_v1/public_v2',
           'files':['PROMPT.txt','TASK.md','starter.sp','contract.json','LICENSE_UPSTREAM.txt']},
 'load':{'id':'LOAD-P01','public':'capload_case_v1/public',
         'files':['PROMPT.txt','TASK.md','starter.sp','fixed_amplifier.sp','contract.json','MODEL_IDENTITY.json','LICENSE_UPSTREAM.txt']},
 'tia':{'id':'TIA-P01','public':'tia_case_v1/public',
        'files':['PROMPT.txt','TASK.md','starter.sp','fixed_amplifier.sp','contract.json','MODEL_IDENTITY.json','LICENSE_UPSTREAM.txt']}}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(v,indent=2,allow_nan=False)+'\n')
def relative(root,name):
 name=name.replace('\\','/')
 if ':' in name or name.startswith('/') or '..' in name.split('/'):raise ValueError('Unsafe dependency path')
 p=(root/name).resolve()
 if not p.is_relative_to(root.resolve()):raise ValueError('Dependency escapes root')
 return p
LOCK=read(HERE/'dependency_lock.json')
def verify():
 for e in LOCK['files']:
  p=relative(ROOT,e['path'])
  if not p.is_file() or p.stat().st_size!=e['bytes'] or sha(p)!=e['sha256']:raise ValueError('Dependency identity mismatch: '+e['path'])
 return len(LOCK['files'])
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def finite(x):return isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x)
def invalid(message):return {'category':'infrastructure_error','success':None,'score':None,'error':message}

def assess_load(data,contract):
 rows=data.get('cases');grid={(x,y) for x in contract['load_capacitances_pF'] for y in contract['feedback_node_stray_capacitances_pF']}
 if data.get('outcome')=='simulation_or_measurement_invalid' or not isinstance(rows,list) or len(rows)!=len(grid):return invalid('Incomplete/invalid load measurements')
 indexed={}
 for row in rows:
  if not isinstance(row,dict) or not isinstance(row.get('case'),dict):return invalid('Malformed load condition')
  c=row['case'];key=(c.get('cl_pF'),c.get('cp_pF'))
  if not all(finite(x) for x in key) or key not in grid or key in indexed:return invalid('Unexpected/duplicate load grid')
  indexed[key]=row
 points=[];lim=contract['limits']
 for cl,cp in sorted(grid):
  row=indexed[(cl,cp)];ac=row.get('ac');tr=row.get('transient')
  if not isinstance(ac,dict) or not isinstance(tr,dict):return invalid('Missing loop/transient measurements')
  for k in ['low_frequency_loop_gain_dB','phase_at_low_frequency_deg','dc_power_uW']:
   if not finite(ac.get(k)):return invalid('Nonfinite/missing loop measurement: '+k)
  cross=ac.get('unity_downward_crossings_Hz');pm=ac.get('phase_margins_deg')
  if not isinstance(cross,list) or not isinstance(pm,list) or len(cross)!=len(pm) or not all(finite(x) and x>0 for x in cross) or not all(finite(x) for x in pm):return invalid('Malformed crossing measurements')
  if any(b<=a for a,b in zip(cross,cross[1:])):return invalid('Crossing frequencies must increase')
  if (not all(finite(tr.get(k)) for k in ['stop_s','rows','max_retained_step_s'])
      or tr['stop_s']<contract['observation_us']*1e-6*(1-1e-7)
      or tr['rows']<=100 or not 0<tr['max_retained_step_s']<=1e-9+1e-14):return invalid('Incomplete/invalid transient coverage')
  edges=tr.get('edges')
  if not isinstance(edges,list) or len(edges)!=4:return invalid('Expected all four commanded edges')
  if any(not isinstance(e,dict) or type(e.get('edge')) is not int for e in edges):return invalid('Malformed edge record')
  ordered={e['edge']:e for e in edges}
  if set(ordered)!={1,2,3,4}:return invalid('Missing/duplicate commanded edge')
  checks=[]
  def check(name,value,op,limit,ok):checks.append({'metric':name,'value':value,'operator':op,'limit':limit,'pass':bool(ok)})
  check('noninverting_loop',ac['phase_at_low_frequency_deg'],'absolute <',90,abs(ac['phase_at_low_frequency_deg'])<90 and bool(cross))
  check('phase_margin_all_crossings',pm,'all >=',lim['all_downward_unity_crossing_phase_margins_deg_min'],bool(pm) and min(pm)>=lim['all_downward_unity_crossing_phase_margins_deg_min'])
  check('dc_power_uW',ac['dc_power_uW'],'0 < value <=',lim['dc_supply_power_uW_max'],0<ac['dc_power_uW']<=lim['dc_supply_power_uW_max'])
  for i,e in sorted(ordered.items()):
   target=1.0 if i%2 else .8
   if e.get('target_V')!=target or 'settle_us' not in e:return invalid('Wrong/missing edge target or settling field')
   s=e['settle_us'];o=e.get('overshoot_V')
   if (s is not None and (not finite(s) or s<0)) or not finite(o) or o<0 or not finite(e.get('endpoint_error_V')):return invalid('Invalid edge measurements')
   check(f'edge{i}_settle_us',s,'<=',lim['settle_us_max_each_of_four_edges'],s is not None and s<=lim['settle_us_max_each_of_four_edges'])
   check(f'edge{i}_overshoot_V',o,'<=',lim['overshoot_V_max_each_edge'],o<=lim['overshoot_V_max_each_edge'])
  points.append({'condition':f'CL={cl}pF, Cp={cp}pF','case':row['case'],'checks':checks,'pass':all(c['pass'] for c in checks)})
 success=all(p['pass'] for p in points)
 return {'category':'pass' if success else 'specification_failure','success':success,'score':100 if success else 0,'points':points}

def assess(task,data,contract):
 if task=='load':return assess_load(data,contract)
 if task=='tia':return module('tia_adapter',HERE/'tia_adapter.py').assess(data,contract)
 old=module('verified_supply_core',ROOT/'eval_core_v1/run_eval.py')
 result=old.assess(data,contract)
 for p in result.get('points',[]):p['condition']=f"VDD={p['vdd']}V"
 return result

def compile_candidate(task,text):
 if task=='supply':return module('verified_supply_core',ROOT/'eval_core_v1/run_eval.py').compile_candidate(text)
 folder='tia_case_v1' if task=='tia' else 'capload_case_v1'
 return module(task+'_network_compiler',ROOT/folder/'network_input.py').compile_network(text)

def stage_runtime():
 stage=Path(tempfile.mkdtemp(prefix='me_')).resolve()
 for e in LOCK['files']:
  dest=relative(stage,e['path']);dest.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(relative(ROOT,e['path']),dest)
  if sha(dest)!=e['sha256']:raise ValueError('Staged dependency mismatch')
 return stage

def write_outputs(out,r,proposal):
 r.update({'schema_version':2,'model_calls':0,'finished_at_utc':datetime.now(timezone.utc).isoformat()})
 save(out/'result.json',r)
 lines=[f"Measured feedback for proposal {proposal} of 3; task {r['task_id']}.",'Outcome: '+r['category']]
 report=[f"# {r['task_id']} evaluation",'',f"Outcome: **{r['category']}**; score: {r.get('score')}",'',
         f"Evidence: {r['evidence_mode']}; model calls: 0.",'','| Condition | Pass | Failed requirements |','|---|---|---|']
 for p in r.get('points',[]):
  lines.append(p['condition'])
  for c in p['checks']:lines.append(f"{c['metric']}: {c['value']}; required {c['operator']} {c['limit']}; pass={c['pass']}")
  report.append(f"| {p['condition']} | {p['pass']} | "+', '.join(c['metric'] for c in p['checks'] if not c['pass'])+' |')
 if r.get('success'):lines.append('All requirements pass. Stop; no further proposal requested.')
 elif r['category'] in ('specification_failure','invalid_candidate'):lines.append(f'{3-proposal} proposal(s) remain.' if proposal<3 else 'The three-proposal allowance is complete.')
 else:lines.append('Infrastructure/measurement outcome; no electrical capability conclusion is supported.')
 if r.get('error'):lines.append(str(r['error']).replace(str(ROOT),'<workspace>').replace(r.get('verifier_workspace','__NO_STAGE__'),'<verifier>'))
 (out/'feedback.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 report+=['','This circuit evaluation is not a model trial. Replay uses saved measurements.',
          'Local verifier separation is organizational, not proven filesystem confidentiality.','']
 (out/'report.md').write_text('\n'.join(report),encoding='utf-8')
 save(out/'manifest.json',{'files':[{'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(out.rglob('*')) if p.is_file()]})
 print(json.dumps({'run_directory':str(out),'task_id':r['task_id'],'category':r['category'],'score':r.get('score'),'model_calls':0},indent=2),flush=True)

def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
 for name in ['inspect','export-task','evaluate','replay']:
  q=sub.add_parser(name);q.add_argument('--task',choices=TASKS,required=True)
  if name=='export-task':q.add_argument('--out',type=Path,required=True)
  if name in ('evaluate','replay'):
   q.add_argument('--run-id',required=True);q.add_argument('--proposal',type=int,choices=(1,2,3),default=1)
   if name=='evaluate':q.add_argument('--candidate',type=Path,required=True);q.add_argument('--numerics',choices=('upstream','refined'),default='upstream')
   else:q.add_argument('--source',type=Path,required=True)
 a=p.parse_args();task=TASKS[a.task]
 if a.command=='inspect':
  print(json.dumps({'task_id':task['id'],'verified_dependencies':verify(),'model_calls':0,'scope':'Prepared Windows environment; no clean installation qualification'},indent=2));return 0
 if a.command=='export-task':
  verify();out=a.out.resolve()
  try:out.mkdir(parents=True,exist_ok=False)
  except FileExistsError:p.error('Export directory exists; use a new path')
  for name in task['files']:shutil.copyfile(ROOT/task['public']/name,out/name)
  print(json.dumps({'files':task['files'],'reference_files_exported':0}));return 0
 if not re.fullmatch(r'[A-Za-z0-9_]{1,32}',a.run_id):p.error('Invalid run ID')
 out=HERE/'runs'/a.task/a.run_id
 try:out.mkdir(parents=True,exist_ok=False)
 except FileExistsError:p.error('Run ID exists; preserve prior evidence')
 r={'task_id':task['id'],'run_id':a.run_id,'evidence_mode':'fresh_native_simulation' if a.command=='evaluate' else 'retained_measurement_replay',
    'category':'infrastructure_error','score':None,'success':None,'native_evaluator_launched':False,
    'runner_sha256':sha(Path(__file__)),'dependency_lock_sha256':sha(HERE/'dependency_lock.json')}
 try:
  r['verified_dependencies']=verify();contract=read(ROOT/task['public']/'contract.json')
  if a.command=='replay':
   source=a.source.resolve();shutil.copyfile(source,out/'measurements.json');r['source_result_sha256']=sha(source)
   r.update(assess(a.task,read(source),contract))
  else:
   body=a.candidate.read_bytes();(out/'candidate_original.sp').write_bytes(body)
   try:compiled,counts=compile_candidate(a.task,body.decode('utf-8'))
   except (ValueError,UnicodeError) as e:
    r.update({'category':'invalid_candidate','score':None,'success':False,'error':str(e)});write_outputs(out,r,a.proposal);return 2
   r.update({'candidate_sha256':sha(out/'candidate_original.sp'),'components':counts,'numerics':a.numerics})
   (out/'candidate_compiled.sp').write_text(compiled,encoding='utf-8',newline='\n')
   stage=stage_runtime();r['verifier_workspace']=str(stage)
   if a.task=='supply':
    candidate=stage/'candidate.sp';native=stage/'analog_supply_pilot_v1/runs/s'
    cmd=[sys.executable,'-E','-X','utf8',str(stage/'supply_portability_v2/run_checked.py'),'--root',str(stage),'--label','s','--candidate',str(candidate),'--numerics',a.numerics]
   elif a.task=='tia':
    candidate=stage/'tia_case_v1/candidate.sp';native=stage/'tia_case_v1/evaluations/s'
    cmd=[sys.executable,'-E','-X','utf8',str(stage/'tia_case_v1/evaluate_frozen.py'),str(candidate),'--label','s']
    if a.numerics=='refined':cmd+=['--refined']
   else:
    candidate=stage/'capload_case_v1/candidate.sp';native=stage/'capload_case_v1/evaluations/s'
    cmd=[sys.executable,'-E','-X','utf8',str(stage/'capload_case_v1/evaluate_network.py'),str(candidate),'--label','s']
    if a.numerics=='refined':cmd+=['--refined']
   candidate.write_bytes(body);save(out/'launch.json',{'command':cmd,'at_utc':datetime.now(timezone.utc).isoformat()})
   env=os.environ.copy();env.pop('PYTHONHOME',None);env.pop('PYTHONPATH',None);r['verifier_wrapper_launched']=True
   with (out/'stdout.txt').open('wb') as so,(out/'stderr.txt').open('wb') as se:
    proc=subprocess.Popen(cmd,cwd=stage,env=env,stdout=so,stderr=se,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    try:proc.wait(timeout=900)
    except subprocess.TimeoutExpired:
     if proc.poll() is None:subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True,timeout=20)
     proc.wait(timeout=20);raise RuntimeError('Verifier timeout; process tree terminated')
   r['evaluator_returncode']=proc.returncode
   if native.exists():
    shutil.copytree(native,out/'native');r['native_evaluator_launched']=bool(list(native.rglob('launch.json')))
   if proc.returncode or not (out/'native/result.json').exists():raise RuntimeError('Verifier did not complete; inspect retained logs')
   data=read(out/'native/result.json');r['native_result_sha256']=sha(out/'native/result.json')
   r.update(assess(a.task,data,contract))
 except Exception as e:r.update(invalid(type(e).__name__+': '+str(e)))
 write_outputs(out,r,a.proposal)
 return 3 if r['category']=='infrastructure_error' else 0

if __name__=='__main__':raise SystemExit(main())
