"""Exercise recovery and integrity boundaries of the current setup downloader."""
from pathlib import Path
import hashlib
import importlib.util
import io
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('current_bootstrap', ROOT / 'reproduction/bootstrap.py')
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)


class Response(io.BytesIO):
    url = 'https://example.invalid/pinned.bin'


class InterruptedResponse(Response):
    def read(self, size=-1):
        if self.tell():
            raise ConnectionError('Simulated interruption')
        return super().read(5)


class DownloadRecoveryTests(unittest.TestCase):
    def setUp(self):
        folder = ROOT / '.local-checks'
        folder.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='download_', dir=folder)
        self.addCleanup(self.temp.cleanup)
        self.cache = Path(self.temp.name)
        self.payload = b'complete pinned payload'
        self.row = {'filename': 'pinned.bin', 'url': Response.url,
                    'bytes': len(self.payload),
                    'sha256': hashlib.sha256(self.payload).hexdigest()}

    def retry(self):
        with patch.object(bootstrap.urllib.request, 'urlopen', return_value=Response(self.payload)):
            target, origin = bootstrap.fetch(self.row, self.cache, False)
        self.assertEqual(target.read_bytes(), self.payload)
        self.assertEqual(origin, 'downloaded_https')

    def test_interruption_allows_retry_and_preserves_unowned_partial(self):
        old_partial = self.cache / 'pinned.bin.part'
        old_partial.write_bytes(b'preexisting')
        with patch.object(bootstrap.urllib.request, 'urlopen', return_value=InterruptedResponse(self.payload)):
            with self.assertRaises(ConnectionError):
                bootstrap.fetch(self.row, self.cache, False)
        self.assertEqual(list(self.cache.iterdir()), [old_partial])
        self.retry()
        self.assertEqual(old_partial.read_bytes(), b'preexisting')

    def test_size_overrun_is_rejected_and_retry_succeeds(self):
        with patch.object(bootstrap.urllib.request, 'urlopen', return_value=Response(self.payload + b'extra')):
            with self.assertRaisesRegex(ValueError, 'size/time bound'):
                bootstrap.fetch(self.row, self.cache, False)
        self.assertEqual(list(self.cache.iterdir()), [])
        self.retry()

    def test_digest_mismatch_is_rejected_and_retry_succeeds(self):
        with patch.object(bootstrap.urllib.request, 'urlopen', return_value=Response(b'x' * len(self.payload))):
            with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                bootstrap.fetch(self.row, self.cache, False)
        self.assertEqual(list(self.cache.iterdir()), [])
        self.retry()

    def test_verified_cache_works_offline_without_network(self):
        target = self.cache / self.row['filename']
        target.write_bytes(self.payload)
        with patch.object(bootstrap.urllib.request, 'urlopen') as network:
            self.assertEqual(bootstrap.fetch(self.row, self.cache, True), (target, 'verified_cache'))
        network.assert_not_called()

    def test_corrupt_cache_is_preserved_and_rejected(self):
        target = self.cache / self.row['filename']
        target.write_bytes(b'corrupt')
        with patch.object(bootstrap.urllib.request, 'urlopen') as network:
            with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                bootstrap.fetch(self.row, self.cache, False)
        network.assert_not_called()
        self.assertEqual(target.read_bytes(), b'corrupt')

    def test_insecure_redirect_is_rejected_without_cache_artifact(self):
        response = Response(self.payload)
        response.url = 'http://example.invalid/pinned.bin'
        with patch.object(bootstrap.urllib.request, 'urlopen', return_value=response):
            with self.assertRaisesRegex(ValueError, 'Non-HTTPS redirect'):
                bootstrap.fetch(self.row, self.cache, False)
        self.assertEqual(list(self.cache.iterdir()), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
