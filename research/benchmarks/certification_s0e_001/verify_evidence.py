"""Read-only integrity and exact predicate checks; no numerical execution."""
from pathlib import Path
from fractions import Fraction
import hashlib, json, sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'certification_s0b_001'))
from runner_io import verify

def require(ok, message):
    if not ok: raise ValueError(message)

def read(p): return json.loads(p.read_text())
def bounds(x):
    return tuple(Fraction(int(x[k]['mantissa']))*Fraction(2)**x[k]['exponent'] for k in ('lower','upper'))

def main():
    packet=read(HERE/'PACKET_MANIFEST.json')
    for row in packet['files']:
        data=(ROOT/row['path']).read_bytes()
        require(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path'])
    run=HERE/'RUN'; integrity=verify(run); spec=read(HERE/'SPEC.json')
    for p in (run/'SOURCE').rglob('*'):
        if p.is_file(): require(p.read_bytes()==(HERE.parent/p.relative_to(run/'SOURCE')).read_bytes(),'source binding')
    records={j['id']:read(run/(j['id']+'.json')) for j in spec['jobs']}
    for j in spec['jobs']:
        r=records[j['id']]
        require(r['job']==j and r['status']==j['expected_status'] and r['reason']==j['expected_reason'],'job mismatch')
        require(r['physical_evaluations']==0 and r['wall_seconds']<30,'scope/time')
    closed=records['phase_closed']; lo,hi=bounds(closed['winding_interval'])
    require(lo<=1<=hi and (hi-lo)/2<=Fraction(1,8),'closed containment/width')
    lo,hi=bounds(records['phase_open']['winding_interval'])
    require(lo>1 and hi<Fraction(3,2),'open regression not reached')
    lo,hi=bounds(records['phase_wide']['winding_interval'])
    require(lo<=1<=hi and (hi-lo)/2>Fraction(1,8),'width regression not reached')
    require(bounds(records['seam_deletion_pass']['singular_square_defect_F'])[1]<=Fraction(39,400),'seam pass')
    require(bounds(records['seam_deletion_fail']['singular_square_defect_F'])[0]>Fraction(39,400),'seam refusal')
    require(records['growth_bound']['arithmetic_message']=='nonfinite bound','bound overflow')
    require(records['growth_ldl']['arithmetic_message']=='nonfinite LDL pivot','LDL overflow')
    require(records['unrelated_error']['error_type']=='ArithmeticError','unrelated error swallowed')
    checks=read(HERE/'PROTOCOL_CHECKS.json')
    require(checks['passed']==10 and all(x['pass'] for x in checks['checks']),'protocol')
    require(read(run/'RESULTS.json')['passed_behaviors']==14,'count')
    print(json.dumps({'status':'PASS_STATIC_INTEGRITY_AND_PREDICATES','jobs':14,'protocol_checks':10,'run_files':integrity['files'],'physical_evaluations':0}))
if __name__=='__main__': main()
