# Zeno

Zeno tests analog circuit repair across supply, load and sensor changes using
three ngspice tasks with deterministic electrical grading. Seven selected
historical sessions used requested gpt-6.1-sol/High and UI-labelled GPT-6/High;
all three SUPPLY sessions exhausted three proposals without a full pass, while
LOAD and TIA achieved finer-confirmed passes. A separate frozen gpt-6.1-sol/High
CLI cohort completed five of nine planned episodes: one SUPPLY failure, two LOAD
passes and two TIA passes, with one episode interrupted and three not run.
Historical SUPPLY runs retain native simulation traces; the LOAD and TIA
sessions and the frozen cohort retain measured summaries, transcripts and
receipts. Candidate circuits, feedback and reproducible checks accompany both
records. All runs were collected in November 2026; each transcript folder
retains the per-run launch timestamps.

The target workflow is amplifier redesign: an engineer changes the supply,
load or sensor interface and needs to verify that the circuit still meets its
requirements. Zeno grades the resulting electrical behavior and retains the
candidate, measured result and supporting evidence for each recorded evaluation.

The tasks draw on amplifier compensation, feedback stability and transient
settling. Their operating grids are synthetic; reference circuits establish
feasibility under the same numerical checks.
[Engineering context and threshold sources](docs/problem.md)

## Video walkthrough

[Zeno Walkthrough | micro1 Eval Hackathon](https://youtu.be/2sTe0UKWpOI) —
public link, no sign-in required (3:21, AI-generated narration).
It covers the engineering problem, why plausible-looking answers fail, the
deterministic grading path, a real reproduction run, the measured near miss,
and the reference and deliberate-control validation.

Short description: Zeno is a deterministic evaluation for analog circuit
repair (electronics). It measures whether a model can repair a
transistor-level amplifier so it still meets every stated electrical
requirement when supply voltage, load capacitance or the sensor interface
changes. Three ngspice tasks — SUPPLY, LOAD and TIA — grade candidate
circuits with pass/fail electrical limits; no LLM judge is used. Every
SUPPLY attempt in the retained records missed at least one measured
requirement — one final circuit passed all other checks yet settled in
13.278–14.053 ns against a 12.24 ns limit — while LOAD and TIA reconfirmed
passes after refinement.

## Finding

One final SUPPLY circuit passed the other checks but settled
in 13.278-14.053 ns against a 12.24 ns rising limit. In the frozen cohort, the
SUPPLY episode missed gain and gain margin and never completed command-relative
settling. LOAD and TIA have finer-confirmed passes in both records.

[Results and failure analysis](docs/results.md) · [Collection method](docs/methodology.md)

## Tasks

| Task | What changes | Historical sessions | Frozen cohort (partial) |
|---|---|---|---|
| [SUPPLY](tasks/revisions/clarified-2/supply/TASK.md) | Supply voltage | 0 passes in 3 sessions | 0 passes in 1 complete episode; 1 interrupted |
| [LOAD](tasks/revisions/clarified-2/load/TASK.md) | Load and parasitic capacitance | 2 passes in 2 sessions | 2 passes in 2 episodes |
| [TIA](tasks/revisions/clarified-2/tia/TASK.md) | Sensor and wiring capacitance | 2 passes in 2 sessions | 2 passes in 2 episodes |

The historical record contains seven complete adaptive sessions and 24 saved
evaluations. The frozen cohort adds five complete episodes and one interrupted
episode; the two records are reported separately.
[Exact model responses](transcripts/README.md) accompany the measurements.
Those sessions used the recorded packets. The [current packets](tasks/README.md)
clarify input limits and reporting precision; their electrical requirements
are unchanged. [Task validation](docs/task-validation.md)

Three tasks, each with several operating conditions. The guide recommends 5-10
tasks; this submission deliberately keeps three validated circuit-repair
scenarios instead of adding unvalidated variants. Operating points are
conditions within a task, not separate tasks.

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
Passing references, negative controls and offline tests check the grader
and setup boundaries. No LLM judge is used.

Simulation and regrading need no model account or API keys. Collection used an
existing ChatGPT subscription; per-run inference cost was unavailable. A
recorded five-control qualification of the earlier v4 evaluator took about
three minutes after roughly 30 seconds of cached setup. The current v5
evaluation reproduced the same control classifications in a clean bootstrapped
environment. [Reproduction record](docs/reproduction.md)

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
