import numpy as np, time
from tbg_ref import TBG
t=time.time(); m=TBG(N=4,eps=0.003,phi=0.0); U=m.real_basis(); lo=m.dim//2-1
nodes=m.find_nodes(); print("v023 baseline, second implementation, N=4")
print("  flat-gap nodes:",[tuple(np.round(f,5)) for f in nodes],"  (bm_strain: (0.75641,0.60857),(0.57869,0.72848))")
seedsR=sorted([(m.remote_gap(np.array([a,b])),a,b) for a in np.linspace(0,1,15,endpoint=False) for b in np.linspace(0,1,15,endpoint=False)])[:4]
rem=min(m.refine(np.array([a,b]),m.remote_gap)[1] for _,a,b in seedsR); print("  min remote gap: %.4f meV  (bm_strain N=4: 5.458, converged 5.500)"%rem)
fs=np.linspace(0,1,12,endpoint=False); lo_=min(m.bands(m.k(np.array([a,b])),1)[0] for a in fs for b in fs); hi=max(m.bands(m.k(np.array([a,b])),1)[1] for a in fs for b in fs)
print("  bandwidth: %.3f meV (bm_strain: 24.259)"%(hi-lo_))
e,cl,md=m.euler_plaquette(U,lo,n1=24,n2=24); print("  plaquette Euler class: e2 = %+.3f, closure %s, min det %+.2f  (bm_strain Wilson loop: -1.000)"%(e,tuple(np.round(cl,3)),md))
w1,w2,lab=m.relative_charge(U,nodes[0],nodes[1],lo); print("  node charges (effective-2x2 winding): %+d, %+d -> %s  (bm_strain: SAME)"%(w1,w2,lab))
print("  (%.0fs)"%(time.time()-t))
