"""Export one verified public packet without the trusted verifier or answers."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parent.parent


def export(task, destination, root=ROOT):
    root=Path(root).resolve()
    catalog=json.loads((root/'tasks/catalog.json').read_text(encoding='utf-8'))['tasks']
    entry=catalog[task]
    folder=(root/'tasks'/task).resolve()
    if not folder.is_relative_to(root/'tasks'):
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
    return {'task_id':entry['task_id'],'files':list(bodies),'reference_files_exported':0}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task',choices=['supply','load','tia'],required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(export(args.task,args.out),indent=2))


if __name__=='__main__':main()
