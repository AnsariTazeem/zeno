"""Refresh maintained runtime manifests while retaining historical verification seals."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT/'reproduction'
PAYLOAD = KIT/'payload'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path, base):
    body = path.read_bytes()
    return {'path': path.relative_to(base).as_posix(), 'bytes': len(body),
            'sha256': hashlib.sha256(body).hexdigest()}


def write(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def main():
    # Existing v5 seals remain authoritative for the frozen apparatus.
    rows = {row['path']: row for row in read(PAYLOAD/'eval_core_v5/dependency_lock.json')['files']}
    extra = [*sorted((PAYLOAD/'public_packets').rglob('*')),
             *[PAYLOAD/'eval_core_v6'/name for name in ('run_eval.py', 'supply_adapter.py', 'tia_adapter.py')]]
    for path in extra:
        if path.is_file():
            row = identity(path, PAYLOAD)
            rows[row['path']] = row
    write(PAYLOAD/'eval_core_v6/dependency_lock.json', {
        'scope': 'v6 runtime dependencies; historical seals and electrical limits retained',
        'files': [rows[name] for name in sorted(rows)]})
    source = KIT/'source_manifest.json'
    paths = {row['path'] for row in read(source)['files']}
    paths.update(path.relative_to(PAYLOAD).as_posix()
                 for folder in ('eval_core_v6', 'public_packets')
                 for path in (PAYLOAD/folder).rglob('*')
                 if path.is_file() and '__pycache__' not in path.parts)
    write(source, {'files': [identity(PAYLOAD/name, PAYLOAD) for name in sorted(paths)]})
    kit = KIT/'kit_manifest.json'
    paths = {row['path'] for row in read(kit)['files']}
    paths.update('payload/'+row['path'] for row in read(source)['files'])
    write(kit, {'files': [identity(KIT/name, KIT) for name in sorted(paths)]})
    # These three documents/manifests were redacted before the maintenance changes.
    # Chain to that historical receipt instead of rewriting its original hashes.
    maintained = {'reproduction/README.md', 'reproduction/source_manifest.json',
                  'reproduction/kit_manifest.json'}
    changes = []
    for row in read(ROOT/'evidence/path_redactions.json')['records']:
        if row['path'] in maintained:
            changes.append({'path': row['path'], 'previous_sha256': row['after_sha256'],
                            'sha256': identity(ROOT/row['path'], ROOT)['sha256']})
    write(KIT/'maintenance_manifest.json', {
        'scope': 'Current runtime documentation and manifest updates after the historical path redactions',
        'historical_receipt': 'evidence/path_redactions.json',
        'changes': changes})


if __name__ == '__main__':
    main()
