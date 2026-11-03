"""Regression for real no-gain data and adversarial missing/corrupt evidence."""
from copy import deepcopy
from pathlib import Path
import json
import shutil
import tempfile
import unittest
import importlib.util
import numpy as np
import supply_adapter as adapter

ROOT = Path(__file__).resolve().parent.parent
BAD = ROOT / 'eval_core_v3/runs/supply/cs02_p2/native'
GOOD = ROOT / 'eval_core_v3/runs/supply/cs01_control/native'
CONTRACT = adapter.read(ROOT / 'analog_supply_pilot_v1/public_v2/contract.json')


class SupplyEvidenceTests(unittest.TestCase):
    def copied(self):
        workspace = Path(__file__).resolve().parent / 'test_workspace'
        workspace.mkdir(exist_ok=True)
        temp = tempfile.TemporaryDirectory(prefix='ev4_', dir=workspace)
        assert Path(temp.name).resolve().is_relative_to(workspace.resolve())
        self.addCleanup(temp.cleanup)
        folder = Path(temp.name) / 'native'
        shutil.copytree(BAD, folder)
        return folder

    def store(self, folder, data):
        (folder / 'result.json').write_text(json.dumps(data), encoding='utf-8')

    def test_actual_completed_no_gain_circuit_scores_zero_without_fake_metrics(self):
        result = adapter.assess(adapter.read(BAD / 'result.json'), CONTRACT, BAD)
        self.assertEqual(result['category'], 'specification_failure')
        self.assertEqual(result['score'], 0)
        self.assertEqual(len(result['points']), 3)
        for point in result['points']:
            self.assertIsNone(point['metrics']['ugf_Hz'])
            self.assertTrue(point['raw_witness']['all_loop_gain_below_zero_certified'])
            self.assertFalse(point['pass'])

    def test_json_only_nulls_stay_unscored(self):
        result = adapter.assess(adapter.read(BAD / 'result.json'), CONTRACT)
        self.assertEqual(result['category'], 'infrastructure_error')
        self.assertIsNone(result['score'])

    def test_passing_reference_preserves_pass(self):
        result = adapter.assess(adapter.read(GOOD / 'result.json'), CONTRACT, GOOD)
        self.assertEqual(result['category'], 'pass')
        self.assertTrue(all(p['pass'] for p in result['points']))

    def test_existing_refined_trace_profile_is_validated(self):
        folder = ROOT / 'eval_core_v3/runs/supply/cs01_r3/native'
        result = adapter.assess(adapter.read(folder / 'result.json'), CONTRACT, folder)
        self.assertEqual(result['category'], 'specification_failure')
        self.assertTrue(all(p['raw_witness']['observed_rows'] == 901 for p in result['points']))

    def test_json_replay_preserves_legacy_categories(self):
        spec = importlib.util.spec_from_file_location('legacy_supply_for_parity', ROOT / 'eval_core_v1/run_eval.py')
        legacy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy)
        for label in ['cs01_control', 'cs01_p1', 'cs01_p2', 'cs01_p3', 'cs02_p1', 'cs02_p2']:
            data = adapter.read(ROOT / 'eval_core_v3/runs/supply' / label / 'native/result.json')
            a, b = adapter.assess(data, CONTRACT), legacy.assess(data, CONTRACT)
            self.assertEqual((a['category'], a['score'], a['success']), (b['category'], b['score'], b['success']))

    def test_truncated_loop_is_not_electrical_failure(self):
        folder = self.copied()
        path = folder / 'eval/opamp_2stg/v115/opamp_loop/stb.txt'
        lines = path.read_text().splitlines()
        path.write_text('\n'.join(lines[:-1]) + '\n')
        self.assertIsNone(adapter.assess(adapter.read(folder / 'result.json'), CONTRACT, folder)['score'])

    def test_nan_loop_is_not_electrical_failure(self):
        folder = self.copied()
        path = folder / 'eval/opamp_2stg/v115/opamp_loop/stb.txt'
        values = np.loadtxt(path, skiprows=1)
        values[4, 1] = np.nan
        np.savetxt(path, values, header='frequency lg_db lg_ph', comments='')
        self.assertIsNone(adapter.assess(adapter.read(folder / 'result.json'), CONTRACT, folder)['score'])

    def test_timed_out_process_is_unscored_even_with_complete_files(self):
        folder = self.copied()
        path = folder / 'eval/opamp_2stg/v120/opamp_loop/completion.json'
        data = adapter.read(path)
        data['timed_out'] = True
        path.write_text(json.dumps(data))
        self.assertIsNone(adapter.assess(adapter.read(folder / 'result.json'), CONTRACT, folder)['score'])

    def test_candidate_identity_cannot_change(self):
        folder = self.copied()
        with (folder / 'candidate_original.sp').open('a') as handle:
            handle.write('* changed candidate\n')
        self.assertIsNone(adapter.assess(adapter.read(folder / 'result.json'), CONTRACT, folder)['score'])

    def test_missing_field_is_not_an_expected_null(self):
        folder = self.copied()
        data = adapter.read(folder / 'result.json')
        del data['points'][0]['metrics']['ugf_Hz']
        self.store(folder, data)
        self.assertIsNone(adapter.assess(data, CONTRACT, folder)['score'])

    def test_reported_gain_must_match_raw_data(self):
        folder = self.copied()
        data = adapter.read(folder / 'result.json')
        data['points'][0]['metrics']['dc_gain_dB'] = 100
        self.store(folder, data)
        self.assertIsNone(adapter.assess(data, CONTRACT, folder)['score'])

    def test_truncated_transient_does_not_gain_a_failure_score(self):
        folder = self.copied()
        path = folder / 'eval/opamp_2stg/v125/opamp_tran/tran.txt'
        lines = path.read_text().splitlines()
        path.write_text('\n'.join(lines[:100]) + '\n')
        self.assertIsNone(adapter.assess(adapter.read(folder / 'result.json'), CONTRACT, folder)['score'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
