"""Check packet compatibility, disclosed syntax and electrical verdict boundaries."""
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
PAYLOAD = ROOT/'reproduction/payload'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition, message):
    if not condition:
        raise ValueError(message)


def packet_checks(root=ROOT):
    catalog = read(root/'tasks/catalog.json')
    revision = catalog['default_revision']
    version = catalog['revisions'][revision]
    records = []
    for task, entry in version['tasks'].items():
        folder = (root/'tasks'/version['folder']/task).resolve()
        require(folder.is_relative_to((root/'tasks').resolve()), 'Packet folder escapes tasks')
        for row in entry['files']:
            path = (folder/row['name']).resolve()
            require(path.is_relative_to(folder), 'Packet file escapes folder')
            body = path.read_bytes()
            require(len(body) == row['bytes'] and hashlib.sha256(body).hexdigest() == row['sha256'],
                    'Packet identity changed: '+task+'/'+row['name'])
        recorded = read(root/'tasks'/task/'contract.json')
        current = read(folder/'contract.json')
        metadata = {'status', 'packet_revision', 'input_format', 'measurement_reporting'}
        require({k: v for k, v in recorded.items() if k not in metadata} ==
                {k: v for k, v in current.items() if k not in metadata},
                'Electrical contract changed: '+task)
        require((folder/'PROMPT.txt').read_bytes() == (folder/'TASK.md').read_bytes(),
                'Prompt and task text diverge: '+task)
        text = (folder/'TASK.md').read_text()
        policy = current['input_format']
        limit = policy.get('maximum_characters', policy.get('maximum_utf8_bytes'))
        require(f'{limit:,}' in text, 'Input-size limit missing from prompt: '+task)
        if policy['name_max_characters'] is not None:
            require(f"{policy['name_max_characters']} characters" in text,
                    'Name limit missing from prompt: '+task)
        if policy['passive_nodes_must_differ']:
            require('distinct nodes' in text, 'Distinct-node rule missing from prompt: '+task)
        require('No model trial has yet' not in text and 'participant review is pending' not in text,
                'Historical status is embedded in the new task: '+task)
        for row in catalog['tasks'][task]['files']:
            if row['name'] not in {'TASK.md', 'PROMPT.txt', 'contract.json'}:
                require((folder/row['name']).read_bytes() == (root/'tasks'/task/row['name']).read_bytes(),
                        'Fixed task asset changed: '+task+'/'+row['name'])
        records.append({'task': task, 'packet_revision': revision, 'electrical_contract_unchanged': True,
                        'prompt_matches_task': True, 'fixed_assets_unchanged': True})
    return records


def syntax_checks(root=ROOT):
    catalog = read(root/'tasks/catalog.json')
    revision = catalog['revisions'][catalog['default_revision']]
    rows = []
    for task in ['supply', 'load', 'tia']:
        folder = root/'tasks'/revision['folder']/task
        policy = read(folder/'contract.json')['input_format']
        source = {'supply': 'analog_supply_pilot_v1/circuit_input.py',
                  'load': 'capload_case_v1/network_input.py',
                  'tia': 'tia_case_v1/network_input.py'}[task]
        compiler = load('syntax_'+task, root/'reproduction/payload'/source)
        compile_candidate = compiler.compile_dut if task == 'supply' else compiler.compile_network
        base = (root/'reference'/f'{task}.sp').read_text()
        prefix, ending = base.rsplit('.ends', 1)
        def add(line):
            return prefix+line+'\n.ends'+ending
        port = {'supply': 'out', 'load': 'load', 'tia': 'out'}[task]
        maximum = policy.get('maximum_characters', policy.get('maximum_utf8_bytes'))
        filler = maximum-len(base.encode('utf-8'))-2
        probes = [('reference', base, True),
                  ('same_node', add(f'Rcheck {port} {port} 1000'), not policy['passive_nodes_must_differ']),
                  ('name_32', add(f'Rcheck {port} '+('n'*32)+' 1000'), True),
                  ('name_33', add(f'Rcheck {port} '+('n'*33)+' 1000'), policy['name_max_characters'] is None),
                  ('size_at_limit', add('*'+('x'*filler)), True),
                  ('size_over_limit', add('*'+('x'*(filler+1))), False),
                  ('duplicate_name', add(f'Rcheck {port} ncheck 1000\nRCHECK {port} ncheck 1000'), False)]
        for label, text, expected in probes:
            try:
                compile_candidate(text)
                accepted = True
            except ValueError:
                accepted = False
            require(accepted == expected, f'{task}: compiler disagrees with disclosed policy: {label}')
            rows.append({'task': task, 'probe': label, 'expected_accepted': expected, 'accepted': accepted})
    return rows


