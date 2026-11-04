# Prior work

| Component | Source | Use |
|---|---|---|
| Amplifier and original testbench | [AnalogPortBench](https://github.com/saeidrajabii/AnalogPortBench/tree/13c40b2dd9bae22b83e2fc4aba0adb05e99e4282), MIT | Circuit and measurement foundation |
| SKY130 models | [ciel release](https://github.com/fossi-foundation/ciel-releases/releases/tag/sky130-f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7), Apache-2.0 notices | Pinned simulation models, downloaded during setup |
| ngspice 41 | conda-forge Windows build `h295a5eb_0`; BSD with component exceptions | External simulator, downloaded during setup |
| PyYAML 6.0.2 | MIT; notices retained in the runtime bundle | Vendored parser and Windows extension |
| NumPy 2.3.5 / zstandard 0.25.0 | Hash-pinned wheels; BSD licenses and bundled notices | Numerical processing and archive decompression, installed during setup |

Zeno adds the operating grids, component restrictions, grading adapters,
command-relative tracking checks, collection protocol, tests and setup tools.
The underlying amplifier, device models and compensation physics are prior work.
Dependencies retain their original license notices.

The ZIP includes the attributed circuit/testbench foundation and PyYAML with
their MIT notices. It includes download recipes for the simulator, process
models, NumPy and zstandard; their archives, installed runtimes and model
libraries are not shipped. Native decks, logs and numerical traces are run
outputs. TI vendor libraries and organizer teaching materials are excluded.

Ngspice's `COPYING` includes LGPL, MPL and GPL component notices alongside BSD.
The external runtime keeps those notices. It is not relabelled as wholly
permissive or covered by Zeno's authorship. See the
[ngspice licensing notes](https://ngspice.sourceforge.io/devel.html) and
[SKY130 license](https://github.com/google/skywater-pdk-libs-sky130_fd_pr/blob/main/LICENSE).

The task mechanisms are supported by Analog Devices' articles on
[capacitive-load stability](https://www.analog.com/en/resources/analog-dialogue/articles/techniques-to-avoid-instability-capacitive-loading.html)
and [transimpedance compensation](https://www.analog.com/en/resources/technical-articles/stabilize-transimpedance-amplifier-circuit-design.html).
The numerical envelopes are synthetic test cases.
