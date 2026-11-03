"""Evaluate a compiled passive network under all six disclosed load conditions."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re

from apparatus import APP,BASE,ROOT,sha,run,analyze_loop,analyze_tran
from network_input import compile_network,InvalidNetwork

def main():
    p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('--label',required=True);p.add_argument('--refined',action='store_true')
    a=p.parse_args();assert re.fullmatch(r'[A-Za-z0-9_]+',a.label)
    assert a.candidate.resolve().is_relative_to(BASE.resolve()),'Use a candidate file within this case directory'
    out=BASE/'evaluations'/a.label;assert not out.exists(),'Use a fresh label'
    freeze=BASE/'freeze.json'
    if freeze.exists():
        assert all(sha(ROOT/x['path'])==x['sha256'] for x in json.loads(freeze.read_text())['files'])
    contract=json.loads((BASE/'public/contract.json').read_text())
    for name,root,key in (('upstream_manifest.json',APP/'upstream','path'),('model_manifest.json',APP/'deps/pdk','file')):
        assert all(sha(root/x[key])==x['sha256'] for x in json.loads((APP/name).read_text())['files'])
    sm=json.loads((APP/'windows_simulator_manifest.json').read_text());exe=APP/sm['exe'];assert sha(exe)==sm['exe_sha256']
    out.mkdir(parents=True);raw=a.candidate.read_bytes();(out/'candidate_original.sp').write_bytes(raw)
    identity={'created_at_utc':datetime.now(timezone.utc).isoformat(),'candidate_sha256':sha(out/'candidate_original.sp'),'refined':a.refined,
              'contract_sha256':sha(BASE/'public/contract.json'),'plant_sha256':sha(BASE/'public/fixed_amplifier.sp'),'simulator_sha256':sm['exe_sha256'],
              'code_sha256':{n:sha(BASE/n) for n in ('apparatus.py','network_input.py','evaluate_network.py')}}
    (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    try:compiled,counts=compile_network(raw.decode('utf-8'))
    except (InvalidNetwork,UnicodeDecodeError) as e:
        result={'outcome':'input_format_invalid','score':None,'simulator_launched':False,'error':str(e)}
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return
    (out/'candidate_compiled.sp').write_text(compiled,encoding='utf-8',newline='\n')
    cases=[{'id':f'case{i:02d}','cl_pF':c,'cp_pF':cp} for i,(c,cp) in enumerate((x,y) for x in contract['load_capacitances_pF'] for y in contract['feedback_node_stray_capacitances_pF'])]
    (out/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
    for c in cases:(out/c['id']).mkdir()
    shared=out/'shared';lib=os.path.relpath(APP/'deps/pdk/sky130A/libs.tech/combined/sky130.lib.spice',shared).replace('\\','/');assert ' ' not in lib
    rel,vnt,abt,step,density=('1e-4','1e-7','1e-13','500p',100) if a.refined else ('1e-3','1e-6','1e-12','1n',50)
    plant=(BASE/'public/fixed_amplifier.sp').read_text()
    deck=f'* LOAD-P01: compiled candidate and fixed public plant\n.lib "{lib}" tt\n.param VDD=1.2\n.global vdd\n.options reltol={rel} gmin=1e-12 vntol={vnt} abstol={abt}\n.temp 27\n{plant}\n{compiled}\nVSUP vdd 0 dc 1.2\nIREF vdd niref dc 20u\nVIN nin 0 dc 0.9 PULSE(0.8 1.0 5u 20n 20n 4.98u 10u)\nXDUT niref nin nampfb drive dut\nXNET drive load fb feedback\nRload load 0 100000\nCload load 0 150p\nCstray fb 0 1p\nVprb_b prb_n1 fb 0\nVprb_inj prb_n1 prb_n2 0 ac 1\nVprb_a prb_n2 nampfb 0\nIprb_inj 0 prb_n1 0 ac 0\n.control\nset wr_singlescale\nset wr_vecnames\noption numdgt=10\n'
    for i,c in enumerate(cases):
        name=c['id']
        deck+=f'alter Cload {c["cl_pF"]*1e-12:.15g}\nalter Cstray {c["cp_pF"]*1e-12:.15g}\nalter VIN dc=0.9\nalter Vprb_inj acmag=1\nalter Iprb_inj acmag=0\nop\nprint all > ../{name}/op_nodes.txt\nac dec {density} 10 10G\nlet lg_tv = -v(prb_n1)/v(prb_n2)\nalter Vprb_inj acmag=0\nalter Iprb_inj acmag=1\nac dec {density} 10 10G\nlet lg_ti = i(Vprb_b)/i(Vprb_a)\nlet tv = ac{2*i+1}.lg_tv\nlet loopgain = (tv*lg_ti - 1)/(tv + lg_ti + 2)\nlet lg_db = db(loopgain)\nlet lg_ph = 180/pi*cph(loopgain)\nwrdata ../{name}/stb.txt lg_db lg_ph\nalter VIN dc=0.8\ntran {step} 25u 0 {step}\nwrdata ../{name}/tran.txt v(nin) v(load) v(drive) i(VSUP)\n'
    deck+='.endc\n.end\n'
    try:
        run(deck,shared,exe,a.refined)
        rows=[];limits=contract['limits']
        for c in cases:
            folder=out/c['id'];ac=analyze_loop(folder);tr=analyze_tran(folder,0.5e-9 if a.refined else 1e-9)
            checks={'noninverting_loop':abs(ac['phase_at_low_frequency_deg'])<90 and bool(ac['phase_margins_deg']),
                    'phase_margin':bool(ac['phase_margins_deg']) and min(ac['phase_margins_deg'])>=limits['all_downward_unity_crossing_phase_margins_deg_min'],
                    'power':0<ac['dc_power_uW']<=limits['dc_supply_power_uW_max'],
                    'settling':all(e['settle_us'] is not None and e['settle_us']<=limits['settle_us_max_each_of_four_edges'] for e in tr['edges']),
                    'overshoot':all(e['overshoot_V']<=limits['overshoot_V_max_each_edge'] for e in tr['edges'])}
            row={'case':c,'ac':ac,'transient':tr,'checks':checks,'pass':all(checks.values())};rows.append(row)
            (folder/'result.json').write_text(json.dumps(row,indent=2,allow_nan=False)+'\n')
        passed=all(r['pass'] for r in rows)
        result={'outcome':'pass' if passed else 'electrical_specification_failure','score':100 if passed else 0,'all_six_points_pass':passed,
                'completed_operating_points':len(rows),'components':counts,'cases':rows,'model_trial':False}
    except (RuntimeError,AssertionError,ValueError,OSError,IndexError) as e:
        result={'outcome':'simulation_or_measurement_invalid','score':None,'simulator_launched':True,'error':type(e).__name__+': '+str(e),'model_trial':False}
    (out/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))

if __name__=='__main__':main()
