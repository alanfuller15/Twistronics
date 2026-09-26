"""One analytic rectangle, two planes, computed seams and repaired q values.

All inequalities use Arb; structural identities use exact rational algebra.
This is a synthetic analytic certificate, not a generic or physical solver.
"""
import hashlib
from fractions import Fraction as F
from pathlib import Path
from flint import arb, arb_mat, fmpq, fmpq_mat
from primitives_s0f import enclosure, frobenius, identity, NonfiniteEnclosure
from certified_s0f import riesz_circle
from frame_bridge import frame_from_projector

HERE = Path(__file__).resolve().parent
N = 64


class Refusal(Exception):
    pass


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def aa(x):
    x = F(x)
    return arb(x.numerator)/x.denominator


def rot(t):
    c, s = t.cos(), t.sin()
    return arb_mat([[c, -s], [s, c]])


def box(i):
    return arb(arb(2*i+1)/(2*N), arb(1)/(2*N))


def chi(t):
    return 10*t**3-15*t**4+6*t**5


def polar(m):
    a, b = m[0, 0]+m[1, 1], m[1, 0]-m[0, 1]
    require(m.det() > 0, 'POLAR_ORIENTATION')
    require(a > 0, 'POLAR_BRANCH')
    d = (a*a+b*b).sqrt()
    return arb_mat([[a/d, -b/d], [b/d, a/d]])


def angle(u):
    require(u[0, 0] > 0, 'ANGLE_BRANCH')
    return (u[1, 0]/u[0, 0]).atan()


