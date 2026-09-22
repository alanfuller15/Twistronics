"""Preserve baseline warnings; add declared denser-loop and gradient checks."""
from pathlib import Path
import json,argparse,traceback
import numpy as np
from scipy.optimize import least_squares
from study import ROOT,P,BOX,Local,jacobian,sha
RP=json.loads((ROOT/'REFINEMENT_PLAN.json').read_text())

def gap_gradient(local,f,D):
    w,v=local.eig(f,D,True)
    if w[4]-w[3]<1e-5:raise RuntimeError('Gap derivative requested too close to a crossing')
    return np.array([v[:,4]@A@v[:,4]-v[:,3]@A@v[:,3] for A in local.A])
def check_minimum(local,candidate,D):
    seed=np.array(candidate['f']);fun=lambda f:gap_gradient(local,f,D)
    J=lambda f:jacobian(fun,f,RP['gradient_solve_J_step'])
    initial=fun(seed)
    opt=least_squares(lambda f:fun(f)/100.,seed,jac=lambda f:J(f)/100.,bounds=BOX.T,xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=RP['max_gradient_solve_evaluations'])
    f=opt.x;grad=fun(f);r,g,ext,ov=local.data(f,D);Hs=[jacobian(fun,f,h) for h in RP['Hessian_steps']]
    asym=[float(np.linalg.norm(H-H.T)/np.linalg.norm(H)) for H in Hs];evs=[np.linalg.eigvalsh((H+H.T)/2) for H in Hs]
    rel=float(np.linalg.norm(Hs[0]-Hs[1])/np.linalg.norm(Hs[1]));disp=float(np.linalg.norm(f-seed));norm=float(np.linalg.norm(grad));interior=bool(np.all(f>BOX[:,0]+1e-4) and np.all(f<BOX[:,1]-1e-4))
    ok=bool(opt.success and norm<RP['gradient_norm_max_meV_per_fractional'] and min(ev.min() for ev in evs)>RP['Hessian_min_eigenvalue'] and rel<RP['Hessian_relative_refinement_max'] and max(asym)<RP['Hessian_relative_asymmetry_max'] and disp<RP['candidate_displacement_max'] and g>RP['positive_gap_min_meV'] and interior and ov>P['minimum_anchor_overlap'] and ext>P['indices']['sampled_exterior_gap_min_meV'])
    return {'D_meV':D,'original_candidate':candidate,'initial_gradient_norm':float(np.linalg.norm(initial)),'f':f.tolist(),'gap_meV':g,'gradient':grad.tolist(),'gradient_norm':norm,'gap_Hessian_eigenvalues':[v.tolist() for v in evs],'Hessian_relative_refinement':rel,'Hessian_relative_asymmetry':asym,'candidate_displacement':disp,'anchor_overlap':ov,'sampled_exterior_gap_meV':ext,'optimizer_success':bool(opt.success),'message':opt.message,'nfev':int(opt.nfev),'criteria_pass':ok}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--N',required=True,type=int,choices=P['N_values']);ap.add_argument('--output',required=True);args=ap.parse_args();dest=ROOT/args.output
 if dest.exists():raise SystemExit('Refusing overwrite')
 parentpath=ROOT/f'N{args.N}.json';parent=json.loads(parentpath.read_text())
 if not parent['status'].startswith('LOCAL_MERGER_DIAGNOSTICS'):raise SystemExit('Parent run incomplete')
 report={'status':'RUNNING','N':args.N,'parent_sha256':sha(parentpath),'plan_sha256':sha(ROOT/'REFINEMENT_PLAN.json'),'source_hashes':{p.name:sha(p) for p in [ROOT/'study.py',ROOT/'refine.py',ROOT/'PLAN.json']},'engines':{},'warnings':[]}
 def save():dest.write_text(json.dumps(report,indent=2)+'\n')
 save()
 try:
  for engine,old in parent['engines'].items():
    local=Local(args.N,engine);rec={'affine_checks':local.checks,'node_indices':[],'enclosing_indices':[],'minima':[]};report['engines'][engine]=rec
    for row in old['node_indices']:
      if row['D_meV']==40. or row['points']!=128:continue
      indices=[]
      for n in RP['loop_points']:
        loops=[local.index(a['center'],a['axes'],a['D_meV'],n) for a in row['loops']]
        rec['node_indices'].append({'D_meV':row['D_meV'],'radius_fraction':row['radius_fraction'],'points':n,'loops':loops});indices.append([round(a['index']) for a in loops])
        if not all(a['sampling_checks_pass'] for a in loops) or sorted(indices[-1])!=[-1,1]:report['warnings'].append(f'{engine}: refined local indices failed, radius fraction {row["radius_fraction"]}, n={n}')
        print('LOOP',args.N,engine,row['radius_fraction'],n,[a['index'] for a in loops],[a['max_phase_step'] for a in loops],flush=True);save()
      if indices[0]!=indices[1]:report['warnings'].append(f'{engine}: refined local indices disagree across meshes')
    indices=[]
    for n in RP['loop_points']:
      loop=local.index(P['indices']['enclosing_ellipse_center'],P['indices']['enclosing_ellipse_axes'],40.,n);rec['enclosing_indices'].append(loop);indices.append(round(loop['index']))
      if not loop['sampling_checks_pass'] or indices[-1]!=0:report['warnings'].append(f'{engine}: enclosing index not resolved at n={n}')
      save()
    if indices[0]!=indices[1]:report['warnings'].append(f'{engine}: enclosing index mesh disagreement')
    for row in old['post_event_minima']:
      attempts=[check_minimum(local,a,row['D_meV']) for a in row['attempts']];rec['minima'].append({'D_meV':row['D_meV'],'attempts':attempts})
      if not all(a['criteria_pass'] for a in attempts):report['warnings'].append(f'{engine}: direct stationary minimum check failed at D={row["D_meV"]}')
      print('GRADIENT',args.N,engine,row['D_meV'],[a['gradient_norm'] for a in attempts],[a['criteria_pass'] for a in attempts],flush=True);save()
    rec['all_evaluations']={'minimum_anchor_overlap':local.min_overlap,'minimum_sampled_exterior_gap_meV':local.min_exterior};save()
  report['status']='TARGETED_REFINEMENT_COMPLETE_WITH_UNRESOLVED_CHECKS' if report['warnings'] else 'TARGETED_REFINEMENT_DIAGNOSTICS_PASS_NOT_CERTIFICATE'
 except Exception:report['status']='UNRESOLVED';report['error']=traceback.format_exc();print(report['error'],flush=True)
 finally:save()
 return 1 if report['status']=='UNRESOLVED' else 0
if __name__=='__main__':raise SystemExit(main())
