"""Analytic checks of carried signs and chronological conjugation."""
import json
import numpy as np
from scipy.linalg import eigh
from transport import ROOT,PLAN,T,Chart3,route,join,align,charge,edge,multiply,inverse,sha

class Toy:
    lo=1
    def __init__(self):
        self.h0=np.diag([-10.,0,0,-2,10.]);self.A=[np.diag([0.,1,0,1,0]),np.zeros((5,5))]
        self.A[1][1,2]=self.A[1][2,1]=self.A[1][2,3]=self.A[1][3,2]=1.
        self.A.append(-self.A[1])
    def H(self,v):return self.h0+sum(v[j]*self.A[j] for j in range(3))
    def edge_norm(self,a,b):return float(np.abs(eigh(self.H(b)-self.H(a),eigvals_only=True)).max())

class SignChart(Chart3):
    def data(self,v):
        d=super().data(v);m=int(np.floor(float(v[2])*2+1e-8));s=np.array([(-1.)**m,1.,(-1.)**m])
        return dict(d,Q=d['Q']*s)

def toyloop(chart,D,x,cfg):
    base=np.array([1.,.5+D,D]);ring=[np.array([x+.2*np.cos(t),D+.2*np.sin(t),D]) for t in np.linspace(0,2*np.pi,cfg['polygon_edges']+1)]
    ring[-1]=ring[0].copy()
    return route(chart,[base,*ring,base],cfg)

def main():
    parent=json.loads((ROOT.parent/'r1_three_band'/'CONTROLS.json').read_text())
    assert parent['all_controls_pass'] and len(parent['controls'])==18
    assert all(sha(ROOT.parent/'r1_three_band'/n)==h for n,h in parent['source_hashes'].items())
    out={'plan_sha256':sha(ROOT/'PLAN.json'),'sources':{n:sha(ROOT/n) for n in ['controls.py','transport.py']},
         'parent_controls_sha256':sha(ROOT.parent/'r1_three_band'/'CONTROLS.json'),'parent_control_count':18,'rows':[]}
    for cfg in PLAN['mesh_levels']:
        for cls in [Chart3,SignChart]:
            chart=cls(Toy(),[1.,.5,0.]);seed=None;last=None;records=[];labels=[]
            for D in [0.,.5,1.]:
                base=[1.,.5+D,D]
                if last is None:seed=align([chart.data(base)])[0]
                else:
                    er,points=edge(chart,last,base,cfg);assert er['pass'];seed=align(points,seed)[-1]
                r,points=toyloop(chart,D,2.,cfg);q,path=charge(points,seed)
                labels.append(q['nearest_label']);records.append({'D':D,'path_pass':r['pass'],'charge':q});last=base
            ok=len(set(labels))==1 and all(r['path_pass'] and r['charge']['valid'] and r['charge']['conjugacy_class']=='+-k' for r in records)
            out['rows'].append({'name':cls.__name__+'_moving_node_'+cfg['name'],'records':records,'pass':bool(ok)})
        chart=Chart3(Toy(),[1.,.5,0.]);seed=align([chart.data([1.,.5,0.])])[0]
        ar,a=toyloop(chart,0.,2.,cfg);br,b=toyloop(chart,0.,0.,cfg)
        qa,_=charge(a,seed);qb,_=charge(b,seed);qcon,_=charge(join(b,a,list(reversed(b))),seed)
        expected=multiply(multiply(qb['quaternion'],qa['quaternion']),inverse(qb['quaternion']))
        error=float(np.max(np.abs(expected-qcon['quaternion'])))
        flip=float(np.max(np.abs(np.array(qa['quaternion'])+qcon['quaternion'])))
        ok=ar['pass'] and br['pass'] and qa['valid'] and qb['valid'] and qcon['valid'] and max(error,flip)<T['cross_check_error']
        out['rows'].append({'name':'direct_conjugation_'+cfg['name'],'A':qa,'B':qb,'BAB_inverse':qcon,'product_error':error,'sign_flip_error':flip,'pass':bool(ok)})
        rejected,points=edge(chart,[-.2,0.,0.],[.2,0.,0.],cfg,2)
        out['rows'].append({'name':'degenerate_transport_rejected_'+cfg['name'],'edge':rejected,'pass':not rejected['pass']})
    out['all_controls_pass']=all(r['pass'] for r in out['rows'])
    (ROOT/'CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
    for r in out['rows']:print(r['name'],r['pass'])
    return 0 if out['all_controls_pass'] else 1

if __name__=='__main__':raise SystemExit(main())
