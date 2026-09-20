"""Numerical acceptance primitives. Thresholds are diagnostics, not a proof of topology.

Noncontractible paths must retain their explicit coordinate lift; do not silently
wrap transport paths. periodic_segment is only for shortest-segment geometry.
"""
import json
import os
import platform
import tempfile
from pathlib import Path

import numpy as np
from scipy.linalg import eigh

POLICY = dict(real_atol=1e-9, hermitian_atol=1e-9, orthogonal_atol=1e-8,
              eigen_relative_tol=1e-10, isolation_meV=1e-5,
              node_gap_meV=1e-6, rank_floor=1e-10,
              overlap_floor=0.1, seam_overlap_floor=0.95,
              seam_norm_error=0.02, integer_tol=0.05,
              node_separation_floor=1e-5, grid_gap_tolerance_meV=0.05)


class GateError(ValueError):
    """A prerequisite failed; the corresponding label is indeterminate."""


def require(condition, message):
    if not bool(condition):
        raise GateError(message)


def finite(value, name='value'):
    require(np.all(np.isfinite(value)), f'{name} is nonfinite')
    return value


def periodic_delta(a, b):
    return (np.asarray(a, float) - np.asarray(b, float) + 0.5) % 1.0 - 0.5


def periodic_segment(a, b):
    d = periodic_delta(b, a)
    finite(d, 'segment')
    require(not np.any(np.isclose(np.abs(d), .5, atol=1e-12, rtol=0)),
            'half-period segment has an ambiguous shortest lift')
    length = float(np.linalg.norm(d))
    require(length > POLICY['node_separation_floor'], 'coincident/unresolved nodes')
    return d, length, np.array([-d[1], d[0]]) / length


def require_nodes(nodes, count=2):
    require(len(nodes) >= count, f'need {count} nodes, found {len(nodes)}')
    for i in range(count):
        finite(nodes[i], 'node')
        for j in range(i):
            require(np.linalg.norm(periodic_delta(nodes[i], nodes[j])) >
                    POLICY['node_separation_floor'], 'duplicate node seeds converged together')


def validate_key(key, allowed):
    require(key in allowed, f'unknown sweep key {key!r}; expected {sorted(allowed)}')
    return key


def integer_charge(w):
    finite(w, 'winding')
    q = int(round(float(w)))
    require(q != 0 and abs(w-q) <= POLICY['integer_tol'],
            f'unresolved/noninteger winding {w}')
    return q


def relative_charge(a, b):
    try:
        return 'SAME' if integer_charge(a)*integer_charge(b) > 0 else 'OPPOSITE'
    except GateError:
        return 'INDETERMINATE'


def checked_qr(matrix):
    finite(matrix, 'QR input')
    singular = np.linalg.svd(matrix, compute_uv=False)
    require(singular[-1] > POLICY['rank_floor'], 'rank-deficient transported frame')
    q, r = np.linalg.qr(matrix)
    signs = np.where(np.diag(r) < 0, -1.0, 1.0)
    q = q * signs
    require(np.max(np.abs(q.T@q-np.eye(q.shape[1]))) <= POLICY['orthogonal_atol'],
            'QR frame not orthonormal')
    return q


def orient(previous, frame, floor=None):
    overlap = previous.T @ frame
    s = np.linalg.svd(overlap, compute_uv=False)
    require(s[-1] >= (POLICY['overlap_floor'] if floor is None else floor),
            f'unresolved frame overlap: sigma_min={s[-1]:.6g}')
    if np.linalg.det(overlap) < 0:
        frame = frame.copy()
        frame[:, -1] *= -1
    return frame, float(s[-1])


