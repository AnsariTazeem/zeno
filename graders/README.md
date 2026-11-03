# Grading

- [Runner](../reproduction/payload/eval_core_v4/run_eval.py): candidate compilation, task execution and result reporting.
- [SUPPLY adapter](../reproduction/payload/eval_core_v4/supply_adapter.py): native identity, sweep and trace checks.
- [TIA adapter](../reproduction/payload/eval_core_v4/tia_adapter.py): sensor transfer, timing and stability checks.
- LOAD grading is the runner's `assess_load` function.

Every requirement must pass at every task condition. Valid scores are 100/0.
Invalid input or execution/evidence has no electrical score. Valid alternative
circuits are accepted without matching the reference netlist.

A completed no-gain sweep can have undefined UGF/phase margin. The v4 SUPPLY
adapter checks the raw evidence and scores that circuit as a failure; missing
or corrupt evidence remains unscored.

[Commands](../docs/run.md) · [Tests](../tests/README.md)
