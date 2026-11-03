# Evidence-aware supply failure classification — version 4

The interrupted SUPPLY repetition exposed a real adapter defect: complete native
sweeps with loop gain entirely below 0 dB yield undefined UGF/PM, which v3 treats
as missing infrastructure data. Native simulation itself succeeded and reported
electrical noncompliance. v4 accepts this narrow, raw-evidence-certified case as
a specification failure, preserving undefined metrics as null rather than
fabricating values. Physical requirements and native test sources are unchanged.

The raw witness checks successful pinned native processes, deck/candidate
identities, every supply, full finite log-frequency coverage and exact frozen
transient re-extraction. All sampled loop gain must be strictly below -0.001 dB.
Missing data, NaNs, wrong grids, failed native execution and JSON-only nulls
remain infrastructure outcomes. Other undefined-crossing cases are not solved
by this narrow fix. Loop margins are not invented or interpreted as stability.

The three original tasks remain available. `evaluate` uses the raw witness for
SUPPLY. `audit-native --task supply --source <native-directory> --run-id <new>`
reclassifies retained complete native artifacts without simulation; its evidence
mode is explicitly retained_raw_native_audit. Plain `replay` still has no raw
evidence and cannot turn null JSON metrics into a scored electrical result.

The original v3 results, interrupted model trial and frozen batch remain intact.
An offline corrected verdict is not a completed adaptive model trial and does
not authorize an unrecorded third proposal or retrospective resume. No new
collection condition is silently pooled with the original one.
