"""Real Fourier-coefficient pullback between changing reciprocal cutoffs.

Identify cell coordinates and remove each model's declared Bloch/layer phases;
then label the periodic envelope by (layer,m,n,real-spinor-index). Missing
Fourier coefficients are zero in a common Hilbert space. Lost frame norm is
measured, not silently renormalized away. This is a declared numerical bundle
identification, not an assertion of laboratory-coordinate time evolution.
"""
import numpy as np
from independent_measurement import require

def labels(adapter):
    m=adapter.model;indices=m.idx if adapter.engine=='bm_lab' else m.mn
    return np.array([(l,a,b,s) for l in (0,1) for a,b in indices for s in (0,1)],int)

def carry(previous,old_labels,current,new_labels):
    old=[tuple(x) for x in old_labels];new=[tuple(x) for x in new_labels]
    require(len(set(old))==len(old) and len(set(new))==len(new),'duplicate basis indices')
    require(previous.shape==(len(old),2) and current.shape==(len(new),2),'basis/frame shape mismatch')
    require(np.isfinite(previous).all() and np.isfinite(current).all(),'nonfinite transport frame')
    lookup={x:i for i,x in enumerate(old)}
    pairs=[(lookup[x],j) for j,x in enumerate(new) if x in lookup]
    require(bool(pairs),'no shared basis')
    oi,ni=np.array(pairs).T;a=previous[oi];b=current[ni]
    old_loss=max(0.,float(np.linalg.eigvalsh(np.eye(2)-a.T@a).max()))
    new_loss=max(0.,float(np.linalg.eigvalsh(np.eye(2)-b.T@b).max()))
    require(old_loss<=.02 and new_loss<=.02,'basis truncation loses too much frame norm')
    u,s,vh=np.linalg.svd(b.T@a);require(float(s.min())>.1,'parameter overlap too small')
    result=current@u@vh
    require(np.max(np.abs(result.T@result-np.eye(2)))<1e-8,'carried frame not orthonormal')
    return result,dict(min_overlap=float(s.min()),old_norm_loss=old_loss,new_norm_loss=new_loss,
                       old_dimension=len(old),new_dimension=len(new),common_dimension=len(pairs),
                       removed=len(old)-len(pairs),added=len(new)-len(pairs))
