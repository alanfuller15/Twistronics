"""Generate SPEC.json for CUTOFF-F-023 (no physical calls).

Usage: build_spec.py SPEC021.json MANIFEST021.json
  SPEC021.json / MANIFEST021.json: research/benchmarks/lower_controls_021{,_execution}/ at Codex execution
  38204bfc987108e60d7e2c1b9561fdd0fe3c6057 (git show output is fine).

Cutoff f = sorted(set(e + b-stencil)), one more shell step (249 vectors, dimension 996).
Points: all twelve reviewed/pending local loops at the four candidates:
  0-191   the six CONTROLS-E-022 loops at R3/R1 (execution 75d9d580, this branch),
  192-383 the six LOWER-CONTROLS-021 loops at R2/R4 (Codex execution 38204bfc, Claude PASS 5844419824).
Reuse (upgrade authorized by Alan): cutoff-e energies and four-state vectors are NOT re-solved; they are
read from the retained state files, each bound here by SHA-256. Only f is solved (384 eigensolves).
Reuse regression: e is re-solved on one baseline loop per source (R3_r1_32 and R2_baseline, 64 points) and
must be bit-identical to the retained arrays; e matrices are rebuilt (no eigensolve) at every point for the
e-in-f nested residual.
"""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
case = json.loads((ROOT / 'docs/certification-readiness/CASE.json').read_text())
s022 = json.loads((ROOT / 'research/benchmarks/controls_e_022/SPEC.json').read_text())
s021 = json.loads(Path(sys.argv[1]).read_text()); m021 = json.loads(Path(sys.argv[2]).read_text())
e = s022['additional_cutoff_e']; assert e == s021['additional_cutoff_e']
f_idx = sorted({(x + dx, y + dy) for x, y in e['ordered_indices'] for dx, dy in case['cutoffs']['b']['stencil']})
f = {'name': 'fifth_neighbor_shell', 'vectors': len(f_idx), 'dimension': 4 * len(f_idx), 'selected_bands_zero_based': [2 * len(f_idx) - 1, 2 * len(f_idx)],
     'ordered_indices': [list(v) for v in f_idx], 'construction': 'sorted(set(e + b stencil)); e from CUTOFF-E-015 / CONTROLS-E-022 SPEC'}

points = s022['points'] + s021['points']; labels = s022['labels'] + s021['labels']
assert len(points) == len({tuple(p) for p in points}) == 384
loops = [dict(l, source='022') for l in s022['loops']] + [dict(l, point_indices=[i + 192 for i in l['point_indices']], source='021') for l in s021['loops']]
loops = [{k: l[k] for k in ('id', 'center', 'half_width', 'points_per_side', 'point_indices', 'source')} for l in loops]

# reuse map: point -> (source, job dir, row); every file bound by SHA-256
E022 = 'research/benchmarks/controls_e_022_execution'
reuse = {'022': {'root': E022, 'format': 'pack', 'files': {}}, '021': {'root': 'EXTERNAL: materialized 021 evidence (materialize.py)', 'format': 'npz', 'files': {},
         'manifest_commit': '38204bfc987108e60d7e2c1b9561fdd0fe3c6057', 'manifest_sha256': hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest()}}
where = {}
for j, owned in enumerate(s022['jobs']):
    d = f'job{j:03}'
    for name in ('STATES.pack', 'SAMPLES.json'): reuse['022']['files'][f'{d}/{name}'] = sha(ROOT / E022 / d / name)
    for r, i in enumerate(owned): where[i] = ['022', d, r]
for j, owned in enumerate(s021['jobs']):
    d = f'job{j:03}'
    for name in ('STATES.npz', 'SAMPLES.json'): reuse['021']['files'][f'{d}/{name}'] = m021['files'][f'{d}/{name}']['sha256']
    for r, i in enumerate(owned): where[i + 192] = ['021', d, r]
assert sorted(where) == list(range(384))
regression_points = [i for l in loops if l['id'] in ('R3_r1_32', 'R2_baseline') for i in l['point_indices']]
assert len(regression_points) == 64

deps = dict(s022['dependencies'])
for p in ['research/benchmarks/controls_e_022/SPEC.json', 'research/benchmarks/controls_e_022/run.py']: deps[p] = sha(ROOT / p)
for p, h in deps.items(): assert sha(ROOT / p) == h, p
spec = {
    'id': 'CUTOFF-F-023',
    'producer': 'Claude Code session (claude/loop-cutoff-d-013); independent review by Codex requested',
    'authorization': 'User: "Yes, proceed" (26 Sep 2026) to reusing hash-bound retained states for already-reviewed cutoffs with a recomputed regression subset; new calculation run. Not gated on review.',
    'engine': 'cutoffs e/f (788/996); e states reused from retained files (hash-bound), f solved; comparisons and six-group holonomy identical to CONTROLS-E-022; FastPointMatrix, jobs of 24, 4 concurrent single-thread workers',
    'scope': 'Finite-cutoff sampled loop diagnostics at R3, R1, R2 and R4 at the sixth cutoff f, with e->f changes. No certified touching, node count, charge, partner correspondence, continuous isolation or infinite-cutoff claim.',
    'additional_cutoff_e': e, 'additional_cutoff_f': f, 'patches': [], 'loops': loops, 'points': points, 'labels': labels,
    'jobs': [list(range(i, i + 24)) for i in range(0, 384, 24)],
    'limits': {'address_space_bytes': 3221225472, 'batch_timeout_seconds': 600, 'file_bytes': 67108864, 'job_timeout_seconds': 90, 'points_per_job': 24, 'threads': 1, 'concurrent_workers': 4},
    'holonomy': s022['holonomy'],
    'reuse': {'cutoff': 'e', 'sources': reuse, 'point_source': {str(i): where[i] for i in range(384)},
              'regression_points': regression_points, 'regression_rule': 'e re-solved (scipy evr) must equal retained e energies and four-state vectors byte for byte'},
    'dependencies': dict(sorted(deps.items())),
}
(HERE / 'SPEC.json').write_text(json.dumps(spec, indent=2, sort_keys=True) + '\n')
print(json.dumps({'f_vectors': len(f_idx), 'f_dim': 4 * len(f_idx), 'f_pair': f['selected_bands_zero_based'], 'points': 384, 'jobs': len(spec['jobs']), 'regression_points': 64, 'reused_files': {k: len(v['files']) for k, v in reuse.items()}}))
