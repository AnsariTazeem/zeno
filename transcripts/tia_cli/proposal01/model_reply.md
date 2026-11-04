```spice
.subckt feedback sense out vref
Rf out sense 10000
Cf out sense 5.2e-12
Rd sense damp 680
Cd damp vref 1e-7
.ends feedback
```

Unmeasured first candidate. Rf sets the nominal −10 kΩ conversion. Cf provides feedback compensation; the series Rd–Cd branch adds frequency-dependent damping while remaining open at DC, preserving the nominal operating point and adding no steady reference load.

The compensation is an engineering estimate. Bandwidth, phase margin, absolute settling, overshoot, and power require simulator verification across all six conditions.