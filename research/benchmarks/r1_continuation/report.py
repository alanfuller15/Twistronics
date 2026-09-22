"""Reconstruct retained evidence without calling production bound functions."""
import itertools
import json
import sys
import numpy as np
from scipy.linalg import eigh, qr
from bounds import ROOT, PLAN, CFG, sha
sys.path.insert(0, str(ROOT.parent/'r1_holonomy'))
from measure import Family
from track import model

def main():
    data = json.loads((ROOT/'RESULTS.json').read_text())
    frames = np.load(ROOT/'FRAMES.npz')
    assert data['plan_sha256'] == sha(ROOT/'PLAN.json')
    assert all(sha(ROOT.parent/n) == h for n, h in data['source_hashes'].items())
    controls = json.loads((ROOT/'CONTROLS.json').read_text())
    assert controls['all_controls_pass'] and controls['plan_sha256'] == data['plan_sha256']
    assert all(sha(ROOT/n) == h for n, h in controls['source_hashes'].items())
    discrepancy = {}
    def close(name, a, b, tolerance=CFG['reconciliation_tolerance']):
        err = float(np.max(np.abs(np.array(a)-np.array(b))))
        discrepancy[name] = max(discrepancy.get(name, 0.), err)
        assert np.isfinite(err) and err <= tolerance, (name, err)
    def g(M):
        return np.array([(M[0, 0]+M[1, 1])/2, (M[0, 0]-M[1, 1])/2, M[0, 1]])
    def norm(M):
        return np.linalg.norm(M, ord=2)
    native_max = {'matrix': 0., 'spectrum': 0., 'gap': 0.}
    for engine in PLAN['engines']:
        fam = Family(engine)
        A = fam.A
        norms = [float(max(abs(eigh(a, eigvals_only=True))))+CFG['norm_allowance'] for a in A[:2]]
        for key, rec in data['centers'].items():
            if rec['engine'] != engine:
                continue
            assert rec['pass'] and rec['root']['accepted']
            r = rec['raw']; F = frames[key]; Q = qr(F, mode='full')[0][:, 2:]
            W = np.column_stack([F, Q]); H = fam.H([*r['y'][:2], r['D_meV']]); E = r['y'][2]
            close('orthogonality', W.T @ W, np.eye(fam.dim), CFG['orthogonality_tolerance'])
            close('center_energy', E, np.trace(F.T @ H @ F)/2)
            close('root_position', r['y'][:2], rec['root']['f'])
            kw = eigh(Q.T @ H @ Q-E*np.eye(fam.dim-2), eigvals_only=True)
            close('complement_spectrum', kw, r['complement_eigenvalues_meV'])
            assert r['inertia'] == [int(sum(kw < 0)), int(sum(kw > 0))] == [r['lo'], fam.dim-r['lo']-2]
            assert r['inertia_correct']
            J = np.stack([g(F.T @ a @ F) for a in A[:2]]+[np.array([-1., 0., 0.])], axis=1)
            C = np.linalg.inv(J); gd = g(F.T @ A[2] @ F); v = -C @ gd
            T = A[2]+v[0]*A[0]+v[1]*A[1]
            primitives = {
                'J': J, 'C': C, 'gD': gd, 'g0': g(F.T @ H @ F-E*np.eye(2)), 'velocity': v,
                'J_singular_values': np.linalg.svd(J, compute_uv=False),
                'G0': min(abs(kw))-CFG['energy_allowance_meV'],
                'axis_norms': norms,
                'cross_axes': [norm(Q.T @ a @ F)+CFG['norm_allowance'] for a in A[:2]],
                'cross_center': norm(Q.T @ H @ F)+CFG['norm_allowance'],
                'cross_velocity': norm(Q.T @ T @ F)+CFG['norm_allowance'],
                'complement_velocity': max(abs(eigh(T-v[2]*np.eye(fam.dim), eigvals_only=True)))+CFG['norm_allowance']
            }
            for name, value in primitives.items():
                close(name, value, r[name])
            m = model(engine, PLAN['N'], r['D_meV'])
            native = m.H(fam.k(np.array(r['y'][:2])))
            materr = float(np.max(np.abs(fam.U.conj().T @ native @ fam.U-H)))
            w = eigh(native, eigvals_only=True, subset_by_index=(r['lo']-1, r['lo']+2))
            specerr = float(np.max(np.abs(w-r['w4'])))
            assert materr <= CFG['matrix_tolerance_meV'] and specerr <= CFG['native_spectrum_tolerance_meV']
            assert w[2]-w[1] <= CFG['native_spectrum_tolerance_meV']
            close('native_spectrum', w, rec['native']['w4'])
            native_max['matrix'] = max(native_max['matrix'], materr)
            native_max['spectrum'] = max(native_max['spectrum'], specerr)
            native_max['gap'] = max(native_max['gap'], float(w[2]-w[1]))
        print('RECONSTRUCTED', engine, flush=True)

    # Separate scalar implementation, including all failed parent attempts.
    def audit_certificate(raw, saved, h):
        assert saved['halfwidth'] == h
        Gline = raw['G0']-h*raw['complement_velocity']
        bline = raw['cross_center']+h*raw['cross_velocity']
        close('bound_Gline', Gline, saved['Gline'])
        close('bound_bline', bline, saved['bline'])
        if Gline <= CFG['complement_margin_meV'] or not raw['inertia_correct']:
            assert not saved['pass'] and saved['reason'] == 'complement_line_or_inertia'
            return
        C, J, v = np.array(raw['C']), np.array(raw['J']), np.array(raw['velocity'])
        row_sums = abs(C).sum(axis=1)
        Y = abs(C @ raw['g0'])+h*abs(C @ (np.array(raw['gD'])+J @ v))+row_sums*(bline**2/Gline+CFG['energy_allowance_meV'])
        rho = max(CFG['minimum_rho_meV'], CFG['radius_factor']*max(Y/row_sums))
        radii = rho*row_sums
        G = Gline-np.dot(raw['axis_norms'], radii[:2])-radii[2]
        B = bline+np.dot(raw['cross_axes'], radii[:2])
        for name, value in [('Y', Y), ('rho_meV', rho), ('radii', radii), ('Gfull', G), ('bfull', B)]:
            close('bound_'+name, value, saved[name])
        if G <= CFG['complement_margin_meV']:
            assert not saved['pass'] and saved['reason'] == 'complement_tube'
            return
        n = [2*b*B/G+B**2*a/G**2 for a, b in zip(raw['axis_norms'], raw['cross_axes'])]+[B**2/G**2]
        residual = abs(np.eye(3)-C @ J)+CFG['dimensionless_allowance']
        qrows = np.array([(sum(residual[i, j]*radii[j] for j in range(3))+row_sums[i]*sum(n[j]*radii[j] for j in range(3)))/radii[i] for i in range(3)])
        q = max(qrows); yn = max(Y/radii)
        beta = yn/(1-q) if q < 1 else None
        for name, value in [('nonlinear_derivative', n), ('contraction_rows', qrows), ('q', q), ('Ynorm', yn), ('self_map', yn+q)]:
            close('bound_'+name, value, saved[name])
        if beta is None:
            assert saved['beta'] is None and saved['inner_radii'] is None
        else:
            close('bound_beta', beta, saved['beta'])
            close('bound_inner_radii', beta*radii, saved['inner_radii'])
        assert saved['pass'] == bool(q <= CFG['contraction_max'] and yn+q <= CFG['self_map_max'])

    totals = {'interval_attempts': 0, 'accepted_leaves': 0, 'failed_parents_retained': 0, 'point_certificates': 0, 'endpoint_containments': 0, 'separation_checks': 0}
    extrema = {'maximum_q': 0., 'maximum_self_map': 0., 'minimum_Gfull_meV': float('inf'), 'minimum_join_margin': [float('inf')]*3, 'maximum_tube_radius': [0.]*3}
    details = []
    def location(raw, D):
        return np.array(raw['y'])+(D-raw['D_meV'])*np.array(raw['velocity'])
    for camp in data['campaigns']:
        assert camp['pass']
        for name, path in camp['nodes'].items():
            assert path['pass']
            attempts = path['attempts']; leaves = [attempts[i] for i in path['leaf_ids']]
            assert path['leaf_ids'] == [x['id'] for x in attempts if not x['children']]
            assert leaves[0]['a'] == 38. and leaves[-1]['b'] == 39.
            assert all(a['b'] == b['a'] for a, b in zip(leaves[:-1], leaves[1:]))
            roots = [x for x in attempts if x['parent'] is None]
            grid = np.linspace(38, 39, camp['initial_intervals']+1)
            assert [(x['a'], x['b']) for x in roots] == list(zip(grid[:-1], grid[1:]))
            for i, c in enumerate(attempts):
                assert c['id'] == i
                raw = data['centers'][c['center']]['raw']
                assert raw['D_meV'] == (c['a']+c['b'])/2
                audit_certificate(raw, c['certificate'], (c['b']-c['a'])/2)
                if c['children']:
                    assert not c['certificate']['pass'] and len(c['children']) == 2
                    left, right = [attempts[k] for k in c['children']]
                    assert left['parent'] == right['parent'] == i
                    assert left['depth'] == right['depth'] == c['depth']+1
                    assert (left['a'], left['b'], right['a'], right['b']) == (c['a'], raw['D_meV'], raw['D_meV'], c['b'])
                    totals['failed_parents_retained'] += 1
                else:
                    assert c['certificate']['pass']
                    s = c['certificate']
                    extrema['maximum_q'] = max(extrema['maximum_q'], s['q'])
                    extrema['maximum_self_map'] = max(extrema['maximum_self_map'], s['self_map'])
                    extrema['minimum_Gfull_meV'] = min(extrema['minimum_Gfull_meV'], s['Gfull'])
                    extrema['maximum_tube_radius'] = np.maximum(extrema['maximum_tube_radius'], s['radii']).tolist()
            assert [p['D_meV'] for p in path['points']] == sorted({x for c in leaves for x in [c['a'], c['b']]})
            points = {p['D_meV']: p for p in path['points']}
            for p in path['points']:
                raw = data['centers'][p['center']]['raw']
                assert p['D_meV'] == raw['D_meV'] and p['certificate']['pass']
                audit_certificate(raw, p['certificate'], 0)
            expected_joins = {(c['id'], D) for c in leaves for D in [c['a'], c['b']]}
            assert {(j['cell'], j['D_meV']) for j in path['joins']} == expected_joins
            assert len(path['joins']) == len(expected_joins)
            for j in path['joins']:
                c, p = attempts[j['cell']], points[j['D_meV']]
                assert j['point_center'] == p['center']
                tube = data['centers'][c['center']]['raw']; point = data['centers'][p['center']]['raw']
                margin = np.array(c['certificate']['radii'])-abs(location(tube, j['D_meV'])-np.array(point['y']))-np.array(p['certificate']['inner_radii'])
                close('join_margin', margin, j['margins'])
                assert min(margin) > 0 and j['pass']
                extrema['minimum_join_margin'] = np.minimum(extrema['minimum_join_margin'], margin).tolist()
            totals['interval_attempts'] += len(attempts)
            totals['accepted_leaves'] += len(leaves)
            totals['point_certificates'] += len(points)
            totals['endpoint_containments'] += len(path['joins'])
            details.append({'engine': camp['engine'], 'initial_intervals': camp['initial_intervals'], 'node': name, 'attempts': len(attempts), 'accepted_leaves': len(leaves), 'failed_parents': len(attempts)-len(leaves), 'min_interval_width_meV': min(c['b']-c['a'] for c in leaves), 'maximum_q': max(c['certificate']['q'] for c in leaves)})
        expected_seps = []
        for n1, n2 in itertools.combinations(PLAN['nodes'], 2):
            p1, p2 = camp['nodes'][n1], camp['nodes'][n2]
            for i in p1['leaf_ids']:
                for j in p2['leaf_ids']:
                    c1, c2 = p1['attempts'][i], p2['attempts'][j]
                    a, b = max(c1['a'], c2['a']), min(c1['b'], c2['b'])
                    if a >= b:
                        continue
                    expected_seps.append((n1, n2, i, j, a, b))
        saved_seps = [(s['nodes'][0], s['nodes'][1], *s['cells'], s['a'], s['b']) for s in camp['separations']]
        assert saved_seps == expected_seps
        for s in camp['separations']:
            c1, c2 = [camp['nodes'][n]['attempts'][i] for n, i in zip(s['nodes'], s['cells'])]
            r1, r2 = [data['centers'][c['center']]['raw'] for c in [c1, c2]]
            delta = np.array([location(r2, D)[:2]-location(r1, D)[:2] for D in [s['a'], s['b']]])
            margin = np.maximum(np.min(delta, axis=0), np.min(-delta, axis=0))-np.array(c1['certificate']['radii'][:2])-np.array(c2['certificate']['radii'][:2])
            close('separation_margin', margin, s['axis_margins'])
            assert max(margin) > 0 and s['pass'] and s['separating_axis'] == int(np.argmax(margin))
        totals['separation_checks'] += len(camp['separations'])
    cross_engine = []
    unmatched = []
    for key, rec in data['centers'].items():
        if rec['engine'] != 'bm':
            continue
        other_key = 'ref'+key[2:]
        if other_key not in data['centers']:
            unmatched.append(key)
            continue
        other = data['centers'][other_key]
        cross_engine.append(float(np.max(np.abs(np.array(rec['raw']['y'])[:2]-other['raw']['y'][:2]))))
    unmatched += [key for key, rec in data['centers'].items() if rec['engine'] == 'ref' and 'bm'+key[3:] not in data['centers']]
    assert max(cross_engine) <= CFG['reconciliation_tolerance']
    assert data['status'] == 'CONDITIONAL_LOCAL_CONTINUATION_PASS' and not data['errors']
    sources = ['PLAN.json', 'bounds.py', 'controls.py', 'CONTROLS.json', 'run.py', 'RESULTS.json', 'FRAMES.npz', 'report.py', 'METHOD.md']
    summary = {'status': 'RECONCILED_CONDITIONAL_LOCAL_CONTINUATION_PASS', 'all_checks_pass': True,
               'analytic_controls': len(controls['controls']), 'distinct_centers': len(data['centers']),
               'totals': totals, 'extrema': extrema, 'campaign_details': details, 'native_maximum_errors_meV': native_max,
               'maximum_cross_engine_position_difference_at_common_centers': max(cross_engine),
               'cross_engine_common_center_pairs': len(cross_engine), 'centers_without_same_D_node_in_other_engine': unmatched,
               'reconstruction_maximum_discrepancies': discrepancy,
               'source_hashes': {n: sha(ROOT/n) for n in sources}, 'scope': PLAN['scope']}
    (ROOT/'SUMMARY.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: v for k, v in summary.items() if k not in ['source_hashes', 'reconstruction_maximum_discrepancies']}, indent=2), flush=True)

if __name__ == '__main__':
    main()
