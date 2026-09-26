"""Generate SPEC.json for LOOP-CUTOFF-D-013 (no physical calls).

Usage: build_spec.py LOOP007_MAP.json PARTNER011_MAP.json
The two MAP files are the byte-identical replays of the audited executions
cbb3bf73 (LOOP-ROBUSTNESS-007) and be6f259d (PARTNER-WINDING-011); they supply
the a/b/c regression gaps at the reused loop coordinates.
"""
import hashlib, json, sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

R3 = (F(737426703, 1073741824), F(193374303, 268435456))          # rounded c candidate (006/007)
R1 = (F(48269915, 134217728), F(19826927, 1073741824))            # rounded c candidate (010/011)
LOOPS = [
    ('R3_r1_32', R3, F(1, 1048576)),
    ('R3_rhalf_32', R3, F(1, 2097152)),
    ('R3_offnode_xplus4r_32', (R3[0] + 4 * F(1, 1048576), R3[1]), F(1, 1048576)),
    ('R1_r1_32', R1, F(1, 65536)),
    ('R1_rhalf_32', R1, F(1, 131072)),
    ('R1_offnode_xplus4r_32', (R1[0] + 4 * F(1, 65536), R1[1]), F(1, 65536)),
]
PPS = 8

def square(c, r, n):
    corners = [(-r, -r), (r, -r), (r, r), (-r, r)]; out = []
    for i, (x, y) in enumerate(corners):
        X, Y = corners[(i + 1) % 4]
        out += [[str(c[0] + x + (X - x) * j / n), str(c[1] + y + (Y - y) * j / n)] for j in range(n)]
    return out

points, labels, loops = [], [], []
for lid, c, r in LOOPS:
    pts = square(c, r, PPS); idx = list(range(len(points), len(points) + len(pts)))
    points += pts; labels += [f'{lid}_{k:02d}' for k in range(len(pts))]
    loops.append({'id': lid, 'center': [str(c[0]), str(c[1])], 'half_width': str(r), 'points_per_side': PPS, 'point_indices': idx})
assert len({tuple(p) for p in points}) == len(points) == 192

def gap(row, k):
    link, side = {'a': ('ab', 'a'), 'b': ('ab', 'b'), 'c': ('bc', 'b')}[k]
    return 1000 * row['comparisons'][link]['metrics']['pair'][side + '_external_gaps_meV'][1]
reg = {k: {} for k in 'abc'}; reused = 0
for path in sys.argv[1:3]:
    for row in json.loads(Path(path).read_text())['samples']:
        key = tuple(row['center'])
        if key in {tuple(p) for p in points}:
            i = points.index(list(key)); reused += 1
            for k in 'abc': reg[k][str(i)] = gap(row, k)
assert reused == 128, reused   # 96 from 007's three R3 loops + 32 from 011's R1 loop

deps = {p: sha(ROOT / p) for p in [
    'docs/certification-readiness/CASE.json',
    'docs/audits/parallel-domain-002-006/spotcheck.py',
    'research/benchmarks/certification_s1a_hardening_001/WHEEL_LOCK.json',
    'research/benchmarks/certification_s1b_001/check.py',
    'research/benchmarks/certification_s1b_001/SPEC.json',
    'research/benchmarks/cutoff_ladder_003/SPEC.json',
    'research/benchmarks/cutoff_shell_012/SPEC.json',
    'research/benchmarks/three_front_001/run.py',
    'research/benchmarks/state_comparison_001/run.py',
]}
# assembly module loaded by certification_s1b_001/check.py.load_parent() is covered by the 012 dependency set
for p, h in json.loads((ROOT / 'research/benchmarks/cutoff_shell_012/SPEC.json').read_text())['dependencies'].items():
    deps.setdefault(p, h); assert sha(ROOT / p) == h, p

spec = {
    'id': 'LOOP-CUTOFF-D-013',
    'producer': 'Claude Code session (claude/loop-cutoff-d-013); independent review by Codex requested',
    'authorization': 'User: "Let’s continue compute here" (this session, 26 Sep 2026). Computation is not gated on review.',
    'engine': 'four nested cutoffs a/b/c/d (196/308/444/604) exactly as CUTOFF-SHELL-012; closed-loop real-overlap holonomy exactly as LOOP-ROBUSTNESS-007',
    'scope': 'Finite-cutoff sampled loop diagnostics at cutoff d around the two candidate external touchings (R3, R1): full and half radius plus translated off-node controls. No certified node count, charge, continuous isolation or infinite-cutoff claim.',
    'loops': loops, 'points': points, 'labels': labels,
    'jobs': [list(range(i, min(192, i + 6))) for i in range(0, 192, 6)],
    'limits': {'address_space_bytes': 3221225472, 'batch_timeout_seconds': 600, 'file_bytes': 67108864, 'job_timeout_seconds': 90, 'points_per_job': 6, 'threads': 1},
    'holonomy': {'min_step_overlap': 0.5, 'quantity': 'sign of det of the ordered product of real overlap matrices around each closed loop (discrete conditioning threshold only)'},
    'regression': {'sources': {'R3 loops': 'LOOP-ROBUSTNESS-007 execution cbb3bf73a3e17a8a76733969d92cee973e100304 (Claude PASS 5843439638)',
                               'R1_r1_32': 'PARTNER-WINDING-011 execution be6f259d63445e7650db2bb688ba4e4c073a89d0 (Codex numerical PASS 5843536759)'},
                   'threshold_meV': 1e-9, 'upper_gap_microeV': reg},
    'dependencies': dict(sorted(deps.items())),
}
(HERE / 'SPEC.json').write_text(json.dumps(spec, indent=2, sort_keys=True) + '\n')
print(json.dumps({'points': len(points), 'jobs': len(spec['jobs']), 'regression_points': reused, 'loops': [l['id'] for l in loops]}))
