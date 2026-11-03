# Technical interpretation of the fresh Sol trial

This note is post-collection analysis. It does not change the task, feedback, budget or scores.

Recorded stop outcome: **budget_exhausted_no_verified_pass**.

| Proposal | Profile | Supply points passing / 3 | Worst gain dB | Worst PM deg | Worst GM dB | Settled edges / 6 |
|---:|---|---:|---:|---:|---:|---:|
| 1 | baseline | 0 | 55.31 | 36.30 | 7.20 | 6 |
| 2 | baseline | 0 | 66.41 | 20.20 | 3.60 | 1 |
| 3 | baseline | 0 | 63.74 | 49.30 | 3.40 | 6 |
| 3 | refined | 0 | 63.74 | 49.30 | 3.40 | 6 |

A settled edge here means it eventually remains inside the command-relative band within its observation window. It can still miss the stricter time limit.

## What the trajectory tests

The engineering challenge is one fixed circuit satisfying coupled gain, bandwidth, loop stability, power and command tracking limits at all three declared supplies. An improvement in one metric or at one supply cannot substitute for that conjunction.

Proposal 2 raised gain compared with proposal 1. At 1.25 V, gain rose from 59.69 to 73.15 dB while phase margin fell from 36.3 to 20.2 degrees. That is a measured tradeoff in this trajectory, not a controlled proof that a particular component caused it: several topology, bias and compensation choices changed together.

Proposal 3 improved phase margin to 65.1, 58.5 and 49.3 degrees at 1.15, 1.20 and 1.25 V, respectively. The first two meet the 55-degree phase-margin requirement. However, gain is only 67.73, 67.13 and 63.74 dB (required at least 72.71), gain margin is 3.9, 4.2 and 3.4 dB (required at least 10), and both settling limits are missed at every supply. Bandwidth and power pass at all three supplies. Improving phase margin alone therefore did not repair the circuit.

Phase margin is evaluated where loop gain crosses unity. Changing a circuit can move that crossing and change the phases of several internal poles and zeros. Phase lead at a selected frequency therefore does not guarantee sufficient margin at the new crossing. Low margin can coincide with ringing and poor tracking; the separate raw transient checks establish whether each candidate actually meets the command target.

## Evidence boundaries

All 60 independent log-frequency AC comparisons preserve the native threshold classifications. These use the same simulated traces; they check extraction, not silicon accuracy. Final baseline/refinement deltas are in review_metrics.json; close.py separately validates process completion, candidate identity and tracking re-extraction.

The precollection reference control passed all three supplies. The task is feasible within this apparatus. It does not establish that a typical human completes it in three proposals or that the hypothetical supply change occurred at a named customer.

Only one adaptive task trial is counted here. Proposals, supplies and refinement reruns are correlated. The requested model is gpt-6.1-sol at High effort; exact backend revision, temperature and seed are unavailable. The code-mode host was qualified for arithmetic, but this does not imply the subject used every available affordance.

The model received its own circuit feedback plus public threshold-provenance metadata. See FEEDBACK_AUDIT_NOTE.md. Reference repairs, other task packets and new control measurements were withheld. Tool input screening and feature restrictions do not prove general OS confinement.

Next delivery gate: participant technical review, then a prospectively specified bounded repeat campaign and clean-environment reproduction. Retain solved controls and every valid pass; do not change criteria to preserve a failure. No expert sign-off or final submission readiness is claimed.
