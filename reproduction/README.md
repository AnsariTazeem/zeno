# Runtime bundle

This directory contains the source, pinned setup recipe and regression
fixtures used by the evaluator. `source_manifest.json` identifies the prepared
source files; `kit_manifest.json` verifies the bundle before setup.

Use `python -I -B bootstrap.py` from the repository root. Setup creates a new
Windows Python 3.12 environment and verifies downloaded models, simulator and
wheels by hash. [Commands](../docs/run.md)

The `payload/eval_core_v4` runner uses earlier adapters for compatible tasks.
Historical task packets and numerical measurements are preserved. Local host
paths in published metadata are redacted; integrity records identify those copies.
The bundle contains references: export one public task before giving it to a
model. [Tasks](../tasks/README.md) · [Grading](../graders/README.md)

Third-party source and license notices remain in the bundle. Simulator/model
payloads are downloaded separately during setup.
