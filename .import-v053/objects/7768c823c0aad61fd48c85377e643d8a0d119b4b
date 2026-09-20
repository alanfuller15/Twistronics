"""
Single-valley Bistritzer–MacDonald continuum model of twisted bilayer graphene
with uniaxial heterostrain and two optional bounded perturbations.

Conventions (stated so the results are reproducible):
  a      = 2.46 A                     graphene lattice constant
  hbar v = 5.944 eV*A                  (Bernevig et al., TBG I)
  w1     = 110 meV (AB), w0 = 0.8*w1   (AA, corrugated)
  theta  = 1.05 deg                    layer l rotated by theta_l = -/+ theta/2
  Valley K only.  K_D = (4pi/3a, 0).
  Heterostrain: layer l carries strain tensor E_l = -/+ E/2 with
      E = eps * [[cos^2 phi - nu sin^2 phi, (1+nu) sin phi cos phi],
                 [(1+nu) sin phi cos phi,  sin^2 phi - nu cos^2 phi]]
      nu = 0.16 (Poisson ratio), phi = strain direction.
  Strain moves the layer Dirac point geometrically, K_l = (1 - E_l) R(theta_l) K_D,
  and adds the pseudo-gauge shift A_l = (sqrt(3) beta / 2a) (E_l,xx - E_l,yy, -2 E_l,xy),
  beta = 3.14 (Bi, Yuan & Fu 2019 form).  Effective Dirac point: K_l + A_l.
  Intralayer:  h_l(p) = hbar v  [R(-theta_l)(p - A_l)] . sigma,  p measured from K_l
      (the geometric shift of K_l is carried entirely by the q_j below)
  Interlayer:  layer-1 momentum p couples to layer-2 momentum p + q_j (j=1,2,3),
      q_j = K_j^(1) - K_j^(2),  K_j = C3^(j-1) K_D  (three equivalent K points),
      T_j = w0 * 1 + w1 * [cos(2pi(j-1)/3) sx + sin(2pi(j-1)/3) sy].
  Moire reciprocal vectors  G1 = q_2 - q_1,  G2 = q_3 - q_1.
  Plane-wave basis: layer-1 momenta k + G, layer-2 momenta k + G + q_1,
      G = m G1 + n G2 with |G| <= N * |G1|  ("N shells").

Perturbations (both couple only nearest harmonics, hence bounded):
  scalar   :  V(r) = A * w1 * sum_{j=1}^{3} cos(G_j . r) * 1_sub * 1_layer
              (G_3 = G2 - G1).  Real, even in r, layer-symmetric:
              preserves C2zT, breaks the BM particle-hole P.
  mass     :  m * sigma_z, same sign in both layers:  breaks C2zT.
"""
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import minimize

sx = np.array([[0, 1], [1, 0]], complex)
sy = np.array([[0, -1j], [1j, 0]], complex)
sz = np.array([[1, 0], [0, -1]], complex)
s0 = np.eye(2, dtype=complex)

A_LAT = 2.46
HBARV = 5944.0  # meV*A


def rot(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])


