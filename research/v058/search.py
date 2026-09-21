"""Finite chart search with retained attempts; no global or continuum proof."""
import numpy as np
from scipy.optimize import minimize, minimize_scalar
from evidence import require


def projected_gradient(x, gradient):
    x, g = np.asarray(x, float), np.asarray(gradient, float).copy()
    g[(x <= 1e-9) & (g > 0)] = 0
    g[(x >= 1-1e-9) & (g < 0)] = 0
    return float(np.max(np.abs(g)))


def checked(fn, x):
    x = np.asarray(x, float)
    require(x.shape == (2,) and np.isfinite(x).all() and np.all(x >= 0) and np.all(x <= 1), 'invalid chart point')
    v, g = fn(x)
    require(np.isfinite(v) and np.asarray(g).shape == (2,) and np.isfinite(g).all(), 'nonfinite objective')
    return float(v), np.asarray(g, float)


def refine(fn, seed, thresholds):
    seed = np.asarray(seed, float); initial, _ = checked(fn, seed); attempts = []
    for method in ['L-BFGS-B', 'SLSQP', 'Nelder-Mead']:
        options = dict(ftol=1e-14, gtol=1e-8, maxiter=300, maxls=40) if method == 'L-BFGS-B' else dict(ftol=1e-13, maxiter=500) if method == 'SLSQP' else dict(xatol=1e-10, fatol=1e-12, maxiter=1000)
        sol = minimize((lambda x: checked(fn, x)[0]) if method == 'Nelder-Mead' else (lambda x: checked(fn, x)), seed,
                       method=method, jac=False if method == 'Nelder-Mead' else True, bounds=[(0,1),(0,1)], options=options)
        finite = bool(np.isfinite(sol.x).all() and np.isfinite(sol.fun))
        inside = finite and bool(np.all(sol.x >= 0) and np.all(sol.x <= 1))
        value, gradient = checked(fn, sol.x) if inside else (None, None)
        pg = projected_gradient(sol.x, gradient) if inside else None
        valid = bool(sol.success and inside and abs(value-float(sol.fun)) <= thresholds['value_consistency'] and value <= initial+thresholds['nonworsening'] and pg <= thresholds['projected_gradient'])
        attempts.append(dict(method=method, success=bool(sol.success), status=int(sol.status), message=str(sol.message), nfev=int(sol.nfev), nit=int(sol.nit),
                             f=sol.x.tolist() if finite else None, optimizer_value=float(sol.fun) if finite else None, checked_value=value,
                             projected_gradient=pg, valid=valid))
        if valid:
            return dict(seed=seed.tolist(), initial=initial, f=sol.x.tolist(), gap=value, gradient=gradient.tolist(), projected_gradient=pg, attempts=attempts)
    error = ValueError('all optimizer attempts rejected'); error.attempts = attempts; error.seed = seed.tolist(); raise error


def edge_search(fn, n, thresholds):
    rows = []
    for axis in [0,1]:
        moving = 1-axis
        for fixed in [0.,1.]:
            def point(t):
                x=np.zeros(2); x[axis]=fixed; x[moving]=t; return x
            ts=np.linspace(0,1,n+1); values=[checked(fn,point(t))[0] for t in ts]
            candidates=[dict(f=point(t).tolist(),gap=values[i],kind='corner') for i,t in [(0,0.),(n,1.)]]
            for j in range(1,n):
                if values[j] > min(values[j-1],values[j+1]): continue
                sol=minimize_scalar(lambda t:checked(fn,point(t))[0],bounds=(ts[j-1],ts[j+1]),method='bounded',options=dict(xatol=1e-12,maxiter=300))
                valid=bool(sol.success and np.isfinite(sol.fun) and np.isfinite(sol.x) and ts[j-1] <= sol.x <= ts[j+1] and sol.fun <= values[j]+thresholds['nonworsening'])
                record=dict(kind='optimized',success=bool(sol.success),status=int(sol.status),message=str(sol.message),nfev=int(sol.nfev),
                            bracket=[float(ts[j-1]),float(ts[j+1])],f=point(sol.x).tolist() if np.isfinite(sol.x) else None,gap=float(sol.fun) if np.isfinite(sol.fun) else None,valid=valid)
                if not valid:
                    error=ValueError('edge optimization rejected');error.attempts=[record];raise error
                candidates.append(record)
            best=min(candidates,key=lambda x:x['gap']);require(best['gap'] <= min(values)+thresholds['nonworsening'],'edge result worsens grid')
            rows.append(dict(axis=axis,fixed=fixed,values=values,minimum=best,candidates=candidates))
    return dict(segments=n,edges=rows,minimum=min(x['minimum']['gap'] for x in rows))


def curvature(fn, x, h):
    x=np.asarray(x,float);require(np.min(np.minimum(x,1-x)) > h,'selected minimum too near boundary for interior curvature check')
    columns=[]
    for axis in [0,1]:
        d=np.eye(2)[axis]*h;columns.append((checked(fn,x+d)[1]-checked(fn,x-d)[1])/(2*h))
    matrix=np.array(columns).T; eig=np.linalg.eigvalsh((matrix+matrix.T)/2)
    return dict(step=h,eigenvalues=eig.tolist(),asymmetry=float(np.max(np.abs(matrix-matrix.T))))


def search(fn, grid, edge_grid, anchors, thresholds):
    axis=np.linspace(0,1,grid+1); values=np.array([[checked(fn,[x,y])[0] for y in axis] for x in axis])
    seeds=list(anchors)
    for i,x in enumerate(axis):
        for j,y in enumerate(axis):
            if values[i,j] <= values[max(0,i-1):min(grid+1,i+2),max(0,j-1):min(grid+1,j+2)].min():seeds.append([x,y])
    edge=edge_search(fn,edge_grid,thresholds)
    for row in edge['edges']:
        for candidate in row['candidates']:
            f=np.array(candidate['f']);seeds.extend([f,np.clip(f,.002,.998)])
    seeds.extend([[x,y] for x in [0.,.5,1.] for y in [0.,.5,1.]])
    seeds=[list(x) for x in sorted(set(tuple(np.asarray(x,float)) for x in seeds))]
    results=[]
    for seed in seeds:
        try: results.append(refine(fn,seed,thresholds))
        except Exception as error:
            error.completed_refinements=results;error.boundary=edge;raise
    best=min(results,key=lambda x:x['gap']);require(best['gap'] <= min(values.min(),edge['minimum'])+thresholds['nonworsening'],'selected result worsens sample')
    curves=[curvature(fn,best['f'],h) for h in thresholds['curvature_steps']]
    require(all(min(c['eigenvalues']) > 0 for c in curves),'selected minimum fails positive curvature')
    return dict(grid=grid,grid_values=values.tolist(),grid_min=float(values.min()),boundary=edge,refinements=results,minimum=best,curvature=curves)


def acceptance(trials, thresholds):
    require(len(trials)==2,'two search meshes required')
    values=[r['minimum']['gap'] for r in trials];edges=[r['boundary']['minimum'] for r in trials]
    require(np.isfinite(values+edges).all() and min(values+edges)>thresholds['positive_gap'],'nonpositive or unresolved sampled gap')
    require(abs(values[1]-values[0]) <= thresholds['mesh_gap'],'interior mesh disagreement')
    require(abs(edges[1]-edges[0]) <= thresholds['mesh_gap'],'edge mesh disagreement')
    return dict(status='ACCEPT_SAMPLED_GAP',gap=min(values),mesh_difference=abs(values[1]-values[0]),boundary_minimum=min(edges),boundary_mesh_difference=abs(edges[1]-edges[0]))
