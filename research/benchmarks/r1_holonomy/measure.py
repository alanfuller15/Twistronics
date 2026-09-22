"""Closed real-frame holonomy with guarded adaptive affine edges.

This is a contour diagnostic, not a full braid acceptance gate.
All O(2) polar factors retain reflections; no determinant is forced positive.
"""
from pathlib import Path
from types import SimpleNamespace
import sys, json, hashlib
import numpy as np
from scipy.linalg import eigh

ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT / 'PLAN.json').read_text())
T = P['thresholds']
sys.path.insert(0, str(ROOT.parent / 'r1_events'))
from track import Solver, model, Monitor
from bm_strain import segment_geometry

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def polar(a):
    u, s, vt = np.linalg.svd(a, full_matrices=False)
    return u @ vt, s

class Family:
    def __init__(self, engine):
        self.engine = engine
        self.models = {D: model(engine, P['N'], D) for D in [38., 38.5, 39.]}
        m = self.models[38.]
        mon = Monitor(m, engine)
        self.U, self.k, self.lo, self.dim = mon.U, mon.k, mon.lo, m.dim
        self.h0 = mon.h0
        self.A = [m.G1[0]*mon.hx + m.G1[1]*mon.hy, m.G2[0]*mon.hx + m.G2[1]*mon.hy]
        hD = self.U.conj().T @ (self.models[39.].H(np.zeros(2)) - m.H(np.zeros(2))) @ self.U
        if np.abs(hD.imag).max() > T['affine_matrix_meV']:
            raise RuntimeError('D derivative is not real')
        self.A.append(hD.real)
        self.checks = []
        self.cache = {}
        self.maximum_frame_orthogonality_error = 0.
        self.edge_norms = {}
        for D, f in [(38., [.47,.74]), (38., [.88,.59]), (38.5,[.77,.63]), (39.,[.47,.74]), (39.,[.88,.59])]:
            native = self.models[D].H(self.k(np.array(f)))
            direct = self.U.conj().T @ native @ self.U
            affine = self.H([*f,D])
            matrix_error = float(np.abs(direct-affine).max())
            w = eigh(native, eigvals_only=True, subset_by_index=(self.lo-1,self.lo+2))
            v = eigh(affine, eigvals_only=True, subset_by_index=(self.lo-1,self.lo+2))
            spectrum_error = float(np.abs(w-v).max())
            self.checks.append({'D_meV':D,'f':f,'matrix_error_meV':matrix_error,'spectrum_error_meV':spectrum_error})
            if matrix_error > T['affine_matrix_meV'] or spectrum_error > T['native_spectrum_meV']:
                raise RuntimeError('Affine family does not match native Hamiltonian')

    def H(self, v):
        return self.h0 + v[0]*self.A[0] + v[1]*self.A[1] + (v[2]-38.)*self.A[2]

    def data(self, v):
        key = tuple(map(float,v))
        if key not in self.cache:
            w, F = eigh(self.H(v), subset_by_index=(self.lo-1,self.lo+2))
            error=float(np.max(np.abs(F[:,1:3].T@F[:,1:3]-np.eye(2))))
            self.maximum_frame_orthogonality_error=max(self.maximum_frame_orthogonality_error,error)
            if not np.isfinite(w).all() or not np.isfinite(F).all() or error>T['orthogonality_tolerance']:
                raise RuntimeError('Invalid eigenframe')
            self.cache[key] = (F[:,1:3], float(min(w[1]-w[0],w[3]-w[2])))
        return self.cache[key]

    def edge_norm(self, a, b):
        delta = np.asarray(b)-a
        key = tuple(map(float,delta))
        if key not in self.edge_norms:
            matrix = sum(delta[j]*self.A[j] for j in range(3))
            self.edge_norms[key] = float(np.abs(eigh(matrix,eigvals_only=True)).max())
        return self.edge_norms[key]

    def solver(self, D):
        # Solver.root/eig are unchanged; this adapter supplies the verified
        # affine family in fractional coordinates at the requested D.
        s = Solver.__new__(Solver)
        s.lo = self.lo-2
        s.mon = SimpleNamespace(k=lambda f: np.asarray(f), hr=lambda f: self.H([*f,D]))
        return s

