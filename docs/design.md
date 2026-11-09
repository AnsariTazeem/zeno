<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:0493d99ae1197763ef8b7ba52fd44b7dbbae992421914e64db92221e4527e2cb -->

# Design

| Requirement | Implementation |
|---|---|
| Preserve all electrical requirements during a repair | Every required metric must pass at every operating point |
| Accept different valid circuits | Grade measured behavior rather than netlist similarity |
| Keep answers out of model inputs | Export one task packet; run the verifier separately |
| Make results auditable | Retain candidates, simulation traces and machine-readable measurements |
| Separate a bad circuit from a failed run | Record electrical failure, invalid input and infrastructure errors separately |

[Core tests](../reproduction/payload/eval_core_v6/test_core.py) cover positive,
negative and equivalent solutions. [Evidence tests](../reproduction/payload/eval_core_v6/test_supply_evidence.py)
cover timeouts, identity changes, damaged traces and undefined-crossing
classification. [Export tests](../tests/test_repository_layout.py)
check the actual model-visible files.

Simulation and grading run locally. A model account is needed only to collect
new model responses. [Setup and commands](run.md)


<!-- /coderabbit-ai-generated:v1 -->