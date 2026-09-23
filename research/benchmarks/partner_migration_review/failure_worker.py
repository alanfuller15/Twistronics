"""Explicit synthetic release controls; none is a graphene result.

The original consumer/metamorphic source is unchanged. Runtime substitutions
force specific failure paths cheaply; they are never used in numerical replay.
"""
import runpy
import sys
from pathlib import Path
import numpy as np

work, mode = Path(sys.argv[1]).resolve(), sys.argv[2]
sys.path.insert(0, str(work))
import guarded_topology as gt
from bm_strain import BM

if mode == 'metamorphic':
    init0, H0 = BM.__init__, BM.H
    def init(self, *args, **kw):
        init0(self, *args, **kw)
        self._review_phi = kw.get('phi_deg', 0.)
    def H(self, k):
        h = H0(self, k)
        if self._review_phi == 197.:
            h = h.copy(); h[0,0] += .125
        return h
    BM.__init__, BM.H = init, H
    BM.flat_bandwidth = lambda self,*a,**kw: 0.
    BM.min_remote = lambda self,*a,**kw: (0., np.array([0.,0.]))
    target = 'metamorphic.py'
else:
    target = 'migrated_valley_control.py'
    nodes = [(0., np.array([.3,.4])), (0., np.array([.6,.6]))]
    if mode == 'no_pair': BM.find_nodes = lambda *a,**kw: []
    else: BM.find_nodes = lambda *a,**kw: nodes
    if mode == 'rejected':
        def reject(S, g): raise gt.Rejected('review_injected_rejection', scope='synthetic')
        gt.pair_charges = reject
    elif mode == 'late_discovery_error':
        counter = [0]
        def find(*a,**kw):
            counter[0] += 1
            if counter[0] == 2: raise RuntimeError('review injected discovery error after first B')
            return nodes
        BM.find_nodes = find
        gt.pair_charges = lambda S,g: dict(status='SYNTHETIC_RETURN',label='SAME',windings=[1.,1.],node_gaps_meV=[0.,0.])
    elif mode != 'no_pair': raise ValueError(mode)
sys.argv = [target]
runpy.run_path(str(work/target), run_name='__main__')
