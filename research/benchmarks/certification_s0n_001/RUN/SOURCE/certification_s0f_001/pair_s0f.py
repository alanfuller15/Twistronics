"""Conditional synthetic certification primitives; no physical model imports.

Matrix balls must enclose the declared continuous exact symmetric family on
a connected cell and its center. Congruence provenance is a caller obligation.
All norms below use Frobenius bounds as sufficient operator-norm bounds.
"""
from fractions import Fraction
from pathlib import Path
import sys
from primitives_s0f import enclosure, frobenius, identity, inertia_ldl, midpoint_matrix
from flint import arb, arb_mat


def block(a, rows, cols):
    return arb_mat([[a[i, j] for j in cols] for i in rows])


def ledger(frame, seam, repair, extra, target):
    values = [Fraction(v) for v in (frame, seam, repair, extra, target)]
    if any(v < 0 for v in values) or values[-1] == 0:
        raise ValueError('finite nonnegative errors and positive target required')
    eps, eta, rho, additional, qtarget = map(arb, (frame, seam, repair, extra, target))
    endpoint = 2*eps+eps**2+(1+eps)**2*eta
    two_maps = 2*eta+eta**2
    four_maps = two_maps*(2+two_maps)
    corner = 2*eps+eps**2+(1+eps)**2*four_maps
    record = {'endpoint_matrix_error':enclosure(endpoint),
              'four_map_error':enclosure(four_maps), 'corner_matrix_error':enclosure(corner)}
    if not endpoint < 1 or not corner < 1:
        return {**record, 'status':'INCONCLUSIVE', 'reason':'ANGLE_DISK_NOT_SEPARATED'}
    endpoint_angle, corner_angle = endpoint.asin(), corner.asin()
    radius = (4*endpoint_angle+rho+additional)/(2*arb.pi())
    record.update({'endpoint_angle_bound':enclosure(endpoint_angle),
                   'corner_angle_bound':enclosure(corner_angle), 'q_radius_bound':enclosure(radius),
                   'repair_allowance':repair, 'q_target':target})
    if not corner_angle < rho:
        return {**record, 'status':'INCONCLUSIVE', 'reason':'CORNER_ALLOWANCE_NOT_JUSTIFIED'}
    if not radius < qtarget:
        return {**record, 'status':'INCONCLUSIVE', 'reason':'Q_BUDGET_NOT_CERTIFIED'}
    return {**record, 'status':'CERTIFIED', 'reason':'CONDITIONAL_ERROR_BUDGET'}


def certify_shift(kcenter, kcell, selected):
    n = kcenter.nrows()
    if kcenter.ncols()!=n or kcell.nrows()!=n or kcell.ncols()!=n:
        raise ValueError('equal square dimensions required')
    if not 0<len(selected)<n or len(set(selected))!=len(selected) or any(type(i) is not int or not 0<=i<n for i in selected):
        raise ValueError('proper distinct selected indices required')
    if any(not a[i,j].is_finite() for a in (kcenter,kcell) for i in range(n) for j in range(n)):
        raise ValueError('finite matrix enclosures required')
    other = [i for i in range(n) if i not in selected]
    dc, dw = block(kcenter,other,other), block(kcell,other,other)
    ac, aw = block(kcenter,selected,selected), block(kcell,selected,selected)
    bc, bw = block(kcenter,other,selected), block(kcell,other,selected)
    record = {'selected_indices':selected, 'center_B_F_bound':enclosure(frobenius(bc))}
    # Catch only the numerical inability to certify this particular inverse.
    # Shape, schema and unrelated arithmetic/backend faults remain exceptions.
    try:
        enclosed_inverse = dc.inv()
    except ZeroDivisionError:
        return {**record,'status':'INCONCLUSIVE','reason':'COMPLEMENT_INVERSE_NOT_CERTIFIED'}
    r, _ = midpoint_matrix(enclosed_inverse)
    q = frobenius(identity(len(other))-r*dw)
    record['inverse_residual_F_bound'] = enclosure(q)
    if not q < 1:
        return {**record,'status':'INCONCLUSIVE','reason':'COMPLEMENT_RESIDUAL_NOT_CERTIFIED'}
    di = inertia_ldl(dc)
    record['complement_inertia'] = di
    if di['status']!='PASS':
        return {**record,'status':'INCONCLUSIVE','reason':'CENTER_COMPLEMENT_INERTIA'}
    nu, beta = frobenius(r)/(1-q), frobenius(bw)
    debit = beta**2*nu
    variation = frobenius(aw-ac)
    sw = arb_mat([[aw[i,j]+arb(0,debit.upper()) for j in range(len(selected))]
                  for i in range(len(selected))])
    si = inertia_ldl(sw)
    record.update({'inverse_norm_bound':enclosure(nu), 'B_F_bound':enclosure(beta),
                   'Schur_correction_bound':enclosure(debit),
                   'direct_A_variation_bound':enclosure(variation),
                   'total_Schur_debit_bound':enclosure(variation+debit), 'small_inertia':si})
    if si['status']!='PASS':
        return {**record,'status':'INCONCLUSIVE','reason':'SCHUR_SIGN_NOT_CERTIFIED'}
    return {**record,'status':'CERTIFIED','reason':'SHIFT_INERTIA',
            'negative':di['negative']+si['negative']}


