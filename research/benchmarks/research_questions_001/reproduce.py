"""Bounded reference-bundle and spectral diagnostics; not a TBG braid calculation.

No network, source mutations, subprocesses or production model changes. Writes
only to a new caller-selected output directory. A failed predicate exits 1.
"""
import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path

import numpy as np

I3 = np.eye(3)


def texture(x, y, m):
    d = np.array([np.sin(x), np.sin(y), m + np.cos(x) + np.cos(y)])
    norm = np.linalg.norm(d)
    if norm < 1e-12:
        raise ValueError("undefined normal: unflattened gap closure")
    return d / norm


def frame(n):
    # Local charts chosen from three Cartesian reference axes. Not one global frame.
    axis = int(np.argmin(np.abs(n)))
    a = I3[axis]
    e1 = a - np.dot(a, n) * n
    e1 /= np.linalg.norm(e1)
    return np.column_stack((e1, np.cross(n, e1))), axis


def rotation(a):
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


def loop(frames):
    w = np.eye(2)
    smin = 1.
    for a, b in zip(frames, np.roll(frames, -1, axis=0)):
        u, s, vt = np.linalg.svd(a.T @ b)
        smin = min(smin, float(s[-1]))
        if s[-1] < 1e-8:
            raise ValueError("singular frame overlap")
        w = w @ (u @ vt)  # retain O(2): never silently force det=+1
    return w, smin


def so_angle(w):
    if np.linalg.det(w) < 0:
        raise ValueError("nonorientable loop: SO(2) angle refused")
    return float(np.arctan2(w[1, 0], w[0, 0]))


def require_resolved(curve):
    if curve['max_phase_step'] >= np.pi/2:
        raise ValueError("phase increments exceed the fixed pi/2 resolution criterion")
    return curve['winding']


def sphere_triangle(a, b, c):
    return 2 * np.arctan2(np.dot(a, np.cross(b, c)),
                         1 + np.dot(a, b) + np.dot(b, c) + np.dot(c, a))


def degree(ns, other_diagonal=False):
    total = 0.
    size = len(ns)
    for i in range(size):
        for j in range(size):
            a, b = ns[i, j], ns[(i+1) % size, j]
            c, d = ns[(i+1) % size, (j+1) % size], ns[i, (j+1) % size]
            triangles = ((a,b,d), (b,c,d)) if other_diagonal else ((a,b,c), (a,c,d))
            total += sum(sphere_triangle(*t) for t in triangles)
    return float(total / (4*np.pi))


def wilson_curve(size, m, orientation=1, gauge=False):
    ks = np.linspace(-np.pi, np.pi, size, endpoint=False)
    angles, overlap, dets = [], 1., []
    for y in np.r_[ks, ks[0]]:
        fs = []
        for x in ks:
            f, _ = frame(orientation * texture(x, y, m))
            if gauge:
                f = f @ rotation(1.7*np.sin(2*x) + .8*np.cos(3*y))
            fs.append(f)
        w, sm = loop(np.array(fs))
        overlap = min(overlap, sm)
        dets.append(float(np.linalg.det(w)))
        angles.append(so_angle(w))
    lifted = np.unwrap(angles)
    return {"winding": float((lifted[-1]-lifted[0])/(2*np.pi)),
            "min_overlap_singular_value": overlap,
            "max_phase_step": float(np.max(np.abs(np.diff(lifted)))),
            "max_det_error": float(np.max(np.abs(np.array(dets)-1))),
            "ky": np.r_[ks, np.pi].tolist(),
            "phase": lifted.tolist()}


def spectral(h, energy, eta):
    es, vs = np.linalg.eigh(h)
    weights = eta / (np.pi * ((energy-es)**2 + eta**2))
    return (vs * weights) @ vs.conj().T


