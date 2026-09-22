"""Bounded dense recheck of partner candidates; sparse mode is not used here."""
import json,sys,time,traceback,platform,gc,zipfile
import numpy as np
import scipy
from scipy.optimize import brentq
from sparse_inputs import ROOT,PLAN,binding,sha
sys.path.insert(0,str(ROOT.parent/'joint_mapping_guarded'))
import jm_model as model

def main():
 dest=ROOT/'CANDIDATES.json'
 if dest.exists():raise FileExistsError('refusing overwrite of retained candidates')
 spec=PLAN['candidate_check'];basis=json.loads((ROOT/'BASIS.json').read_text())
 for n,h in basis['source_hashes'].items():assert sha(ROOT/n)==h,n
 with zipfile.ZipFile(ROOT/'partner_v071p.zip') as z:provided=json.loads(z.read('locate_event_results.json'))
 source=binding(['check_candidates.py','BASIS.json']);source.update({'../'+n:h for n,h in model.sources().items()})
 out={'status':'RUNNING','source_hashes':source,'scope':PLAN['scope'],'rows':[],'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'blas_threads':1}}
 start=time.perf_counter()
 def save():
  out['seconds']=time.perf_counter()-start;dest.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
 save()
 for N in spec['N']:
  seed=next(r for r in provided if r['N']==(12 if N==12 else 10));seeds={'flat':seed['flat'],'node':seed['node'],'gap':'upper'}
  x=dict(spec['state'],D=seed['D']);indices=basis['sets'][str(N)]['indices']
  for eng in spec['engines']:
   row={'N':N,'engine':eng,'seed_record_N':seed['N'],'basis_vectors':len(indices),'dimension':4*len(indices),'measurements':[],'pass':False,'event':None};out['rows'].append(row)
   try:
    cfg=model.config({'N':N,'engine':eng,'indices':indices,'root_radius':spec['root_radius'],'gap_tol':spec['gap_tolerance_meV'],'matrix_tol':spec['matrix_tolerance_meV'],'segment_margin':spec['t_margin']})
    family=model.Family(x,cfg);row['config']=cfg;cache={}
    def measure(d):
     d=float(d)
     if d in cache:return row['measurements'][cache[d]]['result']
     m=model.measure(dict(x,D=d),seeds,cfg,family);cache[d]=len(row['measurements']);row['measurements'].append({'D':d,'result':m})
     if not m['ok'] or not spec['t_margin']<m['t']<1-spec['t_margin']:raise ValueError('rejected root, native or segment check')
     return m
    center=measure(x['D']);row['supplied_D_offset']=center['offset']
    a=x['D']-spec['D_halfwidth_meV'];b=x['D']+spec['D_halfwidth_meV'];row['bracket']=[a,b]
    if measure(a)['offset']*measure(b)['offset']>=0:raise ValueError('no sign bracket within frozen range')
    d=float(brentq(lambda v:measure(v)['offset'],a,b,xtol=spec['D_xtol_meV'],maxiter=spec['scalar_max_iterations']))
    final=measure(d);row['event']={'D':d,'measurement_index':cache[d],'offset':final['offset'],'t':final['t'],'flat':final['flat'],'node':final['node']}
    row['pass']=bool(abs(final['offset'])<=spec['offset_tolerance']);row['reason']='sampled_dense_event_pass' if row['pass'] else 'offset_rejected'
    del family;gc.collect()
   except Exception:row.update(reason='retained_exception',error=traceback.format_exc())
   row['logged_eigensolves']=sum(m['result']['cost'] for m in row['measurements']);save()
   print('CANDIDATE',N,eng,'pass',row['pass'],'D',row['event']['D'] if row['event'] else None,'seconds',round(out['seconds'],1),flush=True)
 out['status']='SAMPLED_TWO_ENGINE_FIVE_CUTOFF_EVENTS_PASS' if all(r['pass'] for r in out['rows']) else 'PARTIAL_CANDIDATE_RESULTS_RETAINED';save();print(out['status'],flush=True)
if __name__=='__main__':main()
