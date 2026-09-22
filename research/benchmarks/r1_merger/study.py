"""Local upper-pair continuation, fold diagnostics and anchored-map indices.
Uses actual eigenpairs, not a fitted two-band surrogate. Saves failed searches.
"""
from pathlib import Path
import sys,json,hashlib,argparse,platform,time,traceback
import numpy as np
import scipy
from scipy.linalg import eigh
from scipy.optimize import least_squares,minimize,linear_sum_assignment
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'r1_events'))
from track import Solver,model
P=json.loads((ROOT/'PLAN.json').read_text())
BOX=np.array(P['box_fractional']);C=np.array(P['anchor_f']);D0=P['anchor_D_meV']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def jacobian(fun,x,h):
    x=np.asarray(x);return np.column_stack([(fun(x+np.eye(len(x))[i]*h)-fun(x-np.eye(len(x))[i]*h))/(2*h) for i in range(len(x))])
def hessian(fun,x,h):
    x=np.asarray(x);e=np.eye(2)*h;f0=fun(x);out=np.zeros((2,2))
    for i in range(2):out[i,i]=(fun(x+e[i])-2*f0+fun(x-e[i]))/h**2
    out[0,1]=out[1,0]=(fun(x+e[0]+e[1])-fun(x+e[0]-e[1])-fun(x-e[0]+e[1])+fun(x-e[0]-e[1]))/(4*h*h)
    return out
def fold_metrics(fun,f,D,h,dD):
    J=jacobian(lambda x:fun(x,D),f,h);u,s,vt=np.linalg.svd(J);left=u[:,-1];v=vt[-1]
    a=float(left@((fun(f,D+dD)-fun(f,D-dD))/(2*dD)))
    b=float(left@((fun(f+h*v,D)-2*fun(f,D)+fun(f-h*v,D))/h**2))
    return {'jacobian':J.tolist(),'singular_values':s.tolist(),'singular_value_ratio':float(s[-1]/s[0]),'left_null':left.tolist(),'momentum_null':v.tolist(),'parameter_coefficient':a,'curvature_coefficient':b,'separation_squared_slope':float(-8*a/b) if b else None,'roots_on_lower_D_side':bool(a*b>0)}
def phase_index(z):
    z=np.asarray(z);phase=np.angle(z[:,0]+1j*z[:,1]);steps=np.angle(np.exp(1j*(np.roll(phase,-1)-phase)))
    winding=float(sum(steps)/(2*np.pi));return winding,float(np.max(np.abs(steps)))

