# Task validation

Each task states its input format, operating conditions, measurements and limits.
The audit checks these declarations against the compiler and grader.

## Input checks

The compiler checks input size, permitted devices and values, names, terminals
and the subcircuit interface before simulation. Boundary tests exercise accepted
and rejected inputs, including exact size limits. All 17 retained model
candidates and the reference circuits satisfy the declared input rules.

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
by the [test suite](../tests/README.md). Separate
[native validation](../evidence/final_validation.json) reproduces the references
and two SUPPLY failures with the actual simulator.

## Run the audit

From the repository root, use the Python environment printed by setup:

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B tools/audit_tasks.py
```

This checks packet integrity, numerical declarations, input boundaries, reporting
precision and verdicts without inference or full-circuit simulation.
[Audit record](../evidence/task_contract_audit.json)

## Recorded results

The current packets make existing input rules and measurement conventions
explicit. Their electrical requirements are unchanged. Historical packets remain
available with `tools/export_task.py --revision recorded`; current export is the
default. Existing model results retain their original packet and grader identity.
No new model trial on the current packets is reported yet.
