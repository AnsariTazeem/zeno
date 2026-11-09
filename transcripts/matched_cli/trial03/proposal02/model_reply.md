```spice
.subckt feedback sense out vref
Rf out sense 10000
Cf out sense 9e-12
Cs sense vref 2.7e-11
.ends feedback
```

Proposal 2: Only the two lowest-capacitance conditions failed, both on phase margin. Adding 27 pF raises total external sense capacitance to 39–187 pF, targeting improved minimum phase margin while preserving DC behavior. Settling and overshoot at the increased maximum capacitance require evaluator confirmation.