"""Read-only raw evidence check; imports no grader or measurement function."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

BASE=Path(__file__).resolve().parent


def witness(root):
    original=json.loads((root/'result.json').read_text())
    assert 'cases' in original
    rows=[]
    knots=np.array([0,1e-6,1.005e-6,2e-6,2.005e-6,3e-6,3.005e-6,4e-6,4.005e-6,5e-6])
    currents=np.array([0,0,20e-6,20e-6,0,0,20e-6,20e-6,0,0])
    for case in original['cases']:
        folder=root/case['case']['id']
        a=np.loadtxt(folder/'tran.txt',skiprows=1)
        assert np.isfinite(a).all() and np.all(np.diff(a[:,0])>0)
        t,ip,sense,voltage,p1,p2=a.T
        assert max(abs(ip-np.interp(t,knots,currents)))<1e-12
        results=[]
        for k,target in enumerate([.7,.9,.7,.9]):
            beginning=(k+1)*1e-6;end=(k+2)*1e-6
            selection=np.flatnonzero((t>=beginning-1e-15)&(t<end-1e-15))
            times=t[selection];v=voltage[selection]
            # Suffix envelope: a correct endpoint cannot hide an earlier violation.
            envelope=np.maximum.accumulate(abs(v-target)[::-1])[::-1]
            persistent=np.flatnonzero(envelope<=.001)
            settle=float((times[persistent[0]]-beginning)*1e9) if len(persistent) else None
            peak=max(0.,float(target-v.min() if k%2==0 else v.max()-target))
            d=case['transient']['edges'][k]
            assert (settle is None)==(d['settle_ns'] is None)
            if settle is not None:
                assert abs(settle-d['settle_ns'])<1e-6
            assert abs(peak-d['overshoot_V'])<1e-10
            deadline=(times>=beginning+500e-9-1e-15)
            results.append({'edge':k+1,'settle_ns':settle,'overshoot_V':peak,
                            'max_error_from_deadline_to_next_edge_V':float(max(abs(v[deadline]-target)))})
        hashes={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in ['tran.txt','stb.txt','transfer.txt','op_nodes.txt']}
        rows.append({'case':case['case'],'edges':results,'raw_sha256':hashes})
    return {'scope':'Independent raw-source waveform and suffix-envelope witnesses; same candidates, no new model trials',
            'run':root.name,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':rows}


def main():
    p=argparse.ArgumentParser();p.add_argument('label');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert a.label.replace('_','').isalnum() and not a.output.exists()
    result=witness(BASE/'evaluations'/a.label)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'cases_verified':len(result['cases']),'run':a.label}))


if __name__=='__main__':
    main()