class Geometry:
    def __init__(self, denominator, bad_gauge=False):
        t = F(1, denominator)
        self.c, self.s = (1-t*t)/(1+t*t), 2*t/(1+t*t)
        e = fmpq_mat([[str(self.c), '0'], ['0', '1'], [str(-self.s), '0']])
        g = fmpq_mat([[0, -1, 0], [1, 0, 0], [0, 0, 0]])
        j = fmpq_mat([[0, -1], [1, 0]])
        connection = e.transpose()*g*e
        require(e.transpose()*e == fmpq_mat([[1, 0], [0, 1]]), 'FRAME_IDENTITY')
        rate = F(0) if bad_gauge else -self.c
        require(connection+j*fmpq(str(rate)) == fmpq_mat(2, 2), 'GAUGE_CONNECTION')
        self.connection = [[str(connection[i, k]) for k in range(2)] for i in range(2)]
        self.shift = arb_mat([[1, 0, 0], [0, 1, 0], [0, 0, 0]])
        self.delta = None

    @staticmethod
    def phi(x, y):
        return x/4+y/2+x*y/4

    def frame(self, x, y):
        p = self.phi(x, y)
        c, s = aa(self.c), aa(self.s)
        f = arb_mat([[c*p.cos(), -p.sin()], [c*p.sin(), p.cos()], [-s, 0]])
        return f*rot(-c*p)

    def ends(self, edge, t):
        return ((arb(1), t), (arb(0), t)) if edge == 1 else ((t, arb(1)), (t, arb(0)))

    def seam(self, edge, t, diagnostics=False):
        target, source = self.ends(edge, t)
        left, right = self.frame(*target), self.frame(*source)
        m = left.transpose()*self.shift*right
        u = polar(m)
        if not diagnostics:
            return u
        deletion = right.transpose()*(identity(3)-self.shift.transpose()*self.shift)*right
        off = (identity(3)-left*left.transpose())*self.shift*right
        # Independent enclosures of both sides of the exact deficit identity.
        residual = identity(2)-m.transpose()*m-deletion-off.transpose()*off
        require(all(residual[i, j].contains(0) for i in range(2) for j in range(2)), 'DEFICIT_IDENTITY')
        return u, frobenius(identity(2)-m.transpose()*m), deletion.trace(), (off.transpose()*off).trace()

    def repair(self, charge=F(1, 128)):
        a = self.seam(2, arb(1))*self.seam(1, arb(0))
        b = self.seam(1, arb(1))*self.seam(2, arb(0))
        bound = frobenius(a-b)
        eta = aa(charge)
        charged = bound+2*(2*eta+eta*eta)
        require(charged <= 1, 'CHARGED_CORNER_BRANCH')
        self.delta = angle(a.transpose()*b)
        return {'corner_distance_F': enclosure(bound), 'charged_corner_bound': enclosure(charged),
                'delta': enclosure(self.delta), 'delta_excludes_zero': not self.delta.contains(0)}

    def repaired(self, edge, t, sign=1):
        u = self.seam(edge, t)
        return u*rot(sign*self.delta*chi(t)) if edge == 2 else u

    def certify(self, sign=1, charge=F(1, 128)):
        corner = self.repair(charge)
        # D R(-Delta) D has singular values >= c^2 (D=diag(c,1)).
        # This uniform analytic gate is supplemented by interval edge checks.
        require(self.c*self.c >= F(19, 20), 'SEAM_SINGULAR_GATE')
        cells, totals = [], []
        for edge in (1, 2):
            total = arb(0)
            for i in range(N):
                t = box(i)
                _, rho, deletion, off = self.seam(edge, t, True)
                require(rho <= arb(39)/400, 'CELL_SINGULAR_GATE')
                # g'(Delta)=c-k/(cos^2 Delta+k^2 sin^2 Delta),
                # hence |g'| <= c+1/k; Delta'=1/4.
                c = aa(self.c)
                k = 2*c/(1+c*c)
                speed = (c+1/k)/4
                if edge == 2:
                    # max chi'=15/8 on [0,1]. Covers every point in cell.
                    speed += self.delta.abs_upper()*arb(15)/8
                require(speed/N < arb.pi()/2, 'LIFT_VARIATION')
                u, v = self.repaired(edge, arb(i)/N, sign), self.repaired(edge, arb(i+1)/N, sign)
                increment = angle(u.transpose()*v)
                total += increment
                cells.append({'edge': edge, 'cell': i, 'rho': enclosure(rho),
                              'deletion_trace': enclosure(deletion), 'off_target_square_trace': enclosure(off),
                              'variation_bound': enclosure(speed/N), 'increment': enclosure(increment)})
            totals.append(total)
        q = (totals[1]-totals[0])/(2*arb.pi())
        require(q.contains(0), 'INTEGER_OUTSIDE_ENCLOSURE')
        require(q.abs_upper() < arb(1)/8, 'INTEGER_WIDTH')
        # Exact gluing requires positive CASE repair. Enclosure is necessary,
        # never sufficient to claim exact closure.
        require(sign == 1, 'EXACT_GLUING_REQUIRED')
        _, _, deletion, off = self.seam(1, arb(0), True)
        require(deletion > 0 and off > 0, 'BOTH_DEFICITS_REQUIRED')
        return {'status': 'CERTIFIED', 'reason': 'ANALYTIC_RECTANGLE_Q', 'q': 0,
                'connection': self.connection, 'c': str(self.c), 's': str(self.s),
                'corner': corner, 'q_interval': enclosure(q), 'cells': cells,
                'bottom_gauge': 'R(-c*x/4)', 'vertical_increment': 'R(-c*(y/2+x*y/4))',
                'domain': '[0,1]^2', 'both_deficits_positive_at_origin': True}


def relative(a, b, bad_identification=False, screen_limit=1):
    # Computed exact E_b^T E_a = diag(v,1). Its positive polar is I.
    v = a.c*b.c+a.s*b.s
    require(v >= F(1, 2), 'Q_SINGULAR_GATE')
    def q(x, y):
        overlap = b.frame(x, y).transpose()*a.frame(x, y)
        return polar(overlap)
    if bad_identification:
        return {'status': 'INCONCLUSIVE', 'reason': 'Q_DEPENDENCY_REFUSED'}
    cells = []
    for edge in (1, 2):
        for i in range(N):
            t = box(i)
            target, source = a.ends(edge, t)
            pulled = q(*target).transpose()*b.repaired(edge, t)*q(*source)
            distance = frobenius(a.repaired(edge, t)-pulled)
            if not distance <= screen_limit:
                return {'status': 'INCONCLUSIVE', 'reason': 'JOINT_EDGE_SCREEN',
                        'failed_edge': edge, 'failed_cell': i, 'distance_F': enclosure(distance)}
            cells.append({'edge': edge, 'cell': i, 'distance_F': enclosure(distance)})
    return {'status': 'CERTIFIED', 'reason': 'REPAIRED_Q_PULLBACK_SCREEN',
            'uniform_Q_smin_lower': str(v), 'cells': cells,
            'joint_angle_bound': '2*pi/3 < pi', 'computed_independently_of_q_difference': True}


