"""Known Spin(3) lifts plus the same guarded paths on an affine 5x5 model."""
import json
import numpy as np
from scipy.linalg import eigh
from scipy.spatial.transform import Rotation
from frame import ROOT,P,T,sha,Chart,rectangle,loop,edge,lift,words

class Toy:
    lo=1
    def __init__(self):
        self.h0=np.diag([-10.,0,0,-2,10.])
        self.A=[np.diag([0.,1,0,1,0]),np.zeros((5,5)),np.zeros((5,5))]
        self.A[1][1,2]=self.A[1][2,1]=self.A[1][2,3]=self.A[1][3,2]=1.
    def H(self,v):return self.h0+v[0]*self.A[0]+v[1]*self.A[1]
    def edge_norm(self,a,b):return float(np.abs(eigh(self.H(b)-self.H(a),eigvals_only=True)).max())

def main():
    out={'plan_sha256':sha(ROOT/'PLAN.json'),'source_hashes':{n:sha(ROOT/n) for n in ['frame.py','controls.py']},'controls':[]}
    for n in [64,128]:
        for axis,angle,expect in [(0,0,'+1'),(0,np.pi,'-i'),(1,np.pi,'-j'),(2,np.pi,'-k'),(2,2*np.pi,'-1'),(2,4*np.pi,'+1')]:
            vectors=np.zeros((n+1,3));vectors[:,axis]=np.linspace(0,angle,n+1)
            raw=Rotation.from_rotvec(vectors).as_matrix()
            result,_=lift(raw)
            out['controls'].append({'name':f'known_rotation_axis{axis}_angle{angle}_n{n}','expected':expect,'result':result,'pass':result['valid'] and result['nearest_label']==expect})
    for cfg in P['mesh_levels']:
        chart=Chart(Toy(),0.,[1.,.5])
        region=rectangle(chart,[[-.2,-.2],[2.2,.5]],cfg['region_cells_per_axis'])
        A,a,_=loop(chart,[2.,0.],.2,cfg);B,b,_=loop(chart,[0.,0.],.2,cfg)
        result,_=words(a,b)
        expected=P['hypotheses']
        ok=(region['pass'] and A['diagnostics_pass'] and B['diagnostics_pass'] and all(x['valid'] for x in result.values()) and
            result['A']['conjugacy_class']==expected['A_class'] and result['B']['conjugacy_class']==expected['B_class'] and
            result['AB']['conjugacy_class']==expected['AB_class'] and result['BA']['conjugacy_class']==expected['BA_class'] and result['commutator']['nearest_label']=='-1')
        out['controls'].append({'name':'affine_adjacent_nodes_'+cfg['name'],'region':region,'A':A,'B':B,'words':result,'pass':bool(ok)})
        crossing,_=edge(chart,[-.2,0.],[.2,0.],cfg,2)
        out['controls'].append({'name':'internal_degeneracy_rejection_'+cfg['name'],'edge':crossing,'pass':not crossing['pass']})
        bad=Chart(Toy(),0.,[1.,.5],B=np.eye(5)[:,[0,2,3]])
        rejected,_=edge(bad,[.5,.5],[1.,.5],cfg,2)
        out['controls'].append({'name':'rank_deficient_anchor_rejection_'+cfg['name'],'edge':rejected,'pass':not rejected['pass']})
    out['all_controls_pass']=all(c['pass'] for c in out['controls'])
    (ROOT/'CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
    for row in out['controls']:print(row['name'],row['pass'])
    return 0 if out['all_controls_pass'] else 1

if __name__=='__main__':raise SystemExit(main())
