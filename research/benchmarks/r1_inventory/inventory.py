"""Energy-aware weighted Schur exclusion outside an inherited unique-node core."""
from pathlib import Path
import hashlib
import itertools
import json
import numpy as np
from scipy.linalg import eigh, qr

ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT/'PLAN.json').read_text()); T = PLAN['thresholds']
SIGNS = np.array(list(itertools.product([0, 1], repeat=3)))
COLUMNS = ['u1_lo', 'u2_lo', 'dD_lo', 'u1_hi', 'u2_hi', 'dD_hi',
           'depth', 'parent', 'left', 'right', 'state', 'L', 'W', 'eta',
           'weighted_B_norm', 'correction_upper', 'linear_lower', 'exclusion_margin']
STATES = {0: 'split', 1: 'excluded', -1: 'depth_limit', -2: 'split_budget'}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def components(a):
    return np.array([np.trace(a)/2, (a[0, 0]-a[1, 1])/2, a[0, 1]])

def primitives(family, raw, F):
    D0 = raw['D_meV']; y0 = np.array(raw['y']); v = np.array(raw['velocity'])
    H0 = family.H([*y0[:2], D0]); dim = len(H0)
    for a in [H0, *family.A]:
        if not np.isfinite(a).all() or np.max(abs(np.imag(a))) > T['matrix_tolerance_meV'] or np.max(abs(a-a.T)) > T['matrix_tolerance_meV']:
            raise ValueError('invalid_real_symmetric_family')
    Q = qr(F, mode='full')[0][:, 2:]; W = np.column_stack([F, Q])
    orth = float(np.max(abs(W.T @ W-np.eye(dim))))
    if orth > T['orthogonality_tolerance']:
        raise ValueError('invalid_orthogonal_frame')
    K = Q.T @ H0 @ Q-y0[2]*np.eye(dim-2)
    kw, V = eigh(K)
    G0 = float(np.min(abs(kw))-T['energy_allowance_meV'])
    if G0 <= 0:
        raise ValueError('singular_center_complement')
    direction = family.A[2]+v[0]*family.A[0]+v[1]*family.A[1]
    B = np.array([Q.T @ a @ F for a in [H0, family.A[0], family.A[1], direction]])
    weighted = np.einsum('ab,ibc->iac', V.T, B)/np.sqrt(abs(kw))[None, :, None]
    gram = np.einsum('ika,jkb->ijab', weighted, weighted)
    w5 = eigh(H0, eigvals_only=True, subset_by_index=(raw['lo']-1, raw['lo']+3))
    J = np.column_stack([components(F.T @ a @ F) for a in family.A[:2]]+[components(-np.eye(2))])
    gD = components(F.T @ family.A[2] @ F)
    g0 = components(F.T @ H0 @ F-y0[2]*np.eye(2))
    nv = float(max(abs(eigh(direction-v[2]*np.eye(dim), eigvals_only=True))))+T['norm_allowance']
    axes = [float(max(abs(eigh(a, eigvals_only=True))))+T['norm_allowance'] for a in family.A[:2]]
    return {'D_meV': D0, 'lo': raw['lo'], 'y': raw['y'], 'velocity': raw['velocity'],
            'G0': G0, 'gram': gram.tolist(), 'w5': w5.tolist(), 'J': J.tolist(), 'g0': g0.tolist(),
            'predictor_residual': (gD+J @ v).tolist(), 'axis_norms': axes, 'complement_velocity': nv,
            'center_energy_offset': float(max(abs(w5[1:3]-y0[2]))),
            'orthogonality_error': orth, 'complement_spectrum_error': float(max(abs(kw-raw['complement_eigenvalues_meV'])))}

def correction(p, a, b):
    a, b = np.asarray(a), np.asarray(b)
    extent = np.maximum(abs(a), abs(b))
    L = float(np.dot(extent, [*p['axis_norms'], p['complement_velocity']]))
    W = p['center_energy_offset']+L+T['energy_allowance_meV']
    eta = (L+W)/p['G0']
    gram = np.asarray(p['gram']); largest = 0.
    for s in SIGNS:
        point = a+s*(b-a); coeff = np.r_[1., point]
        block = np.einsum('i,j,ijab->ab', coeff, coeff, gram)
        largest = max(largest, float(np.linalg.eigvalsh((block+block.T)/2)[-1]))
    weighted = np.sqrt(max(0., largest))+T['weighted_norm_allowance_sqrt_meV']
    upper = weighted**2/(1-eta)+T['energy_allowance_meV'] if eta < T['eta_max'] else None
    return {'L': L, 'W': W, 'eta': float(eta), 'weighted_B_norm': float(weighted), 'correction_upper': float(upper) if upper is not None else None}

