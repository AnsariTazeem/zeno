# Reproduction

The [offline suite](../tests/README.md) checks setup, grading, raw evidence, task
exports, session accounting and publication boundaries.

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

Native qualification verifies runtime identities and reproduces all five
controls. The recorded v4 qualification took about 30 seconds of cached setup
and about three minutes on the tested machine; the current v5 qualification took
under nine minutes on the same host. The receipts retain exact timings and file
identities. The [earlier v4 receipt](../evidence/final_validation.json) records
that qualification for its source snapshot.

The current v5 evaluator qualified separately after the v4 and clarified-1
material was frozen: in a clean bootstrapped Python 3.12 environment, all
[check classifications](../evidence/qualified_v5_summary.json) reproduced the
expected saved-measurement evidence, and the no-gain circuit remained a
specification failure under the v5 undefined-crossing rule. [Commands](run.md)
