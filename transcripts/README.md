# Model responses

| Session | First proposal | Final proposal | Outcome |
|---|---|---|---|
| Original SUPPLY, Sol/High CLI, v3 | [Response](supply/proposal01/model_reply.md) | [Response 3](supply/proposal03/model_reply.md) | No full pass |
| Fresh SUPPLY, Sol/High CLI, v4 | [Response](supply_v4/proposal01/model_reply.md) | [Response 3](supply_v4/proposal03/model_reply.md) | No full pass; only rising settling misses in final circuit |
| SUPPLY repeat, Sol/High CLI, v4 | [Response](supply_v4_repeat/proposal01/model_reply.md) | [Response 3](supply_v4_repeat/proposal03/model_reply.md) | No full pass; collection recovered |
| LOAD, UI-labelled GPT-6/High | [Response](load/proposal01/rendered_answer_whitespace_normalized.txt) | [Response 3](load/proposal03/rendered_answer_whitespace_normalized.txt) | Pass, refined |
| LOAD, Sol/High CLI, v4 | [Response](load_cli/proposal01/model_reply.md) | Same proposal | Pass, refined |
| TIA, UI-labelled GPT-6/High | [Response](tia/proposal01/rendered_answer_whitespace_normalized.txt) | [Response 2](tia/proposal02/rendered_answer_whitespace_normalized.txt) | Pass, refined |

Each folder retains the selected candidate and capture evidence. CLI replies
are captured Markdown; browser replies are whitespace-normalized rendered
text with capture receipts. The complete archive retains broader raw evidence.
Private chat identifiers and local launch paths are withheld from public
metadata; response/candidate bytes stay unchanged. The source map records
each metadata redaction. Unmodified records remain in the local entry archive.

The v3 follow-up interrupted after two replies is not counted as a complete
trial. Its record is `transcripts/interrupted_v3/INTERRUPTED.md` inside the
full entry archive. The original trial's feedback notes are separate.
Backend revisions, temperatures and seeds are unknown. These are different
collection interfaces and grader versions, not a matched model ranking.

The SUPPLY repeat retains the original first answer after a date-directory
lookup interruption. Its remaining proposals resume the same model session.
