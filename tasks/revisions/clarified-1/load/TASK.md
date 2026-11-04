# LOAD-P01: compensate a capacitive-load buffer without losing accuracy

You are reviewing a precision voltage-buffer connection to a new acquisition input. The amplifier, supply, source and input load are fixed. You may replace only the passive network connected to the amplifier output, its inverting input and the load. Deliver one network meeting every requirement below.

This is an authored simulation task grounded in a documented analog-design workflow. The fixed transistor amplifier is attributed public prior work. The load values and requirements below define this case; they are not field measurements or a claim about a particular commercial IC.

## Interface and fixed conditions

- Supply: 1.2 V; TT process; 27 C; reference current: 20 uA injected from vdd into the amplifier's `iref` terminal.
- The supplied `.subckt dut iref inp inn out` is the fixed amplifier. Its non-inverting input `inp` receives the command. Its output is node `drive`. Your feedback port `fb` connects to its inverting input `inn`.
- Supply exactly one `.subckt feedback drive load fb` ending in `.ends feedback`. Node `load` is the acquisition input where accuracy, overshoot and settling are measured. Node `0` is ground. Other permitted node names are private internal network nodes.
- A fixed 100000-ohm resistance connects `load` to ground. Its declared value is known and unchanged across conditions. A fixed capacitance connects `load` to ground. A separate stray capacitance connects `fb` to ground.
- Test all six Cartesian combinations: load capacitance **50, 150, 300 pF** and feedback-node stray capacitance **0.2, 2 pF**. One fixed candidate must pass all six. No hidden load-resistance variation or component tolerance is included.
- The external command is 0.8 V initially, then rises to 1.0 V at 5 us, falls to 0.8 V at 10 us, rises at 15 us and falls at 20 us. Every transition takes 20 ns. Each edge has a 5 us observation window; the trace ends at 25 us. The exact SPICE source is `PULSE(0.8 1.0 5u 20n 20n 4.98u 10u)`.

The electrical connections, excluding the zero-DC test probes used for loop measurement, are:

```spice
XDUT niref command fb drive dut
XNET drive load fb feedback
Rload load 0 100000
Cload load 0 <the tested load capacitance in farads>
Cstray fb 0 <the tested stray capacitance in farads>
```

## Allowed changes and input format

Use only resistors and capacitors in your `feedback` subcircuit. At most eight resistors, eight capacitors and sixteen private internal nodes are permitted. Each component line has exactly four tokens: instance name, first node, second node and literal value.

- Resistors: 1..10000000 ohms, inclusive. Capacitors: 1e-15..1e-7 farads, inclusive.
- Use numeric SI values such as `1000` and `2.2e-11`; suffixes such as `1k` or `22p` and expressions are not accepted by the component compiler.
- Instance names start with R or C. Node/instance names use letters, digits and underscores and start with a letter; `0` is the ground exception. Names are case-insensitive. The interface ports `drive`, `load` and `fb` must all appear.
- Blank lines and full-line `*` comments are allowed. The compiler gives internal nodes a private prefix to prevent collision with supply, source or probe nodes.
- No other device types, sources, models, directives, additional subcircuits, file operations, expressions or changes to the fixed amplifier are allowed. The network cannot connect directly to the command source, supply or reference-current node.
- The minimum permitted resistor can represent an interconnect in this simulation task. No particular topology, resistor count or reference wording is required; alternative compliant networks are welcome.

## Input size and syntax

The complete subcircuit may contain at most **32,768 UTF-8 bytes**, including comments and whitespace. Instance names must be unique, ignoring case. The input compiler adds no separate name-length limit. A component whose two nodes are identical is accepted by this compiler; it still consumes one of the permitted components. Such a component does not establish electrical compliance.

## Requirements at each operating point

1. **Load-node command tracking:** after each of the four edge start times, reach the commanded target within **+/-0.0005 V** no later than **2.5 us**, and remain in that band for the remainder of that edge's 5 us window. A stable output at an incorrect final voltage fails. The settling time is the first retained sample after the last out-of-band sample, measured from the start of the source transition.
2. **Load-node overshoot:** rising overshoot above 1.0 V and falling undershoot below 0.8 V must each be **<=0.010 V**, measured over every corresponding edge window. The target is the commanded voltage, not the candidate's own endpoint.
3. **Loop criterion:** at the 0.9 V DC command, the loop must have a valid non-inverting low-frequency phase (between -90 and +90 degrees at 10 Hz), at least one downward 0 dB crossing, and a phase margin of **>=50 degrees at every downward crossing** in the 10 Hz..10 GHz sweep. Phase margin is `180 + phase_at_crossing - phase_at_10Hz`, using continuous phase. Missing/undefined loop criteria do not pass.
4. **DC power:** total supply power, including the reference-current branch, must be positive and **<=350 uW** at the 0.9 V DC command. This is a DC power criterion, not a transient-energy or noise specification.

The loop test uses voltage/current double injection in the common connection between the feedback network and amplifier inverting input, so both local and load-node feedback paths are included. Its return ratio is `T=(Tv*Ti-1)/(Tv+Ti+2)`, with `Tv=-V(driver)/V(receiver)` under voltage injection and `Ti=I(driver)/I(receiver)` under current injection. The baseline AC grid has 50 points/decade; the transient retained maximum step is 1 ns. Numerical confirmation uses 100 points/decade, a 0.5 ns maximum step and tighter solver tolerances. Physical inputs, limits and the candidate remain unchanged.

All traces must be finite, cover the full declared time/frequency ranges and contain strictly increasing coordinates. The measured command must match the declared waveform. Incomplete/nonfinite data and simulator failures are recorded separately from electrical noncompliance. Passing these six points does not imply continuous capacitance coverage, process/temperature breadth, noise/distortion, layout, transmission-line behavior, ADC sampling kickback or silicon validation.

## Response and feedback protocol

Provide a short engineering explanation and **one complete feedback subcircuit in a `spice` code block**. Distinguish estimates and static checks from actual electrical simulations. Do not invent measured performance.

You have at most **three complete circuit proposals**, including the first. The local evaluator returns your candidate's measured pointwise results and errors after each evaluated proposal. You may revise using that feedback; do not request the reference answer. Stop after a confirmed full pass or the third proposal. If requirements remain unresolved, state that honestly.

The case score is **100 only when every requirement passes at all six points; otherwise a completed electrical evaluation scores 0**. Input-format errors and simulator/measurement-invalid outcomes are labelled separately with no numerical electrical score. Diagnostic checks remain available; they are not averaged into a passing result.

Provenance: the frozen amplifier and device-model apparatus are adapted from [AnalogPortBench, commit 13c40b2dd9bae22b83e2fc4aba0adb05e99e4282](https://github.com/saeidrajabii/AnalogPortBench/tree/13c40b2dd9bae22b83e2fc4aba0adb05e99e4282). Its MIT notice accompanies this packet. The passive-network task, load grid, accuracy/settling protocol and evaluator are authored for this development case; established compensation physics is not claimed as a new invention. Do not retrieve project-local reference networks or published task solutions. Device/circuit-theory documentation is allowed.
