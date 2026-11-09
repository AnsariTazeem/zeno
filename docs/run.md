<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:90e5ea311fcb64a7c2365f5afe5adaf311e9506c400f8ff410d6ae07a4095a96 -->

# Setup and commands

Use Windows x64 Python 3.12 and compatible Windows C/UCRT support. Run commands
from the repository root.

## Prepare dependencies

```powershell
python -I -B bootstrap.py
```

Setup verifies cached files or downloads pinned archives and wheels:
about 42 MB with an empty cache. It creates a short temporary root and
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

This verifies pinned files and runs the regression suite covering setup, download
recovery, grading, raw evidence, task exports, session accounting and publication
boundaries. It makes no model calls, downloads or full-circuit simulation runs.
Logs go to the ignored `.local-checks/` folder.
Test subprocesses use a temporary directory inside that log folder, so they
do not need write access to the system temporary directory.

## Reproduce native controls

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B 'C:/printed/root/qualification.py'
```

This runs 51 grading tests (8 bootstrap-boundary, 30 frozen grading
regressions, 13 SUPPLY-evidence regressions) and five circuit controls: three
passing references, an ordinary SUPPLY failure and a no-gain SUPPLY failure.
Use a fresh prepared root: qualification refuses to overwrite earlier outputs.
The updated qualification uses v6 and compares every reported check value with
relative tolerance 1e-6 and absolute tolerance 1e-9. Native validation of v6
requires a new Windows run; the linked receipts cover earlier revisions.

The recorded v4 runs used about 30 seconds of cached setup and about three
minutes of native qualification on the tested machine; the v5 qualification took
under nine minutes on the same host. Qualification covered 21 conditions in 20
native processes. [Earlier v4 run receipt](../evidence/final_validation.json) ·
[Recorded v5 run receipt](../evidence/qualified_v5_summary.json) ·
[Reproduction](reproduction.md)

The earlier source was checked in a fresh clone and venv. See [reproduction](reproduction.md)
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

Export defaults to the current packet. Add `--revision recorded` for the
<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:d03fc7cbbc9eb780d6586ab83a2fd9257ed94629b6344fde93ccdf6b8e3296ff -->

exact historical task inputs. Electrical grading requirements are unchanged.
The prepared v6 evaluator also

<!-- /coderabbit-ai-generated:v1 -->
supports `export-task --task supply --out NEW_FOLDER --revision clarified-2`
with the same catalog and defaults.
Run `tools/audit_tasks.py` with the prepared Python to check declarations,
input boundaries and verdicts. [Audit details](task-validation.md)

## Runtime and evidence

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:d32194228324269665cda0025ebcb1527d89db721be998dfe446ef669b0545f7 -->

Setup, tests and circuit grading make zero model calls. The collection interface
and model configuration are recorded per campaign.

<!-- /coderabbit-ai-generated:v1 -->
Use the [collection commands](collection.md) to prepare fixed inputs and record
new externally captured responses. Model access remains separate from simulation.

A SUPPLY evaluation launches six native testbenches; LOAD/TIA each launch one
process spanning six conditions. Time depends on circuit behavior, profile and
host. The qualification timings measure the five-control batch, not a fixed
per-candidate runtime.

Model settings, dates, capture timing and candidate feedback are retained in
[transcripts](../transcripts/README.md). The full raw entry archive remains
local; its identity is in [the archive record](../evidence/entry_archive.json).

## Recreate the waveform plot

With NumPy and matplotlib in a separate plotting environment, point the tool
at the original extracted entry archive and choose a new output folder.
This archive is not published; the public checkout alone cannot recreate that
specific plot. See [historical prerequisites](history.md).

```powershell
python -B tools/plot_supply_repeat.py --entry-root 'C:/extracted-entry' --out 'C:/new/plot'
```

It verifies the recorded result hash and re-extracts settling from all three
rising traces. It makes no model or simulator calls.


<!-- /coderabbit-ai-generated:v1 -->