"""Explicit chart edges, corners and known interior seeds."""
import numpy as np
def seeds(sample,index,extra=()):
    points=[[x,y] for x in [0.,.5,1.] for y in [0.,.5,1.] if x in [0.,1.] or y in [0.,1.]]
    for seed in extra:
        f=np.clip(np.asarray(seed,float),0,1);points.append(f.tolist())
        for axis in [0,1]:
            if f[axis]<.1 or f[axis]>.9:
                q=f.copy();q[axis]=1. if f[axis]<.1 else 0.;points.append(q.tolist())
    return [list(t) for t in sorted(set(tuple(p) for p in points))]
