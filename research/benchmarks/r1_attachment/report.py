"""Independent power-basis and projection audit of the retained geometry."""
import itertools
import json
import numpy as np
from geometry import ROOT, PLAN, T, sha
from inputs import read_inputs

def main():
    data = json.loads((ROOT/'RESULTS.json').read_text())
    assert data['plan_sha256'] == sha(ROOT/'PLAN.json')
    assert all(sha(ROOT.parent/n) == h for n, h in data['source_hashes'].items())
    controls = json.loads((ROOT/'CONTROLS.json').read_text())
    assert controls['all_controls_pass'] and controls['plan_sha256'] == data['plan_sha256']
    assert all(sha(ROOT/n) == h for n, h in controls['source_hashes'].items())
    cont, cases, sources = read_inputs()
    assert all(data['source_hashes'][n] == h for n, h in sources.items())
    assert len(cases) == len(data['cases']) == 8
    errors = {}; analytic_bound_violation = 0.
    count = {'interval_attempts': 0, 'accepted_leaves': 0, 'failed_parents': 0, 'unresolved_leaves': 0,
             'polygon_convexity_tests': 0, 'convexity_side_polynomials': 0,
             'node_polygon_tests': 0, 'box_side_polynomials': 0, 'node_stem_tests': 0}
    def close(name, a, b):
        error = float(np.max(np.abs(np.asarray(a)-np.asarray(b))))
        errors[name] = max(errors.get(name, 0.), error)
        assert np.isfinite(error) and error <= T['reconciliation_tolerance'], (name, error)
    def det(u, v):
        return u[..., 0]*v[..., 1]-u[..., 1]*v[..., 0]
    signs = np.array(list(itertools.product([-1., 1.], repeat=2)))
    def polynomials(polygon, points):
        nonlocal analytic_bound_violation
        e0 = np.roll(polygon[0], -1, axis=0)-polygon[0]
        e1 = np.roll(polygon[1], -1, axis=0)-polygon[1]
        z0 = points[0][None]-polygon[0][:, None]
        z1 = points[1][None]-polygon[1][:, None]
        de, dz = e1-e0, z1-z0
        constant = det(e0[:, None], z0)
        linear = det(de[:, None], z0)+det(e0[:, None], dz)
        quadratic = det(de[:, None], dz)
        coef = np.stack([constant, constant+linear/2, constant+linear+quadratic], axis=-1)
        endpoint = constant+linear+quadratic
        exact_min = np.minimum(constant, endpoint)
        exact_max = np.maximum(constant, endpoint)
        t = np.divide(-linear, 2*quadratic, out=np.zeros_like(linear), where=quadratic != 0)
        value = constant+t*(linear+t*quadratic)
        interior = (t > 0) & (t < 1)
        exact_min = np.where(interior & (quadratic > 0), np.minimum(exact_min, value), exact_min)
        exact_max = np.where(interior & (quadratic < 0), np.maximum(exact_max, value), exact_max)
        violation = max(0., float(np.max(np.min(coef, axis=-1)-exact_min)), float(np.max(exact_max-np.max(coef, axis=-1))))
        analytic_bound_violation = max(analytic_bound_violation, violation)
        assert violation <= T['area_allowance']
        length = np.maximum(np.linalg.norm(e0, axis=1), np.linalg.norm(e1, axis=1))+T['length_allowance']
        return coef, length, exact_min, exact_max

    def independently_get(case, entry):
        a, b = entry['a'], entry['b']; midpoint = (a+b)/2
        stations = case['geometry']; j = entry['contour_interval']
        l, r = stations[j], stations[j+1]
        assert l['D_meV'] <= a < b <= r['D_meV']
        start, velocity = np.array(l['vertices']), (np.array(r['vertices'])-l['vertices'])/(r['D_meV']-l['D_meV'])
        vertices = np.array([start+(D-l['D_meV'])*velocity for D in [a, b]])
        boxes = {}
        for node in PLAN['nodes']:
            matches = [c for c in case['paths'][node] if c['a'] <= midpoint <= c['b']]
            assert len(matches) == 1
            cell = matches[0]; raw = cont['centers'][cell['center']]['raw']
            assert cell['a'] <= a < b <= cell['b'] and cell['certificate']['pass']
            assert entry['node_tubes'][node] == {'tube_id': cell['id'], 'center_key': cell['center']}
            centers = np.array([np.array(raw['y'][:2])+(D-raw['D_meV'])*np.array(raw['velocity'][:2]) for D in [a, b]])
            radii = np.array(cell['certificate']['radii'][:2])
            boxes[node] = (centers, radii)
        return vertices, boxes

    details = []
    for case, record in zip(cases, data['cases']):
        for key in ['engine', 'mesh', 'radius', 'polygon_edges', 'track_intervals', 'common_partition', 'inherited_surface_case', 'inherited_loop_labels']:
            assert case[key] == record[key]
        assert record['geometry_source_error'] <= T['geometry_reconstruction_tolerance']
        attempts = record['attempts']; leaf_ids = record['leaf_ids']
        assert leaf_ids == [x['id'] for x in attempts if not x['children']]
        leaves = [attempts[i] for i in leaf_ids]
        assert leaves[0]['a'] == 38 and leaves[-1]['b'] == 39
        assert all(l['b'] == r['a'] for l, r in zip(leaves[:-1], leaves[1:]))
        roots = [x for x in attempts if x['parent'] is None]
        assert [(x['a'], x['b']) for x in roots] == list(zip(case['common_partition'][:-1], case['common_partition'][1:]))
        visited = set()
        def tree(i, parent=None, depth=0):
            assert i not in visited
            visited.add(i); c = attempts[i]
            assert c['id'] == i and c['parent'] == parent and c['depth'] == depth
            if c['children']:
                assert len(c['children']) == 2 and not c['bound']['pass'] and c['state'] == 'split'
                left, right = [attempts[j] for j in c['children']]
                m = (c['a']+c['b'])/2
                assert (left['a'], left['b'], right['a'], right['b']) == (c['a'], m, m, c['b'])
                for child in c['children']:
                    tree(child, i, depth+1)
            else:
                assert c['state'] == ('accepted' if c['bound']['pass'] else 'unresolved_depth_limit')
                assert c['bound']['pass'] or depth == T['maximum_depth']
        for c in roots:
            tree(c['id'])
        assert visited == set(range(len(attempts)))
        minimum = {'q_inside': float('inf'), 'p_outside': float('inf'), 'upper_outside': float('inf'),
                   'stem_p': float('inf'), 'stem_q': float('inf'), 'stem_upper': float('inf'), 'convex_area': float('inf')}
        for entry in attempts:
            vertices, boxes = independently_get(case, entry)
            assert np.array_equal(vertices[:, 2], vertices[:, -1])
            polygon = vertices[:, 2:-1]; n = len(polygon[0])
            saved = entry['bound']; passed = []
            coef, length, exact_min, exact_max = polynomials(polygon, polygon)
            mask = np.ones((n, n), dtype=bool)
            for i in range(n):
                mask[i, i] = mask[i, (i+1) % n] = False
            values = np.where(mask[:, :, None], coef, np.inf)
            lower = float(np.min(values)-T['area_allowance'])
            witness = saved['convex_polygon']['witness_edge_vertex_coefficient']
            assert mask[witness[0], witness[1]]
            close('convex_witness', values[tuple(witness)]-T['area_allowance'], saved['convex_polygon']['minimum_oriented_area'])
            close('convex_minimum', lower, saved['convex_polygon']['minimum_oriented_area'])
            close('edge_length', max(length), saved['convex_polygon']['maximum_edge_length'])
            assert saved['convex_polygon']['pass'] == (lower > 0)
            passed.append(lower > 0)
            if entry['bound']['pass']:
                minimum['convex_area'] = min(minimum['convex_area'], lower)
            count['polygon_convexity_tests'] += 1
            count['convexity_side_polynomials'] += n*(n-2)
            for node, (centers, radii) in boxes.items():
                corners = centers[:, None]+signs[None]*radii
                coef, length, emin, emax = polynomials(polygon, corners)
                nr = saved['nodes'][node]; pr = nr['polygon']; wi = tuple(pr['witness_edge_corner_coefficient'])
                inside = node == 'q'
                scores = ((coef if inside else -coef)-T['area_allowance'])/length[:, None, None]-T['length_allowance']
                margin = float(np.min(scores)) if inside else float(np.max(np.min(scores, axis=(1, 2))))
                close('polygon_margin', margin, pr['clearance_bound'])
                close('polygon_witness', scores[wi], pr['clearance_bound'])
                if not inside:
                    close('outside_fixed_edge', np.min(scores[wi[0]]), pr['clearance_bound'])
                assert pr['relation'] == ('inside' if inside else 'outside')
                assert pr['pass'] == (margin > T['minimum_clearance'])
                passed.append(pr['pass'])
                if entry['bound']['pass']:
                    key = node+('_inside' if inside else '_outside')
                    minimum[key] = min(minimum[key], margin)
                count['node_polygon_tests'] += 1; count['box_side_polynomials'] += 4*n
                for k, sr in enumerate(nr['stems']):
                    segment = vertices[:, k:k+2]
                    count['node_stem_tests'] += 1
                    if sr['axis'] is None:
                        assert not sr['pass']; passed.append(False); continue
                    axis = np.array(sr['axis']); norm = np.linalg.norm(axis)
                    assert np.isfinite(axis).all() and norm > T['minimum_axis_length']
                    # Explicitly enumerate the box corners, unlike the production
                    # support-function formula. D and segment extrema are endpoints.
                    projections = np.einsum('teck,k->tec', segment[:, :, None]-corners[:, None], axis)
                    lower = float(np.min(projections))/(norm+T['length_allowance'])-T['length_allowance']
                    close('stem_margin', lower, sr['clearance_bound'])
                    d, endpoint = sr['witness_D_endpoint_segment_endpoint']
                    close('stem_witness', np.min(projections[d, endpoint])/(norm+T['length_allowance'])-T['length_allowance'], sr['clearance_bound'])
                    assert sr['pass'] == (lower > T['minimum_clearance'])
                    passed.append(sr['pass'])
                    if entry['bound']['pass']:
                        minimum['stem_'+node] = min(minimum['stem_'+node], lower)
            assert entry['bound']['pass'] == all(passed)
        unresolved = sum(not c['bound']['pass'] for c in leaves)
        assert record['unresolved_leaves'] == unresolved
        assert record['pass'] == (unresolved == 0)
        assert record['geometric_winding_if_pass'] == ({'p': 0, 'q': 1, 'upper': 0} if record['pass'] else None)
        count['interval_attempts'] += len(attempts); count['accepted_leaves'] += len(leaves)-unresolved
        count['failed_parents'] += len(attempts)-len(leaves); count['unresolved_leaves'] += unresolved
        details.append({'engine': case['engine'], 'mesh': case['mesh'], 'radius': case['radius'], 'accepted_leaves': len(leaves)-unresolved,
                        'minimum_clearances': minimum, 'pass': record['pass']})
        print('RECONCILED', case['engine'], case['mesh'], case['radius'], minimum, flush=True)
    allpass = all(c['pass'] for c in details) and not data['errors']
    assert (data['status'] == 'CONDITIONAL_TRACKED_NODE_CONTOUR_ATTACHMENT_PASS') == allpass
    source_names = ['PLAN.json', 'geometry.py', 'inputs.py', 'controls.py', 'CONTROLS.json', 'run.py', 'RESULTS.json', 'METHOD.md', 'report.py']
    summary = {'status': 'RECONCILED_CONDITIONAL_TRACKED_NODE_ATTACHMENT_PASS' if allpass else 'UNRESOLVED_GEOMETRY_RECONCILED',
               'all_checks_pass': allpass, 'analytic_controls': len(controls['controls']), 'totals': count, 'cases': details,
               'global_minimum_clearances': {k: min(c['minimum_clearances'][k] for c in details) for k in details[0]['minimum_clearances']},
               'maximum_Bernstein_vs_analytic_extremum_violation': analytic_bound_violation,
               'reconstruction_errors': errors, 'geometric_winding': {'p': 0, 'q': 1, 'upper': 0} if allpass else None,
               'inherited_loop_charge': '+k; reused, not remeasured and not uniquely attributed to q',
               'new_hamiltonian_evaluations': data['new_hamiltonian_evaluations'], 'new_charge_measurements': data['new_charge_measurements'],
               'source_hashes': {n: sha(ROOT/n) for n in source_names}, 'scope': PLAN['scope']}
    (ROOT/'SUMMARY.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    print('STATUS', summary['status'], json.dumps(count), flush=True)

if __name__ == '__main__':
    main()
