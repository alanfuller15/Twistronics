#!/usr/bin/env python3
"""Bind exact synthetic path content to assembly-derived path derivatives."""
import argparse
import copy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
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


def vector(record, name, size, error):
    try:
        raw = record[name]
        need(isinstance(raw, list) and len(raw) == size, error)
        return [rational(value) for value in raw]
    except KeyError:
        raise ValueError(error) from None


def interval(record, axis, error):
    try:
        raw = record[axis]
        need(isinstance(raw, list) and len(raw) == 2, error)
        lo, hi = map(rational, raw)
    except (KeyError, TypeError):
        raise ValueError(error) from None
    need(lo < hi, error)
    return lo, hi


def canonical_rectangle(domain):
    return {axis: [qtext(value) for value in interval(domain, axis, 'INVALID_REQUIRED_DOMAIN')]
            for axis in ('x', 'y')}


def check_exact_cover(cells, required):
    req = {axis: interval(required, axis, 'INVALID_REQUIRED_DOMAIN') for axis in ('x', 'y')}
    boxes = []
    for cell in cells:
        box = {axis: interval(cell.get('domain', {}), axis, 'INVALID_CELL_DOMAIN')
               for axis in ('x', 'y')}
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


def derive_path_bounds(path, assembly, assembly_digest):
    need(assembly.get('schema') == 'synthetic_affine_self_adjoint_assembly_v2',
         'ASSEMBLY_SCHEMA_REQUIRED')
    need(assembly.get('evidence_scope') == 'synthetic_shape_fixture' and
         assembly.get('physical_model_evaluations') == 0,
         'ASSEMBLY_SCOPE_MISMATCH')
    need(assembly.get('self_adjoint_proof') == 'all exact coefficient matrices are real diagonal',
         'SELF_ADJOINT_ASSEMBLY_REQUIRED')
    constant = vector(assembly, 'constant_diagonal', 4, 'ASSEMBLY_COEFFICIENT_REQUIRED')
    xcoef = vector(assembly, 'x_coefficient_diagonal', 4, 'ASSEMBLY_COEFFICIENT_REQUIRED')
    ycoef = vector(assembly, 'y_coefficient_diagonal', 4, 'ASSEMBLY_COEFFICIENT_REQUIRED')
    need(constant == [Q(-3), Q(-1, 3), Q(1, 3), Q(3)] and
         xcoef == [Q(-1), Q(1), Q(0), Q(0)] and
         ycoef == [Q(0), Q(0), Q(-1), Q(1)] and
         assembly.get('matrix_formula') == 'diag(-3-x,-1/3+x,1/3-y,3+y)',
         'ASSEMBLY_FORMULA_MISMATCH')

    need(path.get('schema') == 'synthetic_exact_affine_path_v1', 'PATH_SCHEMA_REQUIRED')
    need(path.get('evidence_scope') == 'synthetic_shape_fixture' and
         path.get('physical_model_evaluations') == 0, 'PATH_SCOPE_MISMATCH')
    need(path.get('assembly_artifact') == 'SYNTHETIC_AFFINE_ASSEMBLY.json' and
         path.get('assembly_artifact_sha256') == assembly_digest,
         'PATH_ASSEMBLY_BINDING_MISMATCH')
    need(path.get('norm') == 'operator', 'OPERATOR_NORM_REQUIRED')
    t0, t1 = interval(path.get('parameter_domain', {}), 't', 'INVALID_PATH_DOMAIN')
    coordinates = path.get('coordinate_formula', {})
    xline = vector(coordinates, 'x', 2, 'PATH_FORMULA_REQUIRED')
    yline = vector(coordinates, 'y', 2, 'PATH_FORMULA_REQUIRED')
    declared = path.get('declared_path_derivatives', {})
    gamma1 = vector(declared, 'gamma1', 2, 'PATH_DERIVATIVE_REQUIRED')
    gamma2 = vector(declared, 'gamma2', 2, 'PATH_DERIVATIVE_REQUIRED')
    gamma3 = vector(declared, 'gamma3', 2, 'PATH_DERIVATIVE_REQUIRED')
    need(gamma1 == [xline[1], yline[1]] and gamma2 == [Q(0), Q(0)] and
         gamma3 == [Q(0), Q(0)], 'PATH_DERIVATIVE_MISMATCH')
    assembly_domain = {axis: interval(assembly.get('parameter_domain', {}), axis,
                                      'ASSEMBLY_DOMAIN_REQUIRED') for axis in ('x', 'y')}
    endpoint_coordinates = {
        'x': [xline[0] + xline[1] * t0, xline[0] + xline[1] * t1],
        'y': [yline[0] + yline[1] * t0, yline[0] + yline[1] * t1]
    }
    for axis, values in endpoint_coordinates.items():
        lo, hi = min(values), max(values)
        need(assembly_domain[axis][0] <= lo <= hi <= assembly_domain[axis][1],
             'PATH_OUTSIDE_WINDOW_DOMAIN')

    h1diag = [gamma1[0] * x + gamma1[1] * y for x, y in zip(xcoef, ycoef)]
    h2diag = [gamma2[0] * x + gamma2[1] * y for x, y in zip(xcoef, ycoef)]
    h3diag = [gamma3[0] * x + gamma3[1] * y for x, y in zip(xcoef, ycoef)]
    declared_h = path.get('declared_H_path_derivative_diagonals', {})
    for name, derived in (('H1', h1diag), ('H2', h2diag), ('H3', h3diag)):
        need(vector(declared_h, name, 4, 'PATH_H_DERIVATIVE_REQUIRED') == derived,
             'PATH_H_DERIVATIVE_MISMATCH')
    bounds = {name: max(map(abs, values))
              for name, values in (('H1', h1diag), ('H2', h2diag), ('H3', h3diag))}
    return {
        'path_parameter_domain': {'t': [qtext(t0), qtext(t1)]},
        'path_coordinate_endpoints': {
            axis: [qtext(value) for value in values]
            for axis, values in endpoint_coordinates.items()},
        'path_derivatives': {name: [qtext(value) for value in values]
                             for name, values in (('gamma1', gamma1),
                                                  ('gamma2', gamma2),
                                                  ('gamma3', gamma3))},
        'H_path_derivative_diagonals': {name: [qtext(value) for value in values]
                                        for name, values in (('H1', h1diag),
                                                             ('H2', h2diag),
                                                             ('H3', h3diag))},
        'H_derivative_bounds': {name: qtext(value) for name, value in bounds.items()},
        'cover_containment': True
    }


