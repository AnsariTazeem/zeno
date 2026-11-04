# Zeno

Zeno evaluates AI-generated analog circuit repairs in ngspice. A circuit must
meet gain, stability, settling, accuracy and power limits at every test point.

## Tasks

| Task | What changes | Recorded result |
|---|---|---|
| [SUPPLY](tasks/supply/TASK.md) | Supply voltage | Three Sol/High sessions; 0 full passes within three proposals |
| [LOAD](tasks/load/TASK.md) | Load and parasitic capacitance | Sol/High passed on proposal 1; UI-labelled GPT-6/High on proposal 3 |
| [TIA](tasks/tia/TASK.md) | Sensor and wiring capacitance | GPT-6/High passed on proposal 2 |

Finer simulation confirmed the final results. The six recorded sessions
use different interfaces and grader versions. One SUPPLY session recovered
from a collection interruption.
[Results](docs/results.md) · [Model responses](transcripts/README.md)

## Run

Requires Windows x64 Python 3.12 and Windows C/UCRT support.

```powershell
python -I -B bootstrap.py
```

Setup prints the new environment path. From the repository root:

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B tools/run_checks.py
```

[Setup and commands](docs/run.md) · [CI](docs/ci.md)

## Code and data

- [Tasks](tasks/README.md), [reference circuits](reference/README.md), [graders](graders/README.md), [tests](tests/README.md).
- [Design](docs/design.md), [methodology](docs/methodology.md), [reproduction](docs/reproduction.md).
- [Prior work](docs/PRIOR_WORK.md) and [AI use](docs/AI_USE.md).

The runtime and regression fixtures live in `reproduction/payload/`. Recorded
prompts and responses retain their original text. These are synthetic,
simulation-only tasks; the current sample is too small for a model ranking.
