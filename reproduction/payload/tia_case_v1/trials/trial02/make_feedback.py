"""Own-candidate-only serializer, fixed before the first proposal."""
import argparse
import hashlib,json
from pathlib import Path
import re
import numpy as np

OUT=Path(__file__).resolve().parent;BASE=OUT.parents[1]
p=argparse.ArgumentParser();p.add_argument('label');p.add_argument('--proposal',type=int,choices=(1,2,3),required=True);a=p.parse_args()
assert re.fullmatch(r'[A-Za-z0-9_]+',a.label)
source=BASE/'evaluations'/a.label/'result.json';r=json.loads(source.read_text())
identity=json.loads((source.parent/'identity.json').read_text())
target=OUT/f'feedback{a.proposal:02d}.txt';assert not target.exists()
lines=[f'Measured feedback for TIA-P01 proposal {a.proposal} of 3.',
       'Same fixed task: native ngspice 41, pinned SKY130 TT/27 C, VDD=1.2 V, ideal reference=.9 V, Iref=20 uA.',
       f"Outcome: {r['outcome']}; electrical score: {r.get('score')}",
       'Profile: '+('refined: max transient step .25 ns, AC 200/decade, tighter tolerances' if identity['refined'] else 'baseline: max transient step .5 ns, AC 100/decade'),
       'Settling uses the absolute command target +/-1 mV and all four edges; NOT_SETTLED means no retained settling in that window.',
       'AC samples below are measurements of this proposal only, not a reference or component recommendation.']
if 'error' in r:
    lines.append('Error: '+r['error'].replace(str(BASE.parent),'<workspace>'))
for item in r.get('cases',[]):
    c,ac,tr=item['case'],item['ac'],item['transient']
    lines += [f"Sensor={c['sensor_pF']} pF, wiring={c['wire_pF']} pF:",'  Checks: '+json.dumps(item['checks'],sort_keys=True),
              '  AC metrics: '+json.dumps(ac,sort_keys=True)]
    nodes=(source.parent/c['id']/'op_nodes.txt').read_text();dc={}
    for name in ['sense','out','vref','vsup#branch','vref#branch']:
        m=re.search(r'(?mi)^'+re.escape(name)+r'\s*=\s*(\S+)',nodes)
        dc[name]=float(m[1]) if m else None
    lines.append('  DC nodes/currents at 10 uA photocurrent (V or A): '+json.dumps(dc))
    lines.append('  Initial 0 uA output error_V: '+str(tr['initial_error_V']))
    for e in tr['edges']:
        settle='NOT_SETTLED' if e['settle_ns'] is None else str(e['settle_ns'])
        lines.append(f"  Edge {e['edge']}, target_V={e['target_V']}, settle_ns={settle}, endpoint_error_V={e['endpoint_error_V']}, overshoot_V={e['overshoot_V']}")
    f,db,phase=np.loadtxt(source.parent/c['id']/'stb.txt',skiprows=1).T
    ft,zreal,zimag=np.loadtxt(source.parent/c['id']/'transfer.txt',skiprows=1).T
    for hz in [1e3,1e4,1e5,1e6,3e6,1e7,3e7,1e8]:
        x=np.log10(hz)
        lines.append('  AC_sample '+json.dumps({'Hz':hz,'loop_dB':float(np.interp(x,np.log10(f),db)),
                     'loop_phase_deg':float(np.interp(x,np.log10(f),phase)),
                     'Zt_real_ohm':float(np.interp(x,np.log10(ft),zreal)),
                     'Zt_imag_ohm':float(np.interp(x,np.log10(ft),zimag))}))
    lines.append(f"  Trace stop_s={tr['stop_s']}, rows={tr['rows']}, max_retained_step_s={tr['max_retained_step_s']}")
if r.get('all_points_pass'):
    lines.append('All six conditions pass; no further proposal requested. Numerical confirmation is performed locally.')
elif a.proposal<3:
    lines.append(f'You have {3-a.proposal} complete proposals remaining. Return one complete revised feedback subcircuit. Keep all criteria unchanged and label estimates honestly; no reference is supplied.')
else:
    lines.append('The three-proposal allowance is complete; no fourth proposal requested.')
target.write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
target.with_suffix('.json').write_text(json.dumps({'source_evaluation':a.label,'result_sha256':sha(source),
     'feedback_sha256':sha(target),'serializer_sha256':sha(Path(__file__)),'candidate_only':True,'reference_hints':False},indent=2)+'\n')
print(json.dumps({'feedback':target.name,'sha256':sha(target),'bytes':target.stat().st_size}))
