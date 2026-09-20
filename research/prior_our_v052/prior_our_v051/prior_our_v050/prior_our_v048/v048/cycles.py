import numpy as np
from measure import require,align

def cycle(sample,index,nb,axis,offset,n):
    first=None;previous=None;overlap=1.;gap=1e100
    for t in np.linspace(0,1,n+1):
        f=[t,offset] if axis==0 else [offset,t];w,_=sample.at(f)
        _,q=sample.frame(f,index,nb)
        gap=min(gap,float(min(w[index]-w[index-1],w[index+nb]-w[index+nb-1])))
        if first is None:first=q;previous=q
        else:previous,s=align(q,previous);overlap=min(overlap,s)
    sewn=sample.model.sewing(axis)@first;norm=float(np.max(np.abs(sewn.T@sewn-np.eye(nb))))
    closing=previous.T@sewn;seam=float(np.linalg.svd(closing,compute_uv=False)[-1]);det=float(np.linalg.det(closing))
    require(norm<=.02,'cycle sewing norm loss');require(seam>=.95,'cycle sewing overlap')
    return dict(sign=1 if det>0 else -1,determinant=det,min_overlap=overlap,seam_overlap=seam,seam_norm_error=norm,min_external_gap=gap)

