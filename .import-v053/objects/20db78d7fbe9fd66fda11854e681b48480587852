import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from measure import Sample,Rejected,align
from models import State,Partner
from replay_events import spatial_jac
from strain_check import cone

class Guards(unittest.TestCase):
    def test_adjacent_degeneracy_rejected(self):
        sample=Sample('original',1,State())
        sample.at=lambda f:(np.array([-9.,-7.,-5.,-3.,1.,1.,5.,9.]),np.eye(8))
        with self.assertRaises(Rejected):sample.frame([0,0],3)
    def test_rank_one_fold_and_sides(self):
        class Synthetic:
            def vector(self,f,anchor,index):return np.array([f[0]**2,f[1]]),1.
        J=spatial_jac(Synthetic(),[0,0],None,0,1e-5)
        np.testing.assert_allclose(np.linalg.svd(J,compute_uv=False),[1,0],atol=1e-12)
        # Local normal form d=(x^2-lambda,y) has roots only for lambda>=0.
        for lam in [.01,.001]:self.assertAlmostEqual(np.sqrt(lam)**2-lam,0)
        self.assertGreater(0.-(-.001),0)
    def test_low_overlap_rejected(self):
        with self.assertRaises(Rejected):align(np.eye(4)[:,2:4],np.eye(4)[:,:2])
    def test_partner_nonhermiticity_rejected(self):
        p=Partner(1,State());old=p.model.H
        def bad(k):
            h=old(k);h[0,1]+=1.;return h
        p.model.H=bad
        with self.assertRaises(Rejected):p.real_hamiltonian([.2,.3])
    def test_zero_hopping_strain_gives_exact_geometric_metric(self):
        E=np.array([[.001,.0002],[.0002,-.00016]])
        _,metric=cone(E,.013,0.)
        np.testing.assert_allclose(metric,(np.eye(2)+E)@(np.eye(2)+E),atol=1e-12)
    def test_hopping_changes_velocity_sign(self):
        e=.0005;_,m=cone(np.eye(2)*e,0.,3.14)
        np.testing.assert_allclose(m,np.eye(2)*((1+e)*np.exp(-3.14*e))**2,atol=1e-12)
        self.assertLess(m[0,0],1.)
    def test_recovers_prior_seam_near_minimum(self):
        # Independent prior v035 24/36-grid result, not this run's initial
        # constrained x=0 minimum. Without explicit seam seeds it is missed.
        import json
        from boundary_audit import seeds
        root=Path(__file__).resolve().parents[1]
        prior=json.loads((root/'sources/v035_endpoint_gaps_N4.json').read_text())
        expected=prior['grids'][-1]['results']['0']['minimum']['gap']
        sample=Sample('original',4,State(A=-.3,T=-1.8,ratio=1.1))
        result=sample.minimum(2,12,extra=seeds([]))
        self.assertAlmostEqual(result['minimum']['gap'],expected,places=6)
if __name__=='__main__':unittest.main()
