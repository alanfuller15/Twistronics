"""Generate SPEC.json for LOOP-LOWER-014 (no physical calls).

Usage: build_spec.py PARTNER008_MAP.json REFINE012_PARTITION.json
- R2/R4 rectangles are rebuilt from PARTNER-LOOPS-008 boxes (depth-10 cell units, boundary step 1/2048,
  counterclockwise from the lower-left corner) and must equal 008's coordinates exactly.
- Controls are the same rectangles translated in x; each control's closed box must contain no cell left
  unresolved by the audited REFINEMENT-012 partition (Claude PASS 5842854287).
"""
import hashlib, json, sys
from fractions import Fraction as F
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rect(x0, y0, x1, y1, unit=F(1, 1024), step=F(1, 2048)):
    X0, Y0, X1, Y1 = (v * unit for v in (x0, y0, x1, y1)); out = []
    for (ax, ay), (bx, by) in zip([(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)], [(X1, Y0), (X1, Y1), (X0, Y1), (X0, Y0)]):
        n = int(max(abs(bx - ax), abs(by - ay)) / step)
        out += [[str(ax + (bx - ax) * j / n), str(ay + (by - ay) * j / n)] for j in range(n)]
    return out

old = json.loads((ROOT / 'research/benchmarks/partner_loops_008/SPEC.json').read_text())
boxes = {l['name']: l for l in old['loops']}
unres = [tuple(c) for c in json.loads(Path(sys.argv[2]).read_text())['unresolved']]
def clear(x0, y0, x1, y1):   # depth-10 box vs depth-12 unresolved cells (closed box, any overlap counts)
    for d, x, y in unres:
        s = 2 ** (d - 10)
        if x0 * s - 1 <= x <= x1 * s and y0 * s - 1 <= y <= y1 * s: return False
    return True

specs = []
for name, lid, shift in [('R2_0.657_0.641', 'R2', -14), ('R4_0.699_0.586', 'R4', 16)]:
    L = boxes[name]; x0, y0, x1, y1 = L['depth10_box_x0_y0_x1_y1']
    pts = rect(x0, y0, x1, y1); assert pts == [old['points'][i] for i in L['point_indices']], name
    assert not clear(x0, y0, x1, y1)                         # the cluster box does contain unresolved cells
    cx0, cx1 = x0 + shift, x1 + shift; assert clear(cx0, y0, cx1, y1), (name, shift)
    specs.append((f'{lid}_box_008', [x0, y0, x1, y1], pts, name))
    specs.append((f'{lid}_control_x{shift:+d}cells', [cx0, y0, cx1, y1], rect(cx0, y0, cx1, y1), None))

points, labels, loops = [], [], []
for lid, box, pts, src in specs:
    idx = list(range(len(points), len(points) + len(pts))); points += pts; labels += [f'{lid}_{k:03d}' for k in range(len(pts))]
    loops.append({'id': lid, 'depth10_box_x0_y0_x1_y1': box, 'unit': '1/1024', 'step': '1/2048', 'point_indices': idx, 'source_008_loop': src})
assert len({tuple(p) for p in points}) == len(points)

def gap(row, k):
    link, side = {'a': ('ab', 'a'), 'b': ('ab', 'b'), 'c': ('bc', 'b')}[k]
    return 1000 * row['comparisons'][link]['metrics']['pair'][side + '_external_gaps_meV'][1]
where = {tuple(p): i for i, p in enumerate(points)}; reg = {k: {} for k in 'abc'}; reused = 0
for row in json.loads(Path(sys.argv[1]).read_text())['samples']:
    i = where.get(tuple(row['center']))
    if i is not None:
        reused += 1
        for k in 'abc': reg[k][str(i)] = gap(row, k)
assert reused == 184, reused

d13 = json.loads((ROOT / 'research/benchmarks/loop_cutoff_d_013/SPEC.json').read_text())
deps = dict(d13['dependencies']); deps['research/benchmarks/partner_loops_008/SPEC.json'] = sha(ROOT / 'research/benchmarks/partner_loops_008/SPEC.json')
for p, h in deps.items(): assert sha(ROOT / p) == h, p
n = len(points)
spec = {
    'id': 'LOOP-LOWER-014',
    'producer': 'Claude Code session (claude/loop-cutoff-d-013); independent review by Codex requested',
    'authorization': 'User: "Proceed with either" (this session, 26 Sep 2026), choosing among proposed next computations. Not gated on review.',
    'engine': 'identical to LOOP-CUTOFF-D-013 (four cutoffs a/b/c/d, 196/308/444/604) with rectangular loops and added lo / lo-1 band groups',
    'scope': 'Finite-cutoff sampled loop diagnostics around the lower-gap clusters R2 and R4 of PARTNER-LOOPS-008, at cutoff d, with translated controls clear of every REFINEMENT-012 unresolved cell. No node count, charge, continuous isolation or infinite-cutoff claim.',
    'loops': loops, 'points': points, 'labels': labels,
    'jobs': [list(range(i, min(n, i + 8))) for i in range(0, n, 8)],
    'limits': {'address_space_bytes': 3221225472, 'batch_timeout_seconds': 900, 'file_bytes': 67108864, 'job_timeout_seconds': 90, 'points_per_job': 8, 'threads': 1},
    'holonomy': {'min_step_overlap': 0.5, 'quantity': 'sign of det of the ordered product of real overlap matrices around each closed loop (discrete conditioning threshold only)',
                 'groups': {'lo_minus_1': 'column 0 (band lo-1)', 'lo': 'column 1', 'hi': 'column 2', 'hi_plus_1': 'column 3', 'selected_pair': 'columns 1..2', 'four': 'columns 0..3'}},
    'control_rule': 'translate the 008 box in x by the stated number of depth-10 cells; closed box must overlap no REFINEMENT-012 unresolved depth-12 cell',
    'regression': {'sources': {'R2_box_008,R4_box_008': 'PARTNER-LOOPS-008 execution c2d3c52e9acba7569b230f371538642b328b6506 (Claude-session run; not yet independently reviewed)'},
                   'threshold_meV': 1e-9, 'upper_gap_microeV': reg},
    'dependencies': dict(sorted(deps.items())),
}
(HERE / 'SPEC.json').write_text(json.dumps(spec, indent=2, sort_keys=True) + '\n')
print(json.dumps({'points': n, 'jobs': len(spec['jobs']), 'regression_points': reused, 'loops': [(l['id'], len(l['point_indices']), l['depth10_box_x0_y0_x1_y1']) for l in loops]}))
