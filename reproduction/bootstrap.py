"""Windows source-kit setup. No model calls, archive scripts or system installs."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.parse
import urllib.request
import venv
import zipfile

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for body in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(body)
    return h.hexdigest()


def safe(root, name):
    rel = PurePosixPath(name.replace('\\', '/'))
    if not rel.parts or rel.is_absolute() or '..' in rel.parts or ':' in name:
        raise ValueError('Unsafe relative path: ' + name)
    result = (root / Path(*rel.parts)).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError('Path escapes root')
    return result


def identity(path, row):
    if not path.is_file() or path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
        raise ValueError('File identity mismatch: ' + str(path))


def save(path, data):
    with path.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(data, indent=2, allow_nan=False) + '\n')


def fetch(row, cache, offline):
    target = safe(cache, row['filename'])
    if target.exists():
        identity(target, row)
        return target, 'verified_cache'
    if offline:
        raise FileNotFoundError('Offline cache missing: ' + row['filename'])
    if urllib.parse.urlsplit(row['url']).scheme != 'https':
        raise ValueError('HTTPS required')
    descriptor, name = tempfile.mkstemp(prefix=target.name + '.', suffix='.part', dir=target.parent)
    part = Path(name)
    count = 0
    started = time.monotonic()
    try:
        with os.fdopen(descriptor, 'wb') as handle, urllib.request.urlopen(row['url'], timeout=60) as response:
            if urllib.parse.urlsplit(response.url).scheme != 'https':
                raise ValueError('Non-HTTPS redirect')
            while body := response.read(1024 * 1024):
                count += len(body)
                if count > row['bytes'] or time.monotonic() - started > 300:
                    raise ValueError('Download size/time bound exceeded')
                handle.write(body)
        identity(part, row)
        part.rename(target)
    finally:
        # Remove only this attempt's file; a prior partial may belong to another run.
        part.unlink(missing_ok=True)
    return target, 'downloaded_https'


def extract_selected(source, expected, destination):
    """Read a tar stream; write only byte-verified allowlisted regular files."""
    found = set()
    with tarfile.open(fileobj=source, mode='r|') as archive:
        for member in archive:
            name = member.name
            safe(destination, name)  # also reject traversal in skipped entries
            if name not in expected:
                continue
            if name in found or not member.isfile():
                raise ValueError('Duplicate/link/special selected member: ' + name)
            row = expected[name]
            if member.size != row['bytes'] or member.size > 64 * 1024 * 1024:
                raise ValueError('Selected member size mismatch: ' + name)
            reader = archive.extractfile(member)
            if reader is None:
                raise ValueError('No selected member bytes')
            body = reader.read(row['bytes'] + 1)
            if len(body) != row['bytes'] or hashlib.sha256(body).hexdigest() != row['sha256']:
                raise ValueError('Selected member digest mismatch: ' + name)
            target = safe(destination, row['destination'])
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as handle:
                handle.write(body)
            found.add(name)
    if found != set(expected):
        raise ValueError('Selected archive members missing: ' + str(sorted(set(expected) - found)[:5]))
    return len(found)


def bounded_stream(compressed):
    import zstandard
    # Inspect the byte-valued frame header, independently of the library's
    # max_window_size unit convention. The pinned frames need only 2/8 MiB.
    limit = 64 * 1024 * 1024
    frame = zstandard.get_frame_parameters(compressed.read(18))
    compressed.seek(0)
    if frame.window_size > limit:
        raise ValueError('Archive frame window exceeds 64 MiB')
    return zstandard.ZstdDecompressor(max_window_size=limit).stream_reader(compressed)


def unpack(row, source, output):
    expected = {e['member']: e for e in row['members']}
    if len(expected) != len(row['members']):
        raise ValueError('Duplicate expected member')
    if row['kind'] == 'conda':
        with zipfile.ZipFile(source) as package:
            names = package.namelist()
            if len(names) != len(set(names)) or any(len(PurePosixPath(x).parts) != 1 for x in names):
                raise ValueError('Unsafe conda ZIP layout')
            payloads = [x for x in names if x.startswith('pkg-') and x.endswith('.tar.zst')]
            if len(payloads) != 1:
                raise ValueError('Expected one conda package payload')
            with package.open(payloads[0]) as compressed, bounded_stream(compressed) as stream:
                return extract_selected(stream, expected, output)
    with source.open('rb') as compressed, bounded_stream(compressed) as stream:
        return extract_selected(stream, expected, output)


def execute(args, output, label, timeout=300):
    # -I on Python commands excludes user site packages and PYTHON* overrides.
    with (output / (label + '_stdout.txt')).open('xb') as stdout, (output / (label + '_stderr.txt')).open('xb') as stderr:
        result = subprocess.run(args, stdout=stdout, stderr=stderr, timeout=timeout,
                                creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError(label + ' failed; inspect retained stdout/stderr')


def materialize(args):
    plan = read(HERE / 'setup_lock.json')
    receipt = read(args.output / 'bootstrap_started.json')
    receipt['wheels'] = read(args.output / 'wheel_receipt.json')
    if 'include-system-site-packages = false' not in (args.output / '.venv/pyvenv.cfg').read_text():
        raise ValueError('System site packages must remain disabled')
    for row in plan['archives']:
        archive, origin = fetch(row, args.cache, args.offline)
        count = unpack(row, archive, args.output)
        receipt['archives'].append({'filename': row['filename'], 'sha256': sha(archive),
                                    'origin': origin, 'extracted_files': count})
    for row in read(args.output / 'eval_core_v3/dependency_lock.json')['files']:
        identity(safe(args.output, row['path']), row)
    import numpy
    import zstandard
    receipt.update({'finished_at_utc': datetime.now(timezone.utc).isoformat(),
                    'outcome': 'setup_complete_native_qualification_pending',
                    'verified_runtime_files': 1202, 'python': sys.version,
                    'python_executable': sys.executable, 'numpy_version': numpy.__version__,
                    'numpy_origin': numpy.__file__, 'zstandard_origin': zstandard.__file__,
                    'system_site_packages': False, 'model_calls': 0,
                    'fresh_machine_proven': False})
    save(args.output / 'bootstrap_result.json', receipt)
    print(json.dumps(receipt, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--cache', type=Path)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--materialize', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if os.name != 'nt' or struct.calcsize('P') != 8 or sys.version_info[:2] != (3, 12):
        parser.error('Use independently installed 64-bit Windows Python 3.12')
    for row in read(HERE / 'kit_manifest.json')['files']:
        identity(safe(HERE, row['path']), row)
    if args.materialize:
        if args.output is None or args.cache is None or Path(sys.prefix).resolve() != (args.output / '.venv').resolve():
            parser.error('Internal materialization requires this output venv')
        materialize(args)
        return
    if args.output is None:
        output = Path(tempfile.mkdtemp(prefix='mr_')).resolve()
    else:
        output = args.output.resolve()
        if output.exists():
            parser.error('Output exists; preserve earlier attempts and choose a new path')
        output.mkdir(parents=True)
    # Match the frozen conservative path budget before copying or execution.
    if len(str(output / 'analog_supply_pilot_v1/runs/s/eval/opamp_2stg/v115/opamp_loop')) > 140:
        parser.error('Use a shorter output root; native include paths are length-sensitive')
    cache = (args.cache or HERE / 'cache').resolve()
    cache.mkdir(parents=True, exist_ok=True)
    receipt = {'started_at_utc': datetime.now(timezone.utc).isoformat(), 'output': str(output),
               'setup_lock_sha256': sha(HERE / 'setup_lock.json'), 'archives': [], 'wheels': [],
               'scope': 'New venv and pinned assets on this host; no fresh OS or independent machine claim'}
    save(output / 'bootstrap_started.json', receipt)
    try:
        for row in read(HERE / 'source_manifest.json')['files']:
            source = safe(HERE / 'payload', row['path'])
            identity(source, row)
            dest = safe(output, row['path'])
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open('xb') as handle:
                handle.write(source.read_bytes())
        venv.EnvBuilder(with_pip=True, symlinks=False).create(output / '.venv')
        python = output / '.venv/Scripts/python.exe'
        plan = read(HERE / 'setup_lock.json')
        for row in plan['wheels']:
            wheel, origin = fetch(row, cache, args.offline)
            receipt['wheels'].append({'filename': row['filename'], 'sha256': sha(wheel), 'origin': origin})
        save(output / 'wheel_receipt.json', receipt['wheels'])
        execute([str(python), '-I', '-m', 'pip', '--isolated', 'install', '--no-index', '--no-deps',
                 '--require-hashes', '--find-links', str(cache), '-r', str(HERE / 'requirements.lock')],
                output, 'pip_install')
        command = [str(python), '-I', str(HERE / 'bootstrap.py'), '--materialize',
                   '--output', str(output), '--cache', str(cache)]
        if args.offline:
            command.append('--offline')
        execute(command, output, 'materialize', timeout=900)
        print(json.dumps({'outcome': 'setup_complete_native_qualification_pending',
                          'output': str(output), 'python': str(python),
                          'next': f'"{python}" -I "{output / "qualification.py"}"'}, indent=2))
    except Exception as error:
        save(output / 'bootstrap_failure.json', {'type': type(error).__name__, 'message': str(error),
                                                'at_utc': datetime.now(timezone.utc).isoformat(),
                                                'scope': 'Setup failure; no model/electrical conclusion'})
        print('Setup failed; partial evidence retained at ' + str(output), file=sys.stderr)
        raise


if __name__ == '__main__':
    main()
