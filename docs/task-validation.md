# Task validation

The `clarified-1` packets make the existing input rules explicit. Electrical
limits, stimuli, operating grids, fixed amplifiers and grading code are unchanged.
This is a packet revision for future trials, not three additional tasks.

## Corrected discrepancies

| Task | Previously unstated rule | Clarification |
|---|---|---|
| SUPPLY | 30,000-character input limit; 32-character names; unique instance names; distinct passive terminals | Explicit size and syntax section |
| SUPPLY | MOS instances require `X` names; `nf` and `m` default to 1 | Explicit instance format and defaults |
| LOAD | 32,768-byte input limit; unique instance names | Explicit byte limit and uniqueness rule |
| TIA | 32,768-byte input limit; 32-character names; distinct passive terminals | Explicit size and syntax section |
| TIA | Old pre-trial status text remained embedded in the instructions | Removed from the new packet; retained in the recorded packet |
| TIA | Phase-margin convention was less explicit than LOAD's | Added the implemented return-ratio and phase-margin definitions |
| SUPPLY | Upstream rounding and linear-frequency interpolation affect boundary verdicts | Declared the existing reporting precision and tested it directly |

The same-node and long-name probes reproduce compiler rejections. They are
input-format examples, not claims that those circuits meet the electrical limits.
All 17 retained model candidates pass the input compiler. No historical model
verdict has been changed by this review.

## Measurement and verdict mapping

| Task | Required outcome | Measurement and acceptance |
|---|---|---|
| SUPPLY | Gain, bandwidth and stability at all three supplies | Gain at 10 Hz; first downward unity crossing; phase relative to low-frequency phase; gain margin at the defined phase crossing |
| SUPPLY | Power, saturation count and input current | Fixed-bias operating point; disclosed power/current limits and model saturation check |
| SUPPLY | Rising/falling command tracking | Absolute targets in the declared edge windows; last excursion determines sustained settling |
| LOAD | Accuracy, settling and overshoot at six load pairs | Four complete edge windows at the load node, relative to the commanded target |
| LOAD | Stability and DC power | Double-injection return ratio; every downward unity crossing; fixed 0.9 V bias point |
| TIA | Signed transfer and bandwidth at six capacitance pairs | Real/imaginary transfer at 10 Hz and first downward −3 dB crossing |
| TIA | Stability and power | Positive low-frequency loop gain, every downward unity crossing, delivered supply/reference power at 10 µA |
| TIA | Initial accuracy and four complete transitions | Absolute targets, sustained settling and peak overshoot over each full window |

Equivalent passing circuits are accepted. A finite result outside a required
limit fails electrically; incomplete/invalid measurements are unscored. A valid
candidate rejected by an input rule is a different issue from electrical failure.

## Reproduce the checks

Use the prepared Python environment from the repository root:

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I -B tools/audit_tasks.py
```

The audit checks 25 numerical declarations, 21 compiler cases, seven reporting
precision cases and 402 verdict
boundaries across all operating points. It also verifies that the new contracts
preserve the recorded electrical requirements and fixed assets. It makes no model
or simulator calls. [Receipt](../evidence/task_contract_audit.json)

Passing references remain the [qualified circuits](../reference/README.md).
The [native validation](../evidence/final_validation.json) reproduced those
references and two SUPPLY failures. The new syntax audit accepts the reference
files under the clarified input rules. Saved alternative and negative cases remain
covered by the grading regressions.

## Current and recorded packets

`tools/export_task.py` defaults to `clarified-1`. Use `--revision recorded` to
recreate the exact files supplied in the existing seven-session record. The
prepared frozen runner's own `export-task` command exports its historical packet;
use the repository export tool for the current packet.

No model trial on `clarified-1` has been collected yet. Current results continue
to identify the original packet and grader versions. The audit supports stated
contract consistency; it does not certify expert agreement, practical threshold
justification, simulator perfection or silicon behavior.
