"""Observe the uploaded global search and report every candidate decision.

No modifications to the uploaded source; wrapper only records refine results.
This tests the reported N4 under-count at the precise v029 checkpoint.
"""
import json
from pathlib import Path
import numpy as np
from models import make,State
ROOT=Path(__file__).resolve().parent

def run():
    m=make('v039_full',4,State(A=0,B=-.4,T=-.7,phi=65,ratio=.8)).model
    original=m.refine;candidates=[]
    def traced(seed,fn):
        f,val=original(seed,fn)
        candidates.append(dict(seed=np.asarray(seed).tolist(),f=f.tolist(),gap=float(val),cone_samples=[float(fn(f+.01*np.array(d))) for d in [[1,0],[0,1]]]))
        return f,val
    m.refine=traced
    global_nodes=m.find_nodes(n=24,keep=8)
    m.refine=original
    local=[m.refine(np.array(seed),m.flat_gap)[0] for seed in [[.6464,.8378],[.6273,.834]]]
    loop_records=[];original_charge=m.node_charge
    def traced_charge(*args,**kwargs):
        q=original_charge(*args,**kwargs);loop_records.append(dict(returned_charge=int(q),min_overlap=float(m.last_smin)));return q
    m.node_charge=traced_charge
    u=m.real_basis();charges=m.relative_charge(u,local[0],local[1],m.dim//2-1)
    endpoint=make('v039_full',4,State(A=-.30,T=-1.8,ratio=1.1)).model
    logged_search=float(endpoint.gap_min(1))
    gated=json.loads((ROOT/'results/endpoint_v039_full_N4.json').read_text())
    best=min((t['minimum'] for t in gated['gaps']['lower']),key=lambda r:r['gap'])
    direct=float(endpoint.gap(1)(np.array(best['f'])))
    return dict(status='OBSERVED',N=4,global_nodes=[f.tolist() for f in global_nodes],candidates=candidates,
                local_nodes=[f.tolist() for f in local],local_separation=float(np.linalg.norm(local[1]-local[0])),
                charges=[int(charges[0]),int(charges[1]),charges[2]],loop_records=loop_records,
                printed_last_smin=float(m.last_smin),pair_min_smin=min(q['min_overlap'] for q in loop_records),
                endpoint_lower_gap=dict(uploaded_default_search=logged_search,boundary_minimum=best,
                                        direct_uploaded_H_at_boundary_minimum=direct))

if __name__=='__main__':
    r=run();(ROOT/'results/search_diagnostic.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
