"""Bounded synthetic examples for the S0b derivation; no physical imports."""
from fractions import Fraction
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'certification_s0a_001'))
from primitives import enclosure, frobenius, identity, inertia_ldl, householder, synthetic_symmetric, midpoint_matrix
from flint import arb, arb_mat


def block(a, rows, cols):
    return arb_mat([[a[i, j] for j in cols] for i in rows])


def phase_budget(frame, seam, repair, extra):
    eps, eta = arb(frame), arb(seam)
    delta = 2*eps+eps*eps+(1+eps)**2*eta
    if not delta < 1:
        return {"observed": "INCONCLUSIVE", "delta": enclosure(delta)}
    angle = delta.asin()
    total = 4*angle+arb(repair)+arb(extra)
    radius = total/(2*arb.pi())
    return {"observed": "WITHIN_Q_BUDGET" if radius < arb('1/8') else "INCONCLUSIVE",
            "delta": enclosure(delta), "per_endpoint_angle": enclosure(angle),
            "total_phase_error": enclosure(total), "q_radius_bound": enclosure(radius)}


def controls(spec):
    l = spec['ledger']
    good = phase_budget(l['frame_error'], l['unrepaired_seam_map_error'], l['repair_angle_error'], l['total_additional_phase_error'])
    bad = phase_budget('1/4', l['unrepaired_seam_map_error'], l['repair_angle_error'], l['total_additional_phase_error'])
    # H(t)=diag(-1,t,2), t in [1/128,1/64]: zero is a valid separating
    # shift, but [-1/4,1/4] includes t and is not spectrum-free.
    t = arb('3/256', arb('1/256'))
    h = arb_mat([[-1,0,0],[0,t,0],[0,0,2]])
    mid = inertia_ldl(h)
    left = inertia_ldl(h+arb('1/4')*identity(3))
    right = inertia_ldl(h-arb('1/4')*identity(3))
    checks = {'phase_budget_pass':good['observed']=='WITHIN_Q_BUDGET',
              'phase_budget_refuses_loose_frames':bad['observed']=='INCONCLUSIVE',
              'single_shift_does_not_certify_window':mid.get('negative')==1 and left.get('negative')==1 and right.get('negative')==2}
    if not all(checks.values()):
        raise AssertionError('known-answer control failed')
    return {'status':'PASS','checks':checks,'accepted_ledger':good,'loose_ledger':bad,
            'single_shift':mid,'window_endpoints':[left,right]}


def cell_family(n):
    h, _, d = synthetic_symmetric(n)
    _, _, q = householder(n)
    e = arb_mat([[arb(((i%3)-1)*((j%5)-2))/(128*n) for j in range(n)] for i in range(n)])
    t = identity(n)+e
    t = arb_mat([[t[i,j]*(1+arb(1+j%3)/1024) for j in range(n)] for i in range(n)])
    v = q*t
    velocities = [arb((-1)**i)/4 for i in range(n)]
    qv = arb_mat([[q[i,j]*velocities[j] for j in range(n)] for i in range(n)])
    hx = qv*q.transpose()
    gram = v.transpose()*v
    return v.transpose()*h*v, v.transpose()*hx*v, gram, d


def uniform_shift(k0, kx, gram, d, width, shift):
    n = len(d)
    s = Fraction(shift)
    below = sorted([i for i in range(n) if d[i] < s], key=lambda i:(s-d[i],i))[:2]
    above = sorted([i for i in range(n) if d[i] > s], key=lambda i:(d[i]-s,i))[:2]
    selected = below+above
    other = [i for i in range(n) if i not in selected]
    kc = k0-arb(shift)*gram
    x = arb(0, arb(width))
    kw = kc+x*kx
    ac, dc = block(kc,selected,selected), block(kc,other,other)
    aw, dw, bw = block(kw,selected,selected), block(kw,other,other), block(kw,other,selected)
    bc = block(kc,other,selected)
    record = {'shift':shift,'selected_indices':selected,'selected_center_eigenvalues':[d[i] for i in selected],
              'center_B_F_bound':enclosure(frobenius(bc)),
              'expected_negative':sum(di < s for di in d)}
    inv_ball = dc.inv()
    r, _ = midpoint_matrix(inv_ball)
    qbound = frobenius(identity(len(other))-r*dw)
    record['inverse_residual_F_bound'] = enclosure(qbound)
    if not qbound < 1:
        return {**record,'status':'INCONCLUSIVE','reason':'COMPLEMENT_INVERSE_NOT_CERTIFIED'}
    di = inertia_ldl(dc)
    record['complement_inertia'] = di
    if di['status'] != 'PASS':
        return {**record,'status':'INCONCLUSIVE','reason':'CENTER_COMPLEMENT_INERTIA'}
    nu = frobenius(r)/(1-qbound)
    beta = frobenius(bw)
    a = frobenius(aw-ac)
    debit = beta*beta*nu
    # Each exact entry of B^T D^-1 B has magnitude <= ||B||_2^2 ||D^-1||_2.
    # Add its full upper endpoint to EVERY entry; correlations may be lost,
    # but every exact symmetric Schur complement is still enclosed.
    sw = arb_mat([[aw[i,j]+arb(0,debit.upper()) for j in range(len(selected))]
                   for i in range(len(selected))])
    si = inertia_ldl(sw)
    record.update({'inverse_norm_bound':enclosure(nu),'B_F_bound':enclosure(beta),
                   'direct_A_variation_bound':enclosure(a),'Schur_correction_bound':enclosure(debit),
                   'total_Schur_debit_bound':enclosure(a+debit),'small_inertia':si})
    if si['status'] != 'PASS':
        return {**record,'status':'INCONCLUSIVE','reason':'SCHUR_SIGN_NOT_CERTIFIED'}
    count = di['negative']+si['negative']
    if count != record['expected_negative']:
        raise AssertionError('certified count disagrees with prescribed center spectrum')
    return {**record,'status':'CERTIFIED_SHIFT','negative':count}


