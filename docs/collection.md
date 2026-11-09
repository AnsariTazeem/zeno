<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:71f0a48e3d8d21f72768a1fbd2bd8feffeef509ce79c2ec028e9bc03838d5d33 -->

# Collect model responses

Collection is separate from simulation. Use the same model, effort, interface,
task inputs and feedback policy throughout a campaign. Responses can be captured
externally or through the subscription CLI. Simulation needs no model account.

## Subscription CLI

On Windows, sign in to Codex using your ChatGPT account. Prepare the campaign
with the installed CLI and its access policy pinned:

```powershell
python -I -B tools/collect_trials.py prepare --name comparison --model gpt-6.1-sol --effort high --interface CLI --codex
python -I -B tools/collect_cli.py --name comparison --trial trial01 --prepared-root 'C:/printed/root'
```

The second command collects one episode. It starts a fresh context, evaluates
each candidate and returns feedback in that same context, stopping at a confirmed
pass or the proposal limit. Run the next scheduled trial with a new trial ID.

Collection uses MXC with restricted reads and no command-network access. Shell,
browser, connector and memory features are disabled. Captures are rejected if a
tool is requested or the effective model/access settings differ from the plan.
The collector makes no resends; connection handling inside the native CLI follows
the client's defaults. There is no separately billed API fallback.

Local canary tests checked input access, denied reads outside the permitted
workspace and denied writes. An arithmetic capture checked the effective profile
and absence of tool requests. [Check record](../evidence/transport_checks.json)

## External capture

To record responses from another controlled interface, prepare without `--codex`:

```powershell
python -I -B tools/collect_trials.py prepare --name comparison --model gpt-6.1-sol --effort high --interface CLI
```

This prepares three fresh-context trials per task, interleaved across tasks,
with at most three proposals per trial. Inputs and evaluator sources are pinned
before any answer is recorded. The campaign stays in the ignored `.local-trials/`
folder. Each trial has a task-only `inputs/trialNN/request.txt`; give the model
that request, not the campaign directory or repository.

New campaigns pin evaluator v6 in addition to their packet revision. Native
recovery verifies the candidate, task, proposal, numerical profile, runner, lock
and saved artifact identities. Older campaigns require their frozen collector.

## Run one trial

Start the ledger entry before sending the request:

```powershell
python -I -B tools/collect_trials.py start --name comparison --trial trial01
```

Use a fresh model context with tools disabled. Save its exact response as UTF-8,
then record and evaluate it using the prepared simulation environment:

```powershell
python -I -B tools/collect_trials.py record --name comparison --trial trial01 --response 'C:/captured/answer.txt' --prepared-root 'C:/printed/root'
```

The command prints the feedback file. If the outcome is `continue`, send only
that feedback in the same model context and record the next exact response.
Start a new context when moving to another trial. Do not mix task conversations.

Passing candidates receive a finer numerical confirmation. A final electrical
failure is also confirmed. Format errors and invalid circuits consume proposals;
they do not receive invented electrical scores. A completed trial succeeds only
with a confirmed passing circuit.

If capture fails before a response is available, retain the failed attempt:

```powershell
python -I -B tools/collect_trials.py interrupt --name comparison --trial trial01 --kind transport_error
```

Infrastructure errors and numerical disagreement stop collection. Do not
regenerate an answer, skip an interrupted trial or change requirements mid-run.
Inspect retained logs before deciding how to recover. Existing outputs are not
overwritten.

## Review the record

```powershell
python -I -B tools/collect_trials.py status --name comparison
```

The summary retains planned, started, incomplete and completed episodes. It
withholds estimates until all three episodes for a task complete. Here, `k`
counts fresh episodes, each with its three-proposal budget. It does not count
individual proposals or simulation reruns. The reported pass@k and pass^k values
use finite-sample combinations; population interpretations require independent,
identically distributed episodes.

Raw responses and host diagnostics remain private until reviewed for publication.
The task-only input folder does not itself enforce an OS sandbox; qualify tool
and file-access restrictions in the model interface used for collection.


<!-- /coderabbit-ai-generated:v1 -->