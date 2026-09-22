"""Bounded numerical and synthetic contract probes; original code is unchanged."""
import hashlib, json, platform, time
from pathlib import Path
import numpy as np
import scipy
from scipy.linalg import eigh
from threadpoolctl import threadpool_info, threadpool_limits
from variant_inputs import ROOT, activate
activate()
from bm_strain import BM
from gate import real_basis
from fast_engine import RealEngine
import topo
from euler import real_frame

def digest(a): return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def dump(name,data): (ROOT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')

def run():
    plan=json.loads((ROOT/'PLAN.json').read_text()); p=plan['native_fast_comparison']
    rows=[]; bases={}; started=time.perf_counter(); counts={'native_H':0,'fast_HR':0,'native_eigh_six':0,'fast_eigh_six':0}
    for N in p['N']:
        K=BM(N=N,valley=1,**p['model']); U=real_basis(K.nG)
        raw=json.dumps(K.idx,separators=(',',':')).encode()
        bases[str(N)]={'dim':K.dim,'nG':K.nG,'ordered_indices':K.idx,'indices_json_sha256':hashlib.sha256(raw).hexdigest()}
        for valley in p['valleys']:
            m=BM(N=N,valley=valley,**p['model']); fast=RealEngine(m)
            for f in p['f']:
                k=m.frac_to_k(np.array(f)); H=m.H(k); counts['native_H']+=1
                HR=U.conj().T@H@U; F=fast.HR(f); counts['fast_HR']+=1
                bounds=(m.dim//2-3,m.dim//2+2)
                wn=eigh(H,eigvals_only=True,subset_by_index=bounds); counts['native_eigh_six']+=1
                wf=eigh(F,eigvals_only=True,subset_by_index=bounds); counts['fast_eigh_six']+=1
                opposite=np.conj(K.H(-k)); counts['native_H']+=1
                Ksame=U.conj().T@K.H(k)@U; counts['native_H']+=1
                row={'N':N,'valley':valley,'f':f,'dim':m.dim,'band_indices':list(range(bounds[0],bounds[1]+1)),
                     'native_matrix_sha256':digest(H),'fast_matrix_sha256':digest(F),
                     'native_reality_residual_meV':float(np.max(np.abs(HR.imag))),
                     'matrix_error_meV':float(np.max(np.abs(F-HR))),
                     'spectrum_error_meV':float(np.max(np.abs(wf-wn))),
                     'native_bands_meV':wn.tolist(),'fast_bands_meV':wf.tolist(),
                     'fast_error_vs_positive_valley_at_same_k_meV':float(np.max(np.abs(F-Ksame))),
                     'native_exact_time_reversal':bool(np.array_equal(H,opposite)) if valley==-1 else None,
                     'matrix_tolerance_met':bool(np.max(np.abs(F-HR))<=p['matrix_tol_meV']),
                     'spectrum_tolerance_met':bool(np.max(np.abs(wf-wn))<=p['spectrum_tol_meV'])}
                rows.append(row)
    # Synthetic API probes: no physical-model or topology conclusions.
    class Toy:
        dim=4; valley=1
        def frac_to_k(self,f): return np.asarray(f)
    Q0=np.eye(4)[:,:2]; Q1=np.eye(4)[:,2:]
    original_frame,original_shift=topo.real_frame,topo.shift_matrix
    try:
        topo.shift_matrix=lambda m,d:np.eye(4)
        topo.real_frame=lambda m,U,k:Q0 if int(round(k[1]*4))%2==0 else Q1
        singular=topo.euler_wilson(Toy(),np.eye(4),nf1=4,nf2=4)
        topo.real_frame=lambda m,U,k:Q0
        lo_runs=[{'lo':lo,'return':topo.euler_wilson(Toy(),np.eye(4),lo=lo,nf1=4,nf2=4)} for lo in (0,1,999)]
    finally:
        topo.real_frame,topo.shift_matrix=original_frame,original_shift
    broken=BM(N=3,eps=.003,kinetic='lab_nn_full',geometry='exact',mass=1.0)
    U=real_basis(broken.nG); k=broken.frac_to_k(np.array([.31,.27]))
    residual=float(np.max(np.abs((U.conj().T@broken.H(k)@U).imag)))
    try:
        real_frame(broken,U,k); frame_status='RETURNED'
    except RuntimeError as ex: frame_status=str(ex)
    try:
        value=topo.band_sign_holonomy(broken,U,broken.dim//2-1,0,.27,n=8)
        band_probe={'status':'RETURNED','value':float(value)}
    except Exception as ex: band_probe={'status':'REJECTED','error':str(ex)}
    controls={
      'synthetic_rank_zero_W':{'kind':'synthetic contract counterexample','frame_orthogonality_residual':float(np.max(np.abs(Q0.T@Q1))),'loop_product_singular_values':[0,0],'returned_euler_estimate':singular[0],'returned_closure':singular[1],'returned_min_polar_det':singular[2],'interpretation':'The returned determinant does not diagnose a singular Wilson product; this does not reproduce |e2|=1 or invalidate a physical run.'},
      'synthetic_unused_lo':{'kind':'synthetic API probe','runs':lo_runs,'interpretation':'lo is assigned but never supplied to real_frame. The original helper always selects the central pair.'},
      'native_broken_reality':{'kind':'native BM negative control','model':{'N':3,'eps':.003,'kinetic':'lab_nn_full','geometry':'exact','mass':1.0},'probe_f':[.31,.27],'imaginary_residual_meV':residual,'real_frame_outcome':frame_status,'band_sign_holonomy':band_probe,'holonomy_axis':0,'holonomy_c':.27,'holonomy_n':8,'interpretation':'Sign-holonomy helper must enforce its real-Hamiltonian precondition; the massless supplied controls are not disproved by this negative control.'}}
    elapsed=time.perf_counter()-started
    result={'plan_sha256':hashlib.sha256((ROOT/'PLAN.json').read_bytes()).hexdigest(),'rows':rows,'contract_probes':controls,'comparison_call_counts':counts,'call_count_scope':'Comparison loop only; negative-control calls listed separately below. Constructor work is included in elapsed time, not in these call counts. Synthetic probes use no eigensolver.','native_negative_control_calls':{'probe_H':1,'real_frame_H':1,'holonomy_H':9,'holonomy_eigh':9},'elapsed_s':elapsed,'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'threadpools':threadpool_info()}}
    dump('BASIS.json',bases);dump('PROBES.json',result)
    print(json.dumps({'rows':len(rows),'K_max_matrix_error_meV':max(r['matrix_error_meV'] for r in rows if r['valley']==1),'Kprime_max_matrix_error_meV':max(r['matrix_error_meV'] for r in rows if r['valley']==-1),'Kprime_max_spectrum_error_meV':max(r['spectrum_error_meV'] for r in rows if r['valley']==-1),'contract_probes':controls,'elapsed_s':elapsed},indent=2))

if __name__=='__main__':
    with threadpool_limits(limits=1): run()
