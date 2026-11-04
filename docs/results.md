# Results

| Session | Proposals | Final outcome |
|---|---:|---|
| SUPPLY, Sol/High CLI, v3 | 3 | No full pass |
| SUPPLY, Sol/High CLI, v4 | 3 | No full pass |
| SUPPLY repeat, Sol/High CLI, v4 | 3 | No full pass; collection recovered |
| LOAD, UI-labelled GPT-6/High | 3 | Pass |
| LOAD, Sol/High CLI, v4 | 1 | Pass |
| TIA, UI-labelled GPT-6/High | 2 | Pass |

Finer simulation confirmed each final result. The sessions use different
interfaces and grader versions; they are not a matched model comparison.

## Fresh LOAD CLI session

The first proposal passes all six conditions, confirmed with finer numerics.
It uses three resistors: output isolation and a divider that compensates the
known load's DC voltage drop. Refined worst settling is 1.99025 us,
maximum overshoot/undershoot is 0.00391143 mV, and minimum phase
margin is 53.5768 degrees. The allowed three-proposal budget stops at
this confirmed pass.

[Measurements](../evidence/load_cli_summary.json) · [Exact answer](../transcripts/load_cli/proposal01/model_reply.md)

## Latest SUPPLY repeat

Final outcome: **no full pass** after 3 proposals. The final circuit misses these checks:

| Metric | Required | 1.15 V | 1.20 V | 1.25 V |
|---|---:|---:|---:|---:|
| Gain, dB | >= 72.71 | 66.700 | 74.170 | 78.120 |
| Phase margin, degrees | >= 55 | 37.300 | 36.500 | 37.500 |
| Gain margin, dB | >= 10 | 5.100 | 4.600 | 4.700 |
| Rising settling, ns | <= 12.24 | Not settled | Not settled | Not settled |
| Falling settling, ns | <= 26.73 | 32.800 | 31.741 | 37.253 |

![Final rising-step response at the three supplies](../evidence/supply_repeat_rising.png)

The output rings and remains below the 1 V target. Briefly crossing the
accuracy band does not satisfy settling. The plot uses the retained finer
traces; its error zoom clips values beyond +/-10 mV.

A UTC/local-date trace lookup stopped collection before the first circuit
was graded. The retained answer was verified and the same session resumed;
it was not regenerated. This is one recovered adaptive trial, not two.

The earlier v4 final circuit passed the other checks but missed rising
settling: 13.278–14.053 ns against a 12.24 ns limit.

[Repeat measurements](../evidence/supply_v4_repeat_summary.json) · [Earlier measurements](../evidence/supply_v4_summary.json) · [Catalog](../results/catalog.json) · [Responses](../transcripts/README.md)

A separate v3 follow-up stopped after two replies on a wrapper defect.
It is excluded from the six complete-session count. Proposals, operating
conditions and refined reruns are correlated measurements. This small
selected sample does not establish a general failure rate.
