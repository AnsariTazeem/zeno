"""Prepare fixed task inputs and record externally collected model responses."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math
import re
import subprocess
import traceback
import uuid

ROOT = Path(__file__).resolve().parent.parent
TASKS = ('supply', 'load', 'tia')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def campaign_path(name, root=ROOT):
    if not re.fullmatch(r'[A-Za-z0-9_]{1,32}', name):
        raise ValueError('Use a campaign name with 1..32 letters, digits or underscores')
    return root/'.local-trials'/name


def prepare(name, model, effort, interface, root=ROOT, codex=False):
    """Freeze nine interleaved episodes before importing any model answer."""
    destination = campaign_path(name, root)
    if destination.exists():
        raise FileExistsError('Campaign exists; preserve its inputs and attempts')
    catalog = read(root/'tasks/catalog.json')
    revision = catalog['default_revision']
    sources = ['tools/collect_trials.py', 'tools/export_task.py', 'tools/audit_publication.py', 'tasks/catalog.json',
               'run_eval.py', 'reproduction/kit_manifest.json']
    transport = None
    if codex:
        sources += ['tools/codex_transport.py', 'tools/collect_cli.py']
        transport = module('prepared_codex_transport', root/'tools/codex_transport.py').describe()
    for row in read(root/'reproduction/kit_manifest.json')['files']:
        source = root/'reproduction'/row['path']
        if source.stat().st_size != row['bytes'] or sha(source) != row['sha256']:
            raise ValueError('Runtime source identity mismatch')
        sources.append('reproduction/'+row['path'])
    entries = catalog['revisions'][revision]['tasks']
    folder = catalog['revisions'][revision]['folder']
    for task in TASKS:
        sources += ['tasks/'+folder+'/'+task+'/'+r['name'] for r in entries[task]['files']]
    identities = {rel: sha(root/rel) for rel in sorted(set(sources))}
    destination.mkdir(parents=True)
    exporter = module('collection_exporter', root/'tools/export_task.py')
    schedule = []
    for repeat in range(3):
        order = TASKS[repeat:]+TASKS[:repeat]
        for task in order:
            trial = 'trial'+str(len(schedule)+1).zfill(2)
            inputs = destination/'inputs'/trial
            exporter.export(task, inputs, root=root, revision=revision)
            parts = ['Complete the task below using only the supplied files and evaluator feedback.',
                     'Do not use tools, browse, retrieve other files or consult other task sessions.',
                     'Use a fresh context for this trial. Return one complete circuit and a short explanation.',
                     'At most three proposals are allowed. Measurements will be returned after each proposal.']
            seen = {}
            for path in sorted(inputs.iterdir()):
                body = path.read_text(encoding='utf-8-sig')
                if body in seen:
                    parts.append(f'File {path.name} is identical to {seen[body]}.')
                else:
                    seen[body] = path.name
                    parts.extend(['\n[BEGIN FILE '+path.name+']', body, '[END FILE '+path.name+']'])
            prompt = inputs/'request.txt'
            prompt.write_text('\n'.join(parts)+'\n', encoding='utf-8', newline='\n')
            schedule.append({'trial': trial, 'task': task, 'repetition': repeat+1,
                             'request_sha256': sha(prompt),
                             'input_files': {p.name: sha(p) for p in sorted(inputs.iterdir())}})
    plan = {'created_at_utc': datetime.now(timezone.utc).isoformat(),
            'requested_model': model, 'requested_effort': effort, 'interface': interface,
            'backend_revision': None, 'temperature': None, 'seed': None,
            'packet_revision': revision, 'trials_per_task': 3, 'proposal_budget': 3,
            'tools': 'none; evaluator feedback only', 'automatic_wrapper_retries': 0,
            'separately_billed_API_fallback': False, 'native_run_prefix': 'c'+uuid.uuid4().hex[:8],
            'sources': identities, 'schedule': schedule, 'transport': transport}
    save(destination/'protocol.json', plan)
    (destination/'protocol.sha256').write_text(sha(destination/'protocol.json')+'\n', encoding='ascii')
    return destination


def verify(folder, root=ROOT):
    if sha(folder/'protocol.json') != (folder/'protocol.sha256').read_text(encoding='ascii').strip():
        raise ValueError('Collection protocol changed')
    plan = read(folder/'protocol.json')
    for rel, digest in plan['sources'].items():
        source = (root/rel).resolve()
        if not source.is_relative_to(root.resolve()) or sha(source) != digest:
            raise ValueError('Frozen collection source changed')
    for slot in plan['schedule']:
        inputs = folder/'inputs'/slot['trial']
        if set(p.name for p in inputs.iterdir()) != set(slot['input_files']):
            raise ValueError('Model-visible file set changed')
        if any(sha(inputs/name) != digest for name, digest in slot['input_files'].items()):
            raise ValueError('Model-visible input changed')
    return plan


def extract(reply, task):
    name = 'dut' if task == 'supply' else 'feedback'
    blocks = re.findall(r'```[^\n]*\n(.*?)```', reply, re.S)
    candidates = [b for b in blocks if re.search(r'(?im)^\s*\.subckt\s+'+name+r'\b', b)]
    if len(candidates) != 1:
        raise ValueError('Return exactly one complete '+name+' subcircuit in a code block')
    return candidates[0]


def feedback(result, proposal):
    data = {'proposal': proposal, 'proposals_remaining': 3-proposal,
            'outcome': result['category'], 'conditions': []}
    for point in result.get('points', []):
        data['conditions'].append({'condition': point['condition'], 'pass': point['pass'],
            'checks': [{key: check[key] for key in ('metric', 'value', 'operator', 'limit', 'pass')}
                       for check in point['checks']]})
    if result['category'] == 'invalid_candidate':
        data['format_requirement'] = 'Use the component grammar and bounds in the task.'
        data['diagnostic'] = result.get('error', 'Invalid component input')
    text = json.dumps(data, indent=2, allow_nan=False)+'\n'
    publication = module('feedback_publication', ROOT/'tools/audit_publication.py')
    if publication.inspect('feedback.json', text.encode()):
        raise ValueError('Private metadata in feedback; stop collection')
    return text


def decision(result, refined, proposal):
    category = result['category']
    if category not in ('pass', 'specification_failure', 'invalid_candidate'):
        return 'infrastructure_error'
    expected = {'pass': 100, 'specification_failure': 0, 'invalid_candidate': None}[category]
    if result.get('score') != expected or (expected is not None and type(result.get('score')) is not int):
        return 'infrastructure_error'
    if category == 'pass' or (category == 'specification_failure' and proposal == 3):
        if refined is None or refined.get('category') == 'infrastructure_error':
            return 'infrastructure_error'
        if refined.get('category') != category or refined.get('score') != expected or type(refined.get('score')) is not int:
            return 'numerical_disagreement'
    if category == 'pass':
        return 'confirmed_pass'
    return 'no_confirmed_pass' if proposal == 3 else 'continue'


def native_evaluate(prepared, task, candidate, run_id, proposal, refined):
    """Reuse a completed evaluation after interruption; never overwrite native output."""
    run = prepared/'eval_core_v4/runs'/task/run_id
    if not run.exists():
        command = [str(prepared/'.venv/Scripts/python.exe'), '-I', '-B',
                   str(prepared/'eval_core_v4/run_eval.py'), 'evaluate', '--task', task,
                   '--candidate', str(candidate), '--run-id', run_id, '--proposal', str(proposal),
                   '--numerics', 'refined' if refined else 'upstream']
        subprocess.run(command, cwd=prepared, check=False)
    if not (run/'result.json').is_file() or not (run/'candidate_original.sp').is_file():
        raise RuntimeError('Native evaluation incomplete; preserve logs and stop collection')
    if (run/'candidate_original.sp').read_bytes() != candidate.read_bytes():
        raise ValueError('Existing native run belongs to a different candidate')
    return read(run/'result.json'), {'result_sha256': sha(run/'result.json'), 'run_id': run_id}


def checked_turn(turn):
    receipt = read(turn/'receipt.json')
    if turn.name != 'proposal'+str(receipt['proposal']):
        raise ValueError('Recorded proposal identity changed')
    for name, field in [('model_reply.txt', 'response_sha256'), ('feedback.txt', 'feedback_sha256')]:
        if sha(turn/name) != receipt[field]:
            raise ValueError('Recorded response or feedback changed')
    candidate = turn/'candidate.sp'
    if (sha(candidate) if candidate.exists() else None) != receipt['candidate_sha256']:
        raise ValueError('Recorded candidate changed')
    return receipt


def checked_outcome(trial):
    outcome = read(trial/'outcome.json')
    if outcome['outcome'] in ('confirmed_pass', 'no_confirmed_pass'):
        turns = sorted(trial.glob('proposal[123]'))
        if not (trial/'started.json').exists() or not turns:
            raise ValueError('Completed trial has no captured attempt')
        receipts = [checked_turn(turn) for turn in turns]
        if (outcome['proposals'] != len(turns) or
                any(r['outcome'] != 'continue' for r in receipts[:-1]) or
                receipts[-1]['outcome'] != outcome['outcome'] or
                outcome['episode_success'] is not (outcome['outcome'] == 'confirmed_pass')):
            raise ValueError('Trial outcome disagrees with recorded proposals')
    return outcome


def active_slot(folder, plan):
    for slot in plan['schedule']:
        trial = folder/'attempts'/slot['trial']
        if (trial/'outcome.json').exists():
            outcome = checked_outcome(trial)['outcome']
            if outcome not in ('confirmed_pass', 'no_confirmed_pass'):
                raise ValueError('Campaign stopped on an infrastructure or protocol outcome')
            continue
        return slot
    raise ValueError('All scheduled trials are complete')


def start(folder, expected_trial, root=ROOT):
    plan = verify(folder, root)
    slot = active_slot(folder, plan)
    if slot['trial'] != expected_trial:
        raise ValueError('Response does not match the active trial')
    trial = folder/'attempts'/slot['trial']
    trial.mkdir(parents=True, exist_ok=True)
    save(trial/'started.json', {'trial': expected_trial,
         'started_at_utc': datetime.now(timezone.utc).isoformat()})


def interrupt(folder, expected_trial, kind, root=ROOT):
    plan = verify(folder, root)
    slot = active_slot(folder, plan)
    trial = folder/'attempts'/slot['trial']
    if expected_trial != slot['trial'] or not (trial/'started.json').exists():
        raise ValueError('Only a started active trial can be interrupted')
    if kind not in ('transport_error', 'protocol_error'):
        raise ValueError('Unknown interruption category')
    save(trial/'outcome.json', {'trial': expected_trial, 'task': slot['task'],
         'outcome': kind, 'proposals': len(list(trial.glob('proposal[123]'))), 'episode_success': None})


def record(folder, response, prepared, expected_trial, root=ROOT, evaluator=native_evaluate):
    plan = verify(folder, root)
    # All trials use the same prepared verifier; host paths remain private.
    lock = 'eval_core_v4/dependency_lock.json'
    if sha(prepared/lock) != sha(root/'reproduction/payload'/lock):
        raise ValueError('Prepare a runtime matching the collection protocol')
    slot = active_slot(folder, plan)
    if slot['trial'] != expected_trial:
        raise ValueError('Response does not match the active trial')
    trial = folder/'attempts'/slot['trial']
    if not (trial/'started.json').is_file():
        raise ValueError('Start the trial before collecting a model response')
    existing = sorted(trial.glob('proposal[123]'))
    for previous in existing:
        if not (previous/'receipt.json').is_file():
            raise ValueError('Incomplete proposal retained; do not regenerate or skip it')
        if checked_turn(previous)['outcome'] != 'continue':
            raise ValueError('Terminal proposal retained; finish its existing trial record')
    number = len(existing)+1
    if number > 3:
        raise ValueError('Proposal budget exhausted')
    turn = trial/('proposal'+str(number))
    turn.mkdir()
    raw = response.read_bytes()
    (turn/'model_reply.txt').write_bytes(raw)
    result = None
    refined = None
    native = []
    try:
        body = extract(raw.decode('utf-8-sig'), slot['task'])
    except (UnicodeError, ValueError) as error:
        outcome = 'no_confirmed_pass' if number == 3 else 'continue'
        category = 'response_format_error'
        message = str(error) if isinstance(error, ValueError) else 'Response must be UTF-8 text'
        report = {'proposal': number, 'proposals_remaining': 3-number, 'outcome': category,
                  'format_requirement': message}
        text = json.dumps(report, indent=2)+'\n'
    else:
        candidate = turn/'candidate.sp'
        candidate.write_text(body, encoding='utf-8', newline='\n')
        try:
            base_id = plan['native_run_prefix']+'_'+slot['trial']+'_b'+str(number)
            result, receipt = evaluator(prepared, slot['task'], candidate, base_id, number, False)
            native.append(receipt)
            category = result['category']
            if category == 'pass' or (category == 'specification_failure' and number == 3):
                refined, receipt = evaluator(prepared, slot['task'], candidate,
                                              base_id.replace('_b', '_f'), number, True)
                native.append(receipt)
            outcome = decision(result, refined, number)
            text = feedback(result, number) if outcome in ('continue', 'confirmed_pass', 'no_confirmed_pass') else ''
        except Exception:
            # Retain failures locally, without returning machine diagnostics to the model.
            (turn/'error.txt').write_text(traceback.format_exc(), encoding='utf-8')
            outcome = 'infrastructure_error'
            category = 'infrastructure_error'
            text = ''
    (turn/'feedback.txt').write_text(text, encoding='utf-8', newline='\n')
    receipt = {'proposal': number, 'response_sha256': sha(turn/'model_reply.txt'),
               'candidate_sha256': sha(turn/'candidate.sp') if (turn/'candidate.sp').exists() else None,
               'category': category, 'outcome': outcome, 'native_evaluations': native,
               'feedback_sha256': sha(turn/'feedback.txt')}
    save(turn/'receipt.json', receipt)
    if outcome != 'continue':
        save(trial/'outcome.json', {'trial': slot['trial'], 'task': slot['task'],
              'outcome': outcome, 'proposals': number,
              'episode_success': outcome == 'confirmed_pass' if outcome in ('confirmed_pass', 'no_confirmed_pass') else None})
    return {'trial': slot['trial'], 'proposal': number, 'outcome': outcome,
            'feedback': str(turn/'feedback.txt')}


def status(folder, root=ROOT):
    plan = verify(folder, root)
    rows = []
    for slot in plan['schedule']:
        trial = folder/'attempts'/slot['trial']
        path = trial/'outcome.json'
        if path.exists():
            value = checked_outcome(trial)
        else:
            turns = sorted(trial.glob('proposal[123]')) if trial.exists() else []
            incomplete = any(not (p/'receipt.json').is_file() for p in turns)
            for turn in turns:
                if (turn/'receipt.json').is_file():
                    checked_turn(turn)
            value = {'outcome': 'incomplete' if incomplete else ('in_progress' if (trial/'started.json').exists() else 'pending'),
                     'proposals': len(turns), 'episode_success': None}
        rows.append({'trial': slot['trial'], 'task': slot['task'],
                     'started': (trial/'started.json').is_file(), **value})
    groups = []
    for task in TASKS:
        members = [r for r in rows if r['task'] == task]
        complete = [r for r in members if r['episode_success'] is not None]
        successes = sum(r['episode_success'] for r in complete)
        # Estimates are withheld until the entire predeclared task group completes.
        estimates = None
        if len(complete) == len(members):
            n = len(complete)
            estimates = {'observed_success_fraction': successes/n,
                         'pass_at_k': {str(k): 1-math.comb(n-successes, k)/math.comb(n, k) for k in range(1, n+1)},
                         'pass_power_k': {str(k): math.comb(successes, k)/math.comb(n, k) for k in range(1, n+1)}}
        groups.append({'task': task, 'planned_episodes': len(members),
                       'complete_episodes': len(complete), 'successful_episodes': successes,
                       'started_episodes': sum(r['started'] for r in members),
                       'other_episodes': len(members)-len(complete), 'estimates': estimates})
    return {'groups': groups, 'attempts': rows,
            'metric_unit': 'One fresh-context adaptive episode, at most three proposals; k counts episodes',
            'statistical_scope': 'Empirical finite-sample estimates; interpreting them as population probabilities requires independent identically distributed episodes'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    create = sub.add_parser('prepare')
    create.add_argument('--name', required=True)
    create.add_argument('--model', required=True)
    create.add_argument('--effort', required=True)
    create.add_argument('--interface', required=True)
    create.add_argument('--codex', action='store_true', help='Pin the installed subscription CLI and its access policy')
    ingest = sub.add_parser('record')
    ingest.add_argument('--name', required=True)
    ingest.add_argument('--response', type=Path, required=True)
    ingest.add_argument('--trial', required=True)
    ingest.add_argument('--prepared-root', type=Path, required=True)
    begin = sub.add_parser('start')
    begin.add_argument('--name', required=True)
    begin.add_argument('--trial', required=True)
    stop = sub.add_parser('interrupt')
    stop.add_argument('--name', required=True)
    stop.add_argument('--trial', required=True)
    stop.add_argument('--kind', choices=('transport_error', 'protocol_error'), required=True)
    status_parser = sub.add_parser('status')
    status_parser.add_argument('--name', required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        print(prepare(args.name, args.model, args.effort, args.interface, codex=args.codex))
    elif args.command == 'record':
        print(json.dumps(record(campaign_path(args.name), args.response, args.prepared_root.resolve(), args.trial), indent=2))
    elif args.command == 'start':
        start(campaign_path(args.name), args.trial)
    elif args.command == 'interrupt':
        interrupt(campaign_path(args.name), args.trial, args.kind)
    else:
        folder = campaign_path(args.name)
        print(json.dumps(status(folder), indent=2))


if __name__ == '__main__':
    main()
