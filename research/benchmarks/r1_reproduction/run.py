"""Explicit-parameter, checkpointed endpoint reproduction; no environment model defaults.
Imported engines/helpers retain their source bytes. Frame instrumentation below adds
four-band spectral diagnostics at precisely the points used by charge/transport.
This is not the full historical acceptance gate.
"""
import argparse, hashlib, json, time, platform, traceback
from pathlib import Path
import numpy as np
import scipy
from scipy.linalg import eigh
from bm_strain import BM, frac_dist
from tbg_ref import TBG
import braid
from gate import real_basis, classify

ROOT=Path(__file__).resolve().parent
PLAN=json.loads((ROOT/'PLAN.json').read_text())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def model(engine,N,D):
    if engine=='bm': return BM(N=N,theta_deg=1.,eps=.007,phi_deg=15.,w1=110.,ratio=.8,kinetic='lab_nn_full',geometry='exact',cutoff_tol=1e-6,Dfield=D)
    return TBG(N=N,theta=1.,eps=.007,phi=15.,w1=110.,w0=88.,kinetic='lab_nn_full',cutoff_tol=1e-9,Dfield=D)

def station(engine,cfg,D):
    start=time.time();m=model(engine,cfg['N'],D);U=real_basis(m.nG) if engine=='bm' else m.real_basis();lo=m.dim//2-1
    kfun=m.frac_to_k if engine=='bm' else m.k
    gap=(lambda f:m.gaps(kfun(f))[0]) if engine=='bm' else m.flat_gap
    points=[];gaps=[];optim=[]
    for seed in PLAN['flat_seeds']:
        if engine=='bm':
            p,g,meta=m.refine(np.array(seed),gap,return_result=True)
            if not meta['success']:raise RuntimeError(str(meta))
        else:
            p,g=m.refine(np.array(seed),gap);meta={'success':True,'detail':'native ref.refine raises on optimizer failure'}
        points.append(p);gaps.append(float(g));optim.append(meta)
    if max(gaps)>1e-6 or frac_dist(*points)<1e-4:raise RuntimeError('invalid flat roots')
    diagnostics={'frames':0,'min_sampled_exterior_gap_meV':float('inf'),'max_imag_meV':0.,'max_hermiticity_meV':0.}
    def frame(k):
        h=U.conj().T@m.H(k)@U
        imag=float(np.abs(h.imag).max());herm=float(np.abs(h-h.conj().T).max())
        diagnostics['max_imag_meV']=max(imag,diagnostics['max_imag_meV']);diagnostics['max_hermiticity_meV']=max(herm,diagnostics['max_hermiticity_meV'])
        if imag>1e-9 or herm>1e-9:raise RuntimeError('real-frame check failed')
        w,v=eigh(h.real,subset_by_index=(lo-1,lo+2))
        diagnostics['frames']+=1
        diagnostics['min_sampled_exterior_gap_meV']=min(diagnostics['min_sampled_exterior_gap_meV'],float(min(w[1]-w[0],w[3]-w[2])))
        return v[:,1:3]
    p,q=points;d=(q-p+.5)%1-.5
    if engine=='bm':
        braid.real_frame=lambda model,u,k:frame(k)
        r=cfg['bm_radius'];a=p+np.array([r,0]);b=p+d+np.array([r,0]);base=frame(kfun(a))
        w1=braid.node_winding(m,U,p,r,cfg['bm_loop_points'],base,exploratory=True)
        end=braid.transport(m,U,[a,b],base,nstep=cfg['transport_points'],exploratory=True)
        w2=braid.node_winding(m,U,p+d,r,cfg['bm_loop_points'],end,exploratory=True)
        overlap=None
    else:
        m.real_frame=lambda u,k,band,nb=2:frame(k)
        r=cfg['ref_radius'];off=-1.5*r*d/np.linalg.norm(d);m.smin_log=[]
        base=frame(kfun(p+off))
        w1=m.node_charge(U,p,lo,base,r=r,npts=cfg['ref_loop_points'])
        end=m.transport(U,lo,p+off,p+d-off,base,n=cfg['transport_points'])
        w2=m.node_charge(U,p+d,lo,end,r=r,npts=cfg['ref_loop_points'])
        overlap=min(m.smin_log)
    lab=classify(w1,w2) if w1 is not None and w2 is not None else 'INDETERMINATE'
    ok=lab==PLAN['expected_labels'][str(D)] and diagnostics['min_sampled_exterior_gap_meV']>0.001
    return dict(engine=engine,stage=cfg['name'],N=cfg['N'],D_meV=D,layer_difference_meV=2*D,dimension=m.dim,nG=m.nG,flat=[x.tolist() for x in points],root_gaps_meV=gaps,optimizer=optim,windings=[w1,w2],label=lab,ref_fixed_frame_overlap=overlap,diagnostics=diagnostics,diagnostic_pass=bool(ok),seconds=time.time()-start)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=[s['name'] for s in PLAN['stages']],required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    dest=ROOT/args.output
    if dest.exists():raise SystemExit('Refusing to overwrite previous run')
    cfg=next(s for s in PLAN['stages'] if s['name']==args.stage)
    report=dict(status='RUNNING',plan_sha256=digest(ROOT/'PLAN.json'),source_sha256={p.name:digest(p) for p in ROOT.glob('*.py')},versions={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},configuration=cfg,rows=[])
    def save():dest.write_text(json.dumps(report,indent=2)+'\n')
    save()
    try:
        for D in PLAN['stations_D_meV']:
            for engine in ['bm','ref']:
                print('START',args.stage,engine,D,flush=True)
                row=station(engine,cfg,D);report['rows'].append(row);save();print('RESULT',engine,D,row['label'],row['windings'],row['diagnostics'],'seconds',round(row['seconds'],2),flush=True)
                if not row['diagnostic_pass']:raise RuntimeError('station failed frozen diagnostic criteria')
            a,b=report['rows'][-2:];dist=max(frac_dist(np.array(p),np.array(q)) for p,q in zip(a['flat'],b['flat']))
            report.setdefault('matched_engine_root_distances',[]).append({'D':D,'distance':float(dist)})
            if dist>1e-4:raise RuntimeError('engine root disagreement')
        report['status']='ENDPOINT_DIAGNOSTICS_PASS_NOT_BRAID_ACCEPTANCE'
    except Exception:
        report['status']='UNRESOLVED';report['error']=traceback.format_exc();print(report['error'],flush=True)
    finally:save()
    return 0 if report['status'].startswith('ENDPOINT') else 1
if __name__=='__main__':raise SystemExit(main())
