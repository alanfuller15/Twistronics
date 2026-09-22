"""N8 follow-up using unchanged local-model and diagnostic implementations."""
from pathlib import Path
import sys,json,argparse,time,traceback,platform,hashlib
import numpy as np
import scipy
from scipy.linalg import eigh
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'r1_merger'))
from study import Local,P,BOX,C,D0,distinct,set_distance,sha,model
from refine import check_minimum
PLAN=json.loads((ROOT/'PLAN.json').read_text())

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=PLAN['engines'],required=True);ap.add_argument('--output',required=True);args=ap.parse_args();engine=args.engine;dest=ROOT/args.output
 if dest.exists():raise SystemExit('Refusing overwrite')
 source=[ROOT/'run.py',ROOT.parent/'r1_merger'/'study.py',ROOT.parent/'r1_merger'/'refine.py',ROOT.parent/'r1_merger'/'PLAN.json',ROOT.parent/'r1_merger'/'REFINEMENT_PLAN.json',ROOT.parent/'r1_merger'/'N6.json',ROOT.parent/'r1_events'/'track.py',ROOT.parent/'r1_events'/'PLAN.json',ROOT.parent/'r1_validation'/'validate.py',ROOT.parent/'r1_validation'/'PLAN.json',*(ROOT.parent/'r1_reproduction').glob('*.py'),ROOT.parent/'r1_reproduction'/'PLAN.json']
 report={'status':'RUNNING','N':PLAN['N'],'engine':engine,'plan_sha256':sha(ROOT/'PLAN.json'),'source_hashes':{str(p.relative_to(ROOT.parent)):sha(p) for p in source},'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'folds':[],'sweeps':{},'node_indices':[],'enclosing_indices':[],'minima':[],'warnings':[]}
 def save():dest.write_text(json.dumps(report,indent=2)+'\n')
 def warn(reason):report['warnings'].append(reason)
 start=time.time();save()
 try:
  local=Local(PLAN['N'],engine);report.update(dimension=local.m.dim,nG=local.m.nG,affine_checks=local.checks);save()
  parent=json.loads((ROOT.parent/'r1_merger'/'N6.json').read_text())['engines'][engine]
  old=next(x for x in parent['sweeps']['forward'] if x['D_meV']==40.)
  report['initial_attempts']=[local.root(r['f'],40.) for r in old['roots']];roots=distinct(report['initial_attempts']);report['initial_roots']=roots;save()
  if len(roots)!=2:raise RuntimeError('N8 initial pair not recovered')
  seeds=[r['f'] for r in roots];seed=np.r_[C,D0]
  for h in P['fold']['derivative_steps']:
   row=local.fold(seed,h);report['folds'].append(row);seed=np.r_[row['f'],row['D_meV']]
   if not row['criteria_pass']:warn(f'Fold criterion failed at h={h}')
   save();print('FOLD',engine,h,row['D_meV'],row['gap_meV'],row['criteria_pass'],flush=True)
  folds=report['folds'];Ds=[x['D_meV'] for x in folds];fs=[x['f'] for x in folds]
  report['fold_refinement']={'D_spread_meV':max(Ds)-min(Ds),'max_f_difference':max(float(np.linalg.norm(np.array(f)-fs[-1])) for f in fs)}
  if report['fold_refinement']['D_spread_meV']>P['fold']['D_spread_max_meV'] or report['fold_refinement']['max_f_difference']>P['fold']['f_spread_max']:warn('Fold derivative refinement disagreement')
  Dstar=folds[-1]['D_meV'];fstar=np.array(folds[-1]['f']);native=model(engine,PLAN['N'],Dstar);w=eigh(native.H(local.mon.k(fstar)),eigvals_only=True,subset_by_index=(local.lo,local.lo+5));fast=local.eig(fstar,Dstar)
  report['native_fold_check']={'D_meV':Dstar,'f':fstar.tolist(),'max_spectrum_error_meV':float(np.max(np.abs(w-fast))),'native_gap_meV':float(w[4]-w[3])};save()
  if report['native_fold_check']['max_spectrum_error_meV']>P['affine_spectrum_tolerance_meV'] or report['native_fold_check']['native_gap_meV']>P['fold']['gap_meV']:raise RuntimeError('Native fold spectrum check failed')
  stations=sorted(set(np.round(np.r_[np.arange(40,40.5001,.05),np.arange(40.25,40.4501,.01)],8)))
  for direction,Ds in [('forward',stations),('reverse',stations[::-1])]:
   rows=[];report['sweeps'][direction]=rows;carried=seeds
   for D in Ds:
    D=float(D);attempts=[local.root(f,D) for f in carried];roots=distinct(attempts);rows.append({'D_meV':D,'attempts':attempts,'roots':roots})
    if len(roots)==2:carried=[r['f'] for r in roots]
    elif len(roots)==1:warn(f'Only one root recovered in {direction} at D={D}')
    save();print('SWEEP',engine,direction,D,len(roots),flush=True)
  report['direction_comparisons']=[]
  for a,b in zip(report['sweeps']['forward'],report['sweeps']['reverse'][::-1]):
   assert a['D_meV']==b['D_meV'];distance=set_distance(a['roots'],b['roots']);report['direction_comparisons'].append({'D_meV':a['D_meV'],'counts':[len(a['roots']),len(b['roots'])],'coordinate_difference':distance})
   if distance is None or distance>P['coordinate_agreement']:warn(f'Direction disagreement at D={a["D_meV"]}')
  save()
  for cfg in PLAN['node_loops']:
   D=40. if cfg['D']=='40.0' else Dstar-.01;roots=distinct([local.root(f,D) for f in seeds])
   if len(roots)!=2:warn(f'No distinct pair for index station D={D}');continue
   sep=float(np.linalg.norm(np.array(roots[0]['f'])-roots[1]['f']))
   for fraction in PLAN['radius_fractions_of_pair_separation']:
    indices=[]
    for n in cfg['points']:
     loops=[local.index(r['f'],[fraction*sep]*2,D,n) for r in roots];report['node_indices'].append({'D_meV':D,'roots':roots,'separation':sep,'radius_fraction':fraction,'points':n,'loops':loops});indices.append([round(a['index']) for a in loops])
     if not all(a['sampling_checks_pass'] for a in loops) or sorted(indices[-1])!=[-1,1]:warn(f'Node index check failed D={D}, fraction={fraction}, n={n}')
     save();print('LOOP',engine,D,fraction,n,[a['index'] for a in loops],[a['max_phase_step'] for a in loops],flush=True)
    if indices[0]!=indices[1]:warn(f'Node index mesh disagreement D={D}, fraction={fraction}')
  for cfg in PLAN['enclosing_loops']:
   for n in cfg['points']:
    D=cfg['D'];row=local.index(P['indices']['enclosing_ellipse_center'],P['indices']['enclosing_ellipse_axes'],D,n);report['enclosing_indices'].append(row)
    if not row['sampling_checks_pass'] or round(row['index'])!=0:warn(f'Enclosing index check failed D={D}, n={n}')
    save();print('ENCLOSING',engine,D,n,row['index'],row['max_phase_step'],flush=True)
  for D in [Dstar+.01,Dstar+.05,40.5]:
   candidates=[local.root(f,D) for f in [C,*seeds]];checks=[check_minimum(local,a,D) for a in candidates];report['minima'].append({'D_meV':D,'candidate_method':'bounded component least squares; positive-gap outputs are not roots','candidates':candidates,'attempts':checks})
   if not all(a['criteria_pass'] for a in checks):warn(f'Stationary-minimum check failed D={D}')
   if any(a['accepted'] for a in candidates):warn(f'Unexpected accepted root at proposed post-fold minimum D={D}')
   if max(np.linalg.norm(np.array(a['f'])-checks[0]['f']) for a in checks)>P['coordinate_agreement']:warn(f'Minimum positions disagree D={D}')
   save();print('MINIMUM',engine,D,[a['gap_meV'] for a in checks],[a['gradient_norm'] for a in checks],[a['criteria_pass'] for a in checks],flush=True)
  report['all_evaluations']={'unique_points':len(local.cache),'minimum_anchor_overlap':local.min_overlap,'minimum_sampled_exterior_gap_meV':local.min_exterior}
  if local.min_overlap<P['minimum_anchor_overlap'] or local.min_exterior<P['indices']['sampled_exterior_gap_min_meV']:warn('Sampled subspace conditioning failure')
  report['status']='N8_LOCAL_DIAGNOSTICS_COMPLETE_WITH_UNRESOLVED_CHECKS' if report['warnings'] else 'N8_LOCAL_DIAGNOSTICS_PASS_NOT_CONVERGENCE_CERTIFICATE'
 except Exception:report['status']='UNRESOLVED';report['error']=traceback.format_exc();print(report['error'],flush=True)
 finally:report['seconds']=time.time()-start;save()
 return 1 if report['status']=='UNRESOLVED' else 0
if __name__=='__main__':raise SystemExit(main())
