"""
tbg_ref.py — independent second implementation (v036).

Deliberately different from bm_strain.py wherever a convention could hide an error:
  * Basis: one absolute-momentum grid k+G for BOTH layers (Koshino et al. PRX 8, 031087 style);
    each layer's Dirac point K_l enters its intralayer block. bm_strain instead offsets the
    layer-2 grid by q_1. Same physics, different truncation.
  * Strain: full (1+E_l) lattice deformation, reciprocal vectors b^(l) = (1+E_l)^{-T} R(theta_l) b,
    moiré vectors G^M = b^(1) - b^(2) exactly, and the velocity renormalisation
    h_l = hbar v [(1 - E_l) R(-theta_l)(p - K_l - A_l)] . sigma, which bm_strain dropped.
    Pseudo-gauge A_l = (sqrt3 beta / 2a)(E_xx - E_yy, -2 E_xy) with beta=3.14 (the physics, kept).
  * Tunnelling written as T(r) = sum_j T_j exp(i q_j . r) with q_j = K_j^(1) - K_j^(2) built from the
    three equivalent K points of each strained, rotated layer (no small-angle formulas).
  * C2zT real basis built NUMERICALLY from the antiunitary A = S_x K (eigenvectors of A with A^2=+1),
    not from a hand-chosen (1,1)/(i,-i) pair.
  * Euler class by a plaquette sum of SO(2) rotation angles of the real 2-frame over the whole BZ
    (lattice Euler class), not by k1-line Wilson loops.
  * Node charge by the winding number of the effective real 2x2 Hamiltonian d(k) = (d_x, d_z)
    around the node, expressed in a fixed real frame; relative charge via orientation transport
    of that fixed frame along the segment between nodes.
  * Different node search: dense grid + Nelder-Mead on the gap, plus a check that the gap grows
    linearly with distance (a genuine cone), not just that the minimum is small.
Perturbations reproduced for the braid test:
  * scalar moiré harmonic  A w1 sum_j cos(G_j . r)   (layer-symmetric, sublattice identity)
  * sin harmonic           B w1 sum_j sin(G_j . r) sigma_z (layer-symmetric)
"""
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import minimize

A0, HV = 2.46, 5944.0           # Angstrom, meV*Angstrom
PX = np.array([[0, 1], [1, 0]], complex); PY = np.array([[0, -1j], [1j, 0]]); PZ = np.diag([1.0, -1.0]).astype(complex); I2 = np.eye(2, dtype=complex)


def R(t):
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])


