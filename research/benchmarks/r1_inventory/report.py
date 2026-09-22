"""Rebuild Gram data, directly bound weighted blocks, and audit the full cover."""
import json
import sys
import numpy as np
from scipy.linalg import eigh, qr
from inventory import ROOT, PLAN, T, sha
from sources import load, read_attachment_inputs
sys.path.insert(0, str(ROOT.parent/'r1_holonomy'))
from measure import Family
from track import model

def main():
    data = json.loads((ROOT/'RESULTS.json').read_text())
    assert data['plan_sha256'] == sha(ROOT/'PLAN.json')
    assert all(sha(ROOT.parent/n) == h for n, h in data['source_hashes'].items())
    tasks, inherited = load(); lookup = {t['key']: t for t in tasks}
    assert all(data['source_hashes'][n] == h for n, h in inherited.items())
    controls = json.loads((ROOT/'CONTROLS.json').read_text())
    assert controls['all_controls_pass'] and controls['plan_sha256'] == data['plan_sha256']
    assert all(sha(ROOT/n) == h for n, h in controls['source_hashes'].items())
    _, contour_cases, _ = read_attachment_inputs()
    errors = {}; totals = {'references': 0, 'attempts': 0, 'accepted_leaves': 0, 'failed_parents': 0, 'unresolved_leaves': 0}
    extrema = {'minimum_exclusion_margin_meV': float('inf'), 'minimum_energy_capture_margin_meV': float('inf'),
               'minimum_other_gap_meV': float('inf'), 'maximum_accepted_eta': 0., 'maximum_depth': 0,
               'maximum_native_matrix_error_meV': 0., 'maximum_native_spectrum_error_meV': 0.}
    def close(name, a, b):
        aa, bb = np.asarray(a), np.asarray(b)
        assert aa.shape == bb.shape
        error = float(np.max(abs(aa-bb)))
        errors[name] = max(errors.get(name, 0.), error)
        assert np.isfinite(error) and error <= T['reconciliation_tolerance'], (name, error)
    def g(M):
        return np.array([(M[0, 0]+M[1, 1])/2, (M[0, 0]-M[1, 1])/2, M[0, 1]])
    def cross(a, b):
        return a[..., 0]*b[..., 1]-a[..., 1]*b[..., 0]
    def min_parallelogram(J, offset, a, b):
        points = np.array([[a[0], a[1]], [b[0], a[1]], [b[0], b[1]], [a[0], b[1]]]) @ J.T+offset
        edges = np.roll(points, -1, axis=0)-points
        sides = cross(edges, -points)
        if np.all(sides >= 0) or np.all(sides <= 0):
            return 0.
        t = np.clip(-np.sum(points*edges, axis=1)/np.sum(edges*edges, axis=1), 0, 1)
        return float(np.min(np.linalg.norm(points+t[:, None]*edges, axis=1)))

    campaign_details = []
    for engine in PLAN['engines']:
        family = Family(engine)
        temporal = json.loads((ROOT.parent/'r1_temporal'/(engine.upper()+'.json')).read_text())
        chart_box = np.array(temporal['bounds'])
        for case in [c for c in contour_cases if c['engine'] == engine]:
            for station in case['geometry']:
                vertices = np.c_[np.array(station['vertices'][2:]), np.full(len(station['vertices'])-2, station['D_meV'])]
                assert np.all(vertices >= chart_box[0]-1e-14) and np.all(vertices <= chart_box[1]+1e-14)
        for campaign in [c for c in data['campaigns'] if c['engine'] == engine]:
            archive = ROOT/campaign['arrays_file']
            assert sha(archive) == campaign['arrays_sha256']
            arrays = np.load(archive); details = {'engine': engine, 'grid': campaign['grid'], 'references': 0, 'attempts': 0, 'accepted_leaves': 0, 'unresolved_leaves': 0}
            assert [r['key'] for r in campaign['references']] == [t['key'] for t in tasks if t['engine'] == engine and t['grid'] == campaign['grid']]
            assert set(arrays.files) == {r['key'] for r in campaign['references']}
            for reference in campaign['references']:
                task = lookup[reference['key']]; raw = task['raw']; saved = reference['primitives']
                for field in ['a', 'b', 'halfwidth', 'center_key', 'parent_certificate', 'containment_endpoints', 'clipped_contour_intervals']:
                    assert reference[field] == task[field]
                # Reconstruct domain containment with affine velocities at every
                # clipped interval endpoint, independently of the producer's blend.
                maximum = np.zeros(2); clipped = 0
                for case in [c for c in contour_cases if c['engine'] == engine]:
                    for l, r in zip(case['geometry'][:-1], case['geometry'][1:]):
                        a, b = max(reference['a'], l['D_meV']), min(reference['b'], r['D_meV'])
                        if a >= b:
                            continue
                        clipped += 1
                        ring0 = np.array(l['vertices'][2:-1]); dr = (np.array(r['vertices'][2:-1])-ring0)/(r['D_meV']-l['D_meV'])
                        for D in [a, b]:
                            ring = ring0+(D-l['D_meV'])*dr
                            predictor = np.array(raw['y'][:2])+(D-raw['D_meV'])*np.array(raw['velocity'][:2])
                            maximum = np.maximum(maximum, np.max(abs(ring-predictor), axis=0))
                            assert np.all(abs(ring-predictor) < np.array(reference['outer_radii']))
                assert clipped == reference['clipped_contour_intervals']
                close('outer_domain', maximum+T['geometry_padding'], reference['outer_radii'])
                F = task['frame']; Q = qr(F, mode='full')[0][:, 2:]; y0 = np.array(raw['y']); v = np.array(raw['velocity']); dim = family.dim
                H = family.H([*y0[:2], raw['D_meV']]); E0 = y0[2]
                kw, V = eigh(Q.T @ H @ Q-E0*np.eye(dim-2))
                B = np.array([Q.T @ a @ F for a in [H, family.A[0], family.A[1], family.A[2]+v[0]*family.A[0]+v[1]*family.A[1]]])
                # Independent construction uses the absolute inverse directly.
                inverse_abs = (V*(1/abs(kw))) @ V.T
                gram = np.array([[bi.T @ inverse_abs @ bj for bj in B] for bi in B])
                weighted = np.array([(V.T @ bi)/np.sqrt(abs(kw))[:, None] for bi in B])
                J = np.stack([g(F.T @ a @ F) for a in family.A[:2]]+[np.array([-1., 0., 0.])], axis=1)
                residual = g(F.T @ family.A[2] @ F)+J @ v
                g0 = g(F.T @ H @ F-E0*np.eye(2))
                w = eigh(H, eigvals_only=True, subset_by_index=(raw['lo']-1, raw['lo']+3))
                axnorm = np.array([max(abs(eigh(a, eigvals_only=True)))+T['norm_allowance'] for a in family.A[:2]])
                nv = float(max(abs(eigh(family.A[2]+v[0]*family.A[0]+v[1]*family.A[1]-v[2]*np.eye(dim), eigvals_only=True))))+T['norm_allowance']
                G0 = float(min(abs(kw))-T['energy_allowance_meV']); e0 = float(max(abs(w[1:3]-E0)))
                Wframe = np.column_stack([F, Q]); orth = float(np.max(abs(Wframe.T @ Wframe-np.eye(dim))))
                for name, value in [('G0', G0), ('gram', gram), ('w5', w), ('J', J), ('g0', g0), ('predictor_residual', residual), ('axis_norms', axnorm), ('complement_velocity', nv), ('center_energy_offset', e0), ('orthogonality_error', orth)]:
                    close('primitive_'+name, value, saved[name])
                assert orth < T['orthogonality_tolerance']
                close('complement_spectrum', kw, raw['complement_eigenvalues_meV'])
                native_model = model(engine, PLAN['N'], raw['D_meV'])
                native = native_model.H(family.k(y0[:2])); matrix_error = float(np.max(abs(family.U.conj().T @ native @ family.U-H)))
                nw = eigh(native, eigvals_only=True, subset_by_index=(raw['lo']-1, raw['lo']+3)); spectrum_error = float(max(abs(nw-w)))
                assert matrix_error < T['matrix_tolerance_meV'] and spectrum_error < T['reconciliation_tolerance'] and reference['native']['pass']
                close('native_w5', nw, reference['native']['w5'])
                extrema['maximum_native_matrix_error_meV'] = max(extrema['maximum_native_matrix_error_meV'], matrix_error)
                extrema['maximum_native_spectrum_error_meV'] = max(extrema['maximum_native_spectrum_error_meV'], spectrum_error)

                def nonlinear(a, b):
                    extent = np.max(abs(np.array([a, b])), axis=0)
                    L = float(extent[:2] @ axnorm+extent[2]*nv); window = e0+L+T['energy_allowance_meV']; eta = (L+window)/G0
                    norms = []
                    for x in [a[0], b[0]]:
                        for y in [a[1], b[1]]:
                            for d in [a[2], b[2]]:
                                WB = weighted[0]+x*weighted[1]+y*weighted[2]+d*weighted[3]
                                norms.append(float(np.linalg.svd(WB, compute_uv=False)[0]))
                    bn = max(norms)+T['weighted_norm_allowance_sqrt_meV']
                    N = bn*bn/(1-eta)+T['energy_allowance_meV'] if eta < T['eta_max'] else None
                    return [L, window, eta, bn, N]
                h = task['halfwidth']; radius = np.array(task['parent_certificate']['radii']); R = np.array(reference['outer_radii'])
                cc = nonlinear([-radius[0], -radius[1], -h], [radius[0], radius[1], h]); stored = reference['core_energy_capture']
                for name, value in zip(['L', 'W', 'eta', 'weighted_B_norm', 'correction_upper'], cc):
                    if value is None:
                        assert stored[name] is None
                    else:
                        close('core_'+name, value, stored[name])
                trace = max(abs(g0[0]-h*residual[0]), abs(g0[0]+h*residual[0]))+float(abs(J[0, :2]) @ radius[:2])
                capture_margin = radius[2]-trace-cc[4]-T['energy_allowance_meV'] if cc[4] is not None else None
                if capture_margin is not None:
                    close('core_capture_margin', capture_margin, stored['capture_margin'])
                assert stored['pass'] == bool(capture_margin is not None and capture_margin > 0)
                if stored['pass']:
                    extrema['minimum_energy_capture_margin_meV'] = min(extrema['minimum_energy_capture_margin_meV'], capture_margin)
                beta = task['parent_certificate']['beta']; assert 0 <= beta < 1
                assert task['parent_certificate']['pass'] and np.all(beta*radius < radius)
                Louter = float(R @ axnorm+h*nv); gap_lower = np.diff(w)[[0, 2, 3]]-2*Louter-T['energy_allowance_meV']
                close('other_gap_lower', gap_lower, reference['other_gaps']['other_gap_lower_meV'])
                assert reference['other_gaps']['pass'] == bool(min(gap_lower) > T['gap_margin_meV'])
                extrema['minimum_other_gap_meV'] = min(extrema['minimum_other_gap_meV'], float(min(gap_lower)))
                rows = arrays[task['key']]; assert rows.shape[1] == 18
                # Explicit expected strip endpoints, independent of strips().
                expected = [([-R[0], -R[1], -h], [-radius[0], R[1], h]), ([radius[0], -R[1], -h], [R[0], R[1], h]),
                            ([-radius[0], -R[1], -h], [radius[0], -radius[1], h]), ([-radius[0], radius[1], -h], [radius[0], R[1], h])]
                roots = reference['cover']['root_indices']; assert len(roots) == 4
                visited = set()
                def tree(i, parent, depth):
                    assert i not in visited; visited.add(i); row = rows[i]
                    a, b = row[:3], row[3:6]
                    assert row[7] == parent and row[6] == depth and np.all(a < b)
                    if row[10] == 0:
                        left, right = map(int, row[8:10]); lr, rr = rows[left], rows[right]
                        axis = int(np.argmax((b-a)*np.r_[axnorm, nv])); m = (a[axis]+b[axis])/2
                        lb = b.copy(); lb[axis] = m; ra = a.copy(); ra[axis] = m
                        assert np.array_equal(lr[:3], a) and np.array_equal(lr[3:6], lb)
                        assert np.array_equal(rr[:3], ra) and np.array_equal(rr[3:6], b)
                        tree(left, i, depth+1); tree(right, i, depth+1)
                    else:
                        assert row[8] == row[9] == -1
                for idx, (a, b) in zip(roots, expected):
                    assert np.array_equal(rows[idx, :3], a) and np.array_equal(rows[idx, 3:6], b)
                    tree(idx, -1, 0)
                assert visited == set(range(len(rows)))
                split_count = 0
                for row in rows:
                    a, b = row[:3], row[3:6]; values = nonlinear(a, b)
                    offset = g0[1:]+residual[1:]*(a[2]+b[2])/2
                    lower = max(0., min_parallelogram(J[1:, :2], offset, a[:2], b[:2])-(b[2]-a[2])/2*np.linalg.norm(residual[1:])-T['energy_allowance_meV'])
                    margin = lower-values[4] if values[4] is not None else None
                    values += [float(lower), margin]
                    for j, val in enumerate(values):
                        if val is None:
                            assert np.isnan(row[11+j])
                        else:
                            close('cell_'+str(j), val, row[11+j])
                    accepted = margin is not None and margin > T['exclusion_margin_meV']
                    expected_state = 1 if accepted else -1 if row[6] >= T['maximum_depth'] else -2 if split_count >= T['maximum_split_nodes_per_reference'] else 0
                    assert row[10] == expected_state
                    if expected_state == 0:
                        split_count += 1
                    elif expected_state == 1:
                        extrema['minimum_exclusion_margin_meV'] = min(extrema['minimum_exclusion_margin_meV'], margin)
                        extrema['maximum_accepted_eta'] = max(extrema['maximum_accepted_eta'], values[2])
                leaves = rows[rows[:, 10] != 0]; unresolved = int(sum(leaves[:, 10] != 1)); accepted_count = len(leaves)-unresolved
                assert reference['cover']['attempts'] == len(rows) and reference['cover']['leaves'] == len(leaves)
                assert reference['cover']['split_nodes'] == split_count and reference['cover']['unresolved_leaves'] == unresolved
                assert reference['cover']['pass'] == (unresolved == 0)
                assert reference['pass'] == bool(reference['native']['pass'] and stored['pass'] and reference['other_gaps']['pass'] and unresolved == 0)
                vol = float(np.sum(np.prod(leaves[:, 3:6]-leaves[:, :3], axis=1)))+8*float(np.prod(radius[:2]))*h
                close('partition_volume', vol, 8*float(np.prod(R))*h)
                extrema['maximum_depth'] = max(extrema['maximum_depth'], int(max(rows[:, 6])))
                for out in [totals, details]:
                    out['references'] += 1; out['attempts'] += len(rows); out['accepted_leaves'] += accepted_count; out['unresolved_leaves'] += unresolved
                totals['failed_parents'] += split_count
            details['pass'] = all(r['pass'] for r in campaign['references'])
            assert campaign['pass'] == details['pass']; campaign_details.append(details)
            print('RECONCILED', json.dumps(details), flush=True)
    allpass = len(campaign_details) == 4 and all(c['pass'] for c in campaign_details) and not data['errors']
    assert (data['status'] == 'CONDITIONAL_SINGLE_NODE_INTERIOR_INVENTORY_PASS') == allpass
    filenames = ['PLAN.json', 'inventory.py', 'controls.py', 'CONTROLS.json', 'sources.py', 'run.py', 'RESULTS.json', 'METHOD.md', 'report.py']+[c['arrays_file'] for c in data['campaigns']]
    summary = {'status': 'RECONCILED_CONDITIONAL_SINGLE_NODE_INTERIOR_INVENTORY_PASS' if allpass else 'UNRESOLVED_INTERIOR_INVENTORY_RECONCILED',
               'all_checks_pass': allpass, 'analytic_controls': len(controls['controls']), 'totals': totals, 'campaigns': campaign_details,
               'extrema': extrema, 'reconstruction_errors': errors,
               'single_node_scope': 'Only q among degeneracies of the selected isolated bands 297..299 in both tested ring interiors, for all D38-39, conditional on the numerical bounds.',
               'charge_interpretation': 'Inherited +k based-loop label can be assigned to the enclosed q branch in the existing fixed-chart and stem convention; no new charge measurement.',
               'source_hashes': {n: sha(ROOT/n) for n in filenames}, 'scope': PLAN['scope']}
    (ROOT/'SUMMARY.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    print('STATUS', summary['status'], json.dumps(totals), json.dumps(extrema), flush=True)

if __name__ == '__main__':
    main()
