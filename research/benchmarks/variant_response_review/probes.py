"""Bounded response review: actual models and explicitly labeled contract controls."""
import json,hashlib,time,platform
import numpy as np,scipy
import scipy.sparse as sp
from scipy.linalg import eigh
from threadpoolctl import threadpool_limits,threadpool_info
from response_inputs import ROOT,activate
activate()
from bm_strain import BM,sz
from knobs import add_harmonic
from gate import real_basis
from fast_engine import RealEngine
from sparse_mode_v2 import CertifiedSparse,Ledger,ComparisonPolicy
import topo,braid

def run():
    start=time.perf_counter();plan=json.loads((ROOT/'PLAN.json').read_text());p=plan['matrix_checks'];rows=[];bases={};sparse=[]
    for N in p['N']:
        for valley in p['valleys']:
            m=BM(N=N,valley=valley,**p['model']);U=real_basis(m.nG);E=RealEngine(m)
            raw=json.dumps(m.idx,separators=(',',':')).encode()
            bases[str(N)]={'dim':m.dim,'ordered_indices':m.idx,'sha256':hashlib.sha256(raw).hexdigest()}
            for f0 in p['f']:
                f=np.array(f0);k=m.frac_to_k(f);H=m.H(k);HR=U.conj().T@H@U;F=E.HR(f);lo=m.dim//2-3
                w,V=eigh(HR.real,subset_by_index=(lo,lo+5));wn=eigh(H,eigvals_only=True,subset_by_index=(lo,lo+5));wf=E.bands(f,3)
                Q=V[:,2:4];Qf=E.frame_k(k,m.dim//2-1)
                derrors=[]
                for axis in (0,1):
                    df=np.eye(2)[axis]*p['derivative_step_fractional']
                    dnative=U.conj().T@(m.H(m.frac_to_k(f+df))-m.H(m.frac_to_k(f-df)))@U/(2*p['derivative_step_fractional'])
                    derrors.append(float(np.max(np.abs(E.dHR_proj(Q,axis)-Q.T@dnative@Q))))
                row={'N':N,'valley':valley,'f':f0,'dim':m.dim,'native_bands_meV':wn.tolist(),'fast_bands_meV':wf.tolist(),'matrix_error_meV':float(np.max(np.abs(F-HR))),'spectrum_error_meV':float(np.max(np.abs(wf-wn))),'derivative_errors_meV':derrors,'frame_projector_error':float(np.max(np.abs(Q@Q.T-Qf@Qf.T)))}
                row['pass']=bool(row['matrix_error_meV']<=p['matrix_tol_meV'] and row['spectrum_error_meV']<=p['spectrum_tol_meV'] and max(derrors)<=p['derivative_tol_meV'] and row['frame_projector_error']<=p['frame_projector_tol']);rows.append(row)
                if N==4:
                    ledger=Ledger();C=CertifiedSparse(m,ledger,ComparisonPolicy(ledger));S=C.S_k(k).toarray()
                    try:
                        ws,_,_=C.window(f,lo,6,where=f'valley={valley},f={f0}')
                        sr={'status':'RETURNED','bands_meV':ws.tolist(),'spectrum_error_meV':float(np.max(np.abs(ws-wn)))}
                    except Exception as ex:sr={'status':'REJECTED','error_type':type(ex).__name__,'error':str(ex)}
                    sparse.append({'valley':valley,'f':f0,'matrix_error_meV':float(np.max(np.abs(S-HR))),'ledger':ledger.entries,**sr})
    controls={}
    m=BM(N=3,eps=.003,kinetic='lab_nn_full',geometry='exact',mass=1);U=real_basis(m.nG)
    try: topo.band_sign_holonomy(m,U,m.dim//2-1,0,.27,n=8);controls['native_mass_reality']={'rejected':False}
    except Exception as ex:controls['native_mass_reality']={'rejected':True,'error_type':type(ex).__name__,'error':str(ex)}
    m=BM(N=3,eps=.003,kinetic='lab_nn_full',geometry='exact');U=real_basis(m.nG)
    controls['native_gap_tol_ignored']={'requested_gap_tol':1e6,'returned':topo.euler_wilson(m,U,nf1=4,nf2=4,gap_tol=1e6)}
    class Toy:
        dim=4;valley=1
        def frac_to_k(self,f):return np.asarray(f)
        def H(self,k):return np.diag([-3.,-1.,1.,3.]).astype(complex)
    class JumpToy(Toy):
        def H(self,k):return np.diag([-3.,-1.,1.,3.] if int(round(4*k[1]))%2==0 else [-1.,-3.,3.,1.]).astype(complex)
    class DegenerateToy(Toy):
        def H(self,k):return np.diag([-2.,0.,0.,2.]).astype(complex)
    class SmoothToy(Toy):
        def H(self,k):
            a=2*np.pi*k[0];c,s=np.cos(a),np.sin(a);R=np.eye(4);R[:2,:2]=[[c,-s],[s,c]]
            return (R@np.diag([-3.,-1.,1.,3.])@R.T).astype(complex)
    shift0=topo.shift_matrix
    try:
        topo.shift_matrix=lambda m,d:np.eye(m.dim)
        controls['synthetic_zero_overlap']={'kind':'piecewise constant synthetic Hamiltonian; API counterexample, not a physical result','returned':topo.euler_wilson(JumpToy(),np.eye(4),nf1=4,nf2=4,gap_tol=.1)}
        controls['synthetic_band_selection']={'lowest_pair':topo.euler_wilson(Toy(),np.eye(4),lo=0,nf1=4,nf2=4),'highest_pair':topo.euler_wilson(Toy(),np.eye(4),lo=2,nf1=4,nf2=4),'expected_external_gap_meV_for_both':2.0}
        try:topo.euler_wilson(Toy(),np.eye(4),lo=999,nf1=4,nf2=4);controls['out_of_range_rejected']=False
        except ValueError:controls['out_of_range_rejected']=True
        try:topo.band_sign_holonomy(DegenerateToy(),np.eye(4),1,0,0,n=4);controls['degenerate_band_rejected']=False
        except topo.DegeneracyError:controls['degenerate_band_rejected']=True
        value,gap=topo.band_sign_holonomy(SmoothToy(),np.eye(4),1,0,0,n=4)
        frames=[topo.frame_at(SmoothToy(),np.eye(4),[t,0],1,1)[1][:,0] for t in np.linspace(0,1,5)]
        controls['synthetic_smooth_band_overlap']={'kind':'smooth periodic real isolated band, coarsely sampled','returned_value':value,'min_band_gap_meV':gap,'min_adjacent_abs_overlap':float(min(abs(a@b) for a,b in zip(frames,frames[1:]))),'n':4}
    finally:topo.shift_matrix=shift0
    # Instrument coordinates while holding frames fixed. Execute the unchanged node_winding implementation.
    Q=np.eye(4)[:,:2];saved=(topo.frame_at,topo.transport,braid.real_frame);geometry=[]
    try:
        for off in ([1.,0.],[-1.,0.]):
            log={'frame_starts':[],'transport':[],'loop_points':[]}
            def frame_at(m,U,k,lo,n=2):log['frame_starts'].append(np.asarray(k).tolist());return np.array([-1.,1.]),Q
            def transport(m,U,pts,base,nstep=300):log['transport'].append([np.asarray(a).tolist() for a in pts]);return Q
            def frame(m,U,k):log['loop_points'].append(np.asarray(k).tolist());return Q
            topo.frame_at=frame_at;topo.transport=transport;braid.real_frame=frame
            topo.pair_charges(Toy(),np.eye(4),[np.array([.3,.4]),np.array([.6,.6])],start_offset=np.array(off))
            geometry.append({'start_offset_direction':off,'base_start':log['frame_starts'][0],'transport':log['transport'][0],'first_loop_start':log['loop_points'][0],'second_loop_start':log['loop_points'][97],'base_to_first_loop_distance':float(np.linalg.norm(np.array(log['frame_starts'][0])-log['loop_points'][0])),'transport_end_to_second_loop_distance':float(np.linalg.norm(np.array(log['transport'][0][-1])-log['loop_points'][97])),'loop_samples':len(log['loop_points'])})
    finally:topo.frame_at,topo.transport,braid.real_frame=saved
    controls['instrumented_loop_geometry']={'kind':'held-constant eigenframes; tests coordinate plumbing only, no charge prediction','runs':geometry}
    C=CertifiedSparse.__new__(CertifiedSparse);C.D=2;C.I=sp.eye(2,format='csr');C.ledger=Ledger();C.policy=ComparisonPolicy(C.ledger)
    A=np.array([[0.,1.],[1.,0.]]);lu,count=C._fact(sp.csr_matrix(A),0.,'synthetic inertia')
    controls['synthetic_inertia']={'kind':'nonsingular symmetric 2x2 kernel counterexample; not an accepted physical sparse window','matrix':A.tolist(),'mu':0.,'true_eigenvalues':np.linalg.eigvalsh(A).tolist(),'returned_negative_count':count,'true_negative_count':1,'U_diagonal':lu.U.diagonal().tolist(),'row_permutation':lu.perm_r.tolist(),'column_permutation':lu.perm_c.tolist(),'ledger':C.ledger.entries}
    # Exact reproduction of the producer's chosen K-prime centers, with native gaps newly retained.
    record=json.loads((ROOT/'original/VALLEY_MIRROR.json').read_text());centers=[]
    for B in plan['mirrored_centers']['B']:
        nk=np.array(record[f'braid_{B}']['K']['nodes']);d=((nk[1]-nk[0])+.5)%1-.5
        m=BM(N=4,eps=.003,phi_deg=0,A_scalar=.2,kinetic='lab_nn_full',geometry='exact',valley=-1);add_harmonic(m,B,mat=sz,use_sin=True)
        fn=lambda f:m.gaps(m.frac_to_k(f))[0]
        p0,res=m.refine((-nk[0])%1,fn)
        centers.append({'B':B,'seed':((-nk[0])%1).tolist(),'p0':p0.tolist(),'p1_used':(p0-d).tolist(),'first_native_gap_meV':float(fn(p0)),'second_native_gap_meV':float(fn(p0-d)),'refiner_returned_gap_meV':float(res),'image':(-d).tolist()})
    out={'plan_sha256':hashlib.sha256((ROOT/'PLAN.json').read_bytes()).hexdigest(),'matrix_rows':rows,'sparse_smoke':sparse,'controls':controls,'mirrored_centers':centers,'elapsed_s':time.perf_counter()-start,'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'threadpools':threadpool_info()}}
    (ROOT/'BASIS.json').write_text(json.dumps(bases,indent=2)+'\n');(ROOT/'PROBES.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'matrix_rows':len(rows),'passing_rows':sum(r['pass'] for r in rows),'max_spectrum_error_meV':max(r['spectrum_error_meV'] for r in rows),'max_derivative_error_meV':max(max(r['derivative_errors_meV']) for r in rows),'sparse_status':[r['status'] for r in sparse],'controls':controls,'mirrored_centers':centers},indent=2))
if __name__=='__main__':
    with threadpool_limits(limits=1):run()
