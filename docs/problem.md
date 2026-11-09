# The engineering problem

An analog engineer often has to reuse a circuit after its supply, load or sensor
changes. The deliverable is a circuit that still meets its accuracy, speed,
stability and power requirements together. A plausible compensation rule is only
a starting point; the revised circuit must be checked at the specified conditions.

## Three changes, three coupled constraints

| Task | Engineering situation | What can go wrong | Required deliverable |
|---|---|---|---|
| SUPPLY | Move a working amplifier to a lower supply | Reduced headroom changes operating points; resizing or compensation can recover one metric while losing another | One transistor circuit meeting all limits at three supplies |
| LOAD | Connect a buffer to a larger capacitive input | Output loading adds phase lag; isolation can reduce ringing but introduce voltage drop | One passive network meeting load-node accuracy, settling, stability and power limits at six load pairs |
| TIA | Connect a current sensor with different capacitance | Input capacitance changes feedback behavior; extra compensation can reduce useful bandwidth | One passive network meeting signed conversion, bandwidth, stability and transient limits at six capacitance pairs |

These are documented design concerns. Analog Devices describes the
[headroom limits of single-supply amplifiers](https://www.analog.com/en/resources/analog-dialogue/raqs/raq-issue-62.html).
Its [capacitive-loading tutorial](https://www.analog.com/en/resources/analog-dialogue/articles/techniques-to-avoid-instability-capacitive-loading.html)
explains the interaction between load, feedback and amplifier output impedance,
including the accuracy cost of out-of-loop isolation. Its
[TIA application note](https://www.analog.com/en/resources/technical-articles/stabilize-transimpedance-amplifier-circuit-design.html)
explains how sensor capacitance affects stability and why excessive feedback
capacitance reduces bandwidth.

An unsettled or offset output gives an acquisition input the wrong voltage at
the required observation time. Ringing can violate the allowed output excursion.
Those are the consequences measured here. Zeno does not estimate field failure
rates, financial losses or a commercial product's performance.

## Where the numbers come from

SUPPLY inherits its base budgets from AnalogPortBench's
[source specification](../reproduction/payload/analog_public_v1/upstream/benchmark/circuits/opamp_2stg/spec.yaml).
That specification derives gain, bandwidth, power and settling limits from a
180 nm source design. Zeno applies the disclosed budgets to the supplied
SKY130 apparatus and adds three lower-supply points, command-relative tracking
and input-current checks. The passing reference establishes feasibility in
that apparatus; the budgets are not measurements from a customer requirement.

| SUPPLY budget | Upstream derivation |
|---|---|
| Gain >=72.71 dB | Source 75.71 dB minus 3 dB |
| Unity-gain frequency >=66.59 MHz | 80% of source 83.23 MHz, as recorded upstream |
| Power <=296.4 uW | 120% of source 247 uW |
| Rising/falling settling <=12.24/26.73 ns | 150% of source 8.16/17.82 ns |
| Phase/gain margins >=55 degrees/10 dB | Fixed upstream limits |
| At most two devices out of saturation | Source count |

LOAD and TIA use authored simulation budgets, stated in their
[LOAD](../tasks/revisions/clarified-2/load/TASK.md) and
[TIA](../tasks/revisions/clarified-2/tia/TASK.md) packets. LOAD allows 0.5 mV
tracking error on a 200 mV step, or 0.25%; TIA allows 1 mV, or 0.5%.
SUPPLY allows 2 mV, or 1%. These are task-specific accuracy bands, not ADC
resolution specifications. The finite grids test simultaneous constraints;
they do not establish continuous coverage or full process/temperature margins.

## What the model record supports

The observed SUPPLY difficulty is closing several electrical requirements
within a three-proposal feedback budget. One final circuit came close but
missed rising settling. LOAD and TIA were solved and remain positive controls.
[Results and transcripts](results.md)

The cases were developed iteratively and the retained sessions are selected
development evidence. They do not establish how often all frontier models fail.
Further collection needs a frozen protocol and matched repetitions; making
solved cases harder merely to obtain failures would not establish relevance.
