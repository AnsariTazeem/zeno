# Grading

- [Runner](../reproduction/payload/eval_core_v5/run_eval.py): candidate compilation, task execution and result reporting.
- [SUPPLY adapter](../reproduction/payload/eval_core_v5/supply_adapter.py): native identity, sweep and trace checks.
- [TIA adapter](../reproduction/payload/eval_core_v5/tia_adapter.py): sensor transfer, timing and stability checks.
- LOAD grading is the runner's `assess_load` function.
- The frozen [v4 runner](../reproduction/payload/eval_core_v4/run_eval.py) and
  [SUPPLY adapter](../reproduction/payload/eval_core_v4/supply_adapter.py)
  are retained unchanged as the historical grader of the recorded cohort.

Every requirement must pass at every task condition. Valid scores are 100/0.
Invalid input or execution/evidence has no electrical score. Valid alternative
circuits are accepted without matching the reference netlist.

A completed no-gain sweep can have undefined UGF/phase margin. The current
SUPPLY adapter checks the raw evidence and scores that circuit as a failure.
A complete sweep with a valid downward unity-gain crossing but no downward
relative -180-degree crossing has no finite gain-margin crossover within the
sweep; that case passes the gain-margin check and is not an infrastructure
error. Missing or corrupt evidence remains unscored.

[Commands](../docs/run.md) · [Tests](../tests/README.md)
