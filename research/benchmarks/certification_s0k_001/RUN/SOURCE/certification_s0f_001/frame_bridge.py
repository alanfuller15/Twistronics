"""Conditional projector-to-frame bridge. No physical imports."""
from pathlib import Path
import sys
from flint import arb, arb_mat

from certified_s0f import certified_boundary, finite_matrix
from primitives_s0f import enclosure, frobenius, identity


@certified_boundary
def frame_from_projector(q, projector_error, candidate, frame_budget):
    """Caller proves rank(P)=2, P orthogonal, ||P-q||<=error, E^T E=I.

    Candidate balls contain that exact E. A small Gram defect is NOT a proof
    of this premise. The frozen fixtures provide E by exact rational algebra.
    """
    n=q.nrows()
    if q.ncols()!=n or candidate.nrows()!=n or candidate.ncols()!=2:
        raise ValueError('square projector approximation and n-by-2 candidate required')
    eps, budget=arb(projector_error), arb(frame_budget)
    if not finite_matrix(q) or not finite_matrix(candidate) or not eps.is_finite() or not eps>=0 or not budget.is_finite() or not budget>0:
        raise ValueError('finite inputs and nonnegative error / positive budget required')
    residual=frobenius((identity(n)-q)*candidate)
    r=(residual+eps).upper()
    record={'residual_F_bound':enclosure(residual), 'projector_error':enclosure(eps),
            'off_plane_operator_bound':enclosure(r)}
    if not r<1:
        return {**record,'status':'INCONCLUSIVE','reason':'FRAME_PROJECTION_NOT_INJECTIVE'}
    # F=PE(E^T PE)^(-1/2); ||F-E|| <= r+1-sqrt(1-r^2).
    eta=r+1-(1-r*r).sqrt()
    record['frame_operator_error_bound']=enclosure(eta)
    if not eta<budget:
        return {**record,'status':'INCONCLUSIVE','reason':'FRAME_ERROR_BUDGET'}
    balls=arb_mat([[arb(candidate[i,j],eta.upper()) for j in range(2)] for i in range(n)])
    return {**record,'status':'CERTIFIED','reason':'CONDITIONAL_PROJECTOR_FRAME_ENCLOSURE',
            '_frame':balls}
