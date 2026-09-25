"""Bounded synthetic certification primitives; no physical-model imports.

The Riesz routine uses the roots-of-unity trapezoid identity
Q_N=(I-((H-cI)/r)^N)^-1.  For a self-adjoint H with target spectrum at
|lambda-c|/r <= alpha < 1 and all other spectrum at >= beta > 1, its
operator error is bounded by alpha^N/(1-alpha^N)+1/(beta^N-1).
The spectral split is an explicit caller obligation and is independently
checked for the fixed synthetic fixtures.
"""
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys

from flint import arb, arb_mat

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'certification_s0a_001'))
from primitives import enclosure, frobenius, identity, midpoint_matrix

_prior_spec = importlib.util.spec_from_file_location('_s0c_certified', ROOT/'certification_s0c_001'/'certified.py')
_prior = importlib.util.module_from_spec(_prior_spec)
_prior_spec.loader.exec_module(_prior)

RECOGNIZED_NONFINITE = {'nonfinite bound', 'nonfinite LDL pivot'}


def finite_matrix(a):
    return all(a[i, j].is_finite() for i in range(a.nrows()) for j in range(a.ncols()))


def fraction_bounds(x):
    def value(y):
        m, e = y.man_exp()
        return Fraction(int(m))*Fraction(2)**int(e)
    return value(x.lower()), value(x.upper())


def conditional_budget(frame, seam, repair, extra, target):
    out = _prior.ledger(frame, seam, repair, extra, target)
    if out['status'] == 'CERTIFIED':
        out['reason'] = 'BUDGET_CONDITIONALLY_SUFFICIENT'
    return out


def approximate_branch_gate(distance, seam_error, corner_angle):
    d, eta, rho = map(arb, (distance, seam_error, corner_angle))
    if any(not x.is_finite() for x in (d, eta, rho)) or d < 0 or eta < 0 or rho < 0:
        raise ValueError('finite nonnegative branch inputs required')
    b = 2*eta+eta**2
    charged = d+2*b
    record = {'approximate_path_distance': enclosure(d), 'single_path_error': enclosure(b),
              'charged_exact_path_distance': enclosure(charged),
              'required_approximate_distance_max': enclosure(1-2*b)}
    if not charged <= 1:
        return {**record, 'status': 'INCONCLUSIVE',
                'reason': 'APPROXIMATE_BRANCH_MARGIN_NOT_CERTIFIED'}
    exact_angle = arb.pi()/3
    separation = arb.pi()-(exact_angle+rho)
    record.update({'exact_corner_angle_bound': enclosure(exact_angle),
                   'branch_separation_after_corner_error': enclosure(separation)})
    if not separation > 0:
        return {**record, 'status': 'INCONCLUSIVE', 'reason': 'BRANCH_SEPARATION_NOT_CERTIFIED'}
    return {**record, 'status': 'CERTIFIED', 'reason': 'APPROXIMATE_BRANCH_GATE'}


def pair_from_enclosed_inputs(v, h0, hx, width, windows, selections, pair):
    n = v.nrows()
    if v.ncols() != n or any(a.nrows() != n or a.ncols() != n for a in (h0, hx)):
        raise ValueError('one square V,H0,Hx tuple with equal dimensions required')
    if not all(finite_matrix(a) for a in (v, h0, hx)):
        raise ValueError('finite enclosed V,H0,Hx required')
    gram = v.transpose()*v
    k0 = v.transpose()*h0*v
    kx = v.transpose()*hx*v
    out = _prior.certify_pair(k0, kx, gram, width, windows, selections, pair)
    out.update({'congruence_built_internally': True,
                'congruence_inputs': ['V', 'H0', 'Hx'],
                'congruence_outputs': ['V^T H0 V', 'V^T Hx V', 'V^T V']})
    return out


