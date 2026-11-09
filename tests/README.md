<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:5e25f59dcdc585f243cd2d277ff7608c35f752a5be4207fb1350d89c737c0336 -->

# Tests

Run `python -I -B tools/run_checks.py` from the repository root using the
prepared venv Python. It needs the pinned NumPy and zstandard packages.

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:a7393f16031f14e553a79140346c72e4bafaaf8af630b24f073324af8f2637f7 -->

<!-- coderabbit-ai-generated-section:v1:200c526e5eef078cd142efd6f06476ed4f1828154843df406358f5b4848c6282 -->

| Suite | Tests | Purpose |
|---|---:|---|
| [Bootstrap boundaries](../reproduction/payload/checks/test_bootstrap.py) | 8 | Archive paths, links, duplicate members, hashes and decompression bounds |
| [Grading regressions](../reproduction/payload/eval_core_v6/test_core.py) | 30 | Correct/incorrect circuits, equivalent results, limits and malformed data |
| [Supply evidence](../reproduction/payload/eval_core_v6/test_supply_evidence.py) | 13 | No-gain evidence, undefined gain-margin classification, missing/corrupt traces, timeouts and identity changes |
| [Repository/export checks](test_repository_layout.py) | 7 | Actual exported packets, tamper rejection and pinned references |
| [Download recovery](test_download_recovery.py) | 6 | Interrupted streams, invalid payloads, HTTPS redirects and verified caches |
| [Task contracts](test_task_contracts.py) | 10 | Current exports, leakage/tamper rejection, numerical declarations, reporting precision and verdict boundaries |
| [Trial summary](test_trial_summary.py) | 15 | Duplicate/missing trials, settings drift, confirmation mismatches, early stops and non-electrical outcomes |
| [Publication boundaries](test_publication.py) | 6 | Local paths, credentials, private session fields, redaction integrity and source boundaries |
| [Collection protocol](test_collection.py) | 18 | Input/history freezes, trial counts, invalid answers, stopping rules, numerical confirmation, CLI dispatch and private feedback |
| [CLI transport](test_transport.py) | 6 | Effective model/access policy, forbidden tools, native provider settings and capture ownership |
| [Runtime integrity](test_runtime_integrity.py) | 12 | Recovered-run identity and artifact checks, numerical agreement, packet revisions, feedback reasons, optimization and staging cleanup |

<!-- /coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:0f58341b9c90abe402bd135344f27502ca8b5d4111d9896d9e349c18a25f42d5 -->

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:1464e9418f56ac167776aa84c3244bf80d32ae881f00a0478d0f9ee3b30144da -->

These 131 offline tests do not run model inference or full-circuit simulation.

<!-- /coderabbit-ai-generated:v1 -->

<!-- /coderabbit-ai-generated:v1 -->
The frozen v1–v5 evaluators and their test files remain available for historical
reproduction. The current suite runs the v6 grading tests. The prepared root's
separate `qualification.py` runs the grading tests and five native controls
through the current runner. Logs use a new directory under `.local-checks/`.


<!-- /coderabbit-ai-generated:v1 -->