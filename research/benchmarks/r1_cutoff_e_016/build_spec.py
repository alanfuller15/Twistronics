"""Generate SPEC.json for R1-CUTOFF-E-016 (no physical calls).

Usage: build_spec.py SHELL012_MAP.json LOOP013_MAP.json
Cutoff e = sorted(set(d + b-stencil)), the same shell step that built c from b and d from c.
Points: the R1 3x3 patch of CUTOFF-SHELL-012 (step 2^-22) and the R1 32-point loop (half-width 2^-16)
of LOOP-CUTOFF-D-013; both reuse exact coordinates, so a/b/c/d upper gaps must reproduce exactly.
"""
import hashlib, json, sys
from fractions import Fraction as F
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
case = json.loads((ROOT / 'docs/certification-readiness/CASE.json').read_text())
d = json.loads((ROOT / 'research/benchmarks/cutoff_shell_012/SPEC.json').read_text())['additional_cutoff']
e_idx = sorted({(x + dx, y + dy) for x, y in d['ordered_indices'] for dx, dy in case['cutoffs']['b']['stencil']})
e = {'name': 'fourth_neighbor_shell', 'vectors': len(e_idx), 'dimension': 4 * len(e_idx), 'selected_bands_zero_based': [2 * len(e_idx) - 1, 2 * len(e_idx)],
     'ordered_indices': [list(v) for v in e_idx], 'construction': 'sorted(set(d + b stencil)); d from CUTOFF-SHELL-012 SPEC'}
s012 = json.loads((ROOT / 'research/benchmarks/cutoff_shell_012/SPEC.json').read_text())
s013 = json.loads((ROOT / 'research/benchmarks/loop_cutoff_d_013/SPEC.json').read_text())
patch = [p for p in s012['patches'] if p['id'] == 'candidate_R1'][0]
loop = [l for l in s013['loops'] if l['id'] == 'R1_r1_32'][0]
points = [s012['points'][i] for i in patch['point_indices']] + [s013['points'][i] for i in loop['point_indices']]
labels = [f'R1_patch_{k}' for k in range(9)] + [f'R1_loop_{k:02d}' for k in range(32)]
assert len({tuple(p) for p in points}) == len(points) == 41
patches = [{'id': 'R1_patch_012', 'center': patch['center'], 'step': patch['step'], 'point_indices': list(range(9))}]
loops = [{'id': 'R1_r1_32', 'center': loop['center'], 'half_width': loop['half_width'], 'points_per_side': loop['points_per_side'], 'point_indices': list(range(9, 41))}]
def gap(row, k):
    link, side = {'a': ('ab', 'a'), 'b': ('ab', 'b'), 'c': ('bc', 'b'), 'd': ('cd', 'b')}[k]
    return 1000 * row['comparisons'][link]['metrics']['pair'][side + '_external_gaps_meV'][1]
where = {tuple(p): i for i, p in enumerate(points)}; reg = {k: {} for k in 'abcd'}; n = 0
for path in sys.argv[1:3]:
    for row in json.loads(Path(path).read_text())['samples']:
        i = where.get(tuple(row['center']))
        if i is not None and str(i) not in reg['a']:
            n += 1
            for k in 'abcd': reg[k][str(i)] = gap(row, k)
assert n == 41, n
deps = dict(s013['dependencies'])
for p in ['research/benchmarks/loop_cutoff_d_013/SPEC.json']: deps[p] = sha(ROOT / p)
for p, h in deps.items(): assert sha(ROOT / p) == h, p
spec = {
    'id': 'R1-CUTOFF-E-016',
    'producer': 'Codex/Astra; independent review requested from Claude',
    'authorization': 'User: "R1-CUTOFF-E-016 as specified by user" (this session, 26 Sep 2026). Not gated on review.',
    'engine': 'five nested cutoffs a/b/c/d/e (196/308/444/604/788); physics, comparisons and holonomy identical to LOOP-CUTOFF-D-013',
    'scope': 'Finite-cutoff sampled diagnostics at R1 only: d->e gap/subspace changes on the 3x3 patch and the loop sign at e. No node count, charge, continuous isolation or infinite-cutoff claim.',
    'additional_cutoff_e': e, 'patches': patches, 'loops': loops, 'points': points, 'labels': labels,
    'jobs': [list(range(i, min(41, i + 6))) for i in range(0, 41, 6)],
    'limits': {'address_space_bytes': 3221225472, 'batch_timeout_seconds': 600, 'file_bytes': 67108864, 'job_timeout_seconds': 90, 'points_per_job': 6, 'threads': 1},
    'holonomy': {'min_step_overlap': 0.5, 'quantity': 'sign of det of the ordered product of real overlap matrices around the closed loop (discrete conditioning threshold only)'},
    'regression': {'sources': {'R1_patch_012': 'CUTOFF-SHELL-012 execution 95376a0da6b1d192b391349dfdde7602497bacd6 (Claude PASS 5843549264)', 'R1_r1_32': 'LOOP-CUTOFF-D-013 execution 76dadaf9478bbb8e99ee26ada6b5ff046fc1628a (Codex review pending)'},
                   'threshold_meV': 1e-9, 'upper_gap_microeV': reg},
    'dependencies': dict(sorted(deps.items())),
}
(HERE / 'SPEC.json').write_text(json.dumps(spec, indent=2, sort_keys=True) + '\n')
print(json.dumps({'e_vectors': len(e_idx), 'e_dim': 4 * len(e_idx), 'e_pair': e['selected_bands_zero_based'], 'points': 41, 'jobs': len(spec['jobs']), 'regression_points': n}))
