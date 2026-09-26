"""Isolate an existing assembly discrepancy without choosing a paper convention."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import numpy as np
import scipy

ROOT = Path(__file__).resolve().parent
MODEL = ROOT.parent / 'vafek_2025' / 'model.py'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def matrix(a):
    return {'real': a.real.tolist(), 'imag': a.imag.tolist()}


def main(output):
    if output.exists():
        raise FileExistsError('Refusing to replace a retained diagnostic: ' + str(output))
    plan = json.loads((ROOT / 'PLAN.json').read_text())
    if sha(MODEL) != plan['model_sha256']:
        raise RuntimeError('Baseline model source mismatch')
    sys.path.insert(0, str(MODEL.parent))
    from model import Model
    rows = []
    tolerance = plan['formula_and_hermiticity_tolerance_meV']
    for case in plan['cases']:
        model = Model(case['parameters'])
        x, y = case['K']; q = case['Q']
        dp = 1 + (x + q/2)**2 + y*y
        dm = 1 + (x - q/2)**2 + y*y
        amplitude = 4 * model.p['cpp'] * model.eps * y
        predicted = np.diag([amplitude/dp]*2 + [-amplitude/dm]*2)
        literal = model.h(case['K'], q)
        direct = model.direct_projection(case['K'], q)
        difference = literal - direct
        wa, wb = np.linalg.eigvalsh(literal), np.linalg.eigvalsh(direct)
        gaps_a, gaps_b = np.diff(wa), np.diff(wb)
        residual = float(np.max(np.abs(difference-predicted)))
        herm = max(float(np.max(abs(h-h.conj().T))) for h in (literal, direct))
        delta = float(np.max(abs(difference)))
        checks = {'finite_matrices': bool(np.isfinite(literal).all() and np.isfinite(direct).all()),
                  'formula_residual_within_tolerance': residual <= tolerance,
                  'hermiticity_within_tolerance': herm <= tolerance}
        if case['expect_equal']:
            checks['declared_zero_control'] = delta <= tolerance
        rows.append({
            **case, 'full_parameters': model.p, 'epsilon_minus': model.eps,
            'literal_matrix_meV': matrix(literal), 'direct_matrix_meV': matrix(direct),
            'predicted_difference_meV': predicted.tolist(),
            'maximum_matrix_difference_meV': delta, 'formula_residual_meV': residual,
            'hermiticity_residual_meV': herm,
            'literal_eigenvalues_meV': wa.tolist(), 'direct_eigenvalues_meV': wb.tolist(),
            'literal_adjacent_gaps_meV': gaps_a.tolist(), 'direct_adjacent_gaps_meV': gaps_b.tolist(),
            'maximum_adjacent_gap_difference_meV': float(np.max(abs(gaps_a-gaps_b))),
            'best_scalar_shift_meV': float(np.mean(wa-wb)),
            'eigenvalue_residual_after_best_scalar_shift_meV': float(np.max(abs((wa-wb)-np.mean(wa-wb)))),
            'checks': checks,
        })
    witness = next(r for r in rows if r['id'] == 'off_axis_witness')
    gap_witness = witness['maximum_adjacent_gap_difference_meV'] > plan['witness_minimum_gap_difference_meV']
    complete = all(all(r['checks'].values()) for r in rows) and gap_witness
    result = {
        'status': 'DIAGNOSTIC_REPRODUCED_CONVENTION_UNRESOLVED' if complete else 'DIAGNOSTIC_FAILED',
        'date_utc': '2026-09-23', 'baseline_commit': plan['baseline_commit'],
        'sources': {'model.py': sha(MODEL), 'PLAN.json': sha(ROOT / 'PLAN.json'), 'diagnose.py': sha(__file__)},
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
        'cases': rows, 'gap_difference_witness': gap_witness,
        'maximum_formula_residual_meV': max(r['formula_residual_meV'] for r in rows),
        'limitations': ['Two existing assemblies authored within this project; no external implementation check.',
                       'Same-coordinate/unitary-plus-scalar equivalence is excluded at the witness only.',
                       'A coordinate or parameter convention transformation is not excluded.',
                       'No root search, braiding or Euler-class calculation; no author-confirmed correction.'],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as handle:
        handle.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'cases': len(rows),
                      'maximum_formula_residual_meV': result['maximum_formula_residual_meV'],
                      'witness_adjacent_gap_difference_meV': witness['maximum_adjacent_gap_difference_meV']}, indent=2))
    return 0 if complete else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    sys.exit(main(parser.parse_args().output.resolve()))
