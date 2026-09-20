"""Numerical acceptance gate (audit v034). Every charge label must pass through
classify(); every real-basis frame must pass through real_frame_checked();
every parallel-transport step through ortho_checked()."""
import numpy as np
from scipy.linalg import eigh

REAL_TOL = 1e-9      # max |Im H| allowed in the C2zT-real basis, meV
WIND_TOL = 0.15      # |w| must be within this of +/-1
COND_TOL = 1e-6      # smallest |R_ii| in QR of a transported frame


class GateError(RuntimeError):
    pass


def real_basis(nG):
    u2 = np.array([[1, 1j], [1, -1j]]) / np.sqrt(2)
    return np.kron(np.eye(2 * nG), u2)


def real_frame_checked(m, U, k, lo, nb=2):
    """Eigenframe of bands lo..lo+nb-1 in the real basis, with the reality residual checked (F04)."""
    HR = U.conj().T @ m.H(k) @ U
    res = float(np.abs(HR.imag).max())
    if res > REAL_TOL:
        raise GateError('Hamiltonian not real in C2zT basis: max|Im|=%.2e meV' % res)
    w, v = eigh(HR.real, subset_by_index=(lo, lo + nb - 1))
    return v


def ortho_checked(M):
    """Orthonormalise the columns of M; refuse rank-deficient input instead of zeroing a column (F03)."""
    q, r = np.linalg.qr(M)
    dr = np.abs(np.diag(r))
    if dr.min() < COND_TOL:
        raise GateError('frame transport became singular: min|R_ii|=%.2e' % dr.min())
    return q * np.sign(np.diag(r))


def classify(w_a, w_b):
    """SAME / OPPOSITE / INDETERMINATE from two windings; zero, non-finite or non-integer
    windings are never labelled (F05)."""
    for w in (w_a, w_b):
        if not np.isfinite(w) or abs(abs(w) - 1.0) > WIND_TOL:
            return 'INDETERMINATE'
    return 'SAME' if w_a * w_b > 0 else 'OPPOSITE'


def require_nodes(nodes, n):
    if len(nodes) < n:
        raise GateError('need %d nodes, found %d' % (n, len(nodes)))
