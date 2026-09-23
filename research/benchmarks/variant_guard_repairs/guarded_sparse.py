"""Conservative sparse windows with mandatory native dense comparison.

No inertia is estimated from LU. LU is only a linear solver for ARPACK.
This mode makes no speedup, root-finding or certified-arithmetic claim.
"""
from contextlib import contextmanager
import hashlib
import json
import time
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh, splu, LinearOperator
from scipy.linalg import eigh
from guarded_topology import Rejected, integer, finite_points
from fast_engine import RealEngine, realify
from bm_strain import BM


def validate_indices(indices):
    raw = np.asarray(indices, dtype=object)
    if raw.ndim != 2 or raw.shape[1] != 2 or len(raw) == 0:
        raise Rejected("invalid_basis_shape")
    out = []
    for row in raw:
        item = []
        for value in row:
            if isinstance(value, (bool, np.bool_, str)):
                raise Rejected("invalid_basis_component", value=str(value))
            f = float(value)
            if not np.isfinite(f) or f != int(f):
                raise Rejected("invalid_basis_component", value=str(value))
            item.append(int(f))
        out.append(tuple(item))
    if len(set(out)) != len(out):
        raise Rejected("duplicate_basis_index")
    return out


def fixed_bm(indices, **kw):
    """Validate before the historical BM constructor can truncate an index."""
    return BM(index_set=validate_indices(indices), **kw)


class Ledger:
    def __init__(self):
        self.entries = []

    def add(self, kind, **kw):
        self.entries.append(dict(kind=kind, **kw))

    @contextmanager
    def component(self, name, attempt):
        start = time.perf_counter()
        status = "COMPLETED"
        try:
            yield
        except Exception:
            status = "FAILED"
            raise
        finally:
            self.add("component", name=name, attempt=attempt, status=status,
                     exclusive_seconds=time.perf_counter()-start)

    def counts(self):
        names = [x["name"] for x in self.entries if x["kind"] == "component"]
        return {name: names.count(name) for name in sorted(set(names))}


