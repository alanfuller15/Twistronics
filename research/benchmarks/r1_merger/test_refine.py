"""Check eigenvalue derivatives against a direct gap finite difference."""
import unittest
import numpy as np
from refine import Local,gap_gradient
class GradientControl(unittest.TestCase):
 def test_eigenvalue_gradient_matches_direct_gap(self):
    m=Local(4,'bm');f=np.array([.779,.6075]);D=40.5;h=1e-7
    gap=lambda x:float(np.diff(m.eig(x,D)[3:5])[0])
    finite=np.array([(gap(f+e*h)-gap(f-e*h))/(2*h) for e in np.eye(2)])
    np.testing.assert_allclose(gap_gradient(m,f,D),finite,rtol=1e-5,atol=1e-5)
if __name__=='__main__':unittest.main(verbosity=2)
