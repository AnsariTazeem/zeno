"""Audit and summarize the retained complete-session catalog, without pooling settings."""
from collections import defaultdict
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
SETTING_FIELDS = ('task', 'task_id', 'model', 'recorded_grader',
                  'backend_revision', 'temperature', 'seed')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def summarize(catalog, root=ROOT):
    """Require confirmed terminal verdicts; preserve trial identities and settings."""
    root = root.resolve()
    trials = defaultdict(list)
    seen_keys = set()
    for row in catalog['evaluations']:
        if row['key'] in seen_keys:
            raise ValueError('Duplicate evaluation key')
        seen_keys.add(row['key'])
        if row['profile'] not in ('baseline', 'refined'):
            raise ValueError('Unknown numerical profile')
        if type(row['proposal']) is not int or not 1 <= row['proposal'] <= 3:
            raise ValueError('Proposal outside the three-proposal budget')
        if row['category'] not in ('pass', 'specification_failure'):
            raise ValueError('Non-electrical outcome requires a separate attempt ledger')
        expected = 100 if row['category'] == 'pass' else 0
        if type(row['score']) is not int or row['score'] != expected:
            raise ValueError('Electrical score disagrees with category')
        relative = Path(row['candidate'])
        path = (root / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to((root/'transcripts').resolve()):
            raise ValueError('Candidate path must stay under transcripts')
        if not path.is_file():
            raise ValueError('Candidate file is missing')
        trials[row['trial_id']].append(row)

    sessions = []
    for trial_id, rows in sorted(trials.items()):
        settings = {name: rows[0][name] for name in SETTING_FIELDS}
        if any(any(row[name] != value for name, value in settings.items()) for row in rows):
            raise ValueError('Settings changed within a trial')
        baseline = sorted((r for r in rows if r['profile'] == 'baseline'), key=lambda r: r['proposal'])
        numbers = [r['proposal'] for r in baseline]
        if not numbers or numbers != list(range(1, len(numbers)+1)):
            raise ValueError('Missing or duplicate baseline proposal')
        if any(r['category'] == 'pass' for r in baseline[:-1]):
            raise ValueError('Trial continued after a passing proposal')
        final = baseline[-1]
        refined = [r for r in rows if r['profile'] == 'refined']
        if len(refined) != 1 or refined[0]['proposal'] != final['proposal']:
            raise ValueError('Final proposal needs exactly one finer confirmation')
        if refined[0]['category'] != final['category']:
            raise ValueError('Numerical profiles disagree')
        # Equal bytes are sufficient: the file path need not be identical.
        candidate = root/final['candidate']
        if candidate.read_bytes() != (root/refined[0]['candidate']).read_bytes():
            raise ValueError('Finer confirmation used a different candidate')
        if final['category'] != 'pass' and len(baseline) != 3:
            raise ValueError('Failure session stopped before its proposal budget')
        sessions.append({'trial_id': trial_id, **settings, 'packet_revision': 'recorded',
                         'proposal_budget': 3, 'proposals': len(baseline),
                         'confirmed_pass': final['category'] == 'pass',
                         'final_candidate': final['candidate'],
                         'final_candidate_sha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
                         'final_baseline': final['key'], 'final_refined': refined[0]['key']})

    proposals = sum(t['proposals'] for t in sessions)
    if catalog['completed_task_trials'] != len(sessions) or catalog['baseline_proposals'] != proposals:
        raise ValueError('Catalog totals disagree with the evaluation records')
    grouped = defaultdict(list)
    for session in sessions:
        key = tuple(json.dumps(session[name], sort_keys=True) for name in SETTING_FIELDS)
        grouped[key].append(session)
    groups = []
    for key, members in sorted(grouped.items()):
        groups.append({**{name: members[0][name] for name in SETTING_FIELDS},
                       'packet_revision': 'recorded', 'proposal_budget': 3,
                       'complete_sessions': len(members),
                       'confirmed_passes': sum(m['confirmed_pass'] for m in members),
                       'proposals_per_session': [m['proposals'] for m in members],
                       'trial_ids': [m['trial_id'] for m in members]})
    return {'scope': 'Selected historical complete sessions; catalog consistency audit, not native regrading',
            'packet_revision': 'recorded', 'complete_sessions': len(sessions),
            'baseline_proposals': proposals, 'saved_evaluations': len(seen_keys),
            'disclosed_interrupted_attempts': catalog['interrupted_attempts_included_separately'],
            'complete_attempt_ledger_available': False,
            'groups': groups, 'sessions': sessions,
            'population_pass_rate': None, 'pass_at_k': None, 'pass_power_k': None,
            'statistical_limit': 'Selected development sessions, sparse groups and unknown backend settings; no population estimate or model ranking'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = summarize(read(ROOT/'results/catalog.json'))
    body = json.dumps(report, indent=2, allow_nan=False)+'\n'
    if args.output:
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(body)
    else:
        print(body, end='')


if __name__ == '__main__':
    main()