def _derive_contract_records(evidence, assembly, path, assembly_digest, path_digest):
    need(evidence.get('schema') == 'synthetic_s1_window_evidence_v2',
         'WINDOW_EVIDENCE_SCHEMA_REQUIRED')
    need(evidence.get('evidence_scope') == 'synthetic_shape_fixture',
         'PHYSICAL_S1_EVIDENCE_REQUIRED')
    need(evidence.get('physical_model_evaluations') == 0,
         'ZERO_PHYSICAL_EVALUATIONS_REQUIRED')
    need(evidence.get('assembly_artifact') == 'SYNTHETIC_AFFINE_ASSEMBLY.json' and
         evidence.get('assembly_artifact_sha256') == assembly_digest,
         'ASSEMBLY_ARTIFACT_HASH_MISMATCH')
    need(evidence.get('path_artifact') == 'SYNTHETIC_PATH_EVIDENCE.json' and
         evidence.get('path_artifact_sha256') == path_digest,
         'PATH_ARTIFACT_HASH_MISMATCH')
    need(evidence.get('contour_policy') == 'max_margin_midpoint_circle_v1',
         'CONTOUR_POLICY_REQUIRED')
    required = canonical_rectangle(evidence.get('required_parameter_domain', {}))
    need(canonical_rectangle(assembly.get('parameter_domain', {})) == required,
         'ASSEMBLY_DOMAIN_MISMATCH')
    selected = evidence.get('selected_zero_based_indices')
    need(isinstance(selected, list) and len(selected) == 2 and
         all(isinstance(value, int) for value in selected) and selected[1] == selected[0] + 1,
         'SELECTED_INDICES_REQUIRED')
    need(assembly.get('selected_zero_based_indices') == selected,
         'ASSEMBLY_SELECTED_INDICES_MISMATCH')
    path_proof = derive_path_bounds(path, assembly, assembly_digest)

    cells = evidence.get('cells')
    need(isinstance(cells, list) and cells, 'EMPTY_WINDOW_INVENTORY')
    ids = [cell.get('cell_id') for cell in cells]
    need(all(isinstance(value, str) and value for value in ids), 'CELL_ID_REQUIRED')
    need(len(ids) == len(set(ids)), 'DUPLICATE_CELL_ID')
    check_exact_cover(cells, evidence['required_parameter_domain'])
    parsed = []
    for cell in cells:
        need(cell.get('status') == 'CERTIFIED_SYNTHETIC_WINDOW', 'UNCERTIFIED_WINDOW_CELL')
        need(cell.get('assembly_evidence_id') == assembly.get('evidence_id'),
             'ASSEMBLY_PROVENANCE_MISMATCH')
        need(cell.get('self_adjoint') is True, 'SELF_ADJOINT_EVIDENCE_REQUIRED')
        need(cell.get('selected_zero_based_indices') == selected, 'SELECTED_INDICES_MISMATCH')
        need('H_derivative_bounds' not in cell and 'derivative_contract_id' not in cell,
             'CELL_DERIVATIVE_OVERRIDE_FORBIDDEN')
        try:
            row = {name: rational(cell[name]) for name in
                   ('cluster_lower', 'cluster_upper', 'lower_complement_upper',
                    'upper_complement_lower')}
        except KeyError:
            raise ValueError('MISSING_SPECTRAL_BOUND') from None
        need(row['lower_complement_upper'] < row['cluster_lower'] <=
             row['cluster_upper'] < row['upper_complement_lower'],
             'CELL_SPECTRAL_ORDER_INVALID')
        parsed.append(row)

    global_low = min(row['cluster_lower'] for row in parsed)
    global_high = max(row['cluster_upper'] for row in parsed)
    center = (global_low + global_high) / 2
    rho = max(center - global_low, global_high - center)
    lower_nearest = max(row['lower_complement_upper'] for row in parsed)
    upper_nearest = min(row['upper_complement_lower'] for row in parsed)
    g = min(center - lower_nearest, upper_nearest - center)
    need(g > rho, 'UNIFORM_SEPARATION_REQUIRED')
    radius = (rho + g) / 2
    distance = min(radius - rho, g - radius)
    need(distance > 0, 'POSITIVE_RESOLVENT_DISTANCE_REQUIRED')
    h1, h2, h3 = (rational(path_proof['H_derivative_bounds'][name])
                  for name in ('H1', 'H2', 'H3'))
    p1 = radius * h1 / distance**2
    p2 = radius * (2 * h1**2 / distance**3 + h2 / distance**2)
    p3 = radius * (6 * h1**3 / distance**4 +
                   6 * h1 * h2 / distance**3 + h3 / distance**2)
    path_domain = path_proof['path_parameter_domain']
    inputs = {
        'contract_id': 'synthetic_path_bound_contour_contract',
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
        'H_derivative_bounds': path_proof['H_derivative_bounds'],
        'H_derivative_semantics': 'derived_from_hash_bound_affine_assembly_and_exact_path',
        'norm': 'operator',
        'fixed_contour': True,
        'uniform_over_path_parameter_domain': True,
        'valid_parameter_domain': path_domain,
        'window_parameter_domain': required,
        'source_evidence_id': evidence['evidence_id'],
        'assembly_evidence_id': assembly['evidence_id'],
        'path_evidence_id': path['evidence_id'],
        'assembly_artifact_sha256': assembly_digest,
        'path_artifact_sha256': path_digest
    }
    outputs = {
        'P1': qtext(p1), 'P2': qtext(p2), 'P3': qtext(p3),
        'K': qtext(p1), 'K1': qtext(p2), 'K2': qtext(p3 + 2 * p2 * p1),
        'norm': 'operator', 'valid_parameter_domain': path_domain
    }
    return {
        'status': 'PASS_SYNTHETIC_PATH_BOUND_WINDOW_TO_CONTRACT',
        'physical_status': 'DECLARED_UNEXECUTED',
        'eligible_for_physical_transport': False,
        'inputs': inputs,
        'outputs': outputs,
        'path_proof': path_proof,
        'coverage': {'cell_count': len(cells), 'exact_cover': True,
                     'window_parameter_domain': required,
                     'path_contained_in_window_cover': True},
        'global_window': {
            'cluster_lower': qtext(global_low), 'cluster_upper': qtext(global_high),
            'nearest_lower_complement_upper': qtext(lower_nearest),
            'nearest_upper_complement_lower': qtext(upper_nearest)
        }
    }


