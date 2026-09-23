"""Cheap synthetic consumer controls; no resulting labels are physics evidence."""
import sys
from pathlib import Path
import numpy as np

work=Path(sys.argv[1]).resolve(); mode=sys.argv[2]
sys.path.insert(0,str(work))
import migrated_valley_control as mv
nodes=[np.array([.3,.4]),np.array([.6,.6])]
def fake(S,g):return dict(label='SAME',windings=[1.,1.],node_gaps_meV=[0.,0.],lo=S.m.dim//2-1,status='SYNTHETIC_RETURN')
if mode=='late_geometry':
    original=mv.gt.geometry;count=[0]
    def geometry(*args,**kwargs):
        count[0]+=1
        if count[0]==3: raise RuntimeError('review injected geometry failure after first B')
        return original(*args,**kwargs)
    mv.gt.geometry=geometry
elif mode=='wrong_gate_status':
    def fake(S,g):return dict(label='SAME',windings=[1.,1.],node_gaps_meV=[0.,0.],lo=S.m.dim//2-1,status='REJECTED')
elif mode=='duplicate_case':
    import json
    p=work/'PLAN_MIGRATION.json';d=json.loads(p.read_text())
    d['coupled_settings']=[d['coupled_settings'][0]]*2
    d['expected_cases']=[dict(c) for c in d['expected_cases'] if c['radius']==.012 for _ in range(2)]
    p.write_text(json.dumps(d,indent=2)+'\n')
else:raise ValueError(mode)
sys.exit(mv.main('OUT',discovery=lambda m:nodes,measure=fake))
