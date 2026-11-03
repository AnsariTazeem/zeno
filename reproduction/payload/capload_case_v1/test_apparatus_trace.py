"""Physical failure cases for four-edge tracking and source/trace integrity."""
import json
from pathlib import Path
import numpy as np
from apparatus import BASE,sha,analyze_tran,command_voltage

OUT=BASE/'trace_validation_02';assert not OUT.exists();OUT.mkdir()
FOLDER=OUT/'temporary_fixture';FOLDER.mkdir()
assert FOLDER.resolve().is_relative_to(BASE.resolve())
t=np.linspace(0,25e-6,25001);vin=command_voltage(t)
perfect=np.column_stack((t,vin,vin,vin,np.full(len(t),-0.0002)))
cases=[]
def check(name,data,expected):
    path=FOLDER/'tran.txt';np.savetxt(path,data,fmt='%.12e',header='time vin load drive current',comments='')
    digest=sha(path)
    try:
        r=analyze_tran(FOLDER,1e-9)
        got='pass' if all(e['settle_us'] is not None and e['settle_us']<=2.5 for e in r['edges']) else 'tracking_failure'
    except (AssertionError,ValueError):got='invalid_trace'
    cases.append({'fixture':name,'expected':expected,'observed':got,'input_sha256':digest})
    assert got==expected,(name,expected,got)
check('ideal_command_following',perfect,'pass')
a=perfect.copy();a[:,2]+=0.00049;check('inside_error_band',a,'pass')
a=perfect.copy();a[:,2]+=0.00051;check('outside_error_band',a,'tracking_failure')
a=perfect.copy();a[:,2]-=0.01;check('stable_but_wrong_final_value',a,'tracking_failure')
a=perfect.copy()
for start,target in ((5e-6,1.0),(10e-6,0.8),(15e-6,1.0),(20e-6,0.8)):
    a[(t>=start+0.1e-6)&(t<start+4.9e-6),2]=target+0.005
check('late_endpoint_only_recovery',a,'tracking_failure')
a=perfect.copy();a[(t>=8e-6)&(t<8.01e-6),2]=1.01;check('late_excursion_after_early_crossing',a,'tracking_failure')
a=perfect.copy();a[t>=20e-6,2]=0.82;check('fourth_edge_only_failure',a,'tracking_failure')
a=perfect.copy();a[:,1]=0.8;check('incorrect_command_source',a,'invalid_trace')
check('truncated_observation',perfect[:-1000],'invalid_trace')
a=perfect.copy();a[100,2]=np.nan;check('nonfinite_output',a,'invalid_trace')
a=perfect.copy();a[100,0]=a[99,0];check('duplicate_timestamp',a,'invalid_trace')
check('retained_time_gap',np.delete(perfect,np.arange(100,110),axis=0),'invalid_trace')
(FOLDER/'tran.txt').unlink()  # Only this generated temporary fixture file.
raw_checks=[]
for p in sorted((BASE/'runs').rglob('tran.txt')):
    if p.parent.name=='shared':continue
    identity=p.parent.parent/'identity.json'
    if not identity.exists():continue
    item=json.loads(identity.read_text());refined=item.get('arguments',{}).get('refined',False)
    r=analyze_tran(p.parent,0.5e-9 if refined else 1e-9)
    raw_checks.append({'trace':p.relative_to(BASE).as_posix(),'sha256':sha(p),'rows':r['rows'],'command_and_integrity_valid':True})
report={'grader_source_sha256':sha(BASE/'apparatus.py'),'test_source_sha256':sha(Path(__file__)),'fixtures':cases,'existing_trace_checks':raw_checks,
        'all_fixtures_match_expected':True,'source_validation_added_before_model_collection':True,'raw_simulations_modified':False}
(OUT/'result.json').write_text(json.dumps(report,indent=2)+'\n')
print('Adversarial fixtures:',len(cases),'all expected; existing traces validated:',len(raw_checks))
