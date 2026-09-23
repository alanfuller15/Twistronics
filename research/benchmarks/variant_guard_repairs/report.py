"""Generate the numerical narrative and path figure from retained results."""
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from reconcile import reconcile

ROOT = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run():
    s = reconcile()
    if s['tests']['failures'] or s['tests']['errors'] or not s['tests']['count']:
        raise RuntimeError('Refusing a passing-test narrative for a failing or empty suite')
    r = json.loads((ROOT/'RESULTS.json').read_text()); rows = r['outcomes']
    with gzip.open(ROOT/'PATHS.json.gz', 'rt') as f: paths = json.load(f)
    pair = [x for x in rows if x['kind'] == 'pair']
    pair_ok = [x for x in pair if x['result']['status'] == 'PASSED_SAMPLED_GATES']
    mirror_error = max(x['max_matrix_error_meV'] for x in s['mirror_checks'] if x['kind'] == 'native_time_reversal')
    root_max = max(max(x['result']['node_gaps_meV']) for x in pair_ok)
    pair_lines = []
    for B in (-.25, -.30):
        for v in (1, -1):
            rr = [x for x in pair if x['B'] == B and x['valley'] == v]
            accepted = [x for x in rr if x['result']['status'] == 'PASSED_SAMPLED_GATES']
            label = ', '.join(sorted(set(x['result']['label'] for x in accepted))) or 'no accepted label'
            minimum = min(x['diagnostics']['min_overlap'] for x in accepted) if accepted else float('nan')
            ext = min(x['diagnostics']['min_external_gap_meV'] for x in accepted) if accepted else float('nan')
            pair_lines.append(f'| {B:.2f} | {"K" if v == 1 else "K′"} | {len(accepted)}/{len(rr)} | {label} | {minimum:.6f} | {ext:.6g} |')
    wilson_lines = []
    for x in [x for x in rows if x['kind'] == 'wilson']:
        out, d = x['result'], x['diagnostics']; mesh = ' × '.join(map(str, x['mesh']))
        estimate = f"{out['euler_estimate']:+.9f}" if 'euler_estimate' in out else out.get('code', out['status'])
        wilson_lines.append(f"| {x['model']} | {mesh} | {estimate} | {d['min_overlap']:.6f} | {d['max_endpoint_sewing_loss']:.6g} | {d['min_external_gap_meV']:.6f} |")
    sp_lines = []
    for x in [x for x in rows if x['kind'] == 'sparse']:
        out = x['result']; status = out['status'] if 'code' not in out else 'REJECTED: '+out['code']
        sp_lines.append(f"| {x['valley']:+d} | {x['f']} | {x['sigma']:g} | {status} |")
    sign_lines = []
    for x in [x for x in rows if x['kind'] == 'sign' and x['intervals'] == 160]:
        out = x['result']; status = f"{out['sign']:+d}" if 'sign' in out else out.get('code', out['status'])
        sign_lines.append(f"| {x['valley']:+d} | {x['band_label']} | {x['axis']} | {status} | {x['diagnostics']['min_external_gap_meV']:.6g} |")
    text = f'''# Guarded variant measurements

This branch implements the focused corrections identified in the [v074p response review](../variant_response_review/README.md). The new opt-in APIs use explicit mirrored coordinate arrays, enforce sampled topology gates, and require a native dense comparison for every accepted sparse window. Historical producers and input archives remain unchanged.

**{s['tests']['count']} regression tests pass.** The bounded run contains {len(pair)} pair measurements, six Wilson meshes, sixteen sign cycles and twelve sparse requests. The tables below are generated from retained records by `report.py`; they are not manually transcribed verdicts.

![Actual K and K-prime measurement paths](mirrored_paths.png)

The figure shows the recorded fine-mesh paths at radius 0.012. Centers, circles, their starts, and the connecting transport segment all undergo the same coordinate inversion. Colored circles identify the two nodes; signed winding depends on the arbitrary base-frame orientation. These are momentum-coordinate paths, not a movie of nodes braiding in parameter space.

## What changed

| Contract | Implemented behavior | Scope |
|---|---|---|
| Loop/base agreement | Explicit closed circles and full transport arrays; mismatched endpoints are refused. K′ uses the exact negative of every K coordinate. | Unwrapped finite-model comparison; no periodic-image substitution. |
| Root checks | Both centers are evaluated natively and must meet the frozen gap threshold. | Uses retained K seeds; no new root search or inventory. |
| Topology acceptance | Native reality, Hermiticity, both available external gaps, pair/single-band overlap, phase increments, and both endpoint sewing directions are enforced. | Sampled gates; no unsampled lower bounds. |
| Wilson product | Gate each link, then multiply its polar factor. Actual endpoint frames separate sewing from the last finite mesh step. | Finite-cutoff sewing is approximate; estimates need not be exact integers. |
| Sparse acceptance | Bind the candidate matrix to the native matrix, solve native absolute ordered bands, then check candidate energies, residuals, orthogonality and subspace agreement. | Conservative dense-assisted window mode; no speedup or root/event claim. |
| Work records | Disjoint component durations and counts; separately named inclusive attempt times; failures retained. | Counts for these APIs, not an audit of all historical consumers. |

The old LU diagonal “inertia proof” is **not used** by the new mode. General pivoted LU remains only as an inverse operator for ARPACK. Its row/column permutations do not supply an inertia certificate. Small residuals alone never authorize a band-window label.

## Mirrored pairs

N=4; θ=1.05°; ε=0.003; φ=0°; A=0.2; `lab_nn_full`; exact geometry; w₁=110 meV and w₀/w₁=0.8. The perturbation is B times the declared sine σz harmonic. The ordered basis is frozen before each model is constructed; complete defaults, harmonics and indices are in [MODELS.json](MODELS.json).

Each row covers radii 0.012 and 0.008 and loop/transport interval counts 96/300 and 192/600. Paths stay at their actual unwrapped coordinates; no modulo operation moves a K′ node to a different finite-cutoff Hamiltonian.

| B | Valley | Passed / attempted | Relative label | Minimum link singular value | Minimum sampled external gap (meV) |
|---|---|---|---|---|---|
{chr(10).join(pair_lines)}

Largest evaluated center gap: **{root_max:.3g} meV**, against 10⁻⁶ meV. Largest entrywise native difference in H_K′(−k) versus conjugate(H_K(k)) over every retained loop/transport/center coordinate: **{mirror_error:.3g} meV**. This equality is also built into the native valley wrapper; it is an implementation consistency check, not an independently coded K′ model.

All four loop/radius refinement comparisons and all eight valley-pair comparisons are retained in [SUMMARY.json](SUMMARY.json). Their pass flags must be consulted if regenerating this report. Earlier producer labels remain historical results; this measurement changes their geometrical implementation rather than silently replacing their evidence.

## Wilson meshes with enforced gates

The strained baseline has A=0, B=0, N=4 and the same strain/kinetic settings as above. The chiral control has N=6, θ=1.06°, ε=0, w₀=0 and `kinetic=none`. No bandwidth scan is rerun.

| Model | Intervals k₁ × k₂ | Euler estimate | Minimum link singular value | Maximum endpoint sewing loss | Minimum sampled external gap (meV) |
|---|---|---|---|---|---|
{chr(10).join(wilson_lines)}

The grid includes both endpoints: (n₁+1)(n₂+1) native frame evaluations. Sewing loss is max |1−σᵢ| for the overlap between the actual endpoint frame and the sewn starting frame. It no longer includes a missing last mesh step. The small noninteger offsets for strained models persist under refinement and must not be presented as cutoff accuracy or an exact topological certificate. Only magnitudes are compared across arbitrary frame orientations. No signed Euler/total-node relation is asserted; see the [reference qualification](../variant_response_review/REFERENCES.md).

## Single-band endpoint cycles

The endpoint uses N=4, ε=0.003, φ=80°, A=−0.30, ratio=0.88, plus the declared −0.40 and layer-antisymmetric −1.8 sine σz harmonics. Both 80- and 160-interval runs are retained; this table shows the latter. Mesh comparisons are in SUMMARY.json.

| Valley | Band | Axis | Sign / refusal | Minimum sampled isolation gap (meV) |
|---|---|---|---|---|
{chr(10).join(sign_lines)}

## Sparse windows: accept or refuse

These twelve requests use six absolute central bands, a fixed 14-eigenpair ARPACK request, and both shifts 0 and 100 meV. A shift does not define an absolute band index. A missing target window is refused without retry or silent fallback. Every accepted window includes a native dense solve, so this is not a sparse performance benchmark.

| Valley | Fractional coordinate | Shift (meV) | Outcome |
|---|---|---|---|
{chr(10).join(sp_lines)}

The regression suite also injects exact eigenpairs from the wrong absolute window and checks their refusal despite good residuals. The former 2×2 LU counterexample remains in the suite: signed U-diagonal count 0, actual negative eigenvalue count 1. The new mode makes no inertia claim.

## Evidence and reproduction

- [PLAN.json](PLAN.json): thresholds and finite run matrix frozen before the first test; SHA256 `{s['plan_sha256']}`.
- [RESULTS.json](RESULTS.json), [SUMMARY.json](SUMMARY.json), [EVALUATIONS.jsonl.gz](EVALUATIONS.jsonl.gz): every attempt, native spectra, gaps, links, phase increments, comparison checks and work records.
- [PATHS.json.gz](PATHS.json.gz), [MODELS.json](MODELS.json): full coordinate arrays and ordered basis/model identities.
- [TESTS.log](TESTS.log), [TESTS.xml](TESTS.xml): regression outcomes. [CLEAN_SMOKE.json](CLEAN_SMOKE.json) and [CLEAN_EVIDENCE.zip](CLEAN_EVIDENCE.zip): fresh-source tests and four targeted repeated requests, without inherited result files.
- [NEGATIVE_CONTROLS.json](NEGATIVE_CONTROLS.json): structured refusal records for six synthetic controls and the retired 2×2 inertia counterexample, generated by `record_controls.py` after the numerical campaign.
- [partner_v074p.zip](partner_v074p.zip), [INPUT_MANIFEST.json](INPUT_MANIFEST.json): byte-preserved partner input. [SOURCE.diff](SOURCE.diff) records this branch's added implementation sources. No original source is patched.
- [FABLE_HANDOFF.md](FABLE_HANDOFF.md): precise adoption boundary and remaining work.

The ledger retains native selected spectra and transport diagnostics, **not all eigenvectors**. Reconciliation independently rebuilds gaps and windings from those records; rerunning source is required to recompute overlaps. Root convergence is not newly demonstrated: retained candidate roots are re-evaluated at their exact coordinates.

From a fresh disposable checkout of this folder, using Python 3.12:

```sh
python -m pip install -r REQUIREMENTS.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p no:cacheprovider test_guards.py --junitxml=TESTS.xml
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python run_campaign.py
python report.py
python record_controls.py
python clean_smoke.py
```

The commands regenerate output files in the disposable copy. `response_inputs.py` verifies the original ZIP and member hashes before extraction. For a read-only reconciliation of numerical records apart from its regenerated summary, run `python reconcile.py`.

**Limits:** these APIs are opt-in; they do not automatically repair historical `topo.py`, `braid.py`, `sparse_mode_v2.py` or their consumers. This pass adds no general sparse Newton/event acceptance, global node inventory, continuous-path isolation proof, new cutoff campaign, physical validation or novelty claim. Two engines sharing measurement code remain a numerical consistency check. Constant tunnelling remains a model assumption.
'''
    (ROOT/'README.md').write_text(text)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'axes.spines.top': False, 'axes.spines.right': False, 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.subplots_adjust(left=.09, right=.97, bottom=.20, top=.85, wspace=.22, hspace=.40)
    fig.text(.07, .963, 'The same paths, explicitly mirrored', fontsize=23, weight='bold', color='#182f46')
    fig.text(.07, .920, 'Native finite model · N = 4 · radius 0.012 · 192 loop / 600 transport intervals', fontsize=12, color='#455769')
    colors = ['#146b8a', '#c46b28']
    for i, B in enumerate((-.25, -.30)):
        key = f'B{B}_r0.012_n192_t600'
        for j, (name, valley) in enumerate([('K', 1), ('Kprime', -1)]):
            ax = axes[i, j]; g = paths[key][name]; nodes = np.asarray(g['nodes']); path = np.asarray(g['transport'])
            out = next(x for x in pair if x['B'] == B and x['valley'] == valley and x['radius'] == .012 and x['loop_intervals'] == 192)
            label = out['result'].get('label', out['result']['status'])
            ax.plot(path[:, 0], path[:, 1], color='#798896', lw=1.6, zorder=1)
            ax.annotate('', xy=path[345], xytext=path[290], arrowprops=dict(arrowstyle='->', color='#536373', lw=1.7))
            for q, loop in enumerate(g['loops']):
                xy = np.array(loop)
                ax.plot(xy[:, 0], xy[:, 1], color=colors[q], lw=2.4, zorder=3)
                ax.scatter(nodes[q, 0], nodes[q, 1], color=colors[q], marker='x', s=32, zorder=4)
                ax.scatter(xy[0, 0], xy[0, 1], facecolor='white', edgecolor=colors[q], linewidth=1.7, s=38, zorder=5)
                ax.annotate(str(q+1), nodes[q], xytext=(-13, 14), textcoords='offset points', color=colors[q], fontsize=12, weight='bold')
            center = nodes.mean(axis=0); span = max(np.ptp(nodes, axis=0))+.09
            ax.set_xlim(center[0]-span/2, center[0]+span/2); ax.set_ylim(center[1]-span/2, center[1]+span/2)
            ax.set_aspect('equal', adjustable='box'); ax.grid(color='#e8edf2', linewidth=.7)
            ax.set_xlabel('Fractional momentum f₁'); ax.set_ylabel('Fractional momentum f₂')
            ax.set_title(f'B = {B:.2f}   ·   {"K" if valley == 1 else "K′"}   ·   {label}', loc='left', pad=12, weight='bold', color='#21384e')
    fig.legend(handles=[Line2D([0], [0], color=colors[0], lw=2, label='Loop 1'), Line2D([0], [0], color=colors[1], lw=2, label='Loop 2'), Line2D([0], [0], color='#798896', lw=1.6, label='Frame transport'), Line2D([0], [0], marker='o', color='none', markeredgecolor='#536373', markerfacecolor='white', label='Loop / transport endpoint')], loc='lower center', bbox_to_anchor=(.5, .064), ncol=4, frameon=False)
    fig.text(.07, .025, 'Measured paths and sampled charge labels. No complete node inventory or continuous-path proof is claimed.', fontsize=10, color='#536373')
    fig.savefig(ROOT/'mirrored_paths.png', dpi=200, facecolor='white'); fig.savefig(ROOT/'mirrored_paths.svg', facecolor='white'); plt.close(fig)
    (ROOT/'FIGURE.json').write_text(json.dumps(dict(generator_sha256=sha(ROOT/'report.py'), sources={f: sha(ROOT/f) for f in ('RESULTS.json', 'PATHS.json.gz', 'SUMMARY.json')}, outputs={f: sha(ROOT/f) for f in ('mirrored_paths.png', 'mirrored_paths.svg')}, scope='Actual retained coordinate arrays; no synthetic band or braid illustration'), indent=2)+'\n')


if __name__ == '__main__': run()
