"""Eight-band guarded measurements; finite searches are not global proofs."""
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import least_squares,minimize
from models import make
from independent_measurement import align,traceless_vector,phase_winding,require,Rejected

GAPS=dict(lower=2,flat=3,upper=4,next=5)
class Sample:
    def __init__(self,engine,N,p):
        self.model=make(engine,N,p);self.cache={};self.metrics=dict(max_eigen_residual=0.,max_reality=0.,max_hermitian=0.)
    def at(self,f):
        key=tuple(np.asarray(f,float))
        if key not in self.cache:
            h,d=self.model.real_hamiltonian(f);lo=self.model.dim//2-4
            w,v=eigh(h,subset_by_index=[lo,lo+7],driver='evx')
            res=float(np.max(np.abs(h@v-v*w))/max(1.,np.max(np.abs(h))))
            require(np.isfinite(w).all() and np.isfinite(v).all(),'nonfinite eigenpairs')
            require(res<1e-10,'eigen residual');require(np.max(np.abs(v.T@v-np.eye(8)))<1e-8,'eigen orthogonality')
            self.metrics['max_eigen_residual']=max(res,self.metrics['max_eigen_residual'])
            self.metrics['max_reality']=max(d['reality_residual'],self.metrics['max_reality'])
            self.metrics['max_hermitian']=max(d['hermitian_residual'],self.metrics['max_hermitian'])
            self.cache[key]=(w,v)
        return self.cache[key]
    def frame(self,f,index,nb=2):
        w,v=self.at(f);require(0<index and index+nb<len(w),'missing external band')
        gap=float(min(w[index]-w[index-1],w[index+nb]-w[index+nb-1]));require(gap>1e-5,'selected group loses isolation')
        return w[index:index+nb],v[:,index:index+nb]
    def vector(self,f,anchor,index):
        w,v=self.frame(f,index);e,s=align(v,anchor);o=v.T@e
        return traceless_vector(o.T@np.diag(w-w.mean())@o),s
    def node(self,seed,index):
        _,anchor=self.frame(seed,index)
        sol=least_squares(lambda f:self.vector(f,anchor,index)[0],seed,xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=150)
        w,_=self.frame(sol.x,index);gap=float(w[1]-w[0]);require(sol.success and gap<1e-6,'node root unresolved')
        return dict(f=sol.x.tolist(),gap=gap,index=index,nfev=sol.nfev)
    def winding(self,node,anchor,index,r,n):
        z=[];overlaps=[]
        for t in np.linspace(0,2*np.pi,n+1):
            d,s=self.vector(np.array(node)+r*np.array([np.cos(t),np.sin(t)]),anchor,index);z.append(d);overlaps.append(s)
        row=phase_winding(np.array(z));row['min_chart_overlap']=min(overlaps);return row
    def transport(self,a,b,base,index,adjacent=(),steps=128):
        a=np.asarray(a);b=np.asarray(b);d=b-a;L=float(np.linalg.norm(d));require(L>1e-5,'collapsed path')
        ts=list(np.linspace(0,1,steps+1))
        for node in adjacent:
            q=np.asarray(node['f']);t=float((q-a)@d/L**2)
            if not 0<t<1:continue
            dist=float(np.linalg.norm(q-a-t*d));ts.append(t);scale=max(dist/L,1e-7)
            for j in range(-2,9):ts.extend([t-scale*2**j,t+scale*2**j])
        ts=sorted(set(t for t in ts if 0<=t<=1));frame=base;minimum=1.;minimum_gap=1e100
        for t in ts[1:]:
            f=a+t*d;w,_=self.at(f);minimum_gap=min(minimum_gap,float(min(w[index]-w[index-1],w[index+2]-w[index+1])))
            _,q=self.frame(f,index);frame,s=align(q,frame);minimum=min(minimum,s)
        return frame,dict(min_overlap=minimum,min_external_gap=minimum_gap,samples=len(ts))
    def pair(self,seeds,index,r=.004,adjacent=()):
        nodes=[self.node(s,index) for s in seeds];a,b=[np.array(z['f']) for z in nodes]
        distance=float(np.linalg.norm(b-a));require(distance>3*r,'node loops overlap or duplicate roots')
        _,base=self.frame(a,index);trials=[]
        for radius,n,steps in [(r,64,128),(r,128,256),(r/2,128,256)]:
            end,td=self.transport(a,b,base,index,adjacent,steps)
            qa=self.winding(a,base,index,radius,n);qb=self.winding(b,end,index,radius,n)
            trials.append(dict(radius=radius,points=n,transport=td,a=qa,b=qb,label='SAME' if qa['charge']*qb['charge']>0 else 'OPPOSITE'))
        require(len({r['label'] for r in trials})==1,'pair label fails mesh/radius refinement')
        return dict(nodes=nodes,separation=distance,label=trials[0]['label'],trials=trials)
    def minimum(self,index,ng,extra=()):
        # Bound all refinements to this explicit chart: finite-cutoff H is not
        # exactly periodic, so coordinates/values are never silently wrapped.
        fs=np.linspace(0,1,ng,endpoint=False);values=np.empty((ng,ng))
        for i,x in enumerate(fs):
            for j,y in enumerate(fs):
                w,_=self.at([x,y]);values[i,j]=w[index+1]-w[index]
        seeds=[np.array(s,float) for s in extra]
        for i,x in enumerate(fs):
            for j,y in enumerate(fs):
                if values[i,j]<=min(values[(i+a)%ng,(j+b)%ng] for a in [-1,0,1] for b in [-1,0,1]):seeds.append(np.array([x,y]))
        best=np.unravel_index(np.argmin(values),values.shape);seeds.append(np.array([fs[best[0]],fs[best[1]]]))
        h0,_=self.model.real_hamiltonian([0,0]);dh=[self.model.real_hamiltonian(e)[0]-h0 for e in [[1,0],[0,1]]]
        def objective(f):
            w,v=self.at(f);vec=v[:,index:index+2];slope=[np.einsum('ij,ij->j',vec,d@vec) for d in dh]
            return float(w[index+1]-w[index]),np.array([s[1]-s[0] for s in slope])
        rows=[]
        for seed in seeds:
            seed=np.clip(seed,0,1);initial=objective(seed)[0]
            sol=minimize(objective,seed,method='L-BFGS-B',jac=True,bounds=[(0,1),(0,1)],options=dict(ftol=1e-14,gtol=1e-7,maxiter=300,maxls=40))
            attempts=[dict(method='L-BFGS-B',success=bool(sol.success),message=str(sol.message),value=float(sol.fun))]
            if not sol.success or sol.fun>initial+1e-7:
                sol=minimize(objective,seed,method='SLSQP',jac=True,bounds=[(0,1),(0,1)],options=dict(ftol=1e-12,maxiter=500))
                attempts.append(dict(method='SLSQP',success=bool(sol.success),message=str(sol.message),value=float(sol.fun)))
            require(sol.success and sol.fun<=initial+1e-7,'gap refinement failed or worsened seed')
            rows.append(dict(f=sol.x.tolist(),gap=float(sol.fun),seed=seed.tolist(),attempts=attempts))
        best=min(rows,key=lambda z:z['gap']);require(best['gap']<=float(values.min())+1e-7,'minimum worse than grid')
        return dict(grid=ng,grid_min=float(values.min()),minimum=best,refinements=rows)

def geometry(a,b,q):
    a=np.asarray(a);b=np.asarray(b);d=b-a;L=np.linalg.norm(d);require(L>1e-8,'collapsed geometry')
    return dict(t=float((q-a)@d/L**2),offset=float((q-a)@np.array([-d[1],d[0]])/L))
