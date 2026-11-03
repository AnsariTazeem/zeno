"""Audit the documented inclusive 10 Hz transfer boundaries before model release."""
import copy,json
from pathlib import Path
from apparatus import BASE,ac_metrics,checks,tran_metrics

def validate():
    source=BASE/'evaluations/reference_rg5000_refined01/case00'
    sample=ac_metrics(source)
    tests=[]
    for imaginary,expected in [(1.,True),(-1.,True),(1.000000001,False),(-1.000000001,False)]:
        ac=copy.deepcopy(sample);ac['dc_transimpedance_imag_ohm']=imaginary
        assert checks(ac)['dc_gain']==expected
        tests.append({'imaginary_ohm':imaginary,'expected_gain_check':expected})
    for real,expected in [(-10100.,True),(-9900.,True),(-10100.000001,False),(-9899.999999,False)]:
        ac=copy.deepcopy(sample);ac['dc_transimpedance_real_ohm']=real
        assert checks(ac)['dc_gain']==expected
        tests.append({'real_ohm':real,'expected_gain_check':expected})
    verified=0
    for label in ['reference_8p2_01','alternative_10p_01','undercompensated_1p_01','reference_rg1000_01',
                  'alternative_rg2000_01','reference_rg5000_01','overcompensated_100p_01',
                  'reference_rg5000_refined01','equivalent_rg5000_01']:
        folder=BASE/'evaluations'/label
        data=json.loads((folder/'result.json').read_text());ident=json.loads((folder/'identity.json').read_text())
        for item in data['cases']:
            f=folder/item['case']['id']
            actual=checks(ac_metrics(f),tran_metrics(f,.25e-9 if ident['refined'] else .5e-9))
            assert actual==item['checks'],(label,item['case'])
            verified+=1
    return {'boundary_tests':tests,'retained_operating_point_verdicts_unchanged':verified,
            'simulations_rerun':0,'model_trials':0}

if __name__=='__main__':
    print(json.dumps(validate(),indent=2))
