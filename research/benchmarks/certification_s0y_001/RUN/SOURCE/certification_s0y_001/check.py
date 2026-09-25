#!/usr/bin/env python3
"""Derive one exact contour contract from complete synthetic S1-shaped windows."""
import argparse
import copy
from fractions import Fraction as Q
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'certification_s0b_001'))
from runner_io import atomic_json, begin, finish, sha, verify


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rational(value):
    try:
        return Q(value)
    except (ValueError, TypeError, ZeroDivisionError):
        raise ValueError('INVALID_RATIONAL') from None


def qtext(value):
    value = Q(value)
    return str(value.numerator) if value.denominator == 1 else f'{value.numerator}/{value.denominator}'


def interval(record, axis, required=False):
    try:
        raw = record[axis]
        need(isinstance(raw, list) and len(raw) == 2,
             'INVALID_REQUIRED_DOMAIN' if required else 'INVALID_CELL_DOMAIN')
        lo, hi = map(rational, raw)
    except (KeyError, TypeError):
        raise ValueError('INVALID_REQUIRED_DOMAIN' if required else 'INVALID_CELL_DOMAIN') from None
    need(lo < hi, 'INVALID_REQUIRED_DOMAIN' if required else 'INVALID_CELL_DOMAIN')
    return lo, hi


def canonical_domain(domain):
    return {axis: [qtext(value) for value in interval(domain, axis, required=True)]
            for axis in ('x', 'y')}


def check_exact_cover(cells, required):
    req = {axis: interval(required, axis, required=True) for axis in ('x', 'y')}
    boxes = []
    for cell in cells:
        box = {axis: interval(cell.get('domain', {}), axis) for axis in ('x', 'y')}
        for axis in ('x', 'y'):
            need(req[axis][0] <= box[axis][0] < box[axis][1] <= req[axis][1],
                 'CELL_OUTSIDE_REQUIRED_DOMAIN')
        boxes.append(box)
    cuts = {axis: sorted({req[axis][0], req[axis][1]} |
                         {edge for box in boxes for edge in box[axis]})
            for axis in ('x', 'y')}
    for xa, xb in zip(cuts['x'], cuts['x'][1:]):
        for ya, yb in zip(cuts['y'], cuts['y'][1:]):
            x, y = (xa + xb) / 2, (ya + yb) / 2
            count = sum(box['x'][0] < x < box['x'][1] and
                        box['y'][0] < y < box['y'][1] for box in boxes)
            need(count != 0, 'COVERAGE_GAP')
            need(count == 1, 'COVERAGE_OVERLAP')
    return req


