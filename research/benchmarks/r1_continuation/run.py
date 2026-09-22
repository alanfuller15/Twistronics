"""Frozen local continuation run. Preserve failed cells and endpoint joins."""
import itertools
import json
import platform
import sys
import time
import traceback
import numpy as np
import scipy
from scipy.linalg import eigh
from bounds import ROOT, PLAN, CFG, sha, center_data, certificate, containment, separation

sys.path.insert(0, str(ROOT.parent/'r1_newton'))
from solver import solve
sys.path.insert(0, str(ROOT.parent/'r1_holonomy'))
from measure import Family
from track import model

def main():
    dest = ROOT/'RESULTS.json'
    if dest.exists():
        raise SystemExit('Refusing overwrite of retained production results')
    controls = json.loads((ROOT/'CONTROLS.json').read_text())
    assert controls['all_controls_pass'] and controls['plan_sha256'] == sha(ROOT/'PLAN.json')
    assert all(sha(ROOT/n) == h for n, h in controls['source_hashes'].items())
    sources = [ROOT/n for n in ['PLAN.json', 'bounds.py', 'controls.py', 'CONTROLS.json', 'run.py']]
    parent = json.loads((ROOT.parent/'r1_newton'/'SUMMARY.json').read_text())
    assert parent['status'] == 'RECONCILED_GUARDED_NEWTON_VARIANT_PASS'
    assert all(sha(ROOT.parent/'r1_newton'/n) == h for n, h in parent['source_hashes'].items())
    sources += [ROOT.parent/'r1_newton'/n for n in ['SUMMARY.json', 'solver.py', 'PLAN.json']]
    sources += [ROOT.parent/'r1_holonomy'/n for n in ['measure.py', 'PLAN.json']]
    for engine in PLAN['engines']:
        p = ROOT.parent/'r1_holonomy'/(engine.upper()+'.json')
        d = json.loads(p.read_text())
        assert all(sha(ROOT.parent/n) == h for n, h in d['source_hashes'].items())
        sources += [p]+[ROOT.parent/n for n in d['source_hashes']]
    out = {'status': 'RUNNING', 'plan_sha256': sha(ROOT/'PLAN.json'),
           'source_hashes': {str(p.relative_to(ROOT.parent)): sha(p) for p in sorted(set(sources))},
           'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__, 'blas_threads': 1},
           'families': [], 'centers': {}, 'campaigns': [], 'errors': []}
    frames = {}
    def save():
        dest.write_text(json.dumps(out, indent=2, allow_nan=False)+'\n')
        np.savez_compressed(ROOT/'FRAMES.npz', **frames)
    save()
    try:
        for engine in PLAN['engines']:
            family = Family(engine)
            out['families'].append({'engine': engine, 'dimension': family.dim, 'affine_checks': family.checks})
            stations = json.loads((ROOT.parent/'r1_holonomy'/(engine.upper()+'.json')).read_text())['tracks']['16']['stations']
            native_cache = {}
            started = time.perf_counter()
            def get_center(node, D):
                key = f'{engine}_{node}_{D:.12f}'
                if key in out['centers']:
                    return key, out['centers'][key]
                k = PLAN['nodes'].index(node)
                seed = np.array([np.interp(D, [s['D_meV'] for s in stations], [s['roots'][k]['f'][j] for s in stations]) for j in range(2)])
                lo = family.lo+int(node == 'upper')
                radius = PLAN['root_seed_box_radius']
                root = solve(family, D, lo, seed, box=[np.maximum(seed-radius, 0), np.minimum(seed+radius, 1)])
                record = {'engine': engine, 'node': node, 'D_meV': D, 'root': root, 'pass': False}
                out['centers'][key] = record
                if not root['accepted']:
                    record['failure'] = 'center_root_rejected'
                    return key, record
                raw, F = center_data(family, D, lo, root['f'])
                frames[key] = F
                if D not in native_cache:
                    native_cache[D] = model(engine, PLAN['N'], D)
                native = native_cache[D].H(family.k(np.array(root['f'])))
                matrix_error = float(np.max(np.abs(family.U.conj().T @ native @ family.U-family.H([*root['f'], D]))))
                w = eigh(native, eigvals_only=True, subset_by_index=(lo-1, lo+2))
                spectrum_error = float(np.max(np.abs(w-raw['w4'])))
                record.update(raw=raw, native={'w4': w.tolist(), 'gap_meV': float(w[2]-w[1]), 'matrix_error_meV': matrix_error, 'spectrum_error_meV': spectrum_error})
                record['pass'] = bool(matrix_error <= CFG['matrix_tolerance_meV'] and spectrum_error <= CFG['native_spectrum_tolerance_meV'] and w[2]-w[1] <= CFG['native_spectrum_tolerance_meV'] and raw['inertia_correct'])
                if not record['pass']:
                    record['failure'] = 'native_or_inertia_check'
                return key, record

            for initial in PLAN['initial_intervals']:
                campaign = {'engine': engine, 'initial_intervals': initial, 'nodes': {}, 'separations': []}
                out['campaigns'].append(campaign)
                for node in PLAN['nodes']:
                    path = {'attempts': [], 'leaf_ids': [], 'points': [], 'joins': []}
                    campaign['nodes'][node] = path
                    def visit(a, b, depth, parent_id=None):
                        key, center = get_center(node, (a+b)/2)
                        cert = certificate(center['raw'], (b-a)/2) if center['pass'] else {'pass': False, 'reason': center.get('failure', 'center_failed')}
                        idx = len(path['attempts'])
                        rec = {'id': idx, 'parent': parent_id, 'a': a, 'b': b, 'depth': depth, 'center': key, 'certificate': cert, 'children': []}
                        path['attempts'].append(rec)
                        if cert['pass'] or depth >= PLAN['max_bisection_depth']:
                            path['leaf_ids'].append(idx)
                        else:
                            mid = (a+b)/2
                            rec['children'] = [visit(a, mid, depth+1, idx), visit(mid, b, depth+1, idx)]
                        return idx
                    grid = np.linspace(*PLAN['D_interval_meV'], initial+1)
                    for a, b in zip(grid[:-1], grid[1:]):
                        visit(float(a), float(b), 0)
                    leaves = [path['attempts'][i] for i in path['leaf_ids']]
                    for D in sorted({v for c in leaves for v in [c['a'], c['b']]}):
                        key, point = get_center(node, D)
                        pc = certificate(point['raw'], 0) if point['pass'] else {'pass': False, 'reason': point.get('failure', 'point_failed')}
                        path['points'].append({'D_meV': D, 'center': key, 'certificate': pc})
                        for cell in leaves:
                            if D not in [cell['a'], cell['b']]:
                                continue
                            cc = out['centers'][cell['center']]
                            join = containment(point['raw'], pc, cc['raw'], cell['certificate'], D) if point['pass'] and cc['pass'] else {'pass': False, 'reason': 'center_failed'}
                            path['joins'].append({'D_meV': D, 'point_center': key, 'cell': cell['id'], **join})
                    path['pass'] = bool(all(c['certificate']['pass'] for c in leaves) and all(p['certificate']['pass'] for p in path['points']) and all(j['pass'] for j in path['joins']))
                    save()
                    print('PATH', engine, initial, node, 'attempts', len(path['attempts']), 'leaves', len(leaves), 'joins', len(path['joins']), 'pass', path['pass'], 'seconds', round(time.perf_counter()-started, 1), flush=True)
                for n1, n2 in itertools.combinations(PLAN['nodes'], 2):
                    p1, p2 = campaign['nodes'][n1], campaign['nodes'][n2]
                    for i in p1['leaf_ids']:
                        for j in p2['leaf_ids']:
                            c1, c2 = p1['attempts'][i], p2['attempts'][j]
                            a, b = max(c1['a'], c2['a']), min(c1['b'], c2['b'])
                            if a >= b:
                                continue
                            if c1['certificate']['pass'] and c2['certificate']['pass']:
                                sep = separation(out['centers'][c1['center']]['raw'], c1['certificate'], out['centers'][c2['center']]['raw'], c2['certificate'], a, b)
                            else:
                                sep = {'pass': False, 'reason': 'unaccepted_tube'}
                            campaign['separations'].append({'nodes': [n1, n2], 'cells': [i, j], 'a': a, 'b': b, **sep})
                campaign['pass'] = bool(all(p['pass'] for p in campaign['nodes'].values()) and all(s['pass'] for s in campaign['separations']))
                save()
        out['status'] = 'CONDITIONAL_LOCAL_CONTINUATION_PASS' if all(c['pass'] for c in out['campaigns']) else 'UNRESOLVED_CONTINUATION_RETAINED'
    except Exception:
        out['errors'].append(traceback.format_exc())
        out['status'] = 'UNRESOLVED_CONTINUATION_RETAINED'
        print(out['errors'][-1], flush=True)
    save()
    print('STATUS', out['status'], 'centers', len(out['centers']), flush=True)
    return 0 if out['status'] == 'CONDITIONAL_LOCAL_CONTINUATION_PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
