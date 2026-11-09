# Task validation

Each task states its input format, operating conditions, measurements and limits.
The audit checks these declarations against the compiler and grader.

## Input checks

The compiler checks input size, permitted devices and values, names, terminals
and the subcircuit interface before simulation. Boundary tests exercise accepted
and rejected inputs, including exact size limits. The 17 model candidates are
the historical audited set; with the reference circuits, they satisfy the
declared input rules.

SUPPLY compares measurements at its stated reporting precision. The audit also
checks the extractor's rounding and interpolation behavior, so a boundary verdict
uses the convention given in the task.

## Electrical checks

| Task | Measurements |
|---|---|
| SUPPLY | Gain, bandwidth, phase/gain margin, DC power, saturation count, input-source current and sustained command tracking at three supplies |
| LOAD | Load-node accuracy, sustained settling, overshoot, loop stability and DC power at six load pairs |
| TIA | Signed conversion, bandwidth, loop stability, power, initial accuracy and four complete transitions at six capacitance pairs |

Every required check must pass at every operating point. The grader accepts
different compliant circuits. Complete measurements outside a limit fail
electrically; invalid inputs and incomplete simulation evidence have separate
outcomes. [Grading rules](../graders/README.md)

The audit exercises 402 electrical verdict boundaries. Passing references,
alternative circuits, deliberately wrong answers and damaged evidence are covered
by the [test suite](../tests/README.md). The
[current task-contract audit](../evidence/task_contract_audit_clarified2_v5.json)
records these checks for the current clarified-2 packets and v5 evaluator,
with zero model and simulator calls.

Native qualification is recorded separately. The
[earlier v4 receipt](../evidence/final_validation.json) reproduces the passing
references and two SUPPLY failures for its source snapshot, and the
[current v5 receipt](../evidence/qualified_v5_summary.json) records the same
five controls under the current evaluator in a clean bootstrapped environment.

## Run the audit

From the repository root, use the Python environment printed by setup:

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B tools/audit_tasks.py
```

This checks packet integrity, numerical declarations, input boundaries, reporting
precision and verdicts without model inference or full-circuit simulation.
[Current audit record](../evidence/task_contract_audit_clarified2_v5.json).
The stored [historical audit record](../evidence/task_contract_audit.json) covers
the earlier clarified-1 packets and remains unchanged.

## Recorded results

The seven historical sessions used the recorded packets. The frozen CLI cohort
used the clarified-1 revision. The current clarified-2 packets make existing
input rules and measurement conventions explicit; their electrical requirements
are unchanged. Existing model results retain their original packet and grader
identity, and no model trial on clarified-2 is reported. Historical packets
remain available with `tools/export_task.py --revision recorded`; current export
is the default.
