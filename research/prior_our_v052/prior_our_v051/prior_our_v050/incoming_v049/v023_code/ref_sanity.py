import numpy as np, time
from tbg_ref import TBG
t=time.time(); m=TBG(N=4)
print("dim",m.dim,"|q0|",np.linalg.norm(m.q[0]))
for f in ([0,0],[1/3,1/3],[2/3,2/3]):
    w=m.bands(m.k(np.array(f)),2); print(" f",f,"flat gap %.2e"%(w[2]-w[1]),"remote %.2f"%min(w[3]-w[2],w[1]-w[0]),np.round(w,3))
fs=np.linspace(0,1,12,endpoint=False); lo=min(m.bands(m.k(np.array([a,b])),1)[0] for a in fs for b in fs); hi=max(m.bands(m.k(np.array([a,b])),1)[1] for a in fs for b in fs)
print(" bandwidth %.2f meV"%(hi-lo), "(%.0fs)"%(time.time()-t))
U=m.real_basis(); print(" real basis OK; residual at random k: %.1e"%np.abs((U.conj().T@m.H(m.k(np.array([0.31,0.27])))@U).imag).max())
e,cl,md=m.euler_plaquette(U,m.dim//2-1,n1=18,n2=18); print(" unstrained plaquette Euler class e2 = %+.3f  closure %s  min plaquette det %+.2f"%(e,tuple(np.round(cl,2)),md))
