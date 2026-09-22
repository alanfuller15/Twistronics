"""Analytic adjacent/internal-node controls for the actual contour sampler."""
import json
import numpy as np
from scipy.linalg import eigh
from measure import ROOT,P,sha,closed_loop

class Toy:
    def __init__(self, internal=False):
        self.internal=internal
        self.cache={}
    def H(self,v):
        x,z=v[:2]
        if self.internal:
            return np.array([[-20,0,0,0],[0,x,z,0],[0,z,-x,0],[0,0,0,20]],float)
        return np.array([[-20,0,0,0],[0,-10,0,0],[0,0,x,z],[0,0,z,-x]],float)
    def data(self,v):
        key=tuple(v)
        if key not in self.cache:
            w,F=eigh(self.H(v))
            self.cache[key]=(F[:,1:3],float(min(w[1]-w[0],w[3]-w[2])))
        return self.cache[key]
    def edge_norm(self,a,b):
        return float(np.abs(eigh(self.H(b)-self.H(a),eigvals_only=True)).max())

def main():
    dest=ROOT/'CONTROLS.json'
    if dest.exists():raise SystemExit('Refusing overwrite')
    square=np.array([[-1,-1,0],[1,-1,0],[1,1,0],[-1,1,0],[-1,-1,0]],float)
    touch=np.array([[-1,0,0],[1,0,0],[1,2,0],[-1,2,0],[-1,0,0]],float)
    cases=[('adjacent_enclosed',Toy(),square,-1),('adjacent_excluded',Toy(),square+[3,0,0],1),
           ('internal_enclosed',Toy(True),square,1),('boundary_degeneracy',Toy(),touch,None)]
    out={'plan_sha256':sha(ROOT/'PLAN.json'),'source_hashes':{p.name:sha(p) for p in [ROOT/'controls.py',ROOT/'measure.py']},'cases':[]}
    for name,family,vertices,expected in cases:
        for cfg in P['mesh_levels']:
            r=closed_loop(family,vertices,cfg)
            passed=(r['accepted_sign']==expected and (not r['diagnostics_pass'] if expected is None else r['diagnostics_pass']))
            if expected is None:passed=passed and not all(e['pass'] for e in r['edges'])
            out['cases'].append({'name':name,'expected':expected,'control_pass':bool(passed),'result':r})
            print(name,cfg['name'],'sign',r['accepted_sign'],'control_pass',passed,flush=True)
    out['all_controls_pass']=all(r['control_pass'] for r in out['cases'])
    dest.write_text(json.dumps(out,indent=2)+'\n')
    return 0 if out['all_controls_pass'] else 1

if __name__=='__main__':raise SystemExit(main())
