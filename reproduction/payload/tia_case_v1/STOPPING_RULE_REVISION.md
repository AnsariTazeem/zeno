# Explicit reference-selection stopping-rule revision

Both selected Rg=1000/2000 networks passed all six AC checks but missed the
500 ns transient deadline at small sensor capacitance. Maximizing minimum
phase margin was therefore an inadequate reference-selection surrogate for
the multi-objective task. Their complete failures remain unchanged.

EXTENSION_01 originally stopped if those two selected networks failed. That
extension is closed with no reference. Before abandoning the case, make one
explicit, capped follow-up: evaluate the **already enumerated and AC-tested
Rg=5000 ohm** network at all six conditions, with the same Rf=10000 ohm and
Cf=8.2 pF. This tests the remaining screened margin/bandwidth tradeoff, without
introducing a new value, topology or electrical limit.

This is an adaptive change in researcher reference exploration, not a
pre-registered unchanged stopping rule. Disclose it in the qualification report.
It cannot be treated as another model trial, a human-success comparison or an
unbiased estimate of feasibility. If it fails, close the case as unqualified;
do not continue parameter search. If it passes, only numerical confirmation,
independent measurement checks, known negative controls and qualification
closure remain authorized in this stage. No model trial starts in this stage.
