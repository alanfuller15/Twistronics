"""Retain structured diagnostics for the specific reviewed negative controls.

This supplements the regression log with raw refusal records; it does not run
another numerical campaign or change the frozen policy.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
import guarded_topology as gt
import guarded_sparse as gs
from test_guards import Toy, Smooth
ROOT = Path(__file__).resolve().parent


def run():
    records = []
    def capture(name, S, call, expected):
        try:
            value = call(S)
            outcome = dict(status='RETURNED', result=value)
        except gt.Rejected as ex:
            outcome = ex.record
        passed = outcome.get('code') == expected
        records.append(dict(name=name, expected_code=expected, passed=passed, outcome=outcome, ledger=S.records))
        if not passed: raise RuntimeError('unexpected negative-control outcome: '+name)
    def sampler(m=None, **kw): return gt.Sampler(Toy() if m is None else m, gt.Policy(**kw), U=np.eye(4))
    class Jump(Toy):
        def H(self, k): return np.diag([-3., -1., 1., 3.] if round(4*k[1]) % 2 == 0 else [-1., -3., 3., 1.]).astype(complex)
    capture('zero_pair_overlap', sampler(Jump()), lambda S: gt.euler_wilson(S, nf1=4, nf2=4, sewings=(np.eye(4), np.eye(4))), 'overlap')
    capture('smooth_band_unresolved_at_n4', sampler(Smooth()), lambda S: gt.band_sign_holonomy(S, 1, 0, 0, n=4, sewing_matrix=np.eye(4)), 'overlap')
    capture('highest_pair_lower_external_gap', sampler(external_gap_meV=3), lambda S: gt.euler_wilson(S, lo=2, nf1=4, nf2=4, sewings=(np.eye(4), np.eye(4))), 'external_gap')
    for axis in (0, 1):
        sew = [np.eye(4), np.eye(4)]; sew[axis] *= .9
        capture(f'endpoint_sewing_axis{axis}', sampler(), lambda S, sew=sew: gt.euler_wilson(S, nf1=4, nf2=4, sewings=sew), 'sewing_loss')
    g = gt.geometry([[.3, .4], [.6, .6]], .012, 8, 8); g['transport'][0][0] += .024
    capture('base_displaced_by_2r', sampler(), lambda S: gt.pair_charges(S, g), 'base_path_mismatch')
    A = np.array([[0., 1.], [1., 0.]])
    lu = gs.splu(gs.sp.csc_matrix(A), diag_pivot_thresh=0., options={'SymmetricMode': True})
    kernel = dict(matrix=A.tolist(), eigenvalues=eigh(A, eigvals_only=True).tolist(), signed_U_diagonal_count=int(np.count_nonzero(lu.U.diagonal() < 0)),
                  U_diagonal=lu.U.diagonal().tolist(), row_permutation=lu.perm_r.tolist(), column_permutation=lu.perm_c.tolist(),
                  replacement_policy='No inertia assertion; native dense ordered comparison is mandatory for accepted windows')
    out = dict(scope='Synthetic software-contract controls only; not graphene evidence', plan_sha256=hashlib.sha256((ROOT/'PLAN.json').read_bytes()).hexdigest(),
               source_sha256={f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ('record_controls.py', 'test_guards.py', 'guarded_topology.py', 'guarded_sparse.py')},
               controls=records, retired_inertia_counterexample=kernel)
    (ROOT/'NEGATIVE_CONTROLS.json').write_text(json.dumps(out, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(controls=len(records), passing=sum(r['passed'] for r in records), retired_inertia_counterexample=kernel), indent=2))


if __name__ == '__main__': run()