def derive_contract(evidence, assembly, assembly_digest):
    need(evidence.get('schema') == 'synthetic_s1_window_evidence_v1',
         'WINDOW_EVIDENCE_SCHEMA_REQUIRED')
    need(evidence.get('evidence_scope') == 'synthetic_shape_fixture',
         'PHYSICAL_S1_EVIDENCE_REQUIRED')
    need(evidence.get('physical_model_evaluations') == 0,
         'ZERO_PHYSICAL_EVALUATIONS_REQUIRED')
    need(evidence.get('assembly_artifact') == 'SYNTHETIC_AFFINE_ASSEMBLY.json',
         'ASSEMBLY_ARTIFACT_REQUIRED')
    need(evidence.get('assembly_artifact_sha256') == assembly_digest,
         'ASSEMBLY_ARTIFACT_HASH_MISMATCH')
    need(assembly.get('schema') == 'synthetic_affine_self_adjoint_assembly_v1' and
         assembly.get('evidence_scope') == 'synthetic_shape_fixture' and
         assembly.get('physical_model_evaluations') == 0,
         'ASSEMBLY_SCOPE_MISMATCH')
    need(evidence.get('contour_policy') == 'max_margin_midpoint_circle_v1',
         'CONTOUR_POLICY_REQUIRED')
    required = canonical_domain(evidence.get('required_parameter_domain', {}))
    need(canonical_domain(assembly.get('parameter_domain', {})) == required,
         'ASSEMBLY_DOMAIN_MISMATCH')
    selected = evidence.get('selected_zero_based_indices')
    need(isinstance(selected, list) and len(selected) == 2 and
         all(isinstance(value, int) for value in selected) and selected[1] == selected[0] + 1,
         'SELECTED_INDICES_REQUIRED')
    need(assembly.get('selected_zero_based_indices') == selected,
         'ASSEMBLY_SELECTED_INDICES_MISMATCH')
    derivative_contract = assembly.get('derivative_contract', {})
    need(derivative_contract.get('norm') == 'operator', 'OPERATOR_NORM_REQUIRED')
    derivative_id = derivative_contract.get('contract_id')
    need(isinstance(derivative_id, str) and derivative_id, 'DERIVATIVE_PROVENANCE_REQUIRED')

    cells = evidence.get('cells')
    need(isinstance(cells, list) and cells, 'EMPTY_WINDOW_INVENTORY')
    ids = [cell.get('cell_id') for cell in cells]
    need(all(isinstance(value, str) and value for value in ids), 'CELL_ID_REQUIRED')
    need(len(ids) == len(set(ids)), 'DUPLICATE_CELL_ID')
    check_exact_cover(cells, required)

    parsed = []
    for cell in cells:
        need(cell.get('status') == 'CERTIFIED_SYNTHETIC_WINDOW', 'UNCERTIFIED_WINDOW_CELL')
        need(cell.get('assembly_evidence_id') == assembly.get('evidence_id'),
             'ASSEMBLY_PROVENANCE_MISMATCH')
        need(cell.get('self_adjoint') is True, 'SELF_ADJOINT_EVIDENCE_REQUIRED')
        need(cell.get('selected_zero_based_indices') == selected, 'SELECTED_INDICES_MISMATCH')
        need(cell.get('derivative_contract_id') == derivative_id,
             'DERIVATIVE_PROVENANCE_MISMATCH')
        try:
            cluster_low = rational(cell['cluster_lower'])
            cluster_high = rational(cell['cluster_upper'])
            lower_complement = rational(cell['lower_complement_upper'])
            upper_complement = rational(cell['upper_complement_lower'])
        except KeyError:
            raise ValueError('MISSING_SPECTRAL_BOUND') from None
        need(lower_complement < cluster_low <= cluster_high < upper_complement,
             'CELL_SPECTRAL_ORDER_INVALID')
        derivatives = cell.get('H_derivative_bounds', {})
        need(all(name in derivatives for name in ('H1', 'H2', 'H3')),
             'UNBOUND_DERIVATIVE_INPUT')
        derivatives = {name: rational(derivatives[name]) for name in ('H1', 'H2', 'H3')}
        need(all(value >= 0 for value in derivatives.values()), 'NEGATIVE_DERIVATIVE_BOUND')
        parsed.append(dict(cluster_low=cluster_low, cluster_high=cluster_high,
                           lower_complement=lower_complement,
                           upper_complement=upper_complement, derivatives=derivatives))

    global_low = min(row['cluster_low'] for row in parsed)
    global_high = max(row['cluster_high'] for row in parsed)
    center = (global_low + global_high) / 2
    rho = max(center - global_low, global_high - center)
    lower_nearest = max(row['lower_complement'] for row in parsed)
    upper_nearest = min(row['upper_complement'] for row in parsed)
    g = min(center - lower_nearest, upper_nearest - center)
    need(g > rho, 'UNIFORM_SEPARATION_REQUIRED')
    radius = (rho + g) / 2
    distance = min(radius - rho, g - radius)
    need(distance > 0, 'POSITIVE_RESOLVENT_DISTANCE_REQUIRED')
    derivatives = {name: max(row['derivatives'][name] for row in parsed)
                   for name in ('H1', 'H2', 'H3')}
    h1, h2, h3 = (derivatives[name] for name in ('H1', 'H2', 'H3'))
    p1 = radius * h1 / distance**2
    p2 = radius * (2 * h1**2 / distance**3 + h2 / distance**2)
    p3 = radius * (6 * h1**3 / distance**4 +
                   6 * h1 * h2 / distance**3 + h3 / distance**2)
    inputs = {
        'contract_id': 'synthetic_s1_window_derived_contract',
        'theorem_id': 'self_adjoint_riesz_contour_differentiation_v1',
        'self_adjoint': True,
        'cluster_dimension': len(selected),
        'selected_zero_based_indices': selected,
        'cluster_center': qtext(center),
        'contour_center': qtext(center),
        'cluster_enclosure_radius': qtext(rho),
        'complement_distance_from_center_lower': qtext(g),
        'contour_radius': qtext(radius),
        'resolvent_distance': qtext(distance),
        'cluster_radius_semantics': 'derived_uniform_supremum_over_exact_cell_cover',
        'complement_distance_semantics': 'derived_uniform_infimum_over_exact_cell_cover',
        'H_derivative_bounds': {name: qtext(value) for name, value in derivatives.items()},
        'norm': 'operator',
        'fixed_contour': True,
        'uniform_over_parameter_domain': True,
        'valid_parameter_domain': required,
        'required_parameter_domain': required,
        'contour_policy': evidence['contour_policy'],
        'source_evidence_id': evidence['evidence_id'],
        'assembly_evidence_id': assembly['evidence_id'],
        'assembly_artifact_sha256': assembly_digest,
        'derivative_contract_id': derivative_id
    }
    outputs = {
        'P1': qtext(p1), 'P2': qtext(p2), 'P3': qtext(p3),
        'K': qtext(p1), 'K1': qtext(p2), 'K2': qtext(p3 + 2 * p2 * p1),
        'norm': 'operator', 'valid_parameter_domain': required
    }
    return {
        'status': 'PASS_SYNTHETIC_S1_WINDOW_TO_CONTRACT',
        'physical_status': 'DECLARED_UNEXECUTED',
        'eligible_for_physical_transport': False,
        'inputs': inputs,
        'outputs': outputs,
        'coverage': {'cell_count': len(cells), 'exact_cover': True,
                     'required_parameter_domain': required},
        'global_window': {
            'cluster_lower': qtext(global_low), 'cluster_upper': qtext(global_high),
            'nearest_lower_complement_upper': qtext(lower_nearest),
            'nearest_upper_complement_lower': qtext(upper_nearest)
        }
    }


