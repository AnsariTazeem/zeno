<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:4a8bcf55c7071f14274c04584478b345858cb2ddcd3a573f44cd2bf10bbce579 -->

# Runtime bundle

This directory contains the source, pinned setup recipe and regression fixtures.
`source_manifest.json` identifies prepared source files; `kit_manifest.json`
<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:0552d4a2bd210efc167ce4b59379d344e5c7e088d73673640cf276ce6d1bc323 -->

verifies the bundle before setup. `maintenance_manifest.json` links updated
setup manifests and this README to their earlier redaction receipt. Run
`python -I -B tools/refresh_manifests.py` from the repository root after an
intentional maintained-runtime change, then rerun the offline checks.

<!-- /coderabbit-ai-generated:v1 -->

Run `python -I -B bootstrap.py` from the repository root on Windows x64 Python 3.12.
Setup verifies downloaded models, simulator and wheels by hash. [Commands](../docs/run.md)

The current runner is `payload/eval_core_v6`. Versions v1–v5 remain frozen for
historical results. The self-contained `payload/public_packets/` folder provides
the same catalog and task exports as the repository, including explicit revisions.

Historical TIA notes are retained because frozen verification seals include their
hashes. Their old review and authorization language does not describe the current
project. Some research scripts need unpublished raw files; see
[historical prerequisites](../docs/history.md).

Third-party source and license notices remain in the bundle. Simulator/model
payloads are downloaded during setup. Export one task packet before giving it to
a model; the bundle contains reference solutions.


<!-- /coderabbit-ai-generated:v1 -->