def declaration_checks(root=ROOT):
    """Check declared numerical requirements against the machine-readable contract."""
    catalog = read(root/'tasks/catalog.json')
    folder = root/'tasks'/catalog['revisions'][catalog['default_revision']]['folder']
    rows = []
    def declared(task, path, render):
        contract = read(folder/task/'contract.json')
        value = contract
        for key in path:
            value = value[key]
        phrase = render(value)
        text = ' '.join((folder/task/'TASK.md').read_text().split())
        require(phrase in text, f'{task}: numerical requirement missing or inconsistent: {phrase}')
        rows.append({'task': task, 'contract_path': '.'.join(path), 'declaration': phrase})
    supply = [('dc_gain_dB', '>=', 'DC gain', 'dB', 1),
              ('ugf_Hz', '>=', 'Unity-gain frequency', 'MHz', 1e6),
              ('pm_deg', '>=', 'Phase margin', 'degrees', 1),
              ('gm_dB', '>=', 'Gain margin', 'dB', 1),
              ('power_uW', '<=', 'DC supply power, including bias', 'uW', 1),
              ('command_rise_settle_ns', '<=', 'Rising settling', 'ns', 1),
              ('command_fall_settle_ns', '<=', 'Falling settling', 'ns', 1),
              ('n_triode', '<=', 'MOS devices out of saturation at DC', '', 1),
              ('input_current_uA', '<=', 'Monitored DC input-source current', 'uA', 1)]
    for key, operator, label, unit, scale in supply:
        declared('supply', ['limits', key, operator],
                 lambda v, op=operator, label=label, unit=unit, scale=scale:
                 f'| {label} | {op}{v/scale:g}'+(' '+unit if unit else '')+' |')
    declared('supply', ['command_error_band_V'], lambda v: f'+/-{v*1000:g} mV band')
    declared('load', ['limits', 'all_downward_unity_crossing_phase_margins_deg_min'], lambda v: f'**>={v:g} degrees')
    declared('load', ['limits', 'command_error_band_V'], lambda v: f'**+/-{v:g} V**')
    declared('load', ['limits', 'settle_us_max_each_of_four_edges'], lambda v: f'**{v:g} us**')
    declared('load', ['limits', 'overshoot_V_max_each_edge'], lambda v: f'**<={v:.3f} V**')
    declared('load', ['limits', 'dc_supply_power_uW_max'], lambda v: f'**<={v:g} uW**')
    declared('tia', ['limits', 'transimpedance_real_at_10Hz_ohm'], lambda v: f'{v[0]:g}..{v[1]:g} ohm')
    declared('tia', ['limits', 'transimpedance_imag_at_10Hz_abs_max_ohm'], lambda v: f'<={v:g} ohm')
    declared('tia', ['limits', 'first_minus_3dB_bandwidth_min_Hz'], lambda v: f'>={v/1e6:g} MHz')
    declared('tia', ['limits', 'all_downward_unity_crossing_phase_margins_min_deg'], lambda v: f'>={v:g} degrees')
    declared('tia', ['limits', 'loop_phase_at_10Hz_abs_less_than_deg'], lambda v: f'absolute initial phase <{v:g} degrees')
    declared('tia', ['limits', 'loop_gain_at_10Hz_greater_than_dB'], lambda v: f'(>{v:g} dB at 10 Hz)')
    declared('tia', ['limits', 'dc_positive_delivered_supply_and_reference_power_max_uW'], lambda v: f'<={v:g} uW')
    declared('tia', ['limits', 'command_error_band_V'], lambda v: f'+/-{v*1000:g} mV')
    declared('tia', ['limits', 'each_edge_settle_max_ns'], lambda v: f'by {v:g} ns')
    declared('tia', ['limits', 'each_edge_overshoot_max_V'], lambda v: f'<={v*1000:g} mV')
    return rows


