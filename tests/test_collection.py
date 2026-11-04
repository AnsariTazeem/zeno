"""Exercise collection freezes, denominators, terminal outcomes and feedback boundaries."""
from pathlib import Path
import importlib.util
import json
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('collection', ROOT/'tools/collect_trials.py')
collection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collection)


class CollectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = ROOT/'.local-checks'
        parent.mkdir(exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix='collection_', dir=parent)
        cls.root = Path(cls.temp.name)
        for folder in ('tasks', 'reproduction'):
            shutil.copytree(ROOT/folder, cls.root/folder,
                            ignore=shutil.ignore_patterns('__pycache__', 'cache', '.venv'))
        (cls.root/'tools').mkdir()
        for name in ('collect_trials.py', 'export_task.py', 'audit_publication.py'):
            shutil.copyfile(ROOT/'tools'/name, cls.root/'tools'/name)
        shutil.copyfile(ROOT/'run_eval.py', cls.root/'run_eval.py')
        cls.prepared = cls.root/'prepared'
        (cls.prepared/'eval_core_v4').mkdir(parents=True)
        shutil.copyfile(ROOT/'reproduction/payload/eval_core_v4/dependency_lock.json', cls.prepared/'eval_core_v4/dependency_lock.json')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.name = self._testMethodName
        self.folder = collection.prepare(self.name[-32:], 'requested-model', 'high', 'text-only', root=self.root)
        collection.start(self.folder, 'trial01', root=self.root)
        self.response = self.folder/'answer.txt'
        self.response.write_text('```spice\n.subckt dut iref inp inn out\n.ends dut\n```\n', encoding='utf-8')
        self.calls = []

    def evaluator(self, prepared, task, candidate, run_id, proposal, refined):
        self.calls.append({'candidate': candidate.read_bytes(), 'refined': refined})
        return {'category': 'pass', 'score': 100, 'points': []}, {'run_id': run_id}

    def record(self, evaluator=None, trial='trial01'):
        return collection.record(self.folder, self.response, self.prepared, trial,
                                 root=self.root, evaluator=evaluator or self.evaluator)

    def test_balanced_schedule_and_private_output(self):
        plan = collection.verify(self.folder, self.root)
        self.assertEqual([r['task'] for r in plan['schedule']],
                         ['supply', 'load', 'tia', 'load', 'tia', 'supply', 'tia', 'supply', 'load'])
        self.assertEqual(self.folder.parent.name, '.local-trials')
        self.assertEqual(plan['proposal_budget'], 3)
        self.assertFalse(plan['separately_billed_API_fallback'])

    def test_only_public_packet_and_request_are_model_visible(self):
        plan = collection.verify(self.folder, self.root)
        catalog = collection.read(self.root/'tasks/catalog.json')
        entries = catalog['revisions'][plan['packet_revision']]['tasks']
        for slot in plan['schedule']:
            names = set(slot['input_files'])
            self.assertEqual(names, {r['name'] for r in entries[slot['task']]['files']} | {'request.txt'})
            request = (self.folder/'inputs'/slot['trial']/'request.txt').read_text()
            self.assertNotIn(str(self.root), request)
            self.assertIn('Do not use tools', request)

    def test_invalid_names_and_existing_campaign_are_rejected(self):
        with self.assertRaises(ValueError):
            collection.campaign_path('../outside', self.root)
        with self.assertRaises(FileExistsError):
            collection.prepare(self.name[-32:], 'm', 'e', 'i', root=self.root)

    def test_changed_protocol_is_rejected(self):
        with (self.folder/'protocol.json').open('a') as stream:
            stream.write(' ')
        with self.assertRaisesRegex(ValueError, 'protocol changed'):
            self.record()
        self.assertEqual(self.calls, [])

    def test_changed_packet_is_rejected(self):
        (self.folder/'inputs/trial01/request.txt').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'input changed'):
            self.record()
        self.assertEqual(self.calls, [])

    def test_changed_source_is_rejected(self):
        path = self.root/'run_eval.py'
        before = path.read_bytes()
        try:
            path.write_bytes(before+b'\n')
            with self.assertRaisesRegex(ValueError, 'source changed'):
                self.record()
        finally:
            path.write_bytes(before)
        self.assertEqual(self.calls, [])

    def test_wrong_trial_is_rejected_before_import(self):
        with self.assertRaisesRegex(ValueError, 'active trial'):
            self.record(trial='trial02')
        self.assertFalse((self.folder/'attempts/trial01/proposal1').exists())

    def test_format_errors_consume_budget(self):
        self.response.write_text('No circuit provided.')
        outcomes = [self.record()['outcome'] for _ in range(3)]
        self.assertEqual(outcomes, ['continue', 'continue', 'no_confirmed_pass'])
        self.assertEqual(self.calls, [])
        state = collection.status(self.folder, self.root)
        self.assertEqual(state['groups'][0]['complete_episodes'], 1)
        self.assertEqual(state['groups'][0]['successful_episodes'], 0)
        self.assertIsNone(state['groups'][0]['estimates'])

    def test_pass_requires_same_candidate_finer_confirmation(self):
        result = self.record()
        self.assertEqual(result['outcome'], 'confirmed_pass')
        self.assertEqual([r['refined'] for r in self.calls], [False, True])
        self.assertEqual(self.calls[0]['candidate'], self.calls[1]['candidate'])

    def test_disagreement_stops_campaign(self):
        def evaluate(*args):
            result, receipt = self.evaluator(*args)
            if args[-1]:
                result.update(category='specification_failure', score=0)
            return result, receipt
        self.assertEqual(self.record(evaluate)['outcome'], 'numerical_disagreement')
        with self.assertRaisesRegex(ValueError, 'Campaign stopped'):
            self.record(trial='trial02')

    def test_electrical_failures_use_full_budget_and_confirm_final(self):
        def evaluate(*args):
            result, receipt = self.evaluator(*args)
            result.update(category='specification_failure', score=0)
            return result, receipt
        self.assertEqual([self.record(evaluate)['outcome'] for _ in range(3)],
                         ['continue', 'continue', 'no_confirmed_pass'])
        self.assertEqual([c['refined'] for c in self.calls], [False, False, False, True])

    def test_invalid_circuits_consume_budget_without_false_electrical_score(self):
        def evaluate(*args):
            result, receipt = self.evaluator(*args)
            result.update(category='invalid_candidate', score=None, error='Unsupported component')
            return result, receipt
        self.assertEqual([self.record(evaluate)['outcome'] for _ in range(3)],
                         ['continue', 'continue', 'no_confirmed_pass'])
        self.assertEqual(len(self.calls), 3)
        self.assertFalse(any(c['refined'] for c in self.calls))
        collection.start(self.folder, 'trial02', root=self.root)
        collection.interrupt(self.folder, 'trial02', 'transport_error', root=self.root)
        state = collection.status(self.folder, self.root)
        self.assertEqual(state['attempts'][1]['outcome'], 'transport_error')
        self.assertIsNone(state['attempts'][1]['episode_success'])
        with self.assertRaisesRegex(ValueError, 'Campaign stopped'):
            self.record(trial='trial03')

    def test_infrastructure_errors_remain_visible_and_are_not_retried(self):
        def evaluate(*args):
            self.calls.append({})
            raise RuntimeError('Synthetic interrupted verifier')
        self.assertEqual(self.record(evaluate)['outcome'], 'infrastructure_error')
        self.assertEqual(len(self.calls), 1)
        state = collection.status(self.folder, self.root)
        self.assertIsNone(state['attempts'][0]['episode_success'])
        self.assertEqual(state['groups'][0]['other_episodes'], 3)
        with self.assertRaisesRegex(ValueError, 'Campaign stopped'):
            self.record(trial='trial02')

    def test_incomplete_proposal_is_not_skipped(self):
        path = self.folder/'attempts/trial01/proposal1'
        path.mkdir(parents=True)
        (path/'model_reply.txt').write_text('retained answer')
        self.assertEqual(collection.status(self.folder, self.root)['attempts'][0]['outcome'], 'incomplete')
        with self.assertRaisesRegex(ValueError, 'Incomplete proposal retained'):
            self.record()

    def test_feedback_excludes_private_fields_and_rejects_path_leaks(self):
        result = {'category': 'invalid_candidate', 'error': 'Component not permitted',
                  'verifier_workspace': 'private location', 'runner_sha256': 'internal identity'}
        text = collection.feedback(result, 1)
        self.assertNotIn('verifier_workspace', text)
        self.assertNotIn('runner_sha256', text)
        result['error'] = 'C:'+ '/Users/'+'example/private.txt'
        with self.assertRaisesRegex(ValueError, 'Private metadata'):
            collection.feedback(result, 1)

    def test_metrics_and_score_types(self):
        self.assertEqual(collection.decision({'category': 'specification_failure', 'score': False}, None, 1), 'infrastructure_error')
        for slot in collection.read(self.folder/'protocol.json')['schedule']:
            trial = self.folder/'attempts'/slot['trial']
            trial.mkdir(parents=True, exist_ok=True)
            collection.save(trial/'outcome.json', {'trial': slot['trial'], 'task': slot['task'],
                'outcome': 'confirmed_pass' if slot['repetition'] < 3 else 'no_confirmed_pass',
                'proposals': 1 if slot['repetition'] < 3 else 3,
                'episode_success': slot['repetition'] < 3})
        group = collection.status(self.folder, self.root)['groups'][0]
        self.assertAlmostEqual(group['estimates']['observed_success_fraction'], 2/3)
        self.assertEqual(group['estimates']['pass_at_k']['2'], 1)
        self.assertAlmostEqual(group['estimates']['pass_power_k']['2'], 1/3)
        self.assertEqual(group['estimates']['pass_power_k']['3'], 0)


if __name__ == '__main__':
    unittest.main()
