#!/usr/bin/env python3
"""Independent exact checks for the S0y retained adapter packet."""
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
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
    evidence = json.loads(evidence_path.read_text())
    assembly = json.loads(assembly_path.read_text())
    need(result['status'] == 'PASS_SYNTHETIC_S1_WINDOW_ADAPTER_AND_REFUSALS', 'summary')
    need(result['physical_status'] == 'DECLARED_UNEXECUTED' and
         result['physical_model_evaluations'] == 0, 'physical boundary')
    need(result['evidence_sha256'] == sha(evidence_path) ==
         spec['fixture_sha256']['SYNTHETIC_WINDOW_EVIDENCE.json'], 'evidence binding')
    need(result['assembly_sha256'] == sha(assembly_path) ==
         spec['fixture_sha256']['SYNTHETIC_AFFINE_ASSEMBLY.json'], 'assembly binding')
    need(evidence['assembly_artifact_sha256'] == sha(assembly_path), 'evidence assembly binding')
    need(assembly['matrix_formula'] == 'diag(-3-x,-1/3+x,1/3-y,3+y)', 'assembly formula')
    need(assembly['physical_model_evaluations'] == 0 and
         assembly['evidence_scope'] == 'synthetic_shape_fixture', 'assembly scope')

    cells = evidence['cells']
    need(len(cells) == spec['expected']['cells'], 'cell count')
    for cell in cells:
        x0, x1 = map(Q, cell['domain']['x'])
        y0, y1 = map(Q, cell['domain']['y'])
        need(x0 < x1 and y0 < y1, 'cell geometry')
        need(Q(cell['cluster_lower']) == Q(-1, 3) + x0, 'cluster lower derivation')
        need(Q(cell['cluster_upper']) == Q(1, 3) - y0, 'cluster upper derivation')
        need(Q(cell['lower_complement_upper']) == -3 - x0,
             'lower complement derivation')
        need(Q(cell['upper_complement_lower']) == 3 + y0,
             'upper complement derivation')
        need(cell['status'] == 'CERTIFIED_SYNTHETIC_WINDOW' and
             cell['self_adjoint'] is True, 'cell status')
        need(cell['H_derivative_bounds'] == {'H1': '1', 'H2': '0', 'H3': '0'},
             'derivative bounds')

    contract = result['contract']
    need(contract['status'] == 'PASS_SYNTHETIC_S1_WINDOW_TO_CONTRACT' and
         contract['physical_status'] == 'DECLARED_UNEXECUTED' and
         contract['eligible_for_physical_transport'] is False, 'contract boundary')
    need(contract['coverage'] == {
        'cell_count': 4, 'exact_cover': True,
        'required_parameter_domain': {'x': ['0', '1/8'], 'y': ['0', '1/8']}
    }, 'coverage')
    need(contract['global_window'] == {
        'cluster_lower': '-1/3', 'cluster_upper': '1/3',
        'nearest_lower_complement_upper': '-3',
        'nearest_upper_complement_lower': '3'
    }, 'global window')
    inputs = contract['inputs']
    expected = spec['expected']
    for key in ('cluster_center', 'cluster_enclosure_radius',
                'complement_distance_from_center_lower', 'contour_radius',
                'resolvent_distance'):
        need(inputs[key] == expected[key], 'derived geometry ' + key)
    need(inputs['cluster_center'] == inputs['contour_center'] == '0', 'fixed centre')
    need(inputs['fixed_contour'] is True and
         inputs['uniform_over_parameter_domain'] is True, 'derived flags')
    need(inputs['cluster_radius_semantics'] ==
         'derived_uniform_supremum_over_exact_cell_cover', 'cluster semantics')
    need(inputs['complement_distance_semantics'] ==
         'derived_uniform_infimum_over_exact_cell_cover', 'complement semantics')
    need(inputs['H_derivative_bounds'] == {'H1': '1', 'H2': '0', 'H3': '0'},
         'contract derivative bounds')
    rho, g = Q(inputs['cluster_enclosure_radius']), Q(inputs['complement_distance_from_center_lower'])
    radius, distance = Q(inputs['contour_radius']), Q(inputs['resolvent_distance'])
    need(radius == (rho + g) / 2 and distance == min(radius - rho, g - radius) > 0,
         'max-margin contour')
    h1, h2, h3 = (Q(inputs['H_derivative_bounds'][name]) for name in ('H1', 'H2', 'H3'))
    p1 = radius * h1 / distance**2
    p2 = radius * (2 * h1**2 / distance**3 + h2 / distance**2)
    p3 = radius * (6 * h1**3 / distance**4 +
                   6 * h1 * h2 / distance**3 + h3 / distance**2)
    outputs = contract['outputs']
    derived = {'K': p1, 'K1': p2, 'K2': p3 + 2 * p2 * p1}
    for key, value in derived.items():
        need(outputs[key] == qtext(value) == expected[key], 'derived bound ' + key)
    need(outputs['P1'] == qtext(p1) and outputs['P2'] == qtext(p2) and
         outputs['P3'] == qtext(p3), 'projector bounds')

    expected_refusals = [
        ('wrong_schema', 'WINDOW_EVIDENCE_SCHEMA_REQUIRED'),
        ('physical_scope_not_accepted', 'PHYSICAL_S1_EVIDENCE_REQUIRED'),
        ('physical_evaluation_claim', 'ZERO_PHYSICAL_EVALUATIONS_REQUIRED'),
        ('assembly_hash_mismatch', 'ASSEMBLY_ARTIFACT_HASH_MISMATCH'),
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
        ('missing_derivative', 'UNBOUND_DERIVATIVE_INPUT'),
        ('negative_derivative', 'NEGATIVE_DERIVATIVE_BOUND'),
        ('derivative_provenance_mismatch', 'DERIVATIVE_PROVENANCE_MISMATCH'),
        ('uniform_separation_missing', 'UNIFORM_SEPARATION_REQUIRED')
    ]
    need(result['refusal_controls'] == [dict(id=name, error=error)
                                        for name, error in expected_refusals], 'refusal controls')
    need(len(result['refusal_controls']) == spec['expected']['refusal_controls'],
         'refusal count')

    for path in (out / 'SOURCE').rglob('*'):
        if path.is_file():
            need(sha(path) == sha(HERE.parent / path.relative_to(out / 'SOURCE')),
                 'source binding')
    need(sha(out / 'S0Y_S1_WINDOW_ADAPTER.md') ==
         sha(HERE.parents[2] / 'docs/certification-readiness/S0Y_S1_WINDOW_ADAPTER.md'),
         'note binding')
    controls = ['intact']
    for name, relative in [('result', 'RESULTS.json'), ('environment', 'ENVIRONMENT.json'),
                           ('source', 'SOURCE/certification_s0y_001/check.py'),
                           ('evidence', 'SOURCE/certification_s0y_001/SYNTHETIC_WINDOW_EVIDENCE.json'),
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
        'status': 'PASS_SYNTHETIC_S1_WINDOW_ADAPTER_PROTOCOL',
        'cells': len(cells), 'refusal_controls': len(expected_refusals),
        'contracts': 1, 'physical_model_evaluations': 0,
        'files': integrity['files'], 'controls': controls
    }, sort_keys=True))


if __name__ == '__main__':
    main()