def edge(family, a, b, cfg):
    a, b = np.asarray(a,float), np.asarray(b,float)
    norm = family.edge_norm(a,b)
    samples, leaves = {}, []
    def get(t):
        if t not in samples:
            v = a.copy() if t == 0 else b.copy() if t == 1 else a+t*(b-a)
            F,g = family.data(v)
            samples[t] = (v,F,g)
        return samples[t]
    def visit(l,r,depth):
        vl,Fl,gl = get(l)
        vr,Fr,gr = get(r)
        variation = norm*(r-l)
        lower = min(gl,gr)-variation-T['floating_allowance_meV']
        smin = float(np.linalg.svd(Fl.T@Fr,compute_uv=False).min())
        ok = (lower>T['exterior_gap_margin_meV'] and
              variation/lower<=cfg['variation_over_lower_gap_max'] and smin>=cfg['target_step_smin'])
        if ok or min(gl,gr)<=T['exterior_gap_margin_meV'] or depth>=T['max_depth']:
            leaves.append({'a':l,'b':r,'depth':depth,'lower_estimate_meV':lower,
                           'variation_meV':variation,'step_smin':smin,'resolved':bool(ok)})
            return
        mid=(l+r)/2
        visit(l,mid,depth+1)
        visit(mid,r,depth+1)
    grid=np.linspace(0,1,cfg['initial_subintervals']+1)
    for l,r in zip(grid[:-1],grid[1:]):
        visit(float(l),float(r),0)
    used=sorted({x['a'] for x in leaves}|{x['b'] for x in leaves})
    nodes=[get(t) for t in used]
    report={'start':a.tolist(),'end':b.tolist(),'Hamiltonian_variation_norm_meV':norm,
            'pass':all(x['resolved'] for x in leaves),'leaves':leaves,
            'samples':[{'t':t,'v':get(t)[0].tolist(),'exterior_gap_meV':get(t)[2]} for t in sorted(samples)]}
    return report,nodes

def matrix_product(frames):
    W=np.eye(2)
    links=[]
    for a,b in zip(frames[:-1],frames[1:]):
        Q,s=polar(a.T@b)
        W=W@Q
        links.append({'Q':Q.tolist(),'singular_values':s.tolist()})
    return W,links

def closed_loop(family, vertices, cfg):
    vertices=np.asarray(vertices,float)
    if not np.array_equal(vertices[0],vertices[-1]):
        raise ValueError('Loop must close exactly in declared coordinates')
    edges=[];nodes=[]
    for a,b in zip(vertices[:-1],vertices[1:]):
        r,points=edge(family,a,b,cfg)
        edges.append(r)
        nodes.extend(points if not nodes else points[1:])
    frames=[x[1] for x in nodes]
    W,links=matrix_product(frames)
    E=frames[0].copy()
    for F in frames[1:]:
        E,_=polar(F@(F.T@E))
    closure=frames[0].T@E
    reverse,_=matrix_product(list(reversed(frames)))
    rng=np.random.default_rng(P['gauge_seed'])
    gauges=[]
    for _ in frames[:-1]:
        theta=rng.uniform(-np.pi,np.pi)
        G=np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
        if rng.integers(2):G[:,1]*=-1
        gauges.append(G)
    gauges.append(gauges[0])
    gauged,_=matrix_product([F@G for F,G in zip(frames,gauges)])
    errors={'projector_vs_overlap':float(np.max(np.abs(closure-W.T))),
            'reversal':float(np.max(np.abs(reverse-W.T))),
            'gauge_covariance':float(np.max(np.abs(gauged-gauges[0].T@W@gauges[0]))),
            'holonomy_orthogonality':float(np.max(np.abs(W.T@W-np.eye(2)))),
            'closure_subspace':float(np.max(np.abs(frames[-1]@frames[-1].T-frames[0]@frames[0].T)))}
    valid=all(x['pass'] for x in edges) and all(v<T['holonomy_tolerance'] for v in errors.values())
    det=float(np.linalg.det(W));valid=valid and abs(abs(det)-1)<T['holonomy_tolerance']
    report={'mesh':cfg['name'],'vertices':vertices.tolist(),'sample_points':len(nodes),
            'edges':edges,'links':links,'holonomy_matrix':W.tolist(),'determinant':det,
            'accepted_sign':int(np.sign(det)) if valid else None,'diagnostics_pass':bool(valid),
            'minimum_step_smin':min(x['step_smin'] for e in edges for x in e['leaves']),
            'minimum_isolation_lower_meV':min(x['lower_estimate_meV'] for e in edges for x in e['leaves']),
            'maximum_variation_over_lower_gap':max(x['variation_meV']/x['lower_estimate_meV'] for e in edges for x in e['leaves'] if x['lower_estimate_meV']>0),
            'cross_checks':errors,'gauge_seed':P['gauge_seed']}
    return report

