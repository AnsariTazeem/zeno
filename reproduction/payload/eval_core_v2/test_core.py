from copy import deepcopy
import unittest
import run_eval as c
LOAD=c.read(c.ROOT/'capload_case_v1/public/contract.json')
GOOD=c.read(c.ROOT/'capload_case_v1/evaluations/reference_compiled_01/result.json')
ALT=c.read(c.ROOT/'capload_case_v1/evaluations/LOAD_T01_P03_refined/result.json')
BAD=c.read(c.ROOT/'capload_case_v1/evaluations/starter_compiled_01/result.json')
def grade(d):return c.assess_load(d,LOAD)
class CoreTests(unittest.TestCase):
 def test_reference_alternative_and_starter(self):
  self.assertTrue(grade(GOOD)['success']);self.assertTrue(grade(ALT)['success'])
  self.assertEqual(grade(BAD)['category'],'specification_failure')
 def test_equivalent_row_edge_orders(self):
  d=deepcopy(GOOD);d['cases'].reverse()
  for x in d['cases']:x['transient']['edges'].reverse()
  self.assertTrue(grade(d)['success'])
 def test_one_bad_margin_among_multiple_crossings_fails(self):
  d=deepcopy(GOOD);a=d['cases'][0]['ac'];a['unity_downward_crossings_Hz']=[1e6,2e6];a['phase_margins_deg']=[80,49]
  self.assertEqual(grade(d)['category'],'specification_failure')
 def test_no_crossing_fails_electrically(self):
  d=deepcopy(GOOD);d['cases'][0]['ac']['unity_downward_crossings_Hz']=[];d['cases'][0]['ac']['phase_margins_deg']=[]
  self.assertEqual(grade(d)['category'],'specification_failure')
 def test_settling_overshoot_and_power_regressions_fail(self):
  for key,value in [('settle_us',2.51),('overshoot_V',.011)]:
   d=deepcopy(GOOD);d['cases'][2]['transient']['edges'][3][key]=value
   self.assertFalse(grade(d)['success'])
  d=deepcopy(GOOD);d['cases'][0]['ac']['dc_power_uW']=351;self.assertFalse(grade(d)['success'])
 def test_none_settling_valid_fail_missing_settling_invalid(self):
  d=deepcopy(GOOD);d['cases'][0]['transient']['edges'][0]['settle_us']=None
  self.assertEqual(grade(d)['category'],'specification_failure')
  del d['cases'][0]['transient']['edges'][0]['settle_us']
  self.assertEqual(grade(d)['category'],'infrastructure_error')
 def test_aggregate_pass_flags_cannot_override_data(self):
  d=deepcopy(BAD);d['all_six_points_pass']=True;d['score']=100
  for row in d['cases']:row['pass']=True;row['checks']={k:True for k in row['checks']}
  self.assertFalse(grade(d)['success'])
 def test_truncated_time_or_grid_is_invalid(self):
  d=deepcopy(GOOD);d['cases'][0]['transient']['stop_s']=20e-6
  self.assertEqual(grade(d)['category'],'infrastructure_error')
  d=deepcopy(GOOD);d['cases'].pop();self.assertIsNone(grade(d)['score'])
 def test_duplicate_grid_or_edge_is_invalid(self):
  d=deepcopy(GOOD);d['cases'][5]=deepcopy(d['cases'][0]);self.assertIsNone(grade(d)['score'])
  d=deepcopy(GOOD);d['cases'][0]['transient']['edges'][3]['edge']=1;self.assertIsNone(grade(d)['score'])
 def test_nonfinite_and_boolean_data_invalid(self):
  for val in [float('nan'),float('inf'),True]:
   d=deepcopy(GOOD);d['cases'][0]['ac']['phase_margins_deg'][0]=val;self.assertIsNone(grade(d)['score'])
 def test_wrong_source_target_invalid(self):
  d=deepcopy(GOOD);d['cases'][0]['transient']['edges'][0]['target_V']=.9;self.assertIsNone(grade(d)['score'])
 def test_simulation_error_is_not_electrical_failure(self):
  self.assertEqual(grade({'outcome':'simulation_or_measurement_invalid'})['category'],'infrastructure_error')
 def test_model_alternative_and_renamed_network_compile(self):
  t=(c.ROOT/'capload_case_v1/trials/trial01/proposal03/candidate_rendered.sp').read_text()
  a,ac=c.compile_candidate('load',t);b,bc=c.compile_candidate('load','* equivalent\n'+t.upper())
  self.assertEqual(a,b);self.assertEqual(ac,bc)
 def test_directives_rejected(self):
  with self.assertRaises(ValueError):c.compile_candidate('load','.subckt feedback drive load fb\n.include nope\n.ends feedback')
 def test_supply_adapter_regression(self):
  contract=c.read(c.ROOT/'analog_supply_pilot_v1/public_v2/contract.json')
  good=c.read(c.ROOT/'analog_supply_pilot_v1/runs/calibration_compiled_01/result.json')
  bad=c.read(c.ROOT/'analog_supply_pilot_v1/runs/t5r3/result.json')
  self.assertTrue(c.assess('supply',good,contract)['success']);self.assertFalse(c.assess('supply',bad,contract)['success'])
 def test_task_exports_do_not_include_private_answers(self):
  self.assertEqual(len(c.TASKS['load']['files']),7)
  for task in c.TASKS.values():
   self.assertFalse(any('private' in x or 'reference' in x for x in task['files']))
if __name__=='__main__':unittest.main(verbosity=2)
