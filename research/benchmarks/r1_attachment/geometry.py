"""Uniform geometry bounds on affine moving polygons, boxes and segments."""
from pathlib import Path
import hashlib
import json
import itertools
import numpy as np

ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT/'PLAN.json').read_text())
T = PLAN['thresholds']
SIGNS = np.array(list(itertools.product([-1., 1.], repeat=2)))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def cross(a, b):
    return a[..., 0]*b[..., 1]-a[..., 1]*b[..., 0]

def guard(*arrays):
    if not all(np.isfinite(a).all() for a in arrays):
        raise ValueError('nonfinite_geometry')

def side_coefficients(polygon, points):
    """Inputs (2,N,2), (2,M,2); output (N,M,3) Bernstein coefficients."""
    polygon, points = np.asarray(polygon), np.asarray(points)
    guard(polygon, points)
    edge = np.roll(polygon, -1, axis=1)-polygon
    z = points[:, None, :, :]-polygon[:, :, None, :]
    b0 = cross(edge[0, :, None, :], z[0])
    b1 = (cross(edge[0, :, None, :], z[1])+cross(edge[1, :, None, :], z[0]))/2
    b2 = cross(edge[1, :, None, :], z[1])
    length_upper = np.max(np.linalg.norm(edge, axis=2), axis=0)+T['length_allowance']
    return np.stack([b0, b1, b2], axis=-1), length_upper

def convex_polygon(polygon):
    p = np.asarray(polygon, float)
    if p.ndim != 3 or p.shape[0] != 2 or p.shape[2] != 2 or p.shape[1] < 3:
        raise ValueError('invalid_polygon_shape')
    coeff, lengths = side_coefficients(p, p)
    n = p.shape[1]
    mask = np.ones((n, n), dtype=bool)
    for i in range(n):
        mask[i, i] = mask[i, (i+1) % n] = False
    scores = np.where(mask[:, :, None], coeff, np.inf)
    index = np.unravel_index(np.argmin(scores), scores.shape)
    lower = float(scores[index]-T['area_allowance'])
    return {'pass': bool(lower > 0), 'minimum_oriented_area': lower,
            'witness_edge_vertex_coefficient': list(map(int, index)),
            'maximum_edge_length': float(max(lengths))}

def box_polygon(polygon, centers, radii, inside):
    p, c, r = np.asarray(polygon), np.asarray(centers), np.asarray(radii)
    guard(p, c, r)
    if c.shape != (2, 2) or r.shape != (2,) or np.any(r < 0):
        raise ValueError('invalid_box')
    corners = c[:, None, :]+SIGNS[None, :, :]*r
    coeff, lengths = side_coefficients(p, corners)
    if inside:
        scores = (coeff-T['area_allowance'])/lengths[:, None, None]-T['length_allowance']
        index = np.unravel_index(np.argmin(scores), scores.shape)
        margin = float(scores[index])
        witness = list(map(int, index))
    else:
        # Select ONE edge that separates ALL corners over the WHOLE interval.
        scores = (-coeff-T['area_allowance'])/lengths[:, None, None]-T['length_allowance']
        edge_margin = np.min(scores, axis=(1, 2))
        edge = int(np.argmax(edge_margin))
        corner, coefficient = np.unravel_index(np.argmin(scores[edge]), scores[edge].shape)
        margin = float(edge_margin[edge])
        witness = [edge, int(corner), int(coefficient)]
    return {'pass': bool(margin > T['minimum_clearance']), 'relation': 'inside' if inside else 'outside',
            'clearance_bound': margin, 'witness_edge_corner_coefficient': witness}

def box_segment(segment, centers, radii):
    """A fixed projection axis excludes a moving segment from a moving box."""
    s, c, r = np.asarray(segment), np.asarray(centers), np.asarray(radii)
    guard(s, c, r)
    if s.shape != (2, 2, 2) or c.shape != (2, 2) or r.shape != (2,) or np.any(r < 0):
        raise ValueError('invalid_segment_or_box')
    endpoints, center = s.mean(axis=0), c.mean(axis=0)
    edge = endpoints[1]-endpoints[0]
    length2 = float(edge @ edge)
    u = float(np.clip((center-endpoints[0]) @ edge/length2, 0, 1)) if length2 else 0.
    direction = endpoints[0]+u*edge-center
    length = float(np.linalg.norm(direction))
    if length <= T['minimum_axis_length']:
        return {'pass': False, 'reason': 'no_midpoint_separating_axis', 'axis': None,
                'clearance_bound': None, 'midpoint_segment_parameter': u}
    axis = direction/length
    projections = np.einsum('tek,k->te', s-c[:, None, :], axis)
    lower = (float(np.min(projections))-float(np.abs(axis) @ r))/(float(np.linalg.norm(axis))+T['length_allowance'])-T['length_allowance']
    index = np.unravel_index(np.argmin(projections), projections.shape)
    return {'pass': bool(lower > T['minimum_clearance']), 'reason': 'separating_axis_bound',
            'axis': axis.tolist(), 'clearance_bound': lower, 'midpoint_segment_parameter': u,
            'witness_D_endpoint_segment_endpoint': list(map(int, index))}

def evaluate(vertices, boxes):
    """vertices=(D endpoint, base/kink/closed ring, xy); boxes keyed by node."""
    vertices = np.array(vertices)
    guard(vertices)
    if not np.array_equal(vertices[:, 2], vertices[:, -1]):
        raise ValueError('unclosed_polygon')
    ring = vertices[:, 2:-1]
    convex = convex_polygon(ring)
    nodes = {}
    for name, box in boxes.items():
        nodes[name] = {'polygon': box_polygon(ring, box['centers'], box['radii'], name == PLAN['inside_node']),
                       'stems': [box_segment(vertices[:, k:k+2], box['centers'], box['radii']) for k in [0, 1]]}
    ok = convex['pass'] and all(n['polygon']['pass'] and all(s['pass'] for s in n['stems']) for n in nodes.values())
    return {'pass': bool(ok), 'convex_polygon': convex, 'nodes': nodes}
