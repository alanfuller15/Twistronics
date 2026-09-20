"""Projected-Hamiltonian charge estimator, independent of legacy winding code.

A fixed reference two-plane defines a smooth local gauge on each small loop.
Polar Procrustes steps transport its orientation along the connecting path.
Charge is winding of (h11-h22, 2*h12), not eigenvector-angle accumulation.
"""
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import least_squares

class Rejected(ValueError):pass

def require(test,message):
    if not bool(test):raise Rejected(message)

def align(frame,reference):
    u,s,vh=np.linalg.svd(frame.T@reference,full_matrices=False)
    require(np.min(s)>.1,'projection/transport overlap too small')
    result=frame@u@vh
    require(np.max(np.abs(result.T@result-np.eye(result.shape[1])))<1e-8,'lost orthonormality')
    return result,float(np.min(s))

def traceless_vector(matrix):
    return np.array([matrix[0,0]-matrix[1,1],2*matrix[0,1]])

def phase_winding(vectors):
    z=vectors[:,0]+1j*vectors[:,1]
    require(np.isfinite(z).all() and np.min(np.abs(z))>1e-6,'unresolved loop gap')
    increments=np.angle(z[1:]*z[:-1].conj())
    require(np.max(np.abs(increments))<np.pi/2,'loop phase steps unresolved')
    winding=float(increments.sum()/(2*np.pi));charge=int(round(winding))
    require(abs(winding-charge)<.05 and abs(charge)==1,'charge not resolved unit integer')
    require(abs(z[-1]-z[0])<1e-7*max(1.,abs(z[0])),'loop gauge did not close')
    return dict(winding=winding,charge=charge,min_loop_gap=float(np.min(np.abs(z))),max_phase_step=float(np.max(np.abs(increments))))

class Measurement:
    def __init__(self,model):
        self.model=model;self.lo=model.dim//2-1;self.cache={}
        self.metrics=dict(max_hermitian=0.,max_reality=0.,max_eigen_residual=0.,min_external_gap=float('inf'))

    def sample(self,f):
        key=tuple(np.asarray(f,float))
        if key not in self.cache:
            h,diag=self.model.real_hamiltonian(f)
            # evx uses bisection/inverse iteration, unlike reference default evr.
            w,v=eigh(h,subset_by_index=[self.lo-1,self.lo+2],driver='evx')
            residual=float(np.max(np.abs(h@v-v*w))/max(1.,np.max(np.abs(h))))
            require(residual<1e-10,'eigen residual')
            require(np.max(np.abs(v.T@v-np.eye(4)))<1e-8,'eigen orthogonality')
            self.metrics['max_eigen_residual']=max(self.metrics['max_eigen_residual'],residual)
            self.metrics['max_reality']=max(self.metrics['max_reality'],diag['reality_residual'])
            self.metrics['max_hermitian']=max(self.metrics['max_hermitian'],diag['hermitian_residual'])
            self.cache[key]=(w,v)
        return self.cache[key]

    def frame(self,f):
        w,v=self.sample(f)
        gap=float(min(w[1]-w[0],w[3]-w[2]))
        require(gap>1e-5,'flat pair not isolated at sampled point')
        self.metrics['min_external_gap']=min(self.metrics['min_external_gap'],gap)
        return w[1:3],v[:,1:3]

    def projected_vector(self,f,reference):
        w,v=self.frame(f);e,overlap=align(v,reference);change=v.T@e
        # Subtract average first to avoid cancelling a large common energy.
        effective=change.T@np.diag(w-w.mean())@change
        return traceless_vector(effective),overlap

    def node(self,seed):
        _,anchor=self.frame(seed)
        def objective(f):return self.projected_vector(f,anchor)[0]
        sol=least_squares(objective,np.asarray(seed,float),xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=200)
        residual=float(np.linalg.norm(objective(sol.x)))
        require(sol.success and residual<1e-6,'node root not converged')
        w,_=self.frame(sol.x)
        return dict(f=sol.x.tolist(),gap=float(w[1]-w[0]),energy=float(w.mean()),nfev=sol.nfev,status=int(sol.status),message=sol.message,residual=residual)

    def transport(self,a,b,reference,steps):
        frame=reference;minimum=1.
        for t in np.linspace(0,1,steps+1)[1:]:
            _,q=self.frame((1-t)*np.asarray(a)+t*np.asarray(b))
            frame,s=align(q,frame);minimum=min(minimum,s)
        return frame,minimum

    def winding(self,center,radius,n,reference):
        vectors=[];overlaps=[]
        for theta in np.linspace(0,2*np.pi,n+1):
            vector,s=self.projected_vector(np.asarray(center)+radius*np.array([np.cos(theta),np.sin(theta)]),reference)
            vectors.append(vector);overlaps.append(s)
        result=phase_winding(np.array(vectors));result['min_chart_overlap']=min(overlaps)
        return result

    def pair(self,seeds,radius):
        nodes=[self.node(seed) for seed in seeds]
        a,b=[np.array(n['f']) for n in nodes]
        distance=float(np.linalg.norm(b-a));require(radius<distance/3,'loops not distinct')
        trials=[]
        for r,n,steps in [(radius,64,128),(radius,128,256),(radius/2,128,256)]:
            start=a+[r,0];end=b+[r,0];_,base=self.frame(start)
            endpoint,overlap=self.transport(start,end,base,steps)
            qa=self.winding(a,r,n,base);qb=self.winding(b,r,n,endpoint)
            trials.append(dict(radius=r,loop_points=n,transport_steps=steps,a=qa,b=qb,min_transport_overlap=overlap,label='SAME' if qa['charge']*qb['charge']>0 else 'OPPOSITE'))
        labels={t['label'] for t in trials};require(len(labels)==1,'label changes with mesh/radius')
        return dict(status='ACCEPT',nodes=nodes,separation=distance,trials=trials,label=trials[0]['label'],diagnostics=self.metrics,sampled_points=len(self.cache))
