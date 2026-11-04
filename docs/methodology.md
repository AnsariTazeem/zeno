# Methodology

Each task defines the allowed circuit elements, operating points and limits.
Every check must pass at every point. Valid results score 100 or 0; invalid
input and invalid execution/evidence are separate unscored outcomes.
Equivalent valid circuits are accepted. No LLM judge is used.

Sessions allow at most three proposals, with feedback only about the submitted
candidate. References are withheld. The final valid proposal is checked with
finer numerics. CLI/UI sessions and grader versions are recorded separately.

The v4 SUPPLY adapter handles a completed sweep whose gain stays below unity:
UGF and phase margin can be undefined. With native identity and trace checks
satisfied, this is an electrical failure. Missing or corrupt data stay unscored.

## Collection conditions

The record includes three complete SUPPLY sessions, two LOAD sessions and two
TIA sessions: seven adaptive trials, 17 baseline proposals and 24 saved
evaluations. The catalog labels the requested model, interface and grader
version for each evaluation. Exact backend revisions, temperatures and seeds
were unavailable. Comparisons between these selected sessions are descriptive;
they do not establish a matched model ranking or a population failure rate.

The SUPPLY repeat recovered from a UTC/local-date trace lookup interruption
using the retained first answer and the same session. It was not regenerated.
A separate v3 follow-up stopped after two replies on a wrapper defect and is
excluded from complete-trial counts. Conditions, proposals and refined runs
are correlated measurements, not independent trials.

## Input boundaries

Export one public packet per fresh model context. LOAD/TIA's fixed amplifier
can expose SUPPLY's repair if tasks are mixed. The verifier uses fresh working
directories. These filesystem boundaries are not an OS sandbox. The fresh
LOAD/TIA CLI collections took place after the repository was public; their
collection receipts record that exposure. References were withheld from the
supplied packets, while prior exposure and absolute confidentiality remain
unverified.
