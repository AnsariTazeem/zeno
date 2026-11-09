```spice
.subckt feedback drive load fb
Riso drive load 1000
Rtop drive fb 1000
Rbottom fb 0 100000
.ends feedback
```

Riso isolates the amplifier from the capacitive load. The feedback divider raises the ideal DC drive voltage by 1.01, compensating the load’s attenuation of 100000/101000.

At 300 pF, the estimated load time constant is 0.297 µs, giving approximately 1.78 µs settling to the specified band for an ideal, instantaneous amplifier response. Finite amplifier gain, loop phase margin, actual settling, overshoot and power remain unverified pending evaluator measurements.