"""Winding sewing on the reviewed analytic rectangle; no physical model."""
import hashlib
import importlib.util
from fractions import Fraction as F
from pathlib import Path
from flint import arb, arb_mat
from primitives_s0f import enclosure, frobenius, NonfiniteEnclosure
from certified_s0f import fraction_bounds

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('s0h_geometry', HERE.parent/'certification_s0h_001/cases.py')
prior = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prior)
require, Refusal, aa, rot, chi = prior.require, prior.Refusal, prior.aa, prior.rot, prior.chi
N = 64


def polar(m):
    """SO(2) polar without an absolute-angle restriction."""
    require(m.det() > 0, 'POLAR_ORIENTATION')
    a, b = m[0, 0]+m[1, 1], m[1, 0]-m[0, 1]
    d2 = a*a+b*b
    require(d2 > 0, 'POLAR_DENOMINATOR')
    d = d2.sqrt()
    return arb_mat([[a/d, -b/d], [b/d, a/d]])


def integer_from_enclosure(value):
    lo, hi = fraction_bounds(value)
    first = -((-lo.numerator)//lo.denominator)
    last = hi.numerator//hi.denominator
    require(first <= last, 'INTEGER_OUTSIDE_ENCLOSURE')
    require(first == last, 'INTEGER_NOT_UNIQUE')
    require((hi-lo)/2 <= F(1, 8), 'INTEGER_HALFWIDTH')
    return first


class WindingGeometry(prior.Geometry):
    def __init__(self, denominator, winding, defect=F(1, 4), edge=2):
        super().__init__(denominator)
        if type(winding) is not int or edge not in (1, 2):
            raise ValueError('integer winding and oriented edge 1 or 2 required')
        self.winding, self.defect, self.edge = winding, defect, edge

    def seam(self, edge, t, diagnostics=False):
        target, source = self.ends(edge, t)
        left, right = self.frame(*target), self.frame(*source)
        phase = (2*arb.pi()*self.winding+aa(self.defect))*t if edge == self.edge else arb(0)
        # Actual shift action: S_w K_source = S K_source R(phase).
        # Ambient S_w=S(Ks R Ks^T + I-Ps) is an explicitly declared
        # parameter-dependent partial isometry. It is NOT the physical shift.
        m = left.transpose()*(self.shift*right*rot(phase))
        u = polar(m)
        if not diagnostics:
            return u
        # Multiplication by R preserves singular values and both deficit
        # traces. Use the tighter unrotated cell bound from the same frames.
        _, rho, deletion, off = super().seam(edge, t, True)
        return u, rho, deletion, off

    def certify(self, sign=1):
        # Structural gluing convention precedes any interval containment test.
        require(sign == 1, 'EXACT_GLUING_REQUIRED')
        corner = self.repair()
        require(self.c*self.c >= F(19, 20), 'SEAM_SINGULAR_GATE')
        totals, variation, rho_max, negative_real_seen = [], arb(0), arb(0), False
        for edge in (1, 2):
            total = arb(0)
            for i in range(N):
                t = prior.box(i)
                _, rho, _, _ = self.seam(edge, t, True)
                require(rho <= arb(39)/400, 'CELL_SINGULAR_GATE')
                rho_max = max(rho_max, rho.upper())
                c = aa(self.c)
                k = 2*c/(1+c*c)
                speed = (c+1/k)/4
                if edge == self.edge:
                    speed += (2*arb.pi()*self.winding+aa(self.defect)).abs_upper()
                if edge == 2:
                    speed += self.delta.abs_upper()*arb(15)/8
                require(speed/N < arb.pi()/2, 'LIFT_VARIATION')
                variation = max(variation, (speed/N).upper())
                u, v = self.repaired(edge, arb(i)/N), self.repaired(edge, arb(i+1)/N)
                negative_real_seen |= bool(u[0, 0] < 0)
                # Positive-real restriction applies to increments only.
                total += prior.angle(u.transpose()*v)
            totals.append(total)
        interval = (totals[1]-totals[0])/(2*arb.pi())
        q = integer_from_enclosure(interval)
        return {'status': 'CERTIFIED', 'reason': 'WINDING_RECTANGLE_Q', 'q': q,
                'q_interval': enclosure(interval), 'corner': corner,
                'edge_totals': [enclosure(x) for x in totals], 'cells_per_edge': N,
                'max_variation': enclosure(variation), 'max_singular_defect_F': enclosure(rho_max),
                'negative_absolute_real_part_observed': negative_real_seen,
                'input': {'winding': self.winding, 'edge': self.edge, 'extra_angle': str(self.defect), 'c': str(self.c)}}


def relative_screen(a, b):
    v = a.c*b.c+a.s*b.s
    require(v >= F(1, 2), 'Q_SINGULAR_GATE')
    count, maximum = 256, arb(0)
    def q(x, y):
        return polar(b.frame(x, y).transpose()*a.frame(x, y))
    for edge in (1, 2):
        for i in range(count):
            t = arb(arb(2*i+1)/(2*count), arb(1)/(2*count))
            target, source = a.ends(edge, t)
            pulled = q(*target).transpose()*b.repaired(edge, t)*q(*source)
            distance = frobenius(a.repaired(edge, t)-pulled)
            if not distance <= 1:
                return {'status': 'INCONCLUSIVE', 'reason': 'JOINT_EDGE_SCREEN',
                        'failed_edge': edge, 'failed_cell': i, 'distance_F': enclosure(distance)}
            maximum = max(maximum, distance.upper())
    return {'status': 'CERTIFIED', 'reason': 'REPAIRED_Q_PULLBACK_SCREEN',
            'cells_per_edge': count, 'max_distance_F': enclosure(maximum),
            'uniform_Q_smin_lower': str(v), 'joint_angle_bound': '2*pi/3 < pi'}


def combine(a, b, screen):
    if a['status'] != 'CERTIFIED' or b['status'] != 'CERTIFIED':
        return {'status': 'INCONCLUSIVE', 'reason': 'INDIVIDUAL_REQUIRED'}
    if screen['status'] != 'CERTIFIED':
        return {'status': 'INCONCLUSIVE', 'reason': screen['reason'], 'individual': {'a': a, 'b': b}, 'relative': screen}
    if a['q'] != b['q']:
        return {'status': 'EXECUTION_ERROR', 'reason': 'CERTIFIED_SCREEN_INTEGER_CONTRADICTION',
                'individual': {'a': a, 'b': b}, 'relative': screen}
    return {'status': 'CERTIFIED', 'reason': 'SYNTHETIC_RELATIVE_WINDING_CLASS',
            'individual': {'a': a, 'b': b}, 'relative': screen}


def run(job, spec):
    try:
        for path, expected in spec['dependencies'].items():
            require(hashlib.sha256((HERE.parent/path).read_bytes()).hexdigest() == expected, 'DEPENDENCY_HASH_REFUSED')
        mode = job['id']
        if mode.startswith('full_'):
            return prior.full_dimension(job)
        if mode.startswith('interval_'):
            x = arb(job['midpoint'], job['radius'])
            return {'status': 'CERTIFIED', 'reason': 'UNIQUE_CONTAINED_INTEGER', 'q': integer_from_enclosure(x)}
        a = WindingGeometry(32, job['winding_a'], edge=job.get('edge', 2))
        ar = a.certify(-1 if mode == 'wrong_repair' else 1)
        if mode.startswith('individual_'):
            return ar
        b = WindingGeometry(40, job['winding_b'])
        br = b.certify()
        # The real unequal-class geometry must independently refuse its screen.
        screen = relative_screen(a, b)
        if mode == 'contradiction_injection':
            # Explicit state-machine fault injection after a genuine same-class
            # geometric screen, never represented as mathematical evidence.
            br = {**br, 'q': br['q']+1, 'injected_fault': 'integer_field_corruption'}
        result = combine(ar, br, screen)
        if mode == 'contradiction_injection':
            result['control_only'] = True
        return result
    except Refusal as exc:
        return {'status': 'INCONCLUSIVE', 'reason': str(exc)}
    except NonfiniteEnclosure as exc:
        return {'status': 'INCONCLUSIVE', 'reason': 'NONFINITE_ENCLOSURE', 'message': str(exc)}
