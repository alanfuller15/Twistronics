"""Bounded structural/component audit; no physical Hamiltonian or mesh run.

Reads hash-bound archived source and retained JSON. Compiles only selected
AST definitions; never activates/extracts/imports the archived packages.
Writes results only to a fresh output directory. No subprocess or network.
"""
import argparse
import ast
from dataclasses import asdict, dataclass
import hashlib
import io
import json
import numbers
from pathlib import Path
import platform
from types import SimpleNamespace
import zipfile

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(b):
    return hashlib.sha256(b).hexdigest()


def definitions(source, names, env):
    tree = ast.parse(source)
    selected = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    if {n.name for n in selected} != set(names):
        raise ValueError('missing archived definitions')
    exec(compile(ast.Module(body=selected, type_ignores=[]), '<hash-bound-archive-definitions>', 'exec'), env)
    return {n: env[n] for n in names}


def rotation(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s], [s, c]])


def run(out):
    out.mkdir(parents=True, exist_ok=False)
    plan_bytes = (HERE / 'PLAN.json').read_bytes()
    plan = json.loads(plan_bytes)
    for path, h in plan['sources'].items():
        if digest((ROOT / path).read_bytes()) != h:
            raise ValueError('source binding mismatch: ' + path)
    with zipfile.ZipFile(ROOT / plan['archive_path']) as z:
        guarded = z.read('guarded_topology.py')
        nested = z.read('partner_v074p.zip')
    with zipfile.ZipFile(io.BytesIO(nested)) as z:
        euler = z.read('euler.py')
    for name, b in [('guarded_topology.py', guarded), ('partner_v074p.zip', nested), ('euler.py', euler)]:
        if digest(b) != plan['archive_members'][name]:
            raise ValueError('archive member mismatch: ' + name)
    env = dict(__name__=__name__, np=np, numbers=numbers, dataclass=dataclass, asdict=asdict)
    shift = definitions(euler.decode(), ['shift_matrix'], env)['shift_matrix']
    parts = definitions(guarded.decode(), ['Rejected', 'Policy', 'Sampler', 'sewing'], env)
    original = json.loads((ROOT / plan['contract_path']).read_text())
    idx = original['basis']['ordered_indices']
    model = SimpleNamespace(pos={tuple(n): i for i, n in enumerate(idx)}, nG=len(idx), dim=4*len(idx), valley=1)
    checks, structural, links = [], [], []
    tol = plan['tolerance']

    def check(name, passed, **kw):
        row = dict(name=name, passed=bool(passed), **kw)
        checks.append(row)
        print(('PASS ' if row['passed'] else 'FAIL ') + name, flush=True)

    check('retained_basis_size', len(idx) == original['basis']['vectors'])
    Smap = {}
    u2 = np.array([[1, 1j], [1, -1j]]) / np.sqrt(2)
    U = np.kron(np.eye(2*model.nG), u2)
    for v in plan['valleys']:
        model.valley = v
        sampler = parts['Sampler'](model)
        for axis in (0, 1):
            d = (-v, 0) if axis == 0 else (0, -v)
            S = parts['sewing'](sampler, axis)
            Smap[v, axis] = S
            retained = [n for n in model.pos if (n[0]+d[0], n[1]+d[1]) in model.pos]
            lost = [list(n) for n in model.pos if n not in retained]
            mask = np.zeros(model.dim)
            for n in retained:
                i = model.pos[n]
                for layer in range(2):
                    mask[2*model.nG*layer+2*i:2*model.nG*layer+2*i+2] = 1
            gram = S.T @ S
            singular = np.linalg.svd(S, compute_uv=False)
            rank = int(np.count_nonzero(singular > tol))
            defect = float(np.linalg.norm(np.eye(model.dim)-gram, 2))
            real_basis_error = float(np.linalg.norm(U.conj().T @ S @ U-S, 2))
            check(f'partial_isometry_v{v}_a{axis}', np.array_equal(gram, np.diag(mask)) and rank == 4*len(retained))
            check(f'nonunitary_v{v}_a{axis}', defect == 1 and rank < model.dim)
            check(f'reverse_shift_v{v}_a{axis}', np.array_equal(shift(model, (-d[0], -d[1])), S.T))
            check(f'real_basis_v{v}_a{axis}', real_basis_error < tol)
            structural.append(dict(valley=v, axis=axis, shift=list(d), dimension=model.dim, rank=rank,
                                   lost_indices=lost, ambient_isometry_defect=defect,
                                   real_basis_transform_error=real_basis_error))
        C = Smap[v, 1] @ Smap[v, 0] - Smap[v, 0] @ Smap[v, 1]
        # Compare exact integer paths, not just a floating-point matrix norm.
        def path(n, first, second):
            t = (n[0]+first[0], n[1]+first[1])
            if t not in model.pos:
                return None
            t = (t[0]+second[0], t[1]+second[1])
            return t if t in model.pos else None
        d1, d2 = (-v, 0), (0, -v)
        disagreements = [list(n) for n in model.pos if path(n, d1, d2) != path(n, d2, d1)]
        columns = int(np.count_nonzero(np.any(C != 0, axis=0)))
        check(f'corner_path_identity_v{v}', columns == 4*len(disagreements))
        structural.append(dict(valley=v, corner_commutator_norm=float(np.linalg.norm(C, 2)),
                               disagreeing_indices=disagreements, differing_columns=columns,
                               meaning='ambient structural test, not selected-band cocycle'))

    F = np.eye(4)[:, :2]
    def endpoint(name, S, expected, code=None, angle=None):
        sampler = parts['Sampler'](SimpleNamespace(dim=4))
        C = S @ F
        M = F.T @ C
        L = np.eye(2)-C.T @ C
        R = (np.eye(4)-F @ F.T) @ C
        sv = np.linalg.svd(M, compute_uv=False)
        status, rejection, O = 'passed', None, None
        try:
            O = sampler.link(F, C, name, sewing=True)
        except parts['Rejected'] as exc:
            status, rejection = 'rejected', exc.record['code']
        check(name+'_gate', status == expected and (code is None or rejection == code))
        identity_error = float(np.linalg.norm(np.eye(2)-M.T@M-L-R.T@R, 2))
        check(name+'_decomposition', identity_error < tol)
        loss = float(1-sv.min())
        delta = float(1-sv.min()**2)
        check(name+'_bounds', np.linalg.norm(L, 2) <= delta+tol and np.linalg.norm(R, 2) <= np.sqrt(max(0, delta))+tol)
        record = dict(name=name, S=S.tolist(), status=status, rejection=rejection,
                      singular_values=sv.tolist(), sewing_loss=loss,
                      norm_loss_squared=float(np.linalg.norm(L, 2)), mismatch_norm=float(np.linalg.norm(R, 2)),
                      decomposition_error=identity_error, ledger=sampler.records)
        if O is not None:
            fitting = float(np.linalg.norm(C-F@O, 2))
            observed_angle = float(np.arctan2(O[1, 0], O[0, 0]))
            check(name+'_fit_bound', fitting <= np.sqrt(max(0, 2*loss))+tol)
            record.update(polar_angle=observed_angle, fitting_norm=fitting)
            if angle is not None:
                check(name+'_angle', abs(observed_angle-angle) < tol)
        links.append(record)
        return record

    endpoint('identity', np.eye(4), 'passed', angle=0.)
    c = plan['accepted_cosine']
    contraction = np.diag([c, c, 1., 1.])
    cut = endpoint('pure_norm_loss', contraction, 'passed', angle=0.)
    s = np.sqrt(1-c*c)
    ambient_rotation = np.block([[c*np.eye(2), -s*np.eye(2)], [s*np.eye(2), c*np.eye(2)]])
    mismatch = endpoint('pure_subspace_mismatch', ambient_rotation, 'passed', angle=0.)
    check('identical_gate_distinct_mechanisms', cut['singular_values'] == mismatch['singular_values'] and
          cut['mismatch_norm'] < tol and mismatch['norm_loss_squared'] < tol and
          cut['norm_loss_squared'] > .01 and mismatch['mismatch_norm'] > .1)
    c = plan['rejected_cosine']
    endpoint('excess_norm_loss', np.diag([c, c, 1., 1.]), 'rejected', code='sewing_loss')
    for theta in plan['phase_controls']:
        T = np.eye(4); T[:2, :2] = rotation(theta)
        row = endpoint('phase_'+str(theta), T, 'passed', angle=theta)
        check('phase_loss_zero_'+str(theta), abs(row['sewing_loss']) < tol)

    alpha = plan['corner_angle']
    T10, T20, T2right = np.eye(4), np.eye(4), np.eye(4)
    T1top = np.eye(4); T1top[:2, :2] = rotation(alpha)
    corner_rows = [endpoint('corner_'+n, T, 'passed') for n, T in
                   [('left_to_right_bottom', T10), ('bottom_to_top_left', T20),
                    ('bottom_to_top_right', T2right), ('left_to_right_top', T1top)]]
    defect = float(np.linalg.norm((T2right@T10-T1top@T20)@F, 2))
    check('local_gates_do_not_impose_corner_cocycle', all(r['status']=='passed' for r in corner_rows) and abs(defect-2*np.sin(alpha/2)) < tol and defect > .5)

    sizing = []
    # Conditional sizing only. This does not choose or run a physical mesh.
    old = json.loads((ROOT / plan['q005_results']).read_text())
    for row in old['conditional_projector_bounds']:
        p, q = row['p1'], row['new_p2']
        A = p*(q+p*p)/6
        ell, target = plan['sizing_loop_length'], plan['sizing_target']
        asymptotic = np.sqrt(A*ell**3/target)
        full = np.sqrt(A*ell**3/target+p*p*ell*ell/2)
        N = int(np.floor(full))+1
        bound = A*ell**3/(N*N-p*p*ell*ell/2)
        check('sizing_'+str(row['centre_K']), full > asymptotic and bound < target)
        sizing.append(dict(centre_K=row['centre_K'], conditional_gap=row['assumed_gap'], p=p, q=q,
                           loop_length=ell, target=target, denominator_free_threshold=float(asymptotic),
                           full_threshold=float(full), sufficient_integer=N, loop_bound=float(bound),
                           status='conditional_arithmetic_not_a_physical_mesh_certificate'))
    result = dict(schema='twistronics_boundary_sewing_audit_v1', passed=all(r['passed'] for r in checks),
                  source_sha256=digest(Path(__file__).read_bytes()), plan_sha256=digest(plan_bytes),
                  environment=dict(python=platform.python_version(), numpy=np.__version__),
                  checks=checks, basis=original['basis'], structural=structural, endpoint_controls=links,
                  synthetic_corner=dict(angle=alpha, defect=defect), conditional_sizing=sizing,
                  limits=plan['limits'])
    (out / 'RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(f"{sum(c['passed'] for c in checks)}/{len(checks)} checks; overall={result['passed']}")
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    raise SystemExit(run(parser.parse_args().output))
