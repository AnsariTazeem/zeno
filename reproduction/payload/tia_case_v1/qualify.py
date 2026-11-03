"""Bounded reference exploration and compiled-network verification; no AI calls."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import sys

from apparatus import BASE,ROOT,APP,sha,save,verify,run,render,ac_metrics,tran_metrics,checks
from network_input import compile_network,InvalidNetwork


def prepare():
    out=BASE/'public';out.mkdir(exist_ok=False)
    sys.path.insert(0,str(ROOT/'analog_supply_pilot_v1'))
    from geometry_domain_v2 import compile_supported_dut
    source=APP/'upstream/benchmark/golden/opamp_2stg_1v2.sp'
    text,counts=compile_supported_dut(source.read_text())
    (out/'fixed_amplifier.sp').write_text(text,encoding='utf-8',newline='\n')
    (out/'LICENSE_UPSTREAM.txt').write_bytes((ROOT/'capload_case_v1/public/LICENSE_UPSTREAM.txt').read_bytes())
    save(out/'MODEL_IDENTITY.json',{'source':source.relative_to(ROOT).as_posix(),'source_sha256':sha(source),
              'compiled_sha256':sha(out/'fixed_amplifier.sp'),'counts':counts,
              'upstream_commit':'13c40b2dd9bae22b83e2fc4aba0adb05e99e4282',
              'scope':'Attributed public plant; authored current-to-voltage fixture and grading'})
    private=BASE/'private';private.mkdir(exist_ok=False)
    for name,cf in [('baseline_1p',1e-12),('baseline_2p2',2.2e-12),('baseline_4p7',4.7e-12),
                    ('baseline_6p8',6.8e-12),('baseline_8p2',8.2e-12),('baseline_10p',10e-12),
                    ('baseline_22p',22e-12),('baseline_100p',100e-12)]:
        (private/(name+'.sp')).write_text(f'.subckt feedback sense out vref\nRf out sense 10000\nCf out sense {cf:.17g}\n.ends feedback\n',encoding='utf-8',newline='\n')
    exe,identities=verify()
    save(BASE/'preparation.json',{'at_utc':datetime.now(timezone.utc).isoformat(),**identities,
                'plan_sha256':sha(BASE/'PLAN.md'),'initial_code_sha256':{p:sha(BASE/p) for p in ['apparatus.py','network_input.py','qualify.py']},
                'plant_sha256':sha(out/'fixed_amplifier.sp'),'model_calls':0})


def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['prepare','screen','evaluate'])
    p.add_argument('--candidate',type=Path);p.add_argument('--label');p.add_argument('--refined',action='store_true')
    a=p.parse_args()
    if a.phase=='prepare':
        prepare();print('Prepared attributed plant and finite baseline inputs');return
    assert a.label and re.fullmatch(r'[A-Za-z0-9_]+',a.label)
    exe,identities=verify()
    prep=json.loads((BASE/'preparation.json').read_text())
    assert sha(BASE/'PLAN.md')==prep['plan_sha256']
    assert sha(BASE/'public/fixed_amplifier.sp')==prep['plant_sha256']
    out=BASE/'evaluations'/a.label;out.mkdir(parents=True,exist_ok=False)
    identity={'created_at_utc':datetime.now(timezone.utc).isoformat(),**identities,'refined':a.refined,
              'model_trial':False,'phase':a.phase,'plan_sha256':sha(BASE/'PLAN.md'),
              'code_sha256':{p:sha(BASE/p) for p in ['apparatus.py','network_input.py','qualify.py']}}
    if a.phase=='screen':
        points=[{'id':f'case{i:02d}','sensor_pF':150,'wire_pF':10,'cf_pF':v}
                 for i,v in enumerate([1,2.2,4.7,6.8,8.2,10,22,100])]
        network='Rscreen out sense 10000\nCscreen out sense 1p\n'
    else:
        assert a.candidate and a.candidate.resolve().is_relative_to(BASE.resolve())
        raw=a.candidate.read_bytes();(out/'candidate_original.sp').write_bytes(raw)
        identity['candidate_sha256']=sha(out/'candidate_original.sp')
        try:
            compiled,counts=compile_network(raw.decode('utf-8'))
        except (InvalidNetwork,UnicodeDecodeError) as exc:
            save(out/'identity.json',identity)
            save(out/'result.json',{'outcome':'input_format_invalid','score':None,'simulator_launched':False,'error':str(exc)})
            print('input_format_invalid');return
        (out/'candidate_compiled.sp').write_text(compiled,encoding='utf-8',newline='\n')
        network=compiled+'\nXNET sense out vref feedback\n'
        identity['components']=counts
        points=[{'id':f'case{i:02d}','sensor_pF':x,'wire_pF':y}
                 for i,(x,y) in enumerate((x,y) for x in [10,70,150] for y in [2,10])]
    save(out/'identity.json',identity);save(out/'cases.json',points)
    for c in points:
        (out/c['id']).mkdir()
    plant=(BASE/'public/fixed_amplifier.sp').read_text()
    shared=out/'shared'
    deck=render(plant,network,points,shared,refined=a.refined,transient=a.phase=='evaluate',screen=a.phase=='screen')
    try:
        run(deck,shared,exe)
        rows=[]
        for c in points:
            folder=out/c['id'];ac=ac_metrics(folder)
            tr=tran_metrics(folder,.25e-9 if a.refined else .5e-9) if a.phase=='evaluate' else None
            check=checks(ac,tr)
            row={'case':c,'ac':ac,'transient':tr,'checks':check,'pass':all(check.values())}
            rows.append(row);save(folder/'result.json',row)
        passed=all(x['pass'] for x in rows)
        result={'outcome':'pass' if passed else 'electrical_specification_failure','score':(100 if passed else 0) if a.phase=='evaluate' else None,
                'scope':'Compiled candidate all-condition evaluation' if a.phase=='evaluate' else 'Trusted standard-baseline AC feasibility screen; not full qualification',
                'completed_operating_points':len(rows),'all_points_pass':passed,'model_trial':False,'cases':rows}
    except (RuntimeError,AssertionError,ValueError,OSError,IndexError) as exc:
        result={'outcome':'simulation_or_measurement_invalid','score':None,'simulator_launched':True,
                'error':type(exc).__name__+': '+str(exc),'model_trial':False}
    assert identities==verify()[1]
    save(out/'result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    if 'cases' in result:
        print(json.dumps([{'case':x['case'],'PM':min(x['ac']['phase_margins_deg']) if x['ac']['phase_margins_deg'] else None,
                           'BW_MHz':x['ac']['first_minus_3dB_Hz']/1e6,'checks':x['checks']} for x in rows],indent=2))


if __name__=='__main__':
    main()
