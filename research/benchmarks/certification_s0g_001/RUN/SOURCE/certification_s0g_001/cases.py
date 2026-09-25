"""Fixed analytic gauge/repair fixtures. No physical model or generic q composer."""
import hashlib
import json
from fractions import Fraction
from flint import arb, arb_mat
from certified_s0f import seam_map, continuous_phase_lift
from primitives_s0f import enclosure, frobenius, identity


def rotation(t):
    c, s = t.cos(), t.sin()
    return arb_mat([[c, -s], [s, c]])


def gauge(correct):
    # F(y)=Rz(y) [ (24/25,0,-7/25), (0,1,0) ].
    # F^T F'=c J; K=F R(-cy), so K^T K'=0 identically.
    # The interval encloses every y in [0,1], not just mesh samples.
    y, c, s = arb('0.5', '0.5'), arb(24)/25, arb(7)/25
    co, si = y.cos(), y.sin()
    f = arb_mat([[c*co,-si],[c*si,co],[-s,0]])
    df = arb_mat([[-c*si,-co],[c*co,-si],[0,0]])
    j = arb_mat([[0,-1],[1,0]])
    rate = -c if correct else arb(0)
    r = rotation(rate*y)
    k = f*r
    dk = df*r+f*r*j*rate
    # Wide interval arithmetic is retained as a diagnostic, not a zero proof.
    diagnostic = frobenius(k.transpose()*dk)
    # Exact trigonometric algebra reduces the connection to (c+rate)J.
    coefficient = c+rate
    exact_rate = -Fraction(24,25) if correct else Fraction(0)
    exact_connection = Fraction(24,25)+exact_rate
    passed = exact_connection == 0
    return {'status':'CERTIFIED' if passed else 'INCONCLUSIVE',
            'reason':'SYNTHETIC_ANALYTIC_KATO_GAUGE' if passed else 'GAUGE_CONNECTION_NOT_ZERO',
            'exact_connection_coefficient':str(exact_connection),
            'connection_coefficient':enclosure(coefficient),
            'unreduced_interval_connection_F':enclosure(diagnostic),
            'proof':'S0G_BATCH.md: fixed analytic gauge lemma',
            'domain':['0','1'], 'analytic_family':'Rz(y)E; E=((24/25,0,-7/25),(0,1,0))'}


def distinct_seam(fail):
    c = arb(9)/10 if fail else arb(24)/25
    s = (1-c*c).sqrt()
    f0 = arb_mat([[1,0],[0,1],[0,0]])
    f1 = arb_mat([[c,0],[0,1],[-s,0]])
    shift = arb_mat([[1,0,0],[0,1,0],[0,0,0]])
    result = seam_map(f1,shift,f0,'1/16','1/128')
    # M=diag(c,1), c>0, hence polar(M)=I and J_exact=F1 F0^T.
    result['exact_map_columns'] = [[enclosure(x) for x in row] for row in [[c,arb(0)],[arb(0),arb(1)],[-s,arb(0)]]]
    result['fixture_proof'] = 'distinct fibres; M=diag(c,1); polar(M)=I'
    return result


def repaired_lift(winding, repair=True, bad_branch=False):
    delta = arb(4) if bad_branch else arb(1)/5
    # Exact principal repair requires |delta|<pi/3 in this fixture.
    if not delta.abs_upper() < arb.pi()/3:
        return {'status':'INCONCLUSIVE','reason':'REPAIR_BRANCH_REFUSED'}
    raw_total = 2*arb.pi()*winding+delta
    corrected_total = raw_total-delta if repair else raw_total
    samples = [[(corrected_total*k/32).cos(), (corrected_total*k/32).sin()] for k in range(33)]
    result = continuous_phase_lift(samples,'0','1/2',
        exact_closure_declared=True, variation_certified=True)
    # Declarations above are proved only for this generated analytic path:
    # exp(i(2pi*n+delta)t) exp(-i delta*t)=exp(2pi*i*n*t).
    # |phase'|/32=2pi*|n|/32 < pi/2 for n=1,2; no hidden turns.
    result['analytic_path'] = {'winding':winding,'steps':32,'repair_applied':repair,
                              'principal_defect':'1/5','family':'linear phase on [0,1]'}
    return result


def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def bound_vector(mode):
    # This only binds generated analytic loop records. It is not the CASE q map.
    a, b = repaired_lift(1), repaired_lift(2)
    records = {'a':{'input':a['analytic_path'],'result':a},
               'b':{'input':b['analytic_path'],'result':b}}
    expected = {role:digest(record) for role,record in records.items()}
    if mode=='swap':
        records['a'], records['b'] = records['b'], records['a']
    elif mode=='tamper':
        records['a']['result']['certified_integer']=2
    elif mode=='conditional':
        records['a']['result']['reason']='CONDITIONAL_PROJECTOR_FRAME_ENCLOSURE'
        expected['a']=digest(records['a'])
    for role, record in records.items():
        if digest(record)!=expected[role]:
            return {'status':'INCONCLUSIVE','reason':'ROLE_CONTENT_BINDING_REFUSED','role':role}
        result=record['result']
        if result['status']!='CERTIFIED' or result['reason']!='CONTINUOUS_PHASE_LIFT':
            return {'status':'INCONCLUSIVE','reason':'ROLE_REASON_REFUSED','role':role}
    qa,qb=(records[r]['result']['certified_integer'] for r in ('a','b'))
    return {'status':'CERTIFIED','reason':'SYNTHETIC_REPAIRED_LOOP_VECTOR',
            'vector':[qa,qb,qa-qb], 'role_hashes':expected,'records':records,
            'scope':'Generated SO(2) loops only; no geometric q-pipeline dependency certificate'}


def run(job,spec):
    name=job['id']
    if name.startswith('gauge_'): return gauge(name=='gauge_correct')
    if name.startswith('seam_'): return distinct_seam(name=='seam_loss')
    if name=='lift_a': return repaired_lift(1)
    if name=='lift_b': return repaired_lift(2)
    if name=='lift_open': return repaired_lift(1,repair=False)
    if name=='repair_branch': return repaired_lift(1,bad_branch=True)
    if name.startswith('vector_'): return bound_vector(name.removeprefix('vector_'))
    raise ValueError('unknown frozen job')
