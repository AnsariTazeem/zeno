<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:993168b1f9f41dabed5dfa0b6cc7b40df8a9c2782fdfe59fa2d47863cb9ff8ba -->

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
and about three minutes on the tested machine; <!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:8777569ba1e60ec9056fca880a1f39a162a470b112e5621f5b3409fb45629138 -->

the recorded v5 qualification took

<!-- /coderabbit-ai-generated:v1 -->
under nine minutes on the same host. The receipts retain exact timings and file
identities. The [earlier v4 receipt](../evidence/final_validation.json) records
that qualification for its source snapshot.

The recorded v5 evaluator qualified separately after the v4 and clarified-1
material was frozen: in a clean bootstrapped Python 3.12 environment, all
[check classifications](../evidence/qualified_v5_summary.json) reproduced the
expected saved-measurement evidence, and the no-gain circuit remained a
specification failure under the v5 undefined-crossing rule. [Commands](run.md)

## Current maintenance revision

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:e8ad24719b391221e713a8cc337dbd48f9ffa119e4b525e899767b03f3c538ae -->

New grading and qualification use v6. Qualification enforces numerical agreement
(relative tolerance 1e-6, absolute tolerance 1e-9), including list-valued measurements
and nulls. On 9 November 2026, the [Windows-hosted qualification](https://github.com/AnsariTazeem/zeno/actions/runs/42560927106)
passed the offline suite and all five native controls on commit `e921a6c`. The
`native-qualification` artifact contains the run evidence and is retained by
GitHub until 16 November 2026. Earlier receipts describe their original revisions.

<!-- /coderabbit-ai-generated:v1 -->


<!-- /coderabbit-ai-generated:v1 -->