def full_dimension(job):
    n = job['dimension']
    a = Geometry(32)
    x = y = arb(1)/2
    k = a.frame(x, y)
    p = a.phi(x, y)
    normal = [aa(a.s)*p.cos(), aa(a.s)*p.sin(), aa(a.c)]
    u, w = aa(F(9999, 10001)), aa(F(200, 10001))
    candidate = arb_mat([[u*k[i, 0]+w*normal[i], k[i, 1]] for i in range(3)])
    # Dense rational orthogonal Householder U=I-2*11^T/n. Multiplication
    # of padded columns by U is computed directly, without a dense U product.
    def embed(m):
        sums = [sum((m[i, j] for i in range(3)), arb(0)) for j in range(2)]
        return arb_mat([[(m[i, j] if i < 3 else arb(0))-2*sums[j]/n for j in range(2)] for i in range(n)])
    k, candidate = embed(k), embed(candidate)
    projector = k*k.transpose()
    h = 2*(identity(n)-projector)
    # Exact spectrum is {0 (twice), 2 (n-2 times)}. No estimated gap enters.
    result = riesz_circle(h, '0', '1', job['nodes'], '0', '2', '1/1024')
    center = result.pop('_center', None)
    if result['status'] != 'CERTIFIED':
        return result
    bound = result['total_projector_operator_error_bound']['upper']
    eps = arb(bound['mantissa'])*arb(2)**bound['exponent']
    frame = frame_from_projector(center, eps, candidate, job['frame_budget'])
    frame.pop('_frame', None)
    return {'status': frame['status'], 'reason': 'FULL_DIMENSION_POINT_BRIDGE' if frame['status'] == 'CERTIFIED' else frame['reason'],
            'dimension': n, 'point': ['1/2', '1/2'], 'riesz': result, 'frame': frame,
            'exact_spectrum': {'0': 2, '2': n-2},
            'premises': 'P=KK^T; U rational orthogonal; E=(u*K1+w*normal,K2), u^2+w^2=1; normalized PE=K',
            'scope': 'Dense fixed-point calibration, not uniform rectangle Riesz or a physical workload'}


def run(job, spec):
    mode = job['id']
    try:
        for path, expected in spec['dependencies'].items():
            actual = hashlib.sha256((HERE.parent/path).read_bytes()).hexdigest()
            if mode == 'dependency_tamper':
                actual = '0'*64
            require(actual == expected, 'DEPENDENCY_HASH_REFUSED')
        if mode.startswith('full_'):
            return full_dimension(job)
        a = Geometry(8 if mode == 'singular_loss' else 32, mode == 'bad_gauge')
        ar = a.certify(sign=-1 if mode == 'wrong_repair' else 1,
                       charge=F(1) if mode == 'branch_charge' else F(1, 128))
        b = Geometry(40)
        br = b.certify()
        screen = relative(a, b, mode == 'unbound_Q', 0 if mode == 'joint_budget' else 1)
        return {'status': screen['status'], 'reason': 'SYNTHETIC_GEOMETRIC_COMPOSITION' if screen['status'] == 'CERTIFIED' else screen['reason'],
                'individual': {'a': ar, 'b': br}, 'relative': screen,
                'dependencies': spec['dependencies'], 'scope': 'Fixed analytic synthetic family only; no numerical Riesz or physical certificate'}
    except Refusal as exc:
        return {'status': 'INCONCLUSIVE', 'reason': str(exc)}
    except NonfiniteEnclosure as exc:
        return {'status': 'INCONCLUSIVE', 'reason': 'NONFINITE_ENCLOSURE', 'message': str(exc)}
