"""Targeted local-root followup; no global braid certificate."""
import json,traceback
import numpy as np
from run import ROOT, model, digest, PLAN
from bm_strain import segment_geometry
P=json.loads((ROOT/'CROSSING_PLAN.json').read_text())
dest=ROOT/'CROSSING.json'
if dest.exists():raise SystemExit('Refusing to overwrite')
r={'status':'RUNNING','plan_sha256':digest(ROOT/'CROSSING_PLAN.json'),'endpoint_plan_sha256':digest(ROOT/'PLAN.json'),'source_sha256':{p.name:digest(p) for p in ROOT.glob('*.py')},'rows':[]}
def save():dest.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for N in P['N_values']:
  for engine in P['engines']:
   seed=np.array(P['upper_seed']);signs=[]
   for D in P['D_values_meV']:
    m=model(engine,N,D);k=m.frac_to_k if engine=='bm' else m.k
    bands=(lambda f:m.bands_near_zero(k(f),2)) if engine=='bm' else (lambda f:m.bands(k(f),2))
    flat=lambda f:(lambda w:w[2]-w[1])(bands(f))
    upper=lambda f:(lambda w:w[3]-w[2])(bands(f))
    pp=[m.refine(np.array(s),flat) for s in PLAN['flat_seeds']];q,g=m.refine(seed,upper)
    if max([g]+[x[1] for x in pp])>1e-6:raise RuntimeError('root residual failed')
    if np.linalg.norm(q-seed)>.05:raise RuntimeError('local continuation displacement exceeded 0.05')
    seed=q;t,off,L=segment_geometry(pp[0][0],pp[1][0],q)
    row={'engine':engine,'N':N,'D_meV':D,'upper':q.tolist(),'upper_gap_meV':float(g),'flat':[x[0].tolist() for x in pp],'flat_gaps_meV':[float(x[1]) for x in pp],'t':t,'offset':off};r['rows'].append(row);save();print(row,flush=True)
    if not 0<t<1:raise RuntimeError('outside segment')
    signs.append(off)
   if not signs[0]>0>signs[1]:raise RuntimeError('original D38-D39 crossing bracket not reproduced')
 r['status']='LOCAL_CROSSING_BRACKET_REPRODUCED_NOT_BRAID_ACCEPTANCE'
except Exception:r['status']='UNRESOLVED';r['error']=traceback.format_exc();print(r['error'],flush=True)
save()
raise SystemExit(0 if r['status'].startswith('LOCAL') else 1)
