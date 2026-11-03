# Methodology

Each task defines the allowed circuit elements, operating points and limits.
Every check must pass at every point. Valid results score 100 or 0; invalid
input and invalid execution/evidence are separate unscored outcomes.
Equivalent valid circuits are accepted. No LLM judge is used.

Sessions allow at most three proposals, with feedback only about the submitted
candidate. References are withheld. The final valid proposal is checked with
finer numerics. CLI/UI sessions and grader versions are recorded separately.
Backend revisions, temperatures and seeds are unknown.

The v4 SUPPLY adapter handles a completed sweep whose gain stays below unity:
UGF and phase margin can be undefined. With native identity and trace checks
satisfied, this is an electrical failure. Missing or corrupt data stay unscored.

The two complete SUPPLY sessions, LOAD session and TIA session are included.
A separate v3 follow-up stopped after two replies on a wrapper defect and is
excluded from complete-trial counts. Conditions, proposals and refined runs
are correlated measurements, not independent trials.

Export one public packet per fresh model context. LOAD/TIA's fixed amplifier
can expose SUPPLY's repair if tasks are mixed. The verifier uses fresh working
directories; it is not a hardened OS sandbox. Public repository exposure must
be recorded for future collections.
