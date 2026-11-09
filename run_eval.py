"""Forward to the current evaluator in an explicitly prepared trusted root."""
from pathlib import Path
import argparse
import subprocess

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, add_help=True)
    parser.add_argument('--prepared-root', type=Path, required=True)
    args, forwarded = parser.parse_known_args()
    root = args.prepared_root.resolve()
    python = root / '.venv/Scripts/python.exe'
    runner = root / 'eval_core_v5/run_eval.py'
    if not all(p.is_file() for p in [python, runner, root / 'bootstrap_result.json']):
        parser.error('Use the completed root printed by bootstrap.py')
    raise SystemExit(subprocess.call([str(python), '-I', '-B', str(runner), *forwarded]))
