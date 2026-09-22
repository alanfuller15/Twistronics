"""Design survey retained separately; no frame-charge labels are computed here."""
import sys,json
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'r1_holonomy'))
from measure import Family,sha

def main():
    out={'purpose':'DESIGN_SURVEY_NOT_CHARGE_ACCEPTANCE','rows':[],'sources':{}}
    for engine in ['bm','ref']:
        fam=Family(engine)
        parent=ROOT.parent/'r1_holonomy'/(engine.upper()+'.json')
        out['sources'][str(parent.relative_to(ROOT.parent))]=sha(parent)
        tracks=json.loads(parent.read_text())['tracks']['16']['stations']
        for s in [tracks[0],tracks[-1]]:
            D=s['D_meV'];q=np.array(s['roots'][1]['f']);u=np.array(s['roots'][2]['f'])
            base=(q+u)/2+[0,.012]
            def get(f):
                w,F=eigh(fam.H([*f,D]),subset_by_index=(fam.lo-1,fam.lo+3))
                return F[:,1:4],float(min(w[1]-w[0],w[4]-w[3])),np.diff(w[1:4]).tolist()
            B=get(base)[0]
            points=[base]
            for c in [q,u]:
                points.extend(np.linspace(base,c+[.003,0],17))
                points.extend(c+.003*np.array([np.cos(t),np.sin(t)]) for t in np.linspace(0,2*np.pi,33))
                points.extend(c+.003*np.array([x,y]) for x in np.linspace(-1,1,7) for y in np.linspace(-1,1,7) if x*x+y*y<=1)
            samples=[]
            for f in points:
                F,g,inner=get(f)
                samples.append({'f':list(f),'exterior_gap_meV':g,'internal_gaps_meV':inner,'anchor_smin':float(np.linalg.svd(B.T@F,compute_uv=False).min())})
            row={'engine':engine,'D_meV':D,'base_f':base.tolist(),'flat_q':q.tolist(),'upper':u.tolist(),'samples':samples,
                 'minimum_exterior_gap_meV':min(x['exterior_gap_meV'] for x in samples),'minimum_anchor_smin':min(x['anchor_smin'] for x in samples)}
            out['rows'].append(row)
            print(engine,D,row['minimum_exterior_gap_meV'],row['minimum_anchor_smin'],flush=True)
    out['source_sha256']=sha(Path(__file__))
    (ROOT/'FEASIBILITY.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__':main()
