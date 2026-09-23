#!/usr/bin/env python3
"""Read-only exact-predicate and hash verification; no numerical rerun."""
from fractions import Fraction
import json
from pathlib import Path
from runner_io import sha, verify

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(p):
    return json.loads(p.read_text())


def value(x):
    return Fraction(int(x['mantissa']))*Fraction(2)**x['exponent']


def bounds(x):
    lo,hi = value(x['lower']),value(x['upper'])
    require(lo<=hi,'invalid endpoints')
    return lo,hi


def signs(record):
    require(record['status']=='PASS','missing decisive pivots')
    negative = 0
    for p in record['pivots']:
        lo,hi = bounds(p)
        require(hi<0 or lo>0,'ambiguous pivot')
        negative += int(hi<0)
    require(negative==record['negative'],'pivot sign count mismatch')
    return len(record['pivots'])


def main():
    run = HERE/'RUN'
    integrity = verify(run)
    spec = read(HERE/'SPEC.json')
    packet = read(HERE/'PACKET_MANIFEST.json')
    for row in packet['files']+packet['prior_bindings']:
        path = ROOT/row['path']
        require(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'packet hash: '+row['path'])
    for name in ['SPEC.json','arithmetic.py','runner_io.py','run_calibration.py','test_runner.py']:
        require((HERE/name).read_bytes()==(run/'SOURCE'/HERE.name/name).read_bytes(),'source snapshot mismatch: '+name)
    require((HERE.parent/'certification_s0a_001/primitives.py').read_bytes()==
            (run/'SOURCE/certification_s0a_001/primitives.py').read_bytes(),'frozen primitive mismatch')
    summary = read(run/'RESULTS.json')
    require(summary['status']=='PASS_EXPECTED_BEHAVIORS','retained run did not pass')
    require(summary['completed_jobs']==summary['passed_jobs']==summary['planned_jobs']==len(spec['jobs']),'job count mismatch')
    require(summary['wall_seconds']<spec['limits']['global_wall_seconds'],'global resource cap')
    pivots,windows,inconclusive,transports = 0,0,0,0
    for job in spec['jobs']:
        r = read(run/(job['id']+'.json'))
        require(r['job']==job and r['status']=='PASS' and r['physical_evaluations']==0,'job provenance or status')
        require(r['wall_seconds']<spec['limits']['job_wall_seconds'],'job time cap')
        if 'expected' in job:
            require(r['observed']==job['expected'],'unexpected outcome')
        if job['kind']=='cell':
            require(bounds(r['Gram_defect_F_bound'])[1]<1,'basis not invertible')
            for shift in r['shifts']:
                if shift['status']=='CERTIFIED_SHIFT':
                    require(bounds(shift['inverse_residual_F_bound'])[1]<1,'uncertified inverse')
                    require(bounds(shift['center_B_F_bound'])[0]>0,'test has zero center residual')
                    pivots += signs(shift['complement_inertia'])+signs(shift['small_inertia'])
                    require(shift['negative']==shift['expected_negative'],'count versus known spectrum')
                    require(shift['negative']==shift['complement_inertia']['negative']+shift['small_inertia']['negative'],'Schur count sum')
            for i,w in enumerate(r['windows']):
                if w['status']=='CERTIFIED_WINDOW':
                    a,b = r['shifts'][2*i:2*i+2]
                    require(a['negative']==b['negative']==w['negative'],'window counts differ')
                    require(w['endpoints']==spec['windows'][i],'window endpoints differ')
                    windows += 1
            if r['observed']=='INCONCLUSIVE':
                inconclusive += 1
                require(any(w['status']=='INCONCLUSIVE' for w in r['windows']),'missing unresolved window')
        elif job['kind']=='transport':
            lo,hi = bounds(r['total_error_bound'])
            target = Fraction(spec['ledger']['frame_error'])
            if r['observed']=='WITHIN_FRAME_BUDGET':
                require(hi<target,'transport budget exceeded')
                transports += 1
            else:
                require(lo>target,'control not decisively over sufficient budget')
                inconclusive += 1
            require(len(r['consistency_checks'])==3,'missing endpoint consistency cases')
            for c in r['consistency_checks']:
                require(bounds(c['endpoint_discrepancy_bound'])[1]<lo,'closed-form consistency failure')
        else:
            require(all(r['checks'].values()) and len(r['checks'])==3,'phase/window controls')
            require(bounds(r['accepted_ledger']['q_radius_bound'])[1]<Fraction(1,8),'q budget')
            require(bounds(r['loose_ledger']['q_radius_bound'])[0]>Fraction(1,8),'loose ledger control')
    runner = read(HERE/'RUNNER_CHECKS.json')
    require(runner['status']=='PASS' and runner['passed']==len(runner['checks'])==10 and all(c['pass'] for c in runner['checks']),'runner controls')
    print(json.dumps({'status':'PASS_STATIC_HASHES_AND_EXACT_PREDICATES','run_files':integrity['files'],
                      'jobs':len(spec['jobs']),'signed_pivots':pivots,'certified_synthetic_windows':windows,
                      'transport_budget_passes':transports,'expected_inconclusive_controls':inconclusive,
                      'runner_controls':10,'physical_evaluations':0},indent=2,sort_keys=True))


if __name__=='__main__':
    main()
