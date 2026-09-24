"""Fixed synthetic frame bridge checks; bounded by the external timeout."""
import hashlib
import json
from pathlib import Path
import sys
from flint import arb, arb_mat, ctx
from frame_bridge import frame_from_projector
from certified_s0f import riesz_circle, seam_map
from primitives_s0f import identity


def main():
    ctx.prec=128
    ctx.threads=1
    here=Path(__file__).resolve().parent
    spec=json.loads((here/'SPEC.json').read_text())
    out=Path(sys.argv[1]); out.mkdir(parents=True,exist_ok=False)
    # Exact rational candidate: columns e1 and (0,c,s), c²+s²=1.
    # Exact target P=diag(1,1,0); PE polar factor is E0 for c>0.
    h=arb_mat([[0,0,0],[0,0,0],[0,0,2]])
    projector=riesz_circle(h,'0','1',32,'0','2','1/64')
    q=projector.pop('_center')
    ep=projector['total_projector_operator_error_bound']['upper']
    eps=arb(ep['mantissa'])*arb(2)**ep['exponent']
    t=arb(1)/1048576; c=(1-t*t)/(1+t*t); s=2*t/(1+t*t)
    e=arb_mat([[1,0],[0,c],[0,s]])
    bridge=frame_from_projector(q,eps,e,'1/16')
    f=bridge.pop('_frame')
    contains=all(f[i,j].contains(int(i==j)) for i in range(3) for j in range(2))
    seam=seam_map(f,arb_mat([[1,0,0],[0,1,0],[0,0,0]]),f,'1/16','1/128')
    singular=frame_from_projector(q,eps,arb_mat([[1,0],[0,0],[0,1]]),'1/16')
    budget=frame_from_projector(q,eps,e,'1/1000000000000')
    checks=[('projector',projector['status']=='CERTIFIED'),
            ('bridge',bridge['status']=='CERTIFIED'),('exact_reference_contained',contains),
            ('partial_shift_seam',seam['status']=='CERTIFIED'),
            ('rank_loss_refused',singular['reason']=='FRAME_PROJECTION_NOT_INJECTIVE'),
            ('frame_budget_refused',budget['reason']=='FRAME_ERROR_BUDGET')]
    result={'status':'PASS' if all(v for _,v in checks) else 'FAIL',
            'checks':[{'name':k,'passed':v} for k,v in checks], 'projector':projector,
            'bridge':bridge,'seam':seam,'rank_loss':singular,'budget':budget,
            'physical_evaluations':0,'spec':spec,'precision':ctx.prec,
            'source_sha256':{n:hashlib.sha256((here/n).read_bytes()).hexdigest() for n in ('SPEC.json','check.py','frame_bridge.py','primitives_s0f.py','pair_s0f.py','certified_s0f.py')}}
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'passed':sum(v for _,v in checks),'checks':len(checks),'physical_evaluations':0}))
    return 0 if result['status']=='PASS' else 1

if __name__=='__main__': raise SystemExit(main())
