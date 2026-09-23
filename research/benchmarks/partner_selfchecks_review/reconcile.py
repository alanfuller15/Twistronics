"""Reconcile supplied claims with fresh producer output and raw measurement ledgers."""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np
from review_inputs import ROOT, activate
INPUT = activate()


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def leaves_compare(a, b, path=''):
    diffs = []; mismatches = []
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b): mismatches.append(dict(path=path, reason='keys differ'))
        for key in a.keys() & b.keys():
            d, m = leaves_compare(a[key], b[key], path+'/'+str(key)); diffs += d; mismatches += m
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): mismatches.append(dict(path=path, reason='length differs'))
        for i, (x, y) in enumerate(zip(a, b)):
            d, m = leaves_compare(x, y, path+'/'+str(i)); diffs += d; mismatches += m
    elif isinstance(a, (float, int)) and not isinstance(a, bool) and isinstance(b, (float, int)) and not isinstance(b, bool):
        diffs.append(dict(path=path, supplied=a, replay=b, absolute_difference=abs(a-b)))
    elif a != b: mismatches.append(dict(path=path, supplied=a, replay=b))
    return diffs, mismatches


def reconcile():
    plan = json.loads((ROOT/'PLAN.json').read_text()); manifest = json.loads((ROOT/'INPUT_MANIFEST.json').read_text())
    executions = json.loads((ROOT/'EXECUTIONS.json').read_text()); output = dict(plan_sha256=sha(ROOT/'PLAN.json'), executions=executions, producers={})
    measurement_sets = {}
    for job in plan['full_replays']:
        name = Path(job['script']).stem.upper(); outcome = next((x for x in executions if x['script'] == job['script']), None)
        if not outcome or outcome['returncode'] != 0 or not outcome['result_present']:
            output['producers'][name] = dict(status='INCOMPLETE', execution=outcome); continue
        a = json.loads((INPUT/job['output']).read_text()); b = json.loads((ROOT/('REPLAY_'+job['output'])).read_text())
        diffs, other = leaves_compare(a, b)
        run = json.loads((ROOT/f'{name}_RUN.json').read_text()); models = json.loads((ROOT/f'{name}_MODELS.json').read_text())
        if not all(run['sources'][f] == rec['sha256'] for f, rec in manifest['files'].items() if f.endswith('.py')):
            raise RuntimeError('executed source mismatch')
        bymodel = {m['model_id']: m for m in models}
        for m in models:
            if hashlib.sha256(json.dumps(m['ordered_indices'], separators=(',', ':')).encode()).hexdigest() != m['indices_json_sha256']:
                raise RuntimeError('ordered basis hash mismatch')
        bymeasurement = defaultdict(list); counts = Counter()
        with gzip.open(ROOT/f'{name}_EVALUATIONS.jsonl.gz', 'rt') as f:
            for line in f:
                row = json.loads(line); counts[row['kind']] += 1
                if row['measurement'] is not None: bymeasurement[row['measurement']].append(row)
        if dict(counts) != run['counts']: raise RuntimeError('work ledger count mismatch')
        measurements = []
        for mid, records in bymeasurement.items():
            starts = [r for r in records if r['kind'] == 'measurement_start']; returns = [r for r in records if r['kind'] == 'measurement_return']
            if len(starts) != 1 or len(returns) != 1: raise RuntimeError('unclosed measurement')
            st, re = starts[0], returns[0]; spectra = [r for r in records if r['kind'] == 'eigh']
            refinements = [r for r in records if r['kind'] == 'refine_return']
            if st['method'] == 'flat_bandwidth':
                reproduced = max(r['eigenvalues_meV'][1] for r in spectra)-min(r['eigenvalues_meV'][0] for r in spectra)
                measured = re['value']
            else:
                reproduced = min(r['returned_gap_meV'] for r in refinements); measured = re['value'][0]
                if any(not r['optimizer']['success'] for r in refinements): raise RuntimeError('rejected refiner used')
            err = abs(reproduced-measured)
            if err > 1e-10: raise RuntimeError('measurement reconstruction mismatch')
            measurements.append(dict(measurement_id=mid, model_id=st['model_id'], method=st['method'], args=st['args'], kwargs=st['kwargs'],
                                     returned_value_meV=measured, reconstructed_value_meV=reproduced, error_meV=err,
                                     eigensolves=len(spectra), refinement_returns=len(refinements)))
        output['producers'][name] = dict(status='REPRODUCED', numeric_leaves=len(diffs), max_numeric_difference=max((x['absolute_difference'] for x in diffs), default=0.),
                                          nonnumeric_mismatches=other, differences=diffs, counts=dict(counts), model_records=len(models),
                                          measurements=measurements, elapsed_s=run['elapsed_s'])
        measurement_sets[name] = (measurements, bymodel)
    if 'BASIS_DEPENDENCE_CHECK' in measurement_sets:
        measurements, models = measurement_sets['BASIS_DEPENDENCE_CHECK']; restored = []
        for row in json.loads((ROOT/'REPLAY_BASIS_DEPENDENCE.json').read_text())['rows']:
            common = row['basis'] == 'common union'
            matched = sorted([m for m in models.values() if m['parameters']['N'] == row['N'] and (m['parameters']['index_set'] is not None) == common], key=lambda m:m['parameters']['phi_deg'])
            if len(matched) != 2: raise RuntimeError('basis row model mapping incomplete')
            a, b = matched
            vals = {}
            for method, field in [('flat_bandwidth', 'd_bandwidth_meV'), ('min_remote', 'd_remote_gap_meV')]:
                selected = [next(r for r in measurements if r['model_id'] == m['model_id'] and r['method'] == method) for m in matched]
                vals[field] = abs(selected[0]['reconstructed_value_meV']-selected[1]['reconstructed_value_meV'])
                if abs(vals[field]-row[field]) > 1e-10: raise RuntimeError('table row does not match measurements')
            bases = [set(tuple(t) for t in m['ordered_indices']) for m in matched]
            restored.append(dict(N=row['N'], basis=row['basis'], model_ids=[a['model_id'], b['model_id']], basis_sizes=[len(x) for x in bases],
                                 symmetric_difference=len(bases[0] ^ bases[1]), **vals))
        output['reconstructed_basis_rows'] = restored
    if 'METAMORPHIC' in measurement_sets:
        measurements, models = measurement_sets['METAMORPHIC']; reconstructed = {}
        for common, prefix in [(False, 'native_'), (True, '')]:
            matched = sorted([m for m in models.values() if any(r['model_id'] == m['model_id'] for r in measurements) and (m['parameters']['index_set'] is not None) == common], key=lambda m:m['parameters']['phi_deg'])
            if len(matched) != 2: raise RuntimeError('MR2 model mapping incomplete')
            for method, field in [('flat_bandwidth', 'd_bandwidth_meV'), ('min_remote', 'd_remote_gap_meV')]:
                values = [next(r['reconstructed_value_meV'] for r in measurements if r['model_id'] == m['model_id'] and r['method'] == method) for m in matched]
                reconstructed[prefix+field] = abs(values[0]-values[1])
        mr2 = next(r for r in json.loads((ROOT/'REPLAY_METAMORPHIC.json').read_text()) if r['relation'].startswith('MR2'))
        if any(abs(v-mr2['values'][k]) > 1e-10 for k, v in reconstructed.items()): raise RuntimeError('MR2 row mismatch')
        output['reconstructed_MR2_values'] = reconstructed
    probes = json.loads((ROOT/'CONTRACT_PROBES.json').read_text())
    output['selfcheck_gate_findings'] = dict(supplied_lint_exit=probes['supplied_readme_lint']['returncode'], supplied_lint_findings=len(probes['supplied_readme_lint']['findings']),
        forced_failure_exit=probes['forced_metamorphic_failure']['returncode'], forced_failed_relations=[r['relation'] for r in probes['forced_metamorphic_failure']['rows'] if not r['holds']],
        generator_changed_readme=not probes['readme_generator']['unchanged'], missed_invalid_fixtures=[r['name'] for r in probes['linter_fixtures'] if r['expected_violation'] and not r['actual_findings']],
        positive_fixtures_pass=sum(not r['expected_violation'] and not r['actual_findings'] for r in probes['linter_fixtures']))
    output['sparse_samples'] = dict(attempted=len(probes['native_sparse_samples']), returned=sum(r['result']['status'] == 'RETURNED' for r in probes['native_sparse_samples']),
                                   maximum_native_energy_error_meV=max((r['result'].get('native_max_error_meV', 0.) for r in probes['native_sparse_samples']), default=None),
                                   caution='Review-time native comparison, not a mandatory comparison enforced by the bundled window routine')
    output['archive_unchanged'] = sha(ROOT/'partner_v076p.zip') == manifest['archive_sha256']
    (ROOT/'SUMMARY.json').write_text(json.dumps(output, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k not in ('producers',)}, indent=2))
    return output


if __name__ == '__main__': reconcile()
