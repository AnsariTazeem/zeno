"""Collect one complete adaptive episode through the pinned ChatGPT CLI."""
from pathlib import Path
import argparse
import importlib.util
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT/'tools'/filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(folder, trial_id, prepared):
    core = load('cli_collection_core', 'collect_trials.py')
    transport = load('cli_collection_transport', 'codex_transport.py')
    plan = core.verify(folder)
    if plan.get('transport') != transport.describe():
        raise ValueError('Prepare this campaign with --codex before collection')
    slot = core.active_slot(folder, plan)
    if slot['trial'] != trial_id:
        raise ValueError('Requested trial is not the next scheduled episode')
    trial = folder/'attempts'/trial_id
    if trial.exists():
        raise FileExistsError('Episode already started; inspect retained capture rather than regenerating')
    work = Path(tempfile.mkdtemp(prefix='zeno_')).resolve()
    assert not any(work.iterdir())
    core.start(folder, trial_id)
    core.save(trial/'working_directory.json', {'path': str(work)})
    prompt = (folder/'inputs'/trial_id/'request.txt').read_bytes()
    session = None
    for number in range(1, 4):
        core.verify(folder)
        capture = trial/('capture'+str(number))
        try:
            session = transport.request(prompt, capture, work, plan['requested_model'],
                                          plan['requested_effort'], plan['transport'], session)
        except ValueError:
            core.interrupt(folder, trial_id, 'protocol_error')
            raise
        except Exception:
            core.interrupt(folder, trial_id, 'transport_error')
            raise
        result = core.record(folder, capture/'reply.txt', prepared, trial_id)
        print(result, flush=True)
        if result['outcome'] != 'continue':
            return result
        prompt = (Path(result['feedback']).read_text(encoding='utf-8')+
                  '\nReturn the next complete proposal with a short explanation. All original requirements remain unchanged.\n').encode()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True)
    parser.add_argument('--trial', required=True)
    parser.add_argument('--prepared-root', type=Path, required=True)
    args = parser.parse_args()
    core = load('cli_collection_path', 'collect_trials.py')
    run(core.campaign_path(args.name), args.trial, args.prepared_root.resolve())
