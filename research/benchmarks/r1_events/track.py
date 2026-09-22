"""Bounded adjacent-node inventory and sampled continuation. Preserves search failures.
Uses unchanged sibling engines and the previously checked affine frame constructor.
No periodic relabelling or exhaustive root count is assumed.
"""
from pathlib import Path
import sys,json,time,traceback,hashlib,argparse,platform
import numpy as np
import scipy
from scipy.linalg import eigh
from scipy.ndimage import minimum_filter
from scipy.optimize import least_squares,linear_sum_assignment
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'r1_validation'))
from validate import Monitor,model
from bm_strain import segment_geometry
P=json.loads((ROOT/'PLAN.json').read_text());GAP_INDEX={'lower':1,'flat':2,'upper':3}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class Solver:
 def __init__(self,N,engine,D):
    self.m=model(engine,N,D);self.mon=Monitor(self.m,engine);self.lo=self.m.dim//2-3
 def eig(self,f,vectors=False):
    return eigh(self.mon.hr(self.mon.k(np.asarray(f))),subset_by_index=(self.lo,self.lo+5),eigvals_only=not vectors)
 def root(self,seed,gap):
    seed=np.asarray(seed,float);i=GAP_INDEX[gap];bounds=(np.maximum(seed-P['local_box_radius'],0),np.minimum(seed+P['local_box_radius'],1))
    if np.any(bounds[0]>=bounds[1]):return {'accepted':False,'seed':seed.tolist(),'reason':'invalid local box'}
    _,v=self.eig(seed,True);anchor=v[:,i:i+2];minimum_overlap=1.
    def residual(f):
        nonlocal minimum_overlap
        w,v=self.eig(f,True);v=v[:,i:i+2];u,s,vt=np.linalg.svd(v.T@anchor);minimum_overlap=min(minimum_overlap,float(s.min()));q=u@vt
        h=q.T@np.diag(w[i:i+2]-np.mean(w[i:i+2]))@q
        return np.array([h[0,0]-h[1,1],2*h[0,1]])
    opt=least_squares(residual,np.clip(seed,*bounds),bounds=bounds,xtol=1e-11,ftol=1e-11,gtol=1e-11,max_nfev=P['max_root_evaluations'])
    f=opt.x;w=self.eig(f);g=float(w[i+1]-w[i]);jac=np.linalg.svd(opt.jac,compute_uv=False)
    ok=bool(opt.success and np.isfinite(f).all() and np.isfinite(g) and g<P['root_gap_meV'] and minimum_overlap>P['minimum_anchor_overlap'])
    return {'accepted':ok,'seed':seed.tolist(),'f':f.tolist(),'gap_meV':g,'optimizer_success':bool(opt.success),'status':int(opt.status),'message':opt.message,'nfev':int(opt.nfev),'min_anchor_overlap':minimum_overlap,'jacobian_singular_values':jac.tolist()}
 def grid(self,n):
    fs=np.linspace(0,1,n);V=np.empty((n,n,2))
    for a,x in enumerate(fs):
        for b,y in enumerate(fs):
            w=self.eig([x,y]);V[a,b]=[w[2]-w[1],w[4]-w[3]]
    seeds={}
    for j,gap in enumerate(['lower','upper']):
        vals=V[:,:,j];mask=vals<=minimum_filter(vals,size=3,mode='constant',cval=np.inf)
        candidates=sorted((float(vals[a,b]),a,b) for a,b in np.argwhere(mask))[:P['max_grid_minima_per_gap']]
        seeds[gap]=[np.array([fs[a],fs[b]]) for val,a,b in candidates]
    return V,seeds

def unique(records):
 roots=[]
 for r in sorted([x for x in records if x['accepted']],key=lambda x:x['gap_meV']):
    if all(np.linalg.norm(np.array(r['f'])-x['f'])>P['dedup_distance'] for x in roots):roots.append(r)
 return sorted(roots,key=lambda x:tuple(x['f']))
