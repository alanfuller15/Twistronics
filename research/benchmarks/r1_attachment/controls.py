"""Analytic geometry and failures invisible to endpoint-only checks."""
import json
import numpy as np
from geometry import ROOT, PLAN, sha, SIGNS, cross, convex_polygon, box_polygon, box_segment

SQUARE = np.array([[-1., -1.], [1., -1.], [1., 1.], [-1., 1.]])
def rotation(a):
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])

def main():
    records = []
    def add(name, passed, **evidence):
        records.append({'name': name, 'pass': bool(passed), **evidence})
    poly = np.array([SQUARE, SQUARE])
    c = np.zeros((2, 2)); r = np.array([.2, .2])
    cv = convex_polygon(poly); inside = box_polygon(poly, c, r, True)
    outside = box_polygon(poly, np.array([[2., 0.], [2., 0.]]), r, False)
    add('static_known_clearances', cv['pass'] and inside['pass'] and outside['pass'] and abs(inside['clearance_bound']-.8) < 1e-8 and abs(outside['clearance_bound']-.8) < 1e-8,
        convex=cv, inside=inside, outside=outside)

    translation = np.array([.4, -.2])
    moving = np.array([SQUARE, SQUARE @ rotation(.15).T+translation])
    centers = np.array([[0., 0.], translation])
    cv = convex_polygon(moving); inc = box_polygon(moving, centers, r, True)
    sampled = []
    for t in np.linspace(0, 1, 101):
        p = (1-t)*moving[0]+t*moving[1]; center = (1-t)*centers[0]+t*centers[1]
        e = np.roll(p, -1, axis=0)-p
        points = center+SIGNS*r
        distances = cross(e[:, None, :], points[None, :, :]-p[:, None, :])/np.linalg.norm(e, axis=1)[:, None]
        sampled.append(float(np.min(distances)))
    add('moving_rotating_polygon', cv['pass'] and inc['pass'] and inc['clearance_bound'] <= min(sampled), convex=cv, interior=inc, minimum_sampled_exact_clearance=min(sampled))
    rev = box_polygon(moving[::-1], centers[::-1], r, True)
    add('parameter_reversal', rev['pass'] and abs(rev['clearance_bound']-inc['clearance_bound']) < 1e-13, reversed=rev)

    # Both endpoint squares enclose x=.75, but the interpolated middle square
    # is only half as large and excludes this point.
    shrinking = np.array([SQUARE @ rotation(-np.pi/3).T, SQUARE @ rotation(np.pi/3).T])
    centers = np.array([[.75, 0.], [.75, 0.]]); small = np.array([.02, .02])
    ends = [box_polygon(np.repeat(shrinking[j:j+1], 2, axis=0), centers, small, True) for j in [0, 1]]
    whole = box_polygon(shrinking, centers, small, True)
    mid = box_polygon(np.repeat(shrinking.mean(axis=0)[None], 2, axis=0), centers, small, False)
    add('endpoint_inside_but_midpoint_outside', all(x['pass'] for x in ends) and not whole['pass'] and mid['pass'], endpoint_tests=ends, interval_test=whole, midpoint_exterior=mid)
    boundary = box_polygon(poly, np.array([[.95, 0.], [.95, 0.]]), np.array([.1, .1]), True)
    add('interior_center_straddling_box_rejected', not boundary['pass'], interval_test=boundary)

    segment = np.array([[[-1., -1.], [-1., 1.]], [[1., -1.], [1., 1.]]])
    center = np.zeros((2, 2))
    ends = [box_segment(np.repeat(segment[j:j+1], 2, axis=0), center, small) for j in [0, 1]]
    whole = box_segment(segment, center, small)
    add('stem_endpoints_clear_but_interior_crosses', all(x['pass'] for x in ends) and not whole['pass'], endpoint_tests=ends, interval_test=whole)
    endpoint_case = box_segment(np.array([[[0., 0.], [1., 0.]], [[0., 0.], [1., 0.]]]), np.array([[-2., 0.], [-2., 0.]]), np.array([.1, .1]))
    add('stem_endpoint_projection', endpoint_case['pass'] and abs(endpoint_case['clearance_bound']-1.9) < 1e-8, interval_test=endpoint_case)

    pentagon = np.c_[np.cos(np.arange(5)*2*np.pi/5), np.sin(np.arange(5)*2*np.pi/5)]
    star = pentagon[[0, 2, 4, 1, 3]]
    for name, p in [('self_intersecting_star_rejected', star), ('reversed_polygon_rejected', SQUARE[::-1]), ('degenerate_edge_rejected', np.insert(SQUARE, 1, SQUARE[0], axis=0))]:
        res = convex_polygon(np.repeat(p[None], 2, axis=0))
        add(name, not res['pass'], interval_test=res)
    bad = poly.copy(); bad[0, 0, 0] = np.nan
    failure = None
    try:
        convex_polygon(bad)
    except ValueError as e:
        failure = str(e)
    add('nonfinite_geometry_rejected', failure == 'nonfinite_geometry', reason=failure)
    result = {'plan_sha256': sha(ROOT/'PLAN.json'), 'source_hashes': {n: sha(ROOT/n) for n in ['geometry.py', 'controls.py']},
              'controls': records, 'all_controls_pass': all(x['pass'] for x in records)}
    (ROOT/'CONTROLS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    for x in records:
        print(x['name'], x['pass'])
    return 0 if result['all_controls_pass'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
