# Zeno

Zeno evaluates model-generated analog circuit repairs in ngspice. It checks
whether one circuit meets gain, stability, settling, accuracy and power limits
across a specified operating grid.

The target workflow is amplifier redesign: an engineer changes the supply,
load or sensor interface and needs to verify that the circuit still meets its
requirements. Zeno grades the resulting electrical behavior and retains the
candidate, simulation traces and score.

## Finding

Three collected SUPPLY sessions ended without a full pass within their
three-proposal budgets. One final circuit passed the other checks but settled
in 13.278-14.053 ns against a 12.24 ns rising limit. LOAD and TIA have
finer-confirmed passes.

[Results and failure analysis](docs/results.md) · [Collection method](docs/methodology.md)

## Tasks

| Task | What changes | Recorded result |
|---|---|---|
| [SUPPLY](tasks/supply/TASK.md) | Supply voltage | Three Sol/High sessions; 0 full passes within three proposals |
| [LOAD](tasks/load/TASK.md) | Load and parasitic capacitance | Sol/High passed on proposal 1; UI-labelled GPT-6/High on proposal 3 |
| [TIA](tasks/tia/TASK.md) | Sensor and wiring capacitance | Sol/High CLI and UI-labelled GPT-6/High both passed on proposal 2 |

The record contains seven complete adaptive sessions and 24 saved evaluations.
[Exact model responses](transcripts/README.md) accompany the measurements.

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

The runtime and regression fixtures live in `reproduction/payload/`.
The tasks use synthetic simulation conditions. Trial-time prompts, responses
and measurement records retain their original content.
