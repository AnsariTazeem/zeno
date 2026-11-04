# Collect model responses

Collection is separate from simulation. Use the same model, effort, interface,
task inputs and feedback policy throughout a campaign. Model login and response
capture happen in the chosen interface; this tool does not call an API or handle
credentials.

## Prepare

```powershell
python -I -B tools/collect_trials.py prepare --name comparison --model gpt-6.1-sol --effort high --interface CLI
```

This prepares three fresh-context trials per task, interleaved across tasks,
with at most three proposals per trial. Inputs and evaluator sources are pinned
before any answer is recorded. The campaign stays in the ignored `.local-trials/`
folder. Each trial has a task-only `inputs/trialNN/request.txt`; give the model
that request, not the campaign directory or repository.

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
