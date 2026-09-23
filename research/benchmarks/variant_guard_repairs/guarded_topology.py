"""Opt-in sampled topology gates. A passed mesh is not a continuous-path proof.

Native model Hamiltonians supply every frame. Closed-form realify is the same
fixed unitary change of basis used by the partner; it is not another model.
Coordinates are never wrapped implicitly. Historical APIs are unchanged.
"""
from dataclasses import dataclass, asdict
import numbers
import numpy as np
from scipy.linalg import eigh
from response_inputs import activate
activate()
from fast_engine import realify
from euler import shift_matrix


class Rejected(RuntimeError):
    def __init__(self, code, **details):
        self.record = dict(status="REJECTED", code=code, **details)
        super().__init__(str(self.record))


def integer(value, name, minimum=0):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, numbers.Integral) or value < minimum:
        raise Rejected("invalid_integer", name=name, value=str(value), minimum=minimum)
    return int(value)


def finite_points(points, minimum=1):
    p = np.asarray(points, float)
    if p.ndim != 2 or p.shape[1] != 2 or len(p) < minimum or not np.isfinite(p).all():
        raise Rejected("invalid_coordinates")
    return p


@dataclass(frozen=True)
class Policy:
    reality_meV: float = 1e-9
    hermiticity_meV: float = 1e-9
    external_gap_meV: float = 1e-5
    internal_gap_meV: float = 1e-6
    root_gap_meV: float = 1e-6
    overlap_min: float = 0.5
    sewing_loss_max: float = 0.05
    phase_step_max_rad: float = 3*np.pi/4
    unit_winding_tol: float = 0.15

    def __post_init__(self):
        for name, value in asdict(self).items():
            if isinstance(value, bool) or not np.isfinite(value) or value <= 0:
                raise Rejected("invalid_policy", name=name, value=str(value))
        if self.overlap_min > 1 or self.sewing_loss_max >= 1 or self.phase_step_max_rad >= np.pi or self.unit_winding_tol >= 0.5:
            raise Rejected("invalid_policy_range")


class Sampler:
    """All evaluated coordinates, selected spectra and gate diagnostics are logged.

    An optional U permits controls in another declared real basis. Production
    BM measurements use the fixed sublattice realify transform.
    """
    def __init__(self, model, policy=None, U=None, ledger=None, name="model"):
        self.m = model
        self.p = Policy() if policy is None else policy
        self.U = U
        self.records = [] if ledger is None else ledger
        self.name = name

    def emit(self, kind, **kw):
        row = dict(kind=kind, model=self.name, **kw)
        self.records.append(row)
        return row

    def reject(self, code, **kw):
        self.emit("rejection", code=code, **kw)
        raise Rejected(code, **kw)

    def frame(self, f, lo, n=2, where="frame"):
        f = finite_points([f])[0]
        lo, n = integer(lo, "lo"), integer(n, "n", 1)
        if lo+n > self.m.dim:
            self.reject("band_range", lo=lo, n=n, dimension=self.m.dim)
        H = self.m.H(self.m.frac_to_k(f))
        if H.shape != (self.m.dim, self.m.dim) or not np.isfinite(H).all():
            self.reject("invalid_matrix", where=where)
        herm = float(np.max(np.abs(H-H.conj().T)))
        R = realify(H) if self.U is None else self.U.conj().T @ H @ self.U
        real = float(np.max(np.abs(R.imag)))
        if not np.isfinite(R).all() or real > self.p.reality_meV or herm > self.p.hermiticity_meV:
            self.reject("matrix_precondition", where=where, reality_meV=real, hermiticity_meV=herm)
        low, high = max(0, lo-1), min(self.m.dim-1, lo+n)
        w, V = eigh(R.real, subset_by_index=(low, high))
        j = lo-low
        lower = float(w[j]-w[j-1]) if lo > 0 else None
        upper = float(w[j+n]-w[j+n-1]) if lo+n < self.m.dim else None
        available = [x for x in (lower, upper) if x is not None]
        ext = min(available) if available else None
        self.emit("frame", where=where, f=f.tolist(), first_band=low,
                  energies_meV=w.tolist(), lo=lo, n=n, lower_external_gap_meV=lower,
                  upper_external_gap_meV=upper, external_gap_meV=ext,
                  external_status="CHECKED" if available else "NOT_APPLICABLE_FULL_SPACE",
                  reality_meV=real, hermiticity_meV=herm)
        if ext is not None and (not np.isfinite(ext) or ext < self.p.external_gap_meV):
            self.reject("external_gap", where=where, value_meV=ext, threshold_meV=self.p.external_gap_meV)
        return w[j:j+n], V[:, j:j+n]

    def link(self, a, b, where, sewing=False):
        M = a.T @ b
        if not np.isfinite(M).all():
            self.reject("nonfinite_link", where=where)
        u, s, vt = np.linalg.svd(M)
        low = float(s.min())
        loss = float(np.max(np.abs(1-s)))
        self.emit("link", where=where, singular_values=s.tolist(), min_overlap=low,
                  sewing=sewing, sewing_loss=loss if sewing else None,
                  polar_det=float(np.linalg.det(u @ vt)))
        if low < self.p.overlap_min:
            self.reject("overlap", where=where, value=low, threshold=self.p.overlap_min)
        if sewing and loss > self.p.sewing_loss_max:
            self.reject("sewing_loss", where=where, value=loss, threshold=self.p.sewing_loss_max)
        return u @ vt