def mutation_controls(evidence, assembly, assembly_digest):
    controls = []

    def run(name, expected, change):
        trial = copy.deepcopy(evidence)
        trial_assembly = copy.deepcopy(assembly)
        change(trial, trial_assembly)
        try:
            derive_contract(trial, trial_assembly, assembly_digest)
        except ValueError as exc:
            need(str(exc) == expected, f'WRONG_REFUSAL:{name}:{exc}')
            controls.append({'id': name, 'error': expected})
        else:
            raise ValueError('WINDOW_MUTATION_ACCEPTED:' + name)

    run('wrong_schema', 'WINDOW_EVIDENCE_SCHEMA_REQUIRED',
        lambda e, a: e.update(schema='other'))
    run('physical_scope_not_accepted', 'PHYSICAL_S1_EVIDENCE_REQUIRED',
        lambda e, a: e.update(evidence_scope='physical_s1_retained'))
    run('physical_evaluation_claim', 'ZERO_PHYSICAL_EVALUATIONS_REQUIRED',
        lambda e, a: e.update(physical_model_evaluations=1))
    run('assembly_hash_mismatch', 'ASSEMBLY_ARTIFACT_HASH_MISMATCH',
        lambda e, a: e.update(assembly_artifact_sha256='0' * 64))
    run('contour_policy_missing', 'CONTOUR_POLICY_REQUIRED',
        lambda e, a: e.pop('contour_policy'))
    run('invalid_required_domain', 'INVALID_REQUIRED_DOMAIN',
        lambda e, a: e['required_parameter_domain'].update(x=['1/8', '0']))
    run('cell_outside_domain', 'CELL_OUTSIDE_REQUIRED_DOMAIN',
        lambda e, a: e['cells'][0]['domain'].update(x=['-1/16', '1/16']))
    run('coverage_gap', 'COVERAGE_GAP', lambda e, a: e['cells'].pop())
    run('coverage_overlap', 'COVERAGE_OVERLAP',
        lambda e, a: e['cells'][0]['domain'].update(x=['0', '1/8']))
    run('duplicate_cell_id', 'DUPLICATE_CELL_ID',
        lambda e, a: e['cells'][1].update(cell_id=e['cells'][0]['cell_id']))
    run('uncertified_cell', 'UNCERTIFIED_WINDOW_CELL',
        lambda e, a: e['cells'][0].update(status='INCONCLUSIVE'))
    run('assembly_provenance_mismatch', 'ASSEMBLY_PROVENANCE_MISMATCH',
        lambda e, a: e['cells'][0].update(assembly_evidence_id='other'))
    run('self_adjoint_missing', 'SELF_ADJOINT_EVIDENCE_REQUIRED',
        lambda e, a: e['cells'][0].update(self_adjoint=False))
    run('selected_indices_mismatch', 'SELECTED_INDICES_MISMATCH',
        lambda e, a: e['cells'][0].update(selected_zero_based_indices=[0, 1]))
    run('spectral_order_invalid', 'CELL_SPECTRAL_ORDER_INVALID',
        lambda e, a: e['cells'][0].update(lower_complement_upper='0'))
    run('missing_spectral_bound', 'MISSING_SPECTRAL_BOUND',
        lambda e, a: e['cells'][0].pop('upper_complement_lower'))
    run('invalid_rational', 'INVALID_RATIONAL',
        lambda e, a: e['cells'][0].update(cluster_lower='not-rational'))
    run('missing_derivative', 'UNBOUND_DERIVATIVE_INPUT',
        lambda e, a: e['cells'][0]['H_derivative_bounds'].pop('H3'))
    run('negative_derivative', 'NEGATIVE_DERIVATIVE_BOUND',
        lambda e, a: e['cells'][0]['H_derivative_bounds'].update(H2='-1'))
    run('derivative_provenance_mismatch', 'DERIVATIVE_PROVENANCE_MISMATCH',
        lambda e, a: e['cells'][0].update(derivative_contract_id='other'))

    def destroy_global_separation(e, a):
        e['cells'][3].update(cluster_lower='-10', cluster_upper='-9',
                             lower_complement_upper='-11', upper_complement_lower='-8')
    run('uniform_separation_missing', 'UNIFORM_SEPARATION_REQUIRED',
        destroy_global_separation)
    return controls


