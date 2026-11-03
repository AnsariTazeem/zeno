# Selected results

Four complete selected adaptive sessions cover three tasks. The separate
interrupted v3 follow-up is excluded from that denominator. LOAD and TIA
passed; both complete SUPPLY sessions exhausted three proposals without
a full pass. Versions/interfaces differ; no population rate is inferred.

## Fresh v4 SUPPLY session

| Proposal | Profile | Supply V | Rise settling ns | Full pass |
|---:|---|---:|---:|---|
| 1 | baseline | 1.15 | 18.372 | False |
| 1 | baseline | 1.2 | 16.792 | False |
| 1 | baseline | 1.25 | 7.372 | False |
| 2 | baseline | 1.15 | 14.432 | False |
| 2 | baseline | 1.2 | 13.782 | False |
| 2 | baseline | 1.25 | 13.322 | False |
| 3 | baseline | 1.15 | 14.052 | False |
| 3 | baseline | 1.2 | 13.672 | False |
| 3 | baseline | 1.25 | 13.282 | False |
| 3 | refined | 1.15 | 14.053 | False |
| 3 | refined | 1.2 | 13.663 | False |
| 3 | refined | 1.25 | 13.278 | False |

The final circuit passes every check except rising settling, whose limit is
12.24 ns. Its finer profile confirms the same failure at all three supplies.
Three proposals and twelve baseline/refined operating points are one
adaptive session, not twelve independent samples. See the compact JSON
under evidence/ and the complete local archive identified there.

Reproduction: 50 tests, five controls, 21 conditions and 20 successful
native processes in a fresh venv on the existing Windows host. Independent
machine/OS replication and broader matched model collection remain open.
