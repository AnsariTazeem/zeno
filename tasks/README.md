# Public tasks

| Task | Instructions | Conditions |
|---|---|---|
| SUPPLY | [Repair the amplifier](revisions/clarified-1/supply/TASK.md) | Three supply voltages |
| LOAD | [Compensate the load](revisions/clarified-1/load/TASK.md) | Six load/parasitic pairs |
| TIA | [Design sensor feedback](revisions/clarified-1/tia/TASK.md) | Six sensor/wiring pairs |

The current packets state the compiler limits and
measurement conventions explicitly. They preserve the electrical requirements.
The original folders retain the exact packets used for the [recorded results](../docs/results.md).
`contract.json` contains the scoring limits; `PROMPT.txt` is the model-facing
request. [catalog.json](catalog.json) records source paths and hashes.

Export one task with `python -I -B tools/export_task.py --task supply --out NEW_FOLDER`
from the repo root. Do not give a model the entire repository or mix task
contexts: it contains references, and LOAD/TIA's plant exposes SUPPLY's repair.

Default export uses the current packet. Add `--revision recorded` to reproduce the
historical input files. [Task audit](../docs/task-validation.md)
