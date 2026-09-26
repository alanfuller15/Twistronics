"""Generate SPEC.json for SWEEP-D-026 (no physical calls).

Usage: build_spec.py SWEEP024_MAP.json
Full-cell gap sweep at cutoffs a and d on a 128x128 exact cell-centred grid x=(2i+1)/256, y=(2j+1)/256
(4x the density of SWEEP-D-024), plus 8 regression points from the 024 grid (a/d lower/upper gaps,
1e-9 meV tolerance; eigenvalue-only solves). Two predeclared batches (A: grid rows j<64 + regression,
B: rows j>=64), each scheduled by the reviewed concurrent_supervisor; one launch each, no retries.
"""
import hashlib, json, sys
from fractions import Fraction as F
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
N = 128
points = [[str(F(2 * i + 1, 2 * N)), str(F(2 * j + 1, 2 * N))] for j in range(N) for i in range(N)]
labels = [f'G_{i:03d}_{j:03d}' for j in range(N) for i in range(N)]
m024 = json.loads(Path(sys.argv[1]).read_text())['samples']
want = ('G_05_05', 'G_20_40', 'G_33_17', 'G_42_41', 'G_44_46', 'G_50_60', 'G_60_08', 'G_12_55')
pick = [r for r in m024 if r['label'] in want]; assert len(pick) == 8
reg = {'lower_gap_meV': {'a': {}, 'd': {}}, 'upper_gap_meV': {'a': {}, 'd': {}}}
for r in pick:
    i = str(len(points)); points.append(r['center']); labels.append('REG024_' + r['label'])
    for k in 'ad':
        reg['lower_gap_meV'][k][i] = r['gaps'][k]['lower_meV']; reg['upper_gap_meV'][k][i] = r['gaps'][k]['upper_meV']
n = len(points); assert len({tuple(p) for p in points}) == n == N * N + 8
W = 4
def partition(idx):
    J = -(-len(idx) // 32); J += (-J) % W; q, r = divmod(len(idx), J)
    cuts = [0]
    for k in range(J): cuts.append(cuts[-1] + q + (1 if k < r else 0))
    jobs = [idx[cuts[k]:cuts[k + 1]] for k in range(J)]
    assert len(jobs) == J and all(1 <= len(j) <= 32 for j in jobs)
    return jobs
batchA = list(range(0, N * N // 2)) + list(range(N * N, n)); batchB = list(range(N * N // 2, N * N))
batches = {'A': partition(batchA), 'B': partition(batchB)}
s025 = json.loads((ROOT / 'research/benchmarks/signs_025/SPEC.json').read_text())
deps = dict(s025['dependencies'])
for p in ['research/benchmarks/signs_025/run.py', 'research/benchmarks/sweep_d_024/run.py']: deps[p] = sha(ROOT / p)
for p, h in deps.items(): assert sha(ROOT / p) == h, p
spec = {
    'id': 'SWEEP-D-026',
    'producer': 'Claude Code session (claude/loop-cutoff-d-013); independent review by Codex requested (not awaited)',
    'authorization': 'User: "Computation heavy workflows only now, no gates" (26 Sep 2026).',
    'engine': 'cutoffs a/d (196/604); FastPointMatrix; scipy evr eigenvalues only (no vectors used); full spectra retained; Codex-reviewed concurrent_supervisor, 4 single-thread workers, two predeclared batches',
    'scope': 'Finite-cutoff sampled full-cell gap maps on a 1/128 grid (lower, upper, internal pair gaps) at a and d with local-minimum inventory. Sampled values only; no certified isolation, touching, count or infinite-cutoff claim; features narrower than the grid spacing are not resolved.',
    'grid': {'n': N, 'coordinates': 'x=(2i+1)/(2n), y=(2j+1)/(2n); periodic unit cell; point index = j*n+i'},
    'candidates': {'R3': ['0.6868', '0.7204'], 'R1': ['0.3596', '0.0185'], 'R2': ['0.65706', '0.63948'], 'R4': ['0.69898', '0.58579']},
    'new_region_rule': 'A strict periodic 8-neighbour local minimum of the lower or upper gap at d below 1 meV whose periodic distance to every R1-R4 candidate exceeds 2/64 is flagged for a separately frozen refinement. Nothing is refined here.',
    'points': points, 'labels': labels, 'batches': batches,
    'limits': {'address_space_bytes': 3221225472, 'batch_timeout_seconds': 600, 'file_bytes': 67108864, 'job_timeout_seconds': 90, 'points_per_job': 32, 'threads': 1, 'concurrent_workers': W},
    'regression': {'sources': {'8 grid points': 'SWEEP-D-024 execution 994ed33839fd1f346604068d4f7c8c905be3873d (Codex sampled-map PASS 5845331866)'}, 'threshold_meV': 1e-9, **reg},
    'dependencies': dict(sorted(deps.items())),
}
(HERE / 'SPEC.json').write_text(json.dumps(spec, indent=2, sort_keys=True) + '\n')
print(json.dumps({'points': n, 'batches': {k: [len(v), max(map(len, v))] for k, v in batches.items()}}))
