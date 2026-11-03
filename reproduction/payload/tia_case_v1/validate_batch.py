"""Check multi-point plot indexing against exact TIA responses at every position."""
import json
import re
import numpy as np
from apparatus import BASE,sha,save,verify,run,render
from network_input import compile_network

out=BASE/'analytic_batch_validation01';out.mkdir(exist_ok=False)
exe,identity=verify()
old=(BASE/'analytic_validation02/fixture00/shared/deck.cir').read_text()
plant=re.search(r'(?ms)^\.subckt dut .*?^\.ends dut\s*$',old)[0]
network,_=compile_network((BASE/'private/shaped_rg5000.sp').read_text())
points=[{'id':f'case{i:02d}','sensor_pF':cs,'wire_pF':wire} for i,(cs,wire) in enumerate([(10,2),(70,10),(150,10)])]
for c in points:
    (out/c['id']).mkdir()
deck=render(plant,network+'XNET sense out vref feedback\n',points,out/'shared',refined=True,transient=False)
deck=re.sub(r'(?m)^\.lib .+\n','',deck)
run(deck,out/'shared',exe)
rows=[]
for c in points:
    f,db,ph=np.loadtxt(out/c['id']/'stb.txt',skiprows=1).T
    ft,zreal,zimag=np.loadtxt(out/c['id']/'transfer.txt',skiprows=1).T
    assert np.array_equal(f,ft)
    s=2j*np.pi*f
    amp=1e4/((1+1j*f/1e4)*(1+1j*f/80e6))
    yin=2e-9+1/5000+s*(c['sensor_pF']+c['wire_pF']+1)*1e-12
    yf=1/10000+s*8.2e-12
    expected_loop=amp*yf/(yin+yf);expected_z=-amp/(yin+(1+amp)*yf)
    observed_loop=10**(db/20)*np.exp(1j*ph*np.pi/180)
    mask=abs(expected_loop)>1e-6
    looperr=float(np.max(abs(observed_loop[mask]/expected_loop[mask]-1)))
    zerr=float(np.max(abs((zreal+1j*zimag)/expected_z-1)))
    assert looperr<1e-5 and zerr<1e-5
    rows.append({'case':c,'max_loop_complex_relative_error':looperr,'max_transimpedance_complex_relative_error':zerr,
                 'stb_sha256':sha(out/c['id']/'stb.txt'),'transfer_sha256':sha(out/c['id']/'transfer.txt')})
save(out/'result.json',{'scope':'Analytical multi-point batch-index validation, not model/task evidence',
          'fixtures':rows,'script_sha256':sha(__file__),'identity':identity})
print(json.dumps(rows,indent=2))
