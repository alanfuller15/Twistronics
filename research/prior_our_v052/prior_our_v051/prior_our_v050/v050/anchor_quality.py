"""Keep provisional anchor rows from being published as accepted node pairs.

No label is promoted to a mesh/radius-gated charge result by this classifier.
"""
import numpy as np

def classify_anchor(row, gap_tol=1e-6, separation_tol=2e-3):
    values=[];seps=[]
    for engine in ['bm','ref']:
        points=np.asarray(row[engine+'_roots'],float)
        gaps=np.asarray(row[engine+'_gaps'],float)
        if points.shape!=(2,2) or gaps.shape!=(2,):raise ValueError('two roots and gaps required per engine')
        if not np.isfinite(points).all() or not np.isfinite(gaps).all() or (gaps<0).any():raise ValueError('invalid anchor values')
        values.extend(gaps);seps.append(float(np.linalg.norm(points[1]-points[0])))
    if max(values)>gap_tol:return 'NONZERO_RESIDUAL_CANDIDATES'
    if min(seps)<=separation_tol:return 'DUPLICATE_OR_UNRESOLVED'
    return 'TWO_LOCAL_ROOTS_UNGATED_CHARGE'
