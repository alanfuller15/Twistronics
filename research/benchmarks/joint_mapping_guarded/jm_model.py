"""Exploratory measurements with explicit finite bases and evaluated root returns."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
from scipy.linalg import eigh

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'joint_mapping_review'))
from inputs import originals
ORIGINAL = originals()
from bm_strain import BM, segment_geometry
from tbg_ref import TBG
from fast_engine import RealEngine, realify
sys.path.insert(0, str(ROOT.parent / 'r1_newton'))
from solver import solve, DEFAULT as SOLVER_DEFAULT

KNOBS = ('eps', 'phi', 'theta', 'D', 'P')
MODEL = dict(kinetic='lab_nn_full', geometry='exact', tunnelling='constant',
             nu=.16, beta=3.14, w1_scale_meV=110., w0_scale_meV=88.,
             D_convention='opposite layer potentials +/-D meV')

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def sources():
    paths = [ROOT / n for n in ('jm_model.py', 'jm_sweep.py', 'jm_trace.py')]
    paths += [ROOT.parent / 'r1_newton' / n for n in ('solver.py', 'PLAN.json')]
    paths += [ROOT.parent / 'joint_mapping_review' / n for n in
              ('inputs.py', 'PLAN.json', 'INPUT_MANIFEST.json', 'partner_joint_mapping.zip')]
    return {str(p.relative_to(ROOT.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths}

def state(x):
    if set(x) != set(KNOBS):
        raise ValueError('state requires exactly eps, phi, theta, D, P')
    x = {k: float(x[k]) for k in KNOBS}
    if not np.isfinite(list(x.values())).all() or x['theta'] <= 0 or x['P'] <= 0:
        raise ValueError('nonfinite or unsupported state')
    return x

def indices_checked(indices):
    a = np.asarray(indices)
    if a.ndim != 2 or a.shape[1] != 2 or len(a) < 3 or not np.isfinite(a).all():
        raise ValueError('invalid reciprocal-index set')
    if not np.equal(a, np.floor(a)).all():
        raise ValueError('reciprocal indices must be integers')
    pairs = [tuple(map(int, p)) for p in a]
    if pairs != sorted(set(pairs)) or (0, 0) not in pairs:
        raise ValueError('indices must be sorted, unique and contain origin')
    if any((-m, -n) not in set(pairs) for m, n in pairs):
        raise ValueError('index set must be inversion symmetric')
    return [list(p) for p in pairs]

def config(raw=None):
    defaults = dict(N=4, engine='bm', indices=None, cutoff_tol=1e-6,
                    root_radius=.02, gap_tol=1e-8, matrix_tol=1e-9,
                    segment_margin=1e-5, separation_min=1e-3, solver=dict(SOLVER_DEFAULT))
    raw = raw or {}
    if set(raw) - set(defaults):
        raise ValueError('unknown model/solver setting')
    c = dict(defaults, **raw)
    if isinstance(c['N'], bool) or int(c['N']) != c['N'] or c['N'] < 1:
        raise ValueError('N must be a positive integer')
    c['N'] = int(c['N'])
    if c['engine'] not in ('bm', 'ref'):
        raise ValueError('unknown engine')
    if c['indices'] is not None:
        c['indices'] = indices_checked(c['indices'])
    if set(c['solver']) - set(SOLVER_DEFAULT):
        raise ValueError('unknown root solver setting')
    c['solver'] = dict(SOLVER_DEFAULT, **c['solver'])
    for k,v in c['solver'].items():
        if not np.isfinite(v) or v < 0:
            raise ValueError('invalid solver setting '+k)
    for k in ('newton_iterations','backtracking_steps','fallback_max_nfev'):
        if int(c['solver'][k]) != c['solver'][k]:
            raise ValueError('solver budget must be integer')
    for k in ('cutoff_tol', 'root_radius', 'gap_tol', 'matrix_tol', 'segment_margin', 'separation_min'):
        if not np.isfinite(c[k]) or c[k] <= 0:
            raise ValueError('invalid setting ' + k)
    if c['segment_margin'] >= .5:
        raise ValueError('invalid interior margin')
    canonical(c)
    return c

def build(x, c):
    """Rebuild each native assembly after replacing all basis-dependent fields."""
    x = state(x)
    kw = dict(N=c['N'], w1=110*x['P'], eps=x['eps'], Dfield=x['D'],
              kinetic=MODEL['kinetic'], cutoff_tol=c['cutoff_tol'])
    if c['engine'] == 'bm':
        m = BM(theta_deg=x['theta'], phi_deg=x['phi'], ratio=.8, geometry='exact', **kw)
    else:
        m = TBG(theta=x['theta'], phi=x['phi'], w0=88*x['P'], **kw)
    radial = [list(p) for p in (m.idx if c['engine'] == 'bm' else m.mn)]
    if c['indices'] is not None:
        pairs = [tuple(p) for p in c['indices']]
        m.nG, m.dim = len(pairs), 4*len(pairs)
        if c['engine'] == 'bm':
            m.idx = pairs; m.pos = {p: i for i, p in enumerate(pairs)}
            m.Gvec = np.array([a*m.G1+b*m.G2 for a, b in pairs])
            m._build_static()
        else:
            m.mn = pairs; m.ix = {p: i for i, p in enumerate(pairs)}
            m.Gv = np.array([a*m.G1+b*m.G2 for a, b in pairs])
            m._static()
    return m, radial

class Family:
    def __init__(self, x, cfg):
        self.x, self.cfg = state(x), config(cfg)
        self.m, self.radial = build(self.x, self.cfg)
        self.dim = self.m.dim
        self.indices = [list(p) for p in (self.m.idx if self.cfg['engine'] == 'bm' else self.m.mn)]
        self.real = RealEngine(self.m)
        self.h0 = self.real.HR([0., 0.])
        self.A = [self.real.HR([1., 0.])-self.h0, self.real.HR([0., 1.])-self.h0,
                  np.diag(np.r_[np.ones(self.dim//2), -np.ones(self.dim//2)])]
        self.native_models = {self.x['D']: self.m}

    def H(self, v):
        return self.h0+v[0]*self.A[0]+v[1]*self.A[1]+(v[2]-self.x['D'])*self.A[2]

    def native_check(self, D, f, lo):
        if D not in self.native_models:
            self.native_models[D] = build(dict(self.x, D=D), self.cfg)[0]
        m = self.native_models[D]
        k = m.frac_to_k(f) if self.cfg['engine'] == 'bm' else m.k(f)
        H = m.H(k); affine = self.H([*f, D])
        w = eigh(H, eigvals_only=True, subset_by_index=(lo-1, lo+2))
        wr = eigh(affine, eigvals_only=True, subset_by_index=(lo-1, lo+2))
        matrix_error = float(np.max(abs(realify(H)-affine)))
        spectrum_error = float(np.max(abs(w-wr)))
        gap = float(w[2]-w[1])
        return dict(gap_meV=gap, w4=w.tolist(), matrix_error_meV=matrix_error,
                    spectrum_error_meV=spectrum_error, eigensolves=2,
                    ok=bool(gap <= self.cfg['gap_tol'] and
                            matrix_error <= self.cfg['matrix_tol'] and
                            spectrum_error <= self.cfg['matrix_tol']))

def image_shifts(roots):
    p, q, u = np.asarray(roots)
    return np.array([-np.floor(q-p+.5), -np.floor(u-p+.5)], int).tolist()

def measure(x, seeds, cfg, family=None):
    """Fixed seed boxes and image choices constrain searches, not prove identity."""
    x, c = state(x), config(cfg)
    family = family or Family(x, c)
    if c != family.cfg or any(x[k] != family.x[k] for k in KNOBS if k != 'D'):
        raise ValueError('measurement/family mismatch')
    seed_roots = np.asarray([*seeds['flat'], seeds['node']], float)
    out = dict(ok=False, x=x, roots=[], native=[], cost=0, reason=None,
               basis=digest(family.indices), dimension=family.dim)
    if seed_roots.shape != (3, 2) or not np.isfinite(seed_roots).all():
        out['reason'] = 'invalid_seeds'; return out
    if seeds.get('gap', 'upper') not in ('upper', 'lower'):
        out['reason'] = 'invalid_adjacent_gap'; return out
    los = [family.dim//2-1]*2 + [family.dim//2 if seeds.get('gap', 'upper') == 'upper' else family.dim//2-2]
    try:
        for s, lo in zip(seed_roots, los):
            box = [np.maximum(s-c['root_radius'], 0), np.minimum(s+c['root_radius'], 1)]
            r = solve(family, x['D'], lo, s, box=box, config=c['solver'])
            out['roots'].append(r); out['cost'] += r['eigensolves']
            if not r['accepted']:
                out['reason'] = 'root_rejected'; return out
            check = family.native_check(x['D'], np.asarray(r['f']), lo)
            out['native'].append(check); out['cost'] += check['eigensolves']
            if not check['ok']:
                out['reason'] = 'native_check_rejected'; return out
        f = np.array([r['f'] for r in out['roots']])
        t, off, sep = segment_geometry(*f)
        out.update(t=float(t), offset=float(off), sep=float(sep), image_shifts=image_shifts(f),
                   flat=f[:2].tolist(), node=f[2].tolist(),
                   seeds=dict(flat=f[:2].tolist(), node=f[2].tolist(), gap=seeds.get('gap', 'upper')))
        # Disjoint flat-root boxes prevent exchanging their labels in this solve.
        disjoint = bool(np.any(abs(seed_roots[1]-seed_roots[0]) > 2*c['root_radius']))
        out['ok'] = bool(disjoint and sep > c['separation_min'] and image_shifts(f) == image_shifts(seed_roots))
        out['reason'] = 'sampled_roots_pass' if out['ok'] else 'separation_or_image_guard'
    except Exception as e:
        out.update(reason='measurement_exception', error=repr(e), cost_complete=False)
    return out

def survey(x, cfg, grid=24, keep=10, tracked=None, local_grid=0):
    """Merge explicit carried seeds, grid minima and an optional segment strip.

    All returned roots are evaluated in [0,1]^2; no modulo wrapping is used.
    A successful search is not a complete node inventory.
    """
    c = config(cfg); family = Family(x, c); x = state(x)
    rec = dict(status='ok', x=x, config=c, basis=digest(family.indices), dimension=family.dim,
               candidates={}, attempts=[], grid_eigensolves=0, cost=0,
               completeness='not_established')
    fs = np.linspace(0, 1, grid, endpoint=False)
    for gap, lo in [('flat', family.dim//2-1), ('upper', family.dim//2), ('lower', family.dim//2-2)]:
        values = np.empty((grid, grid)); seeds = []
        for i, a in enumerate(fs):
            for j, b in enumerate(fs):
                w = eigh(family.H([a,b,x['D']]), eigvals_only=True, subset_by_index=(lo,lo+1))
                values[i,j] = w[1]-w[0]; rec['grid_eigensolves'] += 1
        minima = sorted((values[i,j], i, j) for i in range(grid) for j in range(grid)
                        if values[i,j] <= np.min(values[max(0,i-1):i+2,max(0,j-1):j+2]))[:keep]
        seeds += [('grid', [float(fs[i]),float(fs[j])]) for _,i,j in minima]
        seeds += [('tracked', s) for s in (tracked or {}).get(gap, [])]
        if gap != 'flat' and local_grid and len(rec['candidates']['flat']) == 2:
            p,q = np.array(rec['candidates']['flat']); d = q-p
            if np.linalg.norm(d) > c['separation_min']:
                normal = np.array([-d[1],d[0]])/np.linalg.norm(d)
                seeds += [('segment_strip', (p+t*d+o*normal).tolist())
                          for t in np.linspace(0,1,local_grid)
                          for o in [-c['root_radius']/2, 0., c['root_radius']/2]
                          if np.all((p+t*d+o*normal >= 0) & (p+t*d+o*normal <= 1))]
        found = []
        for source, s in seeds:
            r = solve(family, x['D'], lo, s, config=c['solver'],
                      box=[np.maximum(np.array(s)-c['root_radius'],0), np.minimum(np.array(s)+c['root_radius'],1)])
            a = dict(gap=gap, source=source, root=r, native=None, accepted=False)
            rec['attempts'].append(a); rec['cost'] += r['eigensolves']
            if r['accepted']:
                a['native'] = family.native_check(x['D'], np.array(r['f']), lo)
                rec['cost'] += a['native']['eigensolves']; a['accepted'] = a['native']['ok']
                if a['accepted'] and all(np.linalg.norm(np.array(r['f'])-f) > 1e-5 for f in found):
                    found.append(r['f'])
        rec['candidates'][gap] = found
    rec['cost'] += rec['grid_eigensolves']
    return rec
