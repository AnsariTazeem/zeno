# Model responses

| Session | First proposal | Final proposal | Outcome |
|---|---|---|---|
| Original SUPPLY, Sol/High CLI, v3 | [Response](supply/proposal01/model_reply.md) | [Response 3](supply/proposal03/model_reply.md) | No full pass |
| Fresh SUPPLY, Sol/High CLI, v4 | [Response](supply_v4/proposal01/model_reply.md) | [Response 3](supply_v4/proposal03/model_reply.md) | No full pass; only rising settling misses in final circuit |
| SUPPLY repeat, Sol/High CLI, v4 | [Response](supply_v4_repeat/proposal01/model_reply.md) | [Response 3](supply_v4_repeat/proposal03/model_reply.md) | No full pass; collection recovered |
| LOAD, UI-labelled GPT-6/High | [Response](load/proposal01/rendered_answer_whitespace_normalized.txt) | [Response 3](load/proposal03/rendered_answer_whitespace_normalized.txt) | Pass, refined |
| LOAD, Sol/High CLI, v4 | [Response](load_cli/proposal01/model_reply.md) | Same proposal | Pass, refined |
| TIA, Sol/High CLI, v4 | [Response](tia_cli/proposal01/model_reply.md) | [Response 2](tia_cli/proposal02/model_reply.md) | Pass, refined |
| TIA, UI-labelled GPT-6/High | [Response](tia/proposal01/rendered_answer_whitespace_normalized.txt) | [Response 2](tia/proposal02/rendered_answer_whitespace_normalized.txt) | Pass, refined |

This table indexes the seven historical sessions only. The separate, partial
[frozen CLI cohort](matched_cli/README.md) keeps its own folder and index.

Each folder retains the selected candidate and capture evidence. CLI replies
are captured Markdown; browser replies are whitespace-normalized rendered
text with capture receipts. The complete archive retains broader raw evidence.
Private chat identifiers are withheld from published launch metadata;
response/candidate bytes stay unchanged. Historical native execution logs
retain machine paths used by the simulator. The archive source map and
[metadata record](../evidence/metadata_redactions.json) identify redactions.
Original capture records remain local.

The v3 follow-up interrupted after two replies is not counted as a complete
trial. Its record is `transcripts/interrupted_v3/INTERRUPTED.md` inside the
full entry archive. The original trial's feedback notes are separate.
Settings and collection conditions are described in
[methodology](../docs/methodology.md).

The SUPPLY repeat retains the original first answer after a date-directory
lookup interruption. Its remaining proposals resume the same model session.