def same_set(a,b):
 if len(a)!=len(b):return False
 if not a:return True
 C=np.array([[np.linalg.norm(np.array(x['f'])-y['f']) for y in b] for x in a]);i,j=linear_sum_assignment(C)
 return bool(max(C[i,j])<P['root_set_match_distance'])
def match(prev,cur,next_id):
 cur=[dict(x) for x in cur];links=[];used=set();lost=[]
 if prev and cur:
    C=np.array([[np.linalg.norm(np.array(a['f'])-b['f']) for b in cur] for a in prev]);ii,jj=linear_sum_assignment(C)
    for i,j in zip(ii,jj):
        distance=float(C[i,j])
        if distance>P['max_track_step']:continue
        other=np.delete(C[i],j);margin=float(other.min()-distance) if len(other) else None
        cur[j]['track']=prev[i]['track'];used.add(i)
        links.append({'track':cur[j]['track'],'from_index':int(i),'to_index':int(j),'distance':distance,'nearest_margin':margin,'ambiguous':bool(margin is not None and margin<P['ambiguous_nearest_margin'])})
 for i,a in enumerate(prev):
    if i not in used:lost.append(a['track'])
 born=[]
 for x in cur:
    if 'track' not in x:x['track']=next_id;born.append(next_id);next_id+=1
 return cur,next_id,{'links':links,'unmatched_previous':lost,'new_tracks':born}

