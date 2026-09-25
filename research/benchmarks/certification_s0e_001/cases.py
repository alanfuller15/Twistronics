"""Fixed S0e controls; no physical inputs."""
from flint import arb, arb_mat
from certified import (continuous_phase_lift, seam_map, polar_so2, finite_growth,
                       composition_admissibility, certified_boundary)
from primitives import identity


def phase(offset, radius):
    total = 2*arb.pi()+arb(offset)
    return [[arb((total*k/16).cos(), arb(radius)),
             arb((total*k/16).sin(), arb(radius))] for k in range(17)]


def clean(result):
    return {k:v for k,v in result.items() if not k.startswith('_')}


def run(job, spec):
    kind = job['id']
    if kind.startswith('phase_'):
        radius = '1/1048576' if kind != 'phase_wide' else '1/16'
        offset = '1/100' if kind == 'phase_open' else '0'
        return continuous_phase_lift(phase(offset,radius), '0', '1/2' if kind=='phase_wide' else '1/64',
                  exact_closure_declared=kind!='phase_unbound', variation_certified=True)
    if kind.startswith('seam_'):
        # A genuine partial shift with one discarded ambient coordinate.
        # F0's second column leaks into that coordinate, while F0 stays orthonormal.
        c = arb('24/25' if kind=='seam_deletion_pass' else '9/10' if kind=='seam_deletion_fail' else '1')
        s = (1-c*c).sqrt()
        left=arb_mat([[1,0],[0,1],[0,0]])
        right=arb_mat([[1,0],[0,c],[0,s]])
        shift=arb_mat([[1,0,0],[0,1,0],[0,0,0]])
        return seam_map(left,shift,right,'1/16','1/128')
    if kind=='polar_negative':
        return clean(polar_so2(arb_mat([[2,0],[0,-1]]),'1/128'))
    if kind.startswith('growth_'):
        return finite_growth(kind.split('_')[1])
    if kind.startswith('composition_'):
        records={k:{'status':'CERTIFIED','reason':v} for k,v in
            {'projector':'RIESZ_PROJECTOR_ENCLOSURE','seam':'PARTIAL_SHIFT_SEAM_ENCLOSURE','lift':'CONTINUOUS_PHASE_LIFT'}.items()}
        if kind=='composition_budget':
            records['lift']['reason']='BUDGET_CONDITIONALLY_SUFFICIENT'
        return composition_admissibility(records)
    if kind=='shape_error':
        return seam_map(identity(2), identity(3), identity(2),'1/16','1/128')
    if kind=='unrelated_error':
        @certified_boundary
        def unrelated():
            raise ArithmeticError('nonfinite bound')
        return unrelated()
    raise ValueError('unknown fixed control')
