<!-- coderabbit-ai-generated:v1 -->

# Historical files and prerequisites

I retain the original task packets, evaluators, transcripts and research notes so
that recorded results can be checked against the files used at collection time.
Their dates, draft labels, review status and instructions describe that historical
stage. They are not current project instructions.

## Task packets and evaluators

Use `tools/export_task.py` for a current packet. The original `tasks/supply/`,
`tasks/load/` and `tasks/tia/` folders are recorded inputs. In particular, the old
TIA packet's pending-review and no-trial statements describe its pre-collection
state. The clarified-1 and clarified-2 packets have separate identities.

Evaluators v1–v5 are frozen. New grading and collection use v6, which preserves
v5's electrical rules and adds checked recovery, consistent packet export,
explicit evidence validation and successful-workspace cleanup. Reproduce an old
campaign with its frozen collector and source revision; do not resume it with a
changed collector or silently upgrade its grader.

## Research notes

The TIA files `PLAN.md`, `EXTENSION_01.md`, `COMPOUND_SELECTION.md`,
`STOPPING_RULE_REVISION.md`, `EQUIVALENCE_CHECK.md` and `trials/trial02/PROTOCOL.md`
in `reproduction/payload/tia_case_v1/` record reference exploration and its stopping
rules. The frozen verification seals include their hashes, so the prepared runtime
retains these files. References to a participant, approval or an authorized stage
are part of those original records.

## Historical scripts

The following tools require files from the original research workspace. They are
not fresh-clone setup or qualification commands:

| Script under `reproduction/payload/` | Additional prerequisite |
|---|---|
| `tia_case_v1/validate_batch.py` | `analytic_validation02/fixture00/shared/deck.cir` from the earlier analytical validation |
| `tia_case_v1/boundary_validation.py` | Full per-case raw files and identity records for its nine named evaluations |
| `analog_supply_pilot_v1/prepare_domain_v2.py` | Original `public/` packet and `trials/trial02/freeze.json`; the generator's `public_v2/` output must not already exist |

Use the documented [offline checks and five native controls](run.md) to validate
a fresh checkout. Those commands do not depend on unpublished research folders.

## Waveform archive

`tools/plot_supply_repeat.py` recreates the recorded SUPPLY-repeat plot from the
original entry archive. The archive is not published; its identity and historical
submission state are retained in `evidence/entry_archive.json`. The public checkout
contains the plot and its metadata, but not the repeat's raw waveform files.
Recreating that specific plot requires a copy of the archive with the recorded
hash. A new simulation is a new result and cannot replace the original trace.

## Dependency metadata

Vendored PyYAML includes a redacted local wheel URL in its installation metadata.
That URL is a historical installation record, not a download source. The old WSL
simulator path in `analog_public_v1/run_reference.py` also belongs to the research
workspace. Current setup uses the pinned Windows ngspice build and does not install
that WSL fallback. Vendor notices and frozen dependency bytes remain intact.