class BM:
    def __init__(self, theta_deg=1.05, w1=110.0, ratio=0.8, eps=0.0, phi_deg=0.0,
                 nu=0.16, beta=3.14, N=4, A_scalar=0.0, mass=0.0, kinetic='none', geometry='linear'):
        # geometry: 'linear' (campaign: K_l=(1-E_l)R K, q_j linearised) | 'exact' ((1+E_l)^{-T} R, as tbg_ref)
        if geometry not in ('linear', 'exact'): raise ValueError(geometry)
        self.geometry = geometry
        # kinetic: 'none' (v023 campaign), 'full' (v039: [I+(1-beta)E] R^T, lab gauge),
        #          'lab_nn_full' (v041 declared: R^T [I+(1-beta)E], crystal-frame gauge rotated to lab)
        if kinetic not in ('none', 'full', 'lab_nn_full'): raise ValueError(kinetic)
        self.kinetic, self.beta = kinetic, beta
        self.theta = np.radians(theta_deg)
        self.w1, self.w0 = w1, ratio * w1
        self.N = N
        self.A_scalar, self.mass = A_scalar, mass
        phi = np.radians(phi_deg)
        E = eps * np.array([[np.cos(phi) ** 2 - nu * np.sin(phi) ** 2,
                             (1 + nu) * np.sin(phi) * np.cos(phi)],
                            [(1 + nu) * np.sin(phi) * np.cos(phi),
                             np.sin(phi) ** 2 - nu * np.cos(phi) ** 2]])
        KD = np.array([4 * np.pi / (3 * A_LAT), 0.0])
        self.thetas = [-self.theta / 2, +self.theta / 2]
        self.Es = [-E / 2, +E / 2]
        self.Kl, self.Al = [], []
        lat = (lambda El, th, v: np.linalg.inv(np.eye(2) + El).T @ rot(th) @ v) if geometry == 'exact' \
              else (lambda El, th, v: (np.eye(2) - El) @ rot(th) @ v)
        for th, El in zip(self.thetas, self.Es):
            self.Kl.append(lat(El, th, KD))
            if kinetic == 'lab_nn_full':
                Ec = rot(-th) @ El @ rot(th)                       # strain in the layer's crystal frame
                Ac = np.sqrt(3) * beta / (2 * A_LAT) * np.array([Ec[0, 0] - Ec[1, 1], -2 * Ec[0, 1]])
                self.Al.append(rot(th) @ Ac)                       # rotated back to the lab
            else:
                self.Al.append(np.sqrt(3) * beta / (2 * A_LAT)
                               * np.array([El[0, 0] - El[1, 1], -2 * El[0, 1]]))
        # three equivalent K points and q vectors
        self.q = []
        for j in range(3):
            Kj = rot(2 * np.pi * j / 3) @ KD
            K1 = lat(self.Es[0], self.thetas[0], Kj)
            K2 = lat(self.Es[1], self.thetas[1], Kj)
            self.q.append(K1 - K2)
        self.G1 = self.q[1] - self.q[0]
        self.G2 = self.q[2] - self.q[0]
        self.ktheta = np.linalg.norm(self.q[0])
        self.T = [self.w0 * s0 + self.w1 * (np.cos(2 * np.pi * j / 3) * sx
                                            + np.sin(2 * np.pi * j / 3) * sy)
                  for j in range(3)]
        # plane-wave lattice
        gmax = N * np.linalg.norm(self.G1) + 1e-6
        idx = []
        for m in range(-3 * N, 3 * N + 1):
            for n in range(-3 * N, 3 * N + 1):
                if np.linalg.norm(m * self.G1 + n * self.G2) <= gmax:
                    idx.append((m, n))
        self.idx = idx
        self.pos = {mn: i for i, mn in enumerate(idx)}
        self.nG = len(idx)
        self.dim = 4 * self.nG
        self.Gvec = np.array([m * self.G1 + n * self.G2 for m, n in idx])
        self._build_static()

    # ---- static (k-independent) part -------------------------------------
    def _build_static(self):
        D, nG = self.dim, self.nG
        H = np.zeros((D, D), complex)
        # interlayer tunneling: layer1 (m,n) -> layer2 (m,n)+d_j
        shifts = [(0, 0), (1, 0), (0, 1)]
        for j, (dm, dn) in enumerate(shifts):
            for (m, n), i in self.pos.items():
                t = (m + dm, n + dn)
                if t in self.pos:
                    i2 = self.pos[t]
                    r, c = 2 * nG + 2 * i2, 2 * i
                    H[r:r + 2, c:c + 2] += self.T[j]
                    H[c:c + 2, r:r + 2] += self.T[j].conj().T
        # bounded scalar moire potential (same in both layers)
        if self.A_scalar != 0.0:
            V = 0.5 * self.A_scalar * self.w1
            for lay in range(2):
                off = 2 * nG * lay
                for (m, n), i in self.pos.items():
                    for dm, dn in [(1, 0), (-1, 0), (0, 1), (0, -1), (-1, 1), (1, -1)]:
                        t = (m + dm, n + dn)
                        if t in self.pos:
                            i2 = self.pos[t]
                            H[off + 2 * i2:off + 2 * i2 + 2, off + 2 * i:off + 2 * i + 2] += V * s0
        # C2zT-breaking sublattice mass
        if self.mass != 0.0:
            for i in range(2 * nG):
                H[2 * i:2 * i + 2, 2 * i:2 * i + 2] += self.mass * sz
        self.Hstat = H

    # ---- k-dependent Dirac part -------------------------------------------
    def H(self, k):
        H = self.Hstat.copy()
        nG = self.nG
        for lay in range(2):
            Rinv = rot(-self.thetas[lay]); V = np.eye(2) + (1 - self.beta) * self.Es[lay]
            M = {'none': Rinv, 'full': V @ Rinv, 'lab_nn_full': Rinv @ V}[self.kinetic]
            p = k[None, :] + self.Gvec + (self.q[0][None, :] if lay == 1 else 0.0)
            pp = (p - self.Al[lay]) @ M.T
            off = 2 * nG * lay
            for i in range(nG):
                H[off + 2 * i:off + 2 * i + 2, off + 2 * i:off + 2 * i + 2] += \
                    HBARV * (pp[i, 0] * sx + pp[i, 1] * sy)
        return H

    def frac_to_k(self, f):
        return f[0] * self.G1 + f[1] * self.G2

    def bands_near_zero(self, k, nb=3):
        """Return the nb bands below and nb above charge neutrality."""
        D = self.dim
        lo, hi = D // 2 - nb, D // 2 + nb - 1
        w = eigh(self.H(k), eigvals_only=True, subset_by_index=(lo, hi))
        return w

    def gaps(self, k):
        w = self.bands_near_zero(k, 2)
        # w = [E_-2, E_-1, E_+1, E_+2]; flat bands are w[1], w[2]
        dmid = w[2] - w[1]
        drem = min(w[3] - w[2], w[1] - w[0])
        return dmid, drem, w

    # ---- searches ----------------------------------------------------------
    def grid(self, n, func):
        fs = np.linspace(0, 1, n, endpoint=False)
        out = np.zeros((n, n))
        for i, f1 in enumerate(fs):
            for j, f2 in enumerate(fs):
                out[i, j] = func(np.array([f1, f2]))
        return fs, out

    def local_minima(self, fs, vals, nkeep=6):
        n = len(fs)
        cand = []
        for i in range(n):
            for j in range(n):
                v = vals[i, j]
                nb = [vals[(i + di) % n, (j + dj) % n] for di in (-1, 0, 1) for dj in (-1, 0, 1)
                      if (di, dj) != (0, 0)]
                if v <= min(nb):
                    cand.append((v, fs[i], fs[j]))
        cand.sort()
        return cand[:nkeep]

    def refine(self, f0, func, tol=1e-10, return_result=False):
        res = minimize(lambda f: func(np.array(f)), f0, method='Nelder-Mead',
                       options={'xatol': 1e-7, 'fatol': tol, 'maxiter': 600})
        self.last_refine = dict(success=bool(res.success), status=int(res.status),
                                message=str(res.message), nfev=int(res.nfev))
        fw = res.x % 1.0
        # periodicity check (F08): the truncated plane-wave basis is only approximately
        # periodic, so a node found across a BZ edge is re-refined in the canonical frame
        # and the displacement is recorded rather than silently accepted.
        self.last_refine['wrap_shift'] = 0.0
        if np.any(np.abs(fw - res.x) > 1e-12):
            res2 = minimize(lambda f: func(np.array(f)), fw, method='Nelder-Mead',
                            options={'xatol': 1e-7, 'fatol': tol, 'maxiter': 600})
            self.last_refine['wrap_shift'] = float(np.linalg.norm(res2.x - fw))
            self.last_refine['nfev'] += int(res2.nfev)
            fw, res = res2.x % 1.0, res2
        vw = func(fw)
        if not np.isfinite(vw) or abs(vw - res.fun) > 1e-6 * max(1.0, abs(res.fun)):
            self.last_refine['success'] = False
            self.last_refine['message'] += ' | value changed under periodic wrap'
        if return_result:
            return fw, res.fun, self.last_refine
        return fw, res.fun

    def find_nodes(self, ngrid=18, nkeep=6):
        func = lambda f: self.gaps(self.frac_to_k(f))[0]
        fs, vals = self.grid(ngrid, func)
        out = []
        for v, f1, f2 in self.local_minima(fs, vals, nkeep):
            f, val = self.refine(np.array([f1, f2]), func)
            out.append((val, f))
        # merge duplicates (periodic distance)
        merged = []
        for val, f in sorted(out, key=lambda t: t[0]):
            dup = False
            for _, g in merged:
                d = (f - g + 0.5) % 1.0 - 0.5
                if np.linalg.norm(d) < 0.01:
                    dup = True
            if not dup:
                merged.append((val, f))
        return merged

    def min_remote(self, ngrid=18, nkeep=4):
        func = lambda f: self.gaps(self.frac_to_k(f))[1]
        fs, vals = self.grid(ngrid, func)
        best = (np.inf, None)
        for v, f1, f2 in self.local_minima(fs, vals, nkeep):
            f, val = self.refine(np.array([f1, f2]), func, tol=1e-9)
            if val < best[0]:
                best = (val, f)
        return best

    def flat_bandwidth(self, ngrid=18):
        fs = np.linspace(0, 1, ngrid, endpoint=False)
        lo, hi = np.inf, -np.inf
        for f1 in fs:
            for f2 in fs:
                w = self.bands_near_zero(self.frac_to_k(np.array([f1, f2])), 1)
                lo, hi = min(lo, w[0]), max(hi, w[1])
        return hi - lo


def frac_dist(f, g):
    d = (f - g + 0.5) % 1.0 - 0.5
    return np.linalg.norm(d)


def wrap(d):
    """shortest periodic representative of a fractional displacement"""
    return (np.asarray(d, float) + 0.5) % 1.0 - 0.5


def segment_geometry(F1, F3, Q):
    """Consistent periodic geometry (audit F02): lift F3 and Q into F1's frame by the
    shortest periodic displacement, then return (t, offset) of Q relative to the F1->F3
    segment. Raises on coincident endpoints instead of dividing by zero."""
    d = wrap(np.asarray(F3) - np.asarray(F1)); L = np.linalg.norm(d)
    if L < 1e-9:
        raise ValueError('segment endpoints coincide (sep=%.2e)' % L)
    n = np.array([-d[1], d[0]]) / L
    rel = wrap(np.asarray(Q) - np.asarray(F1))
    return float(rel @ d / L**2), float(rel @ n), L