def geometry(nodes, radius, intervals, transport_intervals, direction=(1., 0.)):
    nodes = finite_points(nodes, 2)
    if len(nodes) != 2 or not np.isfinite(radius) or radius <= 0:
        raise Rejected("invalid_loop_geometry")
    n, nt = integer(intervals, "intervals", 4), integer(transport_intervals, "transport_intervals", 1)
    d = finite_points([direction])[0]
    if np.linalg.norm(d) == 0:
        raise Rejected("zero_start_direction")
    d = radius*d/np.linalg.norm(d)
    t = np.linspace(0, 2*np.pi, n+1)
    offsets = np.cos(t)[:, None]*d + np.sin(t)[:, None]*np.array([-d[1], d[0]])
    loops = [x+offsets for x in nodes]
    for loop in loops:
        loop[-1] = loop[0]
    path = np.linspace(loops[0][0], loops[1][0], nt+1)
    return dict(nodes=nodes.tolist(), loops=[x.tolist() for x in loops], transport=path.tolist(),
                radius=float(radius), periodic_translation=[0, 0], coordinate_policy="unwrapped")


def mirror(g):
    out = dict(g)
    for key in ("nodes", "loops", "transport"):
        out[key] = (-np.asarray(g[key])).tolist()
    return out


def node_winding(S, coordinates, base, lo, where):
    points = finite_points(coordinates, 5)
    if not np.array_equal(points[0], points[-1]):
        S.reject("loop_not_closed", where=where)
    frames = []
    for j, p in enumerate(points):
        w, F = S.frame(p, lo, where=f"{where}:point:{j}")
        gap = float(w[1]-w[0])
        if gap < S.p.internal_gap_meV:
            S.reject("loop_internal_gap", where=where, point=j, value_meV=gap)
        frames.append(F)
    # Same-coordinate alignment is checked, not inferred from frame determinants
    # at different base points. pair_charges enforces the coordinate identity.
    O = S.link(base, frames[0], where+":base")
    e = frames[0] @ O.T
    prev = frames[0][:, :1]
    alpha = float(np.arctan2(e[:, 1] @ prev[:, 0], e[:, 0] @ prev[:, 0]))
    total = 0.
    for j, F in enumerate(frames[1:], 1):
        O = S.link(e, F, f"{where}:pair:{j}")
        e = F @ O.T
        v = F[:, :1]
        sign = S.link(prev, v, f"{where}:band:{j}")[0, 0]
        v = v*sign
        a = float(np.arctan2(e[:, 1] @ v[:, 0], e[:, 0] @ v[:, 0]))
        step = float((a-alpha+np.pi) % (2*np.pi)-np.pi)
        S.emit("angle", where=where, point=j, angle_rad=a, step_rad=step)
        if abs(step) > S.p.phase_step_max_rad:
            S.reject("phase_resolution", where=where, step_rad=step)
        total += step
        alpha, prev = a, v
    return total/np.pi


def pair_charges(S, g, lo=None):
    lo = S.m.dim//2-1 if lo is None else integer(lo, "lo")
    nodes = finite_points(g["nodes"], 2)
    loops = [finite_points(x, 5) for x in g["loops"]]
    path = finite_points(g["transport"], 2)
    if len(nodes) != 2 or len(loops) != 2 or not np.array_equal(path[0], loops[0][0]) or not np.array_equal(path[-1], loops[1][0]):
        S.reject("base_path_mismatch")
    gaps = []
    for j, f in enumerate(nodes):
        w, _ = S.frame(f, lo, where=f"node:{j}")
        gap = float(w[1]-w[0]); gaps.append(gap)
        if gap > S.p.root_gap_meV:
            S.reject("unverified_node", node=j, gap_meV=gap, threshold_meV=S.p.root_gap_meV)
    base = S.frame(path[0], lo, where="transport:0")[1]
    end = base
    for j, f in enumerate(path[1:], 1):
        F = S.frame(f, lo, where=f"transport:{j}")[1]
        O = S.link(end, F, f"transport:{j}")
        end = F @ O.T
    winds = [node_winding(S, loops[0], base, lo, "loop:0"), node_winding(S, loops[1], end, lo, "loop:1")]
    if any(abs(abs(w)-1) > S.p.unit_winding_tol for w in winds):
        S.reject("nonunit_winding", windings=winds)
    return dict(status="PASSED_SAMPLED_GATES", label="SAME" if winds[0]*winds[1] > 0 else "OPPOSITE",
                windings=winds, node_gaps_meV=gaps, lo=lo)


