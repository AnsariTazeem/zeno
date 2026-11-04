# Tests

Run `python -I -B tools/run_checks.py` from the repository root using the
prepared venv Python. It needs the pinned NumPy and zstandard packages.

| Suite | Tests | Purpose |
|---|---:|---|
| [Bootstrap boundaries](../reproduction/payload/checks/test_bootstrap.py) | 8 | Archive paths, links, duplicate members, hashes and decompression bounds |
| [Grading regressions](../reproduction/payload/eval_core_v4/test_core.py) | 30 | Correct/incorrect circuits, equivalent results, limits and malformed data |
| [Supply evidence](../reproduction/payload/eval_core_v4/test_supply_evidence.py) | 12 | No-gain evidence, missing/corrupt traces, timeouts and identity changes |
| [Repository/export checks](test_repository_layout.py) | 7 | Actual exported packets, tamper rejection and pinned references |
| [Download recovery](test_download_recovery.py) | 6 | Interrupted streams, invalid payloads, HTTPS redirects and verified caches |
| [Task contracts](test_task_contracts.py) | 10 | Current exports, leakage/tamper rejection, numerical declarations, reporting precision and verdict boundaries |
| [Trial summary](test_trial_summary.py) | 15 | Duplicate/missing trials, settings drift, confirmation mismatches, early stops and non-electrical outcomes |
| [Publication boundaries](test_publication.py) | 6 | Local paths, credentials, private session fields, redaction integrity and source boundaries |
| [Collection protocol](test_collection.py) | 16 | Input freezes, trial counts, invalid answers, stopping rules, numerical confirmation and private feedback |

These 110 offline tests do not run model inference or full-circuit simulation.
The prepared root's separate `qualification.py` runs the original 50 tests
and five native controls. Logs use a new directory under `.local-checks/`.
