"""Invoke the unchanged tested setup recipe packaged under reproduction/."""
from pathlib import Path
import subprocess
import sys

if __name__ == '__main__':
    raise SystemExit(subprocess.call([sys.executable, '-I', '-B',
        str(Path(__file__).resolve().parent / 'reproduction/bootstrap.py'), *sys.argv[1:]]))
