```spice
.subckt feedback drive load fb
Riso drive load 1000
Rtop drive fb 1000
Rbottom fb 0 100000
.ends feedback
```

Riso isolates the capacitive load from the amplifier’s local feedback loop. At DC, the feedback divider and the Riso–load-resistance divider both have ratio 100000/101000, so ideally `V(load) = V(fb)`, preserving load-node accuracy despite Riso’s voltage drop.

The largest nominal load time constant is approximately 0.30 us. That estimate excludes amplifier slew and recovery; phase margin, settling, overshoot and power remain unverified pending evaluator measurements.