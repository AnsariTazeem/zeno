# Grader v4 reproduction — completed checkpoint

The updated ZIP bootstraps into a new Windows Python venv and reproduces five declared controls. The existing public asset/wheel download hashes and bootstrap mechanism are unchanged; cached bytes were reverified. This is the same host, not an independent OS/machine test.

| Control | Passing conditions | Outcome |
|---|---:|---|
| load_ref01 | 6/6 | pass |
| tia_ref01 | 6/6 | pass |
| supply_ref01 | 3/3 | pass |
| supply_neg01 | 0/3 | specification_failure |
| supply_no_gain01 | 0/3 | specification_failure |

All 50 tests pass: eight archive-boundary checks, 30 integration regressions and 12 supply-evidence tests. Twenty successful new full-circuit native processes cover 21 conditions across five controls; startup preflights are excluded. These are engineering qualification runs, not model trials.

The source kit is 3,688,925 bytes and retains vendored PyYAML with its notice, including its pinned Windows extension. The simulator/model payloads are separately acquired using the same exact public source digests as the earlier tested setup. Fresh source files and all 1,202 locked runtime inputs still match after qualification.

The first packaging attempt omitted four historical JSON fixtures used by the replay-parity test. It failed before native controls started; the failed qualification remains archived. The corrected builder now executes the assembled payload tests before creating a ZIP. Revision 2 includes the exact fixtures and passes the full fresh-environment run.

Observed cached bootstrap: 67.2 seconds; qualification wall time: 472.1 seconds with at most two control workers. These are host-specific observations, not guarantees. No model calls or paid API requests were made by setup/qualification.

Raw-evidence absence-of-unity classification remains distinct from missing data or JSON-only replay. No physical threshold, model or native test source changed. The interrupted v3 model session is not relabelled complete. Competition-license compatibility, external Windows runtime prerequisites, independent-machine reproduction and final entry materials remain separate limitations.
