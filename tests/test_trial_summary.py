"""Prevent false trial counts and unconfirmed or mismatched electrical verdicts."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('trial_summary', ROOT/'tools/summarize_trials.py')
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


class TrialSummaryTests(unittest.TestCase):
    def setUp(self):
        self.catalog = deepcopy(summary.read(ROOT/'results/catalog.json'))

    def reject(self, message):
        with self.assertRaisesRegex(ValueError, message):
            summary.summarize(self.catalog)

    def row(self, key):
        return next(r for r in self.catalog['evaluations'] if r['key'] == key)

    def test_real_record_counts_sessions_not_reruns(self):
        result = summary.summarize(self.catalog)
        self.assertEqual((result['complete_sessions'], result['baseline_proposals'], result['saved_evaluations']), (7, 17, 24))
        self.assertEqual(len(result['groups']), 6)
        self.assertIsNone(result['population_pass_rate'])
        self.assertIsNone(result['pass_at_k'])
        self.assertIsNone(result['pass_power_k'])
        self.assertEqual(result, summary.read(ROOT/'results/session_summary.json'))

    def test_versions_and_interfaces_stay_separate(self):
        groups = summary.summarize(self.catalog)['groups']
        supply = [g for g in groups if g['task'] == 'supply']
        self.assertEqual({g['recorded_grader']: g['complete_sessions'] for g in supply}, {'eval_core_v3': 1, 'eval_core_v4': 2})
        self.assertEqual(len([g for g in groups if g['task'] == 'load']), 2)
        self.assertTrue(all(g['packet_revision'] == 'recorded' for g in groups))

    def test_duplicate_evaluation_rejected(self):
        self.catalog['evaluations'].append(deepcopy(self.catalog['evaluations'][0]))
        self.reject('Duplicate evaluation')

    def test_duplicate_proposal_rejected(self):
        row = deepcopy(self.catalog['evaluations'][0])
        row['key'] = 'duplicate_proposal'
        self.catalog['evaluations'].append(row)
        self.reject('Missing or duplicate baseline')

    def test_missing_proposal_rejected(self):
        self.catalog['evaluations'] = [r for r in self.catalog['evaluations'] if r['key'] != 'supply_p2_baseline']
        self.reject('Missing or duplicate baseline')

    def test_missing_confirmation_rejected(self):
        self.catalog['evaluations'] = [r for r in self.catalog['evaluations'] if r['key'] != 'load_cli_p1_refined']
        self.reject('finer confirmation')

    def test_changed_confirmation_candidate_rejected(self):
        self.row('load_cli_p1_refined')['candidate'] = self.row('tia_cli_p1_baseline')['candidate']
        self.reject('different candidate')

    def test_numerical_disagreement_rejected(self):
        self.row('load_cli_p1_refined').update(category='specification_failure', score=0)
        self.reject('Numerical profiles disagree')

    def test_settings_drift_rejected(self):
        for field in summary.SETTING_FIELDS:
            with self.subTest(field=field):
                saved = self.row('load_cli_p1_refined')[field]
                self.row('load_cli_p1_refined')[field] = 'changed'
                self.reject('Settings changed')
                self.row('load_cli_p1_refined')[field] = saved

    def test_continuing_after_pass_rejected(self):
        self.row('supply_p1_baseline').update(category='pass', score=100)
        self.reject('continued after')

    def test_premature_failure_stop_rejected(self):
        for key in ('load_cli_p1_baseline', 'load_cli_p1_refined'):
            self.row(key).update(category='specification_failure', score=0)
        self.reject('before its proposal budget')

    def test_wrong_score_rejected(self):
        self.row('load_cli_p1_baseline')['score'] = 0
        self.reject('score disagrees')

    def test_catalog_counter_drift_rejected(self):
        self.catalog['completed_task_trials'] += 1
        self.reject('Catalog totals disagree')

    def test_non_electrical_outcomes_are_not_silently_dropped(self):
        self.row('load_cli_p1_baseline').update(category='infrastructure_error', score=None)
        self.reject('separate attempt ledger')

    def test_candidate_path_escape_rejected(self):
        self.row('load_cli_p1_baseline')['candidate'] = '../unrelated/candidate.sp'
        self.reject('under transcripts')


if __name__ == '__main__':
    unittest.main()
