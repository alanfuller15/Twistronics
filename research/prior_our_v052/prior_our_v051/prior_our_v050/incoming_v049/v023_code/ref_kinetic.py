import numpy as np, time
from tbg_ref import TBG
def remote(m):
    seeds=sorted([(m.remote_gap(np.array([a,b])),a,b) for a in np.linspace(0,1,15,endpoint=False) for b in np.linspace(0,1,15,endpoint=False)])[:3]
    return min(m.refine(np.array([a,b]),m.remote_gap)[1] for _,a,b in seeds)
for kin in ['none','geom_wrong','full']:
    t=time.time(); m=TBG(N=4,eps=0.003,kinetic=kin); U=m.real_basis(); lo=m.dim//2-1
    nodes=m.find_nodes(n=15,keep=6); rem=remote(m)
    fs=np.linspace(0,1,12,endpoint=False); bw=max(m.bands(m.k(np.array([a,b])),1)[1] for a in fs for b in fs)-min(m.bands(m.k(np.array([a,b])),1)[0] for a in fs for b in fs)
    e,cl,md=m.euler_plaquette(U,lo,n1=18,n2=18); w1,w2,lab=m.relative_charge(U,nodes[0],nodes[1],lo)
    print(f"kinetic={kin:10s}: nodes {[tuple(np.round(f,4)) for f in nodes]} sep {np.linalg.norm(((nodes[0]-nodes[1])+0.5)%1-0.5):.4f} | remote gap {rem:.3f} meV | bw {bw:.2f} | e2 {e:+.3f} (closure {min(cl):+.2f}) | charges {w1:+d},{w2:+d} {lab} ({time.time()-t:.0f}s)")
print("v026 braid with the full kinetic tensor:")
for B in [-0.25,-0.30]:
    m=TBG(N=4,eps=0.003,A=0.20,B=B,kinetic='full'); U=m.real_basis(); lo=m.dim//2-1
    nodes=m.find_nodes(n=24,keep=8)
    if len(nodes)==2:
        w1,w2,lab=m.relative_charge(U,nodes[0],nodes[1],lo); print(f"  B={B:+.2f}: nodes {[tuple(np.round(f,4)) for f in nodes]} charges {w1:+d},{w2:+d} -> {lab}")
    else: print(f"  B={B:+.2f}: {len(nodes)} nodes {[tuple(np.round(f,3)) for f in nodes]}")
