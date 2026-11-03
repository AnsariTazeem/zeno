"""Persist complete observed UI exports; assert browser/local transport hashes."""
import argparse
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
import sys

p=argparse.ArgumentParser();p.add_argument('proposal',type=int,choices=(1,2,3));a=p.parse_args()
data=json.load(sys.stdin)
for key in ['candidate','answer']:
    assert hashlib.sha256(data[key].encode('utf-8')).hexdigest()==data[key+'_sha256'],key
assert data['complete_DUT_blocks']==1
assert data['candidate'].lower().count('.subckt feedback ')==1
assert data['candidate'].strip().lower().endswith('.ends feedback')
out=Path(__file__).resolve().parent/f'proposal{a.proposal:02d}';out.mkdir(exist_ok=False)
(out/'candidate_rendered.sp').write_bytes(data['candidate'].encode('utf-8'))
(out/'rendered_answer_whitespace_normalized.txt').write_bytes(data['answer'].encode('utf-8'))
(out/'rendered_code_blocks.json').write_text(json.dumps(data.get('code_blocks',[]),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
receipt={'trial_id':'TIA-P01-T02','proposal':a.proposal,'retained_at_utc':datetime.now(timezone.utc).isoformat(),
         'capture_method':'Complete final rendered answer and all code blocks, before next request/response controls',
         'candidate_sha256':data['candidate_sha256'],'rendered_answer_sha256':data['answer_sha256'],
         'prose_normalization':'Collapse whitespace runs, trim, terminal LF; exact code separately retained',
         'code_normalization':'Rendered code trimEnd plus one terminal LF; initial blank retained',
         'browser_hashes_matched':True,'code_changed_by_researcher':False,
         'complete_DUT_blocks_in_latest_answer':data['complete_DUT_blocks'],'conversation_url':data['url'],
         'source':'Rendered UI export, not raw API response'}
(out/'capture_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'retained':str(out),'candidate_sha256':data['candidate_sha256']}))
