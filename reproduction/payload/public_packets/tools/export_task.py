"""Export one verified public packet without the trusted verifier or answers."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parent.parent


def export(task, destination, root=ROOT, revision=None):
    root=Path(root).resolve()
    catalog=json.loads((root/'tasks/catalog.json').read_text(encoding='utf-8'))
    revision=revision or catalog.get('default_revision','recorded')
    if revision=='recorded':
        entry=catalog['tasks'][task]
        folder=(root/'tasks'/task).resolve()
    else:
        if revision not in catalog.get('revisions',{}):
            raise ValueError('Unknown task packet revision: '+revision)
        version=catalog['revisions'][revision]
        entry=version['tasks'][task]
        allowed={row['name'] for row in catalog['tasks'][task]['files']}
        if {row['name'] for row in entry['files']} != allowed:
            raise ValueError('Revised packet changes the allowed public file set')
        folder=(root/'tasks'/version['folder']/task).resolve()
    if not folder.is_relative_to((root/'tasks').resolve()):
        raise ValueError('Task path escapes public packets')
    bodies={}
    for row in entry['files']:
        name=row['name']
        if not name or PurePosixPath(name).name!=name or '\\' in name or ':' in name or name in ['.','..']:
            raise ValueError('Invalid public packet filename')
        source=(folder/name).resolve()
        if not source.is_relative_to(folder):
            raise ValueError('Packet path escapes task')
        body=source.read_bytes()
        if len(body)!=row['bytes'] or hashlib.sha256(body).hexdigest()!=row['sha256']:
            raise ValueError('Public packet identity mismatch: '+name)
        if name in bodies:raise ValueError('Duplicate public packet filename')
        bodies[name]=body
    out=Path(destination).resolve()
    out.mkdir(parents=True,exist_ok=False)
    for name,body in bodies.items():
        with (out/name).open('xb') as handle:handle.write(body)
    return {'task_id':entry['task_id'],'packet_revision':revision,
            'files':list(bodies),'reference_files_exported':0}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task',choices=['supply','load','tia'],required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--revision',help='Packet revision; default is the current catalog revision. Use recorded for historical trials.')
    args=parser.parse_args()
    print(json.dumps(export(args.task,args.out,revision=args.revision),indent=2))


if __name__=='__main__':main()
