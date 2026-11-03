# TIA-P01-T02 development collection protocol

The user authorized starting the pilot. An automated specification/grader review
aligned the implementation's inclusive 1 ohm boundary to the existing task;
all 54 qualification verdicts remained unchanged. This is not human/domain-
expert approval. Participant technical review remains pending for submission.
Use public packet revision 3 and its complete qualification seal unchanged.

One fresh temporary Unpersonalized ChatGPT conversation, selected GPT-6 / High
as observed in the UI. The UI says memory, plugins and custom instructions are
ignored. Exact backend revision, temperature, seed and token usage are not
available; do not invent them. Use the existing subscription and no separately
billed inference API. Upload only the frozen public PROMPT.txt, followed by
own-candidate feedback files. Never upload private inputs, calibration results,
previous trial answers, researcher reports or project-directory access.

At most three complete circuit proposals; exactly one complete replacement
feedback subcircuit per response. Preserve the complete rendered final answer
and all code blocks before response controls, reload or any next request.
Code uses rendered trimEnd plus one LF, with leading whitespace retained.
Prose whitespace is collapsed and disclosed; browser/local SHA-256 matches
establish transport integrity. These are UI exports, not raw API responses.
If a response contains multiple alternatives, do not cherry-pick one. Missing,
ambiguous or malformed answers, browser failures, input violations and simulator
failures remain separately classified; do not repair a scored candidate.

The candidate goes through evaluate_frozen.py and the same R/C compiler and six-
condition evaluator used for the reference. Return only its own measurements
using the fixed serializer: per-point loop/transfer/power/DC/edge metrics and
predeclared sampled AC values, without reference hints or bespoke design advice.
Use one retained feedback message between proposals. No fourth proposal.

Confirm a baseline full pass with the same circuit under tighter numerical
settings, then stop inference. If refinement reveals noncompliance, retain both
and return its own refined feedback within the remaining proposal allowance.
If all three fail, numerically corroborate the last valid circuit where useful.
Numerical reruns are not new model attempts. A pass retires this case as gap
evidence under this protocol; a failure supports only this bounded interaction.

The generic simulator result model_trial=false means its script makes no model
call. The independent session/capture records establish model origin for this
trial's inputs. One conversation, three possible adaptive proposals, six
correlated conditions and four edges must not become inflated model sample
counts. Keep prior SUPPLY and LOAD results separate.
