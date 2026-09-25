#!/usr/bin/env python3
"""Independent exact checks for the S0ab triple-binding packet."""
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'certification_s0b_001'))
from runner_io import begin, sha, verify


def need(ok, message):
    if not ok:
        raise ValueError(message)


def qtext(value):
    value = Q(value)
    return str(value.numerator) if value.denominator == 1 else f'{value.numerator}/{value.denominator}'


def main():
    out = HERE / 'RUN'
    integrity = verify(out)
    result = json.loads((out / 'RESULTS.json').read_text())
    spec = json.loads((HERE / 'SPEC.json').read_text())
    evidence_path = HERE / 'SYNTHETIC_WINDOW_EVIDENCE.json'
    assembly_path = HERE / 'SYNTHETIC_AFFINE_ASSEMBLY.json'
    path_path = HERE / 'SYNTHETIC_PATH_EVIDENCE.json'
    evidence = json.loads(evidence_path.read_text())
    assembly = json.loads(assembly_path.read_text())
    path = json.loads(path_path.read_text())
    need(result['status'] == 'PASS_SYNTHETIC_TRIPLE_BINDING_AND_REFUSALS', 'summary')
    need(result['physical_status'] == 'DECLARED_UNEXECUTED' and
         result['physical_model_evaluations'] == 0, 'physical boundary')
    for name, artifact, digest_key in (
            ('SYNTHETIC_WINDOW_EVIDENCE.json', evidence_path, 'evidence_sha256'),
            ('SYNTHETIC_AFFINE_ASSEMBLY.json', assembly_path, 'assembly_sha256'),
            ('SYNTHETIC_PATH_EVIDENCE.json', path_path, 'path_sha256')):
        need(result[digest_key] == sha(artifact) == spec['fixture_sha256'][name],
             name + ' binding')
    need(evidence['assembly_artifact_sha256'] == path['assembly_artifact_sha256'] ==
         sha(assembly_path), 'assembly links')
    need(evidence['path_artifact_sha256'] == sha(path_path), 'path link')

    constant = list(map(Q, assembly['constant_diagonal']))
    xcoef = list(map(Q, assembly['x_coefficient_diagonal']))
    ycoef = list(map(Q, assembly['y_coefficient_diagonal']))
    need(constant == [Q(-3), Q(-1, 3), Q(1, 3), Q(3)], 'constant diagonal')
    need(xcoef == [Q(-1), Q(1), 0, 0] and ycoef == [0, 0, Q(-1), Q(1)],
         'affine coefficient diagonals')
    need(assembly['matrix_formula'] == 'diag(-3-x,-1/3+x,1/3-y,3+y)',
         'assembly formula')

    t0, t1 = map(Q, path['parameter_domain']['t'])
    xline = list(map(Q, path['coordinate_formula']['x']))
    yline = list(map(Q, path['coordinate_formula']['y']))
    endpoints = {'x': [xline[0] + xline[1] * t0, xline[0] + xline[1] * t1],
                 'y': [yline[0] + yline[1] * t0, yline[0] + yline[1] * t1]}
    need(endpoints == {'x': [Q(0), Q(1, 8)], 'y': [Q(0), Q(1, 16)]},
         'path endpoints')
    gamma1 = [xline[1], yline[1]]
    gamma2 = gamma3 = [Q(0), Q(0)]
    need(list(map(Q, path['declared_path_derivatives']['gamma1'])) == gamma1 and
         list(map(Q, path['declared_path_derivatives']['gamma2'])) == gamma2 and
         list(map(Q, path['declared_path_derivatives']['gamma3'])) == gamma3,
         'path derivatives')
    h_diagonals = {
        'H1': [gamma1[0] * x + gamma1[1] * y for x, y in zip(xcoef, ycoef)],
        'H2': [Q(0)] * 4,
        'H3': [Q(0)] * 4
    }
    for name, values in h_diagonals.items():
        need(list(map(Q, path['declared_H_path_derivative_diagonals'][name])) == values,
             name + ' chain rule')
    derivative_bounds = {name: qtext(max(map(abs, values)))
                         for name, values in h_diagonals.items()}
    need(derivative_bounds == {'H1': '1', 'H2': '0', 'H3': '0'},
         'derived operator norms')

    cells = evidence['cells']
    need(len(cells) == spec['expected']['cells'], 'cell count')
    for cell in cells:
        x0, x1 = map(Q, cell['domain']['x'])
        y0, y1 = map(Q, cell['domain']['y'])
        need(x0 < x1 and y0 < y1, 'cell geometry')
        need(Q(cell['cluster_lower']) == Q(-1, 3) + x0, 'cluster lower derivation')
        need(Q(cell['cluster_upper']) == Q(1, 3) - y0, 'cluster upper derivation')
        need(Q(cell['lower_complement_upper']) == -3 - x0, 'lower complement derivation')
        need(Q(cell['upper_complement_lower']) == 3 + y0, 'upper complement derivation')
        need('H_derivative_bounds' not in cell and 'derivative_contract_id' not in cell,
             'no cell derivative inputs')

    contract = result['contract']
    need(contract['status'] == 'PASS_SYNTHETIC_PATH_BOUND_WINDOW_TO_CONTRACT' and
         contract['physical_status'] == 'DECLARED_UNEXECUTED' and
         contract['eligible_for_physical_transport'] is False, 'contract boundary')
    proof = contract['path_proof']
    need(proof['path_parameter_domain'] == {'t': ['0', '1/8']} and
         proof['path_coordinate_endpoints'] == {'x': ['0', '1/8'], 'y': ['0', '1/16']} and
         proof['cover_containment'] is True, 'path proof')
    need(proof['H_derivative_bounds'] == derivative_bounds, 'path-derived bounds')
    need(contract['coverage'] == {
        'cell_count': 4, 'exact_cover': True,
        'window_parameter_domain': {'x': ['0', '1/8'], 'y': ['0', '1/8']},
        'path_contained_in_window_cover': True
    }, 'coverage')
    need(contract['global_window'] == {
        'cluster_lower': '-1/3', 'cluster_upper': '1/3',
        'nearest_lower_complement_upper': '-3',
        'nearest_upper_complement_lower': '3'
    }, 'global window')
    inputs, expected = contract['inputs'], spec['expected']
    need(inputs['binding_spec_sha256'] == result['binding_spec_sha256'] == sha(HERE / 'SPEC.json'),
         'binding spec identity')
    need(inputs['window_artifact_sha256'] == result['evidence_sha256'] == sha(evidence_path),
         'window contract identity')
    need(inputs['assembly_artifact_sha256'] == result['assembly_sha256'] == sha(assembly_path) and
         inputs['path_artifact_sha256'] == result['path_sha256'] == sha(path_path),
         'assembly/path contract identity')
    for key in ('cluster_center', 'cluster_enclosure_radius',
                'complement_distance_from_center_lower', 'contour_radius',
                'resolvent_distance'):
        need(inputs[key] == expected[key], 'derived geometry ' + key)
    need(inputs['H_derivative_bounds'] == expected['H_derivative_bounds'] and
         inputs['H_derivative_semantics'] ==
         'derived_from_hash_bound_affine_assembly_and_exact_path', 'derivative provenance')
    need(inputs['valid_parameter_domain'] == expected['path_domain'] and
         inputs['window_parameter_domain'] == {'x': ['0', '1/8'], 'y': ['0', '1/8']},
         'domain separation')
    rho = Q(inputs['cluster_enclosure_radius'])
    g = Q(inputs['complement_distance_from_center_lower'])
    radius, distance = Q(inputs['contour_radius']), Q(inputs['resolvent_distance'])
    need(radius == (rho + g) / 2 and distance == min(radius - rho, g - radius) > 0,
         'max-margin contour')
    h1, h2, h3 = (Q(derivative_bounds[name]) for name in ('H1', 'H2', 'H3'))
    p1 = radius * h1 / distance**2
    p2 = radius * (2 * h1**2 / distance**3 + h2 / distance**2)
    p3 = radius * (6 * h1**3 / distance**4 + 6 * h1 * h2 / distance**3 +
                   h3 / distance**2)
    outputs = contract['outputs']
    derived = {'K': p1, 'K1': p2, 'K2': p3 + 2 * p2 * p1}
    for name, value in derived.items():
        need(outputs[name] == qtext(value) == expected[name], 'derived bound ' + name)

    expected_refusals = [
        ('wrong_schema', 'WINDOW_EVIDENCE_SCHEMA_REQUIRED'),
        ('physical_scope_not_accepted', 'PHYSICAL_S1_EVIDENCE_REQUIRED'),
        ('physical_evaluation_claim', 'ZERO_PHYSICAL_EVALUATIONS_REQUIRED'),
        ('assembly_hash_mismatch', 'ASSEMBLY_ARTIFACT_HASH_MISMATCH'),
        ('path_hash_mismatch', 'PATH_ARTIFACT_HASH_MISMATCH'),
        ('contour_policy_missing', 'CONTOUR_POLICY_REQUIRED'),
        ('invalid_required_domain', 'INVALID_REQUIRED_DOMAIN'),
        ('cell_outside_domain', 'CELL_OUTSIDE_REQUIRED_DOMAIN'),
        ('coverage_gap', 'COVERAGE_GAP'),
        ('coverage_overlap', 'COVERAGE_OVERLAP'),
        ('duplicate_cell_id', 'DUPLICATE_CELL_ID'),
        ('uncertified_cell', 'UNCERTIFIED_WINDOW_CELL'),
        ('assembly_provenance_mismatch', 'ASSEMBLY_PROVENANCE_MISMATCH'),
        ('self_adjoint_missing', 'SELF_ADJOINT_EVIDENCE_REQUIRED'),
        ('selected_indices_mismatch', 'SELECTED_INDICES_MISMATCH'),
        ('spectral_order_invalid', 'CELL_SPECTRAL_ORDER_INVALID'),
        ('missing_spectral_bound', 'MISSING_SPECTRAL_BOUND'),
        ('invalid_rational', 'INVALID_RATIONAL'),
        ('cell_derivative_understatement', 'CELL_DERIVATIVE_OVERRIDE_FORBIDDEN'),
        ('uniform_separation_missing', 'UNIFORM_SEPARATION_REQUIRED'),
        ('assembly_schema_missing', 'ASSEMBLY_SCHEMA_REQUIRED'),
        ('assembly_coefficient_missing', 'ASSEMBLY_COEFFICIENT_REQUIRED'),
        ('assembly_formula_mismatch', 'ASSEMBLY_FORMULA_MISMATCH'),
        ('path_schema_missing', 'PATH_SCHEMA_REQUIRED'),
        ('path_assembly_binding_mismatch', 'PATH_ASSEMBLY_BINDING_MISMATCH'),
        ('invalid_path_domain', 'INVALID_PATH_DOMAIN'),
        ('path_outside_window_domain', 'PATH_OUTSIDE_WINDOW_DOMAIN'),
        ('path_derivative_mismatch', 'PATH_DERIVATIVE_MISMATCH'),
        ('path_H_derivative_mismatch', 'PATH_H_DERIVATIVE_MISMATCH'),
        ('path_operator_norm_missing', 'OPERATOR_NORM_REQUIRED'),
        ('path_consistent_content_old_digest', 'PATH_ARTIFACT_HASH_MISMATCH'),
        ('window_consistent_content_old_digest', 'WINDOW_ARTIFACT_HASH_MISMATCH')
    ]
    need(result['refusal_controls'] == [dict(id=name, error=error)
                                        for name, error in expected_refusals], 'refusal controls')
    need(len(expected_refusals) == spec['expected']['refusal_controls'], 'refusal count')

    for source in (out / 'SOURCE').rglob('*'):
        if source.is_file():
            need(sha(source) == sha(HERE.parent / source.relative_to(out / 'SOURCE')),
                 'source binding')
    need(sha(out / 'S0AB_TRIPLE_BINDING.md') ==
         sha(HERE.parents[2] / 'docs/certification-readiness/S0AB_TRIPLE_BINDING.md'),
         'note binding')
    with tempfile.TemporaryDirectory() as temporary:
        copied = Path(temporary) / 'SOURCE'
        shutil.copytree(out / 'SOURCE', copied)
        changed_path = copied / 'certification_s0ab_001/SYNTHETIC_PATH_EVIDENCE.json'
        changed = json.loads(changed_path.read_text())
        changed['coordinate_formula'] = {'x': ['0', '1/2'], 'y': ['0', '1/4']}
        changed['declared_path_derivatives'] = {
            'gamma1': ['1/2', '1/4'], 'gamma2': ['0', '0'], 'gamma3': ['0', '0']}
        changed['declared_H_path_derivative_diagonals'] = {
            'H1': ['-1/2', '1/2', '-1/4', '1/4'],
            'H2': ['0', '0', '0', '0'], 'H3': ['0', '0', '0', '0']}
        changed_path.write_text(
            json.dumps(changed, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        probe = subprocess.run(
            [sys.executable, '-B',
             str(copied / 'certification_s0ab_001/check.py'), '--worker'],
            capture_output=True, text=True, timeout=10)
        need(probe.returncode != 0 and
             'PATH_ARTIFACT_HASH_MISMATCH' in (probe.stderr + probe.stdout),
             'consistent-content old-digest refusal')
    with tempfile.TemporaryDirectory() as temporary:
        copied = Path(temporary) / 'SOURCE'
        shutil.copytree(out / 'SOURCE', copied)
        changed_window = copied / 'certification_s0ab_001/SYNTHETIC_WINDOW_EVIDENCE.json'
        changed = json.loads(changed_window.read_text())
        changed['cells'].reverse()
        changed_window.write_text(
            json.dumps(changed, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        probe = subprocess.run(
            [sys.executable, '-B',
             str(copied / 'certification_s0ab_001/check.py'), '--worker'],
            capture_output=True, text=True, timeout=10)
        need(probe.returncode != 0 and
             'WINDOW_ARTIFACT_HASH_MISMATCH' in (probe.stderr + probe.stdout),
             'consistent-window old-digest refusal')
    controls = ['intact']
    for name, relative in [('result', 'RESULTS.json'), ('environment', 'ENVIRONMENT.json'),
                           ('source', 'SOURCE/certification_s0ab_001/check.py'),
                           ('path', 'SOURCE/certification_s0ab_001/SYNTHETIC_PATH_EVIDENCE.json'),
                           ('marker', 'COMPLETE.json')]:
        with tempfile.TemporaryDirectory() as temporary:
            copy = Path(temporary) / 'run'
            shutil.copytree(out, copy)
            target = copy / relative
            if name == 'marker':
                target.unlink()
            else:
                with target.open('a') as stream:
                    stream.write('\nTAMPERED\n')
            try:
                verify(copy)
            except (ValueError, FileNotFoundError, json.JSONDecodeError):
                controls.append(name + '_refused')
            else:
                raise ValueError('mutation accepted: ' + name)
    try:
        begin(out)
    except FileExistsError:
        controls.append('overwrite_refused')
    else:
        raise ValueError('overwrite accepted')
    print(json.dumps({
        'status': 'PASS_SYNTHETIC_TRIPLE_BINDING_PROTOCOL',
        'cells': len(cells), 'refusal_controls': len(expected_refusals),
        'contracts': 1, 'physical_model_evaluations': 0,
        'files': integrity['files'], 'controls': controls
    }, sort_keys=True))


if __name__ == '__main__':
    main()