def precision_checks(root=ROOT):
    """Exercise the pinned extractor's reporting and interpolation conventions."""
    from unittest.mock import patch
    import numpy as np
    catalog = read(root/'tasks/catalog.json')
    folder = root/'tasks'/catalog['revisions'][catalog['default_revision']]['folder']/'supply'
    policy = read(folder/'contract.json')['measurement_reporting']
    expected = {'dc_gain_dB': 2, 'pm_deg': 1, 'gm_dB': 1, 'power_uW': 2, 'input_current_uA': 4}
    require(policy['rounded_before_comparison'] == expected, 'Reporting precision policy changed')
    require(policy['crossing_interpolation'] == 'linear_frequency' and
            policy['saturation_margin_decimals_before_count'] == 3, 'Interpolation/count policy changed')
    benchmark = root/'reproduction/payload/analog_public_v1/upstream/benchmark'
    sys.path.insert(0, str(benchmark))
    try:
        measure = load('pinned_measurement_probe', benchmark/'measure.py')
        sim = load('pinned_interpolation_probe', benchmark/'sim.py')
        results = [
            ('rounded_phase_inside', measure._pm_relative(np.array([10., 100.]), np.array([0., -125.04]), 100.), 55.),
            ('rounded_phase_outside', measure._pm_relative(np.array([10., 100.]), np.array([0., -125.06]), 100.), 54.9),
            ('rounded_current_inside', measure._input_current_uA({'vin#branch': .010049e-6}), .01),
            ('rounded_current_outside', measure._input_current_uA({'vin#branch': .010051e-6}), .0101),
            ('linear_frequency_crossing', sim.xcross(np.array([10., 100.]), np.array([2., -2.]), 0.), 55.)]
        for vds, count in [(.3996, 0), (.3994, 1)]:
            with patch.object(measure, 'read_print', return_value={
                '@m1[id]': 1e-6, '@m1[vgs]': .5, '@m1[vds]': vds, '@m1[vdsat]': .4}):
                result = measure.headroom(Path('unused'), [('m1', 'n', '0', 'out')])
            results.append(('rounded_saturation_'+str(vds), result['n_triode'], count))
        for label, actual, expected_value in results:
            require(actual == expected_value, 'Reporting convention mismatch: '+label)
    finally:
        sys.path.remove(str(benchmark))
    return [{'probe': label, 'actual': actual, 'expected': expected_value}
            for label, actual, expected_value in results]


