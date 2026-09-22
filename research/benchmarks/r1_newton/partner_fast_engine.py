"""fast_engine.py — partner engine study: a C2zT real-basis mode for both engines and a Newton node refiner.

Physics is unchanged. The static Hamiltonian is transformed ONCE to the real basis with the closed form of U^dag H U
(U = I (x) u2, u2 = [[1, i], [1, -i]]/sqrt2) and checked real; per k only the Dirac 2x2 blocks are added, which in this
basis are exactly real: hv*(pp_x sigma_z - pp_y sigma_x). If the static part is not real (C2zT broken, e.g. the hBN mass)
construction raises NotReal and the caller must use the complex engine. Build the RealEngine AFTER any add_harmonic call:
it snapshots the static matrix."""
import numpy as np
from scipy.linalg import eigh
import bm_strain as bs
from tbg_ref import R as Rref, HV
class NotReal(RuntimeError): pass
def realify(H):
    Baa = H[0::2, 0::2]; Bab = H[0::2, 1::2]; Bba = H[1::2, 0::2]; Bbb = H[1::2, 1::2]
    R = np.empty_like(H)
    R[0::2, 0::2] = 0.5 * (Baa + Bab + Bba + Bbb); R[0::2, 1::2] = 0.5j * (Baa - Bab + Bba - Bbb)
    R[1::2, 0::2] = 0.5j * (-Baa - Bab + Bba + Bbb); R[1::2, 1::2] = 0.5 * (Baa - Bab - Bba + Bbb)
    return R
class RealEngine:
    def __init__(self, m, tol=1e-9):
        self.m = m; self.kind = 'bm' if hasattr(m, 'Hstat') else 'ref'
        Rs = realify(m.Hstat if self.kind == 'bm' else m.Hs); res = float(np.abs(Rs.imag).max())
        if not res < tol: raise NotReal(f'static Hamiltonian not real in the C2zT basis: max|Im|={res:.2e} meV')
        self.static_residual = res; self.HRs = np.ascontiguousarray(Rs.real); self.D = m.dim; nG = m.nG; self.layers = []
        for l in range(2):
            if self.kind == 'bm':
                Rinv = bs.rot(-m.thetas[l]); V = np.eye(2) + (1 - m.beta) * m.Es[l]
                M = {'none': Rinv, 'full': V @ Rinv, 'lab_nn_full': Rinv @ V}[m.kinetic]; hv = bs.HBARV
                shift = m.q[0][None, :] if l == 1 else 0.0
                ppf = (lambda k, M=M, shift=shift, Al=m.Al[l]: ((k[None, :] + m.Gvec + shift) - Al) @ M.T)
            else:
                V = {'none': np.eye(2), 'geom_wrong': np.eye(2) - m.El[l], 'full': np.eye(2) + (1 - m.beta) * m.El[l], 'lab_nn_full': np.eye(2) + (1 - m.beta) * m.El[l]}[m.kinetic]
                M = Rref(-m.thl[l]) @ V if m.kinetic == 'lab_nn_full' else V @ Rref(-m.thl[l]); hv = HV
                ppf = (lambda k, M=M, l=l: (m.origin + k[None, :] + m.Gv - m.Kl[l][0] - m.Al[l]) @ M.T)
            self.layers.append(dict(M=M, ppf=ppf, idx=2 * nG * l + 2 * np.arange(nG), hv=hv))
        self.G = [m.G1, m.G2]; self.nH = 0
    def kc(self, f): return self.m.frac_to_k(np.asarray(f, float)) if self.kind == 'bm' else self.m.k(np.asarray(f, float))
    def HR_k(self, k):
        self.nH += 1; H = self.HRs.copy()
        for L in self.layers:
            pp = L['ppf'](k); i = L['idx']; a = L['hv'] * pp[:, 0]; b = L['hv'] * pp[:, 1]
            H[i, i] += a; H[i + 1, i + 1] -= a; H[i, i + 1] -= b; H[i + 1, i] -= b
        return H
    def HR(self, f): return self.HR_k(self.kc(f))
    def bands(self, f, nb=3):
        D = self.D; return eigh(self.HR(f), eigvals_only=True, subset_by_index=(D // 2 - nb, D // 2 + nb - 1), overwrite_a=True, check_finite=False)
    def gap(self, gi):
        """gi: 1 lower|flat1, 2 flat, 3 flat2|upper (same convention as tbg_ref.gap)"""
        return lambda f: (lambda w: w[gi + 1] - w[gi])(self.bands(f, 3))
    def frame_k(self, k, lo, nb=2):
        return eigh(self.HR_k(k), subset_by_index=(lo, lo + nb - 1), overwrite_a=True, check_finite=False)[1]
    def dHR_proj(self, F, a):
        """F^T (dHR/df_a) F; dHR/df_a is block diagonal with the same 2x2 block per layer: hv*(dpp_x sz - dpp_y sx), dpp = M G_a"""
        out = np.zeros((F.shape[1], F.shape[1]))
        for L in self.layers:
            dpp = L['M'] @ self.G[a]; i = L['idx']; Fa = F[i]; Fb = F[i + 1]
            out += L['hv'] * (dpp[0] * (Fa.T @ Fa - Fb.T @ Fb) - dpp[1] * (Fa.T @ Fb + Fb.T @ Fa))
        return out
    def newton_node(self, f0, lo, maxit=40, tol=1e-11, trust=0.02, ext_min=1e-5):
        """Newton on the fixed-frame effective 2x2 d-vector of bands (lo, lo+1); H is affine in k, so the only
        approximation per step is the frame. Returns (f, gap, info); info['converged'] False -> caller falls back."""
        f = np.array(f0, float); hist = []
        for it in range(maxit):
            lo4 = max(lo - 1, 0); w, F = eigh(self.HR(f), subset_by_index=(lo4, lo + 2), overwrite_a=True, check_finite=False)
            j = lo - lo4; wp = w[j:j + 2]; Fp = F[:, j:j + 2]; g = wp[1] - wp[0]
            ext = min((wp[0] - w[j - 1]) if j > 0 else np.inf, w[j + 2] - wp[1]); hist.append(dict(it=it, f=f.tolist(), gap=float(g), ext=float(ext)))
            if ext < ext_min: return f, g, dict(converged=False, reason='pair not isolated', evals=it + 1, hist=hist)
            if g < tol: return f, g, dict(converged=True, evals=it + 1, hist=hist)
            A = [self.dHR_proj(Fp, a) for a in (0, 1)]
            J = np.array([[(A[0][0, 0] - A[0][1, 1]) / 2, (A[1][0, 0] - A[1][1, 1]) / 2], [A[0][0, 1], A[1][0, 1]]])
            try: step = np.linalg.solve(J, -np.array([(wp[0] - wp[1]) / 2, 0.0]))
            except np.linalg.LinAlgError: return f, g, dict(converged=False, reason='singular Jacobian', evals=it + 1, hist=hist)
            n = np.linalg.norm(step); f = f + (step * trust / n if n > trust else step)
        return f, g, dict(converged=False, reason='maxit', evals=maxit, hist=hist)
