"""End-to-end adoption check: re-run LOWER-CONTROLS-021 (192 points x c/d/e) with upgrades 1+2 and compare
every retained number with Codex's execution 38204bfc.

usage: reproduce_021.py SRC_ROOT EVIDENCE_DIR OUT_DIR --wheel WHEEL [--points-per-job 32]
SRC_ROOT: checkout of codex/r1-e016-lower017 at 38204bfc (for lower_controls_021/run.py and SPEC).
EVIDENCE_DIR: materialized 021 evidence (materialize.py output).

Per job (subprocess, one thread, same rlimits as 021): wheel provenance + ladder exactly as the 021
worker, then FastPointMatrix per cutoff instead of point_matrix; nested residuals, scipy evr eigh,
residual asserts and metrics() are the 021 worker's own functions. The supervisor then asserts:
  - every energy/four-state vector array is bit-identical to the retained STATES.npz rows, and
  - every SAMPLES row (gaps, angles, containment, residuals) equals the retained row exactly.
"""
import argparse, json, os, resource, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(); ap.add_argument('src', type=Path); ap.add_argument('evidence', type=Path); ap.add_argument('out', type=Path)
ap.add_argument('--wheel', required=True); ap.add_argument('--points-per-job', type=int, default=32); ap.add_argument('--job', type=int); ap.add_argument('--indices')
a = ap.parse_args()
src = a.src.resolve()
R21 = src / 'research/benchmarks/lower_controls_021'


def load(p, name):
    import importlib.util
    s = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


if a.job is not None:  # worker
    lim = json.loads((R21 / 'SPEC.json').read_text())['limits']
    resource.setrlimit(resource.RLIMIT_AS, (lim['address_space_bytes'],) * 2); resource.setrlimit(resource.RLIMIT_FSIZE, (lim['file_bytes'],) * 2)
    t0 = time.perf_counter()
    import numpy as np
    from scipy.linalg import eigh
    sys.path.insert(0, str(HERE)); from fast_pipeline import FastPointMatrix, pack_states
    r21 = load(R21 / 'run.py', 'r21'); cfg = json.loads((R21 / 'SPEC.json').read_text())
    old = load(src / 'research/benchmarks/three_front_001/run.py', 'old'); sc = load(src / 'research/benchmarks/state_comparison_001/run.py', 'sc')
    np, base, assembly, case, provenance = old.setup(a.wheel); case = r21.ladder(case)
    t_setup = time.perf_counter() - t0
    fast = {k: FastPointMatrix(base, assembly, old.float_coefficients(assembly, case, k)[0]) for k in r21.KEYS}
    t_coef = time.perf_counter() - t0 - t_setup
    rows = []; arrays = {f'{k}_{t}': [] for k in r21.KEYS for t in ['energies', 'vectors']}; tb = te = 0.0
    for index in map(int, a.indices.split(',')):
        x, y = cfg['points'][index]
        t = time.perf_counter(); H = {k: fast[k](x, y) for k in r21.KEYS}; tb += time.perf_counter() - t
        nested = {}
        for left, right in r21.LINKS:
            ii = sc.embedding(r21.pair_case(case, left, right)); nested[left + right] = float(np.max(abs(H[right][np.ix_(ii, ii)] - H[left]))); assert nested[left + right] < 1e-10
        E = {}; V = {}; res = {}
        t = time.perf_counter()
        for k in r21.KEYS:
            assert np.max(abs(H[k] - H[k].T)) < 1e-10
            E[k], v = eigh(H[k], driver='evr'); lo, hi = case['cutoffs'][k]['selected_bands_zero_based']; V[k] = v[:, lo - 1:hi + 2]
            res[k] = float(np.max(abs(H[k] @ V[k] - V[k] * E[k][lo - 1:hi + 2]))); assert res[k] < 1e-8
            arrays[k + '_energies'].append(E[k]); arrays[k + '_vectors'].append(V[k])
        te += time.perf_counter() - t
        rows.append({'index': index, 'label': cfg['labels'][index], 'center': [x, y], 'nested_residual_meV': nested, 'eigenpair_residual_meV': res, 'comparisons': r21.metrics(sc, case, E, V)})
    d = a.out / f'job{a.job:03d}'; d.mkdir(parents=True, exist_ok=True)
    (d / 'SAMPLES.json').write_text(json.dumps(rows, indent=2, sort_keys=True, allow_nan=False) + '\n')
    (d / 'STATES.pack').write_bytes(pack_states({k: np.array(v) for k, v in arrays.items()}))
    (d / 'TIMING.json').write_text(json.dumps({'setup_provenance_ladder_s': t_setup, 'fast_matrix_setup_s': t_coef, 'matrix_build_s': tb, 'eigh_s': te, 'worker_total_s': time.perf_counter() - t0, 'points': len(rows)}) + '\n')
    sys.exit(0)

