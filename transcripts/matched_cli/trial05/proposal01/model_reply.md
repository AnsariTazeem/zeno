```spice
.subckt feedback sense out vref
Rf out sense 10000
Cf out sense 1e-11
.ends feedback
```

Proposal 1: The 10 kΩ resistor sets the nominal −10 kΩ transimpedance. The 10 pF capacitor provides feedback compensation, with an isolated feedback pole near 1.59 MHz. Actual bandwidth, stability, power, and settling across all six conditions remain to be evaluated.