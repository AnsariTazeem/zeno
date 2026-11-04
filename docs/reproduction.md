# Reproduction

The offline suite has 57 tests: eight setup-boundary checks, 30 grading tests,
12 raw-evidence tests and seven packet/export tests.

Native qualification runs three passing references and two SUPPLY failures:

| Control | Passing conditions |
|---|---:|
| SUPPLY reference | 3/3 |
| LOAD reference | 6/6 |
| TIA reference | 6/6 |
| Ordinary SUPPLY failure | 0/3 |
| No-gain SUPPLY failure | 0/3 |

Twenty full-circuit native processes cover 21 conditions. The reference results
were reproduced in a new local clone and venv; the source identities matched
afterward. [Local receipt](../evidence/clone_verification.json)

[GitHub Actions](https://github.com/AnsariTazeem/zeno/actions) runs the offline
suite on Windows. The manual native job also passed on a GitHub-hosted runner.
[Hosted receipt](../evidence/hosted_verification.json). Run IDs,
source commits and artifacts identify the tested snapshot.

Local cached setup took 77.703 seconds and native qualification 344.141 seconds.
These are observed timings on one computer. [Commands](run.md)