class TBG:
    def __init__(self, theta=1.05, w1=110.0, w0=88.0, eps=0.0, phi=0.0, nu=0.16, beta=3.14, N=4, A=0.0, B=0.0, Bt=0.0, kinetic=None):
        # kinetic must be given explicitly (v041): 'none' | 'geom_wrong' (v036, retained for record) | 'full' (v039) | 'lab_nn_full' (v041 declared)
        if kinetic not in ('none', 'geom_wrong', 'full', 'lab_nn_full'): raise ValueError('kinetic must be one of none/geom_wrong/full/lab_nn_full, got %r' % (kinetic,))
        self.kinetic = kinetic; self.beta = beta
        th = np.radians(theta); ph = np.radians(phi)
        E = eps * np.array([[np.cos(ph)**2 - nu*np.sin(ph)**2, (1+nu)*np.sin(ph)*np.cos(ph)],
                            [(1+nu)*np.sin(ph)*np.cos(ph), np.sin(ph)**2 - nu*np.cos(ph)**2]])
        self.El = [-E/2, +E/2]; self.thl = [-th/2, +th/2]
        KD = np.array([4*np.pi/(3*A0), 0.0])                                                              # K point
        Kj = [R(2*np.pi*j/3) @ KD for j in range(3)]                                                       # three equivalent K's
        lat = lambda l, v: np.linalg.inv(np.eye(2) + self.El[l]).T @ R(self.thl[l]) @ v                   # (1+E)^{-T} R
        self.Kl = [[lat(l, k) for k in Kj] for l in range(2)]
        self.q = [self.Kl[0][j] - self.Kl[1][j] for j in range(3)]
        self.G1 = self.q[1] - self.q[0]; self.G2 = self.q[2] - self.q[0]
        gauge = lambda Em: np.sqrt(3)*beta/(2*A0) * np.array([Em[0, 0]-Em[1, 1], -2*Em[0, 1]])
        if kinetic == 'lab_nn_full':
            self.Al = [R(self.thl[l]) @ gauge(R(-self.thl[l]) @ self.El[l] @ R(self.thl[l])) for l in range(2)]
        else:
            self.Al = [gauge(self.El[l]) for l in range(2)]
        self.Tj = [w0*I2 + w1*(np.cos(2*np.pi*j/3)*PX + np.sin(2*np.pi*j/3)*PY) for j in range(3)]
        self.w1, self.A, self.B, self.Bt, self.N = w1, A, B, Bt, N
        # absolute-momentum grid centred on the layer-1 Dirac point K_0^(1), shared by both layers
        self.origin = self.Kl[0][0]
        gmax = N*np.linalg.norm(self.G1) + 1e-9
        self.mn = [(a, b) for a in range(-3*N, 3*N+1) for b in range(-3*N, 3*N+1) if np.linalg.norm(a*self.G1 + b*self.G2) <= gmax]
        self.ix = {t: i for i, t in enumerate(self.mn)}; self.nG = len(self.mn); self.dim = 4*self.nG
        self.Gv = np.array([a*self.G1 + b*self.G2 for a, b in self.mn])
        self._static()

    def _blk(self, H, l1, i1, l2, i2, M):
        r = 2*self.nG*l1 + 2*i1; c = 2*self.nG*l2 + 2*i2; H[r:r+2, c:c+2] += M

    def _static(self):
        H = np.zeros((self.dim, self.dim), complex); nG = self.nG
        # interlayer: layer-1 momentum p couples to layer-2 momentum p + q_j; on the shared grid the
        # transfer q_j - q_0 is a moiré vector (0, G1, G2) and q_0 is carried by K^(2) in the Dirac block
        for j, sh in enumerate([(0, 0), (1, 0), (0, 1)]):
            for (a, b), i in self.ix.items():
                t = (a+sh[0], b+sh[1])
                if t in self.ix:
                    self._blk(H, 1, self.ix[t], 0, i, self.Tj[j]); self._blk(H, 0, i, 1, self.ix[t], self.Tj[j].conj().T)
        # perturbations: cos harmonic (real, even) and sin*sigma_z (imaginary coefficient x sigma_z)
        for l in range(2):
            for (a, b), i in self.ix.items():
                for dm, dn in [(1, 0), (-1, 0), (0, 1), (0, -1), (-1, 1), (1, -1)]:
                    t = (a+dm, b+dn)
                    if t not in self.ix: continue
                    if self.A: self._blk(H, l, self.ix[t], l, i, 0.5*self.A*self.w1*I2)
                    if self.B or self.Bt:
                        s = +1 if (dm, dn) in [(1, 0), (0, 1), (-1, 1)] else -1     # +G_j vs -G_j
                        amp = self.B + (self.Bt if l == 0 else -self.Bt)            # layer-symmetric + layer-antisymmetric sin*sigma_z
                        if amp: self._blk(H, l, self.ix[t], l, i, (-1j*s)*0.5*amp*self.w1*PZ)
        assert np.abs(H - H.conj().T).max() < 1e-12
        self.Hs = H

    def H(self, k):
        H = self.Hs.copy(); nG = self.nG
        for l in range(2):
            V = {'none': np.eye(2), 'geom_wrong': np.eye(2) - self.El[l],
                 'full': np.eye(2) + (1 - self.beta) * self.El[l],
                 'lab_nn_full': np.eye(2) + (1 - self.beta) * self.El[l]}[self.kinetic]   # Fermi-velocity tensor v/v0
            M = R(-self.thl[l]) @ V if self.kinetic == 'lab_nn_full' else V @ R(-self.thl[l])
            pp = (self.origin + k[None, :] + self.Gv - self.Kl[l][0] - self.Al[l]) @ M.T
            for i in range(nG):
                self._blk(H, l, i, l, i, HV*(pp[i, 0]*PX + pp[i, 1]*PY))
        return H

    def k(self, f):
        return f[0]*self.G1 + f[1]*self.G2

    def bands(self, k, nb=3):
        return eigh(self.H(k), eigvals_only=True, subset_by_index=(self.dim//2-nb, self.dim//2+nb-1))

    def flat_gap(self, f):
        w = self.bands(self.k(f), 2); return w[2]-w[1]

    def remote_gap(self, f):
        w = self.bands(self.k(f), 2); return min(w[3]-w[2], w[1]-w[0])

    def refine(self, f0, fn):
        r = minimize(lambda f: fn(np.array(f)), f0, method='Nelder-Mead', options={'xatol': 1e-8, 'fatol': 1e-11, 'maxiter': 800})
        if not r.success: raise RuntimeError(r.message)
        return r.x, r.fun

    def find_nodes(self, fn=None, n=24, keep=8):
        fn = fn or self.flat_gap
        fs = np.linspace(0, 1, n, endpoint=False); V = np.array([[fn(np.array([a, b])) for b in fs] for a in fs])
        seeds = sorted([(V[i, j], fs[i], fs[j]) for i in range(n) for j in range(n)
                        if V[i, j] <= min(V[(i+di) % n, (j+dj) % n] for di in (-1, 0, 1) for dj in (-1, 0, 1))])[:keep]
        out = []
        for v, a, b in seeds:
            f, val = self.refine(np.array([a, b]), fn)
            if val < 1e-6 and all(np.linalg.norm(((f-g)+0.5) % 1-0.5) > 0.01 for g in out):
                # cone check: gap must grow ~linearly at distance 0.01 in two directions
                if all(fn(f + 0.01*np.array(dv)) > 0.05 for dv in ([1, 0], [0, 1])): out.append(f % 1)
        return out

    # ---------- C2zT real structure, built numerically ----------
    def real_basis(self):
        Sx = np.kron(np.eye(2*self.nG), PX)                                       # antiunitary A = Sx K
        # A-invariant real basis: columns v with Sx conj(v) = v.  Take W = (I + Sx)/sqrt2 columns and
        # orthonormalise the real span numerically (Sx is symmetric so e^{i pi/4}(I+Sx)... avoided on purpose)
        # generic construction: for each pair (2j,2j+1) the vectors (1,1)/sqrt2 and (i,-i)/sqrt2 satisfy Sx conj(v)=v.
        # We re-derive them as eigenvectors of the unitary Sx restricted to each pair, then rotate by the phase
        # that makes Sx conj(v) = v; this is the numerical route and is checked against A below.
        cols = []
        for j in range(2*self.nG):
            e = np.zeros(self.dim, complex); e[2*j] = 1; f = np.zeros(self.dim, complex); f[2*j+1] = 1
            for v in (e + Sx @ np.conj(e), 1j*(e - Sx @ np.conj(e))):          # v + A v is A-invariant; i(v - A v) likewise
                v = v/np.linalg.norm(v); cols.append(v)
        U = np.array(cols).T
        assert np.allclose(Sx @ np.conj(U), U), 'real basis is not A-invariant'
        assert np.allclose(U.conj().T @ U, np.eye(self.dim)), 'real basis not orthonormal'
        return U

    def real_frame(self, U, k, lo, nb=2):
        HR = U.conj().T @ self.H(k) @ U
        if np.abs(HR.imag).max() > 1e-9: raise RuntimeError('not real: %.2e' % np.abs(HR.imag).max())
        w, v = eigh(HR.real, subset_by_index=(lo, lo+nb-1)); return v

    # ---------- lattice Euler class (plaquette sum) ----------
    def euler_plaquette(self, U, lo, n1=24, n2=24):
        """Sum over BZ plaquettes of the SO(2) rotation angle of the real 2-frame transported around each
        plaquette, with orientation carried consistently from a base point; returns e2 (float) and a flag
        for non-orientability (any plaquette holonomy with det<0 or an orientation mismatch on closing)."""
        F = {}
        for i in range(n1+1):
            for j in range(n2+1):
                F[i, j] = self.real_frame(U, self.k(np.array([i/n1, j/n2])), lo)
        # fix orientation by continuity along rows then columns
        for i in range(n1+1):
            for j in range(n2+1):
                if (i, j) == (0, 0): continue
                ref = F[i, j-1] if j > 0 else F[i-1, j]
                if np.linalg.det(ref.T @ F[i, j]) < 0: F[i, j] = F[i, j] @ np.diag([1, -1])
        total = 0.0; mind = 1.0
        for i in range(n1):
            for j in range(n2):
                W = np.eye(2)
                for (a, b), (c, d) in [((i, j), (i+1, j)), ((i+1, j), (i+1, j+1)), ((i+1, j+1), (i, j+1)), ((i, j+1), (i, j))]:
                    W = W @ (F[a, b].T @ F[c, d])
                u, s, vt = np.linalg.svd(W); O = u @ vt; mind = min(mind, np.linalg.det(O))
                total += np.arctan2(O[1, 0], O[0, 0])
        # periodic closure of the orientation: compare F[n1,j] with the shifted F[0,j] and F[i,n2] with F[i,0]
        S1 = self.shift((-1, 0)); S2 = self.shift((0, -1))
        cl = min(np.linalg.det(F[n1, j].T @ (S1 @ F[0, j])) for j in range(n2+1)), min(np.linalg.det(F[i, n2].T @ (S2 @ F[i, 0])) for i in range(n1+1))
        return total/(2*np.pi), cl, mind

    def shift(self, d):
        S = np.zeros((self.dim, self.dim))
        for (a, b), i in self.ix.items():
            t = (a+d[0], b+d[1])
            if t in self.ix:
                for l in range(2):
                    for s in range(2): S[2*self.nG*l+2*self.ix[t]+s, 2*self.nG*l+2*i+s] = 1
        return S

    # ---------- node charge from the effective real 2x2 Hamiltonian ----------
    def node_charge(self, U, node, lo, frame, r=0.01, npts=72):
        """Winding of d=(d_x,d_z) of H projected on a FIXED real 2-frame around the node."""
        ang = []; smin = 1.0
        for t in np.linspace(0, 2*np.pi, npts, endpoint=False):
            k = self.k(node + r*np.array([np.cos(t), np.sin(t)]))
            HR = (U.conj().T @ self.H(k) @ U).real
            Fk = self.real_frame(U, k, lo)                                       # true subspace at this loop point
            smin = min(smin, np.linalg.svd(frame.T @ Fk, compute_uv=False).min())  # frame must span it (gate)
            h = frame.T @ HR @ frame
            dz, dx = 0.5*(h[0, 0]-h[1, 1]), h[0, 1]; ang.append(np.arctan2(dz, dx))
        w = float(np.sum(np.diff(np.unwrap(np.append(ang, ang[0])))) / (2*np.pi))
        self.last_smin = smin; self.smin_log = getattr(self, 'smin_log', []) + [smin]
        if smin < 0.9 or abs(abs(w) - 1) > 0.05: return None                       # invalid: no numeric sentinel
        return round(w)

    def transport(self, U, lo, f_from, f_to, base, n=200):
        prev = base
        for s in np.linspace(0, 1, n)[1:]:
            fr = self.real_frame(U, self.k(f_from + s*(f_to-f_from)), lo)
            if np.linalg.det(prev.T @ fr) < 0: fr = fr @ np.diag([1, -1])
            prev = fr
        return prev

    def relative_charge(self, U, n1, n2, lo, r=None):
        d = ((n2-n1)+0.5) % 1-0.5; n2 = n1 + d
        sep = np.linalg.norm(d)
        if not np.isfinite(sep) or sep < 1e-4: raise ValueError('nonfinite/coincident seeds (sep=%.1e)' % sep)
        requested = 0.01 if r is None else float(r)
        if not np.isfinite(requested) or requested <= 0: raise ValueError('radius must be positive and finite')
        r = min(requested, 0.01, 0.3*sep)
        self.smin_log = []
        off = -1.5*r*d/sep                                            # frame point on the side away from the partner node
        base = self.real_frame(U, self.k(n1 + off), lo)
        w1 = self.node_charge(U, n1, lo, base, r=r)
        fr2 = self.transport(U, lo, n1 + off, n2 - off, base, n=300)   # transported to the far side of n2
        w2 = self.node_charge(U, n2, lo, fr2, r=r)
        self.last_smin = min(self.smin_log)                               # minimum over BOTH loops
        if w1 is None or w2 is None or abs(w1) != 1 or abs(w2) != 1: return w1, w2, 'INDETERMINATE'
        return w1, w2, ('SAME' if w1*w2 > 0 else 'OPPOSITE')


    # ---------- generic helpers for the later checkpoints ----------
    def gap(self, i):
        """gap function between bands (D/2-3+i, D/2-2+i): i=1 lower|flat1, 2 flat gap, 3 flat2|upper, 4 upper|next, 0 below|lower"""
        return lambda f: (lambda w: w[i+1]-w[i])(self.bands(self.k(np.asarray(f)), 3))

    def gap_min(self, i, n=18, keep=4):
        """bounded multistart minimum of gap i over the fundamental cell, with explicit seam seeds (v040 correction)."""
        if not isinstance(n, (int, np.integer)) or n < 2 or not isinstance(keep, (int, np.integer)) or keep < 1:
            raise ValueError('gap_min requires integer n >= 2 and keep >= 1')
        fn = self.gap(i); fs = np.linspace(0, 1, n, endpoint=False)
        V = np.array([[fn(np.array([a, b])) for b in fs] for a in fs])
        if not np.isfinite(V).all(): raise RuntimeError('nonfinite gap grid')
        seeds = sorted([(V[p, q], fs[p], fs[q]) for p in range(n) for q in range(n)
                        if V[p, q] <= min(V[(p+dp) % n, (q+dq) % n] for dp in (-1, 0, 1) for dq in (-1, 0, 1))])[:keep]
        pts = [np.array([a, b]) for _, a, b in seeds]
        for a, b in list(pts):                                                   # seam/edge seeds for every candidate
            pts += [np.array([a, b]) + np.array(sh) for sh in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= a+sh[0] <= 1 and 0 <= b+sh[1] <= 1]
            pts += [np.array([1.0 if a > 0.5 else 0.0, b]), np.array([a, 1.0 if b > 0.5 else 0.0])]
        # Cover both faces explicitly, including inward seeds: clipping a
        # Nelder-Mead simplex on a face can otherwise retain a false edge
        # minimum. Two-grid agreement alone missed the endpoint regression.
        for a, b in list(pts):
            pts += [np.array([0., b]), np.array([1., b]), np.array([a, 0.]), np.array([a, 1.])]
        pts += [np.array([a, b]) for a in (0., .5, 1.) for b in (0., .5, 1.)]
        pts += [np.clip(p, .01, .99) for p in list(pts) if np.any((p == 0.) | (p == 1.))]
        pts = [np.array(p) for p in sorted(set(tuple(p) for p in pts))]
        best = np.inf; self.gap_min_log = []
        for p0 in pts:
            p0 = np.clip(p0, 0, 1); initial = float(fn(p0))
            if not np.isfinite(initial): raise RuntimeError('nonfinite gap seed')
            r = minimize(lambda f: fn(np.array(f)), p0, method='Nelder-Mead',
                         bounds=[(0, 1), (0, 1)], options={'xatol': 1e-8, 'fatol': 1e-11, 'maxiter': 800})
            self.gap_min_log.append(dict(seed=p0.tolist(), initial=initial,
                                         success=bool(r.success), value=float(r.fun),
                                         message=str(getattr(r, 'message', ''))))
            if not r.success or not np.isfinite(r.fun) or r.fun > initial + 1e-7:
                raise RuntimeError('gap refinement failed, nonfinite, or worsened seed')
            best = min(best, r.fun)
        if not np.isfinite(best): raise RuntimeError('no accepted gap refinement')
        return best

    def band_sign_holonomy(self, U, band, axis, c, n=100):
        """sign holonomy of the single real eigenvector of `band` around the cycle along `axis` at offset c (w1 of a line bundle)."""
        S = self.shift((-1, 0)) if axis == 0 else self.shift((0, -1)); prev = None; first = None
        for t in np.linspace(0, 1, n+1):
            q = np.array([t, c]) if axis == 0 else np.array([c, t])
            v = self.real_frame(U, self.k(q), band, nb=1)
            if prev is not None and prev[:, 0] @ v[:, 0] < 0: v = -v
            if first is None: first = v
            prev = v
        return float(prev[:, 0] @ (S @ first)[:, 0])
