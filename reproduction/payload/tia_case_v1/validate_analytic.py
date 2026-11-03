"""Independent closed-form two-pole TIA validation, separate from task plant."""
import argparse
import json
from pathlib import Path
import re

import numpy as np
from apparatus import BASE,sha,save,verify,run,render
from network_input import compile_network


def main():
    p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--rg',type=float);a=p.parse_args()
    assert re.fullmatch(r'[A-Za-z0-9_]+',a.label)
    out=BASE/a.label;out.mkdir(exist_ok=False)
    exe,identity=verify()
    # Exact independent model A(s)=1e4/[(1+s/w1)(1+s/w2)], zero output
    # impedance, and explicitly finite input admittance. This is a trusted
    # analytical test fixture, never a candidate or the transistor task plant.
    f1,f2=1e4,80e6
    ideal=f'''.subckt dut iref inp inn out
Rbias iref 0 10000
Rin inn 0 1e9
Cin inn 0 1p
Efirst e0 0 inp inn 10000
Rp1 e0 n1 1000
Cp1 n1 0 {1/(2*np.pi*1000*f1):.17g}
Ebuffer n2 0 n1 0 1
Rp2 n2 n3 1000
Cp2 n3 0 {1/(2*np.pi*1000*f2):.17g}
Eout out 0 n3 0 1
.ends dut
'''
    rows=[]
    configs=[(10,2,8.2),(150,10,8.2)] if a.rg else [(10,2,1),(150,10,8.2),(70,2,100)]
    for k,(cs,wire,cf) in enumerate(configs):
        folder=out/f'fixture{k:02d}';folder.mkdir()
        point={'id':'case00','sensor_pF':cs,'wire_pF':wire}
        (folder/'case00').mkdir()
        extra=f'Rg sense vref {a.rg:.17g}\n' if a.rg else ''
        network,_=compile_network(f'.subckt feedback sense out vref\nRf out sense 10000\nCf out sense {cf*1e-12:.17g}\n{extra}.ends feedback\n')
        shared=folder/'shared'
        deck=render(ideal,network+'XNET sense out vref feedback\n',[point],shared,refined=True,transient=False)
        deck=re.sub(r'(?m)^\.lib .+\n','',deck)
        run(deck,shared,exe)
        f,db,ph=np.loadtxt(folder/'case00/stb.txt',skiprows=1).T
        zf,zreal,zimag=np.loadtxt(folder/'case00/transfer.txt',skiprows=1).T
        assert np.array_equal(f,zf)
        s=2j*np.pi*f
        amp=10000/((1+1j*f/f1)*(1+1j*f/f2))
        # Sum of sensor shunt + explicit input resistor is 2 nS. Sensor/wire
        # and the ideal test amplifier's 1 pF input cap all participate.
        yin=2e-9+s*(cs+wire+1)*1e-12+(1/a.rg if a.rg else 0)
        yf=1/10000+s*cf*1e-12
        expected_loop=amp*yf/(yin+yf)
        expected_z=-amp/(yin+(1+amp)*yf)
        observed_loop=10**(db/20)*np.exp(1j*ph*np.pi/180)
        observed_z=zreal+1j*zimag
        mask=np.abs(expected_loop)>1e-6
        looperr=float(np.max(np.abs(observed_loop[mask]/expected_loop[mask]-1)))
        zerr=float(np.max(np.abs(observed_z/expected_z-1)))
        assert looperr<1e-5 and zerr<1e-5,(looperr,zerr)
        row={'sensor_pF':cs,'wire_pF':wire,'cf_pF':cf,'Rg_ohm':a.rg,'max_loop_complex_relative_error':looperr,
             'max_transimpedance_complex_relative_error':zerr,
             'stb_sha256':sha(folder/'case00/stb.txt'),'transfer_sha256':sha(folder/'case00/transfer.txt')}
        rows.append(row)
    save(out/'result.json',{'scope':'Independent analytical validation, no task/model trial',
               'derivation':'Yin=Gshunt+Gin+s(Csensor+Cwire+Cin); Yf=1/Rf+sCf; L=A*Yf/(Yin+Yf); Zt=-A/[Yin+(1+A)*Yf].',
               'fixtures':rows,'identity':identity,'script_sha256':sha(__file__)})
    print(json.dumps(rows,indent=2))


if __name__=='__main__':
    main()
