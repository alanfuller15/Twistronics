"""Reproduce two v078p software-boundary defects using synthetic measurements.

This is a pinned baseline observation suite, NOT a corrected-package acceptance
gate. Exit zero means the documented baseline behavior was reproduced. No
discovery, Hamiltonian diagonalization, frame transport or charge measurement is
run. The preserved consumer source is never modified.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'migration_contract_review'
ARCHIVE_SHA = 'd703b6c027d5725ed173c69d221f450a34922e46d1320350ab1c08e3448c545e'
BASELINE_COMMIT = '44dc66951057a995ee0999c785aca3e0e6c67092'
MODES = ('matching_plan', 'plan_N', 'plan_eps', 'existing_success', 'existing_abort')
ABORT_MESSAGE = 'synthetic constructor failure after Run initialization'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def inventory(path):
    return {p.name: {'bytes': p.stat().st_size, 'sha256': sha(p)}
            for p in sorted(path.iterdir()) if p.is_file()}


def worker(work, mode):
    # Each worker has its own freshly extracted package and process globals.
    os.chdir(work)
    sys.path.insert(0, str(work))
    plan_path = work / 'PLAN_MIGRATION.json'
    original_plan = json.loads(plan_path.read_text())
    plan = json.loads(plan_path.read_text())
    mutations = {'plan_N': ('N', 5), 'plan_eps': ('eps', 0.004)}
    if mode in mutations:
        key, value = mutations[mode]
        plan['model_defaults'][key] = value
        write_json(plan_path, plan)

    import numpy as np
    import scipy
    import migrated_valley_control as mv

    out = work / 'OUT'
    before_contents = {}
    if mode.startswith('existing_'):
        out.mkdir()
        before_contents = {
            'ROWS.jsonl': '{"synthetic_prior_row":"retain-me"}\n',
            'DIAGNOSTICS.jsonl': '{"synthetic_prior_diagnostic":"retain-me"}\n',
            'SUMMARY.json': '{"run_status":"SYNTHETIC_PRIOR"}\n',
        }
        for name, content in before_contents.items():
            (out / name).write_text(content)
    before = inventory(out) if out.exists() else {}
    calls = []
    original_BM = mv.BM

    def observed_BM(*args, **kwargs):
        calls.append({
            'args_count': len(args),
            'defaults': {k: kwargs.get(k) for k in plan['model_defaults']},
            'valley': kwargs.get('valley'),
            'frozen_index_count': len(kwargs['index_set']) if 'index_set' in kwargs else None,
        })
        if mode == 'existing_abort':
            raise RuntimeError(ABORT_MESSAGE)
        return original_BM(*args, **kwargs)

    mv.BM = observed_BM
    measurements = []

    def synthetic_measure(sampler, geometry):
        measurements.append(sampler.name)
        # Same normal-return shape as the baseline; no ledger diagnostics or
        # actual measurements. These invented values have no scientific meaning.
        return dict(label='SAME', windings=[1., 1.], node_gaps_meV=[0., 0.],
                    lo=sampler.m.dim // 2 - 1, status='PASSED_SAMPLED_GATES')

    exception = None
    try:
        rc = mv.main(str(out), discovery=lambda model: [np.array([.3, .4]),
                     np.array([.6, .6])], measure=synthetic_measure)
    except Exception as exc:
        exception = {'type': type(exc).__name__, 'message': str(exc)}
        traceback.print_exc()
        rc = 1

    rows = [json.loads(line) for line in (out / 'ROWS.jsonl').read_text().splitlines()]
    models = json.loads((out / 'MODELS.json').read_text()) if (out / 'MODELS.json').exists() else {}
    observation = {
        'mode': mode, 'synthetic_only': True, 'returncode': rc,
        'exception': exception,
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
        'source_sha256': {name: sha(work / name) for name in mv.SRC},
        'original_plan_defaults': original_plan['model_defaults'],
        'declared_plan_defaults': plan['model_defaults'],
        'constructor_calls': calls, 'synthetic_measurement_cases': measurements,
        'model_record_defaults': {key: rec['defaults'] for key, rec in models.items()},
        'expected_cases': [c['case_id'] for c in plan['expected_cases']],
        'rows': rows,
        'summary': json.loads((out / 'SUMMARY.json').read_text()),
        'before_contents': before_contents, 'before_files': before,
        'after_files': inventory(out),
        'after_prior_file_contents': {name: (out / name).read_text() for name in before_contents},
        'limitations': 'Synthetic discovery and measure; real constructor/geometry only. No scientific gate result.',
    }
    write_json(work / 'OBSERVATION.json', observation)
    return rc


def evaluate(mode, rc, obs, trusted_sources):
    """Return explicit failed predicates; never equate a refusal with success."""
    checks = {}
    checks['current_observation'] = (obs.get('mode') == mode and obs.get('synthetic_only') is True)
    checks['exit_matches_observation'] = (type(obs.get('returncode')) is int and obs['returncode'] == rc)
    source = obs.get('source_sha256', {})
    checks['unchanged_executed_sources'] = all(source.get(k) == v for k, v in trusted_sources.items())
    if mode == 'existing_abort':
        checks['specific_injected_exception'] = (rc == 1 and obs.get('exception') ==
                {'type': 'RuntimeError', 'message': ABORT_MESSAGE})
        checks['one_constructor_no_measurements'] = (len(obs['constructor_calls']) == 1 and
                                                     obs['synthetic_measurement_cases'] == [])
        checks['rows_and_diagnostics_truncated'] = all(
            obs['before_files'][name]['bytes'] > 0 and obs['after_files'][name]['bytes'] == 0
            for name in ('ROWS.jsonl', 'DIAGNOSTICS.jsonl'))
        checks['prior_summary_left_unchanged'] = (obs['summary'] == {'run_status': 'SYNTHETIC_PRIOR'} and
            obs['before_files']['SUMMARY.json'] == obs['after_files']['SUMMARY.json'])
    else:
        checks['consumer_returned_complete'] = (rc == 0 and obs.get('exception') is None and
                                                obs['summary']['run_status'] == 'COMPLETE')
        expected = obs['expected_cases']
        checks['eight_unique_synthetic_cases'] = (len(expected) == len(set(expected)) == 8 and
            obs['synthetic_measurement_cases'] == expected and
            [r['case_id'] for r in obs['rows']] == expected and
            all(r['status'] == 'ACCEPTED' and r['gate_status'] == 'PASSED_SAMPLED_GATES' for r in obs['rows']))
        checks['eleven_real_constructor_calls'] = len(obs['constructor_calls']) == 11
        checks['constructors_used_baseline_defaults'] = all(
            call['args_count'] == 0 and call['defaults'] == obs['original_plan_defaults']
            for call in obs['constructor_calls'])
        checks['ten_model_records_used_baseline_defaults'] = (len(obs['model_record_defaults']) == 10 and all(
            {k: value[k] for k in obs['original_plan_defaults']} == obs['original_plan_defaults']
            for value in obs['model_record_defaults'].values()))
        if mode in ('plan_N', 'plan_eps'):
            key, new_value = {'plan_N': ('N', 5), 'plan_eps': ('eps', 0.004)}[mode]
            expected_plan = dict(obs['original_plan_defaults'], **{key: new_value})
            checks['exact_single_plan_mutation'] = obs['declared_plan_defaults'] == expected_plan
            checks['mutated_plan_hash_recorded'] = (obs['summary']['plan_sha256'] == source['PLAN_MIGRATION.json'])
            checks['declared_value_not_used'] = all(call['defaults'][key] != new_value for call in obs['constructor_calls'])
        else:
            checks['unmutated_plan'] = obs['declared_plan_defaults'] == obs['original_plan_defaults']
        if mode == 'existing_success':
            checks['all_three_prior_files_replaced'] = all(
                obs['before_files'][name] != obs['after_files'][name] and
                obs['after_prior_file_contents'][name] != content
                for name, content in obs['before_contents'].items())
    return {'checks': checks, 'failed': [k for k, v in checks.items() if not v],
            'baseline_observation_reproduced': all(checks.values())}


def main(output):
    if not __debug__:
        raise RuntimeError('Run without -O: the preserved extractor uses assertions')
    if sha(BASE / 'partner_v078p.zip') != ARCHIVE_SHA:
        raise RuntimeError('Wrong baseline archive')
    sys.path.insert(0, str(BASE))
    from review_inputs import extract
    # Refuse to overwrite a prior observation suite, including partially finished runs.
    output.mkdir(parents=True, exist_ok=False)
    input_manifest = json.loads((BASE / 'INPUT_MANIFEST.json').read_text())
    outcomes = {}
    for mode in MODES:
        dest = output / mode
        dest.mkdir()
        with tempfile.TemporaryDirectory(prefix='twistronics-boundary-') as temp:
            work = extract(Path(temp) / 'source', source_only=True)
            command = [sys.executable, str(Path(__file__).resolve()), '--worker', str(work), '--mode', mode]
            result = subprocess.run(command, cwd=work, text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, timeout=60,
                                    env=dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1'))
            (dest / 'STDOUT.log').write_text(result.stdout)
            (dest / 'STDERR.log').write_text(result.stderr)
            observation_path = work / 'OBSERVATION.json'
            if not observation_path.exists():
                outcomes[mode] = {'returncode': result.returncode, 'failed': ['missing current observation'],
                                  'baseline_observation_reproduced': False}
                continue
            observation = json.loads(observation_path.read_text())
            (dest / 'OBSERVATION.json').write_bytes(observation_path.read_bytes())
            # Independently verify every source named by the consumer except the
            # deliberately mutable plan. It must match the original archive.
            trusted = {k: input_manifest['files'][k]['sha256'] for k in
                       ('guarded_topology.py', 'guarded_sparse.py', 'migrated_valley_control.py',
                        'response_inputs.py', 'partner_v074p.zip')}
            outcomes[mode] = dict(returncode=result.returncode,
                                 **evaluate(mode, result.returncode, observation, trusted))
        print(mode + ': ' + json.dumps(outcomes[mode]))
    original_unchanged = sha(BASE / 'partner_v078p.zip') == ARCHIVE_SHA
    success = original_unchanged and all(o['baseline_observation_reproduced'] for o in outcomes.values())
    write_json(output / 'RECEIPT.json', {
        'baseline_commit': BASELINE_COMMIT, 'archive_sha256': ARCHIVE_SHA,
        'probe_sha256': sha(__file__), 'extractor_sha256': sha(BASE / 'review_inputs.py'),
        'original_archive_unchanged': original_unchanged, 'cases': outcomes,
        'all_baseline_observations_reproduced': success,
        'meaning_of_exit_zero': 'Pinned baseline behaviors reproduced, including defects; NOT correction acceptance.',
        'scientific_results': False,
        'artifacts': {str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*')) if p.is_file()},
    })
    return 0 if success else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--worker', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--mode', choices=MODES, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        sys.exit(worker(args.worker.resolve(), args.mode))
    if args.output is None:
        parser.error('--output must name a new directory')
    sys.exit(main(args.output.resolve()))