def worker():
    evidence_path = HERE / 'SYNTHETIC_WINDOW_EVIDENCE.json'
    assembly_path = HERE / 'SYNTHETIC_AFFINE_ASSEMBLY.json'
    evidence = json.loads(evidence_path.read_text())
    assembly = json.loads(assembly_path.read_text())
    digest = sha(assembly_path)
    contract = derive_contract(evidence, assembly, digest)
    controls = mutation_controls(evidence, assembly, digest)
    return {
        'status': 'PASS_SYNTHETIC_S1_WINDOW_ADAPTER_AND_REFUSALS',
        'physical_status': 'DECLARED_UNEXECUTED',
        'physical_model_evaluations': 0,
        'evidence_sha256': sha(evidence_path),
        'assembly_sha256': digest,
        'contract': contract,
        'refusal_controls': controls
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.worker:
        start = time.monotonic()
        result = worker()
        result['wall_seconds'] = time.monotonic() - start
        print(json.dumps(result, sort_keys=True))
        return
    need(args.output is not None, 'OUTPUT_REQUIRED')
    spec = json.loads((HERE / 'SPEC.json').read_text())
    for path, digest in spec['dependencies'].items():
        need(sha(HERE.parent / path) == digest, 'DEPENDENCY_HASH')
    out = begin(args.output)
    for path in list(spec['dependencies']) + [
        f'certification_s0y_001/{name}' for name in
        ('check.py', 'verify.py', 'SPEC.json', 'SYNTHETIC_AFFINE_ASSEMBLY.json',
         'SYNTHETIC_WINDOW_EVIDENCE.json')]:
        destination = out / 'SOURCE' / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE.parent / path, destination)
    shutil.copyfile(HERE.parents[2] / 'docs/certification-readiness/S0Y_S1_WINDOW_ADAPTER.md',
                    out / 'S0Y_S1_WINDOW_ADAPTER.md')
    atomic_json(out / 'ENVIRONMENT.json', {
        'python': platform.python_version(), 'machine': platform.machine(),
        'system': platform.system(), 'arithmetic': 'fractions.Fraction',
        'threads': 1, 'physical_model_evaluations': 0
    })
    frozen = out / 'SOURCE/certification_s0y_001/check.py'
    run = subprocess.run([sys.executable, '-B', str(frozen), '--worker'],
                         capture_output=True, text=True, timeout=10)
    need(run.returncode == 0, run.stderr)
    result = json.loads(run.stdout)
    finish(out, result)
    print(json.dumps(verify(out), sort_keys=True))
    print(json.dumps({'status': result['status'],
                      'refusals': len(result['refusal_controls']),
                      'wall_seconds': result['wall_seconds']}, sort_keys=True))


if __name__ == '__main__':
    main()
