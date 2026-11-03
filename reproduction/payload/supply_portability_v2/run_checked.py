"""Preflight first, then invoke the unchanged frozen SUPPLY evaluator."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import preflight

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,required=True)
parser.add_argument('--label',required=True)
parser.add_argument('--candidate',type=Path,required=True)
parser.add_argument('--numerics',choices=('upstream','refined'),default='upstream')
args=parser.parse_args()
root=args.root.resolve();candidate=args.candidate
if not candidate.is_absolute():candidate=root/candidate
candidate=candidate.resolve()
preflight.validate_label(args.label)
key=hashlib.sha256(str(root).encode('utf-8')).hexdigest()[:10]
out=HERE/'checked_runs'/f'{key}_{args.label}'
out.mkdir(parents=True,exist_ok=False)
code,check=preflight.run(root,args.label,out/'preflight')
receipt={'started_at_utc':datetime.now(timezone.utc).isoformat(),'preflight_outcome':check['outcome'],
         'model_calls':0,'evaluator_launched':False,'wrapper_sha256':preflight.sha(Path(__file__)),
         'numerics':args.numerics}
if code==0:
    # Identity checks precede imports or execution of the locked evaluator.
    if not candidate.is_file():
        receipt.update({'outcome':'missing_candidate','message':'Candidate file does not exist'})
        code=2
    else:
        receipt['candidate_sha256']=preflight.sha(candidate)
        env=os.environ.copy()
        env.pop('PYTHONHOME',None);env.pop('PYTHONPATH',None)
        command=[sys.executable,'-E','-X','utf8',str(root/'analog_supply_pilot_v1/run_candidate_v2.py'),
                 str(candidate),'--label',args.label,'--numerics',args.numerics]
        receipt.update({'evaluator_launched':True,'command':command})
        # The unchanged evaluator enforces its own 120-second timeout for each
        # native child. Do not kill only its outer parent and orphan a solver.
        with (out/'stdout.txt').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
            proc=subprocess.run(command,cwd=root,env=env,stdout=stdout,stderr=stderr,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        receipt['evaluator_returncode']=proc.returncode
        result_path=root/'analog_supply_pilot_v1/runs'/args.label/'result.json'
        if proc.returncode!=0 or not result_path.is_file():
            receipt['outcome']='evaluator_or_input_invalid';code=3
        else:
            data=json.loads(result_path.read_text(encoding='utf-8'))
            receipt['result_path']=str(result_path)
            receipt['result_sha256']=preflight.sha(result_path)
            if len(data.get('points',[]))!=3 or any(x.get('errors') or x.get('outcome_category')=='simulation_or_measurement_invalid' for x in data['points']):
                receipt['outcome']='simulation_or_measurement_invalid';code=3
            else:
                receipt['outcome']='electrical_pass' if data['all_points_pass'] else 'electrical_specification_failure'
                receipt['point_passes']=[x['pass'] for x in data['points']]
                # Successful measurement execution is distinct from circuit success.
                code=0
else:
    receipt['outcome']='preflight_blocked'
receipt['finished_at_utc']=datetime.now(timezone.utc).isoformat()
(out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
raise SystemExit(code)
