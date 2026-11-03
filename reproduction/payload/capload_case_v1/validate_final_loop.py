"""Compare the loop probe against independently solved linear nodal equations.

The ideal two-pole test amplifier is ONLY an oracle-validation fixture, never
the transistor-level task plant. No PDK is required for these small tests.
"""
import json
from pathlib import Path
import numpy as np
from apparatus import APP,BASE,sha,run
NETWORKS={
'direct':'Riso drive load 1\nRfb drive fb 1\n',
'gaintrim':'Riso drive load 1000\nRfb drive fb 1000\nRg fb 0 100000\n',
'snubber':'Riso drive load 1\nRfb drive fb 1\nRsn drive nsn 100\nCsn nsn 0 3.3e-10\n'}

OUT=BASE/'loop_validation_02'
assert not OUT.exists()
OUT.mkdir()
sm=json.loads((APP/'windows_simulator_manifest.json').read_text());exe=APP/sm['exe'];assert sha(exe)==sm['exe_sha256']
rows=[]
for variant in ('direct','gaintrim','snubber'):
    folder=OUT/variant
    network=NETWORKS[variant]
    c1=1/(2*np.pi*1000*1e4);c2=1/(2*np.pi*1000*50e6)
    deck=f'* Analytically solvable validation fixture, NOT the evaluation plant\n.subckt ideal inp inn out\nEerr err 0 inp inn 10000\nRdom err d1 1000\nCdom d1 0 {c1:.16g}\nEbuf1 b1 0 d1 0 1\nRp2 b1 d2 1000\nCp2 d2 0 {c2:.16g}\nEbuf2 buf 0 d2 0 1\nRout buf out 50\nRin inn 0 10000000\n.ends ideal\nVIN nin 0 dc 0\nXamp nin nampfb drive ideal\n{network}Rload load 0 100000\nCload load 0 150p\nCstray fb 0 1p\nVprb_b prb_n1 fb 0\nVprb_inj prb_n1 prb_n2 0 ac 1\nVprb_a prb_n2 nampfb 0\nIprb_inj 0 prb_n1 0 ac 0\n.control\nset wr_singlescale\nset wr_vecnames\noption numdgt=12\nac dec 50 10 10G\nlet lg_tv = -v(prb_n1)/v(prb_n2)\nalter Vprb_inj acmag=0\nalter Iprb_inj acmag=1\nac dec 50 10 10G\nlet lg_ti = i(Vprb_b)/i(Vprb_a)\nlet tv = ac1.lg_tv\nlet loopgain = (tv*lg_ti - 1)/(tv + lg_ti + 2)\nlet lg_db = db(loopgain)\nlet lg_ph = 180/pi*cph(loopgain)\nwrdata stb.txt lg_db lg_ph\n.endc\n.end\n'
    run(deck,folder,exe,False)
    data=np.loadtxt(folder/'stb.txt',skiprows=1)
    assert data.shape[1]==3 and np.isfinite(data).all()
    branches=[(t[0][0].upper(),t[1],t[2],float(t[3])) for t in (line.split() for line in network.splitlines())]
    branches += [('R','load','0',100000),('C','load','0',150e-12),('C','fb','0',1e-12),('R','fb','0',1e7)]
    nodes=sorted({n for _,a,b,_ in branches for n in (a,b) if n!='0'});idx={n:i for i,n in enumerate(nodes)}
    expected=[]
    for f in data[:,0]:
        s=2j*np.pi*f;y=np.zeros((len(nodes),len(nodes)),complex);rhs=np.zeros(len(nodes),complex)
        for kind,a,b,v in branches:
            adm=1/v if kind=='R' else s*v
            if a!='0':y[idx[a],idx[a]]+=adm
            if b!='0':y[idx[b],idx[b]]+=adm
            if a!='0' and b!='0':y[idx[a],idx[b]]-=adm;y[idx[b],idx[a]]-=adm
        y[idx['drive'],idx['drive']]+=1/50;rhs[idx['drive']]+=1/50
        beta=np.linalg.solve(y,rhs)[idx['fb']]
        expected.append(10000/((1+s/(2*np.pi*1e4))*(1+s/(2*np.pi*50e6)))*beta)
    expected=np.asarray(expected)
    db=20*np.log10(np.abs(expected));phase=np.angle(expected,deg=True)
    mask=(db>=-40)&(db<=40)
    db_error=float(np.max(np.abs(data[mask,1]-db[mask])))
    phase_error=float(np.max(np.abs(np.angle(np.exp(1j*np.deg2rad(data[mask,2]-phase[mask])),deg=True))))
    ok=db_error<=0.01 and phase_error<=0.1
    row={'variant':variant,'max_gain_error_dB_near_crossover':db_error,'max_phase_error_deg_near_crossover':phase_error,
         'gain_tolerance_dB':0.01,'phase_tolerance_deg':0.1,'pass':ok}
    rows.append(row)
    np.savetxt(folder/'independent_mna.txt',np.column_stack([data[:,0],db,phase]),header='Hz gain_dB phase_deg')
report={'purpose':'Mathematical oracle check, not evaluation-plant qualification','method':'Independent complex nodal solve plus exact two-pole forward transfer; comparison over -40..+40 dB return ratio',
        'runner_sha256':sha(Path(__file__)),'apparatus_source_sha256':sha(BASE/'apparatus.py'),'cases':rows,'all_pass':all(x['pass'] for x in rows)}
(OUT/'result.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert report['all_pass'],'Loop measurement disagrees with the analytic fixture; do not qualify the new task yet'
