"""Frozen S0d synthetic fixtures, separate from certification decisions."""
from pathlib import Path
import sys

from flint import arb, arb_mat

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'certification_s0a_001'))
from primitives import enclosure, frobenius, householder, identity
from certified import (approximate_branch_gate, conditional_budget,
                       continuous_phase_lift, pair_from_enclosed_inputs,
                       polar_so2, riesz_circle, seam_map)


def diagonal(values):
    return arb_mat([[values[i] if i == j else 0 for j in range(len(values))]
                    for i in range(len(values))])


def selections(labels, windows):
    out = []
    for window in windows:
        for raw in window:
            shift = arb(raw)
            below = sorted([i for i, d in enumerate(labels) if arb(d) < shift],
                           key=lambda i: (abs(difference(labels[i], raw)), i))[:2]
            above = sorted([i for i, d in enumerate(labels) if arb(d) > shift],
                           key=lambda i: (abs(difference(labels[i], raw)), i))[:2]
            out.append(below+above)
    return out


def difference(a, b):
    from fractions import Fraction
    return Fraction(a)-Fraction(b)


def enclosed_frame(theta, radius):
    c, s, r = arb(theta).cos(), arb(theta).sin(), arb(radius)
    return arb_mat([[arb(c, r), arb(-s, r)],
                    [arb(s, r), arb(c, r)],
                    [arb(0, r), arb(0, r)]])


def phase_samples(count, radius):
    r = arb(radius)
    return [[arb((2*arb.pi()*k/count).cos(), r),
             arb((2*arb.pi()*k/count).sin(), r)] for k in range(count+1)]


def projector_fixture(job):
    _, _, q = householder(6)
    values = [-3, -2, 0, 0, 2, 3]
    h = q*diagonal(values)*q.transpose()
    out = riesz_circle(h, '0', '1', job['nodes'], job['inner_ratio'],
                       job['outer_ratio'], job['target_error'])
    center = out.pop('_center')
    target = arb_mat([[q[i, j] for j in (2, 3)] for i in range(6)])
    complement = arb_mat([[q[i, j] for j in (0, 1, 4, 5)] for i in range(6)])
    out.update({'fixture_target_action_F_bound': enclosure(frobenius(center*target-target)),
                'fixture_complement_action_F_bound': enclosure(frobenius(center*complement)),
                'fixture_spectrum': values, 'fixture_target_indices': [2, 3]})
    return out


def _run(job, spec):
    kind = job['kind']
    if kind == 'budget':
        l = spec['ledger']
        return conditional_budget(l['frame_error'], l['seam_map_error'],
                                  l['repair_angle_error'], l['additional_phase_error'],
                                  l['q_halfwidth'])
    if kind == 'branch':
        return approximate_branch_gate(job['distance'], spec['ledger']['seam_map_error'],
                                       spec['ledger']['repair_angle_error'])
    if kind == 'congruence':
        labels = [-4, -3, 0, 0, 3, 4]
        return pair_from_enclosed_inputs(identity(6), diagonal(labels), arb_mat(6, 6),
                                         '0', spec['windows'], selections(labels, spec['windows']), [2, 3])
    if kind == 'shape_fault':
        return pair_from_enclosed_inputs(arb_mat(6, 5), identity(6), arb_mat(6, 6),
                                         '0', spec['windows'], [[0, 1, 2, 3]]*4, [2, 3])
    if kind == 'nonfinite':
        # Finite input whose enclosure operation grows beyond the backend's
        # representable range; this exercises numerical growth, not bad schema.
        return {'unreachable': enclosure(arb('1e100').exp())}
    if kind == 'projector':
        return projector_fixture(job)
    if kind == 'seam':
        return seam_map(enclosed_frame('0', job['entry_radius']),
                        enclosed_frame('1/5', job['entry_radius']),
                        spec['ledger']['frame_error'], job['target_error'])
    if kind == 'polar_singular':
        out = polar_so2(diagonal([1, -1]), '1/128')
        return {k: v for k, v in out.items() if not k.startswith('_')}
    if kind == 'phase':
        return continuous_phase_lift(phase_samples(job['samples'], job['entry_radius']),
                                     '1/2', '1/64')
    if kind == 'phase_branch':
        return continuous_phase_lift([[arb(1), arb(0)], [arb(-1), arb(0)]], '0', '1/64')
    if kind == 'phase_ambiguous':
        return continuous_phase_lift(phase_samples(job['samples'], job['entry_radius']),
                                     '0', '1/2')
    raise ValueError('unknown fixed fixture kind')


def run(job, spec):
    try:
        return _run(job, spec)
    except ArithmeticError as exc:
        if str(exc) in {'nonfinite bound', 'nonfinite LDL pivot'}:
            return {'status': 'INCONCLUSIVE', 'reason': 'NONFINITE_ENCLOSURE',
                    'arithmetic_message': str(exc)}
        raise
