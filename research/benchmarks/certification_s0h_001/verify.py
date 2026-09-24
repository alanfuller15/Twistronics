"""Read-only release verification; does not rerun numerical work."""
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'certification_s0b_001'))
from runner_io import verify, sha


def require(condition, name):
    if not condition:
        raise ValueError(name)


def main():
    out = HERE/'RUN'
    integrity = verify(out)
    spec = json.loads((HERE/'SPEC.json').read_text())
    summary = json.loads((out/'RESULTS.json').read_text())
    require(summary['status'] == 'PASS_EXPECTED_BEHAVIORS', 'summary')
    require(len(summary['jobs']) == len(spec['jobs']), 'job count')
    for source in (out/'SOURCE').rglob('*'):
        if source.is_file():
            require(sha(source) == sha(HERE.parent/source.relative_to(out/'SOURCE')), 'source')
    require(sha(out/'S0H_COMPOSITION.md') == sha(HERE.parents[2]/'docs/certification-readiness/S0H_COMPOSITION.md'), 'derivation')
    env = json.loads((out/'ENVIRONMENT.json').read_text())
    require(env['wheel']['sha256'] == spec['backend']['wheel_sha256'] and env['native_artifacts'], 'backend')
    require(env['python_flint'] == spec['backend']['python_flint'] and env['FLINT'] == spec['backend']['flint'], 'versions')
    for path, expected in spec['dependencies'].items():
        require(sha(HERE.parent/path) == expected, 'dependency')
    for job in spec['jobs']:
        result = json.loads((out/(job['id']+'.json')).read_text())
        require(result['job'] == job, 'job input')
        require((result['status'], result['reason']) == (job['expected_status'], job['expected_reason']), job['id'])
        require(result['physical_evaluations'] == 0, 'physical scope')
    for mode in ('joined', 'unbound_Q', 'joint_budget'):
        result = json.loads((out/(mode+'.json')).read_text())
        for r in result['individual'].values():
            require(r['status'] == 'CERTIFIED' and r['q'] == 0, 'individual persistence')
            require(len(r['cells']) == 128 and r['corner']['delta_excludes_zero'], 'geometry')
    good = json.loads((out/'joined.json').read_text())
    require(len(good['relative']['cells']) == 128, 'relative coverage')
    for n in (196, 308):
        result = json.loads((out/('full_'+str(n)+'.json')).read_text())
        require(result['dimension'] == n and result['riesz']['status'] == result['frame']['status'] == 'CERTIFIED', 'dense bridge')
    print(json.dumps({'status': 'PASS_STATIC_INTEGRITY_AND_PREDICATES', 'jobs': len(spec['jobs']), 'record_files': integrity['files']}))


if __name__ == '__main__':
    main()
