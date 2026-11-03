# Current local entry

The latest local archive is `Zeno_Eval_DRAFT_03_02.zip`: 32,825,001 bytes.
It was built from source commit `04d4d139b3de0ed37443ab5620df186c6054c53d`.
[The receipt](../evidence/latest_entry.json) records its SHA-256 and checks.
The ZIP is stored locally, not uploaded to GitHub.

The actual ZIP was extracted into a new directory. Its 57 offline checks,
15 saved model-evaluation audits, bootstrap help and prepared-evaluator
inspection passed. All manifest hashes still matched afterward. It contains
55 completed native model-run records and 20 separate clone-control native
records; those are process counts, not model-trial counts.

The three tasks, passing references, model responses, raw model-run results,
setup recipe and full clone qualification evidence are included. Simulation
dependencies still download by hash during setup; Windows Python 3.12 and
compatible Windows C/UCRT support are prerequisites.

The first assembly stopped on a Windows sandbox error during temporary-file
cleanup. The test runner now gives its subprocesses a temporary directory
inside the ignored check workspace. The corrected source and extracted
archive pass all 57 checks. The failed assembly and logs remain local.

This is a draft. The video, rights decision, independent-machine run and
broader model/task evidence remain open. See [the guide checklist](guide_checklist.md).
No agreement was accepted and no entry was submitted by this workflow.
