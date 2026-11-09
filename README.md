# Zeno

Short description: Zeno is a deterministic evaluation for analog circuit
repair (electronics). In this domain an answer is correct only under
measurement, so schematic text that merely sounds right often fails when the
circuit is simulated. The eval measures whether a model can repair a
transistor-level amplifier so that every stated electrical requirement still
passes when the supply voltage, load capacitance or sensor interface changes.
Three ngspice tasks — SUPPLY, LOAD and TIA — grade candidate circuits with
fixed pass/fail limits; no LLM judge is used. Key finding: every SUPPLY
session in the retained records missed at least one measured requirement —
the best circuit settled in 13.278–14.053 ns against a 12.24 ns limit — while
LOAD and TIA passes were confirmed after refinement.

## Video walkthrough

[Zeno Walkthrough | micro1 Eval Hackathon](https://youtu.be/2sTe0UKWpOI)
(3 minutes 21 seconds) — shows the engineering problem, what a task prompt and
candidate look like, the deterministic grading path in a real terminal, the
measured near miss, and the reference and deliberately wrong circuits that
validate the grader.

## Domain and expertise

Analog circuit design. The evaluation draws on amplifier design, frequency
compensation, feedback-loop stability (phase and gain margins), transient
settling, and sensor-interface design with transimpedance amplifiers.

## What it tests and why it matters

Each task changes one realistic design constraint and asks the model to keep
the circuit inside every stated limit. Engineers make these exact changes
when a product spec moves; the hard part is that gain, stability margins,
settling and power interact, so a repair that fixes one requirement tends to
break another. This eval is for anyone benchmarking models on engineering
work where a convincing wrong answer has a real cost: grading is by
measurement only, so an answer that merely sounds right cannot score.

## Tasks

Three tasks, each with several operating conditions; operating points are
conditions within a task, not separate tasks.

| Task | Design change | Why it is difficult |
|---|---|---|
| [SUPPLY](tasks/revisions/clarified-2/supply/TASK.md) | Run one repaired amplifier at three lower supply voltages | Bias points shift with the supply, moving gain, margins, settling and power together; fixed circuit elements then interact at each supply. |
| [LOAD](tasks/revisions/clarified-2/load/TASK.md) | Drive acquisition inputs with heavier parasitic capacitance | The load moves the loop's pole and the buffer must keep accuracy and stability at six load/parasitic pairs while only the surrounding passive network may change. |
| [TIA](tasks/revisions/clarified-2/tia/TASK.md) | Sense a photodiode through wiring and sensor capacitance | The feedback network must hold signed conversion accuracy, bandwidth, stability and power across six capacitance pairs with fixed devices and a fixed subcircuit interface. |

- Every requirement must pass at every operating point; scores are 100 or 0.
  Invalid inputs and incomplete simulation evidence are scored separately
  from electrical failures.
- Any compliant circuit is accepted — the reference netlist is not required.
- [Reference circuits](reference/README.md) are public; reference and
  deliberately wrong controls validate the grader (they pass and fail as
  designed).

## Setup and run

Prerequisites: Windows x64 with Python 3.12 installed system-wide. No API
keys, tokens or environment variables are required — evaluation is local
simulation (see `.env.example`).

Setup, in one command (prints the prepared environment root):

```powershell
python -I -B bootstrap.py
```

Offline regression checks, from the repository root (about 30 s):

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B tools/run_checks.py
```

Grade any candidate circuit, e.g. the bundled reference (seconds per run):

```powershell
python run_eval.py --prepared-root 'C:/printed/root' evaluate --task supply --candidate reference/supply.sp --run-id readme_example
```

Use `--task load` or `--task tia` with any candidate file; the JSON result
carries the measured values and per-requirement verdicts. A five-control
grader qualification runs in five to nine minutes after about a minute of
cached setup (longer with a cold download cache). Evaluation is local and
free; the recorded model sessions ran through an existing ChatGPT
subscription, and per-run inference cost is not reported.
[Setup and commands](docs/run.md) · [Reproduction record](docs/reproduction.md)

## Models tested and results

All model sessions were collected in November 2026. Reasoning effort was High
in both interfaces. Temperature and seed were not set (interface defaults;
recorded per run in `results/catalog.json`). A session could submit at most
three candidate circuits, with evaluator feedback between proposals and no
tools or web access. The two records are reported separately because they
come from different packets and grader versions.

Selected historical record — 7 sessions, 24 evaluations:

| Task | Sessions | Proposals per session | Full passes | Final score |
|---|---|---|---|---|
| SUPPLY | 3 | up to 3 | 0 of 3 | 0 |
| LOAD | 2 | up to 3 | 2 of 2 | 100 (pass, refined) |
| TIA | 2 | up to 3 | 2 of 2 | 100 (pass, refined) |

Models as recorded: `gpt-6.1-sol` with High reasoning over the CLI (5
sessions) and `GPT-6` with High reasoning over the web UI (2 sessions). Each
capture receipt stores its exact model label, and per-run dates are in the
transcripts.

Matched CLI cohort — `gpt-6.1-sol` / High, CLI:

| Task | Episodes | Proposals per episode | Full passes |
|---|---|---|---|
| SUPPLY | 1 | up to 3 | 0 of 1 |
| LOAD | 2 | up to 3 | 2 of 2 |
| TIA | 2 | up to 3 | 2 of 2 |

Representative transcripts for every session and episode are indexed in
[transcripts/README.md](transcripts/README.md) (cohort:
[matched_cli](transcripts/matched_cli/README.md)), with measured summaries in
[results](results/README.md) and raw entries in
[evidence](evidence/matched_cli_summary.json).

## Why models fail

- SUPPLY: every session missed at least one measured requirement. The best
  final circuit passed gain, margin, power and falling-settling checks, yet
  its step response crosses the target band briefly and then rings — the
  grader counts settling only once the output stays put, so that near miss
  (above) failed. Another session missed gain and gain margin outright.
  Compensation that reads well on a schematic left too little reserve once
  gain, margins, settling and power were measured together.
- LOAD/TIA: passes were earned, not automatic. In both records the first TIA
  proposal missed the initial-accuracy requirement and the refined second
  proposal passed; LOAD sessions refined a working candidate to a
  confirmed pass.
- Measurement exposes what inspection misses: candidates that look right in
  schematic form fail on loop dynamics — the margin/settling trade-off.
  [Full failure analysis](docs/results.md)

## Prior work and sources

- [AnalogPortBench](docs/PRIOR_WORK.md) (MIT): amplifier circuits and the
  measurement foundation come from it; Zeno adds the task grids, restrictions,
  grading adapters and collection workflow. Upstream licences are retained in
  each task packet (`LICENSE_UPSTREAM.txt`).
- Thresholds and engineering context: [docs/problem.md](docs/problem.md).
  Task validation: [docs/task-validation.md](docs/task-validation.md).
- AI tools assisted implementation and analysis;
  [disclosure](docs/AI_USE.md).

## Repository map

- [Tasks](tasks/README.md) — task packets, contracts, prompts.
- [Graders](graders/README.md) and [run_eval.py](run_eval.py) — deterministic
  grading.
- [Results and evidence](results/README.md) — scores, raw measured outputs.
- [Transcripts](transcripts/README.md) — full model responses.
- [Tests](tests/README.md) — 119 offline checks including grader regressions.
- Runtime and qualification fixtures: `reproduction/`.
