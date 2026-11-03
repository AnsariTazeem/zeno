# Analog evaluation reproduction kit — v4 grader

This version packages the evidence-aware supply grader. The original physical
tasks, device model, native simulator and acceptance limits are unchanged.
Complete no-gain traces are scored as noncompliance without inventing UGF/PM/GM.
Missing or invalid evidence and JSON-only nulls remain unscored.

Use independently installed Windows x64 Python 3.12:

```powershell
& 'C:/path/to/Python312/python.exe' -I bootstrap.py
```

Setup creates a new short temporary root and venv. Use the printed paths:

```powershell
& 'C:/printed/root/.venv/Scripts/python.exe' -I 'C:/printed/root/qualification.py'
```

It runs eight archive-boundary checks, 30 existing integration regressions and
12 supply-evidence checks, followed by five native controls: SUPPLY/LOAD/TIA
positive references, the retained final supply failure and the new no-gain
failure. That is 21 conditions across five controls, not model trials. Existing
source and example fixtures from the v3 namespace are intentionally retained;
the invoked evaluator and grading tests are eval_core_v4.

The exact public downloads and wheel hashes match the previous tested recipe:
41,668,459 bytes with an empty cache. A verified cache may be reused; all bytes
are checked again. No model calls, API keys, accounts, conda activation, 7-Zip
installation, archive install scripts or system configuration changes. Existing
Windows C/UCRT support is a prerequisite. Fresh OS/independent-machine testing
is not established by a successful venv check on the same host.

To grade a new circuit from the prepared root, use its venv Python:

```powershell
python -I eval_core_v4/run_eval.py evaluate --task supply --candidate your.sp --run-id new01
```

Exit 0 means valid execution, including an electrical failure; 2 is invalid
input and 3 is an infrastructure outcome. Use unique run IDs. Raw-native audit
is distinct from fresh simulation and JSON-only replay. Read eval_core_v4/README.md.

This trusted kit contains reference circuits and old responses. Never give the
whole kit or multiple task contexts to a subject model. Export one public
packet per fresh session; LOAD/TIA's plant exposes SUPPLY's repair if mixed.
No OS-confidentiality, silicon, independent expert or prize claim is made.

AnalogPortBench and vendored PyYAML notices are retained. PyYAML includes its
pinned Windows extension, so this is not an all-text archive. Models/simulator
payloads download externally with their notices. Mixed runtime licenses and
competition compatibility remain a separate rights-review matter; external
installation alone is not clearance. No TI/OpenCode/organizer assets are added.

The prior supply trial interrupted by v3 remains interrupted. Offline correction
does not invent its missing third response or a completed replication. New
model trials are collected and reported separately using the frozen v4 condition.