class Local:
 def __init__(self,N,engine):
    s=Solver(N,engine,D0);self.m=s.m;self.mon=s.mon;self.lo=s.lo;self.N=N;self.engine=engine
    self.hc=self.mon.hr(self.mon.k(C));self.A=[]
    for e in np.eye(2):
      dk=self.mon.k(C+e)-self.mon.k(C);self.A.append(dk[0]*self.mon.hx+dk[1]*self.mon.hy)
    ma,mb=model(engine,N,40.),model(engine,N,40.5);hd=(mb.H(self.mon.k(C))-ma.H(self.mon.k(C)))/.5
    hd=self.mon.U.conj().T@hd@self.mon.U
    if np.abs(hd.imag).max()>1e-9:raise RuntimeError('Nonreal D derivative')
    self.hD=hd.real;self.checks=[]
    for D,m in [(40.,ma),(40.5,mb)]:
      for f in [C,BOX[:,0],BOX[:,1]]:
        native=m.H(self.mon.k(f));direct=self.mon.U.conj().T@native@self.mon.U;res=float(np.abs(direct-self.H(f,D)).max())
        w=eigh(native,eigvals_only=True,subset_by_index=(self.lo,self.lo+5));v=self.eig(f,D)
        err=float(np.max(np.abs(w-v)));self.checks.append({'D':D,'f':f.tolist(),'matrix_error_meV':res,'spectrum_error_meV':err})
        if res>P['affine_matrix_tolerance_meV'] or err>P['affine_spectrum_tolerance_meV']:raise RuntimeError('Affine family check failed')
    _,v=self.eig(C,D0,True);self.anchor=v[:,3:5];self.cache={};self.min_overlap=1.;self.min_exterior=np.inf
 def H(self,f,D):return self.hc+(f[0]-C[0])*self.A[0]+(f[1]-C[1])*self.A[1]+(D-D0)*self.hD
 def eig(self,f,D,vectors=False):return eigh(self.H(f,D),subset_by_index=(self.lo,self.lo+5),eigvals_only=not vectors)
 def data(self,f,D):
    key=(*map(float,f),float(D))
    if key not in self.cache:
      w,v=self.eig(f,D,True);u,s,vt=np.linalg.svd(v[:,3:5].T@self.anchor);q=u@vt
      h=q.T@np.diag(w[3:5]-np.mean(w[3:5]))@q;r=np.array([h[0,0]-h[1,1],2*h[0,1]])
      gap=float(w[4]-w[3]);ext=float(min(w[3]-w[2],w[5]-w[4]));overlap=float(s.min())
      self.min_overlap=min(self.min_overlap,overlap);self.min_exterior=min(self.min_exterior,ext)
      self.cache[key]=(r,gap,ext,overlap)
    return self.cache[key]
 def fun(self,f,D):return self.data(f,D)[0]
 def root(self,seed,D):
    opt=least_squares(lambda f:self.fun(f,D),np.clip(seed,*BOX.T),bounds=BOX.T,xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=P['max_root_evaluations'])
    r,g,ext,ov=self.data(opt.x,D)
    return {'f':opt.x.tolist(),'seed':list(seed),'gap_meV':g,'sampled_exterior_gap_meV':ext,'anchor_overlap':ov,'accepted':bool(opt.success and g<P['root_gap_meV'] and ov>P['minimum_anchor_overlap']),'optimizer_success':bool(opt.success),'nfev':int(opt.nfev),'message':opt.message}
 def fold(self,seed,h):
    def fun(z):
      f=z[:2];D=z[2];r=self.fun(f,D);J=jacobian(lambda x:self.fun(x,D),f,h)
      return np.r_[r,np.linalg.det(J)/10000.]
    opt=least_squares(fun,seed,bounds=(np.r_[BOX[:,0],40.],np.r_[BOX[:,1],40.5]),jac='3-point',diff_step=1e-5,x_scale=[.01,.02,.25],xtol=1e-11,ftol=1e-11,gtol=1e-11,max_nfev=P['fold']['max_evaluations'])
    f,D=opt.x[:2],float(opt.x[2]);r,g,ext,ov=self.data(f,D);metrics=fold_metrics(self.fun,f,D,h,P['fold']['parameter_difference_meV']);T=P['fold']
    passed=bool(opt.success and g<T['gap_meV'] and metrics['singular_value_ratio']<T['singular_value_ratio_max'] and metrics['singular_values'][0]>T['large_singular_value_min'] and abs(metrics['parameter_coefficient'])>T['parameter_coefficient_abs_min'] and abs(metrics['curvature_coefficient'])>T['curvature_coefficient_abs_min'] and metrics['roots_on_lower_D_side'] and ov>P['minimum_anchor_overlap'] and ext>P['indices']['sampled_exterior_gap_min_meV'])
    return {'f':f.tolist(),'D_meV':D,'derivative_step':h,'gap_meV':g,'sampled_exterior_gap_meV':ext,'anchor_overlap':ov,'metrics':metrics,'optimizer_success':bool(opt.success),'message':opt.message,'nfev':int(opt.nfev),'criteria_pass':passed}
 def index(self,center,axes,D,n):
    data=[self.data(np.array(center)+np.array(axes)*[np.cos(t),np.sin(t)],D) for t in np.arange(n)*2*np.pi/n]
    z=np.array([a[0] for a in data]);w,step=phase_index(z);g=min(a[1] for a in data);ext=min(a[2] for a in data);ov=min(a[3] for a in data);T=P['indices']
    valid=bool(g>P['root_gap_meV'] and ext>T['sampled_exterior_gap_min_meV'] and ov>P['minimum_anchor_overlap'] and step<T['max_phase_step_radians'] and abs(w-round(w))<T['integer_tolerance'])
    return {'center':list(center),'axes':list(axes),'D_meV':D,'points':n,'index':w,'max_phase_step':step,'min_gap_meV':g,'min_sampled_exterior_gap_meV':ext,'min_anchor_overlap':ov,'sampling_checks_pass':valid,'components':z.tolist()}
 def minimum(self,seed,D):
    fun=lambda x:float(self.fun(x,D)@self.fun(x,D))
    opt=minimize(fun,seed,method='Nelder-Mead',bounds=BOX,options={'xatol':1e-11,'fatol':1e-18,'maxiter':P['post_event_minima']['max_iterations']})
    r,g,ext,ov=self.data(opt.x,D);H=hessian(fun,opt.x,P['post_event_minima']['Hessian_step_fractional']);ev=np.linalg.eigvalsh(H);T=P['post_event_minima']
    interior=bool(np.all(opt.x>BOX[:,0]+1e-4) and np.all(opt.x<BOX[:,1]-1e-4))
    ok=bool(opt.success and interior and g>T['positive_gap_min_meV'] and ev.min()>T['minimum_Hessian_eigenvalue'] and ov>P['minimum_anchor_overlap'])
    return {'D_meV':D,'seed':list(seed),'f':opt.x.tolist(),'gap_meV':g,'gap_squared_Hessian_eigenvalues':ev.tolist(),'interior':interior,'optimizer_success':bool(opt.success),'nfev':int(opt.nfev),'message':str(opt.message),'criteria_pass':ok}