def crossing(N,engine):
 evaluations=[]
 def measure(D,seed):
    s=Solver(N,engine,D);flat=[s.root(f,'flat') for f in P['flat_seeds']];up=s.root(seed,'upper')
    if not all(r['accepted'] for r in [*flat,up]):raise RuntimeError('crossing root failure')
    if np.linalg.norm(np.array(up['f'])-seed)>.05:raise RuntimeError('crossing continuation jump')
    t,off,L=segment_geometry(flat[0]['f'],flat[1]['f'],up['f'])
    if not 0<t<1:raise RuntimeError('crossing outside segment')
    r={'D_meV':D,'t':t,'offset':off,'flat':flat,'upper':up};evaluations.append(r);return r
 a=measure(38.,np.array(P['crossing_refinement']['upper_seed']));b=measure(39.,np.array(a['upper']['f']))
 if not a['offset']>0>b['offset']:raise RuntimeError('crossing bracket not reproduced')
 while b['D_meV']-a['D_meV']>P['crossing_refinement']['max_width_meV']:
    mid=(a['D_meV']+b['D_meV'])/2;c=measure(mid,(np.array(a['upper']['f'])+b['upper']['f'])/2)
    if c['offset']>0:a=c
    else:b=c
 return {'bracket_D_meV':[a['D_meV'],b['D_meV']],'endpoint_t':[a['t'],b['t']],'endpoint_offsets':[a['offset'],b['offset']],'evaluations':evaluations}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--N',type=int,choices=P['N_values'],required=True);ap.add_argument('--output',required=True);args=ap.parse_args();dest=ROOT/args.output;gridpath=dest.with_suffix('.npz')
 if dest.exists() or gridpath.exists():raise SystemExit('Refusing overwrite')
 sources=[ROOT/'track.py',ROOT.parent/'r1_validation'/'validate.py',ROOT.parent/'r1_validation'/'PLAN.json',* (ROOT.parent/'r1_reproduction').glob('*.py'),ROOT.parent/'r1_reproduction'/'PLAN.json']
 report={'status':'RUNNING','N':args.N,'plan_sha256':sha(ROOT/'PLAN.json'),'source_hashes':{str(f.relative_to(ROOT.parent)):sha(f) for f in sources},'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'stations':[],'crossing_refinements':{},'coverage_warnings':[]};grids={}
 def save():dest.write_text(json.dumps(report,indent=2)+'\n');np.savez_compressed(gridpath,**grids)
 save()
 try:
  for engine in P['engines']:
   prev={'lower':[],'upper':[]};ids={'lower':0,'upper':0};flat_seed=P['flat_seeds']
   for D in np.arange(P['D_interval_meV'][0],P['D_interval_meV'][1]+P['D_step_meV']/2,P['D_step_meV']):
    start=time.time();D=float(D);s=Solver(args.N,engine,D);flat=[s.root(f,'flat') for f in flat_seed]
    if not all(r['accepted'] for r in flat) or np.linalg.norm(np.array(flat[0]['f'])-flat[1]['f'])<1e-4:raise RuntimeError('flat-pair root failure')
    flat_seed=[r['f'] for r in flat];V,seeds=s.grid(P['coarse_grid_points_per_axis']);key=f'{engine}_D{D:g}_coarse';grids[key]=V
    row={'engine':engine,'D_meV':D,'flat':flat,'affine_checks':s.mon.affine_checks,'affine_spectrum_errors':s.mon.spectral_checks,'grids':[key],'gaps':{}}
    fine=None
    if D in P['fine_grid_D_meV']:
        V,fine=s.grid(P['fine_grid_points_per_axis']);key=f'{engine}_D{D:g}_fine';grids[key]=V;row['grids'].append(key)
    for gap in P['adjacent_gaps']:
        carried=[np.array(r['f']) for r in prev[gap]]
        if D==36. and gap=='upper':carried += [np.array(x) for x in P['known_upper_seeds_at_D36']]
        attempts=[]
        for source,seedlist in [('continuation',carried),('coarse_grid',seeds[gap]),('fine_grid',fine[gap] if fine else [])]:
            for seed in seedlist:
                r=s.root(seed,gap);r['seed_source']=source;attempts.append(r)
        roots=unique(attempts);coarse=unique([r for r in attempts if r['seed_source']!='fine_grid']);fine_roots=unique([r for r in attempts if r['seed_source']!='coarse_grid']) if fine else None
        agreement=same_set(coarse,fine_roots) if fine else None
        if agreement is False:report['coverage_warnings'].append({'engine':engine,'D':D,'gap':gap,'reason':'coarse/fine inventories differ despite shared continuation seeds'})
        roots,ids[gap],tracking=match(prev[gap],roots,ids[gap])
        for r in roots:
            t,off,L=segment_geometry(flat[0]['f'],flat[1]['f'],r['f']);delta=np.array(r['f'])-flat[0]['f'];image=((delta+.5)%1-.5)-delta
            r['geometry']={'t':t,'offset':off,'image_shift':image.tolist()}
        if any(x['ambiguous'] for x in tracking['links']):report['coverage_warnings'].append({'engine':engine,'D':D,'gap':gap,'reason':'ambiguous nearest continuation'})
        rejected=sum(not r['accepted'] for r in attempts)
        if rejected:report['coverage_warnings'].append({'engine':engine,'D':D,'gap':gap,'reason':'rejected seed refinements retained; not a count of missed roots','count':rejected})
        if tracking['unmatched_previous']:report['coverage_warnings'].append({'engine':engine,'D':D,'gap':gap,'reason':'previously tracked roots not recovered; no annihilation inference','tracks':tracking['unmatched_previous']})
        row['gaps'][gap]={'roots':roots,'attempts':attempts,'grid_agreement':agreement,'tracking':tracking};prev[gap]=roots
    row['seconds']=time.time()-start;report['stations'].append(row);save()
    print('STATION',args.N,engine,D,'counts',[(g,len(row['gaps'][g]['roots'])) for g in P['adjacent_gaps']],'grids',[row['gaps'][g]['grid_agreement'] for g in P['adjacent_gaps']],'seconds',round(row['seconds'],1),flush=True)
   report['crossing_refinements'][engine]=crossing(args.N,engine);save();print('BRACKET',args.N,engine,report['crossing_refinements'][engine]['bracket_D_meV'],flush=True)
  report['status']='BOUNDED_TRACKING_COMPLETE_WITH_COVERAGE_WARNINGS' if report['coverage_warnings'] else 'BOUNDED_TRACKING_COMPLETE_NOT_GLOBAL_INVENTORY_PROOF'
 except Exception:report['status']='UNRESOLVED';report['error']=traceback.format_exc();print(report['error'],flush=True)
 finally:save()
 return 1 if report['status']=='UNRESOLVED' else 0
if __name__=='__main__':raise SystemExit(main())
