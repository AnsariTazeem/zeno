# Results

| Session | Proposals | Final outcome |
|---|---:|---|
| SUPPLY, Sol/High CLI, v3 | 3 | No full pass |
| SUPPLY, Sol/High CLI, v4 | 3 | No full pass |
| LOAD, UI-labelled GPT-6/High | 3 | Pass |
| TIA, UI-labelled GPT-6/High | 2 | Pass |

Finer simulation confirmed each final result. The sessions use different
interfaces and grader versions; they are not a matched model comparison.

## Latest SUPPLY circuit

| Supply | Rising settling | Limit |
|---:|---:|---:|
| 1.15 V | 14.053 ns | 12.24 ns |
| 1.20 V | 13.663 ns | 12.24 ns |
| 1.25 V | 13.278 ns | 12.24 ns |

The final proposal passes the other checks but misses rising settling at all
three supplies. Earlier proposals also missed stability requirements. This
case measures the difficulty of meeting the coupled limits within three
proposals; it does not establish a general failure rate.

[Measurements](../evidence/supply_v4_summary.json) · [Catalog](../results/catalog.json) · [Responses](../transcripts/README.md)

A separate SUPPLY follow-up stopped after two replies on a wrapper defect.
It is excluded from the four complete-session count. Proposals, operating
conditions and refined reruns are correlated measurements.
