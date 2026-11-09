<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:8176564dbec1f876da99f3b4713a51b34c16b1e7af0264d2d7bd7cdf6ca40a64 -->

# Zeno

I built Zeno to evaluate analog circuit repair when supply voltage, load capacitance,
or sensor capacitance changes. Three ngspice tasks grade candidate circuits against
electrical limits for accuracy, speed, stability and power. Every requirement must
pass at every operating point; grading does not use an LLM judge.

## Tasks

| Task | Design change | Conditions |
|---|---|---|
| [SUPPLY](tasks/revisions/clarified-2/supply/TASK.md) | Repair a transistor-level amplifier for lower supply voltages | Three supplies |
| [LOAD](tasks/revisions/clarified-2/load/TASK.md) | Compensate a fixed amplifier for capacitive loading | Six load/parasitic pairs |
| [TIA](tasks/revisions/clarified-2/tia/TASK.md) | Design passive feedback for a current sensor | Six sensor/wiring pairs |

The operating grids are synthetic. Passing references establish feasibility under
the same checks used for candidate circuits. [Engineering context](docs/problem.md)

## Results

The historical record contains seven complete sessions and 24 evaluations.
SUPPLY exhausted its three-proposal budget in all three sessions. LOAD and TIA
passed in both of their sessions, with finer numerical confirmation.
One final SUPPLY candidate passed the other checks but settled in 13.278–14.053 ns
against a 12.24 ns rising limit.

A separate frozen CLI cohort completed five of nine planned episodes: one SUPPLY
failure, two LOAD passes and two TIA passes. One episode was interrupted and three
were not run. These records use different packet and grader revisions and are
reported separately. They do not establish a population failure rate or model ranking.

[Results and measurements](docs/results.md) · [Collection method](docs/methodology.md) ·
[Original responses](transcripts/README.md)

## Run

Requires Windows x64 Python 3.12 and compatible Windows C/UCRT support.

```powershell
python -I -B bootstrap.py
```

Setup prints the prepared environment path. From the repository root:

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B tools/run_checks.py
python -I -B run_eval.py --prepared-root 'C:/printed/root' evaluate --task supply --candidate 'C:/your/circuit.sp' --run-id new01
```

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:9e7a404d871b7ea926c1721b99cbf4628cfc0a5165dea3f3befd954857c134df -->

Simulation and regrading need no model account or API keys. The current evaluator
is v6. Earlier evaluators and their receipts remain available for reproducing
recorded results. A [Windows qualification run](https://github.com/AnsariTazeem/zeno/actions/runs/42560927106) passed
the offline suite and all five native controls on commit `e921a6c`.

<!-- /coderabbit-ai-generated:v1 -->

[Setup and commands](docs/run.md) · [Grading](graders/README.md) · [CI](docs/ci.md)

## Walkthrough

[Video walkthrough](https://youtu.be/2sTe0UKWpOI) covers the problem, grading,
reproduction, a measured near miss, references and negative controls.

## Code and evidence

- [Public task packets](tasks/README.md), [reference circuits](reference/README.md), [tests](tests/README.md).
- [Design](docs/design.md), [task validation](docs/task-validation.md), [reproduction](docs/reproduction.md).
- [Prior work and licenses](docs/PRIOR_WORK.md), [historical files and prerequisites](docs/history.md).

The amplifier and original testbench foundation come from AnalogPortBench (MIT).
Zeno adds the task grids, input restrictions, grading adapters and collection tools.
The runtime and regression fixtures live in `reproduction/payload/`.
Original prompts, responses and measurements retain their recorded contents.

Export one task packet per fresh model context. This repository contains reference
solutions, and LOAD/TIA's fixed amplifier exposes SUPPLY's repair.


<!-- /coderabbit-ai-generated:v1 -->