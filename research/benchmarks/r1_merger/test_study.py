"""Analytic controls plus a native-model affine/root cross-check."""
import unittest,json
import numpy as np
from study import fold_metrics,phase_index,hessian,Local,ROOT
class StudyControls(unittest.TestCase):
 def test_fold_direction_and_coefficients(self):
    m=fold_metrics(lambda f,D:np.array([f[0]**2+D,f[1]]),np.zeros(2),0.,1e-4,1e-4)
    self.assertLess(m['singular_value_ratio'],1e-10)
    self.assertTrue(m['roots_on_lower_D_side'])
    self.assertAlmostEqual(m['separation_squared_slope'],-4.)
 def test_opposite_local_indices(self):
    t=np.arange(128)*2*np.pi/128
    for sign in (-1,1):
      w,step=phase_index(np.array([np.cos(t),sign*np.sin(t)]).T)
      self.assertAlmostEqual(w,sign);self.assertLess(step,.06)
 def test_positive_gap_hessian_after_analytic_fold(self):
    H=hessian(lambda f:(f[0]**2+.01)**2+f[1]**2,np.zeros(2),1e-5)
    np.testing.assert_allclose(H,np.diag([.04,2]),atol=1e-7)
 def test_native_model_root(self):
    local=Local(4,'bm');p=json.loads((ROOT.parent/'r1_events'/'N4.json').read_text())
    row=next(x for x in p['stations'] if x['engine']=='bm' and x['D_meV']==40.)
    old=next(x for x in row['gaps']['upper']['roots'] if x['track']==1)
    r=local.root([.774,.616],40.)
    self.assertTrue(r['accepted']);self.assertLess(np.linalg.norm(np.array(r['f'])-old['f']),1e-7)
    self.assertLess(abs(np.linalg.norm(local.fun(r['f'],40.))-r['gap_meV']),1e-9)
if __name__=='__main__':unittest.main(verbosity=2)
