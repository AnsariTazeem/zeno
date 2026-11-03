# Prior work and authored contribution

| Material | Provenance | Treatment |
|---|---|---|
| Amplifier, original testbench/measurement/threshold infrastructure | [AnalogPortBench](https://github.com/saeidrajabii/AnalogPortBench/tree/13c40b2dd9bae22b83e2fc4aba0adb05e99e4282), commit 13c40b2dd9bae22b83e2fc4aba0adb05e99e4282 | Existing MIT work, notices retained; not claimed as a novel amplifier or benchmark foundation |
| SKY130 simulation models | [ciel release](https://github.com/fossi-foundation/ciel-releases/releases/tag/sky130-f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7), open_pdks build f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7 | Existing model technology; payload downloaded by hash; retained model notice |
| Native simulator | ngspice 41 conda-forge Windows build h295a5eb_0 | Separately downloaded, hash-verified; mixed component notices; competition compatibility not cleared |
| PyYAML | 6.0.2 pinned vendored package, including Windows extension | Existing MIT dependency; notice and original bytes retained |
| NumPy / zstandard | 2.3.5 / 0.25.0 | Exact external wheel hashes; no new numerical method claimed |
| Authored extensions | Explicit supply grid, load and sensor workflow envelopes, component compilers, command-target/data checks, collection/feedback orchestration, native/replay interfaces, source locks, setup, validation and analysis | AI-assisted event work; participant review unfinished |

## Why the workflows are plausible

Analog Devices' [capacitive-load article](https://www.analog.com/en/resources/analog-dialogue/articles/techniques-to-avoid-instability-capacitive-loading.html)
describes how capacitive loads affect amplifier stability and compensation
choices. Its [transimpedance article](https://www.analog.com/en/resources/technical-articles/stabilize-transimpedance-amplifier-circuit-design.html)
discusses sensor/input capacitance, compensation, bandwidth and ringing.
These support workflow mechanisms; they do not validate our numeric envelope,
customer prevalence, a particular SKY130 circuit or a universal AI limitation.
No article figures, vendor model archives or full articles are redistributed.

## What is outside this selected evidence

The earlier passive-pullup pilot, additional supply screens, abandoned ADC/LDO
investigations, interrupted browser sessions and numerical noise controls are
outside this three-task selected catalog. The full development history remains
in the local project. The selected table is not a claim that no other experiment
was performed. No OpenCode artifacts are incorporated.

This draft was assembled after the selected model runs. Historical task bytes,
including old status wording, remain unchanged. Dated findings and the catalog
give the current outcome; the packager did not retrospectively edit a prompt
or forbid an observed successful topology.
