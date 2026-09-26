#!/usr/bin/env python3
"""Bounded three-front packet. Producer checks never constitute independent review."""
import argparse, gzip, hashlib, importlib.util, json, os, resource, signal, subprocess, sys, time
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,obj): Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

def bindings(commit):
    manifest=json.loads((HERE/'SOURCE_BINDINGS.json').read_text())
    for name,sha in manifest.items():
        if digest(ROOT/name)!=sha: raise RuntimeError('SOURCE_MISMATCH:'+name)
    if commit:
        if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=commit: raise RuntimeError('HEAD_MISMATCH')
        for name in [*manifest,str((HERE/'SOURCE_BINDINGS.json').relative_to(ROOT))]:
            saved=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)
            if saved!=(ROOT/name).read_bytes(): raise RuntimeError('COMMIT_FILE_MISMATCH:'+name)
    return manifest

def setup(wheel):
    import numpy as np
    from flint import ctx
    ctx.prec=128;ctx.threads=1
    base=load(ROOT/'research/benchmarks/certification_s1b_001/check.py','tf_base')
    assembly=base.load_parent()
    case=json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text());assembly.validate_case(case)
    audit=load(ROOT/'docs/audits/parallel-domain-002-006/spotcheck.py','tf_provenance')
    lock=json.loads((ROOT/'research/benchmarks/certification_s1a_hardening_001/WHEEL_LOCK.json').read_text())
    provenance=audit.reviewer_provenance(Path(wheel),lock)
    provenance['scope']='producer runtime; reuse of loader inventory, not an independent audit'
    return np,base,assembly,case,provenance

def initial():
    old=json.loads((ROOT/'research/benchmarks/parallel_domain_006_execution/PARTITION.json').read_text())
    accepted=sorted(tuple(c) for state in old.values() for c in state['accepted'])
    parents=sorted(tuple(c) for state in old.values() for c in state['unresolved'])
    assert len(accepted)==2671 and len(parents)==120 and not any(s['frontier'] for s in old.values())
    assert all(d==10 for d,x,y in parents)
    children=sorted((11,2*x+i,2*y+j) for d,x,y in parents for i in range(2) for j in range(2))
    return accepted,parents,children

def partition_check(cells):
    import numpy as np
    raster=np.zeros((2048,2048),dtype=np.uint8)
    for d,x,y in cells:
        assert 1<=d<=11 and 0<=x<2**d and 0<=y<2**d
        s=2**(11-d);view=raster[x*s:(x+1)*s,y*s:(y+1)*s];assert not view.any();view[:]=1
    assert raster.all()

def refine(args,np,base,assembly,case):
    spec=json.loads((HERE/'SPEC.json').read_text())['refinement']
    _,_,children=initial();owned=children[args.slot::4]
    method=load(ROOT/'research/benchmarks/certification_s1b_method_004/check.py','tf_method')
    cutoff=case['cutoffs']['a'];coef,_=assembly.assemble_coefficients(cutoff['ordered_indices'],case)
    old=ROOT/'research/benchmarks/certification_s1b_quadrant_a_002';sys.path.insert(0,str(old))
    verifier=load(old/'verify.py','tf_verify')
    factors=0
    with (args.output/'CELLS.ndjson').open('x') as f:
        for cell in owned:
            evidence=method.probe_cell(base,assembly,coef,cutoff,{'precision_bits':128,'recomputation_decimal_digits':10},list(cell))
            p,r=verifier.verify_physical_evidence(evidence,evidence['status'],{'algorithm':{'precision_bits':128,'recomputation_decimal_digits':10}},cell)
            factors+=p+r;assert factors<=spec['factorizations_per_worker']
            f.write(json.dumps({'cell':cell,'evidence':evidence},sort_keys=True,separators=(',',':'))+'\n');f.flush();os.fsync(f.fileno())
    return {'completed_cells':len(owned),'factorizations':factors,'slot':args.slot,'independent_review':'PENDING'}

def float_coefficients(assembly,case,key):
    from flint import arb_mat
    c,geo=assembly.assemble_coefficients(case['cutoffs'][key]['ordered_indices'],case)
    return c,geo

def point_matrix(base,assembly,coef,x,y):
    h=base.matrix_from_coefficients(coef,Fraction(x),Fraction(y))
    return assembly.mid_float([[h[i,j] for j in range(h.ncols())] for i in range(h.nrows())])

def cutoff(args,np,base,assembly,case):
    import scipy.linalg as la
    spec=json.loads((HERE/'SPEC.json').read_text())['cutoff']
    rows=[];summaries={}
    for key in ['a','b']:
        coef,_=float_coefficients(assembly,case,key);lo,hi=case['cutoffs'][key]['selected_bands_zero_based'];group=[]
        for point in spec['points']:
            h=point_matrix(base,assembly,coef,*point['center']);e,v=la.eigh(h,driver='evr',check_finite=True)
            residual=float(np.max(np.abs(h@v-v*e)));assert residual<1e-8 and np.max(np.abs(h-h.T))<1e-12
            row={'cutoff':key,'point':point,'eigenvalues_meV':e.tolist(),'upper_gap_meV':float(e[hi+1]-e[hi]),'lower_gap_meV':float(e[lo]-e[lo-1]),'max_eigenpair_residual_meV':residual}
            rows.append(row);group.append(row)
        m=min(group,key=lambda r:(r['upper_gap_meV'],r['point']['index']));summaries[key]={'minimum_upper_gap_meV':m['upper_gap_meV'],'point':m['point']}
    write(args.output/'SPECTRA.json',rows)
    return {'status':'EXPLORATORY_POINT_COMPARISON','points_per_cutoff':len(spec['points']),'eigensolver_starts':len(rows),'minima':summaries,'independent_review':'PENDING','claim':'Sampled finite models only. No gap closure, global minimum, convergence, or certified area.'}

