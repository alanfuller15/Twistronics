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
from primitives_s0f import enclosure, frobenius, identity, midpoint_matrix, NonfiniteEnclosure, inertia_ldl
from functools import wraps

_prior_spec = importlib.util.spec_from_file_location('_s0f_pair', Path(__file__).resolve().parent/'pair_s0f.py')
_prior = importlib.util.module_from_spec(_prior_spec)
_prior_spec.loader.exec_module(_prior)
if _prior.inertia_ldl is not inertia_ldl:
    raise ImportError("S0f reused inertia identity mismatch")

def certified_boundary(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except NonfiniteEnclosure as exc:
            return {'status': 'INCONCLUSIVE', 'reason': 'NONFINITE_ENCLOSURE',
                    'arithmetic_message': str(exc)}
    return wrapped


@certified_boundary
def finite_growth(kind):
    # A finite input overflows the backend; both primitive paths are exercised.
    x = arb('1e100').exp()
    if kind == 'bound':
        return enclosure(x)
    if kind == 'ldl':
        return inertia_ldl(arb_mat([[x]]))
    raise ValueError('unknown finite-growth control')



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


def seam_map(left, shift, right, gram_tolerance, map_target):
    """Caller binds both frames to consistent rectangle orientations.

    det(M)>0 has the intended orientation meaning only under this premise.
    """
    if left.ncols() != 2 or right.ncols() != 2 or shift.nrows() != left.nrows() or shift.ncols() != right.nrows():
        raise ValueError('compatible F1,S,F0 dimensions required')
    if not all(finite_matrix(x) for x in (left, shift, right)):
        raise ValueError('finite F1,S,F0 required')
    gl = frobenius(left.transpose()*left-identity(2))
    gr = frobenius(right.transpose()*right-identity(2))
    if not gl < arb(gram_tolerance) or not gr < arb(gram_tolerance):
        return {'status': 'INCONCLUSIVE', 'reason': 'FRAME_GRAM_SANITY_NOT_CERTIFIED'}
    m = left.transpose()*shift*right
    polar = polar_so2(m, map_target)
    if polar['status'] != 'CERTIFIED':
        return {k:v for k,v in polar.items() if not k.startswith('_')}
    # Sufficient operator bound: ||I-M^T M||_2 <= ||I-M^T M||_F.
    # rho <= 1-(19/20)^2 implies every singular value >= 19/20.
    rho = frobenius(identity(2)-m.transpose()*m)
    record = {'overlap_built_internally': True, 'singular_square_defect_F': enclosure(rho),
              'singular_gate_threshold': enclosure(arb(39)/400),
              'left_Gram_defect_F': enclosure(gl), 'right_Gram_defect_F': enclosure(gr)}
    if not rho <= arb(39)/400:
        return {**record, 'status': 'INCONCLUSIVE', 'reason': 'SEAM_SINGULAR_GATE_NOT_CERTIFIED'}
    seam = left*polar['_polar']*right.transpose()
    _, error = midpoint_matrix(seam)
    record['seam_map_error_F_bound'] = enclosure(error)
    if not error < arb(map_target):
        return {**record, 'status': 'INCONCLUSIVE', 'reason': 'SEAM_MAP_ERROR_BUDGET'}
    return {**record, 'status': 'CERTIFIED', 'reason': 'PARTIAL_SHIFT_SEAM_ENCLOSURE'}


def continuous_phase_lift(samples, step_cos_floor, closure_target, *, exact_closure_declared=False, variation_certified=False):
    if exact_closure_declared is not True or variation_certified is not True:
        return {"status": "INCONCLUSIVE", "reason": "UPSTREAM_PATH_CERTIFICATE_REQUIRED"}
    if not arb(step_cos_floor).is_finite() or not arb(step_cos_floor) >= 0:
        raise ValueError("finite nonnegative dot floor required")
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
    if not lo <= integer <= hi:
        return {**record, 'status': 'INCONCLUSIVE', 'reason': 'INTEGER_OUTSIDE_ENCLOSURE'}
    if (hi-lo)/2 > Fraction(1, 8):
        return {**record, 'status': 'INCONCLUSIVE', 'reason': 'INTEGER_HALFWIDTH_EXCEEDED'}
    if not lo > integer-Fraction(1, 2) or not hi < integer+Fraction(1, 2):
        return {**record, 'status': 'INCONCLUSIVE', 'reason': 'UNIQUE_INTEGER_NOT_CERTIFIED'}
    return {**record, 'status': 'CERTIFIED', 'reason': 'CONTINUOUS_PHASE_LIFT',
            'certified_integer': integer}


COMPOSITION_REASONS = {
    'projector': 'RIESZ_PROJECTOR_ENCLOSURE',
    'seam': 'PARTIAL_SHIFT_SEAM_ENCLOSURE',
    'lift': 'CONTINUOUS_PHASE_LIFT',
}


def composition_admissibility(records):
    """Reason gate only, not a final q certificate or proof of provenance."""
    if set(records) != set(COMPOSITION_REASONS):
        raise ValueError('exact composition roles required')
    for role, reason in COMPOSITION_REASONS.items():
        if records[role].get('status') != 'CERTIFIED' or records[role].get('reason') != reason:
            return {'status': 'INCONCLUSIVE', 'reason': 'COMPOSITION_REASON_REFUSED', 'role': role}
    return {'status': 'CERTIFIED', 'reason': 'SYNTHETIC_REASON_GATE_ONLY'}

# All public arithmetic entry points classify only dedicated enclosure failures.
for _name in ('conditional_budget', 'approximate_branch_gate', 'pair_from_enclosed_inputs',
              'riesz_circle', 'polar_so2', 'seam_map', 'continuous_phase_lift'):
    globals()[_name] = certified_boundary(globals()[_name])
