"""Analytic positive control and a missed-by-grid crossing for adaptive isolation."""
from validate import bound_intervals

def main():
    # Eigenvalues of diag(-(t-c), t-c) cross between the initial sample points.
    c=0.413501
    crossing=bound_intervals(lambda t:2*abs(t-c),2.)
    assert not crossing['pass'], 'must reject a crossing missed by the initial grid'
    # diag(-sqrt((t-c)^2+a^2), +sqrt(...)): minimum gap = 2a = 0.04.
    a=.02
    import math
    avoided=bound_intervals(lambda t:2*math.sqrt((t-c)**2+a*a),2.)
    assert avoided['pass']
    assert .001 < avoided['min_lower_estimate_meV'] <= 2*a
    limited=bound_intervals(lambda t:.02,2.,maxdepth=0)
    assert not limited['pass'], 'exhausting depth must not silently certify'
    print('3 analytic isolation controls passed; unresolved depth is rejected.')
if __name__=='__main__':main()