def affine_minimum(J, offset, lo, hi):
    """Minimum norm on a parallelogram: interior zero or one of four edges."""
    J, offset, lo, hi = map(np.asarray, [J, offset, lo, hi])
    zero = np.linalg.solve(J, -offset)
    if np.all(zero >= lo) and np.all(zero <= hi):
        return 0.
    values = []
    for fixed in [0, 1]:
        free = 1-fixed
        for x in [lo[fixed], hi[fixed]]:
            base = offset+J[:, fixed]*x; direction = J[:, free]
            value = float(np.clip(-(base @ direction)/(direction @ direction), lo[free], hi[free]))
            values.append(float(np.linalg.norm(base+value*direction)))
    return min(values)

def exclude(p, a, b):
    c = correction(p, a, b); J = np.array(p['J'])[1:, :2]
    residual = np.array(p['predictor_residual'])[1:]
    offset = np.array(p['g0'])[1:]+residual*(a[2]+b[2])/2
    lower = max(0., affine_minimum(J, offset, a[:2], b[:2])-(b[2]-a[2])/2*np.linalg.norm(residual)-T['energy_allowance_meV'])
    margin = lower-c['correction_upper'] if c['correction_upper'] is not None else None
    return dict(c, linear_lower=float(lower), exclusion_margin=float(margin) if margin is not None else None,
                **{'pass': bool(margin is not None and margin > T['exclusion_margin_meV'])})

def core_capture(p, radii, h):
    r = np.array(radii); c = correction(p, [-r[0], -r[1], -h], [r[0], r[1], h])
    residual = p['predictor_residual'][0]
    trace = max(abs(p['g0'][0]-h*residual), abs(p['g0'][0]+h*residual))+float(abs(np.array(p['J'])[0, :2]) @ r[:2])
    energy = trace+c['correction_upper'] if c['correction_upper'] is not None else None
    margin = r[2]-energy-T['energy_allowance_meV'] if energy is not None else None
    return dict(c, projected_trace_upper=float(trace), candidate_energy_upper=float(energy) if energy is not None else None,
                parent_energy_radius=float(r[2]), capture_margin=float(margin) if margin is not None else None,
                **{'pass': bool(margin is not None and margin > 0)})

def outer_guard(p, R, h):
    c = correction(p, [-R[0], -R[1], -h], [R[0], R[1], h])
    gaps = np.diff(p['w5'])[[0, 2, 3]]-2*c['L']-T['energy_allowance_meV']
    return {'L': c['L'], 'other_gap_lower_meV': gaps.tolist(), 'pass': bool(min(gaps) > T['gap_margin_meV'])}

def strips(R, core, h):
    x, y = R; rx, ry = core
    if not (0 < rx < x and 0 < ry < y and h > 0):
        raise ValueError('invalid_core_or_outer_domain')
    return [(np.array(a), np.array(b)) for a, b in [
        ([-x, -y, -h], [-rx, y, h]), ([rx, -y, -h], [x, y, h]),
        ([-rx, -y, -h], [rx, -ry, h]), ([-rx, ry, -h], [rx, y, h])]]

def cover(p, R, core, h, limits=None):
    cfg = dict(T, **(limits or {})); rows = []; roots = []; splits_used = 0
    def visit(a, b, depth, parent):
        nonlocal splits_used
        i = len(rows); bound = exclude(p, a, b)
        state = 1 if bound['pass'] else -1 if depth >= cfg['maximum_depth'] else -2 if splits_used >= cfg['maximum_split_nodes_per_reference'] else 0
        scalar = [bound[k] if bound[k] is not None else np.nan for k in ['L', 'W', 'eta', 'weighted_B_norm', 'correction_upper', 'linear_lower', 'exclusion_margin']]
        rows.append([*a, *b, depth, parent, -1, -1, state, *scalar])
        if state == 0:
            splits_used += 1
            axis = int(np.argmax((b-a)*np.array([*p['axis_norms'], p['complement_velocity']])))
            mid = (a[axis]+b[axis])/2
            lb = b.copy(); lb[axis] = mid; ra = a.copy(); ra[axis] = mid
            left = visit(a, lb, depth+1, i); right = visit(ra, b, depth+1, i)
            rows[i][8:10] = [left, right]
        return i
    for a, b in strips(R, core, h):
        roots.append(visit(a, b, 0, -1))
    rows = np.array(rows, dtype=float); leaves = rows[rows[:, 10] != 0]
    return rows, {'root_indices': roots, 'attempts': len(rows), 'leaves': len(leaves), 'split_nodes': splits_used,
                  'unresolved_leaves': int(np.sum(leaves[:, 10] != 1)), 'pass': bool(np.all(leaves[:, 10] == 1)),
                  'minimum_accepted_exclusion_margin_meV': float(np.min(leaves[leaves[:, 10] == 1, 17])) if np.any(leaves[:, 10] == 1) else None,
                  'maximum_depth': int(max(rows[:, 6]))}