# supervisor
import numpy as np
sys.path.insert(0, str(HERE)); from fast_pipeline import unpack_states
cfg = json.loads((R21 / 'SPEC.json').read_text()); n = len(cfg['points'])
assert not a.out.exists(); a.out.mkdir(parents=True)
jobs = [list(range(i, min(n, i + a.points_per_job))) for i in range(0, n, a.points_per_job)]
env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
lim = cfg['limits']; receipts = []; t_all = time.perf_counter()
for j, owned in enumerate(jobs):
    t = time.perf_counter()
    p = subprocess.run([sys.executable, '-B', __file__, str(src), str(a.evidence), str(a.out), '--wheel', a.wheel, '--job', str(j), '--indices', ','.join(map(str, owned))], env=env, timeout=lim['job_timeout_seconds'], capture_output=True, text=True)
    receipts.append({'job': j, 'points': len(owned), 'exit_code': p.returncode, 'elapsed_s': time.perf_counter() - t, 'stderr_tail': p.stderr[-400:]})
    assert p.returncode == 0, receipts[-1]
wall = time.perf_counter() - t_all

# compare with retained 021 evidence
ret_rows = {}; ret_arr = {}
for jd in sorted(a.evidence.glob('job*')):
    rr = json.loads((jd / 'SAMPLES.json').read_text()); z = np.load(jd / 'STATES.npz')
    for r_i, r in enumerate(rr):
        ret_rows[r['index']] = r
        for name in z.files: ret_arr[(r['index'], name)] = z[name][r_i]
rows_equal = arrays_equal = 0; mism = []
for j, owned in enumerate(jobs):
    d = a.out / f'job{j:03d}'; rr = json.loads((d / 'SAMPLES.json').read_text()); st = unpack_states((d / 'STATES.pack').read_bytes())
    for r_i, r in enumerate(rr):
        if r == ret_rows[r['index']]: rows_equal += 1
        else: mism.append(['row', r['index']])
        for name, arr in st.items():
            if arr[r_i].tobytes() == ret_arr[(r['index'], name)].tobytes(): arrays_equal += 1
            else: mism.append(['array', r['index'], name])
timing = [json.loads((a.out / f'job{j:03d}' / 'TIMING.json').read_text()) for j in range(len(jobs))]
summary = {'reproduces': 'LOWER-CONTROLS-021 execution 38204bfc987108e60d7e2c1b9561fdd0fe3c6057',
           'points': n, 'eigensolves': 3 * n, 'jobs': len(jobs), 'points_per_job': a.points_per_job,
           'samples_rows_identical': rows_equal, 'state_arrays_identical': arrays_equal, 'state_arrays_total': 6 * n, 'mismatches': mism[:20],
           'summed_job_seconds': sum(r['elapsed_s'] for r in receipts), 'wall_seconds': wall, 'max_job_seconds': max(r['elapsed_s'] for r in receipts),
           'breakdown_seconds': {k: sum(t[k] for t in timing) for k in ['setup_provenance_ladder_s', 'fast_matrix_setup_s', 'matrix_build_s', 'eigh_s', 'worker_total_s']},
           'reference_021_summed_job_seconds': json.loads((a.evidence / 'BATCH.json').read_text())['summed_job_seconds'],
           'packed_state_bytes': sum((a.out / f'job{j:03d}' / 'STATES.pack').stat().st_size for j in range(len(jobs))),
           'retained_npz_bytes': sum(p.stat().st_size for p in a.evidence.glob('job*/STATES.npz')),
           'receipts': receipts}
summary['status'] = 'PASS' if not mism and rows_equal == n and arrays_equal == 6 * n else 'FAIL'
(a.out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
print(json.dumps({k: v for k, v in summary.items() if k != 'receipts'}, indent=1))
