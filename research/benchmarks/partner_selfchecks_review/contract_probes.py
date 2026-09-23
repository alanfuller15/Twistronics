"""Focused executable probes, with synthetic controls labeled separately."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np
import scipy
import scipy.sparse as sp
from scipy.linalg import eigh
from threadpoolctl import threadpool_limits
from review_inputs import ROOT, activate, extract
INPUT = activate()
import claim_lint as lint
import topo as T
from bm_strain import BM
from gate import real_basis
from sparse_mode_v2 import CertifiedSparse, Ledger, ComparisonPolicy


def plain(x):
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, np.generic): return x.item()
    raise TypeError(type(x).__name__)
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def capture(fn):
    try: return dict(status='RETURNED', value=fn())
    except Exception as ex: return dict(status='REJECTED', error_type=type(ex).__name__, error=str(ex))


def run():
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    out = dict(plan_sha256=digest(ROOT/'PLAN.json'), source_sha256={p.name: digest(p) for p in INPUT.glob('*.py')},
               probe_source_sha256=digest(__file__), environment=dict(numpy=np.__version__, scipy=scipy.__version__))
    supplied = subprocess.run([sys.executable, 'claim_lint.py', '.'], cwd=INPUT, env=env, text=True, capture_output=True, timeout=30)
    out['supplied_readme_lint'] = dict(returncode=supplied.returncode, stdout=supplied.stdout, stderr=supplied.stderr, findings=lint.lint(str(INPUT)))
    (ROOT/'LINT_REPLAY.log').write_text(supplied.stdout+supplied.stderr)
    fixtures = [
        ('valid_value', 'Measured overlap = 0.995703 in evidence.json.\n', {'overlap': .995703}, False),
        ('wrong_value', 'Measured overlap = 0.730 in evidence.json.\n', {'overlap': .995703}, True),
        ('unbound_two_digit', 'Measured gap = 5.3 meV.\n', {}, True),
        ('wrong_two_digit', 'Measured gap = 5.3 meV in evidence.json.\n', {'gap': 101.834}, True),
        ('wrong_field_same_record', 'Measured overlap = 0.730 in evidence.json.\n', {'overlap': .995703, 'unrelated_parameter': .730}, True),
        ('missing_record', 'All cases pass missing.json.\n', {}, True),
        ('backtick_as_evidence', 'All cases pass `placeholder`.\n', {}, True),
        ('year_prefix_measurement', 'Measured gap = 19.876 meV in evidence.json.\n', {'gap': 2.345}, True),
        ('tiny_value_drift', 'Measured residual = 1e-30 meV in evidence.json.\n', {'residual': 1e-13}, True),
        ('correct_scientific_notation', 'Measured residual = 4.20×10⁻⁶ meV in evidence.json.\n', {'residual': 4.2e-6}, False)
    ]
    out['linter_fixtures'] = []
    with tempfile.TemporaryDirectory(prefix='v076p_lint_') as td:
        p = Path(td)
        for name, prose, record, should_flag in fixtures:
            (p/'README.md').write_text(prose); (p/'evidence.json').write_text(json.dumps(record))
            findings = lint.lint(str(p))
            out['linter_fixtures'].append(dict(name=name, prose=prose, evidence_json=record, expected_violation=should_flag, actual_findings=findings,
                                               detects_expected_behavior=bool(findings) == should_flag))
    with tempfile.TemporaryDirectory(prefix='v076p_regenerate_') as td:
        p = extract(td); sentinel = '# REVIEW SENTINEL\nNo generated tables are present.\n'; (p/'README.md').write_text(sentinel)
        before = digest(p/'README.md')
        r = subprocess.run([sys.executable, 'regenerate_readme.py'], cwd=p, env=env, text=True, capture_output=True, timeout=30)
        out['readme_generator'] = dict(returncode=r.returncode, stdout=r.stdout, stderr=r.stderr, sentinel=sentinel, before_sha256=before,
                                       after_sha256=digest(p/'README.md'), unchanged=(p/'README.md').read_text() == sentinel)
    with tempfile.TemporaryDirectory(prefix='v076p_forced_') as td:
        p = extract(td); (p/'METAMORPHIC.json').unlink()
        r = subprocess.run([sys.executable, str(ROOT/'forced_failure_worker.py'), str(p)], cwd=p, env=env, text=True, capture_output=True, timeout=90)
        rows = json.loads((p/'METAMORPHIC.json').read_text()) if (p/'METAMORPHIC.json').exists() else []
        out['forced_metamorphic_failure'] = dict(scope='Runtime-injected MR1 perturbation and stubbed expensive scans; harness exit test only',
                                                worker_sha256=digest(ROOT/'forced_failure_worker.py'), original_suite_unchanged=digest(p/'metamorphic.py') == digest(INPUT/'metamorphic.py'),
                                                returncode=r.returncode, rows=rows, stdout=r.stdout, stderr=r.stderr)
    class Toy:
        dim = 4; valley = 1
        def frac_to_k(self, f): return np.asarray(f)
        def H(self, k): return np.diag([-3., -1., 1., 3.]).astype(complex)
    class Jump(Toy):
        def H(self, k): return np.diag([-3., -1., 1., 3.] if round(4*k[1]) % 2 == 0 else [-1., -3., 3., 1.]).astype(complex)
    class Smooth(Toy):
        def H(self, k):
            a = 2*np.pi*k[0]; c, s = np.cos(a), np.sin(a); R = np.eye(4); R[:2, :2] = [[c, -s], [s, c]]
            return R @ super().H(k) @ R.T
    class Nonisolated(Toy):
        def H(self, k): return np.diag([-1., -1., 1., 3.]).astype(complex)
    controls = {}; saved_shift = T.shift_matrix
    try:
        T.shift_matrix = lambda m, d: np.eye(m.dim)
        controls['enforced_gap'] = capture(lambda: T.euler_wilson(Toy(), np.eye(4), nf1=4, nf2=4, gap_tol=3.))
        controls['highest_pair_gap_fixed'] = capture(lambda: T.euler_wilson(Toy(), np.eye(4), lo=2, nf1=4, nf2=4))
        controls['fractional_wilson_index'] = capture(lambda: T.euler_wilson(Toy(), np.eye(4), lo=1.5, nf1=4, nf2=4))
        controls['zero_pair_link_refusal'] = capture(lambda: T.euler_wilson(Jump(), np.eye(4), nf1=4, nf2=4))
        controls['smooth_band_zero_link_refusal'] = capture(lambda: T.band_sign_holonomy(Smooth(), np.eye(4), 1, 0, 0., n=4))
        controls['smooth_band_refined_positive'] = capture(lambda: T.band_sign_holonomy(Smooth(), np.eye(4), 1, 0, 0., n=32))
        controls['nan_gap_threshold'] = capture(lambda: T.euler_wilson(Toy(), np.eye(4), nf1=4, nf2=4, gap_tol=float('nan')))
        controls['negative_overlap_threshold'] = capture(lambda: T.euler_wilson(Jump(), np.eye(4), nf1=4, nf2=4, min_overlap=-1.))
        controls['highest_single_band'] = capture(lambda: T.band_sign_holonomy(Toy(), np.eye(4), 3, 0, 0., n=4))
        T.shift_matrix = lambda m, d: np.zeros((m.dim, m.dim)) if tuple(d) == (-1, 0) else np.eye(m.dim)
        controls['zero_k1_sewing'] = capture(lambda: T.euler_wilson(Toy(), np.eye(4), nf1=4, nf2=4))
        controls['zero_single_band_sewing'] = capture(lambda: T.band_sign_holonomy(Toy(), np.eye(4), 1, 0, 0., n=4))
        T.shift_matrix = lambda m, d: np.eye(m.dim)
        # This returns a zero winding, not an accepted unit-charge prediction.
        controls['nonisolated_loop_routine'] = capture(lambda: T.winding_at(Nonisolated(), np.eye(4), np.array([.3, .4]), .012, 8, np.eye(4)[:, 1:3], 0., 1))
    finally: T.shift_matrix = saved_shift
    # Execute the actual changed coordinate plumbing with constant synthetic frames.
    geometry = []; original_frame = T.frame_at
    try:
        for angle in (0., float(np.pi)):
            points = []
            def frame(m, U, k, lo, n=2):
                points.append(np.asarray(k).tolist()); return np.array([-1., 1.]), np.eye(4)[:, :2]
            T.frame_at = frame
            r = T.pair_charges(Toy(), np.eye(4), np.array([[.3, .4], [.6, .6]]), start_angle=angle, npts=8, nstep=5)
            base = points[0]; loop1 = points[1:10]; transport = points[10:15]; loop2 = points[15:24]
            geometry.append(dict(start_angle=angle, all_evaluated_coordinates=points, returned_metadata=r[3],
                                 base_to_loop1_distance=float(np.linalg.norm(np.array(base)-loop1[0])), transport_end_to_loop2_distance=float(np.linalg.norm(np.array(transport[-1])-loop2[0])),
                                 actual_loop_samples=[len(loop1), len(loop2)], actual_transport_samples=len(transport), returned_transport_samples=len(r[3]['transport'])))
    finally: T.frame_at = original_frame
    out['topology_controls'] = dict(scope='Synthetic software controls, not new graphene results', cases=controls, coordinate_instrument=geometry)
    kernels = []
    for name, A in [('reviewed_swap', np.array([[0., 1.], [1., 0.]])), ('symmetric_positive_control', np.array([[2., 1.], [1., -2.]]))]:
        C = CertifiedSparse.__new__(CertifiedSparse); C.D = len(A); C.I = sp.eye(len(A), format='csr'); C.ledger = Ledger(); C.policy = ComparisonPolicy(C.ledger)
        lu, count = C._fact(sp.csr_matrix(A), 0., name)
        kernels.append(dict(name=name, matrix=A.tolist(), eigenvalues=eigh(A, eigvals_only=True).tolist(), reported_count=count,
                            expected_count=int(np.count_nonzero(eigh(A, eigvals_only=True) < 0)), row_permutation=lu.perm_r.tolist(), column_permutation=lu.perm_c.tolist(), ledger=C.ledger.entries))
    out['sparse_kernel_controls'] = kernels
    spec = json.loads((ROOT/'PLAN.json').read_text())['bounded_native_checks']; sparse_rows = []; models = []
    for v in spec['valleys']:
        m = BM(N=spec['N'], eps=spec['eps'], kinetic=spec['kinetic'], geometry=spec['geometry'], valley=v)
        U = real_basis(m.nG); model_id = len(models); idx = [list(x) for x in m.idx]
        models.append(dict(id=model_id, valley=v, N=spec['N'], eps=spec['eps'], kinetic=spec['kinetic'], geometry=spec['geometry'], dimension=m.dim, ordered_indices=idx,
                           basis_sha256=hashlib.sha256(json.dumps(idx, separators=(',', ':')).encode()).hexdigest(), defaults='Unchanged BM constructor defaults for omitted arguments'))
        for f in spec['points']:
            ledger = Ledger(); C = CertifiedSparse(m, ledger, ComparisonPolicy(ledger)); lo = m.dim//2-3
            native = eigh(m.H(m.frac_to_k(np.array(f))), eigvals_only=True, subset_by_index=(lo, lo+5))
            try:
                w, V, _ = C.window(np.array(f), lo, 6)
                error = float(np.max(np.abs(w-native)))
                result = dict(status='RETURNED', values_meV=w.tolist(), native_max_error_meV=error, within_review_tolerance=error <= 1e-8)
            except Exception as ex: result = dict(status='REJECTED', error_type=type(ex).__name__, error=str(ex))
            sparse_rows.append(dict(model_id=model_id, f=f, lo=lo, n=6, native_energies_meV=native.tolist(), result=result, ledger=ledger.entries))
    out['native_sparse_samples'] = sparse_rows; out['native_models'] = models
    (ROOT/'CONTRACT_PROBES.json').write_text(json.dumps(out, indent=2, default=plain, allow_nan=False)+'\n')
    print(json.dumps(dict(linter_findings=len(out['supplied_readme_lint']['findings']), missed_fixture_violations=[x['name'] for x in out['linter_fixtures'] if x['expected_violation'] and not x['actual_findings']],
                         generator_unchanged=out['readme_generator']['unchanged'], forced_failure_exit=out['forced_metamorphic_failure']['returncode'],
                         topology_status={k: v['status'] for k, v in controls.items()}, native_sparse_status=[x['result']['status'] for x in sparse_rows]), indent=2))


if __name__ == '__main__':
    with threadpool_limits(limits=1): run()
