"""Generate SPEC.json for SWEEP-D-024 (no physical calls).

Usage: build_spec.py LOOP014_MAP.json
Full-domain gap sweep at cutoffs a (the coverage cutoff) and d: a 64x64 cell-centred exact grid
x=(2i+1)/128, y=(2j+1)/128 over the periodic unit cell k = xG1 + yG2, plus 8 regression points from
LOOP-LOWER-014 (a and d lower/upper gaps, 1e-9 meV). Eigenvalues only (scipy evr, eigvals_only=True):
the sweep uses no eigenvectors; full spectra are retained.
"""
import hashlib, json, sys
from fractions import Fraction as F
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
N = 64
grid = [[str(F(2 * i + 1, 2 * N)), str(F(2 * j + 1, 2 * N))] for j in range(N) for i in range(N)]
labels = [f'G_{i:02d}_{j:02d}' for j in range(N) for i in range(N)]
m014 = json.loads(Path(sys.argv[1]).read_text())['samples']
pick = [r for r in m014 if r['label'].endswith(('_000', '_040'))]
assert len(pick) == 8, [r['label'] for r in pick]
reg = {'lower_gap_meV': {'a': {}, 'd': {}}, 'upper_gap_meV': {'a': {}, 'd': {}}}
points = grid + [r['center'] for r in pick]; labels += ['REG014_' + r['label'] for r in pick]
assert len({tuple(p) for p in points}) == len(points) == N * N + 8
for k, r in enumerate(pick):
    i = str(N * N + k)
    for c, (link, side) in (('a', ('ab', 'a')), ('d', ('cd', 'b'))):
        g = r['comparisons'][link]['metrics']['pair'][side + '_external_gaps_meV']
        reg['lower_gap_meV'][c][i], reg['upper_gap_meV'][c][i] = g[0], g[1]
n = len(points); J = 32; size = -(-n // J)
jobs = [list(range(s, min(n, s + size))) for s in range(0, n, size)]
assert len(jobs) == J and sum(jobs, []) == list(range(n))
s022 = json.loads((ROOT / 'research/benchmarks/controls_e_022/SPEC.json').read_text())
deps = dict(s022['dependencies'])
for p in ['research/benchmarks/controls_e_022/run.py', 'research/benchmarks/loop_lower_014/SPEC.json']: deps[p] = sha(ROOT / p)
for p, h in deps.items(): assert sha(ROOT / p) == h, p
spec = {
    'id': 'SWEEP-D-024',
    'producer': 'Claude Code session (claude/loop-cutoff-d-013); independent review by Codex requested',
    'authorization': 'User selected "New compute: domain sweep" (26 Sep 2026). Not gated on review.',
    'engine': 'cutoffs a/d (196/604); FastPointMatrix; scipy evr eigenvalues only (no vectors are used); 4 concurrent single-thread workers',
    'scope': 'Finite-cutoff sampled full-domain gap maps (lower external gap e[lo]-e[lo-1], upper external gap e[hi+1]-e[hi], internal pair gap) at cutoffs a and d on a 1/64 grid, with local-minimum inventory. Sampled values only: no certified isolation, touching, count or infinite-cutoff claim; the grid cannot resolve features narrower than its spacing.',
    'grid': {'n': N, 'coordinates': 'x=(2i+1)/(2n), y=(2j+1)/(2n), i,j in 0..n-1; periodic unit cell; point index = j*n+i'},
    'candidates': {'R3': ['0.6868', '0.7204'], 'R1': ['0.3596', '0.0185'], 'R2': ['0.65706', '0.63948'], 'R4': ['0.69898', '0.58579']},
    'new_region_rule': 'A local minimum (periodic 8-neighbour) of the lower or upper gap at d whose value is below 1 meV and whose periodic distance to every R1-R4 candidate exceeds 2/64 is flagged for a separately frozen refinement run. No refinement or loop is executed in this run.',
    'patches': [], 'loops': [], 'points': points, 'labels': labels, 'jobs': jobs,
    'limits': {'address_space_bytes': 3221225472, 'batch_timeout_seconds': 600, 'file_bytes': 67108864, 'job_timeout_seconds': 90, 'points_per_job': size, 'threads': 1, 'concurrent_workers': 4},
    'regression': {'sources': {'8 points': 'LOOP-LOWER-014 execution e1fa393b33984862cce885d320c77324fedffa98 (Codex numerical PASS 5844110028)'}, 'threshold_meV': 1e-9, **reg},
    'dependencies': dict(sorted(deps.items())),
}
(HERE / 'SPEC.json').write_text(json.dumps(spec, indent=2, sort_keys=True) + '\n')
print(json.dumps({'points': n, 'jobs': len(jobs), 'points_per_job': size, 'regression_points': 8}))
