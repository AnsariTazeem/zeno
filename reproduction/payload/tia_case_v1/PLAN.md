# TIA-P01 qualification plan, before reference exploration

2 November 2026. This investigates a new current-to-voltage sensor workflow,
not a modification or rescoring of LOAD-P01 or SUPPLY-P01. No model is tested
until a reference and the measurement apparatus have passed qualification.

## Application and authored assumptions

A hypothetical pulsed optical measurement channel translates 0..20 uA to
0.9..0.7 V with nominal -10 kOhm transimpedance. Each light/dark plateau lasts
1 us. Data must be usable 500 ns after a transition, with <=1 mV error retained
until the next transition. The minimum small-signal bandwidth is 1 MHz and
overshoot/undershoot beyond the commanded final level is <=10 mV.

The external sensor capacitance is 10,70,150 pF; wiring/input stray is 2 or
10 pF, giving six combinations. Intrinsic transistor capacitances remain in
the amplifier model and are not counted again as an explicit input capacitor.
The photodiode is a disclosed linear current-source/capacitance approximation
with 1 GOhm shunt resistance to the ideal 0.9 V reference. It is not a named
commercial detector, APD, real customer dataset or nonlinear optical model.
Output load is 2 pF. The public transistor amplifier is fixed at 1.2 V, TT,
27 C, Iref=20 uA. It is reused with attribution, not claimed as original IP.

All loop downward unity crossings need >=55 degrees margin. Low-frequency
transimpedance must be negative, with magnitude 10000 ohm +/-1%. The initial
0 uA output and both command levels must satisfy the same +/-1 mV accuracy
band. Quiescent delivered power at 10 uA input is <=300 uW, counting positive
power from the 1.2 V supply and the ideal 0.9 V reference, with no credit for
power absorbed by the reference. Feedback-network components may connect to
sense, out, vref, ground and their own private internal nodes. They may not
alter the sensor, fixed amplifier or stimulus. Up to eight R and eight C,
R=1..1e7 ohm, C=1e-15..1e-7 F; no sources, models, includes or directives.

The numeric envelope is authored and provisional pending feasibility and
participant review, not derived from a commercial datasheet guarantee. Do
not relax these limits to rescue a reference. If infeasible, record that
result and create a separately justified design revision, or stop the case.

## Cheap feasibility screen, then qualification

First screen the straightforward baseline: 10 kOhm feedback resistor with
parallel feedback capacitor 1,2.2,4.7,6.8,8.2,10,22,100 pF. Use the worst
declared total external input capacitance, 150+10 pF. Collect AC loop and
current-to-output transfer only. This tests a standard baseline before any
compound network. All values/results are retained; it is not an AI trial.

Select at most two AC-feasible baseline values, then verify through the actual
restricted network compiler under all six conditions, with full 5 us traces
and all four command edges. Confirm the stronger reference with half transient
step and denser AC/tighter tolerances. Include a deliberately undercompensated
and an overcompensated/bandwidth-limited completed negative control. If either
intended control passes, accept the outcome and replace its description, not
the task's success criteria. Do not assume the screen proves transient success.

Numerical profiles: baseline max transient step 0.5 ns, AC 100/decade;
refined max step 0.25 ns, AC 200/decade; both export 12-digit scientific data.
The source starts at 0 uA, rises to 20 uA at 1 us, falls at 2 us, rises at
3 us, falls at 4 us, with 5 ns linear ramps. Stop at 5 us. Settling is measured
from ramp start and must persist through the remainder of each 1 us window;
an endpoint-relative band cannot replace the specified command target.

## Apparatus and honesty gates

Verify public model/upstream/binary identities and retain full raw data,
decks, selected inputs, numerical settings, process completion and source
provenance. Distinguish completed electrical misses from missing/invalid data
and simulator failures. Validate current-source sign and waveform, all-edge
retention, bandwidth crossing and loop extraction. Compare the double-injection
probe and current-to-output transfer against independently derived analytical
two-pole TIA fixtures before calling the apparatus qualified.

This stage stops at a feasibility/qualification decision and reviewable packet.
It does not call another model, claim a frontier-model gap or manufacture a
failure by forbidding an alternative that meets the declared contract. Human
participant/expert review, clean-machine reproduction, task breadth, wider model
trials and final submission requirements remain separate open gates.
