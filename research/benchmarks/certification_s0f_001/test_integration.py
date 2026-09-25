"""Import isolation and reused-path exception propagation controls."""
from pathlib import Path
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent


def main():
    checks=[]
    for preload in ('certification_s0a_001', 'certification_s0b_001'):
        name='primitives' if preload.endswith('s0a_001') else 'arithmetic'
        code=f"""
import sys
sys.path.insert(0,{str(HERE.parent/preload)!r})
import {name}
sys.path.insert(0,{str(HERE)!r})
import certified_s0f as c, primitives_s0f as p
assert c._prior.inertia_ldl is p.inertia_ldl
assert c.NonfiniteEnclosure is p.NonfiniteEnclosure
"""
        r=subprocess.run([sys.executable,'-B','-c',code],capture_output=True,text=True,timeout=10)
        checks.append({'name':'preload_'+preload,'passed':r.returncode==0,'stderr':r.stderr})
    import certified_s0f as c
    import primitives_s0f as p
    from flint import arb, arb_mat, ctx
    ctx.prec=128
    original=c._prior.inertia_ldl
    calls=[]
    def injected(a):
        # Deliberate fault injection at the reused LDL boundary, not a natural
        # overflow claim for the well-conditioned pair below.
        calls.append(a.nrows())
        return original(arb_mat([[arb('1e100').exp()]]))
    c._prior.inertia_ldl=injected
    try:
        h=arb_mat([[-4,0,0,0,0,0],[0,-3,0,0,0,0],[0,0,0,0,0,0],
                   [0,0,0,0,0,0],[0,0,0,0,3,0],[0,0,0,0,0,4]])
        result=c.pair_from_enclosed_inputs(p.identity(6),h,arb_mat(6,6),'0',
                [['-5/4','-3/4'],['3/4','5/4']],[[0,1,2,3]]*4,[2,3])
    finally:
        c._prior.inertia_ldl=original
    checks.append({'name':'reused_pair_LDL_fault_injection','passed':bool(calls) and
        result.get('reason')=='NONFINITE_ENCLOSURE' and result.get('status')=='INCONCLUSIVE',
        'calls':calls,'result':result})
    print(json.dumps({'status':'PASS' if all(x['passed'] for x in checks) else 'FAIL',
                      'checks':checks,'physical_evaluations':0},indent=2))
    return 0 if all(x['passed'] for x in checks) else 1

if __name__=='__main__': raise SystemExit(main())
