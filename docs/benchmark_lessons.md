# Lessons from the reference benchmarks

We inspected pinned source revisions. We did not run these benchmarks or
install their harnesses. Zeno implements the useful mechanisms in its Python
runner; the full reference repositories are not runtime dependencies.

| Source and lesson | Zeno implementation | Check |
|---|---|---|
| [SWE-bench: fix the issue and preserve working behavior](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/grading.py) | All constraints must pass together; fixing timing cannot excuse broken gain, power or stability | `test_initial_accuracy_power_and_edge_regressions`, `test_reference_alternative_and_negative` in [core tests](../reproduction/payload/eval_core_v4/test_core.py) |
| SWE-bench: missing execution evidence is not success | Separate invalid-input, electrical-failure and infrastructure outcomes; native identity/coverage checks | Timeout, truncated trace and changed-candidate tests in [supply evidence tests](../reproduction/payload/eval_core_v4/test_supply_evidence.py) |
| [tau2-bench: accept a valid outcome without demanding one path](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/evaluator/evaluator.py) | Grade behavior, not similarity to the reference; accept permitted alternatives and equivalent data ordering | `test_reference_alternative_and_negative`, `test_row_and_edge_order_equivalent`, `test_model_network_and_equivalent_case_compile` |
| [tau2-bench: consistency differs from any-success](https://github.com/sierra-research/tau2-bench/blob/da0835f6c67baef58bdda18f2a3b037dfb3a1754/src/tau2/metrics/agent_metrics.py) | Session, proposal, condition and refined-run counts stay separate; incomplete sessions remain separate | [Result catalog](../results/catalog.json); no pass@k/pass^k estimate from this small mixed sample |
| [Terminal-Bench: separate instructions, environment, solution and verifier](https://github.com/harbor-framework/terminal-bench/tree/4031b48384a5946ba2c5b3c5fa59246ce8d47d92/tasks/batched-eval-parity) | Public packets, withheld references, pinned setup and candidate-only evaluation | [Export tool](../tools/export_task.py), [layout tests](../tests/test_repository_layout.py) and fresh verifier workspaces |
| Terminal-Bench: protect grading and retain artifacts | Reject file/simulator directives; verify candidate/deck/process identity; retain raw outputs | `test_source_directive_rejected`, `test_candidate_identity_cannot_change` |

The verifier uses a fresh directory, not a hardened separate container. No
general sandbox-security claim is made. The new exporter checks actual files,
improving on the earlier filename-list test.

These mechanisms support grader design. Model-gap evidence comes from the
recorded trials, not from the reputation of the reference frameworks.

Further reading from the guide:

- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
- [Lance Martin: Automating eval design and hillclimbing](https://claude.dev/blog/automating-eval-design-and-hillclimbing/).
- [OpenAI: GDPval](https://openai.com/index/gdpval/), used for task realism/review methodology, not a model ranking.
