# Zeno

Simulation-based evaluations of AI-assisted analog circuit repair. A proposed
circuit must meet coupled accuracy, stability, timing and power requirements
at every disclosed operating point. Invalid evidence stays separate from an
electrically valid failure.

This repository imports an existing tested evaluation snapshot. Commits split
that import by responsibility; they do not reconstruct the original development
timeline. The underlying amplifier and model infrastructure are attributed
prior work, with substantial AI-assisted extensions. No measured-silicon,
production-readiness or broad model-failure-rate claim is made.

## Tasks and observed results

| Task | Challenge | Selected complete sessions |
|---|---|---|
| SUPPLY | Joint requirements at 1.15, 1.20 and 1.25 V | Two separate Sol/High sessions had no full pass within three proposals; grader versions differ |
| LOAD | Amplifier compensation across load/parasitic conditions | GPT-6/High passed on proposal 3, with finer confirmation |
| TIA | Sensor current-to-voltage feedback across wiring/sensor conditions | GPT-6/High passed on proposal 2, with finer confirmation |

These are four selected adaptive sessions across three tasks. Proposals,
operating points and numerical reruns are correlated. An interrupted v3
SUPPLY follow-up is disclosed separately and excluded from completed trials.
Backend revisions, seeds and temperatures are unknown. See [results](docs/results.md).

## Run offline checks

Use Windows x64 Python 3.12, NumPy 2.3.5 and zstandard 0.25.0 in your chosen
environment. The bootstrapped venv below supplies both pinned dependencies:

```powershell
python -I -B tools/run_checks.py
```

This checks frozen file identities and runs 50 existing setup/grading tests.
It makes no model calls, downloads or full-circuit simulations.

## Prepare the native simulator environment

```powershell
python -I -B bootstrap.py
```

This invokes the byte-identical tested reproduction recipe, creates a new
short temporary root and venv, and prints its paths. It verifies cached bytes
or downloads pinned public assets and wheels (41,668,459 bytes on an empty
cache). Windows x64 Python 3.12 and compatible Windows C/UCRT support are
prerequisites; no API key or model account is used by setup/grading.

Run the printed root's qualification script with its own venv Python:

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B 'C:/printed/root/qualification.py'
```

Qualification runs the tests and five fresh circuit controls. The existing
host qualification passed 50 tests and reproduced 21 conditions through 20
successful full-circuit native processes. Independent-machine/OS reproduction
remains unperformed. Existing output directories are exclusive; do not reuse
a qualification root or run ID. See [setup details](docs/reproduction.md).

To inspect or evaluate a circuit using that prepared root:

```powershell
python -I -B run_eval.py --prepared-root 'C:/printed/root' inspect --task supply
python -I -B run_eval.py --prepared-root 'C:/printed/root' evaluate --task supply --candidate 'C:/your/circuit.sp' --run-id new01
```

Exit 0 includes valid electrical failures; 2 means invalid input and 3 means
infrastructure failure. Add `--numerics refined` for the frozen finer profile.
The runner does not provision model access or automatically collect responses.

## Find the code

- [Current evaluator](reproduction/payload/eval_core_v4/run_eval.py) and [raw-evidence supply adapter](reproduction/payload/eval_core_v4/supply_adapter.py).
- Public task packets: [SUPPLY](reproduction/payload/analog_supply_pilot_v1/public_v2/TASK.md), [LOAD](reproduction/payload/capload_case_v1/public/TASK.md), [TIA](reproduction/payload/tia_case_v1/public/TASK.md).
- [Grading tests](reproduction/payload/eval_core_v4/test_core.py), [supply evidence tests](reproduction/payload/eval_core_v4/test_supply_evidence.py) and [setup boundary tests](reproduction/payload/checks/test_bootstrap.py).
- [Methodology and isolation](docs/methodology.md), [attribution](docs/PRIOR_WORK.md), [AI assistance](docs/AI_USE.md) and [rights inventory](docs/RIGHTS_REVIEW.md).

The versioned reproduction tree intentionally retains historical namespaces,
small compatibility modules and native regression fixtures so its tested hashes
stay unchanged. Generated runs, simulator/model downloads, installers, raw local
research and unrelated OpenCode artifacts are excluded from the Git import.

This is a trusted verifier repository containing answers and witnesses. Never
give the whole repository to a subject model. Export only one public task
packet per fresh context. Public availability may affect future contamination
assumptions; no OS-confidentiality guarantee is claimed.

## Evidence and delivery status

`evidence/` contains compact measured summaries and validation receipts. The
complete 27,434,760-byte local entry archive retains selected raw model outputs,
decks and traces; its digest is recorded in [the archive identity](evidence/entry_archive.json).
It has not been uploaded by the initial source-import workflow. Git fixtures
are regression inputs, not a replacement for the complete collection archive.

The entry remains a draft: three tasks versus the guide's recommended 5–10,
small selected model samples, unresolved third-party competition-rights review,
no independent-machine run and no hosted walkthrough yet. Existing license
notices retain their scope; no new blanket license is asserted. No independent
human expert validation, organizer approval or winning probability is claimed.
