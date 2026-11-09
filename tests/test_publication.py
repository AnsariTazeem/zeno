"""Keep host paths and authentication details out of publishable artifacts."""
from pathlib import Path
import hashlib
import importlib.util
import json
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('publication', ROOT/'tools/audit_publication.py')
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)


class PublicationTests(unittest.TestCase):
    def test_current_files_are_clean(self):
        result = publication.audit()
        self.assertEqual(result['findings'], [])
        self.assertEqual(result['outcome'], 'passed')

    def test_redacted_files_match_their_integrity_record(self):
        receipt = json.loads((ROOT/'evidence/path_redactions.json').read_text())
        self.assertFalse(receipt['electrical_measurements_changed'])
        self.assertFalse(receipt['model_responses_changed'])
        maintenance = json.loads((ROOT/'reproduction/maintenance_manifest.json').read_text())
        changes = {row['path']: row for row in maintenance['changes']}
        self.assertEqual(set(changes), {'reproduction/README.md',
                                      'reproduction/source_manifest.json',
                                      'reproduction/kit_manifest.json'})
        for row in receipt['records']:
            with self.subTest(path=row['path']):
                expected = row['after_sha256']
                if row['path'] in changes:
                    change = changes[row['path']]
                    self.assertEqual(change['previous_sha256'], expected)
                    expected = change['sha256']
                self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(), expected)

    def test_private_paths_and_chat_links_are_detected(self):
        samples = [('local_user_path', 'C:'+ '/Users/'+'example/private.txt'),
                   ('local_user_path', '/home/'+'example/private.txt'),
                   ('local_user_path', '/Users/'+'example/private.txt'),
                   ('private_chat_url', 'https://chatgpt.com/'+'c/'+'12345678-1234-1234-1234-123456789abc')]
        for kind, value in samples:
            self.assertIn({'path': 'example.txt', 'kind': kind}, publication.inspect('example.txt', value.encode()))

    def test_nested_private_fields_and_empty_placeholders(self):
        private = json.dumps({'nested': [{'thread_id': 'private'}]}).encode()
        self.assertEqual(publication.inspect('x.json', private), [{'path': 'x.json', 'kind': 'private_session_field'}])
        self.assertEqual(publication.inspect('x.jsonl', private+b'\n'+b'{}\n'),
                         [{'path': 'x.jsonl', 'kind': 'private_session_field'}])
        public = json.dumps({'thread_id': None, 'session_id': '[removed]'}).encode()
        self.assertEqual(publication.inspect('x.json', public), [])

    def test_secrets_are_detected_without_echoing_them(self):
        secret = ('sk'+'-'+('x'*32)).encode()
        self.assertEqual(publication.inspect('x.txt', secret), [{'path': 'x.txt', 'kind': 'credential'}])

    def test_path_escape_is_rejected_before_reading(self):
        with self.assertRaisesRegex(ValueError, 'escapes source root'):
            publication.audit(names=['../private.txt'])


if __name__ == '__main__':
    unittest.main()
