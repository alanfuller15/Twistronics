"""Generate SPEC.json for SIGNS-025 (no physical calls).

Usage: build_spec.py SWEEP024_MAP.json
Sign-accounting test at cutoff d: seven exact CCW rectangles on the 1/2048 lattice (one point per lattice
step, lower-left start, closing last-to-first) enclosing different subsets of the four candidates.
PREDICTION (frozen before any physical call): each group's discrete loop sign equals the product of the
signs of the enclosed candidates, using the reviewed local signs
  R3, R1: lo-1 +1, lo +1, hi -1, hi+1 -1, pair -1, four +1
  R2, R4: lo-1 -1, lo -1, hi +1, hi+1 +1, pair -1, four +1.
Regression: 8 sweep-grid points of SWEEP-D-024 (d lower/upper gaps, 1e-9 meV).
"""
import hashlib, json, sys
from fractions import Fraction as F
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
D = 2048
BOXES = {'B_R2R4': (1310, 1470, 1170, 1350), 'B_R2R4R3': (1310, 1470, 1170, 1520), 'B_R3': (1370, 1450, 1430, 1520),
         'B_R2': (1310, 1380, 1270, 1350), 'B_R4': (1395, 1470, 1160, 1240), 'B_R1': (700, 775, 0, 75), 'B_ctrl': (400, 480, 600, 680)}
CAND = {'R3': (F('0.6868'), F('0.7204')), 'R1': (F('0.3596'), F('0.0185')), 'R2': (F('0.65706'), F('0.63948')), 'R4': (F('0.69898'), F('0.58579'))}
LOCAL = {'upper': {'lo_minus_1': 1, 'lo': 1, 'hi': -1, 'hi_plus_1': -1, 'selected_pair': -1, 'four': 1},
         'lower': {'lo_minus_1': -1, 'lo': -1, 'hi': 1, 'hi_plus_1': 1, 'selected_pair': -1, 'four': 1}}
KIND = {'R3': 'upper', 'R1': 'upper', 'R2': 'lower', 'R4': 'lower'}

def rect(x0, x1, y0, y1):
    pts = [(x, y0) for x in range(x0, x1)] + [(x1, y) for y in range(y0, y1)] + [(x, y1) for x in range(x1, x0, -1)] + [(x0, y) for y in range(y1, y0, -1)]
    return [[str(F(x, D)), str(F(y, D))] for x, y in pts]

points, where, loops = [], {}, []
for bid, (x0, x1, y0, y1) in BOXES.items():
    idx = []
    for p in rect(x0, x1, y0, y1):
        if tuple(p) not in where: where[tuple(p)] = len(points); points.append(p)
        idx.append(where[tuple(p)])
    inside = sorted(k for k, (x, y) in CAND.items() if F(x0, D) < x < F(x1, D) and F(y0, D) < y < F(y1, D))
    pred = {g: 1 for g in LOCAL['upper']}
    for k in inside:
        for g in pred: pred[g] *= LOCAL[KIND[k]][g]
    loops.append({'id': bid, 'lattice_denominator': D, 'x_range': [x0, x1], 'y_range': [y0, y1], 'point_indices': idx, 'encloses': inside, 'predicted_signs': pred})
labels = [f'P{i:05d}' for i in range(len(points))]
# regression: 8 sweep grid points
sweep = json.loads(Path(sys.argv[1]).read_text())['samples']
pick = [r for r in sweep if r['label'] in ('G_05_05', 'G_20_40', 'G_33_17', 'G_42_41', 'G_44_46', 'G_50_60', 'G_60_08', 'G_12_55')]
assert len(pick) == 8
reg = {'lower_gap_meV': {}, 'upper_gap_meV': {}}
for r in pick:
    i = str(len(points)); points.append(r['center']); labels.append('REG024_' + r['label'])
    reg['lower_gap_meV'][i] = r['gaps']['d']['lower_meV']; reg['upper_gap_meV'][i] = r['gaps']['d']['upper_meV']
n = len(points); assert len({tuple(p) for p in points}) == n
W = 4; J = -(-n // 32); J += (-J) % W; size = -(-n // J)
jobs = [list(range(s, min(n, s + size))) for s in range(0, n, size)]
while len(jobs) % W: jobs.append([])
assert all(1 <= len(j) <= 32 for j in jobs) and sum(jobs, []) == list(range(n)) and len(jobs) % W == 0
s022 = json.loads((ROOT / 'research/benchmarks/controls_e_022/SPEC.json').read_text())
deps = dict(s022['dependencies'])
for p in ['research/benchmarks/controls_e_022/run.py', 'research/tools/concurrent/concurrent_supervisor.py', 'research/tools/concurrent/bounded_worker.py']: deps[p] = sha(ROOT / p)
for p, h in deps.items(): assert sha(ROOT / p) == h, p
spec = {
    'id': 'SIGNS-025',
    'producer': 'Claude Code session (claude/loop-cutoff-d-013); independent review by Codex requested',
    'authorization': 'User: "Let\'s proceed with research compute" (26 Sep 2026). Not gated on review.',
    'engine': 'cutoff d (604); FastPointMatrix; full-spectrum scipy evr with eigenvectors; six-group discrete holonomy as CONTROLS-E-022; Codex-reviewed concurrent_supervisor (e039de6a, copied byte-identically) with 4 single-thread workers',
    'scope': 'Finite-cutoff discrete sign-accounting consistency on seven large rectangles at cutoff d. A match to the predicted products is consistency of discrete loop signs with the four-candidate inventory on these loops only; no certified touching, node count, charge, partner correspondence, continuous isolation or infinite-cutoff claim.',
    'prediction_rule': 'sign(group, loop) = product over enclosed candidates of the reviewed local sign; empty loop +1. Mismatches or invalid (conditioning < 0.5) loops are reported as found; no retries, re-sampling or adaptive points.',
    'supervisor_source': {'commit': 'e039de6ae4b6a9285fad0fa63155c1324ba45a55', 'files': ['research/tools/concurrent_supervisor.py', 'research/tools/bounded_worker.py'], 'claude_review': '5845181342'},
    'patches': [], 'loops': loops, 'points': points, 'labels': labels, 'jobs': jobs,
    'limits': {'address_space_bytes': 3221225472, 'batch_timeout_seconds': 600, 'file_bytes': 67108864, 'job_timeout_seconds': 90, 'points_per_job': 32, 'threads': 1, 'concurrent_workers': W},
    'holonomy': s022['holonomy'],
    'regression': {'sources': {'8 grid points': 'SWEEP-D-024 execution 994ed33839fd1f346604068d4f7c8c905be3873d (eigenvalue-only; tolerance comparison)'}, 'threshold_meV': 1e-9, **reg},
    'dependencies': dict(sorted(deps.items())),
}
(HERE / 'SPEC.json').write_text(json.dumps(spec, indent=2, sort_keys=True) + '\n')
print(json.dumps({'points': n, 'jobs': len(jobs), 'points_per_job': size, 'loops': {l['id']: [len(l['point_indices']), l['encloses'], l['predicted_signs']] for l in loops}}))