def dynamics(args,np,base,assembly,case):
    import scipy.linalg as la
    cfg=json.loads((HERE/'SPEC.json').read_text())['dynamics'];n=args.grid;assert n in cfg['grids']
    cutoff=case['cutoffs']['a'];lo,hi=cutoff['selected_bands_zero_based'];dim=cutoff['dimension']
    coef,geo=float_coefficients(assembly,case,'a');ev=np.zeros((n,n,2));vec=np.zeros((n,n,dim,2));residual=0.
    for i in range(n):
        for j in range(n):
            h=point_matrix(base,assembly,coef,Fraction(2*i+1,2*n),Fraction(2*j+1,2*n))
            e,v=la.eigh(h,subset_by_index=(lo,hi),driver='evr');ev[i,j]=e;vec[i,j]=v
            residual=max(residual,float(np.max(np.abs(h@v-v*e))))
    assert residual<1e-8
    # Real-basis seed at layer 1, G=(0,0), first real component; projection is gauge independent.
    seed=2*cutoff['ordered_indices'].index([0,0]);projection=vec[:,:,seed,:]
    g=np.array([[float(x.mid()) for x in geo[k]] for k in ['G1','G2']]).T
    direct=2*np.pi*np.linalg.inv(g).T/10 # reciprocal inverse angstrom -> direct nm
    area=abs(float(np.linalg.det(direct)));m=4*n;dx=.25;pixel_area=area*dx*dx
    x=(np.arange(n)+.5)/n;xx,yy=np.meshgrid(x,x,indexing='ij');center=[float(Fraction(v)) for v in cfg['center']]
    times=np.array(cfg['times_fs']);summaries={};states={}
    for width in cfg['widths']:
        envelope=np.exp(-((xx-center[0])**2+(yy-center[1])**2)/(4*width*width))
        weights=projection*envelope[:,:,None];weights/=np.linalg.norm(weights)
        probs=[];frames=[];boundary=[];means=[]
        for t in times:
            phased=weights*np.exp(-1j*ev*t/cfg['hbar_meV_fs']);amplitudes=np.einsum('ijdb,ijb->ijd',vec,phased)
            padded=np.zeros((m,m,dim),complex);start=(m-n)//2;padded[start:start+n,start:start+n]=amplitudes
            psi=np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(padded,axes=(0,1)),axes=(0,1)),axes=(0,1))*m
            density=np.sum(np.abs(psi)**2,axis=2)/pixel_area
            mass=float(density.sum()*pixel_area);probs.append(mass);assert abs(mass-1)<1e-10
            edge=np.ones((m,m),bool);edge[8:-8,8:-8]=False;boundary.append(float(density[edge].sum()*pixel_area))
            middle=m//2;crop=density[middle-32:middle+32,middle-32:middle+32];assert crop.shape==(64,64);frames.append(crop.astype('<f4'))
        tag='sigma'+str(width).replace('.','p');array=np.stack(frames);array.tofile(args.output/(tag+'-density.bin'))
        states[tag+'_weights']=weights
        summaries[tag]={'sigma_fractional':width,'max_norm_error':max(abs(p-1) for p in probs),'maximum_boundary_probability':max(boundary),'mean_energy_meV':float(np.sum(abs(weights)**2*ev)),'window_probability':(array.sum(axis=(1,2),dtype=np.float64)*pixel_area).tolist(),'density_file':tag+'-density.bin','density_sha256':digest(args.output/(tag+'-density.bin'))}
    np.savez_compressed(args.output/'MODES.npz',energies_meV=ev,vectors=vec,**states)
    return {'status':'APPROXIMATE_DYNAMICS_PENDING_COMPARISON','grid':n,'eigensolver_starts':n*n,'frames':len(times),'times_fs':times.tolist(),'display_grid':64,'step_moire':dx,'direct_basis_columns_nm':direct.tolist(),'pixel_area_nm_squared':pixel_area,'seed_real_basis_index':seed,'max_eigenpair_residual_meV':residual,'packets':summaries,'independent_review':'PENDING','claim':'Projected fixed finite Hamiltonian; coarse-grained envelope density sums reciprocal-component probabilities incoherently. No atom-resolved density, seam matching, convergence proof, experiment, or certified area.'}

