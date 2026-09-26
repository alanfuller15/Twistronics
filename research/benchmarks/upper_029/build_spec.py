"""Generate SPEC.json for UPPER-029 (no physical calls).

1/1024 gap maps at cutoff d around the two upper-pair candidates, matching VALLEY-027's resolution and box size:
  R3 box: x 643..763, y 665..809 (/1024);  R1 box: x 308..428, y -54..90 (/1024; the cell is periodic, so
  y<0 is the same momentum shifted by -G2). 2 x 121 x 145 = 35090 points, eigenvalues only (scipy evr),
  four predeclared batches under the reviewed concurrent_supervisor. No loops. Outputs: interior local minima
  of the lower/upper/pair gaps per box. Sampled values only.
"""
import hashlib, json
from fractions import Fraction as F
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
BOXES = {'R3': (643, 763, 665, 809), 'R1': (308, 428, -54, 90)}
points, labels, boxes = [], [], []
for bid, (x0, x1, y0, y1) in BOXES.items():
    start = len(points)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            points.append([str(F(x, 1024)), str(F(y, 1024))]); labels.append(f'{bid}_{x}_{y}')
    boxes.append({'id': bid, 'x_range': [x0, x1], 'y_range': [y0, y1], 'denominator': 1024, 'start': start, 'points': len(points) - start})
n = len(points); assert n == 2 * 121 * 145 and len({tuple(p) for p in points}) == n
W = 4
def partition(idx):
    J = -(-len(idx) // 32); J += (-J) % W; q, r = divmod(len(idx), J); cuts = [0]
    for k in range(J): cuts.append(cuts[-1] + q + (1 if k < r else 0))
    jobs = [idx[cuts[k]:cuts[k + 1]] for k in range(J)]; assert all(1 <= len(j) <= 32 for j in jobs); return jobs
q = n // 4
batches = {b: partition(list(range(i * q, n if i == 3 else (i + 1) * q))) for i, b in enumerate('ABCD')}
s27 = json.loads((ROOT / 'research/benchmarks/valley_027/SPEC.json').read_text())
deps = dict(s27['dependencies'])
for p in ['research/benchmarks/valley_027/run.py']: deps[p] = sha(ROOT / p)
for p, h in deps.items(): assert sha(ROOT / p) == h, p
spec = {'id': 'UPPER-029', 'producer': 'Claude Code session (claude/loop-cutoff-d-013); independent review by Codex requested (not awaited)',
        'authorization': 'User: "Computation heavy workflows only now, no gates"; "You pick and continue" (26 Sep 2026).',
        'engine': 'cutoff d (604); FastPointMatrix; scipy evr eigenvalues only; full spectra retained; reviewed concurrent_supervisor, 4 single-thread workers, four predeclared batches',
        'scope': 'Finite-cutoff sampled 1/1024 gap maps around R3 and R1 with interior local-minimum inventories. No certified isolation, touching, count, charge or infinite-cutoff claim.',
        'boxes': boxes, 'candidates': s27['candidates'], 'points': points, 'labels': labels, 'batches': batches,
        'limits': s27['limits'], 'dependencies': dict(sorted(deps.items()))}
(HERE / 'SPEC.json').write_text(json.dumps(spec, indent=2, sort_keys=True) + '\n')
print(json.dumps({'points': n, 'batches': {k: [len(v), sum(map(len, v))] for k, v in batches.items()}}))
