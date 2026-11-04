"""Reject widened access, changed model settings and tool requests in captures."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('transport', ROOT/'tools/codex_transport.py')
transport = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transport)


class TransportTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT/'.local-checks'
        parent.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='transport_', dir=parent)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.work = self.folder/'inputs'
        self.home = self.folder/'client'
        self.work.mkdir()
        self.context = {'model': 'fixed-model', 'effort': 'high', 'approval_policy': 'never',
            'cwd': str(self.work), 'permission_profile': {'type': 'managed', 'network': 'restricted',
            'file_system': {'type': 'restricted', 'entries': [
                {'path': {'type': 'special', 'value': {'kind': 'minimal'}}, 'access': 'read'},
                {'path': {'type': 'path', 'path': str(self.work)}, 'access': 'read'},
                {'path': {'type': 'path', 'path': str(self.home/'tmp/arg0-windows/current')}, 'access': 'read'}]}}}

    def audit(self, context=None, calls=None, owner='owned'):
        rows = [{'type': 'session_meta', 'payload': {'id': owner}}]
        if context is not False:
            rows.append({'type': 'turn_context', 'payload': context or self.context})
        rows += calls or []
        path = self.folder/'trace.jsonl'
        path.write_text(''.join(json.dumps(r)+'\n' for r in rows), encoding='utf-8')
        return transport.audit_trace(path, 'owned', self.work, 'fixed-model', 'high', self.home)

    def test_accepts_expected_effective_profile(self):
        result = self.audit()
        self.assertTrue(result['restricted_read_policy'])
        self.assertEqual(result['tool_requests'], 0)

    def test_rejects_broader_access_and_different_settings(self):
        mutations = [lambda c: c.update(model='different'), lambda c: c.update(effort='low'),
                     lambda c: c.update(approval_policy='on-request'),
                     lambda c: c['permission_profile'].update(network='enabled'),
                     lambda c: c['permission_profile']['file_system'].update(type='unrestricted'),
                     lambda c: c['permission_profile']['file_system']['entries'][0]['path']['value'].update(kind='root'),
                     lambda c: c['permission_profile']['file_system']['entries'][1].update(access='write'),
                     lambda c: c['permission_profile']['file_system']['entries'][2]['path'].update(path=str(self.folder/'answers'))]
        for mutate in mutations:
            context = deepcopy(self.context)
            mutate(context)
            with self.assertRaises(ValueError):
                self.audit(context)

    def test_rejects_tool_calls_missing_context_and_wrong_owner(self):
        for kind in ('function_call', 'custom_tool_call'):
            with self.assertRaisesRegex(ValueError, 'Tool request'):
                self.audit(calls=[{'type': 'response_item', 'payload': {'type': kind, 'name': 'exec'}}])
        with self.assertRaisesRegex(ValueError, 'settings are missing'):
            self.audit(context=False)
        with self.assertRaisesRegex(ValueError, 'ownership mismatch'):
            self.audit(owner='other')

    def test_command_keeps_access_and_retry_controls(self):
        args = transport.command('codex', self.work, self.folder/'answer.txt', 'fixed-model', 'high')
        self.assertNotIn('--sandbox', args)
        self.assertIn('--ignore-user-config', args)
        self.assertIn('windows.sandbox="mxc"', args)
        self.assertIn('web_search="disabled"', args)
        self.assertFalse(any(a.startswith('model_providers.') for a in args))
        self.assertIn('unbounded_connection_retries', args)
        self.assertIn('shell_tool', args)
        resumed = transport.command('codex', self.work, self.folder/'answer.txt', 'fixed-model', 'high', 'owned')
        self.assertEqual(resumed[resumed.index('resume')+1], 'owned')

    def test_api_overrides_are_removed_from_child_environment(self):
        with patch.dict(transport.os.environ, {'OPENAI_API_KEY': 'example', 'CODEX_API_KEY': 'example',
                                             'OPENAI_BASE_URL': 'example', 'AZURE_OPENAI_API_KEY': 'example'}):
            result = transport.environment()
        self.assertFalse(any(k.upper().startswith(('OPENAI_', 'AZURE_OPENAI_', 'CODEX_API_')) for k in result))

    def test_identity_mismatch_stops_before_output_or_model_launch(self):
        output = self.folder/'capture'
        with patch.object(transport, 'describe', return_value={'cli_sha256': 'new'}):
            with self.assertRaisesRegex(ValueError, 'identity'):
                transport.request(b'input', output, self.work, 'fixed-model', 'high', {'cli_sha256': 'old'})
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
