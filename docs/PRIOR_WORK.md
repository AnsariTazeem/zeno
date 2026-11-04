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

The source includes the circuit/testbench foundation and PyYAML with their MIT
notices. Setup downloads the simulator, process models, NumPy and zstandard
separately. Native decks, logs and numerical traces are simulation outputs.

Ngspice's `COPYING` includes LGPL, MPL and GPL component notices alongside BSD.
The external runtime retains those notices. See the
[ngspice licensing notes](https://ngspice.sourceforge.io/devel.html) and
[SKY130 license](https://github.com/google/skywater-pdk-libs-sky130_fd_pr/blob/main/LICENSE).

[Engineering background and threshold sources](problem.md)