def match_window(left, right, endpoints, required_count):
    lo, hi = map(Fraction,endpoints)
    if not lo < hi or type(required_count) is not int or required_count < 0:
        raise ValueError('ordered window and nonnegative integer count required')
    r = {'endpoints':endpoints, 'required_count':required_count}
    if left['status']!='CERTIFIED' or right['status']!='CERTIFIED':
        return {**r,'status':'INCONCLUSIVE','reason':'WINDOW_ENDPOINT_NOT_CERTIFIED'}
    r['endpoint_counts'] = [left['negative'],right['negative']]
    if left['negative']!=right['negative']:
        return {**r,'status':'INCONCLUSIVE','reason':'WINDOW_COUNTS_DIFFER'}
    r['spectrum_free_window'] = True
    if left['negative']!=required_count:
        return {**r,'status':'INCONCLUSIVE','reason':'DECLARED_INDEX_NOT_CERTIFIED'}
    return {**r,'status':'CERTIFIED','reason':'DECLARED_INDEX_WINDOW',
            'guaranteed_gap_width':str(hi-lo),'center_line_resolvent_distance':str((hi-lo)/2)}


def certify_pair(k0, kx, gram, width, windows, selections, pair):
    n = k0.nrows()
    if any(a.nrows()!=n or a.ncols()!=n for a in (k0,kx,gram)):
        raise ValueError('equal square dimensions required')
    if len(pair)!=2 or any(type(i) is not int for i in pair) or not 0<pair[0]<pair[1]<n-1 or pair[1]!=pair[0]+1:
        raise ValueError('declared pair must have both external neighbors')
    if len(windows)!=2 or len(selections)!=4 or Fraction(width)<0:
        raise ValueError('two windows, four selections and nonnegative width required')
    if not Fraction(windows[0][1]) < Fraction(windows[1][0]):
        raise ValueError('lower window must precede upper window')
    eta = frobenius(identity(n)-gram)
    record = {'dimension':n, 'declared_pair':pair, 'required_counts':[pair[0],pair[1]+1],
              'Gram_defect_F_bound':enclosure(eta)}
    if not eta < 1:
        return {**record,'status':'INCONCLUSIVE','reason':'BASIS_NOT_CERTIFIED'}
    shifts=[]
    for i,s in enumerate(v for w in windows for v in w):
        kc = k0-arb(s)*gram
        kw = kc+arb(0,arb(width))*kx
        shifts.append({'shift':s,**certify_shift(kc,kw,selections[i])})
    checks=[match_window(shifts[2*i],shifts[2*i+1],windows[i],record['required_counts'][i]) for i in range(2)]
    record.update({'shifts':shifts,'windows':checks})
    if all(w['status']=='CERTIFIED' for w in checks):
        return {**record,'status':'CERTIFIED','reason':'DECLARED_PAIR_WINDOWS'}
    reason='DECLARED_INDEX_NOT_CERTIFIED' if any(w['reason']=='DECLARED_INDEX_NOT_CERTIFIED' for w in checks) else 'PAIR_WINDOWS_NOT_CERTIFIED'
    return {**record,'status':'INCONCLUSIVE','reason':reason}
