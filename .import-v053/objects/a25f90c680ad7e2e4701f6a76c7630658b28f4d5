"""Small synthetic probes of remaining public-API guard behavior.

These do not measure a physical state or enter the replay's acceptance gate.
Uploaded source is not modified; class globals are temporarily mocked in this
separate process solely to make an optimizer failure deterministic.
"""
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from models import TBG
import tbg_ref

def run():
    m=object.__new__(TBG);m.gap=lambda i:lambda f:1.+float(np.sum((np.asarray(f)-.4)**2))
    original=tbg_ref.minimize
    try:
        tbg_ref.minimize=lambda *args,**kwargs:SimpleNamespace(success=False,fun=1.)
        result=m.gap_min(1,n=3,keep=2)
    finally:tbg_ref.minimize=original
    return dict(scope='Synthetic failure injection, not a campaign measurement',
      failed_optimizer_result='positive infinity' if np.isposinf(result) else repr(result),
      failed_optimizer_would_pass_naive_positive_gap_test=bool(result>0),
      primary_harness_uses_this_helper=False,
      radius_expression=dict(request=-1.0,separation=.1,result=float(min(-1.0 or .01,.01,.3*.1))),
      interpretation='The public helper still needs explicit failure/nonfinite handling and positive finite radius validation; primary measurements use their own guarded routines.')

if __name__=='__main__':
    r=run();(Path(__file__).resolve().parent/'provenance/source_guard_probes.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
