# Zeno

Zeno tests analog circuit repair across supply, load and sensor changes using
three ngspice tasks with deterministic electrical grading. In seven selected
adaptive sessions using requested Sol/High CLI and UI-labelled GPT-6/High, all
three SUPPLY sessions exhausted three proposals without a full pass; LOAD and
TIA achieved finer-confirmed passes. Candidate circuits, feedback, raw
simulation traces and reproducible checks accompany the results.

The target workflow is amplifier redesign: an engineer changes the supply,
load or sensor interface and needs to verify that the circuit still meets its
requirements. Zeno grades the resulting electrical behavior and retains the
candidate, simulation traces and score.

The tasks draw on amplifier compensation, feedback stability and transient
settling. Their operating grids are synthetic; reference circuits establish
feasibility under the same numerical checks.

## Finding

One final SUPPLY circuit passed the other checks but settled
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

Each circuit must pass every stated requirement at every operating point.
The deterministic grader accepts electrically valid alternatives and keeps
invalid inputs and execution errors separate from electrical failures.
Passing references, negative controls and 63 offline tests check the grader
and setup boundaries. No LLM judge is used.

Simulation and regrading need no model account or API keys. Collection used an
existing ChatGPT subscription; per-run inference cost was unavailable. A
recorded five-control qualification took 344.141 seconds after 77.703 seconds
of cached setup. [Reproduction record](docs/reproduction.md)

## Code and data

- [Tasks](tasks/README.md), [reference circuits](reference/README.md), [graders](graders/README.md), [tests](tests/README.md).
- [Design](docs/design.md), [methodology](docs/methodology.md), [reproduction](docs/reproduction.md).
- [Prior work](docs/PRIOR_WORK.md) and [AI use](docs/AI_USE.md).

The amplifier and original measurement foundation come from AnalogPortBench
(MIT). Zeno adds the task grids, restrictions, grading adapters and collection
workflow. AI tools assisted research, implementation and analysis; validation
includes native simulation, negative controls and raw-trace checks.

The runtime and regression fixtures live in `reproduction/payload/`.
The tasks use synthetic simulation conditions. Trial-time prompts, responses
and measurement records retain their original content.
