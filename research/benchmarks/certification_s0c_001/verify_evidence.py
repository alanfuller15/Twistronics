#!/usr/bin/env python3
"""Read-only record, provenance and exact rational predicate verification."""
from fractions import Fraction
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'certification_s0b_001'))
from runner_io import sha,verify


def require(condition,message):
    if not condition:
        raise ValueError(message)


def read(p):
    return json.loads(p.read_text())


def bound(x):
    def v(z):
        return Fraction(int(z['mantissa']))*Fraction(2)**z['exponent']
    lo,hi=v(x['lower']),v(x['upper'])
    require(lo<=hi,'invalid bound endpoints')
    return lo,hi


def signs(record):
    require(record['status']=='PASS','missing inertia certificate')
    negative=0
    for p in record['pivots']:
        lo,hi=bound(p)
        require(hi<0 or lo>0,'indefinite pivot')
        negative+=int(hi<0)
    require(negative==record['negative'],'inertia sign count differs')
    return len(record['pivots'])


def main():
    spec,packet=read(HERE/'SPEC.json'),read(HERE/'PACKET_MANIFEST.json')
    for row in packet['files']+packet['prior_bindings']:
        p=ROOT/row['path']
        require(p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'changed packet file: '+row['path'])
    run=HERE/'RUN'
    integrity=verify(run)
    for p in (run/'SOURCE').rglob('*'):
        if p.is_file():
            original=HERE.parent/p.relative_to(run/'SOURCE')
            require(original.read_bytes()==p.read_bytes(),'snapshot mismatch: '+str(p))
    summary=read(run/'RESULTS.json')
    require(summary['status']=='PASS_EXPECTED_BEHAVIORS','run did not pass')
    require(summary['completed_jobs']==summary['passed_behaviors']==summary['planned_jobs']==len(spec['jobs']),'job count mismatch')
    require(summary['wall_seconds']<spec['limits']['global_wall_seconds'],'global time ceiling')
    require(summary['raw_status_counts']=={'CERTIFIED':4,'INCONCLUSIVE':6,'EXECUTION_ERROR':1},'expected outcome distribution')
    pivots,accepted_windows=0,0
    for job in spec['jobs']:
        r=read(run/(job['id']+'.json'))
        require(r['job']==job and r['status']==job['expected_status'] and r['reason']==job['expected_reason'],'job status/reason differs')
        require(r['physical_evaluations']==0 and r['wall_seconds']<spec['limits']['job_wall_seconds'],'scope or resource ceiling')
        if job['kind']=='ledger':
            corner,q=bound(r['corner_angle_bound']),bound(r['q_radius_bound'])
            cap,target=Fraction(job['repair']),Fraction(spec['ledger']['q_halfwidth'])
            if r['status']=='CERTIFIED':
                require(corner[1]<cap and q[1]<target,'conditional ledger failed')
            elif job['id']=='corner_old_cap':
                require(corner[0]>cap and q[1]<target,'old-cap control predicates')
            else:
                require(corner[1]<cap and q[0]>target,'overspent control predicates')
        elif job['kind']=='inverse':
            if job['mode']=='center':
                require('inverse_residual_F_bound' not in r,'inverse-exception path not reached')
            else:
                require(bound(r['inverse_residual_F_bound'])[0]>1,'wide-cell residual control')
        elif job['kind']=='gram':
            require(bound(r['Gram_defect_F_bound'])[0]>=1 and 'shifts' not in r,'uncertain-basis control')
        elif job['kind']=='dimension_fault':
            require(r['error_type']=='ValueError' and 'square dimensions' in r['message'],'genuine dimension fault misclassified')
        else:
            n=r['dimension']
            require(bound(r['Gram_defect_F_bound'])[1]<1,'uncertified basis')
            require(r['declared_pair']==job['pair'] and r['required_counts']==[job['pair'][0],job['pair'][1]+1],'declared indices differ')
            oracle=[(n-2)//2]*2+[(n-2)//2+2]*2
            for i,s in enumerate(r['shifts']):
                require(s['status']=='CERTIFIED' and bound(s['inverse_residual_F_bound'])[1]<1,'shift certificate missing')
                pivots+=signs(s['complement_inertia'])+signs(s['small_inertia'])
                require(s['negative']==s['complement_inertia']['negative']+s['small_inertia']['negative']==oracle[i],'count versus independent fixture spectrum')
                if job['kind']=='cell':
                    require(bound(s['center_B_F_bound'])[0]>0,'missing perturbed-basis residual')
            for i,w in enumerate(r['windows']):
                require(w['endpoints']==spec['windows'][i] and w['spectrum_free_window'] is True,'window binding')
                counts=[s['negative'] for s in r['shifts'][2*i:2*i+2]]
                require(w['endpoint_counts']==counts and counts[0]==counts[1],'endpoint counts differ')
                if job['id']=='small_wrong_pair':
                    require(w['status']=='INCONCLUSIVE' and w['reason']=='DECLARED_INDEX_NOT_CERTIFIED' and counts[0]!=w['required_count'],'wrong-index control falsely accepted')
                else:
                    require(w['status']=='CERTIFIED' and counts[0]==w['required_count'],'declared window failed')
                    require(Fraction(w['guaranteed_gap_width'])==Fraction(1,2) and Fraction(w['center_line_resolvent_distance'])==Fraction(1,4),'window distance record')
                    accepted_windows+=1
    checks=read(HERE/'PROTOCOL_CHECKS.json')
    require(checks['status']=='PASS' and checks['passed']==len(checks['checks'])==8 and all(c['pass'] for c in checks['checks']),'protocol checks')
    require(pivots==2064 and accepted_windows==6,'retained evidence totals')
    print(json.dumps({'status':'PASS_STATIC_HASHES_AND_EXACT_PREDICATES','jobs':len(spec['jobs']),
                      'raw_status_counts':summary['raw_status_counts'],'signed_pivots':pivots,
                      'declared_pair_windows':accepted_windows,'protocol_checks':8,
                      'run_files':integrity['files'],'physical_evaluations':0},indent=2,sort_keys=True))


if __name__=='__main__':
    main()