def _load_bound_json(path):
    """Load one artifact and derive its identity inside the checked boundary."""
    raw = Path(path).read_bytes()
    try:
        record = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError('BOUND_ARTIFACT_JSON_REQUIRED') from None
    need(isinstance(record, dict), 'BOUND_ARTIFACT_OBJECT_REQUIRED')
    return record, hashlib.sha256(raw).hexdigest()


def derive_contract(evidence_path, assembly_path, path_path):
    """Derive only from accepted file paths; callers cannot inject stale digests."""
    evidence, _ = _load_bound_json(evidence_path)
    assembly, assembly_digest = _load_bound_json(assembly_path)
    path, path_digest = _load_bound_json(path_path)
    return _derive_contract_records(
        evidence, assembly, path, assembly_digest, path_digest)


def mutation_controls(evidence, assembly, path, assembly_digest, path_digest,
                      evidence_path, assembly_path, path_path):
    controls = []

    def run(name, expected, change):
        trial_e = copy.deepcopy(evidence)
        trial_a = copy.deepcopy(assembly)
        trial_p = copy.deepcopy(path)
        change(trial_e, trial_a, trial_p)
        try:
            _derive_contract_records(
                trial_e, trial_a, trial_p, assembly_digest, path_digest)
        except ValueError as exc:
            need(str(exc) == expected, f'WRONG_REFUSAL:{name}:{exc}')
            controls.append({'id': name, 'error': expected})
        else:
            raise ValueError('MUTATION_ACCEPTED:' + name)

    cases = [
        ('wrong_schema', 'WINDOW_EVIDENCE_SCHEMA_REQUIRED', lambda e, a, p: e.update(schema='other')),
        ('physical_scope_not_accepted', 'PHYSICAL_S1_EVIDENCE_REQUIRED', lambda e, a, p: e.update(evidence_scope='physical')),
        ('physical_evaluation_claim', 'ZERO_PHYSICAL_EVALUATIONS_REQUIRED', lambda e, a, p: e.update(physical_model_evaluations=1)),
        ('assembly_hash_mismatch', 'ASSEMBLY_ARTIFACT_HASH_MISMATCH', lambda e, a, p: e.update(assembly_artifact_sha256='0' * 64)),
        ('path_hash_mismatch', 'PATH_ARTIFACT_HASH_MISMATCH', lambda e, a, p: e.update(path_artifact_sha256='0' * 64)),
        ('contour_policy_missing', 'CONTOUR_POLICY_REQUIRED', lambda e, a, p: e.pop('contour_policy')),
        ('invalid_required_domain', 'INVALID_REQUIRED_DOMAIN', lambda e, a, p: e['required_parameter_domain'].update(x=['1/8', '0'])),
        ('cell_outside_domain', 'CELL_OUTSIDE_REQUIRED_DOMAIN', lambda e, a, p: e['cells'][0]['domain'].update(x=['-1/16', '1/16'])),
        ('coverage_gap', 'COVERAGE_GAP', lambda e, a, p: e['cells'].pop()),
        ('coverage_overlap', 'COVERAGE_OVERLAP', lambda e, a, p: e['cells'][0]['domain'].update(x=['0', '1/8'])),
        ('duplicate_cell_id', 'DUPLICATE_CELL_ID', lambda e, a, p: e['cells'][1].update(cell_id=e['cells'][0]['cell_id'])),
        ('uncertified_cell', 'UNCERTIFIED_WINDOW_CELL', lambda e, a, p: e['cells'][0].update(status='INCONCLUSIVE')),
        ('assembly_provenance_mismatch', 'ASSEMBLY_PROVENANCE_MISMATCH', lambda e, a, p: e['cells'][0].update(assembly_evidence_id='other')),
        ('self_adjoint_missing', 'SELF_ADJOINT_EVIDENCE_REQUIRED', lambda e, a, p: e['cells'][0].update(self_adjoint=False)),
        ('selected_indices_mismatch', 'SELECTED_INDICES_MISMATCH', lambda e, a, p: e['cells'][0].update(selected_zero_based_indices=[0, 1])),
        ('spectral_order_invalid', 'CELL_SPECTRAL_ORDER_INVALID', lambda e, a, p: e['cells'][0].update(lower_complement_upper='0')),
        ('missing_spectral_bound', 'MISSING_SPECTRAL_BOUND', lambda e, a, p: e['cells'][0].pop('upper_complement_lower')),
        ('invalid_rational', 'INVALID_RATIONAL', lambda e, a, p: e['cells'][0].update(cluster_lower='not-rational')),
        ('cell_derivative_understatement', 'CELL_DERIVATIVE_OVERRIDE_FORBIDDEN', lambda e, a, p: e['cells'][0].update(H_derivative_bounds={'H1': '0', 'H2': '0', 'H3': '0'})),
        ('uniform_separation_missing', 'UNIFORM_SEPARATION_REQUIRED', lambda e, a, p: e['cells'][3].update(cluster_lower='-10', cluster_upper='-9', lower_complement_upper='-11', upper_complement_lower='-8')),
        ('assembly_schema_missing', 'ASSEMBLY_SCHEMA_REQUIRED', lambda e, a, p: a.update(schema='other')),
        ('assembly_coefficient_missing', 'ASSEMBLY_COEFFICIENT_REQUIRED', lambda e, a, p: a.pop('x_coefficient_diagonal')),
        ('assembly_formula_mismatch', 'ASSEMBLY_FORMULA_MISMATCH', lambda e, a, p: a['x_coefficient_diagonal'].__setitem__(0, '0')),
        ('path_schema_missing', 'PATH_SCHEMA_REQUIRED', lambda e, a, p: p.update(schema='other')),
        ('path_assembly_binding_mismatch', 'PATH_ASSEMBLY_BINDING_MISMATCH', lambda e, a, p: p.update(assembly_artifact_sha256='0' * 64)),
        ('invalid_path_domain', 'INVALID_PATH_DOMAIN', lambda e, a, p: p['parameter_domain'].update(t=['1/8', '0'])),
        ('path_outside_window_domain', 'PATH_OUTSIDE_WINDOW_DOMAIN', lambda e, a, p: p['coordinate_formula'].update(y=['1/4', '1/2'])),
        ('path_derivative_mismatch', 'PATH_DERIVATIVE_MISMATCH', lambda e, a, p: p['declared_path_derivatives'].update(gamma1=['0', '0'])),
        ('path_H_derivative_mismatch', 'PATH_H_DERIVATIVE_MISMATCH', lambda e, a, p: p['declared_H_path_derivative_diagonals'].update(H1=['0', '0', '0', '0'])),
        ('path_operator_norm_missing', 'OPERATOR_NORM_REQUIRED', lambda e, a, p: p.update(norm='frobenius')),
    ]
    for name, expected, change in cases:
        run(name, expected, change)
    with tempfile.TemporaryDirectory(prefix='s0aa-content-binding-') as temporary:
        root = Path(temporary)
        copied_evidence = root / evidence_path.name
        copied_assembly = root / assembly_path.name
        copied_path = root / path_path.name
        shutil.copyfile(evidence_path, copied_evidence)
        shutil.copyfile(assembly_path, copied_assembly)
        changed = copy.deepcopy(path)
        changed['coordinate_formula'] = {'x': ['0', '1/2'], 'y': ['0', '1/4']}
        changed['declared_path_derivatives'] = {
            'gamma1': ['1/2', '1/4'],
            'gamma2': ['0', '0'],
            'gamma3': ['0', '0']
        }
        changed['declared_H_path_derivative_diagonals'] = {
            'H1': ['-1/2', '1/2', '-1/4', '1/4'],
            'H2': ['0', '0', '0', '0'],
            'H3': ['0', '0', '0', '0']
        }
        copied_path.write_text(
            json.dumps(changed, indent=2, sort_keys=True) + '\n',
            encoding='utf-8')
        try:
            derive_contract(copied_evidence, copied_assembly, copied_path)
        except ValueError as exc:
            need(str(exc) == 'PATH_ARTIFACT_HASH_MISMATCH',
                 'WRONG_REFUSAL:path_consistent_content_old_digest:' + str(exc))
            controls.append({
                'id': 'path_consistent_content_old_digest',
                'error': 'PATH_ARTIFACT_HASH_MISMATCH'
            })
        else:
            raise ValueError(
                'MUTATION_ACCEPTED:path_consistent_content_old_digest')
    return controls


