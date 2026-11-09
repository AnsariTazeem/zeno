# Frozen CLI cohort

Five complete adaptive episodes and one interrupted episode from a frozen
collector run on 2026-11-04. They are separate from the seven
[historical sessions](../README.md).

| Episode | Task | Proposals | Outcome | Responses |
|---|---|---:|---|---|
| trial01 | SUPPLY | 3 | No confirmed pass | [1](trial01/proposal01/model_reply.md) · [3](trial01/proposal03/model_reply.md) |
| trial02 | LOAD | 1 | Pass, refined | [1](trial02/proposal01/model_reply.md) |
| trial03 | TIA | 2 | Pass, refined | [1](trial03/proposal01/model_reply.md) · [2](trial03/proposal02/model_reply.md) |
| trial04 | LOAD | 1 | Pass, refined | [1](trial04/proposal01/model_reply.md) |
| trial05 | TIA | 2 | Pass, refined | [1](trial05/proposal01/model_reply.md) · [2](trial05/proposal02/model_reply.md) |
| trial06 | SUPPLY | 1 | Interrupted; unscored | [1](trial06/proposal01/model_reply.md) |

The protocol requested `gpt-6.1-sol` at High effort through the CLI, with the
`clarified-1` packets, three planned episodes per task, at most three proposals
and no tools or automatic retries. Each `capture_audit.json` records the
effective model and effort, zero tool requests and the restricted read/network
policy. Each folder also retains the exact input message, candidate and
feedback; `receipt.json` links their hashes. Published receipts omit a
campaign-local run-id prefix; run suffixes and hashes are unchanged.

The campaign stopped after trial06. Trials 07-09 were not started, so task
groups are incomplete and no pass@k or pass^k estimate is reported.
[Interruption record](trial06/INTERRUPTED.md) · [Cohort summary](../../evidence/matched_cli_summary.json)
