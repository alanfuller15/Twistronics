"""Retained geometry/isolation design survey; no charge labels."""
import sys,json
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'r1_three_band'))
from frame import Family,polar,sha

def geometry(s,r=.003):
    p,q,u=[np.array(x['f']) for x in s['roots']]
    d=q-p;e=d/np.linalg.norm(d);normal=np.array([-e[1],e[0]])
    base=p+.55*d;kink=u-.006*normal;anchor=q-r*e
    return base,kink,anchor,q,normal

def main():
    out={'status':'DESIGN_SURVEY_NO_CHARGE_LABELS','source_sha256':sha(Path(__file__)),'rows':[],'sources':{}}
    for engine in ['bm','ref']:
        fam=Family(engine);parent=ROOT.parent/'r1_holonomy'/(engine.upper()+'.json')
        stations=json.loads(parent.read_text())['tracks']['16']['stations'];out['sources'][str(parent.relative_to(ROOT.parent))]=sha(parent)
        base=geometry(stations[0])[0]
        def get(f,D):
            w,F=eigh(fam.H([*f,D]),subset_by_index=(fam.lo-1,fam.lo+3))
            return w,F[:,1:4]
        B=get(base,38.)[1]
        for station in stations[::8]:
            D=station['D_meV'];samples=[]
            for radius in [.003,.0015]:
                base,kink,anchor,q,n=geometry(station,radius)
                pts=list(np.linspace(base,kink,25))+list(np.linspace(kink,anchor,25))
                theta=np.arctan2(*(anchor-q)[::-1])
                pts += [q+radius*np.array([np.cos(t),np.sin(t)]) for t in np.linspace(theta,theta+2*np.pi,33)]
                for f in pts:
                    w,F=get(f,D);smin=float(np.linalg.svd(B.T@F,compute_uv=False).min())
                    samples.append({'f':f.tolist(),'radius':radius,'eigenvalues_meV':w.tolist(),'gaps_meV':np.diff(w).tolist(),'anchor_smin':smin})
            row={'engine':engine,'D_meV':D,'base':base.tolist(),'kink':kink.tolist(),'samples':samples,
                 'minimum_all_gap_meV':min(min(x['gaps_meV']) for x in samples),'minimum_anchor_smin':min(x['anchor_smin'] for x in samples)}
            out['rows'].append(row);print(engine,D,row['minimum_all_gap_meV'],row['minimum_anchor_smin'],flush=True)
    (ROOT/'SURVEY.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__':main()
