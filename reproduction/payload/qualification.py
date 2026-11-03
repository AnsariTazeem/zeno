"""Run frozen grading tests and four native controls in a prepared source kit."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'qualification'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    with path.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(data, indent=2, allow_nan=False) + '\n')


def run(label, command, timeout=1000):
    started = time.monotonic()
    with (OUT / (label + '_stdout.txt')).open('xb') as stdout, (OUT / (label + '_stderr.txt')).open('xb') as stderr:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True, timeout=20)
            process.wait(timeout=20)
            raise RuntimeError(label + ' timed out; retained as infrastructure failure')
    return {'label': label, 'returncode': code, 'elapsed_seconds': time.monotonic() - started,
            'command': command}


def main():
    OUT.mkdir(exist_ok=False)
    result = {'started_at_utc': datetime.now(timezone.utc).isoformat(), 'outcome': 'incomplete',
              'model_calls': 0, 'runs': [], 'scope': 'Fresh venv/download test on this Windows host; not a fresh OS or independent machine'}
    try:
        assert Path(sys.prefix).resolve() == (ROOT / '.venv').resolve(), 'Use the new environment Python'
        assert 'include-system-site-packages = false' in (ROOT / '.venv/pyvenv.cfg').read_text()
        import numpy
        assert numpy.__version__ == '2.3.5'
        assert Path(numpy.__file__).resolve().is_relative_to(ROOT / '.venv')
        result['environment'] = {'python': sys.version, 'executable': sys.executable,
                                 'isolated': bool(sys.flags.isolated), 'numpy_origin': numpy.__file__,
                                 'numpy_version': numpy.__version__, 'venv_configuration': (ROOT / '.venv/pyvenv.cfg').read_text()}
        assert sys.flags.isolated
        spec = importlib.util.spec_from_file_location('qualified_core', ROOT / 'eval_core_v4/run_eval.py')
        core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core)
        assert core.verify() == 1202
        for label, script in [('bootstrap_adversarial', ROOT / 'checks/test_bootstrap.py'),
                              ('frozen_regressions', ROOT / 'eval_core_v4/test_core.py'),
                              ('supply_evidence_regressions', ROOT / 'eval_core_v4/test_supply_evidence.py')]:
            launcher = "import sys,runpy; sys.path.insert(0,sys.argv[1]); script=sys.argv[2]; sys.argv=[script]; runpy.run_path(script,run_name='__main__')"
            entry = run(label, [sys.executable, '-I', '-B', '-c', launcher, str(script.parent), str(script)], 120)
            result['runs'].append(entry)
            assert entry['returncode'] == 0, label
        print('Bootstrap adversarial and frozen grading tests passed', flush=True)
        cases = read(ROOT / 'checks/controls.json')['controls']
        assert len({(c['task'], c['label']) for c in cases}) == len(cases), 'Duplicate task/run identifier'
        def native(case):
            label = case['label']
            log_label = case['task'] + '_' + label
            print('Starting native control: ' + log_label, flush=True)
            command = [sys.executable, '-I', '-B', str(ROOT / 'eval_core_v4/run_eval.py'),
                       'evaluate', '--task', case['task'], '--candidate', str(ROOT / case['candidate']),
                       '--run-id', label]
            entry = run(log_label, command)
            folder = ROOT / 'eval_core_v4/runs' / case['task'] / label
            common = read(folder / 'result.json')
            assert entry['returncode'] == 0 and common['category'] == case['category'], label
            assert common['model_calls'] == 0 and common['evidence_mode'] == 'fresh_native_simulation'
            expected = core.assess(case['task'], read(ROOT / case['expected_native']),
                                   read(ROOT / core.TASKS[case['task']]['public'] / 'contract.json'),
                                   native_dir=ROOT / case['expected_native_directory'] if case.get('expected_native_directory') else None)
            assert expected['category'] == common['category']
            assert len(common['points']) == len(expected['points']) == case['conditions']
            deltas = []
            for new, old in zip(common['points'], expected['points']):
                assert new['condition'] == old['condition'] and new['pass'] == old['pass']
                assert len(new['checks']) == len(old['checks'])
                for check, original in zip(new['checks'], old['checks']):
                    assert all(check[k] == original[k] for k in ['metric', 'operator', 'limit', 'pass'])
                    a, b = check['value'], original['value']
                    if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)) and math.isfinite(a) and math.isfinite(b):
                        deltas.append({'condition': new['condition'], 'metric': check['metric'], 'absolute_delta': abs(a-b)})
            completions = list((folder / 'native').rglob('completion.json'))
            assert len(completions) == case['native_processes']
            for path in completions:
                done = read(path)
                assert done['returncode'] == 0 and not done['timed_out'] and not done['fatal_log_match']
            for row in read(folder / 'manifest.json')['files']:
                assert sha(folder / row['path']) == row['sha256']
            entry.update({'category': common['category'], 'conditions': len(common['points']),
                          'passing_conditions': sum(p['pass'] for p in common['points']),
                          'native_processes': len(completions), 'all_check_classifications_reproduced': True,
                          'metric_deltas': deltas, 'candidate_sha256': common['candidate_sha256'],
                          'result_sha256': sha(folder / 'result.json')})
            write(OUT / (log_label + '_comparison.json'), entry)
            print('Completed native control: ' + log_label + ' -> ' + common['category'], flush=True)
            return entry
        # Two independent workspaces; bounded concurrency, no agents/inference.
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(native, case) for case in cases]
            errors = []
            for future in as_completed(futures):
                try:
                    result['runs'].append(future.result())
                except Exception as error:
                    errors.append(type(error).__name__ + ': ' + str(error))
            if errors:
                raise RuntimeError('; '.join(errors))
        result['verified_runtime_files_after_runs'] = core.verify()
        result['outcome'] = 'fresh_venv_controls_reproduced_on_existing_host'
    except Exception as error:
        result['outcome'] = 'qualification_incomplete'
        result['error'] = type(error).__name__ + ': ' + str(error)
    result['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    write(OUT / 'result.json', result)
    files = []
    for folder in [OUT, ROOT / 'eval_core_v4/runs']:
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                files.append({'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size, 'sha256': sha(path)})
    write(OUT / 'artifact_manifest.json', {'files': files})
    print(json.dumps({k: v for k, v in result.items() if k not in ['runs', 'environment']}, indent=2), flush=True)
    return 0 if result['outcome'] == 'fresh_venv_controls_reproduced_on_existing_host' else 3


if __name__ == '__main__':
    raise SystemExit(main())
