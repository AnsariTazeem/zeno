# Zeno

Zeno evaluates AI-generated repairs to analog circuits. It runs proposed
circuits in ngspice across fixed operating conditions, checking gain,
stability, settling, accuracy and power together.

This targets amplifier and sensor-interface design, where a circuit can look
stable yet miss a timing or accuracy limit. The scenarios use public SKY130
circuits; they are simulated examples, not measured hardware.

## Results so far

| Task | Repair | Observed result |
|---|---|---|
| [SUPPLY](tasks/supply/TASK.md) | Meet requirements at three supply voltages | Two Sol/High sessions: no full pass within three proposals each |
| [LOAD](tasks/load/TASK.md) | Compensate an amplifier across six load conditions | GPT-6/High passed on proposal 3 |
| [TIA](tasks/tia/TASK.md) | Design feedback for six sensor/wiring conditions | GPT-6/High passed on proposal 2 |

Finer simulation confirmed the final outcomes. The latest SUPPLY circuit
misses only rising settling: 13.278-14.053 ns against a 12.24 ns limit.
These are four adaptive sessions, not a model ranking. Grader versions and
interfaces differ. [Results and limits](docs/results.md) · [Model responses](transcripts/README.md)

## Run it

Use Windows x64 Python 3.12 with compatible Windows C/UCRT support:

```powershell
python -I -B bootstrap.py
```

Setup prints a new environment path. Use its Python for the offline checks:

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B tools/run_checks.py
```

Every requirement must pass at every task condition. Invalid evidence is
unscored. No LLM judge is used. [Setup, grading, runtime and cost](docs/run.md)

## Find things

- [Tasks](tasks/README.md), [reference circuits](reference/README.md), [graders](graders/README.md), [tests](tests/README.md).
- [Recorded results](results/README.md) and [transcripts](transcripts/README.md).
- [Lessons from SWE-bench, tau2-bench and Terminal-Bench](docs/benchmark_lessons.md).
- [Prior work](docs/PRIOR_WORK.md), [AI assistance](docs/AI_USE.md) and [guide checklist](docs/guide_checklist.md).
- [Automated checks](docs/ci.md): workflow defined; no hosted run yet.
- [Clean-clone test](docs/clone_reproduction.md): 57 checks and five native controls reproduced on this host.

The tested source lives under `reproduction/payload/`. Its paths and hashes
stay unchanged; the folders above make it easier to inspect. The full local
entry archive is identified in [evidence/entry_archive.json](evidence/entry_archive.json).

**Status: draft.** More trials, an independent-machine run, rights review and
the walkthrough remain open. The guide checklist records the gaps.
Nothing has been submitted or pushed to GitHub.
