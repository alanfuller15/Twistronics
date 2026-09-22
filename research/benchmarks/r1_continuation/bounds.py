"""Conditional Schur-complement contraction bounds, in (f1,f2,E)."""
from pathlib import Path
import hashlib
import json
import numpy as np
from scipy.linalg import eigh, qr

ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT / 'PLAN.json').read_text())
CFG = PLAN['bounds']

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def components(a):
    return np.array([np.trace(a)/2, (a[0, 0]-a[1, 1])/2, a[0, 1]])

def opnorm(a):
    return float(np.linalg.svd(a, compute_uv=False)[0])

def symnorm(a):
    return float(np.max(np.abs(eigh(a, eigvals_only=True))))

def center_data(family, D, lo, f, frame=None):
    """Numerical primitives; their enclosure status is explicitly conditional."""
    for a in [family.h0, *family.A]:
        if not np.isfinite(a).all() or np.max(np.abs(np.imag(a))) > CFG['matrix_tolerance_meV']:
            raise ValueError('nonfinite_or_nonreal_coefficients')
        if np.max(np.abs(a-a.T)) > CFG['matrix_tolerance_meV']:
            raise ValueError('nonsymmetric_coefficients')
    H = np.real(family.H([*f, D]))
    w, V = eigh(H, subset_by_index=(lo-1, lo+2))
    F = qr(V[:, 1:3], mode='full')[0][:, :2] if frame is None else np.array(frame)
    # QR completion need not preserve column signs: keep F, use only its complement.
    Q = qr(F, mode='full')[0][:, 2:]
    W = np.column_stack([F, Q])
    orth = float(np.max(np.abs(W.T @ W - np.eye(family.dim))))
    if orth > CFG['orthogonality_tolerance']:
        raise ValueError('nonorthogonal_frame')
    E = float(np.trace(F.T @ H @ F)/2)
    K = Q.T @ H @ Q - E*np.eye(family.dim-2)
    kw = eigh(K, eigvals_only=True)
    J = np.column_stack([components(F.T @ a @ F) for a in family.A[:2]] + [components(-np.eye(2))])
    sv = np.linalg.svd(J, compute_uv=False)
    if sv[-1] < CFG['inverse_smin_min']:
        raise ValueError('singular_projected_map')
    C = np.linalg.inv(J)
    gD = components(F.T @ family.A[2] @ F)
    velocity = -C @ gD
    T = family.A[2] + velocity[0]*family.A[0] + velocity[1]*family.A[1]
    pad = CFG['norm_allowance']
    raw = {
        'D_meV': float(D), 'lo': int(lo), 'y': [*map(float, f), E],
        'w4': w.tolist(), 'frame_orthogonality_error': orth,
        'complement_eigenvalues_meV': kw.tolist(),
        'inertia': [int(np.sum(kw < 0)), int(np.sum(kw > 0))],
        'inertia_correct': bool(np.sum(kw < 0) == lo and np.sum(kw > 0) == family.dim-lo-2),
        'g0': components(F.T @ H @ F - E*np.eye(2)).tolist(),
        'J': J.tolist(), 'C': C.tolist(), 'gD': gD.tolist(), 'velocity': velocity.tolist(),
        'J_singular_values': sv.tolist(),
        'G0': float(np.min(np.abs(kw))-CFG['energy_allowance_meV']),
        'cross_center': opnorm(Q.T @ H @ F)+pad,
        'cross_axes': [opnorm(Q.T @ a @ F)+pad for a in family.A[:2]],
        'axis_norms': [symnorm(a)+pad for a in family.A[:2]],
        'cross_velocity': opnorm(Q.T @ T @ F)+pad,
        'complement_velocity': symnorm(T-velocity[2]*np.eye(family.dim))+pad
    }
    return raw, F