def riesz_circle(h, center, radius, nodes, inner_ratio, outer_ratio, target_error):
    n = h.nrows()
    if h.ncols() != n or not finite_matrix(h):
        raise ValueError('finite square self-adjoint enclosure required')
    if type(nodes) is not int or nodes < 2:
        raise ValueError('at least two fixed quadrature nodes required')
    c, r = arb(center), arb(radius)
    alpha, beta, target = map(arb, (inner_ratio, outer_ratio, target_error))
    if not r > 0 or not alpha >= 0 or not alpha < 1 or not beta > 1 or not target > 0:
        raise ValueError('positive radius/error and separated spectral ratios required')
    x = (h-c*identity(n))/r
    try:
        q = (identity(n)-x**nodes).inv()
    except ZeroDivisionError:
        return {'status': 'INCONCLUSIVE', 'reason': 'QUADRATURE_INVERSE_NOT_CERTIFIED',
                'nodes': nodes}
    center_q, rounding = midpoint_matrix(q)
    inside = alpha**nodes/(1-alpha**nodes)
    outside = 1/(beta**nodes-1)
    analytic = inside+outside
    total = analytic+rounding
    record = {'nodes': nodes, 'quadrature_identity': 'roots_of_unity_trapezoid',
              'inner_ratio_bound': enclosure(alpha), 'outer_ratio_bound': enclosure(beta),
              'analytic_operator_error_bound': enclosure(analytic),
              'interval_rounding_F_bound': enclosure(rounding),
              'total_projector_operator_error_bound': enclosure(total),
              'symmetry_defect_F_bound': enclosure(frobenius(center_q-center_q.transpose())),
              'target_error': str(target_error)}
    reason = 'RIESZ_PROJECTOR_ENCLOSURE' if total < target else 'PROJECTOR_ERROR_BUDGET'
    status = 'CERTIFIED' if total < target else 'INCONCLUSIVE'
    return {**record, 'status': status, 'reason': reason, '_center': center_q}


def polar_so2(m, target_error):
    if m.nrows() != 2 or m.ncols() != 2 or not finite_matrix(m):
        raise ValueError('finite 2x2 overlap enclosure required')
    a, b = m[0, 0]+m[1, 1], m[1, 0]-m[0, 1]
    denominator2 = a*a+b*b
    record = {'conformal_denominator_squared': enclosure(denominator2)}
    if not denominator2 > 0:
        return {**record, 'status': 'INCONCLUSIVE',
                'reason': 'POLAR_DENOMINATOR_NOT_CERTIFIED'}
    determinant = m[0, 0]*m[1, 1]-m[0, 1]*m[1, 0]
    record['overlap_determinant'] = enclosure(determinant)
    if not determinant > 0:
        return {**record, 'status': 'INCONCLUSIVE',
                'reason': 'POLAR_ORIENTATION_NOT_CERTIFIED'}
    d = denominator2.sqrt()
    u = arb_mat([[a/d, -b/d], [b/d, a/d]])
    center_u, rounding = midpoint_matrix(u)
    defect = frobenius(identity(2)-center_u.transpose()*center_u)
    target = arb(target_error)
    record.update({'polar_rounding_F_bound': enclosure(rounding),
                   'center_orthogonality_defect_F_bound': enclosure(defect),
                   'target_error': str(target_error)})
    if not rounding < target:
        return {**record, 'status': 'INCONCLUSIVE', 'reason': 'POLAR_ERROR_BUDGET'}
    return {**record, 'status': 'CERTIFIED', 'reason': 'POLAR_SO2_ENCLOSURE',
            '_polar': u, '_polar_center': center_u}


