# Grading

- [Current runner](../reproduction/payload/eval_core_v4/run_eval.py): CLI, candidate compilation and task outcomes.
- [SUPPLY adapter](../reproduction/payload/eval_core_v4/supply_adapter.py): raw sweep, trace and native-identity checks.
- [TIA adapter](../reproduction/payload/eval_core_v4/tia_adapter.py): sensor transfer, timing and stability checks.
- LOAD grading is in the current runner's `assess_load` function.

Every stated check must pass at every task condition. Valid scores are 100/0.
Invalid candidates and invalid execution/evidence have no electrical score.
No LLM judge is used; valid alternatives need not match a reference netlist.

The v4 supply fix preserves null UGF/PM/GM when a verified complete no-gain
sweep makes them undefined. That circuit fails; missing/corrupt evidence stays
unscored. It is a narrow fix, not a solution for every possible crossing case.

Code remains at its tested paths to preserve file hashes and compatibility.
Use [run_eval.py](../run_eval.py) with the prepared environment. Candidate
execution uses fresh verifier directories; hardened container isolation has
not been established. [Tests](../tests/README.md) · [Commands](../docs/run.md)