def worker(args):
    spec=json.loads((HERE/'SPEC.json').read_text());bindings(args.implementation_commit)
    resource.setrlimit(resource.RLIMIT_AS,(spec['limits']['address_space_bytes'],)*2)
    resource.setrlimit(resource.RLIMIT_FSIZE,(spec['limits']['max_file_bytes'],)*2)
    np,base,assembly,case,provenance=setup(args.wheel);write(args.output/'RUNTIME.json',provenance)
    result={'refine':refine,'cutoff':cutoff,'dynamics':dynamics}[args.front](args,np,base,assembly,case)
    result.update(implementation_commit=args.implementation_commit,spec_sha256=digest(HERE/'SPEC.json'));write(args.output/'RESULTS.json',result)

def run(args):
    bindings(args.implementation_commit);spec=json.loads((HERE/'SPEC.json').read_text())
    if args.front=='cutoff':
        if args.review_receipt is None: raise RuntimeError('CUTOFF_INDEPENDENT_PRE_EXECUTION_REVIEW_REQUIRED')
        review=json.loads(args.review_receipt.read_text())
        if not (review.get('reviewer')=='CLAUDE' and review.get('verdict')=='PASS' and review.get('reviewed_commit')==args.implementation_commit and review.get('url','').startswith('https://github.com/alanfuller15/Twistronics/pull/2#')): raise RuntimeError('CUTOFF_REVIEW_BINDING')
    args.output.mkdir(parents=True,exist_ok=False)
    if args.front=='cutoff':write(args.output/'REVIEW_RECEIPT.json',review)
    command=[sys.executable,'-B',str(HERE/'run.py'),'worker','--front',args.front,'--slot',str(args.slot),'--grid',str(args.grid),'--output',str(args.output),'--wheel',str(args.wheel),'--implementation-commit',args.implementation_commit]
    env=dict(os.environ);env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    start=time.monotonic();timeout=spec['limits']['wall_seconds'][args.front];termination='NORMAL_EXIT'
    with (args.output/'WORKER.log').open('wb') as out:
        proc=subprocess.Popen(command,stdout=out,stderr=subprocess.STDOUT,env=env,start_new_session=True)
        try: rc=proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            termination='WATCHDOG_TIMEOUT';os.killpg(proc.pid,signal.SIGTERM)
            try: rc=proc.wait(timeout=10)
            except subprocess.TimeoutExpired: os.killpg(proc.pid,signal.SIGKILL);rc=proc.wait()
    try: os.killpg(proc.pid,0);empty=False
    except ProcessLookupError: empty=True
    files={p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in args.output.iterdir() if p.is_file()}
    receipt={'implementation_commit':args.implementation_commit,'front':args.front,'slot':args.slot,'grid':args.grid,'monotonic_start':start,'wall_limit_seconds':timeout,'elapsed_seconds':time.monotonic()-start,'exit_code':rc,'termination':termination,'process_group_empty':empty,'files':files}
    write(args.output/'RECEIPT.json',receipt);print(json.dumps(receipt));return 0 if rc==0 and empty and termination=='NORMAL_EXIT' else 1

def controls():
    bindings(None);a,p,c=initial();assert len(c)==480 and len(set(c))==480
    partition_check(a+c)
    shards=[c[i::4] for i in range(4)];assert all(len(s)==120 for s in shards) and sorted(sum(shards,[]))==c
    for faulty in [a+c+[c[0]],a+c[:-1]]:
        try: partition_check(faulty)
        except AssertionError: pass
        else: raise RuntimeError('BAD_PARTITION_ACCEPTED')
    assert sum(Fraction(1,4**d) for d,x,y in a)==Fraction(131057,131072)
    cfg=json.loads((HERE/'SPEC.json').read_text());pts=cfg['cutoff']['points'];assert len(pts)==64 and len({tuple(p['center']) for p in pts})==64
    import numpy as np
    # Analytic Fourier controls: constant momentum amplitude localizes at origin;
    # uniform phase changes cannot alter density; unitary FFT preserves mass.
    v=np.ones((16,16,2),complex);v/=np.linalg.norm(v)
    f=np.fft.ifft2(v,axes=(0,1))*16
    assert abs(np.sum(abs(f)**2)-1)<1e-12 and abs(f[0,0]).sum()>0
    assert np.allclose(abs(np.fft.ifft2(v*np.exp(1j*.7),axes=(0,1)))**2,abs(f/16)**2)
    print(json.dumps({'status':'PASS','physical_calls':0,'children':480,'owners':4,'controls':['exact partition','overlap rejection','gap rejection','round-robin ownership','exact inherited area','64 fixed distinct paired points','unitary Fourier norm','phase-invariant density']}))

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','controls']);p.add_argument('--front',choices=['refine','cutoff','dynamics']);p.add_argument('--slot',type=int,default=0);p.add_argument('--grid',type=int,default=16);p.add_argument('--wheel',type=Path);p.add_argument('--output',type=Path);p.add_argument('--implementation-commit');p.add_argument('--review-receipt',type=Path);args=p.parse_args()
    if args.mode=='controls': controls();return 0
    assert args.implementation_commit and len(args.implementation_commit)==40 and args.wheel and args.output
    assert 0<=args.slot<4
    return run(args) if args.mode=='run' else worker(args)
if __name__=='__main__':sys.exit(main())
