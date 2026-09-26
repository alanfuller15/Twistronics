#!/usr/bin/env python3
"""Read-only hash, provenance and exact predicate verifier for S0d."""
from fractions import Fraction
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent/'certification_s0b_001'))
from runner_io import sha, verify


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def bound(record):
    def value(endpoint):
        return Fraction(int(endpoint['mantissa']))*Fraction(2)**endpoint['exponent']
    lower, upper = value(record['lower']), value(record['upper'])
    require(lower <= upper, 'invalid bound endpoints')
    return lower, upper


def signed_pivots(inertia):
    require(inertia['status'] == 'PASS', 'missing inertia certificate')
    negative = 0
    for pivot in inertia['pivots']:
        lower, upper = bound(pivot)
        require(upper < 0 or lower > 0, 'zero-containing signed pivot')
        negative += int(upper < 0)
    require(negative == inertia['negative'], 'inertia count mismatch')
    return len(inertia['pivots'])


def main():
    spec, packet = read(HERE/'SPEC.json'), read(HERE/'PACKET_MANIFEST.json')
    for row in packet['files']+packet['prior_bindings']:
        path = ROOT/row['path']
        require(path.stat().st_size == row['bytes'] and sha(path) == row['sha256'],
                'changed packet file: '+row['path'])
    run = HERE/'RUN'
    integrity = verify(run)
    for path in (run/'SOURCE').rglob('*'):
        if path.is_file():
            original = HERE.parent/path.relative_to(run/'SOURCE')
            require(original.read_bytes() == path.read_bytes(),
                    'snapshot mismatch: '+str(path))
    summary = read(run/'RESULTS.json')
    require(summary['status'] == 'PASS_EXPECTED_BEHAVIORS', 'run did not pass')
    require(summary['completed_jobs'] == summary['passed_behaviors'] ==
            summary['planned_jobs'] == len(spec['jobs']), 'job count mismatch')
    require(summary['raw_status_counts'] ==
            {'CERTIFIED': 6, 'INCONCLUSIVE': 6, 'EXECUTION_ERROR': 1},
            'raw outcome distribution')
    require(summary['wall_seconds'] < spec['limits']['global_wall_seconds'],
            'global time ceiling')

    records = {}
    for job in spec['jobs']:
        record = read(run/(job['id']+'.json'))
        records[job['id']] = record
        require(record['job'] == job and record['status'] == job['expected_status'] and
                record['reason'] == job['expected_reason'],
                'status/reason mismatch: '+job['id'])
        require(record['physical_evaluations'] == 0 and
                record['wall_seconds'] < spec['limits']['job_wall_seconds'],
                'scope or time ceiling: '+job['id'])

    budget = records['budget_named']
    require(bound(budget['corner_angle_bound'])[1] < Fraction(3, 16) and
            bound(budget['q_radius_bound'])[1] < Fraction(1, 8),
            'conditional budget predicates')

    branch = records['branch_gate_pass']
    refused = records['branch_gate_approx_only']
    require(bound(branch['single_path_error']) == (Fraction(257, 16384),)*2,
            'single path debit')
    require(bound(branch['required_approximate_distance_max']) ==
            (Fraction(7935, 8192),)*2, 'approximate branch threshold')
    require(bound(branch['charged_exact_path_distance'])[1] <= 1 and
            bound(branch['branch_separation_after_corner_error'])[0] > 0,
            'positive branch gate')
    require(bound(refused['approximate_path_distance'])[1] < 1 and
            bound(refused['charged_exact_path_distance'])[0] > 1,
            'approximation-only control')

    congruence = records['internal_congruence']
    require(congruence['congruence_built_internally'] is True and
            congruence['congruence_inputs'] == ['V', 'H0', 'Hx'] and
            congruence['required_counts'] == [2, 4], 'internal congruence binding')
    pivots = 0
    for shift in congruence['shifts']:
        require(shift['status'] == 'CERTIFIED', 'uncertified congruence shift')
        pivots += signed_pivots(shift['complement_inertia'])
        pivots += signed_pivots(shift['small_inertia'])
    require(pivots == 24 and all(w['status'] == 'CERTIFIED'
                                 for w in congruence['windows']),
            'congruence window evidence')
    require(records['nonfinite_growth']['arithmetic_message'] == 'nonfinite bound',
            'recognized nonfinite path')
    require(records['shape_fault']['error_type'] == 'ValueError' and
            'equal dimensions' in records['shape_fault']['message'],
            'shape fault was reclassified')

    projector = records['projector_good']
    under = records['projector_underresolved']
    require(projector['quadrature_identity'] == 'roots_of_unity_trapezoid' and
            projector['fixture_spectrum'] == [-3, -2, 0, 0, 2, 3] and
            projector['fixture_target_indices'] == [2, 3], 'projector fixture binding')
    require(bound(projector['analytic_operator_error_bound'])[0] <= Fraction(1, 255) <=
            bound(projector['analytic_operator_error_bound'])[1],
            'roots-of-unity error identity')
    require(bound(projector['total_projector_operator_error_bound'])[1] < Fraction(1, 64) and
            bound(projector['fixture_target_action_F_bound'])[1] < Fraction(1, 10**20) and
            bound(projector['fixture_complement_action_F_bound'])[1] < Fraction(1, 128),
            'projector positive predicates')
    require(bound(under['total_projector_operator_error_bound'])[0] > Fraction(1, 64),
            'underresolved projector control')

    seam = records['seam_good']
    require(seam['overlap_built_internally'] is True and
            bound(seam['left_Gram_defect_F_bound'])[1] < Fraction(1, 16) and
            bound(seam['right_Gram_defect_F_bound'])[1] < Fraction(1, 16) and
            bound(seam['polar']['overlap_determinant'])[0] > 0 and
            bound(seam['seam_map_error_F_bound'])[1] < Fraction(1, 128),
            'seam enclosure predicates')
    require(bound(records['polar_singular']['conformal_denominator_squared']) ==
            (Fraction(0), Fraction(0)), 'singular polar control')

    phase = records['phase_winding']
    require(phase['certified_integer'] == phase['candidate_integer'] == 1 and
            len(phase['increments']) == 16 and
            all(bound(step['dot'])[0] > Fraction(1, 2) for step in phase['increments']) and
            bound(phase['closure_angle_bound'])[0] > Fraction(-1, 64) and
            bound(phase['closure_angle_bound'])[1] < Fraction(1, 64),
            'continuous phase lift predicates')
    qlower, qupper = bound(phase['winding_interval'])
    require(Fraction(1, 2) < qlower <= qupper < Fraction(3, 2),
            'unique integer interval')
    require(bound(records['phase_branch_bad']['failed_dot_bound'])[1] < 0,
            'branch-cut refusal control')
    ambiguous = bound(records['phase_integer_ambiguous']['winding_interval'])
    require(not (Fraction(1, 2) < ambiguous[0] and ambiguous[1] < Fraction(3, 2)),
            'ambiguous integer control accidentally isolated')

    checks = read(HERE/'PROTOCOL_CHECKS.json')
    require(checks['status'] == 'PASS' and checks['passed'] ==
            len(checks['checks']) == 10 and all(c['pass'] for c in checks['checks']),
            'protocol checks')
    print(json.dumps({'status': 'PASS_STATIC_HASHES_AND_EXACT_PREDICATES',
                      'jobs': len(spec['jobs']),
                      'raw_status_counts': summary['raw_status_counts'],
                      'signed_pivots': pivots, 'phase_steps': len(phase['increments']),
                      'protocol_checks': 10, 'run_files': integrity['files'],
                      'physical_evaluations': 0}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
