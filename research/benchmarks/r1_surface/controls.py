"""Controls include a degeneracy hidden strictly inside a gapped boundary."""
import json
import numpy as np
from surface import ROOT,PLAN,T,cover,point,corners,operator_norms,Spectrum,summaries,sha
class Toy:
    lo=1
    def __init__(self):
        self.h0=np.diag([-10.,0.,0.,5.,10.]);self.A=[np.zeros((5,5)) for _ in range(3)]
        self.A[0][1,1]=1;self.A[0][2,2]=-1
        self.A[1][1,2]=self.A[1][2,1]=1
        self.A[2]=-self.A[1]
    def H(self,v):return self.h0+sum(v[j]*self.A[j] for j in range(3))
def exact(v):
    r=np.hypot(v[0],v[1]-v[2]);return np.sort([-10.,-r,r,5.,10.])
def main():
    toy=Toy();norms=operator_norms(toy);spectrum=Spectrum(toy);out=[]
    patches={
      'center_hidden_node':np.array([[[-1,-1,0],[1,-1,0]],[[-1,1,0],[1,1,0]]],float),
      'offcenter_hidden_node':np.array([[[-.75,-1.25,0],[1.25,-1.25,0]],[[-.75,.75,0],[1.25,.75,0]]],float),
      'gapped_affine':np.array([[[.2,1,0],[1,1,.1]],[[.2,1.5,.2],[1,1.5,.3]]],float),
      'gapped_bilinear':np.array([[[-1,1.5,0],[1,1.5,.2]],[[-1,1.5,.2],[1,2.5,-.3]]],float)}
    for name,c in patches.items():
        rows=cover(c,spectrum,norms);s=summaries(rows)
        boundary=min(np.diff(exact(point(c,u,t))).min() for x in np.linspace(0,1,101) for u,t in [(x,0),(x,1),(0,x),(1,x)])
        violation=0.;spectrum_error=0.
        for row in rows[rows[:,8]!=0]:
            for u in np.linspace(row[0],row[1],5):
                for t in np.linspace(row[2],row[3],5):
                    w=exact(point(c,u,t));violation=max(violation,float(np.max(row[18:22]-np.diff(w))))
            spectrum_error=max(spectrum_error,float(np.max(np.abs(row[12:17]-exact(row[9:12])))))
        expected='hidden' not in name
        ok=s['pass']==expected and boundary>T['gap_margin_meV'] and violation<1e-12 and spectrum_error<1e-12
        if not expected:ok=ok and np.any(rows[:,8]==-2)
        out.append({'name':name,'summary':s,'boundary_minimum_gap_meV':float(boundary),'maximum_bound_violation_meV':violation,'spectrum_error_meV':spectrum_error,'pass':bool(ok)})
    c=patches['gapped_bilinear'];a=cover(c,spectrum,norms);sa=summaries(a)
    for axis in [0,1]:
        b=cover(np.flip(c,axis),spectrum,norms);sb=summaries(b)
        out.append({'name':f'reverse_parameter_{axis}','summary':sb,'pass':bool(sb['pass'] and abs(sa['minimum_lower_meV']-sb['minimum_lower_meV'])<1e-12 and sb['leaves']==sa['leaves'])})
    fail=cover(c,spectrum,norms,dict(T,maximum_depth=0));out.append({'name':'unresolved_budget_retained','summary':summaries(fail),'pass':bool(not summaries(fail)['pass'] and fail[0,8]==-3)})
    out={'plan_sha256':sha(ROOT/'PLAN.json'),'source_hashes':{n:sha(ROOT/n) for n in ['surface.py','controls.py']},'controls':out,'all_controls_pass':all(r['pass'] for r in out)}
    (ROOT/'CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
    for r in out['controls']:print(r['name'],r['pass'])
    return 0 if out['all_controls_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