def distinct(attempts):
    out=[]
    for x in sorted([a for a in attempts if a['accepted']],key=lambda a:a['gap_meV']):
      if all(np.linalg.norm(np.array(x['f'])-b['f'])>P['root_separation'] for b in out):out.append(x)
    return sorted(out,key=lambda a:a['f'][0])
def set_distance(a,b):
    if len(a)!=len(b):return None
    if not a:return 0.
    costs=np.array([[np.linalg.norm(np.array(x['f'])-y['f']) for y in b] for x in a]);i,j=linear_sum_assignment(costs);return float(max(costs[i,j]))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--N',type=int,choices=P['N_values'],required=True);ap.add_argument('--output',required=True);args=ap.parse_args();dest=ROOT/args.output;maps_path=dest.with_suffix('.npz')
 if dest.exists() or maps_path.exists():raise SystemExit('Refusing overwrite')
 sources=[ROOT/'study.py',ROOT.parent/'r1_events'/'track.py',ROOT.parent/'r1_events'/'PLAN.json',ROOT.parent/'r1_validation'/'validate.py',ROOT.parent/'r1_validation'/'PLAN.json',*(ROOT.parent/'r1_reproduction').glob('*.py'),ROOT.parent/'r1_reproduction'/'PLAN.json',ROOT.parent/'r1_events'/f'N{args.N}.json']
 report={'status':'RUNNING','N':args.N,'plan_sha256':sha(ROOT/'PLAN.json'),'source_hashes':{str(p.relative_to(ROOT.parent)):sha(p) for p in sources},'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'engines':{},'warnings':[]};maps={}
 def save():dest.write_text(json.dumps(report,indent=2)+'\n');np.savez_compressed(maps_path,**maps)
 def warn(engine,reason):report['warnings'].append({'engine':engine,'reason':reason})
 save()
 try:
  parent=json.loads((ROOT.parent/'r1_events'/f'N{args.N}.json').read_text())
  stations=sorted(set(np.round(np.r_[np.arange(40,40.5001,.05),np.arange(40.25,40.4501,.01)],8)))
  for engine in P['engines']:
    start=time.time();local=Local(args.N,engine);old=next(x for x in parent['stations'] if x['engine']==engine and x['D_meV']==40.)
    seeds=[a['f'] for a in old['gaps']['upper']['roots'] if np.all(np.array(a['f'])>BOX[:,0]) and np.all(np.array(a['f'])<BOX[:,1])]
    if len(seeds)!=2:raise RuntimeError('Parent local-pair selection failed')
    rec={'affine_checks':local.checks,'parent_seeds':seeds,'sweeps':{},'folds':[],'node_indices':[],'enclosing_indices':[],'post_event_minima':[]};report['engines'][engine]=rec;save()
    for direction,Ds in [('forward',stations),('reverse',stations[::-1])]:
      carried=seeds;rows=[];rec['sweeps'][direction]=rows
      for D in Ds:
        D=float(D);attempts=[local.root(f,D) for f in carried];roots=distinct(attempts)
        rows.append({'D_meV':D,'attempts':attempts,'roots':roots})
        if len(roots)==2:carried=[a['f'] for a in roots]
        elif len(roots)==1:warn(engine,f'Only one distinct root recovered in {direction} at D={D}')
        save();print('SWEEP',args.N,engine,direction,D,'roots',len(roots),'gaps',[a['gap_meV'] for a in attempts],flush=True)
    rec['direction_comparisons']=[]
    for a,b in zip(rec['sweeps']['forward'],rec['sweeps']['reverse'][::-1]):
      assert a['D_meV']==b['D_meV'];dist=set_distance(a['roots'],b['roots']);rec['direction_comparisons'].append({'D_meV':a['D_meV'],'counts':[len(a['roots']),len(b['roots'])],'coordinate_difference':dist})
      if dist is None or dist>P['coordinate_agreement']:warn(engine,f'Direction disagreement at D={a["D_meV"]}')
    seed=np.r_[C,D0]
    for h in P['fold']['derivative_steps']:
      fold=local.fold(seed,h);rec['folds'].append(fold);save();seed=np.r_[fold['f'],fold['D_meV']]
      if not fold['criteria_pass']:warn(engine,f'Fold criteria failed at derivative step {h}')
      print('FOLD',args.N,engine,h,fold['D_meV'],fold['gap_meV'],fold['criteria_pass'],flush=True)
    Ds=[a['D_meV'] for a in rec['folds']];fs=[a['f'] for a in rec['folds']]
    rec['fold_refinement']={'D_spread_meV':max(Ds)-min(Ds),'max_f_difference':max(float(np.linalg.norm(np.array(f)-fs[-1])) for f in fs)}
    if rec['fold_refinement']['D_spread_meV']>P['fold']['D_spread_max_meV'] or rec['fold_refinement']['max_f_difference']>P['fold']['f_spread_max']:warn(engine,'Fold derivative refinement disagreement')
    Dstar=rec['folds'][-1]['D_meV']
    for D in [40.,Dstar-.01]:
      roots=distinct([local.root(s,D) for s in seeds])
      if len(roots)!=2:warn(engine,f'Index station lacks a distinct accepted pair at D={D}');continue
      sep=float(np.linalg.norm(np.array(roots[0]['f'])-roots[1]['f']))
      for fraction in P['indices']['radius_fractions_of_pair_separation']:
       for n in P['indices']['loop_points']:
        loops=[local.index(r['f'],[fraction*sep]*2,D,n) for r in roots]
        rec['node_indices'].append({'D_meV':D,'roots':roots,'separation':sep,'radius_fraction':fraction,'points':n,'loops':loops})
        if not all(a['sampling_checks_pass'] for a in loops) or sorted(round(a['index']) for a in loops)!=[-1,1]:warn(engine,f'Opposite local indices not resolved at D={D}, radius fraction={fraction}, n={n}')
      save()
    for D in P['indices']['enclosing_D_meV']:
     for n in P['indices']['loop_points']:
      loop=local.index(P['indices']['enclosing_ellipse_center'],P['indices']['enclosing_ellipse_axes'],D,n);rec['enclosing_indices'].append(loop)
      if not loop['sampling_checks_pass'] or round(loop['index'])!=0:warn(engine,f'Enclosing index check failed at D={D}, n={n}')
    for D in [Dstar+.01,Dstar+.05,40.5]:
      records=[local.minimum(f,D) for f in [C,*seeds]];rec['post_event_minima'].append({'D_meV':D,'attempts':records})
      if not all(x['criteria_pass'] for x in records):warn(engine,f'Positive local minimum diagnostic failed at D={D}')
      if max(np.linalg.norm(np.array(x['f'])-records[0]['f']) for x in records)>P['coordinate_agreement']:warn(engine,f'Local minima disagree at D={D}')
      print('MINIMUM',args.N,engine,D,[a['gap_meV'] for a in records],flush=True);save()
    n=P['gap_maps']['points_per_axis']
    for D in P['gap_maps']['D_meV']:
      values=np.empty((n,n,3))
      for i,x in enumerate(np.linspace(*BOX[0],n)):
       for j,y in enumerate(np.linspace(*BOX[1],n)):
        r,g,ext,ov=local.data([x,y],D);values[i,j]=[g,ext,ov]
      key=f'{engine}_D{D:g}';maps[key]=values
      rec.setdefault('gap_maps',[]).append({'key':key,'minimum_sampled_gap_meV':float(values[:,:,0].min()),'minimum_sampled_exterior_gap_meV':float(values[:,:,1].min()),'minimum_sampled_anchor_overlap':float(values[:,:,2].min())});save()
    rec['all_evaluations']={'unique_points':len(local.cache),'minimum_anchor_overlap':local.min_overlap,'minimum_sampled_exterior_gap_meV':local.min_exterior}
    if local.min_overlap<P['minimum_anchor_overlap'] or local.min_exterior<P['indices']['sampled_exterior_gap_min_meV']:warn(engine,'Sampled subspace conditioning failed')
    rec['seconds']=time.time()-start;save();print('COMPLETE',args.N,engine,'seconds',rec['seconds'],flush=True)
  report['status']='LOCAL_MERGER_DIAGNOSTICS_COMPLETE_WITH_UNRESOLVED_CHECKS' if report['warnings'] else 'LOCAL_MERGER_DIAGNOSTICS_CONSISTENT_NOT_CERTIFICATE'
 except Exception:report['status']='UNRESOLVED';report['error']=traceback.format_exc();print(report['error'],flush=True)
 finally:save()
 return 1 if report['status']=='UNRESOLVED' else 0
if __name__=='__main__':raise SystemExit(main())