def continue_nodes(family, parent, intervals, on_station=None):
    seeds=[x['f'] for x in parent['crossing']['evaluations'][0]['flat']]
    seeds.append(parent['crossing']['evaluations'][0]['upper']['f'])
    rows=[];aligned={};minimum_overlap=1.
    for j,D in enumerate(np.linspace(38.,39.,intervals+1)):
        s=family.solver(float(D))
        roots=[s.root(seed,'flat' if n<2 else 'upper') for n,seed in enumerate(seeds)]
        for seed,r in zip(seeds,roots):
            r['step_distance']=float(np.linalg.norm(np.asarray(r['f'])-seed))
        if not all(r['accepted'] and r['step_distance']<P['root_max_step'] for r in roots):
            raise RuntimeError('Root continuation gate failed: '+json.dumps({'D':D,'roots':roots}))
        if np.linalg.norm(np.array(roots[0]['f'])-roots[1]['f'])<P['minimum_flat_pair_separation']:
            raise RuntimeError('Flat nodes no longer separated')
        t,off,_=segment_geometry(roots[0]['f'],roots[1]['f'],roots[2]['f'])
        row={'D_meV':float(D),'roots':roots,'upper_geometry':{'t':float(t),'normal_offset':float(off)},'temporal_step_smin':[]}
        for n in [0,1]:
            F,_=family.data([*roots[n]['f'],D])
            if j:
                Q,singular=polar(F.T@aligned[(j-1,n)])
                F=F@Q
                minimum_overlap=min(minimum_overlap,float(singular.min()))
                row['temporal_step_smin'].append(float(singular.min()))
            aligned[(j,n)]=F
        rows.append(row);seeds=[r['f'] for r in roots]
        if on_station is not None:on_station(rows)
    return {'intervals':intervals,'stations':rows,'minimum_temporal_step_smin':minimum_overlap,
            'temporal_conditioning_pass':minimum_overlap>=P['temporal_step_smin']},aligned

def static_vertices(station,r):
    p,q=[np.array(x['f']) for x in station['roots']]
    d=(q-p+.5)%1-.5;q=p+d;off=1.5*r*d/np.linalg.norm(d)
    pts=[p+[r,0],q+[r,0],q+off,p-off,p+[r,0]]
    return [list(x)+[station['D_meV']] for x in pts]

def ribbon_vertices(track,shift):
    p=[[*((np.array(s['roots'][0]['f'])+shift).tolist()),s['D_meV']] for s in track['stations']]
    q=[[*((np.array(s['roots'][1]['f'])+shift).tolist()),s['D_meV']] for s in track['stations']]
    return [p[0],*q,*list(reversed(p))]