def certificate(raw, halfwidth, *, radius_override=None):
    """Uniform moving-box bound. Override exists solely for adversarial controls."""
    h = float(halfwidth)
    out = {'halfwidth': h, 'pass': False, 'reason': None}
    C, J = np.array(raw['C']), np.array(raw['J'])
    c = np.sum(np.abs(C), axis=1)
    Gline = raw['G0']-h*raw['complement_velocity']
    bline = raw['cross_center']+h*raw['cross_velocity']
    out.update(Gline=Gline, bline=bline)
    if not raw['inertia_correct'] or Gline <= CFG['complement_margin_meV']:
        out['reason'] = 'complement_line_or_inertia'
        return out
    linear_residual = np.array(raw['gD'])+J @ np.array(raw['velocity'])
    Y = np.abs(C @ raw['g0']) + h*np.abs(C @ linear_residual)
    Y += c*(bline*bline/Gline+CFG['energy_allowance_meV'])
    rho = max(CFG['minimum_rho_meV'], CFG['radius_factor']*float(np.max(Y/c)))
    r = rho*c if radius_override is None else np.array(radius_override, float)
    a, b = np.array(raw['axis_norms']), np.array(raw['cross_axes'])
    G = Gline-float(a @ r[:2])-r[2]
    B = bline+float(b @ r[:2])
    out.update(Y=Y.tolist(), rho_meV=rho, radii=r.tolist(), Gfull=G, bfull=B)
    if not np.isfinite(r).all() or np.any(r <= 0) or G <= CFG['complement_margin_meV']:
        out['reason'] = 'complement_tube'
        return out
    nonlinear = np.r_[2*b*B/G+B*B*a/G**2, B*B/G**2]
    inverse_error = np.abs(np.eye(3)-C @ J)+CFG['dimensionless_allowance']
    qrows = (inverse_error @ r + c*float(nonlinear @ r))/r
    q, ynorm = float(np.max(qrows)), float(np.max(Y/r))
    beta = ynorm/(1-q) if q < 1 else None
    ok = q <= CFG['contraction_max'] and ynorm+q <= CFG['self_map_max']
    out.update(nonlinear_derivative=nonlinear.tolist(), contraction_rows=qrows.tolist(),
               q=q, Ynorm=ynorm, self_map=ynorm+q, beta=beta,
               inner_radii=(beta*r).tolist() if beta is not None else None,
               **{'pass': bool(ok), 'reason': 'accepted' if ok else 'contraction_or_self_map'})
    return out

def enclosure(raw, cert, D, inner=False):
    center = np.array(raw['y'])+(D-raw['D_meV'])*np.array(raw['velocity'])
    radii = np.array(cert['inner_radii' if inner else 'radii'])
    return center-radii, center+radii

def containment(point_raw, point_cert, tube_raw, tube_cert, D):
    if not point_cert['pass'] or not tube_cert['pass']:
        return {'pass': False, 'reason': 'unaccepted_certificate'}
    pl, pu = enclosure(point_raw, point_cert, D, inner=True)
    tl, tu = enclosure(tube_raw, tube_cert, D)
    margins = np.minimum(pl-tl, tu-pu)
    return {'pass': bool(np.min(margins) > 0), 'margins': margins.tolist(),
            'reason': 'strict_containment' if np.min(margins) > 0 else 'point_enclosure_not_contained'}

def separation(raw1, cert1, raw2, cert2, a, b):
    """At least one momentum coordinate separates boxes over all of [a,b]."""
    differences = []
    for D in [a, b]:
        c1 = np.array(raw1['y'])+(D-raw1['D_meV'])*np.array(raw1['velocity'])
        c2 = np.array(raw2['y'])+(D-raw2['D_meV'])*np.array(raw2['velocity'])
        differences.append(c2[:2]-c1[:2])
    delta = np.array(differences)
    radius = np.array(cert1['radii'][:2])+np.array(cert2['radii'][:2])
    margins = np.maximum(np.min(delta, axis=0), np.min(-delta, axis=0))-radius
    return {'pass': bool(np.max(margins) > 0), 'axis_margins': margins.tolist(),
            'separating_axis': int(np.argmax(margins))}
