# Setup and commands

Use Windows x64 Python 3.12 and compatible Windows C/UCRT support. Run commands
from the repository root.

## Prepare dependencies

```powershell
python -I -B bootstrap.py
```

Setup verifies cached files or downloads pinned archives and wheels:
41,668,459 bytes with an empty cache. It creates a short temporary root and
venv, then prints their paths. NumPy 2.3.5 and zstandard 0.25.0 are pinned.
No model account or API key is needed for simulation or grading. Windows may
later remove the temporary root; rerun setup to create a new one.

## Run offline checks

Stay in the repository root and use the printed environment's Python:

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B tools/run_checks.py
```

This verifies frozen files, runs the existing 50 setup/grading tests and checks
the public task copies and exports. It makes no model calls, downloads or
full-circuit simulation runs. Logs go to the ignored `.local-checks/` folder.

## Reproduce native controls

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B 'C:/printed/root/qualification.py'
```

This runs the original 50 tests and five circuit controls: three passing
references, an ordinary SUPPLY failure and a no-gain SUPPLY failure. Use a
fresh prepared root: qualification refuses to overwrite earlier outputs.

The completed run on this computer took about 67 seconds for cached setup and
472 seconds for qualification. Qualification covered 21 conditions in 20
successful full-circuit native processes. These are observed timings, not
guarantees. [Reproduction report](reproduction.md)

## Grade a circuit

```powershell
python -I -B run_eval.py --prepared-root 'C:/printed/root' inspect --task supply
python -I -B run_eval.py --prepared-root 'C:/printed/root' evaluate --task supply --candidate 'C:/your/circuit.sp' --run-id new01
```

Use a new run ID each time. Add `--numerics refined` for the finer profile.
`load` and `tia` use the same interface. Exit 0 includes a valid electrical
failure; 2 means invalid input and 3 means an infrastructure error. Every
stated requirement must pass at every condition. Scores are 100/0 for valid
evidence. [Grading details](../graders/README.md)

## Export a task for a model

```powershell
python -I -B tools/export_task.py --task supply --out 'C:/new/task-folder'
```

Only that task's verified public files are copied. The destination must not
exist. Give the model that folder only, in a fresh context. This repository
contains references; LOAD/TIA's fixed plant can expose SUPPLY's repair.
Export checks reduce accidental leakage but do not establish OS isolation
or absence of training exposure.

## Cost and evidence

Setup, tests and circuit grading make zero model calls. Historical collection
used the existing ChatGPT subscription, with no separately billed API fallback.
Subscription usage consumed quota; no per-run dollar inference cost is known.
Model access and collection are separate from this offline runner.

A SUPPLY evaluation launches six native testbenches; LOAD/TIA each launch one
process spanning six conditions. Time depends on circuit behavior, profile and
host. The qualification timings measure the five-control batch, not a fixed
per-candidate runtime.

Model settings, dates, capture timing and candidate feedback are retained in
[transcripts](../transcripts/README.md). Exact backend revisions, temperatures
and seeds are unknown. The full raw entry archive remains local; its identity
is in [the archive record](../evidence/entry_archive.json).