def verdict_checks(root=ROOT):
    payload = root/'reproduction/payload'
    core = load('contract_audit_core', payload/'eval_core_v5/run_eval.py')
    fixtures = {
        'supply': payload/'eval_core_v3/runs/supply/cs01_control/native/result.json',
        'load': payload/'capload_case_v1/evaluations/reference_compiled_01/result.json',
        'tia': payload/'tia_case_v1/evaluations/reference_rg5000_refined01/result.json'
    }
    original = {'supply': 'analog_supply_pilot_v1/public_v2', 'load': 'capload_case_v1/public',
                'tia': 'tia_case_v1/public'}
    rows = []
    def probe(task, label, path, value, expected):
        baseline = read(fixtures[task])
        for point in range(len(baseline[path[0]])):
            data = deepcopy(baseline)
            location = list(path)
            location[1] = point
            target = data
            for key in location[:-1]:
                target = target[key]
            target[location[-1]] = value
            result = core.assess(task, data, read(payload/original[task]/'contract.json'))
            require(result.get('category') == ('pass' if expected else 'specification_failure'),
                    f'{task}: unexpected boundary verdict for {label}, point {point+1}: {result.get("category")}')
            rows.append({'task': task, 'point': point+1, 'probe': label,
                         'expected_pass': expected, 'category': result['category']})
    for task, path in fixtures.items():
        require(core.assess(task, read(path), read(payload/original[task]/'contract.json'))['success'],
                'Reference failed: '+task)
    supply = read(payload/original['supply']/'contract.json')
    for metric, rule in supply['limits'].items():
        operator, limit = next(iter(rule.items()))
        path = ['points', 0, 'command_tracking' if metric.startswith('command_') else 'metrics',
                metric.removeprefix('command_')]
        delta = max(abs(limit)*1e-6, 1e-6)
        probe('supply', metric+'_at_limit', path, limit, True)
        probe('supply', metric+'_outside', path, limit-delta if operator == '>=' else limit+delta, False)
    load_contract = read(payload/original['load']/'contract.json')['limits']
    probe('load', 'phase_margin_at_limit', ['cases', 0, 'ac', 'phase_margins_deg'],
          [load_contract['all_downward_unity_crossing_phase_margins_deg_min']], True)
    probe('load', 'phase_margin_outside', ['cases', 0, 'ac', 'phase_margins_deg'], [49.999], False)
    probe('load', 'power_at_limit', ['cases', 0, 'ac', 'dc_power_uW'], load_contract['dc_supply_power_uW_max'], True)
    probe('load', 'zero_power', ['cases', 0, 'ac', 'dc_power_uW'], 0, False)
    probe('load', 'power_outside', ['cases', 0, 'ac', 'dc_power_uW'], 350.001, False)
    probe('load', 'phase_90', ['cases', 0, 'ac', 'phase_at_low_frequency_deg'], 90, False)
    probe('load', 'phase_below_90', ['cases', 0, 'ac', 'phase_at_low_frequency_deg'], 89.999, True)
    tia = read(payload/original['tia']/'contract.json')['limits']
    for value, expected in [(-10100, True), (-9900, True), (-10100.001, False), (-9899.999, False)]:
        probe('tia', 'real_transfer_'+str(value), ['cases', 0, 'ac', 'dc_transimpedance_real_ohm'], value, expected)
    for field, good, bad in [('dc_transimpedance_imag_ohm', 1, 1.000001),
                             ('first_minus_3dB_Hz', 1e6, 999999),
                             ('dc_delivered_power_uW', 300, 300.001),
                             ('low_frequency_loop_gain_dB', .001, 0),
                             ('phase_at_low_frequency_deg', 89.999, 90)]:
        probe('tia', field+'_boundary', ['cases', 0, 'ac', field], good, True)
        probe('tia', field+'_outside', ['cases', 0, 'ac', field], bad, False)
    probe('tia', 'zero_power', ['cases', 0, 'ac', 'dc_delivered_power_uW'], 0, False)
    probe('tia', 'phase_margin_at_limit', ['cases', 0, 'ac', 'phase_margins_deg'], [55], True)
    probe('tia', 'phase_margin_outside', ['cases', 0, 'ac', 'phase_margins_deg'], [54.999], False)
    probe('tia', 'initial_error_at_limit', ['cases', 0, 'transient', 'initial_error_V'], .001, True)
    probe('tia', 'initial_error_outside', ['cases', 0, 'transient', 'initial_error_V'], .001001, False)
    for task in ['load', 'tia']:
        contract = load_contract if task == 'load' else tia
        unit = 'us' if task == 'load' else 'ns'
        limit = contract['settle_us_max_each_of_four_edges'] if task == 'load' else contract['each_edge_settle_max_ns']
        for edge in range(4):
            path = ['cases', 0, 'transient', 'edges', edge]
            probe(task, f'edge{edge+1}_settling_at_limit', path+['settle_'+unit], limit, True)
            probe(task, f'edge{edge+1}_settling_outside', path+['settle_'+unit], limit+.0001, False)
            probe(task, f'edge{edge+1}_overshoot_at_limit', path+['overshoot_V'], .01, True)
            probe(task, f'edge{edge+1}_overshoot_outside', path+['overshoot_V'], .010001, False)
    return rows


def audit(root=ROOT):
    packets = packet_checks(root)
    declarations = declaration_checks(root)
    precision = precision_checks(root)
    syntax = syntax_checks(root)
    verdicts = verdict_checks(root)
    return {'outcome': 'passed', 'packet_revision': read(root/'tasks/catalog.json')['default_revision'],
            'evaluator': 'reproduction/payload/eval_core_v5/run_eval.py',
            'packets': packets, 'declarations': declarations, 'precision_checks': precision,
            'syntax_checks': syntax, 'verdict_checks': verdicts,
            'declared_requirements_checked': len(declarations),
            'precision_checks_passed': len(precision),
            'syntax_checks_passed': len(syntax), 'verdict_checks_passed': len(verdicts),
            'model_calls': 0, 'simulator_calls': 0,
            'scope': 'Input/compiler and saved-measurement boundary checks; not expert agreement or new model trials'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Optional new JSON receipt; never overwrite a prior receipt')
    args = parser.parse_args()
    result = audit()
    if args.out:
        with args.out.open('x', encoding='utf-8') as handle:
            json.dump(result, handle, indent=2, allow_nan=False)
            handle.write('\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in {'declarations', 'syntax_checks', 'verdict_checks'}}, indent=2))
