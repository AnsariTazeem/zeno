"""Plot the recorded repeat's final rising edge. Requires NumPy and matplotlib."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--entry-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root = args.entry_root.resolve()
    args.out.mkdir(parents=True, exist_ok=False)
    os.environ['MPLCONFIGDIR'] = str(args.out / 'mpl_cache')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    measure = Path(__file__).resolve().parent.parent / 'reproduction/payload/analog_public_v1/strict_measure.py'
    spec = importlib.util.spec_from_file_location('frozen_tracking', measure)
    tracking = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tracking)
    rows = [row for row in read(root / 'results/catalog.json')['evaluations']
            if row['trial_id'] == 'supply_v4_repeat_recovered' and row['profile'] == 'refined']
    assert len(rows) == 1
    row = rows[0]
    relative = Path(row['native_result_in_entry_archive'])
    if relative.is_absolute() or relative.drive or '..' in relative.parts:
        raise ValueError('Native result path escapes the entry root')
    result_path = (root / relative).resolve()
    if not result_path.is_relative_to(root):
        raise ValueError('Native result path escapes the entry root')
    assert sha(result_path) == row['native_result_sha256']
    result = read(result_path)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.8), sharex=True)
    fig.subplots_adjust(left=.10, right=.97, top=.87, bottom=.15, hspace=.30)
    fig.suptitle('SUPPLY repeat: final rising-step response', x=.10, ha='left', fontsize=17, fontweight='bold')
    fig.text(.10, .91, 'Finer simulation | TT, 27 C | 0.8 to 1.0 V command | 1 pF load', fontsize=10)
    sources = []
    for point, label, color in zip(sorted(result['points'], key=lambda item: item['vdd']),
                                   ['v115', 'v120', 'v125'], ['#0072B2', '#D55E00', '#009E73']):
        trace = result_path.parent / 'eval/opamp_2stg' / label / 'opamp_tran/tran.txt'
        metrics = tracking.follower_metrics(trace)
        assert metrics == point['command_tracking']
        data = tracking.load_trace(trace)
        mask = (data['time'] >= 5e-9 - 1e-15) & (data['time'] < 55e-9 - 1e-15)
        elapsed = (data['time'][mask] - 5e-9) * 1e9
        voltage = data['v(nout)'][mask]
        axes[0].plot(elapsed, voltage, color=color, label=f"{point['vdd']:.2f} V supply", lw=1.5)
        axes[1].plot(elapsed, (voltage - 1) * 1000, color=color, lw=1.5)
        sources.append({'trace_in_entry': trace.relative_to(root).as_posix(), 'sha256': sha(trace),
                        'vdd': point['vdd'], 'rise_settle_ns': metrics['rise_settle_ns']})
    axes[0].axhline(1, color='#555555', ls=':', lw=1)
    axes[0].set_ylabel('Output (V)')
    axes[0].set_title('Full rising response', loc='left', fontsize=11)
    axes[0].legend(loc='lower right', fontsize=10)
    axes[1].axhspan(-2, 2, color='#dcefe1')
    axes[1].axhline(0, color='#777777', lw=.7)
    axes[1].set_ylim(-10, 10)
    axes[1].set_ylabel('Output error (mV)')
    axes[1].set_xlabel('Time since rising edge (ns)')
    axes[1].set_title('Error zoom: +/-2 mV band; errors beyond +/-10 mV are clipped here', loc='left', fontsize=11)
    axes[1].text(13, 8.5, '12.24 ns deadline', fontsize=10)
    for axis in axes:
        axis.axvline(12.24, color='#444444', ls='--', lw=1)
        axis.set_xlim(0, 50)
        axis.grid(alpha=.18)
    fig.text(.10, .055, 'Pass requires entering the band by the deadline and staying inside through the rest of this edge window.\n'
             'Simulation only. This chart covers the rising check; the full task also grades other electrical requirements.', fontsize=9)
    figure = args.out / 'supply_repeat_rising.png'
    fig.savefig(figure, dpi=180, facecolor='white')
    plt.close(fig)
    metadata = {'catalog_key': row['key'], 'native_result_sha256': sha(result_path), 'sources': sources,
                'measurement_code_sha256': sha(measure), 'plot_code_sha256': sha(Path(__file__)),
                'figure_sha256': sha(figure), 'matplotlib': matplotlib.__version__, 'numpy': np.__version__,
                'model_calls': 0, 'simulator_calls': 0, 'deadline_ns': 12.24, 'error_band_mV': 2}
    with (args.out / 'supply_repeat_rising.json').open('x', encoding='utf-8') as stream:
        json.dump(metadata, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'figure': str(figure), 'raw_traces_rechecked': len(sources)}))


if __name__ == '__main__':
    main()
