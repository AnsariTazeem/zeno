<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:9a69d4d63f832f0f5a97a7fafd6984d20fd18ab16daee0430a8c5fb4a028e3ba -->

# Grading

- [Runner](../reproduction/payload/eval_core_v6/run_eval.py): compilation, execution, replay and reporting.
- [SUPPLY adapter](../reproduction/payload/eval_core_v6/supply_adapter.py): native identity, sweep and trace checks.
- [TIA adapter](../reproduction/payload/eval_core_v6/tia_adapter.py): sensor transfer, timing and stability checks.
- LOAD grading uses the runner's `assess_load` function.

Every requirement must pass at every task condition. Valid scores are 100/0.
Invalid input or execution evidence has no electrical score. Different valid
circuits can pass without matching the reference netlist.

A complete no-gain sweep can have undefined unity-gain frequency and phase margin.
The SUPPLY adapter checks the raw evidence and scores that circuit as a failure.
A complete sweep with a downward unity crossing and no downward relative
-180-degree crossing passes the gain-margin check: it has no finite crossover
within the sweep. Missing or corrupt evidence remains unscored. Feedback includes
the reason for an accepted undefined gain margin.

The current v6 runner preserves these v5 electrical rules. It uses the current
packet by default for export, records the proposal/profile identities, rejects
optimized Python execution and removes successful temporary verifier workspaces
after copying their evidence. Failed workspaces remain available for diagnosis.

Qualification requires matching classifications and reported values within
relative tolerance `1e-6` and absolute tolerance `1e-9` in each metric's units.
Lists are compared element by element; nulls must match. These tolerances apply
to reproduction checks and do not change the electrical pass thresholds.

<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:feaa5bf164421b534572d097ad038537731a7ca465e46d2f21f8bd9c5d82856b -->

Versions v1–v5 remain frozen. The [v5 receipt](../evidence/qualified_v5_summary.json)
describes its original source. A separate [Windows run](https://github.com/AnsariTazeem/zeno/actions/runs/42560927106)
qualified v6 on commit `e921a6c`.

<!-- /coderabbit-ai-generated:v1 -->
[Commands](../docs/run.md) · [Tests](../tests/README.md)


<!-- /coderabbit-ai-generated:v1 -->