def seam_map(left, right, frame_target, map_target):
    if left.nrows() != right.nrows() or left.ncols() != 2 or right.ncols() != 2:
        raise ValueError('equal ambient-by-two frame enclosures required')
    if not finite_matrix(left) or not finite_matrix(right):
        raise ValueError('finite frame enclosures required')
    gl = frobenius(left.transpose()*left-identity(2))
    gr = frobenius(right.transpose()*right-identity(2))
    record = {'left_Gram_defect_F_bound': enclosure(gl),
              'right_Gram_defect_F_bound': enclosure(gr),
              'overlap_built_internally': True}
    if not gl < arb(frame_target) or not gr < arb(frame_target):
        return {**record, 'status': 'INCONCLUSIVE',
                'reason': 'FRAME_ORTHONORMALITY_NOT_CERTIFIED'}
    polar = polar_so2(left.transpose()*right, map_target)
    record['polar'] = {k: v for k, v in polar.items() if not k.startswith('_')}
    if polar['status'] != 'CERTIFIED':
        return {**record, 'status': polar['status'], 'reason': polar['reason']}
    seam = left*polar['_polar']*right.transpose()
    seam_center, seam_error = midpoint_matrix(seam)
    record.update({'seam_map_error_F_bound': enclosure(seam_error),
                   'seam_center_symmetry_defect_F_bound': enclosure(frobenius(seam_center-seam_center.transpose())),
                   'target_error': str(map_target)})
    if not seam_error < arb(map_target):
        return {**record, 'status': 'INCONCLUSIVE', 'reason': 'SEAM_MAP_ERROR_BUDGET'}
    return {**record, 'status': 'CERTIFIED', 'reason': 'SEAM_MAP_ENCLOSURE'}


def continuous_phase_lift(samples, step_cos_floor, closure_target):
    if len(samples) < 2:
        raise ValueError('at least two ordered phase samples required')
    if any(len(z) != 2 or any(not x.is_finite() for x in z) for z in samples):
        raise ValueError('finite two-component phase samples required')
    increments, total = [], arb(0)
    for z in samples:
        norm2 = z[0]*z[0]+z[1]*z[1]
        if not norm2 > arb('1/2'):
            return {'status': 'INCONCLUSIVE', 'reason': 'PHASE_SAMPLE_NOT_SEPARATED'}
    for left, right in zip(samples[:-1], samples[1:]):
        dot = left[0]*right[0]+left[1]*right[1]
        cross = left[0]*right[1]-left[1]*right[0]
        if not dot > arb(step_cos_floor):
            return {'status': 'INCONCLUSIVE', 'reason': 'PHASE_STEP_BRANCH_NOT_SEPARATED',
                    'completed_steps': len(increments), 'failed_dot_bound': enclosure(dot)}
        angle = (cross/dot).atan()
        increments.append({'dot': enclosure(dot), 'angle': enclosure(angle)})
        total += angle
    first, last = samples[0], samples[-1]
    dot = first[0]*last[0]+first[1]*last[1]
    cross = first[0]*last[1]-first[1]*last[0]
    if not dot > 0:
        return {'status': 'INCONCLUSIVE', 'reason': 'ENDPOINT_BRANCH_NOT_SEPARATED'}
    closure = (cross/dot).atan()
    if not closure.abs_upper() < arb(closure_target):
        return {'status': 'INCONCLUSIVE', 'reason': 'ENDPOINT_CLOSURE_NOT_CERTIFIED',
                'closure_angle_bound': enclosure(closure)}
    winding = total/(2*arb.pi())
    lo, hi = fraction_bounds(winding)
    midpoint = (lo+hi)/2
    integer = (midpoint+Fraction(1, 2)).numerator//(midpoint+Fraction(1, 2)).denominator
    record = {'increments': increments, 'lift_total_angle': enclosure(total),
              'winding_interval': enclosure(winding), 'closure_angle_bound': enclosure(closure),
              'candidate_integer': integer}
    if not lo > integer-Fraction(1, 2) or not hi < integer+Fraction(1, 2):
        return {**record, 'status': 'INCONCLUSIVE', 'reason': 'UNIQUE_INTEGER_NOT_CERTIFIED'}
    return {**record, 'status': 'CERTIFIED', 'reason': 'CONTINUOUS_PHASE_LIFT',
            'certified_integer': integer}
