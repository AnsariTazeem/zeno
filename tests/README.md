# Tests

Run `python -I -B tools/run_checks.py` from the repository root using the
prepared venv Python. It needs the pinned NumPy and zstandard packages.

| Suite | Tests | Purpose |
|---|---:|---|
| [Bootstrap boundaries](../reproduction/payload/checks/test_bootstrap.py) | 8 | Archive paths, links, duplicate members, hashes and decompression bounds |
| [Grading regressions](../reproduction/payload/eval_core_v4/test_core.py) | 30 | Correct/incorrect circuits, equivalent results, limits and malformed data |
| [Supply evidence](../reproduction/payload/eval_core_v4/test_supply_evidence.py) | 12 | No-gain evidence, missing/corrupt traces, timeouts and identity changes |
| [Repository/export checks](test_repository_layout.py) | 7 | Actual exported packets, tamper rejection and pinned references |

These 57 offline checks do not run model inference or full-circuit simulation.
The prepared root's separate `qualification.py` runs the original 50 tests
and five native controls. Logs use a new directory under `.local-checks/`.
