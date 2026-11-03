# Guide check — 3 November 2026

Source: [micro1 Participant Guide](https://hrcdn.net/s3_pub/istreet-assets/R_8vs8ejamSPapSbUxmcWQ/Eval_Hackathon_Participant_Guide.pdf),
22 pages. Local PDF SHA-256:
`5b9109672654cf0784456f8d64948aa3104e929b01112bfc77f85e685f540e12`.
The file was read and page 18's layout checked. It is not bundled in the repo.

Page 18 suggests a folder layout and defers to the submission format released
at kickoff. Folder names alone do not establish compliance.

| Guide item | State | Evidence or remaining work |
|---|---|---|
| Clear, realistic tasks with stated rules | Implemented, simulation scope | Three public packets and numerical contracts; customer prevalence/hardware validity not established |
| Passing references and deliberately wrong answers | Tested | Five native controls; positive, negative, equivalent-solution and corrupt-evidence tests |
| Grade the result and preserve constraints | Implemented | Every required metric must pass across the whole grid |
| Keep answers out of model inputs | Public export tested | Actual packet identity/export checks; separate OS/container isolation not established |
| Explain model failures | Recorded | Responses, feedback and SUPPLY settling analysis; LOAD/TIA successes retained |
| Multiple trials per task, report spread | Partial | SUPPLY: two complete sessions under separately labelled grader versions. LOAD/TIA: one each. Guide suggests 3–5 as a start |
| Evidence across model conditions | Limited | CLI Sol/High and UI-labelled GPT-6/High are not a matched comparison; backend/settings partly unknown |
| Roughly 5–10 tasks | Below recommendation | Three distinct tasks. Conditions are not counted as extra tasks |
| Clean reproduction, versions, runtime and cost | Partial | Fresh-venv native qualification passed on this host; independent-machine run untested |
| Prior work, AI use and permitted data | Disclosed; rights decision open | Public infrastructure, synthetic tasks and notices; no TI/OpenCode assets in curated source |
| Author expertise and human review | Unverified | No independent human expert review or personal checking record claimed |
| ZIP under 50 MB; no videos or credentials | Draft verified | Local 27,434,760-byte archive passed extraction/replay and bounded credential-pattern checks |
| Description and accessible video ≤5 minutes | Unfinished | Description/script drafts exist; no recorded/hosted video or tested link |
| Final rubric self-assessment | Open | This is a requirement audit, not a scored mock judging session; no score is invented |
| Agreement, final fields and submission | Not completed here | No terms accepted and no submission made by this workflow |

The build continues without lessons or quizzes as prerequisites. The review
criterion remains unverified; a linter or test count does not replace it.
These repository changes do not update the sealed submission ZIP. A later
package revision must include them and repeat the delivery checks.
