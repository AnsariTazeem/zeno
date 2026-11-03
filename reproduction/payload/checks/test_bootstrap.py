"""Adversarial tests for archive/filesystem writes in the new bootstrap."""
from pathlib import Path
import hashlib
import importlib.util
import io
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location('bootstrap_under_test', Path(__file__).with_name('bootstrap_under_test.py'))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def archive(entries):
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode='w') as handle:
        for name, body, kind in entries:
            item = tarfile.TarInfo(name)
            item.type = kind
            item.size = len(body) if kind == tarfile.REGTYPE else 0
            if kind == tarfile.SYMTYPE:
                item.linkname = '../outside'
            handle.addfile(item, io.BytesIO(body) if kind == tarfile.REGTYPE else None)
    data.seek(0)
    return data


class ArchiveBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='mb_')
        self.root = Path(self.tmp.name)
        self.expected = {'ok': {'bytes': 2, 'sha256': hashlib.sha256(b'OK').hexdigest(), 'destination': 'a/ok'}}

    def tearDown(self):
        self.tmp.cleanup()

    def test_regular_allowlisted_bytes_only(self):
        self.assertEqual(b.extract_selected(archive([('extra', b'no', tarfile.REGTYPE), ('ok', b'OK', tarfile.REGTYPE)]), self.expected, self.root), 1)
        self.assertEqual((self.root / 'a/ok').read_bytes(), b'OK')
        self.assertFalse((self.root / 'extra').exists())

    def test_traversal_absolute_drive_rejected(self):
        for name in ['../outside', '/outside', 'C:/outside', 'a/../../outside']:
            with self.assertRaises(ValueError):
                b.safe(self.root, name)
        with self.assertRaises(ValueError):
            b.extract_selected(archive([('../outside', b'NO', tarfile.REGTYPE)]), self.expected, self.root)

    def test_selected_links_rejected(self):
        with self.assertRaises(ValueError):
            b.extract_selected(archive([('ok', b'', tarfile.SYMTYPE)]), self.expected, self.root)
        self.assertFalse((self.root / 'a/ok').exists())

    def test_wrong_content_rejected_before_write(self):
        with self.assertRaises(ValueError):
            b.extract_selected(archive([('ok', b'NO', tarfile.REGTYPE)]), self.expected, self.root)
        self.assertFalse((self.root / 'a/ok').exists())

    def test_missing_and_duplicate_members_rejected(self):
        with self.assertRaises(ValueError):
            b.extract_selected(archive([]), self.expected, self.root)
        with self.assertRaises(ValueError):
            b.extract_selected(archive([('ok', b'OK', tarfile.REGTYPE), ('ok', b'OK', tarfile.REGTYPE)]), self.expected, self.root)

    def test_existing_file_preserved(self):
        (self.root / 'a').mkdir()
        (self.root / 'a/ok').write_bytes(b'old')
        with self.assertRaises(FileExistsError):
            b.extract_selected(archive([('ok', b'OK', tarfile.REGTYPE)]), self.expected, self.root)
        self.assertEqual((self.root / 'a/ok').read_bytes(), b'old')

    def test_bad_cached_download_not_silently_reused(self):
        row = {'filename': 'asset', 'bytes': 2, 'sha256': hashlib.sha256(b'OK').hexdigest()}
        (self.root / 'asset').write_bytes(b'NO')
        with self.assertRaises(ValueError):
            b.fetch(row, self.root, True)
        self.assertEqual((self.root / 'asset').read_bytes(), b'NO')

    def test_streaming_decode_and_oversized_window_guard(self):
        import zstandard
        data = b'archive-stream' * 100
        compressed = zstandard.ZstdCompressor().compress(data)
        with b.bounded_stream(io.BytesIO(compressed)) as reader:
            self.assertEqual(reader.read(), data)
        with patch.object(zstandard, 'get_frame_parameters', return_value=SimpleNamespace(window_size=64*1024*1024+1)):
            with self.assertRaises(ValueError):
                b.bounded_stream(io.BytesIO(compressed))


if __name__ == '__main__':
    unittest.main(verbosity=2)
