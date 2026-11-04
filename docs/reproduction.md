# Reproduction

The offline suite has 63 tests: eight setup-boundary checks, six download-recovery
checks, 30 grading tests, 12 raw-evidence tests and seven packet/export tests.

Downloads use a separate temporary file for each attempt. Interrupted or invalid
downloads are removed; verified cache files and pre-existing partials are preserved.

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

The latest local check verified all 1,202 runtime files, passed 63 offline
tests and reproduced all five controls. Cached setup took 32.732 seconds and
native qualification took 192.526 seconds. These are observed timings on one
computer. [Latest receipt](../evidence/final_validation.json) · [Commands](run.md)