def main(out):
    out.mkdir(parents=True, exist_ok=False)
    checks = []
    def check(name, value, target=0., tol=1e-10):
        ok = bool(np.isfinite(value) and abs(value-target) <= tol)
        checks.append(dict(name=name, value=float(value), target=float(target), tolerance=tol, passed=ok))
    def refused(name, fn):
        try:
            fn()
        except ValueError as e:
            checks.append(dict(name=name, passed=True, rejection=str(e)))
        else:
            checks.append(dict(name=name, passed=False, rejection=None))

    rows, curves = [], {}
    for m, expected in [(-1, 1), (-3, 0)]:
        for size in [48, 96]:
            ks = np.linspace(-np.pi, np.pi, size, endpoint=False)
            ns = np.array([[texture(x, y, m) for y in ks] for x in ks])
            deg, alt = degree(ns), degree(ns, True)
            wc = wilson_curve(size, m)
            row = dict(m=m, mesh=size, degree=deg, other_diagonal_degree=alt,
                       euler_from_degree=2*deg, **{k:v for k,v in wc.items() if k not in ('ky','phase')})
            rows.append(row)
            check(f"m{m}_mesh{size}_degree", deg, expected)
            check(f"m{m}_mesh{size}_other_diagonal", alt, expected)
            check(f"m{m}_mesh{size}_Wilson_winding", wc['winding'], 2*expected)
            check(f"m{m}_mesh{size}_Wilson_det", wc['max_det_error'])
            checks.append(dict(name=f"m{m}_mesh{size}_phase_resolution",passed=wc['max_phase_step']<np.pi/2,
                               value=wc['max_phase_step'],upper_bound=float(np.pi/2)))
            if size==96:curves[str(m)]=wc

    refused("coarse_mesh_24_phase_resolution_rejected",lambda:require_resolved(wilson_curve(24,-1)))

    normal = wilson_curve(48, -1)
    gauged = wilson_curve(48, -1, gauge=True)
    flipped = wilson_curve(48, -1, orientation=-1)
    check("SO2_gauge_curve", np.max(np.abs(np.exp(1j*np.array(normal['phase']))-np.exp(1j*np.array(gauged['phase'])))))
    check("normal_reversal_flips_Euler", flipped['winding'], -2)
    ks = np.linspace(-np.pi, np.pi, 96, endpoint=False)
    fs = np.array([frame(texture(x,.37,-1))[0] for x in ks])
    w,_ = loop(fs)
    wb,_ = loop(np.roll(fs,17,axis=0))
    wr,_ = loop(fs[::-1])
    check("base_point_shift",np.max(np.abs(w-wb)))
    check("reverse_loop",np.max(np.abs(wr-w.T)))
    n=texture(.23,-.17,-1)
    check("normal_reversal_same_H",np.max(np.abs((2*np.outer(n,n)-I3)-(2*np.outer(-n,-n)-I3))))

    # Explicit sphere north/south chart transition on the equator.
    # Each smooth polar chart is regular at its own pole, not the other one.
    angles=[]
    for phi in np.linspace(0,2*np.pi,193):
        e_theta=np.array([0.,0.,-1.])
        e_phi=np.array([-np.sin(phi),np.cos(phi),0.])
        e=np.column_stack((e_theta,e_phi))
        north=e@rotation(-phi);south=e@rotation(phi)
        angles.append(so_angle(north.T@south))
    patch_winding=float((np.unwrap(angles)[-1]-np.unwrap(angles)[0])/(2*np.pi))
    check("sphere_chart_transition_winding",patch_winding,2.)

    ts=np.linspace(0,2*np.pi,201,endpoint=False)
    mobius_frames=np.array([np.column_stack(([-np.sin(t/2),np.cos(t/2),0],[0,0,1])) for t in ts])
    mw,ms=loop(mobius_frames)
    check("Mobius_holonomy_det",np.linalg.det(mw),-1.)
    refused("Mobius_SO2_phase_rejected",lambda:so_angle(mw))
    refused("undefined_normal_m_minus2_rejected",lambda:texture(0,0,-2))

    # The two reference models are pointwise isospectral, but their projectors differ.
    # Units here are dimensionless; eta is an illustrative broadening, not a fit.
    p=np.diag([1.,0.,0.]);eta=.08
    energy=np.linspace(-2,2,401)
    n1=texture(np.pi/2,0,-1);n0=texture(np.pi/2,0,-3)
    h1=2*np.outer(n1,n1)-I3;h0=2*np.outer(n0,n0)-I3
    curves_s={"energy":energy.tolist(),"eta":eta,"k":[float(np.pi/2),0.],"units":"dimensionless"}
    for label,h in [('euler2',h1),('euler0',h0)]:
        aa=np.array([spectral(h,e,eta) for e in energy])
        curves_s[label+'_trace']=np.trace(aa,axis1=1,axis2=2).real.tolist()
        curves_s[label+'_probe']=np.einsum('ij,eji->e',p,aa).real.tolist()
    trace_diff=float(np.max(np.abs(np.array(curves_s['euler2_trace'])-curves_s['euler0_trace'])) )
    probe_diff=float(np.max(np.abs(np.array(curves_s['euler2_probe'])-curves_s['euler0_probe'])) )
    check("isospectral_trace_equal",trace_diff)
    checks.append(dict(name="fixed_orbital_probe_distinguishes_reference_pair",value=probe_diff,lower_bound=1.,passed=probe_diff>1.))
    # A k-dependent passive change of representation also obeys covariance.
    cov_res,wrong_res=0.,0.
    for x,y in [(.23,-.17),(1.,.4),(-.7,1.3)]:
        n=texture(x,y,-1);h=2*np.outer(n,n)-I3
        angle=.7*np.sin(x)+.4*np.cos(y)
        u=np.eye(3);u[:2,:2]=rotation(angle)
        a=spectral(h,-.8,eta);at=spectral(u@h@u.T,-.8,eta)
        cov_res=max(cov_res,abs(np.trace(p@a)-np.trace((u@p@u.T)@at)))
        wrong_res=max(wrong_res,abs(np.trace(p@a)-np.trace(p@at)))
    check("k_dependent_covariant_probe",cov_res)
    checks.append(dict(name="untransformed_probe_control_detected",value=float(wrong_res),lower_bound=.01,passed=wrong_res>.01))
    # A coherent projector distinguishes relative phases even at one momentum.
    plus=np.array([1.,1.])/np.sqrt(2);minus=np.array([1.,-1.])/np.sqrt(2)
    pp=np.outer(plus,plus);rho_plus=pp;rho_minus=np.outer(minus,minus)
    check("relative_phase_same_diagonal",np.max(np.abs(np.diag(rho_plus)-np.diag(rho_minus))))
    check("coherent_probe_relative_phase_contrast",np.trace(pp@rho_plus)-np.trace(pp@rho_minus),1.)

    # Existing unmodified projected model: finite diagnostic points, both Q signs.
    model_path=Path(__file__).resolve().parents[1]/'vafek_2025'/'model.py'
    spec=importlib.util.spec_from_file_location('retained_vafek_model',model_path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    model=module.Model();swap=np.kron(module.X,module.X)
    probe=np.diag([1.,0.,0.,0.]);cov_probe=swap@probe@swap.T
    vafek=[]
    for k in [(.23,-.17),(.4,.31),(-.21,.37)]:
        hp=model.h(k,.5);hm=model.h(k,-.5)
        dp=model.direct_projection(k,.5);dm=model.direct_projection(k,-.5)
        energy=float(np.linalg.eigvalsh(hp)[1]);eta_meV=.2
        ap=spectral(hp,energy,eta_meV);am=spectral(hm,energy,eta_meV)
        bp=spectral(dp,energy,eta_meV);bm=spectral(dm,energy,eta_meV)
        row={"k":list(k),"Q_values":[-.5,.5],"energy_meV":energy,"eta_meV":eta_meV,
             "matrix_Q_reversal_residual_meV":float(np.max(np.abs(swap@hp@swap.T-dm))),
             "same_Q_gap_difference_meV":float(np.max(np.abs(np.diff(np.linalg.eigvalsh(hp))-np.diff(np.linalg.eigvalsh(dp))))),
             "Q_symmetric_trace_difference":float(abs(np.trace(ap+am)-np.trace(bp+bm))),
             "Q_symmetric_fixed_probe_difference":float(abs(np.trace(probe@(ap+am))-np.trace(probe@(bp+bm)))),
             "Q_symmetric_covariant_probe_difference":float(abs(np.trace(probe@(ap+am))-np.trace(cov_probe@(bp+bm))))}
        vafek.append(row)
        check(f"vafek_{k}_matrix_Q_reversal",row['matrix_Q_reversal_residual_meV'])
        check(f"vafek_{k}_symmetric_trace",row['Q_symmetric_trace_difference'])
        check(f"vafek_{k}_symmetric_covariant_probe",row['Q_symmetric_covariant_probe_difference'])
    check("vafek_retained_same_Q_gap_witness",vafek[0]['same_Q_gap_difference_meV'],1.5320713555991716,1e-9)
    fixed_contrast=max(r['Q_symmetric_fixed_probe_difference'] for r in vafek)
    checks.append(dict(name="Q_symmetric_fixed_probe_not_guaranteed_equal",value=fixed_contrast,lower_bound=1e-5,passed=fixed_contrast>1e-5))
    for c in checks:c['passed']=bool(c['passed'])

    result={"schema":"twistronics.reference-questions.v1","scope":"Synthetic reference models, not TBG or braid validation",
            "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "environment":{"python":platform.python_version(),"numpy":np.__version__},
            "orientation":"dkx wedge dky; e1 cross e2 = n = d/|d|; W = product polar(F_i^T F_next)",
            "bundle_results":rows,"wilson_curves":curves,"sphere_chart_transition_winding":patch_winding,
            "mobius":{"determinant":float(np.linalg.det(mw)),"external_gap":2.,"min_link_singular_value":ms},
            "spectral":{"trace_max_difference":trace_diff,"probe_max_difference":probe_diff,"covariant_probe_residual":float(cov_res),"untransformed_probe_difference":float(wrong_res)},
            "vafek_fixed_points":vafek,"retained_model_sha256":hashlib.sha256(model_path.read_bytes()).hexdigest(),
            "checks":checks,"passed":all(c['passed'] for c in checks)}
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (out/'SPECTRAL_CURVES.json').write_text(json.dumps(curves_s,indent=2,allow_nan=False)+'\n')
    print(json.dumps({"passed":result['passed'],"checks":len(checks),"failed":[c for c in checks if not c['passed']],"bundle_results":rows,"spectral":result['spectral'],"mobius":result['mobius']},indent=2))
    return 0 if result['passed'] else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    raise SystemExit(main(parser.parse_args().output.resolve()))
