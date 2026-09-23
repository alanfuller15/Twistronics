"""Reconstruct reported quantities from retained records, without solver imports."""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def reconcile(root=ROOT):
    root = Path(root)
    result = json.loads((root/'RESULTS.json').read_text())
    plan = json.loads((root/'PLAN.json').read_text())
    if result['plan_sha256'] != sha(root/'PLAN.json'):
        raise RuntimeError('plan changed since execution')
    for file, digest in result['sources'].items():
        if sha(root/file) != digest: raise RuntimeError('executed source changed: '+file)
    rows = defaultdict(list)
    with gzip.open(root/'EVALUATIONS.jsonl.gz', 'rt') as f:
        for line in f:
            record = json.loads(line); rows[record['attempt_id']].append(record)
    with gzip.open(root/'PATHS.json.gz', 'rt') as f: paths = json.load(f)
    counts = Counter(r['kind'] for rs in rows.values() for r in rs)
    frame_error = 0.; winding_error = 0.; wilson_error = 0.
    for outcome in result['outcomes']:
        kind, status = outcome['kind'], outcome['result']['status']
        if kind == 'sparse': continue
        data = rows[outcome['id']]
        frames = [x for x in data if x['kind'] == 'frame']
        links = [x for x in data if x['kind'] == 'link']
        if len(frames) != outcome['diagnostics']['frame_evaluations']: raise RuntimeError('frame count mismatch')
        for r in frames:
            w = r['energies_meV']; j = r['lo']-r['first_band']; n = r['n']
            lower = w[j]-w[j-1] if j else None
            upper = w[j+n]-w[j+n-1] if j+n < len(w) else None
            for actual, recorded in [(lower, r['lower_external_gap_meV']), (upper, r['upper_external_gap_meV'])]:
                if actual is None:
                    if recorded is not None: raise RuntimeError('external gap applicability mismatch')
                else: frame_error = max(frame_error, abs(actual-recorded))
        if status != 'PASSED_SAMPLED_GATES': continue
        if any(x['kind'] == 'rejection' for x in data): raise RuntimeError('accepted rejected attempt')
        if any(r['external_gap_meV'] is not None and r['external_gap_meV'] < plan['policy']['external_gap_meV'] for r in frames):
            raise RuntimeError('accepted inadequate external gap')
        if any(r['min_overlap'] < plan['policy']['overlap_min'] for r in links): raise RuntimeError('accepted unresolved overlap')
        if any(r['sewing'] and r['sewing_loss'] > plan['policy']['sewing_loss_max'] for r in links): raise RuntimeError('accepted inadequate sewing')
        if kind == 'pair':
            for j, w in enumerate(outcome['result']['windings']):
                total = sum(x['step_rad'] for x in data if x['kind'] == 'angle' and x['where'] == f'loop:{j}')/np.pi
                winding_error = max(winding_error, abs(total-w))
            roots = [x for x in frames if x['where'].startswith('node:')]
            if len(roots) != 2: raise RuntimeError('missing evaluated root')
            for x, gap in zip(roots, outcome['result']['node_gaps_meV']):
                j = x['lo']-x['first_band']; native_gap = x['energies_meV'][j+1]-x['energies_meV'][j]
                if abs(native_gap-gap) > 1e-12 or native_gap > plan['policy']['root_gap_meV']: raise RuntimeError('root gap mismatch')
        if kind == 'wilson':
            phases = [r for r in data if r['kind'] == 'wilson_phases']
            if len(phases) != 1: raise RuntimeError('missing Wilson phases')
            wind = float((np.unwrap(phases[0]['phases_rad'])[-1]-phases[0]['phases_rad'][0])/(2*np.pi))
            wilson_error = max(wilson_error, abs(wind-outcome['result']['euler_estimate']))
            for axis in (1, 2):
                if not any(r['sewing'] and r['where'].startswith(f'sewing{axis}:') for r in links): raise RuntimeError('missing sewing direction')
    for name, g in paths.items():
        for key in ('nodes', 'loops', 'transport'):
            if not np.array_equal(g['Kprime'][key], -np.asarray(g['K'][key])): raise RuntimeError('not an exact path mirror')
        for valley in ('K', 'Kprime'):
            if not np.array_equal(g[valley]['transport'][0], g[valley]['loops'][0][0]) or not np.array_equal(g[valley]['transport'][-1], g[valley]['loops'][1][0]):
                raise RuntimeError('base path mismatch')
    refinements = []
    for B in plan['braid']['B']:
        for valley in (1, -1):
            rr = [r for r in result['outcomes'] if r['kind'] == 'pair' and r['B'] == B and r['valley'] == valley]
            complete = len(rr) == 4 and all(r['result']['status'] == 'PASSED_SAMPLED_GATES' for r in rr)
            spread = float(np.ptp(np.abs([r['result']['windings'] for r in rr]), axis=0).max()) if complete else None
            refinements.append(dict(kind='loop_radius_and_mesh', B=B, valley=valley, count=len(rr), maximum_abs_winding_spread=spread,
                                    passed=bool(complete and len(set(r['result']['label'] for r in rr)) == 1 and spread <= plan['braid']['refinement_abs_winding_tol'])))
    for name in sorted(set(r['model'] for r in result['outcomes'] if r['kind'] == 'wilson')):
        rr = [r for r in result['outcomes'] if r['kind'] == 'wilson' and r['model'] == name]
        ok = len(rr) == 2 and all(r['result']['status'] == 'PASSED_SAMPLED_GATES' for r in rr)
        diff = abs(abs(rr[0]['result']['euler_estimate'])-abs(rr[1]['result']['euler_estimate'])) if ok else None
        refinements.append(dict(kind='wilson_mesh', model=name, comparable=ok, absolute_estimate_difference=diff,
                                same_integer_magnitude=bool(ok and abs(rr[0]['result']['nearest_integer']) == abs(rr[1]['result']['nearest_integer']))))
    for name in sorted(set(r['model'] for r in result['outcomes'] if r['kind'] == 'sign')):
        for band in ('flat1', 'flat2'):
            for axis in (0, 1):
                rr = [r for r in result['outcomes'] if r['kind'] == 'sign' and r['model'] == name and r['band_label'] == band and r['axis'] == axis]
                ok = len(rr) == 2 and all(r['result']['status'] == 'PASSED_SAMPLED_GATES' for r in rr)
                refinements.append(dict(kind='sign_mesh', model=name, band=band, axis=axis,
                                        passed=bool(ok and rr[0]['result']['sign'] == rr[1]['result']['sign'])))
    sparse_checks = []
    for name in sorted(set(r['model'] for r in result['outcomes'] if r['kind'] == 'sparse')):
        data = rows[name]
        for a in [r for r in data if r['kind'] == 'accepted']:
            records = [r for r in data if r.get('attempt') == a['attempt']]
            checked = {r['name'] for r in records if r['kind'] == 'check' and r['passed']}
            expected = {'native_matrix_tol_meV', 'ordered_energy_tol_meV', 'residual_tol_meV', 'orthogonality_tol', 'projector_tol'}
            if not expected <= checked: raise RuntimeError('missing accepted sparse gate')
            if sum(r['kind'] == 'component' and r['name'] == 'native_dense_eigh' and r['status'] == 'COMPLETED' for r in records) != 1:
                raise RuntimeError('accepted without exactly one native dense solve')
            sparse_checks.extend(r for r in records if r['kind'] == 'check')
    tests = ET.parse(root/'TESTS.xml').getroot()
    cases = tests.findall('.//testcase')
    summary = dict(plan_sha256=sha(root/'PLAN.json'), inputs={f: sha(root/f) for f in ['RESULTS.json', 'EVALUATIONS.jsonl.gz', 'PATHS.json.gz', 'TESTS.xml']},
                   tests=dict(count=len(cases), failures=len(tests.findall('.//failure')), errors=len(tests.findall('.//error'))),
                   outcome_counts={kind: dict(Counter(r['result']['status'] for r in result['outcomes'] if r['kind'] == kind)) for kind in ('pair', 'wilson', 'sign', 'sparse')},
                   ledger_counts=dict(counts), external_gap_reconstruction_error_meV=frame_error, winding_reconstruction_error=winding_error,
                   wilson_reconstruction_error=wilson_error, refinements=refinements, mirror_checks=result['checks'],
                   sparse_accepted_max_checks={name: max(r['value'] for r in sparse_checks if r['name'] == name) for name in sorted(set(r['name'] for r in sparse_checks))},
                   archive_unchanged=sha(root/'partner_v074p.zip') == 'be296d77d1051909d04fa91bcff0374bcd1d3f05f9783e6b3c37885f0188f163')
    if max(frame_error, winding_error, wilson_error) > 1e-10: raise RuntimeError('record reconstruction mismatch')
    (root/'SUMMARY.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == '__main__': reconcile()