def worker():
    evidence_path = HERE / 'SYNTHETIC_WINDOW_EVIDENCE.json'
    assembly_path = HERE / 'SYNTHETIC_AFFINE_ASSEMBLY.json'
    path_path = HERE / 'SYNTHETIC_PATH_EVIDENCE.json'
    evidence, _ = _load_bound_json(evidence_path)
    assembly, assembly_digest = _load_bound_json(assembly_path)
    path, path_digest = _load_bound_json(path_path)
    contract = derive_contract(evidence_path, assembly_path, path_path)
    controls = mutation_controls(
        evidence, assembly, path, assembly_digest, path_digest,
        evidence_path, assembly_path, path_path)
    return {
        'status': 'PASS_SYNTHETIC_INTRINSIC_CONTENT_BINDING_AND_REFUSALS',
        'physical_status': 'DECLARED_UNEXECUTED',
        'physical_model_evaluations': 0,
        'evidence_sha256': sha(evidence_path),
        'assembly_sha256': assembly_digest,
        'path_sha256': path_digest,
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
    for name, digest in spec['fixture_sha256'].items():
        need(sha(HERE / name) == digest, 'FIXTURE_HASH')
    out = begin(args.output)
    source_names = ('check.py', 'verify.py', 'SPEC.json',
                    'SYNTHETIC_AFFINE_ASSEMBLY.json', 'SYNTHETIC_PATH_EVIDENCE.json',
                    'SYNTHETIC_WINDOW_EVIDENCE.json')
    for path in list(spec['dependencies']) + [f'certification_s0aa_001/{name}' for name in source_names]:
        destination = out / 'SOURCE' / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE.parent / path, destination)
    shutil.copyfile(HERE.parents[2] / 'docs/certification-readiness/S0AA_CONTENT_BINDING.md',
                    out / 'S0AA_CONTENT_BINDING.md')
    atomic_json(out / 'ENVIRONMENT.json', {
        'python': platform.python_version(), 'machine': platform.machine(),
        'system': platform.system(), 'arithmetic': 'fractions.Fraction',
        'threads': 1, 'physical_model_evaluations': 0
    })
    frozen = out / 'SOURCE/certification_s0aa_001/check.py'
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
