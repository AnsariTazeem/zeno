# Design

| Decision | Implementation | Reference |
|---|---|---|
| A repair must preserve other requirements | All circuit metrics must pass together | [SWE-bench grading](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/grading.py) |
| Accept valid alternatives | Grade measured behavior, not netlist similarity | [tau2 evaluator](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/evaluator/evaluator.py) |
| Separate the task from its answers and verifier | Public packet export, withheld references and fresh verifier directories | [Terminal-Bench task layout](https://github.com/harbor-framework/terminal-bench/tree/4031b48384a5946ba2c5b3c5fa59246ce8d47d92/tasks/batched-eval-parity) |
| Preserve execution evidence | Candidate/deck hashes, native completion records and raw traces | [SUPPLY adapter](../reproduction/payload/eval_core_v4/supply_adapter.py) |
| Distinguish failure from missing evidence | Electrical failure, invalid candidate and infrastructure error are separate outcomes | [Grading](../graders/README.md) |

[Core tests](../reproduction/payload/eval_core_v4/test_core.py) cover positive,
negative and equivalent solutions. [Evidence tests](../reproduction/payload/eval_core_v4/test_supply_evidence.py)
cover timeouts, identity changes and damaged traces. [Export tests](../tests/test_repository_layout.py)
check the actual model-visible files.

These references informed the harness design. Their frameworks are not runtime
dependencies, and no benchmark results from them are reported here.
