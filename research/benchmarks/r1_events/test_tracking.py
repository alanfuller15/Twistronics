"""Controls for identity handling and an actual-model root/spectrum cross-check."""
import json
import unittest
import numpy as np
from scipy.linalg import eigh
from track import Solver,match,ROOT

class TrackingControls(unittest.TestCase):
 def test_permutation_keeps_identities(self):
    prev=[{'f':[.2,.2],'track':4},{'f':[.8,.8],'track':7}]
    cur,_,info=match(prev,[{'f':[.79,.8]},{'f':[.21,.2]}],8)
    self.assertEqual([x['track'] for x in cur],[7,4]);self.assertFalse(info['unmatched_previous'])
 def test_far_root_is_not_forced_to_match(self):
    cur,_,info=match([{'f':[.2,.2],'track':4}],[{'f':[.8,.8]}],5)
    self.assertEqual(cur[0]['track'],5);self.assertEqual(info['unmatched_previous'],[4])
 def test_close_alternatives_are_flagged(self):
    _,_,info=match([{'f':[.2,.2],'track':4}],[{'f':[.19,.2]},{'f':[.21,.2]}],5)
    self.assertTrue(info['links'][0]['ambiguous'])
 def test_known_root_against_native_spectrum(self):
    old=json.loads((ROOT.parent/'r1_reproduction'/'CROSSING.json').read_text())
    old=next(x for x in old['rows'] if x['N']==4 and x['engine']=='bm' and x['D_meV']==38)
    s=Solver(4,'bm',38);root=s.root([.7704,.6288],'upper')
    self.assertTrue(root['accepted']);self.assertLess(np.linalg.norm(np.array(root['f'])-old['upper']),1e-7)
    direct=eigh(s.m.H(s.mon.k(np.array(root['f']))),eigvals_only=True,subset_by_index=(s.lo,s.lo+5))
    self.assertLess(np.max(np.abs(direct-s.eig(root['f']))),1e-8)
    self.assertLess(direct[4]-direct[3],1e-6)

if __name__=='__main__':unittest.main(verbosity=2)
