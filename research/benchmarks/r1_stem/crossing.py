"""Conditional exact-Schur velocity and moving-segment crossing bounds."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT/'PLAN.json').read_text()); T = PLAN['thresholds']
sys.path.insert(0, str(ROOT.parent/'r1_continuation'))
from bounds import center_data, certificate, CFG
sys.path.insert(0, str(ROOT.parent/'r1_newton'))
from solver import solve
sys.path.insert(0, str(ROOT.parent/'r1_holonomy'))
from measure import Family
from track import model
sys.path.insert(0, str(ROOT.parent/'r1_attachment'))
from inputs import read_inputs

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load():
    cont, cases, sources = read_inputs()
    for folder, flag in [('r1_attachment', 'all_checks_pass'), ('r1_inventory', 'all_checks_pass')]:
        p = ROOT.parent/folder/'SUMMARY.json'; data = json.loads(p.read_text())
        assert data[flag]; sources[str(p.relative_to(ROOT.parent))] = sha(p)
        for n, h in data['source_hashes'].items():
            p = ROOT.parent/folder/n; assert sha(p) == h
            sources[str(p.relative_to(ROOT.parent))] = h
    return cont, cases, sources

def cross(a, b):
    return a[..., 0]*b[..., 1]-a[..., 1]*b[..., 0]

def bernstein(q):
    """Power coefficients in t in [0,1], converted without sampling."""
    return np.array([q[0], q[0]+q[1]/2, sum(q)])

def polynomial(a0, a1, b0, b1, product):
    return np.array([product(a0, b0), product(a1, b0)+product(a0, b1), product(a1, b1)])

def velocity_bound(raw, cert):
    if not cert['pass']:
        return {'pass': False}
    C = np.array(raw['C']); r = np.array(cert['radii'])
    B, G, q = cert['bfull'], cert['Gfull'], cert['q']
    nonlinear = 2*raw['cross_velocity']*B/G+B*B*raw['complement_velocity']/G**2
    residual = np.array(raw['gD'])+np.array(raw['J'])@raw['velocity']
    forcing = (np.abs(C@residual)+np.sum(abs(C), axis=1)*nonlinear)/r
    norm = float(max(forcing)/(1-q))
    vr = r*norm+T['derivative_allowance']
    return {'pass': True, 'nonlinear_D': float(nonlinear), 'scaled_forcing': forcing.tolist(),
            'scaled_velocity_radius': norm, 'velocity_radius': vr.tolist()}

def identity(raw, cert, parent_raw, parent_cert, a, b):
    if not cert['pass'] or not parent_cert['pass']:
        return {'pass': False}
    margins = []
    for D in [a, b]:
        c = np.array(raw['y'])+(D-raw['D_meV'])*np.array(raw['velocity'])
        p = np.array(parent_raw['y'])+(D-parent_raw['D_meV'])*np.array(parent_raw['velocity'])
        margins.append(np.array(parent_cert['radii'])-np.array(cert['radii'])-abs(c-p))
    return {'pass': bool(np.min(margins) > T['identity_margin']), 'margins': np.array(margins).tolist()}

def stem(case, a, b):
    mid = (a+b)/2
    g = case['geometry']
    j = next(j for j in range(len(g)-1) if g[j]['D_meV'] <= mid <= g[j+1]['D_meV'])
    left, right = g[j:j+2]
    assert a >= left['D_meV']-1e-13 and b <= right['D_meV']+1e-13
    x = np.array(left['vertices'])[[0, 2]]
    v = (np.array(right['vertices'])[[0, 2]]-x)/(right['D_meV']-left['D_meV'])
    return np.array([x+(D-left['D_meV'])*v for D in [a,b]]), v

def geometry(raw, cert, ends, velocities, a, b):
    """Bounds include node position and velocity errors, not fitted trajectories."""
    if not cert['pass']:
        return {'pass': False}
    vb = velocity_bound(raw, cert)
    pred = np.array([np.array(raw['y'][:2])+(D-raw['D_meV'])*np.array(raw['velocity'][:2]) for D in [a,b]])
    posr = np.array(cert['inner_radii'][:2]); vr = np.array(vb['velocity_radius'][:2])
    e = ends[:,1]-ends[:,0]; w = pred-ends[:,0]
    de, dw = e[1]-e[0], w[1]-w[0]
    qs = polynomial(e[0], de, w[0], dw, cross)
    qn = polynomial(e[0], de, w[0], dw, np.dot)
    ql = polynomial(e[0], de, e[0], de, np.dot)
    maxe = np.max(abs(e), axis=0)
    side_error = float(maxe[::-1]@posr+T['geometry_allowance'])
    bs = bernstein(qs); side = [float(min(bs)-side_error), float(max(bs)+side_error)]
    ep = velocities[1]-velocities[0]; wp = np.array(raw['velocity'][:2])-velocities[0]
    slopes = np.array([cross(ep, wi)+cross(ei,wp) for ei,wi in zip(e,w)])
    slope_error = float(abs(ep[::-1])@posr+maxe[::-1]@vr+T['derivative_allowance'])
    slope = [float(min(slopes)-slope_error), float(max(slopes)+slope_error)]
    bn, bl = bernstein(qn), bernstein(ql)
    dot_error = float(maxe@posr+T['geometry_allowance'])
    num = [float(min(bn)-dot_error),float(max(bn)+dot_error)]
    den = [float(min(bl)-T['geometry_allowance']),float(max(bl)+T['geometry_allowance'])]
    along = None if den[0] <= 0 else [float(min(n/d for n in num for d in den)),float(max(n/d for n in num for d in den))]
    return {'pass': bool(along is not None), 'side_coefficients':qs.tolist(), 'dot_coefficients':qn.tolist(),
            'length_coefficients':ql.tolist(), 'side_bernstein':bs.tolist(), 'side_error':side_error,
            'side_bounds':side, 'slope_predictor_endpoints':slopes.tolist(), 'slope_error':slope_error,
            'slope_bounds':slope, 'numerator_bounds':num, 'denominator_bounds':den, 'along_bounds':along,
            'velocity':vb}

def interval_newton(a,b,mid,side,slope):
    if slope[0] <= 0 <= slope[1]:
        return {'pass':False,'reason':'derivative_contains_zero'}
    candidates = [mid-s/d for s in side for d in slope]
    lo=max(a,min(candidates)-T['geometry_allowance']); hi=min(b,max(candidates)+T['geometry_allowance'])
    return {'pass':bool(lo <= hi), 'interval':[float(lo),float(hi)],'raw_candidates':candidates}