def cell(job, spec):
    k0,kx,gram,d = cell_family(job['dimension'])
    eta = frobenius(identity(len(d))-gram)
    if not eta < 1:
        raise ArithmeticError('preconditioner not certified invertible')
    shifts = [uniform_shift(k0,kx,gram,d,job['width'],s) for w in spec['windows'] for s in w]
    windows = []
    for i,w in enumerate(spec['windows']):
        a,b = shifts[2*i:2*i+2]
        ok = a['status']==b['status']=='CERTIFIED_SHIFT' and a['negative']==b['negative']
        windows.append({'endpoints':w,'status':'CERTIFIED_WINDOW' if ok else 'INCONCLUSIVE',
                        'negative':a.get('negative') if ok else None,
                        'guaranteed_gap_width':str(Fraction(w[1])-Fraction(w[0])) if ok else None,
                        'center_line_resolvent_distance':str((Fraction(w[1])-Fraction(w[0]))/2) if ok else None})
    observed = 'CERTIFIED_WINDOW_PAIR' if all(w['status']=='CERTIFIED_WINDOW' for w in windows) else 'INCONCLUSIVE'
    if observed != job['expected']:
        raise AssertionError('unexpected cell outcome: '+observed)
    return {'status':'PASS','observed':observed,'Gram_defect_F_bound':enclosure(eta),'shifts':shifts,'windows':windows}


def apply_blocks(e, f):
    return arb_mat([[sum((e[i%4,k]*f[i-i%4+k,j] for k in range(3)), arb(0)) if i%4<3 else f[i,j]
                     for j in range(2)] for i in range(f.nrows())])


def exact_rotation(t, x):
    a, b = 20*t+t*t/2+x*t, 3*t*t/2
    ca,sa,cb,sb = a.cos(),a.sin(),b.cos(),b.sin()
    return arb_mat([[ca,-sa*cb,sa*sb],[sa,ca*cb,-ca*sb],[0,sb,cb]])


def variable_transport(job, spec):
    n,steps = job['dimension'],job['steps']
    _,_,q = householder(n)
    f0 = arb_mat([[q[i,j] for j in range(2)] for i in range(n)])
    center,error = midpoint_matrix(f0)
    initial = error
    defect,rounding = arb(0),arb(0)
    h = arb(1)/steps
    # At x=0: ||A_t|| <= |a''|+|b''|+2|a'||b'| <= 1+3+126=130.
    for k in range(steps):
        tm = (arb(k)+arb('1/2'))/steps
        a = 20*tm+tm*tm/2
        ap,bp = 20+tm,3*tm
        s,c = a.sin(),a.cos()
        ac = arb_mat([[0,-ap,bp*s],[ap,0,-bp*c],[-bp*s,bp*c,0]])
        propagator = (h*ac).exp()
        debit = arb(130)*h*h*frobenius(center)/4
        y = apply_blocks(propagator,center)
        center,radius = midpoint_matrix(y)
        error += debit+radius
        defect += debit
        rounding += radius
    strip = arb(job['strip'])
    parameter = 7*strip*arb(2).sqrt()
    total = error+parameter
    threshold = arb(spec['ledger']['frame_error'])
    observed = 'WITHIN_FRAME_BUDGET' if total < threshold else 'INCONCLUSIVE'
    if observed != job['expected']:
        raise AssertionError('unexpected transport outcome: '+observed)
    checks = []
    for x in [-strip,arb(0),strip]:
        ref = apply_blocks(exact_rotation(arb(1),x),f0)
        discrepancy = frobenius(center-ref)
        if not discrepancy < total:
            raise AssertionError('known solution consistency check failed')
        checks.append({'x':enclosure(x),'endpoint_discrepancy_bound':enclosure(discrepancy)})
    return {'status':'PASS','observed':observed,'initial_error':enclosure(initial),
            'defect_sum_bound':enclosure(defect),'rounding_sum_bound':enclosure(rounding),
            'parameter_debit':enclosure(parameter),'total_error_bound':enclosure(total),
            'consistency_checks':checks,'generator_is_variable_and_noncommuting':True,
            'implementation_structure':'repeated 3x3 blocks with fourth coordinate fixed; no dense physical-generator timing claim'}