def real_hamiltonian(m, U, k):
    H = finite(m.H(k), 'Hamiltonian')
    herm = float(np.max(np.abs(H-H.conj().T)))
    require(herm <= POLICY['hermitian_atol'], f'non-Hermitian H: {herm}')
    # O(D^2) exact block contraction for the project's canonical real basis.
    u2 = np.array([[1, 1j], [1, -1j]])/np.sqrt(2)
    if U is None:
        blocks = H.reshape(m.dim//2, 2, m.dim//2, 2)
        HR = np.einsum('ai,manb,bj->minj', u2.conj(), blocks, u2,
                       optimize=True).reshape(m.dim, m.dim)
    else:
        HR = U.conj().T @ H @ U
    imag = float(np.max(np.abs(HR.imag)))
    require(imag <= POLICY['real_atol'], f'C2zT real-basis residual {imag} meV')
    return HR.real, dict(real_residual=imag, hermitian_residual=herm)


def spectrum(m, k, lo, nb, U=None):
    H, diagnostics = real_hamiltonian(m, U, k)
    left, right = max(0, lo-1), min(m.dim-1, lo+nb)
    values, vectors = eigh(H, subset_by_index=(left, right))
    residual = np.max(np.abs(H@vectors-vectors*values))/max(1., np.max(np.abs(H)))
    require(residual <= POLICY['eigen_relative_tol'], f'eigen residual {residual}')
    require(np.max(np.abs(vectors.T@vectors-np.eye(len(values)))) < POLICY['orthogonal_atol'],
            'nonorthogonal eigenvectors')
    diagnostics['eigen_relative_residual'] = float(residual)
    return values, vectors, left, diagnostics


def selected_frame(values, vectors, first, lo, nb):
    j = lo-first
    require(0 <= j and j+nb <= len(values), 'selected bands out of range')
    gaps = []
    if j > 0: gaps.append(values[j]-values[j-1])
    if j+nb < len(values): gaps.append(values[j+nb]-values[j+nb-1])
    require(gaps and min(gaps) > POLICY['isolation_meV'],
            f'band group not isolated along sampled path: {gaps}')
    return vectors[:, j:j+nb], float(min(gaps))


def checked_frame(m, U, k, lo=None, nb=2):
    lo = m.dim//2-1 if lo is None else lo
    w, v, first, _ = spectrum(m, k, lo, nb, U)
    return selected_frame(w, v, first, lo, nb)[0]


def converged_winding(m, U, center, radius, npts, base, lo):
    canonical=np.kron(np.eye(m.dim//2),np.array([[1,1j],[1,-1j]])/np.sqrt(2))
    require(np.allclose(U,canonical,atol=1e-12,rtol=0), 'unsupported real-basis convention')
    measurement=Measurement(m)
    first=measurement.winding(center,radius,npts,base,lo)
    second=measurement.winding(center,radius,2*npts,base,lo)
    require(first['charge']==second['charge'], 'winding fails mesh convergence')
    start=np.asarray(center)+np.array([radius,0])
    end=np.asarray(center)+np.array([radius/2,0])
    smaller,_=measurement.transport([start,end],base,lo,2*npts)
    third=measurement.winding(center,radius/2,2*npts,smaller,lo)
    require(first['charge']==third['charge'], 'winding fails radius convergence')
    return second


def converged_cycle(m, lo, nb, axis, offset, npts, sewing):
    me=Measurement(m)
    first=me.cycle(lo,nb,axis,offset,npts,sewing)
    second=me.cycle(lo,nb,axis,offset,2*npts,sewing)
    require(first['sign']==second['sign'], 'cycle fails mesh convergence')
    return second


def euler_measurement(me, lo, nf1, nf2, sewing1, sewing2):
    """SO(2) Wilson-loop degree, only for an isolated orientable two-frame.

    Link polar factors remove contraction; each link retains its singular-value
    diagnostic. Closure sewing is tested at the actual reciprocal endpoint.
    """
    xcycle=me.cycle(lo,2,0,0,2*nf1,sewing1)
    require(xcycle['sign']==1,'Euler class undefined: nonorientable k1 cycle')
    phases=[]; loop_determinants=[]; previous=None; min_overlap=1.; gap=float('inf'); seams=[]
    for x in np.linspace(0,1,nf1,endpoint=False):
        frames=[]
        for y in np.linspace(0,1,nf2+1):
            fr,g=me.frame([x,y],lo);frames.append(fr);gap=min(gap,g)
        if previous is not None:frames[0],_=orient(previous,frames[0])
        previous=frames[0]
        W=np.eye(2)
        for a,b in zip(frames[:-1],frames[1:]):
            u,s,vt=np.linalg.svd(a.T@b);min_overlap=min(min_overlap,float(s[-1]))
            require(s[-1]>=POLICY['overlap_floor'],'Wilson link unresolved')
            W=W@(u@vt)
        sewn=sewing2@frames[0];u,s,vt=np.linalg.svd(frames[-1].T@sewn)
        require(s[-1]>=POLICY['seam_overlap_floor'],'Wilson sewing overlap unresolved')
        require(np.max(np.abs(sewn.T@sewn-np.eye(2)))<=POLICY['seam_norm_error'],'Wilson sewing norm loss')
        seams.append(float(s[-1]));W=W@(u@vt)
        loop_determinants.append(float(np.linalg.det(W)))
        require(np.linalg.det(W)>0,'Euler class undefined: nonorientable k2 cycle')
        phases.append(float(np.arctan2(W[1,0],W[0,0])))
    increments=np.angle(np.exp(1j*np.diff(phases+[phases[0]])))
    require(np.max(np.abs(increments))<np.pi/2,'Wilson phase sampling unresolved')
    value=float(np.sum(increments)/(2*np.pi));q=int(round(value))
    require(abs(value-q)<POLICY['integer_tol'],'Euler winding noninteger')
    return dict(euler=q,winding=value,phases=phases,loop_determinants=loop_determinants,min_overlap=min_overlap,
                min_external_gap=gap,min_seam_overlap=min(seams),k1_cycle=xcycle,
                max_phase_increment=float(np.max(np.abs(increments))))


def atomic_json(path, data):
    """Replace only after a complete finite JSON document has been flushed."""
    path = Path(path)
    text = json.dumps(data, indent=2, allow_nan=False)+'\n'
    fd, temporary = tempfile.mkstemp(prefix='.'+path.name+'.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(text); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def save_checkpoint(path, state):
    import scipy
    state = dict(state)
    state['_checkpoint'] = dict(schema=1, python=platform.python_version(),
                               numpy=np.__version__, scipy=scipy.__version__,
                               script=Path(__import__('sys').argv[0]).name,
                               policy=POLICY)
    atomic_json(path, state)


def load_checkpoint(path):
    with open(path) as stream: state=json.load(stream)
    require(isinstance(state, dict) and 'x' in state and 'step' in state,
            'invalid checkpoint structure')
    finite(state['x'], 'checkpoint parameters'); finite(state['step'], 'checkpoint step')
    require(state['step'] > 0, 'checkpoint step must be positive')
    meta=state.get('_checkpoint')
    if meta:
        import scipy, sys
        require(meta.get('script') == Path(sys.argv[0]).name, 'checkpoint belongs to another script')
        require(meta.get('numpy') == np.__version__ and meta.get('scipy') == scipy.__version__,
                'checkpoint dependency environment differs')
    return state


def refine_checked(f0, func, tol=1e-10, wrap=False, optimizer=None, bounds=None):
    from scipy.optimize import minimize
    finite(f0, 'refinement seed')
    optimizer = minimize if optimizer is None else optimizer
    def objective(x): return float(finite(func(np.asarray(x)), 'refinement objective'))
    options = dict(method='Nelder-Mead', options={'xatol':1e-7, 'fatol':tol, 'maxiter':600})
    if bounds is not None: options['bounds']=bounds
    result = optimizer(objective, np.asarray(f0, float), **options)
    info = dict(success=bool(result.success), status=int(result.status),
                message=str(result.message), nfev=int(result.nfev),
                raw_x=np.asarray(result.x).tolist(), raw_fun=float(result.fun))
    require(result.success, f'optimizer did not converge: {info}')
    x = np.asarray(result.x)
    finite(x, 'refined coordinates'); finite(result.fun, 'refined objective')
    value = objective(x)
    require(abs(value-result.fun) <= max(tol*10, 1e-8), 'optimizer value mismatch')
    if wrap:
        x = x % 1.0
        wrapped = objective(x)
        require(abs(wrapped-value) <= max(tol*10, 1e-8),
                f'wrapping changes objective: {value} -> {wrapped}')
        value = wrapped
    info.update(x=x.tolist(), fun=value, wrapped=wrap)
    return x, value, info


class Measurement:
    """Cached six-band frames with per-point symmetry/eigensolver evidence."""
    def __init__(self, model):
        self.model = model
        self.lo = model.dim//2-2
        self.cache = {}
        self.metrics = dict(real_residual=0., hermitian_residual=0., eigen_relative_residual=0.)

    def at(self, f):
        key = tuple(float(x) for x in f)
        if key not in self.cache:
            item = spectrum(self.model, self.model.frac_to_k(np.asarray(f)), self.lo, 4)
            for k, v in item[3].items(): self.metrics[k] = max(self.metrics[k], v)
            self.cache[key] = item
        return self.cache[key]

    def frame(self, f, lo, nb=2):
        w,v,first,_ = self.at(f)
        return selected_frame(w,v,first,lo,nb)

    def transport(self, points, base, lo, steps):
        prev=base; overlap=1.; gap=float('inf')
        for a,b in zip(points[:-1], points[1:]):
            for s in np.linspace(0,1,steps+1)[1:]:
                fr,g=self.frame(np.asarray(a)+s*(np.asarray(b)-a),lo)
                prev,sv=orient(prev,fr); overlap=min(overlap,sv); gap=min(gap,g)
        return prev, dict(min_overlap=overlap, min_external_gap=gap)

    def winding(self, center, radius, npts, base, lo):
        frames=[]; gap=float('inf'); internal=float('inf')
        for t in np.linspace(0,2*np.pi,npts+1):
            f=np.asarray(center)+radius*np.array([np.cos(t),np.sin(t)])
            fr,g=self.frame(f,lo); gap=min(gap,g); frames.append(fr)
            w,_,first,_=self.at(f); internal=min(internal,w[lo-first+1]-w[lo-first])
        require(internal > POLICY['isolation_meV'], 'loop touches its target degeneracy')
        e,sv=orient(base,frames[0]); e0=e.copy(); overlap=sv
        u=frames[0][:,0]; alpha=np.arctan2(e[:,1]@u,e[:,0]@u); total=0.
        for fr in frames[1:]:
            sv=float(np.linalg.svd(e.T@fr,compute_uv=False)[-1]); overlap=min(overlap,sv)
            require(sv >= POLICY['overlap_floor'], 'winding frame overlap unresolved')
            e=checked_qr(fr@(fr.T@e)); v=fr[:,0]
            require(abs(v@u) >= POLICY['overlap_floor'], 'eigenvector angular sampling unresolved')
            if v@u<0:v=-v
            u=v; angle=np.arctan2(e[:,1]@u,e[:,0]@u)
            total+=(angle-alpha+np.pi)%(2*np.pi)-np.pi; alpha=angle
        closing=e.T@e0
        require(np.linalg.det(closing)>0 and np.linalg.svd(closing,compute_uv=False)[-1]>.95,
                'contractible frame failed closure')
        hol=float(np.arctan2(closing[1,0],closing[0,0]))
        raw=float(total/np.pi); corrected=float((total-hol)/np.pi)
        charge=integer_charge(corrected)
        require(abs(charge)==1, 'loop does not resolve a simple unit-charge node')
        return dict(raw_winding=raw, frame_holonomy_pi=hol/np.pi,
                    corrected_winding=corrected, charge=charge,
                    min_overlap=overlap, min_external_gap=gap, min_internal_gap=internal)

    def cycle(self, lo, nb, axis, offset, npts, sewing):
        frames=[]; gap=float('inf'); overlap=1.
        for t in np.linspace(0,1,npts+1):
            f=np.array([t,offset]) if axis==0 else np.array([offset,t])
            fr,g=self.frame(f,lo,nb); frames.append(fr); gap=min(gap,g)
        previous=frames[0]
        for fr in frames[1:]:
            previous,sv=orient(previous,fr); overlap=min(overlap,sv)
        sewn=sewing@frames[0]
        norm_error=float(np.max(np.abs(sewn.T@sewn-np.eye(nb))))
        closure=previous.T@sewn; seam=float(np.linalg.svd(closure,compute_uv=False)[-1])
        determinant=float(np.linalg.det(closure))
        require(norm_error <= POLICY['seam_norm_error'], f'sewing loses norm: {norm_error}')
        require(seam >= POLICY['seam_overlap_floor'], f'poor sewing overlap: {seam}')
        return dict(sign=1 if determinant>0 else -1, determinant=determinant,
                    min_overlap=overlap, seam_overlap=seam, seam_norm_error=norm_error,
                    min_external_gap=gap)
