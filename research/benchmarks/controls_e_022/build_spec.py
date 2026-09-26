"""Generate SPEC.json for CONTROLS-E-022 (no physical calls).

Usage: build_spec.py LOOP013_MAP.json CUTOFF015_MAP.json R1E016_MAP.json
Question: do the R3/R1 half-radius loops and translated controls of LOOP-CUTOFF-D-013 keep their
signs at cutoff e? (015/016 took only the baseline loops to e.)
Points: all six 013 loops, reused exactly (192 points), solved at c/d/e.
Regression (lower and upper gaps, 1e-9 meV): c/d at all 192 points against 013; e on R3_r1_32
against 015 and on R1_r1_32 against 016.
Engine: 015's physics and holonomy, with the reviewed fast pipeline (FastPointMatrix, jobs of 32,
pack_states) and up to 4 concurrent single-thread workers.
"""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
s013 = json.loads((ROOT / 'research/benchmarks/loop_cutoff_d_013/SPEC.json').read_text())
s015 = json.loads((ROOT / 'research/benchmarks/cutoff_e_015/SPEC.json').read_text())
points, labels, loops = s013['points'], s013['labels'], s013['loops']
assert len(points) == len({tuple(p) for p in points}) == 192

def gaps(row, link, side):
    g = row['comparisons'][link]['metrics']['pair'][side + '_external_gaps_meV']; return g[0], g[1]
where = {tuple(p): i for i, p in enumerate(points)}
reg = {'lower_gap_meV': {k: {} for k in 'cde'}, 'upper_gap_meV': {k: {} for k in 'cde'}}
for row in json.loads(Path(sys.argv[1]).read_text())['samples']:          # 013: c = bc b-side, d = cd b-side
    i = where[tuple(row['center'])]
    for k, (link, side) in (('c', ('bc', 'b')), ('d', ('cd', 'b'))):
        reg['lower_gap_meV'][k][str(i)], reg['upper_gap_meV'][k][str(i)] = gaps(row, link, side)
ne = 0
for path in sys.argv[2:4]:                                                 # 015 / 016: e = de b-side
    for row in json.loads(Path(path).read_text())['samples']:
        i = where.get(tuple(row['center']))
        if i is None: continue
        ne += 1; reg['lower_gap_meV']['e'][str(i)], reg['upper_gap_meV']['e'][str(i)] = gaps(row, 'de', 'b')
assert len(reg['lower_gap_meV']['c']) == len(reg['lower_gap_meV']['d']) == 192 and ne == 64, ne
assert sorted(map(int, reg['lower_gap_meV']['e'])) == list(range(0, 32)) + list(range(96, 128))

deps = dict(s015['dependencies'])
for p in ['research/benchmarks/cutoff_e_015/SPEC.json', 'research/benchmarks/loop_cutoff_d_013/SPEC.json',
          'research/tools/fast_pipeline/fast_pipeline.py', 'research/tools/fast_pipeline/controls.py']:
    deps[p] = sha(ROOT / p)
for p, h in deps.items(): assert sha(ROOT / p) == h, p
spec = {
    'id': 'CONTROLS-E-022',
    'producer': 'Claude Code session (claude/loop-cutoff-d-013); independent review by Codex requested',
    'authorization': 'User: "New calculation run ... We\'re actively computing the space. Let\'s use it" (26 Sep 2026). Not gated on review.',
    'engine': 'cutoffs c/d/e (444/604/788); physics, comparisons and holonomy identical to CUTOFF-E-015; matrices from the reviewed FastPointMatrix (Codex PASS 5844535047); up to 4 concurrent single-thread workers',
    'scope': 'Finite-cutoff sampled loop diagnostics at R3 and R1: baseline, half-radius and translated-control loops of LOOP-CUTOFF-D-013 evaluated at cutoff e. No certified touching, node count, charge, partner correspondence, continuous isolation or infinite-cutoff claim.',
    'additional_cutoff_e': s015['additional_cutoff_e'], 'patches': [], 'loops': loops, 'points': points, 'labels': labels,
    'jobs': [loop['point_indices'] for loop in loops],
    'limits': {'address_space_bytes': 3221225472, 'batch_timeout_seconds': 600, 'file_bytes': 67108864, 'job_timeout_seconds': 90, 'points_per_job': 32, 'threads': 1, 'concurrent_workers': 4},
    'holonomy': s015['holonomy'],
    'regression': {'sources': {'c,d (192 points)': 'LOOP-CUTOFF-D-013 execution 76dadaf9478bbb8e99ee26ada6b5ff046fc1628a (Codex PASS 5844109917)',
                               'e R3_r1_32': 'CUTOFF-E-015 execution 4445bddae841373db5b049fe423b7d3f09c5e883 (Codex numerical PASS 5844110148)',
                               'e R1_r1_32': 'R1-CUTOFF-E-016 execution eb26c1ae6e037b15db50d7660f6f32e32099e870 (Claude PASS 5844025322)'},
                   'threshold_meV': 1e-9, **reg},
    'dependencies': dict(sorted(deps.items())),
}
(HERE / 'SPEC.json').write_text(json.dumps(spec, indent=2, sort_keys=True) + '\n')
print(json.dumps({'points': 192, 'jobs': len(spec['jobs']), 'regression_pairs': {k: sum(len(v) for v in reg[k].values()) for k in reg}}))
