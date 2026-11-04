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

Keep Windows `TEMP` and `TMP` at a short, writable location. Native evaluation
creates its own scratch directory there; redirecting it into a long project
path can break ngspice's model includes. The default setup chooses a short
temporary output root. Preserve failed logs and use a new root when retrying.

## Run offline checks

Stay in the repository root and use the printed environment's Python:

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B tools/run_checks.py
```

This verifies frozen files and runs 88 tests covering setup, download recovery,
grading, raw evidence, task exports and session accounting. It makes no model calls, downloads or
full-circuit simulation runs. Logs go to the ignored `.local-checks/` folder.
Test subprocesses use a temporary directory inside that log folder, so they
do not need write access to the system temporary directory.

## Reproduce native controls

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B 'C:/printed/root/qualification.py'
```

This runs the original 50 tests and five circuit controls: three passing
references, an ordinary SUPPLY failure and a no-gain SUPPLY failure. Use a
fresh prepared root: qualification refuses to overwrite earlier outputs.

The latest fresh-venv run took 32.732 seconds for cached setup and 192.526
seconds for native qualification. It covered 21 conditions in 20 native
processes. [Run receipt](../evidence/final_validation.json) · [Reproduction](reproduction.md)

The source was checked in a fresh clone and venv. See [reproduction](reproduction.md)
and [CI](ci.md) for run details.

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
The collection boundaries are documented in [methodology](methodology.md).

Export defaults to the `clarified-1` packet. Add `--revision recorded` for the
exact historical task inputs. Electrical grading requirements are unchanged.
Run `tools/audit_tasks.py` with the prepared Python to check declarations,
input boundaries and verdicts. [Audit details](task-validation.md)

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
[transcripts](../transcripts/README.md). The full raw entry archive remains
local; its identity is in [the archive record](../evidence/entry_archive.json).

## Recreate the waveform plot

With NumPy and matplotlib in a separate plotting environment, point the tool
at an extracted entry archive and choose a new output folder:

```powershell
python -B tools/plot_supply_repeat.py --entry-root 'C:/extracted-entry' --out 'C:/new/plot'
```

It verifies the recorded result hash and re-extracts settling from all three
rising traces. It makes no model or simulator calls.
