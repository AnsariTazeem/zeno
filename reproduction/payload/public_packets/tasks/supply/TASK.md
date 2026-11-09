# SUPPLY-P01 development-2: repair an amplifier for three supply conditions

This is a simulation-only engineering development task adapted from a public analog reference. A hypothetical supply-reduction requirement is being tested; this is not a claim about a particular customer or measured silicon. Use the supplied circuit and constraints. Do not retrieve published solutions or other project files; device-physics documentation is allowed. A local simulator will evaluate your proposals and return feedback.

The supplied `starter.sp` uses SKY130 1.8 V LVT transistors and was checked at 1.8 V, TT/27 C, VCM=0.9 V, CL=1 pF and Iref=20 uA: gain 80.74 dB, UGF 78.82 MHz, phase margin 68.4 degrees, gain margin 12.3 dB and power 267.72 uW. Its command-relative rising/falling settling was 8.272/8.812 ns. Its performance at the new supplies is not stated here.

Deliver one fixed transistor-level replacement that passes **each discrete supply point 1.15, 1.20 and 1.25 V**, with every other test condition unchanged. Meeting only nominal supply is insufficient. You may change topology, biasing, transistor sizes and passive values. You may not change the testbench, models, sources, reference current, input waveform, common mode, load or metric definitions. Passing these three points is not a continuous-supply or all-PVT guarantee.

## Physical and test conditions

- `.subckt dut iref inp inn out`: iref is a 20 uA current injected from vdd; inp/inn are non-inverting/inverting inputs; out is the output; global vdd is the supply and 0 is ground.
- MOS instance order is **drain gate source bulk**. Use only `sky130_fd_pr__nfet_01v8_lvt` or `sky130_fd_pr__pfet_01v8_lvt`. W/L are literal numbers in micrometres. For both models W=1..1000; NMOS L=0.15..10 and PMOS L=0.35..10, inclusive; nf=1 and integer m=1..100. These model-specific length limits are required by the pinned simulation model bins. Unsupported geometry is rejected by preflight before electrical simulation. NMOS bulk must be 0; PMOS bulk must be vdd or its own source. These are simulation-task bounds, not a foundry layout/DRC signoff.
- Only MOS instances, positive resistors (1 ohm..10 Mohm) and capacitors (1 fF..100 pF) are allowed internally. At most 80 MOS instances, 32 resistors and 32 capacitors. No ideal/dependent sources, switches, behavioral models, extra model/subcircuit definitions, simulator directives, expressions or file operations. Node/instance names use letters/digits/underscores, starting with a letter, plus node `0`. Exactly one `.subckt dut iref inp inn out` ending with `.ends dut`.
- TT process at 27 C; Iref=20 uA, CL=1 pF, VCM=0.9 V. Unity-gain follower: inp is driven; inn is connected to out. Command swings between 0.8 and 1.0 V. Rise/fall source times are 10 ps, initial rising edge at 5 ns, falling edge at 55 ns, period 100 ns; observation is 0..200 ns. Maximum retained transient step is 10 ps.
- Small-signal loop gain uses the supplied Middlebrook double-injection follower testbench, sweeping 10 Hz..10 GHz, 50 points/decade. Metrics are gain at 10 Hz (labelled DC gain), first downward 0 dB crossing for UGF, phase margin relative to low-frequency phase, and gain margin at the first downward relative -180-degree crossing. Invalid/missing crossings or simulation data do not pass. Numerical refinement may confirm borderline/surprising outcomes without changing physical conditions.

## Required at every supply point

| Metric | Requirement |
|---|---:|
| DC gain | >=72.71 dB |
| Unity-gain frequency | >=66.59 MHz |
| Phase margin | >=55 degrees |
| Gain margin | >=10 dB |
| DC supply power, including bias | <=296.4 uW |
| Rising settling | <=12.24 ns |
| Falling settling | <=26.73 ns |
| MOS devices out of saturation at DC | <=2 |
| Monitored DC input-source current | <=0.01 uA |

Settling is measured against the **commanded target**, in a +/-2 mV band (1% of the 0.2 V step), over rising [5,55) ns and falling [55,105) ns windows. It must remain inside the band through the rest of that edge window; an early crossing followed by an excursion is not settled. The reported time is the first retained sample after the last out-of-band sample. A deficient output that merely stops changing is not a passing follower. Device saturation uses the model's |Vds|-|Vdsat| operating-point check. A negative margin counts as one out-of-saturation device; it is not independently a failure unless the allowed count is exceeded.

## Submission and feedback

Give a short engineering diagnosis and **one complete replacement subcircuit** in a `spice` code block. State which performance claims are simulated versus estimates; do not fabricate numerical runs. The component-only subset is compiled before simulation. Equivalent circuit designs are welcome; no particular topology or reference text is required.

You have at most **three complete circuit proposals**, including the first. After each proposal, the local simulator returns pointwise metrics, command-tracking results and simulation/format errors. You may repair your candidate using that feedback. Stop after a verified full pass. If you cannot meet the requirements within that allowance, state what remains unresolved. A simulator/access failure is recorded separately from electrical noncompliance.

Provenance: the starter circuit, base testbenches and base metric thresholds are adapted from [AnalogPortBench](https://github.com/saeidrajabii/AnalogPortBench/tree/13c40b2dd9bae22b83e2fc4aba0adb05e99e4282), MIT license in `LICENSE_UPSTREAM.txt`. Our development extension adds the explicit three-supply requirement, command-relative tracking/data checks and bounded feedback protocol. This is an attributed adapted pilot, not a claim that the underlying circuit or prior benchmark is original.
