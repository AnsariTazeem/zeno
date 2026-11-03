# Public tasks

| Task | Instructions | Conditions |
|---|---|---|
| SUPPLY | [Repair the amplifier](supply/TASK.md) | Three supply voltages |
| LOAD | [Compensate the load](load/TASK.md) | Six load/parasitic pairs |
| TIA | [Design sensor feedback](tia/TASK.md) | Six sensor/wiring pairs |

These are the versioned packets used in the recorded trials. Their original
text, including dated status notes, is retained for replay.
`contract.json` contains the scoring limits; `PROMPT.txt` is the model-facing
request. [catalog.json](catalog.json) records source paths and hashes.

Export one task with `python -I -B tools/export_task.py --task supply --out NEW_FOLDER`
from the repo root. Do not give a model the entire repository or mix task
contexts: it contains references, and LOAD/TIA's plant exposes SUPPLY's repair.
