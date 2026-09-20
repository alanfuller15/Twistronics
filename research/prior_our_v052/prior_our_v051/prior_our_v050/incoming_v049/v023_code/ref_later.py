import numpy as np, time, sys
from tbg_ref import TBG
kin=sys.argv[1] if len(sys.argv)>1 else 'full'; N=int(sys.argv[2]) if len(sys.argv)>2 else 4
STAGES=set(sys.argv[3].split(',')) if len(sys.argv)>3 else {'v029','v031','v033'}
print(f"kinetic={kin} N={N}")
# v029 pre-annihilation and post-transfer
if 'v029' in STAGES:
  t=time.time(); m=TBG(N=N,eps=0.003,phi=65,A=0.0,B=-0.40,Bt=-0.70,kinetic=kin); U=m.real_basis(); lo=m.dim//2-1
  nodes=m.find_nodes(n=24,keep=8)
  if len(nodes)==2:
      w1,w2,lab=m.relative_charge(U,nodes[0],nodes[1],lo); print(f"  v029 Btau=-0.70 flat pair: {[tuple(np.round(f,4)) for f in nodes]} sep {np.linalg.norm(((nodes[0]-nodes[1])+0.5)%1-0.5):.4f} charges {w1:+d},{w2:+d} -> {lab}  [logged OPPOSITE] ({time.time()-t:.0f}s)")
  else: print(f"  v029 Btau=-0.70: {len(nodes)} flat nodes {[tuple(np.round(f,3)) for f in nodes]}")
  t=time.time(); m=TBG(N=N,eps=0.003,phi=65,A=0.0,B=-0.40,Bt=-0.74,kinetic=kin); U=m.real_basis()
  fl=m.find_nodes(n=24,keep=8); up=m.find_nodes(fn=m.gap(3),n=24,keep=8)
  print(f"  v029 Btau=-0.74: flat nodes {len(fl)} (min flat gap {m.gap_min(2):.3f} meV), upper nodes {[tuple(np.round(f,3)) for f in up]}, lower gap min {m.gap_min(1):.2f}",end='')
  if len(up)==2:
      w1,w2,lab=m.relative_charge(U,up[0],up[1],m.dim//2); print(f" | U pair charges {w1:+d},{w2:+d} -> {lab} [logged SAME] ({time.time()-t:.0f}s)")
  else: print()
# v031 U-pair braid via w0/w1
for ratio in ([0.99,1.00] if 'v031' in STAGES else []):
    t=time.time(); m=TBG(N=N,eps=0.003,phi=80,A=0.0,B=-0.40,Bt=-0.80,w0=110.0*ratio,kinetic=kin); U=m.real_basis()
    up=m.find_nodes(fn=m.gap(3),n=24,keep=8)
    if len(up)==2:
        w1,w2,lab=m.relative_charge(U,up[0],up[1],m.dim//2); print(f"  v031 w0/w1={ratio:.2f}: U pair {[tuple(np.round(f,4)) for f in up]} charges {w1:+d},{w2:+d} -> {lab} [logged {'SAME' if ratio<1 else 'OPPOSITE'}] ({time.time()-t:.0f}s)")
    else: print(f"  v031 w0/w1={ratio:.2f}: {len(up)} upper nodes {[tuple(np.round(f,3)) for f in up]}")
# v033 endpoint
if 'v033' in STAGES:
  t=time.time(); m=TBG(N=N,eps=0.003,phi=80,A=-0.30,B=-0.40,Bt=-1.8,w0=110.0*1.1,kinetic=kin); U=m.real_basis(); D=m.dim
  gaps=[m.gap_min(i) for i in (0,1,2,3,4)]; fl=m.find_nodes(n=24,keep=8)
  print(f"  v033 endpoint: gap minima below|lower {gaps[0]:.2f}, lower|flat1 {gaps[1]:.2f}, flat {gaps[2]:.3f}, flat2|upper {gaps[3]:.2f}, upper|next {gaps[4]:.2f} meV; flat nodes {len(fl)}")
  for lab,band in [('lower',D//2-2),('flat1',D//2-1),('flat2',D//2),('upper',D//2+1)]:
      print(f"    {lab:6s} w1 sign holonomy: k1 {m.band_sign_holonomy(U,band,0,0):+.2f},{m.band_sign_holonomy(U,band,0,0.5):+.2f}  k2 {m.band_sign_holonomy(U,band,1,0):+.2f},{m.band_sign_holonomy(U,band,1,0.5):+.2f}")
  print(f"  ({time.time()-t:.0f}s)")
