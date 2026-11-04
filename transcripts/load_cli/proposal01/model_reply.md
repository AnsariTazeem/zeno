```spice
.subckt feedback drive load fb
Riso drive load 1000
Rtop drive fb 1000
Rbottom fb 0 100000
.ends feedback
```

The 1000 Ω series resistor isolates the amplifier from the capacitive load. At DC, the feedback divider and the known load resistance give identical ratios: `fb = load = drive × 100000/101000`. This compensates the isolation resistor’s voltage drop, subject to amplifier gain and offset.

Estimated worst-case load time constant is 297 ns, giving approximately 1.8 µs settling for an ideal drive step to the specified error band. Actual settling, overshoot, phase margin and power remain unmeasured and require simulator feedback.