"""Reject packet drift and exercise the actual compiler and grader boundaries."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


auditor = load('task_contract_auditor', ROOT/'tools/audit_tasks.py')
exporter = load('revision_exporter', ROOT/'tools/export_task.py')


class TaskContractTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT/'.local-checks'
        parent.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='contract_', dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def fixture(self):
        root = self.folder/'fixture'
        shutil.copytree(ROOT/'tasks', root/'tasks')
        return root

    def repin(self, root, task, name):
        catalog_path = root/'tasks/catalog.json'
        catalog = auditor.read(catalog_path)
        revision = catalog['revisions'][catalog['default_revision']]
        body = (root/'tasks'/revision['folder']/task/name).read_bytes()
        row = next(x for x in revision['tasks'][task]['files'] if x['name'] == name)
        row.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
        catalog_path.write_text(json.dumps(catalog), encoding='utf-8')

    def test_default_export_uses_current_packet_and_fixed_assets(self):
        catalog = auditor.read(ROOT/'tasks/catalog.json')
        revision = catalog['revisions'][catalog['default_revision']]
        for task, entry in revision['tasks'].items():
            destination = self.folder/task
            receipt = exporter.export(task, destination)
            self.assertEqual(receipt['packet_revision'], 'clarified-1')
            self.assertEqual(receipt['reference_files_exported'], 0)
            self.assertEqual({x.name for x in destination.iterdir()}, {x['name'] for x in entry['files']})
            for row in entry['files']:
                self.assertEqual(hashlib.sha256((destination/row['name']).read_bytes()).hexdigest(), row['sha256'])
        self.assertEqual(len(auditor.packet_checks()), 3)

    def test_unknown_revision_fails_before_writing(self):
        destination = self.folder/'output'
        with self.assertRaisesRegex(ValueError, 'Unknown task packet revision'):
            exporter.export('tia', destination, revision='unknown')
        self.assertFalse(destination.exists())

    def test_changed_current_packet_fails_before_writing(self):
        root = self.fixture()
        (root/'tasks/revisions/clarified-1/tia/PROMPT.txt').write_text('changed')
        destination = self.folder/'output'
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            exporter.export('tia', destination, root)
        self.assertFalse(destination.exists())

    def test_revision_path_escape_is_rejected(self):
        root = self.fixture()
        path = root/'tasks/catalog.json'
        catalog = auditor.read(path)
        catalog['revisions']['clarified-1']['folder'] = '../outside'
        path.write_text(json.dumps(catalog))
        with self.assertRaisesRegex(ValueError, 'escapes'):
            exporter.export('tia', self.folder/'output', root)
        self.assertFalse((self.folder/'output').exists())

    def test_added_reference_file_cannot_be_exported(self):
        root = self.fixture()
        path = root/'tasks/catalog.json'
        catalog = auditor.read(path)
        revision = catalog['revisions']['clarified-1']
        reference = (ROOT/'reference/tia.sp').read_bytes()
        (root/'tasks'/revision['folder']/'tia/reference.sp').write_bytes(reference)
        revision['tasks']['tia']['files'].append({'name': 'reference.sp', 'bytes': len(reference),
            'sha256': hashlib.sha256(reference).hexdigest()})
        path.write_text(json.dumps(catalog))
        with self.assertRaisesRegex(ValueError, 'allowed public file set'):
            exporter.export('tia', self.folder/'output', root)
        self.assertFalse((self.folder/'output').exists())

    def test_repinning_cannot_hide_changed_electrical_limit(self):
        root = self.fixture()
        path = root/'tasks/revisions/clarified-1/tia/contract.json'
        contract = auditor.read(path)
        contract['limits']['each_edge_settle_max_ns'] = 999
        path.write_text(json.dumps(contract))
        self.repin(root, 'tia', 'contract.json')
        with self.assertRaisesRegex(ValueError, 'Electrical contract changed'):
            auditor.packet_checks(root)

    def test_declarations_detect_a_wrong_numeric_requirement(self):
        root = self.fixture()
        path = root/'tasks/revisions/clarified-1/tia/TASK.md'
        path.write_text(path.read_text().replace('by 500 ns', 'by 900 ns'))
        with self.assertRaisesRegex(ValueError, 'numerical requirement'):
            auditor.declaration_checks(root)
        self.assertEqual(len(auditor.declaration_checks()), 25)

    def test_compilers_match_disclosed_input_boundaries(self):
        rows = auditor.syntax_checks()
        self.assertEqual(len(rows), 21)
        self.assertTrue(any(row['accepted'] for row in rows))
        self.assertTrue(any(not row['accepted'] for row in rows))
        self.assertTrue(all(row['accepted'] == row['expected_accepted'] for row in rows))

    def test_graders_match_the_stated_electrical_boundaries(self):
        rows = auditor.verdict_checks()
        self.assertEqual(len(rows), 402)
        self.assertTrue(all((row['category'] == 'pass') == row['expected_pass'] for row in rows))

    def test_supply_reporting_matches_the_pinned_measurement_code(self):
        self.assertEqual(len(auditor.precision_checks()), 7)


if __name__ == '__main__':
    unittest.main(verbosity=2)
