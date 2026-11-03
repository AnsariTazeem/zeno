"""Physical failure fixtures and network abuse checks; no simulator launches."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
from apparatus import BASE,sha,save,stimulus,tran_metrics,ac_metrics,checks
from network_input import compile_network,InvalidNetwork


def main():
    p=argparse.ArgumentParser();p.add_argument('--label',default='validation_fixtures02');args=p.parse_args()
    assert args.label.replace('_','').isalnum()
    out=BASE/args.label;out.mkdir(exist_ok=False)
    valid='.subckt feedback sense out vref\nRf out sense 10000\nCf out sense 8.2e-12\n.ends feedback\n'
    canonical,counts=compile_network(valid)
    equivalent='* case and spacing independent\n.SUBCKT feedback sense out vref\nrF sense out 1e4\ncF sense out 8.2E-12\n.ENDS feedback\n'
    compile_network(equivalent)
    # A valid split resistor path plus reference-port compensation is allowed.
    compound='.subckt feedback sense out vref\nRa out a 5000\nRb a sense 5000\nCf out sense 8.2e-12\nCr sense vref 1e-15\n.ends feedback\n'
    compiled,_=compile_network(compound)
    assert 'net_a' in compiled
    attacks={
        'include':valid.replace('Rf out sense 10000','.include secret.lib'),
        'control':valid.replace('Rf out sense 10000','.control'),
        'voltage_source':valid.replace('Rf out sense 10000','Vx out sense 1'),
        'expression':valid.replace('10000','{10000}'),
        'suffix':valid.replace('10000','10k'),
        'negative':valid.replace('10000','-10000'),
        'nan':valid.replace('10000','NaN'),
        'infinity':valid.replace('10000','1e999'),
        'zero_resistance':valid.replace('10000','0'),
        'same_node':valid.replace('Rf out sense','Rf out out'),
        'duplicate':valid.replace('Cf out sense','Rf out sense'),
        'wrong_header':valid.replace('sense out vref','out sense vref',1),
        'extra_subcircuit':valid.replace('.ends feedback','.ends feedback\n.subckt other a b'),
        'path_injection':valid.replace('Rf out sense','Rf ../../bad sense'),
        'reserved_instance':valid.replace('Rf out sense','Bscript out sense'),
        'too_many_components':valid.replace('.ends feedback','\n'.join(f'R{i} sense out 10000' for i in range(9))+'\n.ends feedback'),
        'no_output_port':valid.replace('out','different'),
        'too_many_private_nodes':valid.replace('.ends feedback','\n'.join(f'C{i} n{i*2} n{i*2+1} 1e-12' for i in range(8))+'\nCz z sense 1e-12\n.ends feedback')
    }
    rejected=[]
    for name,text in attacks.items():
        try:
            compile_network(text)
        except InvalidNetwork:
            rejected.append(name)
        else:
            raise AssertionError('Unsafe input accepted: '+name)
    # Uniform raw-source fixture: exact declared pulse and ideal current-to-voltage
    # waveform. This fixture tests measurement logic, not feasibility of the plant.
    t=np.arange(10001)*.5e-9
    current=stimulus(t)
    data=np.column_stack([t,current,np.full_like(t,.9),.9-10000*current,
                          np.full_like(t,-200e-6),np.zeros_like(t)])
    cases=[]
    def attempt(name,a,expected):
        folder=out/name;folder.mkdir()
        np.savetxt(folder/'tran.txt',a,header='time i(vphoto) v(sense) v(out) i(vsup) i(vref)',comments='',fmt='%.12e')
        try:
            result=tran_metrics(folder,.5e-9)
            passed=abs(result['initial_error_V'])<=.001 and all(x['settle_ns'] is not None and x['settle_ns']<=500 and x['overshoot_V']<=.01 for x in result['edges'])
            outcome='pass' if passed else 'electrical_failure'
        except (AssertionError,ValueError,IndexError):
            outcome='measurement_invalid';result=None
        assert outcome==expected,(name,outcome,expected)
        cases.append({'name':name,'expected':expected,'observed':outcome,'metrics':result,'sha256':sha(folder/'tran.txt')})
    attempt('valid_ideal_command',data,'pass')
    a=data.copy();a[:,3]+=.0025;attempt('wrong_equilibrium',a,'electrical_failure')
    a=data.copy();a[(t>=1.8e-6)&(t<1.9e-6),3]+=.004;attempt('late_excursion',a,'electrical_failure')
    a=data.copy();a[t>=4.7e-6,3]+=.004;attempt('fourth_edge_only',a,'electrical_failure')
    a=data.copy();a[(t>=1.1e-6)&(t<1.12e-6),3]-=.012;attempt('overshoot_only',a,'electrical_failure')
    a=data.copy();a[np.argmin(abs(t-1.002e-6)),3]=.68
    attempt('overshoot_before_ramp_end',a,'electrical_failure')
    a=data.copy();a[:,1]*=-1;attempt('wrong_source_sign',a,'measurement_invalid')
    a=data.copy();a[5000,3]=np.nan;attempt('nan_voltage',a,'measurement_invalid')
    a=data.copy();a[5000,0]=a[4999,0];attempt('duplicate_time',a,'measurement_invalid')
    attempt('truncated',data[:-5],'measurement_invalid')
    attempt('gap',np.delete(data,np.arange(4000,4010),axis=0),'measurement_invalid')
    attempt('missing_column',data[:,:-1],'measurement_invalid')
    # First/last correct samples alone cannot hide an error after the deadline.
    a=data.copy();a[(t>=3.6e-6)&(t<3.65e-6),3]+=.003
    attempt('correct_endpoint_late_failure',a,'electrical_failure')
    # Synthetic independently known AC traces target sign, magnitude, bandwidth
    # and missing-sweep checks. They are measurement fixtures, not plant data.
    freq=np.logspace(1,10,901)
    amp=1e4/((1+1j*freq/1e3)*(1+1j*freq/40e6))
    ac_cases=[]
    for name,gain,bw,expect in [('valid',-10000,2e6,{'dc_gain':True,'bandwidth':True}),
                              ('wrong_sign',10000,2e6,{'dc_gain':False}),
                              ('wrong_gain',-9000,2e6,{'dc_gain':False}),
                              ('too_slow',-10000,.5e6,{'bandwidth':False})]:
        folder=out/('ac_'+name);folder.mkdir()
        z=gain/(1+1j*freq/bw)
        np.savetxt(folder/'stb.txt',np.column_stack([freq,20*np.log10(abs(amp)),np.unwrap(np.angle(amp))*180/np.pi]),header='frequency lg_db lg_ph',comments='',fmt='%.12e')
        np.savetxt(folder/'transfer.txt',np.column_stack([freq,z.real,z.imag]),header='frequency zreal zimag',comments='',fmt='%.12e')
        (folder/'op_nodes.txt').write_text('vsup#branch = -0.0002\nvref#branch = 0\n')
        metrics=ac_metrics(folder);observed=checks(metrics)
        assert all(observed[k]==v for k,v in expect.items()),name
        ac_cases.append({'name':name,'checks':observed,'expected_checks':expect})
    save(out/'result.json',{'accepted_valid_topologies':3,'rejected_unsafe_inputs':rejected,
                          'transient_fixtures':cases,'AC_fixtures':ac_cases,
                          'model_calls':0,'script_sha256':sha(__file__),'apparatus_sha256':sha(BASE/'apparatus.py')})
    print(json.dumps({'valid_inputs':3,'rejected_inputs':len(rejected),'transient_fixtures':len(cases),'AC_fixtures':len(ac_cases)}))


if __name__=='__main__':
    main()
