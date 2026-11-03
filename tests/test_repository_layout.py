"""Check actual public exports, identity boundaries and reference provenance."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,tempfile,unittest

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('public_export',ROOT/'tools/export_task.py')
exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
CATALOG=json.loads((ROOT/'tasks/catalog.json').read_text())['tasks']


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        folder=ROOT/'.local-checks'
        folder.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='packet_',dir=folder)
        self.addCleanup(self.temp.cleanup)
        self.tmp=Path(self.temp.name)

    def fixture(self):
        root=self.tmp/'fixture'
        shutil.copytree(ROOT/'tasks',root/'tasks')
        return root

    def test_public_packets_are_exact_copies(self):
        for task,meta in CATALOG.items():
            for row in meta['files']:
                a=(ROOT/'tasks'/task/row['name']).read_bytes()
                b=(ROOT/'reproduction/payload'/meta['frozen_source']/row['name']).read_bytes()
                self.assertEqual(a,b)
                self.assertEqual(hashlib.sha256(a).hexdigest(),row['sha256'])

    def test_exports_have_only_task_files(self):
        for task,meta in CATALOG.items():
            out=self.tmp/task
            result=exporter.export(task,out)
            self.assertEqual(result['reference_files_exported'],0)
            self.assertEqual({p.name for p in out.iterdir()},{r['name'] for r in meta['files']})
            for row in meta['files']:
                self.assertEqual(hashlib.sha256((out/row['name']).read_bytes()).hexdigest(),row['sha256'])

    def test_existing_destination_is_preserved(self):
        out=self.tmp/'existing';out.mkdir();(out/'keep.txt').write_text('keep')
        with self.assertRaises(FileExistsError):exporter.export('supply',out)
        self.assertEqual((out/'keep.txt').read_text(),'keep')
        self.assertEqual(len(list(out.iterdir())),1)

    def test_tampered_packet_fails_before_writing(self):
        root=self.fixture()
        (root/'tasks/supply/starter.sp').write_text('changed')
        out=self.tmp/'out'
        with self.assertRaises(ValueError):exporter.export('supply',out,root)
        self.assertFalse(out.exists())

    def test_catalog_path_escape_is_rejected(self):
        root=self.fixture();path=root/'tasks/catalog.json'
        data=json.loads(path.read_text());data['tasks']['supply']['files'][0]['name']='../outside'
        path.write_text(json.dumps(data))
        out=self.tmp/'out'
        with self.assertRaises(ValueError):exporter.export('supply',out,root)
        self.assertFalse(out.exists())

    def test_reference_circuits_are_pinned_to_tested_controls(self):
        for task in CATALOG:
            self.assertEqual((ROOT/'reference'/f'{task}.sp').read_bytes(),
                             (ROOT/'reproduction/payload/checks'/f'{task}_ref01.sp').read_bytes())

    def test_task_catalog_does_not_point_to_references(self):
        expected={'supply':{'PROMPT.txt','TASK.md','starter.sp','contract.json','LICENSE_UPSTREAM.txt'},
                  'load':{'PROMPT.txt','TASK.md','starter.sp','fixed_amplifier.sp','contract.json','MODEL_IDENTITY.json','LICENSE_UPSTREAM.txt'},
                  'tia':{'PROMPT.txt','TASK.md','starter.sp','fixed_amplifier.sp','contract.json','MODEL_IDENTITY.json','LICENSE_UPSTREAM.txt'}}
        self.assertEqual(set(CATALOG),set(expected))
        for task,meta in CATALOG.items():self.assertEqual({r['name'] for r in meta['files']},expected[task])


if __name__=='__main__':unittest.main(verbosity=2)