class CheckedSparse:
    def __init__(self, model, declared_indices, policy, ledger=None):
        self.m = model
        self.indices = validate_indices(declared_indices)
        if not isinstance(model, BM) or not model.index_set_fixed or list(model.idx) != self.indices:
            raise Rejected("fixed_declared_basis_required")
        self.p = dict(policy)
        required = ("native_matrix_tol_meV", "ordered_energy_tol_meV", "residual_tol_meV", "orthogonality_tol", "projector_tol", "edge_gap_meV")
        for name in required:
            value = self.p[name]
            if isinstance(value, bool) or not np.isfinite(value) or value <= 0:
                raise Rejected("invalid_sparse_policy", name=name, value=str(value))
        self.ledger = Ledger() if ledger is None else ledger
        self.counter = 0
        with self.ledger.component("setup", 0):
            self.E = RealEngine(model)
        self.identity = dict(dimension=model.dim, ordered_indices=[list(x) for x in self.indices],
                             basis_sha256=hashlib.sha256(json.dumps(self.indices, separators=(",", ":")).encode()).hexdigest())

    def check(self, name, value, attempt):
        threshold = self.p[name]
        passed = bool(np.isfinite(value) and value <= threshold)
        self.ledger.add("check", attempt=attempt, name=name, value=float(value) if np.isfinite(value) else None,
                        threshold=threshold, passed=passed)
        if not passed:
            raise Rejected("sparse_comparison", check=name, value=str(value), threshold=threshold)

    def window(self, f, lo, n=2, sigma=0., request_k=14):
        self.counter += 1
        attempt = self.counter
        start = time.perf_counter()
        status = "REJECTED"
        try:
            f = finite_points([f])[0]
            lo, n, k = integer(lo, "lo"), integer(n, "n", 1), integer(request_k, "request_k", 1)
            if lo+n > self.m.dim or n > k or k >= self.m.dim or not np.isfinite(sigma):
                raise Rejected("unsupported_sparse_request")
            if list(self.m.idx) != self.indices or self.m.dim != 4*len(self.indices):
                raise Rejected("basis_changed")
            self.ledger.add("request", attempt=attempt, f=f.tolist(), lo=lo, n=n, sigma=float(sigma), request_k=k)
            with self.ledger.component("native_assembly", attempt):
                H = self.m.H(self.m.frac_to_k(f))
                R = realify(H)
                if not np.isfinite(R).all():
                    raise Rejected("nonfinite_native_matrix")
                self.check("native_matrix_tol_meV", float(np.max(np.abs(H-H.conj().T))), attempt)
                self.check("native_matrix_tol_meV", float(np.max(np.abs(R.imag))), attempt)
            with self.ledger.component("candidate_assembly", attempt):
                C = self.E.HR(f)
                self.check("native_matrix_tol_meV", float(np.max(np.abs(C-R))), attempt)
                S = sp.csc_matrix(C)
            low, high = max(0, lo-1), min(self.m.dim-1, lo+n)
            with self.ledger.component("native_dense_eigh", attempt):
                wd, Vd = eigh(R.real, subset_by_index=(low, high))
            j = lo-low
            gaps = ([float(wd[j]-wd[j-1])] if lo > 0 else []) + ([float(wd[j+n]-wd[j+n-1])] if lo+n < self.m.dim else [])
            target, targetV = wd[j:j+n], Vd[:, j:j+n]
            self.ledger.add("native_target", attempt=attempt, first_band=low, energies_meV=wd.tolist(), edge_gaps_meV=gaps)
            if any(g < self.p["edge_gap_meV"] for g in gaps):
                raise Rejected("unresolved_sparse_window_edge", gaps_meV=gaps)
            with self.ledger.component("lu_factorization", attempt):
                lu = splu(S-float(sigma)*sp.eye(self.m.dim, format="csc"))
            op = LinearOperator(S.shape, matvec=lu.solve, dtype=float)
            with self.ledger.component("arpack", attempt):
                ws, Vs = eigsh(S, k=k, sigma=float(sigma), which="LM", OPinv=op,
                               v0=np.ones(self.m.dim), tol=0)
            order = np.argsort(ws)
            ws, Vs = ws[order], Vs[:, order]
            self.ledger.add("arpack_spectrum", attempt=attempt, energies_meV=ws.tolist())
            with self.ledger.component("validation", attempt):
                errors = [float(np.max(np.abs(ws[a:a+n]-target))) for a in range(len(ws)-n+1)]
                good = [a for a, error in enumerate(errors) if error <= self.p["ordered_energy_tol_meV"]]
                if len(good) != 1:
                    raise Rejected("absolute_window_not_matched", match_count=len(good), best_error_meV=min(errors))
                a = good[0]; w, V = ws[a:a+n], Vs[:, a:a+n]
                self.check("ordered_energy_tol_meV", errors[a], attempt)
                self.check("residual_tol_meV", float(np.linalg.norm(R.real @ V-V*w, axis=0).max()), attempt)
                self.check("orthogonality_tol", float(np.max(np.abs(V.T @ V-np.eye(n)))), attempt)
                self.check("projector_tol", float(np.linalg.norm(V-targetV @ (targetV.T @ V), 2)), attempt)
            status = "ACCEPTED_DENSE_CHECKED"
            self.ledger.add("accepted", attempt=attempt, lo=lo, n=n, energies_meV=w.tolist(), candidate_offset=a)
            return w, V
        except Exception as ex:
            details = ex.record if isinstance(ex, Rejected) else dict(code="solver_failure", error_type=type(ex).__name__, message=str(ex))
            self.ledger.add("rejected", attempt=attempt, details=details)
            if isinstance(ex, Rejected):
                raise
            raise Rejected("solver_failure", error_type=type(ex).__name__, message=str(ex)) from ex
        finally:
            # Inclusive attempt wall time is separately named; never add to components.
            self.ledger.add("attempt", attempt=attempt, status=status, inclusive_wall_seconds=time.perf_counter()-start)
