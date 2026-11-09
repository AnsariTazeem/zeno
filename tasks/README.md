<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:aa0892346a767d8f41dc5085882f82315fbd07d6d5e209bc6a98cc21290aa405 -->

# Public tasks

| Task | Instructions | Conditions |
|---|---|---|
| SUPPLY | [Repair the amplifier](revisions/clarified-2/supply/TASK.md) | Three supply voltages |
| LOAD | [Compensate the load](revisions/clarified-2/load/TASK.md) | Six load/parasitic pairs |
| TIA | [Design sensor feedback](revisions/clarified-2/tia/TASK.md) | Six sensor/wiring pairs |

The current packets (clarified-2) state the compiler limits and measurement
conventions explicitly. They preserve the electrical requirements of the
original packets. Original packets in `supply/`, `load/`, and `tia/` are
retained as exact historical inputs. Their status and review wording describe
collection time; use the linked current packets for new work. The frozen CLI cohort used clarified-1.
No model trial on clarified-2 is included in the published results.
`contract.json` contains the scoring limits; `PROMPT.txt` is the model-facing
request. [catalog.json](catalog.json) records source paths and hashes.

Export one task with `python -I -B tools/export_task.py --task supply --out NEW_FOLDER`
from the repo root. Do not give a model the entire repository or mix task
contexts: it contains references, and LOAD/TIA's plant exposes SUPPLY's repair.
Default export uses the current packet. Add `--revision recorded` to reproduce the
historical input files, or `--revision clarified-1` for the frozen cohort's packet.
[Task audit](../docs/task-validation.md)


<!-- /coderabbit-ai-generated:v1 -->