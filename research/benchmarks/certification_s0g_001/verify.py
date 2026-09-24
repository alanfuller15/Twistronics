"""Read-only release integrity, source equality and exact-predicate verification."""
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'certification_s0b_001'))
from runner_io import verify,sha


def require(ok,message):
    if not ok: raise ValueError(message)


def main():
    out=HERE/'RUN'
    integrity=verify(out)
    spec=json.loads((HERE/'SPEC.json').read_text())
    summary=json.loads((out/'RESULTS.json').read_text())
    require(summary['status']=='PASS_EXPECTED_BEHAVIORS' and len(summary['jobs'])==len(spec['jobs']),'summary')
    for source in (out/'SOURCE').rglob('*'):
        if source.is_file(): require(sha(source)==sha(HERE.parent/source.relative_to(out/'SOURCE')),'source '+str(source))
    require(sha(out/'S0G_BATCH.md')==sha(HERE.parents[2]/'docs/certification-readiness/S0G_BATCH.md'),'derivation')
    env=json.loads((out/'ENVIRONMENT.json').read_text())
    require(env['wheel']['sha256']==spec['backend']['wheel_sha256'] and len(env['native_artifacts'])>0,'backend')
    require(env['python_flint']==spec['backend']['python_flint'] and env['FLINT']==spec['backend']['flint'],'versions')
    for job in spec['jobs']:
        r=json.loads((out/(job['id']+'.json')).read_text())
        require(r['job']==job and (r['status'],r['reason'])==(job['expected_status'],job['expected_reason']),job['id'])
        require(r['physical_evaluations']==0,'physical scope')
    require(json.loads((out/'gauge_correct.json').read_text())['exact_connection_coefficient']=='0','gauge')
    require(json.loads((out/'gauge_unconverted.json').read_text())['exact_connection_coefficient']=='24/25','negative gauge')
    require(json.loads((out/'vector_good.json').read_text())['vector']==[1,2,-1],'vector')
    print(json.dumps({'status':'PASS_STATIC_INTEGRITY_AND_PREDICATES','jobs':len(spec['jobs']),'record_files':integrity['files']}))


if __name__=='__main__': main()
