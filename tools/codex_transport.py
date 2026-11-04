"""Capture one subscription-authenticated, tool-free Codex response privately."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time

DISABLED = ('apps', 'plugins', 'browser_use', 'browser_use_external', 'computer_use',
            'memories', 'multi_agent', 'multi_agent_v2', 'unbounded_connection_retries',
            'shell_snapshot', 'shell_tool', 'unified_exec', 'view_image',
            'workspace_dependencies', 'image_generation', 'goals', 'sleep_tool')
SETTINGS = ('project_doc_max_bytes=0', 'memories.use_memories=false',
            'memories.generate_memories=false', 'agents.enabled=false',
            'shell_environment_policy.inherit="core"', 'web_search="disabled"',
            'windows.sandbox="mxc"', 'default_permissions="zeno"',
            'permissions.zeno.filesystem={ ":minimal" = "read", ":workspace_roots" = { "." = "read" } }',
            'permissions.zeno.network.enabled=false')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write('\n')


def environment():
    env = os.environ.copy()
    for key in list(env):
        if key.upper().startswith(('OPENAI_', 'AZURE_OPENAI_', 'CODEX_API_')):
            env.pop(key)
    return env


def describe():
    cli = shutil.which('codex')
    if not cli:
        raise RuntimeError('Codex CLI is not installed')
    version = subprocess.run([cli, '--version'], capture_output=True, check=True, timeout=30)
    return {'cli_sha256': sha(Path(cli)), 'cli_version': version.stdout.decode().strip(),
            'settings': list(SETTINGS), 'disabled_features': list(DISABLED),
            'authentication': 'ChatGPT subscription; no API fallback', 'timeout_seconds': 900,
            'automatic_wrapper_retries': 0, 'provider_transport_retries': 'Built-in CLI defaults'}


def command(cli, work, output, model, effort, session=None):
    args = [cli, '--ask-for-approval', 'never', '-C', str(work), 'exec']
    if session:
        args += ['resume', session]
    args += ['--ignore-user-config', '--ignore-rules', '--strict-config',
             '--skip-git-repo-check', '--json', '--model', model,
             '-c', 'model_reasoning_effort='+json.dumps(effort)]
    for setting in SETTINGS:
        args += ['-c', setting]
    for feature in DISABLED:
        args += ['--disable', feature]
    return args+['--output-last-message', str(output), '-']


def audit_trace(path, session, work, model, effort, home):
    events = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    if events[0].get('type') != 'session_meta' or events[0]['payload'].get('id') != session:
        raise ValueError('Capture ownership mismatch')
    calls = [r for r in events if r.get('type') == 'response_item' and
             r.get('payload', {}).get('type') in ('function_call', 'custom_tool_call')]
    if calls:
        raise ValueError('Tool request in a tool-free trial')
    contexts = [r['payload'] for r in events if r.get('type') == 'turn_context']
    if not contexts:
        raise ValueError('Effective collection settings are missing')
    for context in contexts:
        if (context.get('model') != model or context.get('effort') != effort or
                context.get('approval_policy') != 'never' or Path(context['cwd']).resolve() != work.resolve()):
            raise ValueError('Effective model or context settings changed')
        profile = context.get('permission_profile', {})
        fs = profile.get('file_system', {})
        if profile.get('network') != 'restricted' or fs.get('type') != 'restricted':
            raise ValueError('Restricted permission profile is not effective')
        found_work = False
        for entry in fs.get('entries', []):
            if entry.get('access') != 'read':
                raise ValueError('Unexpected write access in collection policy')
            target = entry['path']
            if target.get('type') == 'special':
                if target.get('value', {}).get('kind') != 'minimal':
                    raise ValueError('Unexpected special filesystem root')
            elif target.get('type') == 'path':
                allowed = Path(target['path']).resolve()
                if allowed == work.resolve():
                    found_work = True
                elif not allowed.is_relative_to((home/'tmp/arg0-windows').resolve()):
                    raise ValueError('Unexpected readable filesystem root')
            else:
                raise ValueError('Unknown filesystem entry')
        if not found_work:
            raise ValueError('Collection workspace is missing from its policy')
    return {'effective_model': model, 'effective_effort': effort, 'tool_requests': 0,
            'restricted_read_policy': True, 'restricted_network_policy': True,
            'trace_sha256': sha(path), 'contexts_checked': len(contexts)}


def request(prompt, output, work, model, effort, pinned, session=None):
    """One invocation, no resend; partial captures remain for inspection."""
    if describe() != pinned:
        raise ValueError('CLI identity or collection settings changed')
    output.mkdir(parents=True, exist_ok=False)
    cli = shutil.which('codex')
    env = environment()
    auth = subprocess.run([cli, 'login', 'status'], env=env, capture_output=True, timeout=30)
    if auth.returncode != 0 or b'Logged in using ChatGPT' not in auth.stdout+auth.stderr:
        raise RuntimeError('ChatGPT subscription authentication not confirmed')
    args = command(cli, work, output/'reply.txt', model, effort, session)
    started = datetime.now(timezone.utc)
    save(output/'launch.json', {'started_at_utc': started.isoformat(), 'command': args,
          'request_sha256': hashlib.sha256(prompt).hexdigest(), 'requested_session': session})
    (output/'request.txt').write_bytes(prompt)
    clock = time.monotonic()
    with (output/'events.jsonl').open('wb') as stdout, (output/'stderr.txt').open('wb') as stderr:
        process = subprocess.Popen(args, cwd=work, env=env, stdin=subprocess.PIPE,
                                   stdout=stdout, stderr=stderr,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        try:
            process.communicate(prompt, timeout=pinned['timeout_seconds'])
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True, timeout=20)
            process.communicate(timeout=20)
            raise RuntimeError('Model transport timed out; capture retained without retry')
    events = [json.loads(line) for line in (output/'events.jsonl').read_text(encoding='utf-8-sig').splitlines()]
    if (process.returncode != 0 or not (output/'reply.txt').is_file() or
            not (output/'reply.txt').stat().st_size or not any(e.get('type') == 'turn.completed' for e in events)):
        raise RuntimeError('Incomplete model capture; no automatic retry')
    ids = {e['thread_id'] for e in events if e.get('type') == 'thread.started'}
    if len(ids) != 1 or (session and ids != {session}):
        raise ValueError('Unexpected model session identity')
    session = ids.pop()
    home = Path(env.get('CODEX_HOME', Path.home()/'.codex'))
    dates = {started.strftime('%Y/%m/%d'), started.astimezone().strftime('%Y/%m/%d')}
    traces = {p for date in dates for p in (home/'sessions'/date).glob('*'+session+'.jsonl')}
    if len(traces) != 1:
        raise ValueError('Owned model trace is missing or ambiguous')
    audit = audit_trace(traces.pop(), session, work, model, effort, home)
    save(output/'audit.json', {**audit, 'elapsed_seconds': time.monotonic()-clock,
          'reply_sha256': sha(output/'reply.txt'),
          'usage': [e.get('usage') for e in events if e.get('type') == 'turn.completed']})
    save(output/'session.json', {'session_id': session})
    return session
