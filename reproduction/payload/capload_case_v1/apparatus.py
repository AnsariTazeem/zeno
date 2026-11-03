"""Frozen-plant simulation and measurement support; no reference network values."""
import hashlib,json,os,re,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
APP=ROOT/"analog_public_v1"
BAD=re.compile(r"(?im)^\s*error|timestep too small|doAnalyses:.*(?:failed|timestep)|convergence problem|fatal error|simulation interrupted|simulation aborted|segmentation fault")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def crossings(f,y,target):
    hits=np.flatnonzero((y[:-1]>target)&(y[1:]<=target))
    return [float(10**(np.log10(f[i])+(target-y[i])/(y[i+1]-y[i])*(np.log10(f[i+1])-np.log10(f[i])))) for i in hits]

def analyze_loop(folder):
    a=np.loadtxt(folder/'stb.txt',skiprows=1,ndmin=2)
    assert a.shape[1]==3 and np.isfinite(a).all() and np.all(np.diff(a[:,0])>0)
    f,db,ph=a.T
    assert f[0]<=10.00001 and f[-1]>=1e10*(1-1e-6)
    u=crossings(f,db,0)
    margins=[float(180+np.interp(np.log10(x),np.log10(f),ph)-ph[0]) for x in u]
    nodes=(folder/'op_nodes.txt').read_text()
    current=float(re.search(r'(?m)^vsup#branch\s*=\s*([^\s]+)',nodes)[1])
    return {'low_frequency_loop_gain_dB':float(db[0]),'phase_at_low_frequency_deg':float(ph[0]),
            'unity_downward_crossings_Hz':u,'phase_margins_deg':margins,'dc_power_uW':-current*1.2e6}

def analyze_tran(folder,step_s):
    a=np.loadtxt(folder/'tran.txt',skiprows=1,ndmin=2)
    assert a.shape[1]==5 and len(a)>100 and np.isfinite(a).all()
    t,vin,load,drive,current=a.T
    assert np.all(np.diff(t)>0) and t[0]<=1e-15 and t[-1]>=25e-6*(1-1e-7)
    assert np.max(np.diff(t))<=step_s+1e-14
    expected=command_voltage(t)
    assert np.max(np.abs(vin-expected))<=2e-6,'Command source does not match the declared waveform'
    rows=[]
    for n,target in enumerate((1.0,0.8,1.0,0.8)):
        start=(5+5*n)*1e-6;end=start+5e-6
        mask=(t>=start-1e-15)&(t<end-1e-15)
        tt=t[mask];yy=load[mask]
        assert len(tt)>100 and tt[0]<=start+step_s+1e-14 and tt[-1]>=end-2*step_s
        outside=np.flatnonzero(np.abs(yy-target)>0.0005)
        index=outside[-1]+1 if len(outside) else 0
        settle=float((tt[index]-start)*1e6) if index<len(tt) else None
        overshoot=float(max(0,np.max(yy-target if target==1 else target-yy)))
        rows.append({'edge':n+1,'target_V':target,'settle_us':settle,'endpoint_error_V':float(yy[-1]-target),'overshoot_V':overshoot})
    return {'edges':rows,'stop_s':float(t[-1]),'rows':len(t),'max_retained_step_s':float(np.max(np.diff(t))),
            'drive_range_V':[float(drive.min()),float(drive.max())]}

def command_voltage(t):
    t=np.asarray(t);phase=np.mod(t-5e-6,10e-6)
    y=np.where(phase<20e-9,0.8+0.2*phase/20e-9,
        np.where(phase<5e-6,1.0,np.where(phase<5.02e-6,1.0-0.2*(phase-5e-6)/20e-9,0.8)))
    return np.where(t<5e-6,0.8,y)

def run(deck,folder,exe,refined):
    folder.mkdir()
    path=folder/'deck.cir';path.write_text(deck,encoding='utf-8',newline='\n')
    command=[str(exe),'-n','-b','-D','ngbehavior=hsa','-D','ng_nomodcheck',path.name]
    env=os.environ.copy();env['SPICE_SCRIPTS']=str(APP/'sim_scripts')
    (folder/'launch.json').write_text(json.dumps({'started_at_utc':datetime.now(timezone.utc).isoformat(),'command':command,'deck_sha256':sha(path),'refined':refined},indent=2)+'\n')
    started=time.monotonic();timed_out=False
    with (folder/'stdout.txt').open('w',encoding='utf-8') as out,(folder/'stderr.txt').open('w',encoding='utf-8') as err:
        proc=subprocess.Popen(command,cwd=folder,stdout=out,stderr=err,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
        try:proc.wait(timeout=120)
        except subprocess.TimeoutExpired:
            timed_out=True;proc.kill();proc.wait(timeout=10)
    log=(folder/'stdout.txt').read_text(errors='replace')+(folder/'stderr.txt').read_text(errors='replace')
    record={'returncode':proc.returncode,'timed_out':timed_out,'fatal_log_match':bool(BAD.search(log)),'elapsed_seconds':time.monotonic()-started}
    (folder/'completion.json').write_text(json.dumps(record,indent=2)+'\n')
    if timed_out or proc.returncode or record['fatal_log_match']:
        raise RuntimeError('Simulation invalid; inspect '+str(folder))
