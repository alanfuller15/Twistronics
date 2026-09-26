"""Generate SPEC.json for LOOPS-028 (no physical calls). Follow-up to VALLEY-027, whose loop batch was not
derivable because loop points were de-duplicated against eigenvalue-only grid points (disclosed defect).
Here the three identical loops are solved self-contained (de-duplicated only among themselves) with full evr
vectors; the 027 grid summary is derived from the hash-bound 027 A/B MAP files. Original VALLEY-027 notes:

Usage: build_spec.py SWEEP026_SUMMARY.json
Part G (batches A, B): lower/upper/pair gap map of the R2-R4 valley at cutoff d on the exact 1/1024 lattice,
x in [636, 756]/1024, y in [553, 697]/1024 (121 x 145 = 17545 points), eigenvalues only.
Part L (batch C): three exact CCW square loops on the 1/4096 lattice around the shallow 1.577 meV lower-gap dip
reported by SWEEP-D-026 at (171/256, 159/256): half-width 32/4096 and 16/4096, and a control translated by
+64/4096 in y (away from the valley). Full evr with four-state vectors; six-group holonomy.
PREDICTION (frozen): every group on all three loops is +1, i.e. the dip carries no net discrete sign
(implied by SIGNS-025 B_R2 and B_R2R4 matching the R2-only and R2+R4 products).
"""
import hashlib, json, sys
from fractions import Fraction as F
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
S026 = json.loads(Path(sys.argv[1]).read_text())
dip = [m for m in S026['local_minima_d']['lower_meV']['minima'] if abs(m['gap_d_meV'] - 1.5766) < 1e-3]
assert len(dip) == 1 and dip[0]['center'] == ['171/256', '159/256'], dip
X0, X1, Y0, Y1 = 636, 756, 553, 697
points, labels = [], []
nG = 0
D = 4096; cx, cy = 171 * 16, 159 * 16          # dip centre on the 1/4096 lattice
def square(x0, x1, y0, y1):
    pts = [(x, y0) for x in range(x0, x1)] + [(x1, y) for y in range(y0, y1)] + [(x, y1) for x in range(x1, x0, -1)] + [(x0, y) for y in range(y1, y0, -1)]
    return [[str(F(x, D)), str(F(y, D))] for x, y in pts]
LOOPS = {'DIP_r32': (cx - 32, cx + 32, cy - 32, cy + 32), 'DIP_r16': (cx - 16, cx + 16, cy - 16, cy + 16), 'DIP_ctrl_y+64': (cx - 32, cx + 32, cy + 32, cy + 96)}
where = {}; loops = []
for lid, (x0, x1, y0, y1) in LOOPS.items():
    idx = []
    for p in square(x0, x1, y0, y1):
        if tuple(p) not in where: where[tuple(p)] = len(points); points.append(p); labels.append(f'L_{lid}_{len(idx):03d}')
        idx.append(where[tuple(p)])
    loops.append({'id': lid, 'lattice_denominator': D, 'x_range': [x0, x1], 'y_range': [y0, y1], 'point_indices': idx,
                  'predicted_signs': {g: 1 for g in ('lo_minus_1', 'lo', 'hi', 'hi_plus_1', 'selected_pair', 'four')}})
n = len(points); assert len({tuple(p) for p in points}) == n
R2 = (F('0.65706'), F('0.63948'))
for l in loops:   # R2 must be outside every loop
    x0, x1 = (F(v, D) for v in l['x_range']); y0, y1 = (F(v, D) for v in l['y_range'])
    assert not (x0 < R2[0] < x1 and y0 < R2[1] < y1)
W = 4
def partition(idx):
    J = -(-len(idx) // 32); J += (-J) % W; q, r = divmod(len(idx), J); cuts = [0]
    for k in range(J): cuts.append(cuts[-1] + q + (1 if k < r else 0))
    jobs = [idx[cuts[k]:cuts[k + 1]] for k in range(J)]; assert all(1 <= len(j) <= 32 for j in jobs); return jobs
batches = {'L': partition(list(range(n)))}
E27 = ROOT / 'research/benchmarks/valley_027_execution'
grid_maps = {b: {'path': f'research/benchmarks/valley_027_execution/{b}/MAP.json', 'sha256': sha(E27 / b / 'MAP.json')} for b in 'AB'}
s026 = json.loads((ROOT / 'research/benchmarks/valley_027/SPEC.json').read_text())
deps = dict(s026['dependencies'])
for p in ['research/benchmarks/valley_027/run.py', 'research/benchmarks/valley_027/SPEC.json']: deps[p] = sha(ROOT / p)
for p, h in deps.items(): assert sha(ROOT / p) == h, p
spec = {
    'id': 'LOOPS-028',
    'producer': 'Claude Code session (claude/loop-cutoff-d-013); independent review by Codex requested (not awaited)',
    'authorization': 'User: "Computation heavy workflows only now, no gates"; "You pick and continue" (26 Sep 2026).',
    'engine': 'cutoff d (604); FastPointMatrix; full evr with four-state vectors at every loop point; six-group discrete holonomy as SIGNS-025; reviewed concurrent_supervisor, 4 single-thread workers; grid summary from hash-bound VALLEY-027 A/B MAPs (zero solves)',
    'scope': 'Finite-cutoff sampled 1/1024 gap map of the R2-R4 valley and discrete loop signs around the SWEEP-D-026 shallow lower-gap dip. No certified isolation, touching, count, charge or infinite-cutoff claim.',
    'grid': {'x_range': [X0, X1], 'y_range': [Y0, Y1], 'denominator': 1024, 'points': 121 * 145, 'order': 'y outer, x inner', 'source_maps': grid_maps},
    'dip_source': {'run': 'SWEEP-D-026 execution 263cb758598724b2f6c25665d654616b6600ce98', 'center': dip[0]['center'], 'gap_d_meV': dip[0]['gap_d_meV']},
    'candidates': s026['candidates'], 'loops': loops, 'points': points, 'labels': labels, 'batches': batches,
    'limits': {'address_space_bytes': 3221225472, 'batch_timeout_seconds': 600, 'file_bytes': 67108864, 'job_timeout_seconds': 90, 'points_per_job': 32, 'threads': 1, 'concurrent_workers': W},
    'holonomy': {'min_step_overlap': 0.5, 'quantity': 'sign of det of the ordered product of real overlap matrices around the closed loop (discrete conditioning threshold only)'},
    'dependencies': dict(sorted(deps.items())),
}
(HERE / 'SPEC.json').write_text(json.dumps(spec, indent=2, sort_keys=True) + '\n')
print(json.dumps({'loop_points': n, 'total': n, 'batches': {k: [len(v), sum(map(len, v))] for k, v in batches.items()}}))
