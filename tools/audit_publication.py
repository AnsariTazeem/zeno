"""Check published files for credentials, private session fields and local paths."""
from pathlib import Path
import argparse
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = {
    'credential': re.compile(rb'(?:sk-[A-Za-z0-9_-]{24,}|fc-[A-Za-z0-9]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN'
                             rb'[^\r\n]*PRIVATE KEY-----)'),
    'local_user_path': re.compile(rb'(?i)(?:[A-Z]:[\\/]+Users[\\/]+[^\\/\s"\x27]+|/ho' rb'me/[^/\s"\x27]+)'),
    'private_chat_url': re.compile(rb'https://chatgpt\.com/c/[0-9a-f-]{36}'),
}
PRIVATE_FIELDS = {'session_id', 'thread_id', 'resume_session'}


def inspect(name, body):
    findings = [{'path': name, 'kind': kind} for kind, pattern in PATTERNS.items() if pattern.search(body)]
    if name.endswith('.json'):
        data = json.loads(body)

        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in PRIVATE_FIELDS and child and not str(child).startswith('['):
                        findings.append({'path': name, 'kind': 'private_session_field'})
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)
        walk(data)
    return findings


def publication_files(root):
    if (root/'.git').exists():
        result = subprocess.run(['git', 'ls-files', '-co', '--exclude-standard', '-z'],
                                cwd=root, capture_output=True, check=True)
        return sorted(set(filter(None, result.stdout.decode('utf-8').split('\0'))))
    folders = ('docs', 'tasks', 'reference', 'graders', 'tools', 'results',
               'transcripts', 'tests', 'evidence', 'reproduction', '.github')
    files = [p for name in folders for p in (root/name).rglob('*')
             if p.is_file() and not {'__pycache__', '.venv', 'cache'}.intersection(p.relative_to(root).parts)]
    files += [root/name for name in ('README.md', 'bootstrap.py', 'run_eval.py',
              'requirements.txt', '.env.example', '.gitignore', '.gitattributes') if (root/name).is_file()]
    return sorted({p.relative_to(root).as_posix() for p in files})


def audit(root=ROOT, names=None):
    root = Path(root).resolve()
    names = publication_files(root) if names is None else names
    findings = []
    for name in names:
        path = (root/name).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Publication path escapes source root')
        findings.extend(inspect(name, path.read_bytes()))
    return {'outcome': 'passed' if not findings else 'failed',
            'files_checked': len(names), 'findings': findings,
            'scope': 'Current files; pattern scan excludes Git history and is not a security certification'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    body = json.dumps(result, indent=2)+'\n'
    if args.out:
        with args.out.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(body)
    print(body, end='')
    return 0 if result['outcome'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
