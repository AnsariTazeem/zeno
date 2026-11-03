"""TIA measurement and trusted fixture rendering; no reference network values."""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

import numpy as np

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
APP=ROOT/'analog_public_v1'
BAD=re.compile(r'(?im)^\s*error|timestep too small|doAnalyses:.*(?:failed|timestep)|convergence problem|fatal error|simulation interrupted|simulation aborted|segmentation fault')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p,obj):
    Path(p).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def verify():
    counts={}
    for name,root,key in [('upstream_manifest.json',APP/'upstream','path'),('model_manifest.json',APP/'deps/pdk','file')]:
        files=json.loads((APP/name).read_text())['files']
        assert all(sha(root/x[key])==x['sha256'] for x in files),name
        counts[name]=len(files)
    sm=json.loads((APP/'windows_simulator_manifest.json').read_text())
    exe=APP/sm['exe'];assert sha(exe)==sm['exe_sha256']
    return exe,{**counts,'simulator_sha256':sm['exe_sha256']}


def run(deck,folder,exe):
    folder.mkdir(parents=True,exist_ok=False)
    path=folder/'deck.cir';path.write_text(deck,encoding='utf-8',newline='\n')
    command=[str(exe),'-n','-b','-D','ngbehavior=hsa','-D','ng_nomodcheck',path.name]
    env=os.environ.copy();env['SPICE_SCRIPTS']=str(APP/'sim_scripts')
    save(folder/'launch.json',{'started_at_utc':datetime.now(timezone.utc).isoformat(),'command':command,
                             'deck_sha256':sha(path),'simulator_sha256':sha(exe)})
    started=time.monotonic();timed_out=False
    with (folder/'stdout.txt').open('w',encoding='utf-8') as stdout,(folder/'stderr.txt').open('w',encoding='utf-8') as stderr:
        proc=subprocess.Popen(command,cwd=folder,stdout=stdout,stderr=stderr,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            proc.wait(timeout=180)
        except subprocess.TimeoutExpired:
            timed_out=True;proc.kill();proc.wait(timeout=10)
    log=(folder/'stdout.txt').read_text(errors='replace')+(folder/'stderr.txt').read_text(errors='replace')
    record={'returncode':proc.returncode,'timed_out':timed_out,'fatal_log_match':bool(BAD.search(log)),
            'elapsed_seconds':time.monotonic()-started}
    save(folder/'completion.json',record)
    if timed_out or proc.returncode or record['fatal_log_match']:
        raise RuntimeError('Simulation invalid: '+str(folder))


def crossings(f,y,target):
    hits=np.flatnonzero((y[:-1]>target)&(y[1:]<=target))
    return [float(10**(np.log10(f[i])+(target-y[i])/(y[i+1]-y[i])*(np.log10(f[i+1])-np.log10(f[i])))) for i in hits]


def load_ac(p,columns):
    a=np.loadtxt(p,skiprows=1,ndmin=2)
    assert a.shape[1]==columns and np.isfinite(a).all() and np.all(np.diff(a[:,0])>0)
    assert a[0,0]<=10.00001 and a[-1,0]>=1e10*(1-1e-8),'Incomplete AC sweep'
    return a


def ac_metrics(folder):
    f,db,ph=load_ac(folder/'stb.txt',3).T
    unity=crossings(f,db,0)
    margins=[float(180+np.interp(np.log10(x),np.log10(f),ph)-ph[0]) for x in unity]
    ft,zreal,zimag=load_ac(folder/'transfer.txt',3).T
    z=zreal+1j*zimag;mag=np.abs(z);mdb=20*np.log10(mag)
    assert np.isfinite(mdb).all() and mag[0]>0
    bw=crossings(ft,mdb,mdb[0]-3)
    assert bw,'No measured -3 dB crossing'
    peak=float(np.max(mdb)-mdb[0])
    nodes=(folder/'op_nodes.txt').read_text()
    def value(name):
        return float(re.search(r'(?m)^'+re.escape(name)+r'\s*=\s*(\S+)',nodes)[1])
    power=max(0.,-value('vsup#branch')*1.2e6)+max(0.,-value('vref#branch')*.9e6)
    return {'dc_transimpedance_real_ohm':float(zreal[0]),'dc_transimpedance_imag_ohm':float(zimag[0]),
            'first_minus_3dB_Hz':bw[0],'all_minus_3dB_crossings_Hz':bw,'response_peak_dB':peak,
            'phase_at_low_frequency_deg':float(ph[0]),'low_frequency_loop_gain_dB':float(db[0]),
            'unity_downward_crossings_Hz':unity,'phase_margins_deg':margins,'dc_delivered_power_uW':power}


def stimulus(t):
    t=np.asarray(t)
    q=np.mod(t-1e-6,2e-6)
    return np.where(t<1e-6,0.,np.where(q<5e-9,20e-6*q/5e-9,
                    np.where(q<1e-6,20e-6,np.where(q<1.005e-6,20e-6*(1-(q-1e-6)/5e-9),0.))))


def tran_metrics(folder,max_step):
    a=np.loadtxt(folder/'tran.txt',skiprows=1,ndmin=2)
    assert a.shape[1]==6 and len(a)>100 and np.isfinite(a).all()
    t,current,sense,out,vsup,vref=a.T
    assert np.all(np.diff(t)>0) and abs(t[0])<1e-15 and t[-1]>=5e-6-1e-15
    assert np.diff(t).max()<=max_step+2e-16,'Transient gaps'
    assert np.max(np.abs(current-stimulus(t)))<=1e-12,'Wrong current waveform'
    edges=[]
    for n,target in enumerate([.7,.9,.7,.9]):
        start=(n+1)*1e-6;end=start+1e-6
        mask=(t>=start-1e-15)&(t<end-1e-15)
        tt,yy=t[mask],out[mask]
        assert len(tt)>100 and tt[0]<=start+max_step+2e-16 and tt[-1]>=end-2*max_step
        bad=np.flatnonzero(np.abs(yy-target)>.001)
        j=bad[-1]+1 if len(bad) else 0
        settle=float((tt[j]-start)*1e9) if j<len(tt) else None
        overshoot=float(max(0.,np.max(target-yy if target==.7 else yy-target)))
        edges.append({'edge':n+1,'target_V':target,'settle_ns':settle,
                      'endpoint_error_V':float(yy[-1]-target),'overshoot_V':overshoot})
    return {'initial_error_V':float(out[0]-.9),'edges':edges,'rows':len(t),'stop_s':float(t[-1]),
            'max_retained_step_s':float(np.diff(t).max()),'sense_range_V':[float(sense.min()),float(sense.max())]}


def checks(ac,tr=None):
    c={'dc_gain':abs(ac['dc_transimpedance_real_ohm']+10000)<=100 and abs(ac['dc_transimpedance_imag_ohm'])<=1,
       'bandwidth':ac['first_minus_3dB_Hz']>=1e6,
       'valid_loop':bool(ac['phase_margins_deg']) and abs(ac['phase_at_low_frequency_deg'])<90 and ac['low_frequency_loop_gain_dB']>0,
       'phase_margin':bool(ac['phase_margins_deg']) and min(ac['phase_margins_deg'])>=55,
       'power':0<ac['dc_delivered_power_uW']<=300}
    if tr is not None:
        c.update({'initial_accuracy':abs(tr['initial_error_V'])<=.001,
                  'settling':all(x['settle_ns'] is not None and x['settle_ns']<=500 for x in tr['edges']),
                  'overshoot':all(x['overshoot_V']<=.01 for x in tr['edges'])})
    return c


def render(plant,network,points,shared,refined=False,transient=True,screen=False):
    library=os.path.relpath(APP/'deps/pdk/sky130A/libs.tech/combined/sky130.lib.spice',shared).replace('\\','/')
    assert ' ' not in library
    density,step,rel,vnt,abt=(200,'250p','1e-5','1e-8','1e-14') if refined else (100,'500p','1e-4','1e-7','1e-13')
    # The sense voltage is copied to a high-input-impedance witness; its series
    # photocurrent source therefore exports the actual stimulus without a sign guess.
    text=f'''* TIA-P01 trusted testbench
.lib "{library}" tt
.global vdd
.options reltol={rel} gmin=1e-12 vntol={vnt} abstol={abt}
.temp 27
{plant}
{network}
VSUP vdd 0 dc 1.2
VREF vref 0 dc .9
IREF vdd niref dc 20u
IPD 0 photo dc 10u ac 0 PULSE(0 20u 1u 5n 5n .995u 2u)
VPHOTO photo sense 0
XDUT niref vref ainn out dut
Csensor sense 0 150p
Cwire sense 0 10p
Rshunt sense vref 1e9
Cload out 0 2p
Vprb_b prb_n1 sense 0
Vprb_inj prb_n1 prb_n2 0 ac 1
Vprb_a prb_n2 ainn 0
Iprb_inj 0 prb_n1 0 ac 0
.control
set wr_singlescale
set wr_vecnames
option numdgt=12
'''
    for i,c in enumerate(points):
        name=c['id']
        text+=f'alter Csensor {c["sensor_pF"]*1e-12:.17g}\nalter Cwire {c["wire_pF"]*1e-12:.17g}\n'
        if screen:
            text+=f'alter Cscreen {c["cf_pF"]*1e-12:.17g}\n'
        text+=f'''alter IPD dc=10u
alter IPD acmag=0
alter Vprb_inj acmag=1
alter Iprb_inj acmag=0
op
print all > ../{name}/op_nodes.txt
ac dec {density} 10 10G
let lg_tv = -v(prb_n1)/v(prb_n2)
alter Vprb_inj acmag=0
alter Iprb_inj acmag=1
ac dec {density} 10 10G
let lg_ti = i(Vprb_b)/i(Vprb_a)
let tv = ac{3*i+1}.lg_tv
let loopgain = (tv*lg_ti - 1)/(tv + lg_ti + 2)
let lg_db = db(loopgain)
let lg_ph = 180/pi*cph(loopgain)
wrdata ../{name}/stb.txt lg_db lg_ph
alter Iprb_inj acmag=0
alter IPD acmag=1
ac dec {density} 10 10G
let zreal = real(v(out))
let zimag = imag(v(out))
wrdata ../{name}/transfer.txt zreal zimag
alter IPD acmag=0
alter IPD dc=0
'''
        if transient:
            text+=f'tran {step} 5u 0 {step}\nwrdata ../{name}/tran.txt i(VPHOTO) v(sense) v(out) i(VSUP) i(VREF)\n'
    return text+'.endc\n.end\n'
