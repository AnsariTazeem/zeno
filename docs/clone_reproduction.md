# Clean-clone reproduction

The committed source at `c3fd48ddff9aca0c53f26a041f06a1df7877b4ee` was cloned locally into a new short
directory using Git's normal transport, without shared object storage or
alternates. The clone contained 482 tracked files and none of the surrounding
research directories.

A new venv was bootstrapped from the clone using hash-reverified cached
assets. All 57 offline checks passed. Fresh native qualification then
reproduced three positive references and two expected SUPPLY failures:

| Control | Passing conditions |
|---|---:|
| SUPPLY reference | 3/3 |
| LOAD reference | 6/6 |
| TIA reference | 6/6 |
| Ordinary SUPPLY failure | 0/3 |
| No-gain SUPPLY failure | 0/3 |

Twenty full-circuit native processes covered 21 conditions. Qualification
also reran the original 50 tests; those are not additional independent tests
or model trials. Source identities still matched afterward, and the clone's
Git working tree stayed clean.

Observed times: cached bootstrap 77.7 seconds, offline checks 9.7 seconds
and native qualification 344.1 seconds. The [receipt](../evidence/clone_verification.json)
records the exact source commit, counts and scope.

This closes the risk that the tested snapshot silently needs untracked
research files. It remains a same-host test using an existing verified cache.
It does not establish independent-machine/OS or cold-cache reproduction.
The [CI workflow](ci.md) is defined but has not run on GitHub.
