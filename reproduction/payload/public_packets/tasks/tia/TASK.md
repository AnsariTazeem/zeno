# TIA-P01: passive feedback for a pulsed-current sensor front end

Numerically qualified development task; participant review is pending. No model
trial has been released. Read this task together
with `contract.json` and the fixed `fixed_amplifier.sp`; neither contains the
private reference networks or calibration answers.

## Goal and physical boundary

Design one passive feedback network for the fixed transistor amplifier. A
synthetic optical sensor supplies 0..20 uA into `sense`; the intended conversion
is `Vout = 0.9 V - 10000 ohm * Iphoto`. The amplifier's non-inverting input is
connected to the ideal 0.9 V reference. Its inverting input senses `sense` through
an ideal measurement probe. Its output is `out`. The supply is 1.2 V, bias
reference current is 20 uA, model corner TT and temperature 27 C.

The fixed fixture includes sensor capacitance from sense to ground of 10,70 or
150 pF, wiring capacitance of 2 or 10 pF, 1 GOhm sensor shunt from sense to vref,
and 2 pF output load to ground. Every combination of the two capacitance lists
must pass with the same network: six operating conditions, one task.
Intrinsic device capacitances remain in the model and are not duplicated by
the external capacitance values. Any R/C component added inside your network
is allowed if it meets the stated component and electrical limits.

The sensor is an ideal current/capacitance approximation. Noise, photodiode
nonlinearity, optical dynamics, dark current, APD bias, layout and physical
reference-buffer performance are outside this task. This is not a complete
optical-receiver certification or a commercial-part guarantee.

## Required network format

Return one complete replacement, with no simulator directives:

```spice
.subckt feedback sense out vref
* R/C components only, using literal SI numeric values
.ends feedback
```

Up to eight resistors and eight capacitors; at most sixteen private internal
nodes. Resistance is 1..1e7 ohm; capacitance 1e-15..1e-7 F. Use decimal/scientific
SI values, such as `1234` and `2.5e-10` (format examples only), with no suffixes, expressions or
parameters. Ground is `0`. Only sense,out,vref,0 and your own internal nodes may
appear. Internal nodes are renamed by the compiler and cannot access supply,
bias or amplifier-internal nodes. Both sense and out must be used; vref is
optional. Component names must be unique. No voltage/current sources, switches,
models, includes, control blocks, nested subcircuits or file operations.

## All required electrical checks

- At 10 Hz, used as the declared low-frequency transimpedance measurement,
  the real transfer `V(out)/Iphoto` must be -10100..-9900 ohm and the imaginary
  part's absolute value <=1 ohm. Current is positive into sense. This explicitly
  states the finite-frequency DC approximation, including its sign convention.
- The first downward -3 dB crossing relative to the 10 Hz transimpedance
  magnitude must be >=1 MHz. Frequency sweep is 10 Hz..10 GHz. A missing crossing
  or incomplete/nonfinite export is invalid measurement, not assumed success.
- The double-injection loop return ratio must have positive low-frequency gain
  (>0 dB at 10 Hz), absolute initial phase <90 degrees, at least one downward
  unity crossing, and phase margin >=55 degrees at every such crossing.
- At 10 uA DC input, positive delivered power from the supply and reference is
  `max(0,-1.2*I(VSUP)) + max(0,-0.9*I(VREF)) <=300 uW`. Absorbed reference power
  gives no credit. This is the disclosed quiescent apparatus measure; dynamic
  energy and a real reference generator's conversion losses are not measured.
- Initial output at 0 uA must be within +/-1 mV of 0.9 V.
- Photocurrent starts at 0 uA, rises at 1 us to 20 uA, falls at 2 us, rises at
  3 us, and falls at 4 us. Each transition is a 5 ns linear ramp; stop is 5 us.
  The target sequence is 0.7,0.9,0.7,0.9 V. After each ramp starts, output must
  enter and remain within +/-1 mV of that absolute target by 500 ns, until the
  next transition. An endpoint-relative band or a single correct final sample
  does not satisfy this criterion.
- Overshoot/undershoot beyond each edge's final target must be <=10 mV,
  inspected throughout the entire edge window, including during the source
  ramp. For a falling output edge inspect target minus minimum output; for a
  rising edge inspect maximum output minus target, floored at zero.

The full source waveform, coverage, retained maximum step, finite values and
all four edge windows are checked. Baseline numerics use 0.5 ns maximum step
and 100 AC points/decade; confirmation halves the step, doubles the AC density
and tightens tolerances as listed in `contract.json`. Measurements interpolate
crossings in log frequency. Refined confirmation preserves the physical circuit.

## Outcome and evidence

A score of 100 requires every check at all six conditions. A completed electrical
failure scores zero; malformed/unsafe input or missing/invalid simulation data
is unscored and reported separately. Equivalent passing networks are accepted;
no particular reference topology or component count below the stated maximum
is required. The test does not measure whether a model can obtain a solution
from a public answer repository.

In a future model trial the allowance is at most three complete proposals,
with only the current proposal's measured condition feedback between attempts.
Stop on a confirmed full pass. Do not claim simulation results unless they were
actually returned by the apparatus. No model trial has yet been conducted for
this case, and participant review is pending for final submission; an authorized development pilot may proceed.

## Attribution

The fixed amplifier is compiled from AnalogPortBench's MIT-licensed
`benchmark/golden/opamp_2stg_1v2.sp` at commit
`13c40b2dd9bae22b83e2fc4aba0adb05e99e4282`. `MODEL_IDENTITY.json` and
`LICENSE_UPSTREAM.txt` accompany it. The current-to-voltage scenario, operating
grid and verification are authored. General TIA compensation methods and the
public plant are prior work; an original system scenario is not new circuit
physics or proof of a frontier-model limitation.
