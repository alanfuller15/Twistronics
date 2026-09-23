"""Harness-contract control, NOT a scientific replay.

Execute unchanged metamorphic.py after an explicitly injected MR1 violation.
Stub the expensive bandwidth/minimum methods only in this disposable control.
"""
import runpy
import sys
from pathlib import Path
import numpy as np
work = Path(sys.argv[1]).resolve(); sys.path.insert(0, str(work))
from bm_strain import BM
init0 = BM.__init__; H0 = BM.H
def init(self, *args, **kw):
    init0(self, *args, **kw); self._review_phi = kw.get('phi_deg', 0.)
def H(self, k):
    h = H0(self, k)
    if self._review_phi == 197.:
        h = h.copy(); h[0, 0] += .125
    return h
BM.__init__ = init; BM.H = H
BM.flat_bandwidth = lambda self, *a, **kw: 0.
BM.min_remote = lambda self, *a, **kw: (0., np.array([0., 0.]))
sys.argv = ['metamorphic.py']
runpy.run_path(str(work/'metamorphic.py'), run_name='__main__')