def sewing(S, axis):
    v = int(getattr(S.m, "valley", 1))
    return shift_matrix(S.m, (-v, 0) if axis == 0 else (0, -v))


def euler_wilson(S, lo=None, nf1=24, nf2=40, sewings=None):
    """Sampled winding with real endpoints and explicit sewing in both axes.

    Each link is gated before taking its polar factor. Multiplying orthogonal
    factors avoids ill-conditioning of the unnormalized overlap product.
    """
    lo = S.m.dim//2-1 if lo is None else integer(lo, "lo")
    n1, n2 = integer(nf1, "nf1", 4), integer(nf2, "nf2", 4)
    s1, s2 = (sewing(S, 0), sewing(S, 1)) if sewings is None else sewings
    grid = [[S.frame([i/n1, j/n2], lo, where=f"grid:{i}:{j}")[1]
             for j in range(n2+1)] for i in range(n1+1)]
    # All interior links along k1, then exact-endpoint k1 sewing at every k2.
    for i in range(n1):
        for j in range(n2+1):
            S.link(grid[i][j], grid[i+1][j], f"axis1:{i}:{j}")
    for j in range(n2+1):
        S.link(grid[-1][j], s1 @ grid[0][j], f"sewing1:{j}", sewing=True)
    for i in range(1, n1+1):
        O = S.link(grid[i-1][0], grid[i][0], f"base:{i}")
        if np.linalg.det(O) < 0:
            grid[i][0] = grid[i][0] @ np.diag([1., -1.])
    closure = S.link(grid[-1][0], s1 @ grid[0][0], "base:closure", sewing=True)
    if np.linalg.det(closure) < 0:
        S.reject("nonorientable_axis1")
    phases = []
    for i, row in enumerate(grid):
        W = np.eye(2)
        for j in range(n2):
            W = W @ S.link(row[j], row[j+1], f"axis2:{i}:{j}")
        W = W @ S.link(row[-1], s2 @ row[0], f"sewing2:{i}", sewing=True)
        if np.linalg.det(W) < 0:
            S.reject("nonorientable_axis2", row=i)
        phases.append(float(np.arctan2(W[1, 0], W[0, 0])))
    steps = np.diff(np.unwrap(phases))
    S.emit("wilson_phases", phases_rad=phases, increments_rad=steps.tolist())
    if max(abs(steps)) > S.p.phase_step_max_rad:
        S.reject("phase_resolution", max_step_rad=float(max(abs(steps))))
    estimate = float(np.sum(steps)/(2*np.pi))
    if abs(estimate-round(estimate)) > S.p.unit_winding_tol:
        S.reject("wilson_closure", estimate=estimate)
    return dict(status="PASSED_SAMPLED_GATES", euler_estimate=estimate, nearest_integer=round(estimate),
                phases_rad=phases, mesh=[n1, n2], lo=lo,
                interpretation="Sampled finite-model estimate; sign depends on base orientation")


def band_sign_holonomy(S, band, axis, c, n=80, sewing_matrix=None):
    band, axis, n = integer(band, "band"), integer(axis, "axis"), integer(n, "n", 4)
    if axis not in (0, 1) or not np.isfinite(c):
        S.reject("invalid_cycle")
    sm = sewing(S, axis) if sewing_matrix is None else sewing_matrix
    first = prev = None
    for j, t in enumerate(np.linspace(0, 1, n+1)):
        f = [t, c] if axis == 0 else [c, t]
        _, F = S.frame(f, band, n=1, where=f"cycle:{j}")
        if prev is not None:
            F = F @ S.link(prev, F, f"cycle:{j}").T
        if first is None:
            first = F
        prev = F
    O = S.link(prev, sm @ first, "cycle:sewing", sewing=True)
    return dict(status="PASSED_SAMPLED_GATES", sign=int(round(O[0, 0])),
                closure_overlap=float((prev.T @ sm @ first)[0, 0]), intervals=n, band=band, axis=axis)
