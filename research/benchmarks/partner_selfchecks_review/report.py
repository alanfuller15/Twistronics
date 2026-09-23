"""Evidence-bound review narrative and scientific figure; no new numerical solves."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from reconcile import reconcile
ROOT = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run():
    s = reconcile(); p = json.loads((ROOT/'CONTRACT_PROBES.json').read_text())
    if any(x['status'] != 'REPRODUCED' for x in s['producers'].values()): raise RuntimeError('incomplete producer replay')
    m = json.loads((ROOT/'REPLAY_METAMORPHIC.json').read_text()); b = json.loads((ROOT/'REPLAY_BASIS_DEPENDENCE.json').read_text())['rows']
    numeric = sum(x['numeric_leaves'] for x in s['producers'].values()); error = max(x['max_numeric_difference'] for x in s['producers'].values())
    eigensolves = sum(x['counts']['eigh'] for x in s['producers'].values()); model_count = sum(x['model_records'] for x in s['producers'].values())
    band_lines = []
    for x in b:
        sizes = str(x['basis_vectors'])+' / '+str(x['basis_vectors']) if 'basis_vectors' in x else f"{x['basis_a']} / {x['basis_b']}"
        band_lines.append(f"| {x['N']} | {x['basis']} | {sizes} | {x['d_bandwidth_meV']:.8g} | {x['d_remote_gap_meV']:.8g} |")
    lint_lines = []
    for f in p['linter_fixtures']:
        expected = 'flag violation' if f['expected_violation'] else 'accept'
        actual = ', '.join(x['rule'] for x in f['actual_findings']) or 'no findings'
        lint_lines.append(f"| `{f['name']}` | {expected} | {actual} | {'as expected' if f['detects_expected_behavior'] else 'missed invalid claim'} |")
    basis_native = next(x for x in b if x['N'] == 4 and x['basis'] == 'native per angle')
    basis_common = next(x for x in b if x['N'] == 4 and x['basis'] == 'common union')
    factor = basis_native['d_remote_gap_meV']/basis_common['d_remote_gap_meV']
    text = f'''# v076p self-check review

**Keep the numerical diagnostics; the delivery checks are not yet an enforcing release gate.** Both unchanged producers reproduce their supplied results. The claimed README generator does not generate content, a failed metamorphic assertion does not fail the process, and the linter misses several simple invalid claims.

This folder preserves the original [partner_v076p.zip](partner_v076p.zip), records the review, and supplies a focused [Fable next pass](FABLE_NEXT_PASS.md). It adds no model or campaign change. The previously published [guarded APIs](../variant_guard_repairs/README.md) remain separate opt-in implementations.

## Useful numerical evidence

All nine supplied metamorphic rows and all five basis-diagnostic rows reproduce. Across **{numeric} numeric leaves**, the maximum supplied-versus-replay difference is **{error:g}** in this environment; nonnumeric fields also match. Nine rows means **eight assertion rows plus one unconditional diagnostic**, MR6, which reports finite-cutoff reciprocal-periodicity error rather than asserting a tolerance.

The most useful result is the sensitivity to which reciprocal vectors are retained. At N=4, using a common basis for the tested 17°/77° models reduces the remote-gap discrepancy from **{basis_native['d_remote_gap_meV']:.8g} meV** to **{basis_common['d_remote_gap_meV']:.8g} meV**, a factor of about **{factor:.1f}**. The basis sizes change from 47/71 to 71/71 vectors. This is evidence of a finite-model sensitivity worth retaining.

![Finite-model sensitivity to basis choice](basis_sensitivity.png)

| N | Basis policy | Vectors at 17° / 77° | Absolute bandwidth difference (meV) | Absolute remote-gap difference (meV) |
|---|---|---|---|---|
{chr(10).join(band_lines)}

The basis table uses an 8×8 bandwidth grid and a 10×10 remote-gap seed grid followed by the native refiner. MR2 instead uses 10×10 and 12×12. Its different bandwidth figures must not be substituted into this table. The review independently reconstructs bandwidths from retained eigenvalues, remote minima from retained successful refinement returns, and model pairings from their ordered basis records.

Interpret the result as a reduction in the tested discrepancy, not a derivation of exact C3 covariance. A common list of integer labels does not alone specify the symmetry's momentum/basis transformation. The diagnostic also tests 17°/77°; it does not directly reproduce the historical 0°/60° calculation mentioned in the partner README. No retroactive historical validation is added here.

## Delivery blockers reproduced

| Finding | Executed evidence | Consequence |
|---|---|---|
| G1 — failed relation exits successfully | A labeled runtime control adds 0.125 meV to one MR1 matrix. The unchanged suite records `holds=false`, prints one violation, then exits **{p['forced_metamorphic_failure']['returncode']}**. | A build relying on its exit status will pass the failed suite. |
| G2 — generator is a placeholder | A sentinel README remains byte-identical; the script exits 0 and prints “tables regenerated.” Source contains no README write or table emission. | The shipped script cannot reproduce the claimed generated tables. |
| G3 — claimed evidence can be unresolved or wrong | Seven invalid fixtures produce no linter findings, including a missing file and a wrong metric from the same JSON. | Filename proximity and number matching do not bind scientific claims to records. |
| G4 — the package fails its own linter | The unchanged README yields **{len(p['supplied_readme_lint']['findings'])} findings**, exit status **{p['supplied_readme_lint']['returncode']}**, matching the included lint log. | The stated “no deliverable leaves” rule is not demonstrated by this deliverable. |

G1 is a synthetic harness-contract control, not an altered physical result. Its expensive unrelated scans are explicitly stubbed; the scientific replay is a separate unmodified run. G2 changes only a README inside a disposable extraction. The preserved input ZIP is untouched.

The linter has useful behavior too: it flags a plainly wrong bound value, accepts a correct value, and parses the tested Unicode scientific notation. These are small controls, not broad recall/precision measurements.

| Fixture | Expected | Observed | Assessment |
|---|---|---|---|
{chr(10).join(lint_lines)}

The missed cases come from explicit source rules: numbers with only two digits after punctuation removal are skipped; numeric prefixes 19/20 are treated as dates; values anywhere in the cited JSON may match an unrelated field; missing evidence files are silently ignored; a backticked identifier counts as evidence; and any two magnitudes below 10⁻¹² are considered matching. The last rule can hide many orders of magnitude of drift despite the stated relative tolerance.

Some findings on the partner README are method/input bookkeeping rather than false scientific results. One material binding error is its MR2 failure paragraph: it cites BASIS_DEPENDENCE.json while quoting the different-grid METAMORPHIC.json bandwidth value. Use explicit claim types and field/model bindings rather than broadening exemptions until the document passes.

## Bundled topology changes: credit and limits

The v076p archive also changes `topo.py` and `sparse_mode_v2.py` relative to v074p. Those changes are separate from its new linter/metamorphic files; [SOURCE.diff](SOURCE.diff) retains the exact differences.

| Previous issue | v076p result in this review |
|---|---|
| Negative loop start used the wrong base point | Fixed in the coordinate control: both start angles 0 and π have zero base-to-loop and transport-end-to-second-loop mismatch. |
| Unused Wilson external-gap threshold | A 2 meV gap is refused when 3 meV is required. |
| Highest pair omits its lower external gap | The 4-band control now reports the existing 2 meV lower gap. |
| Fractional Wilson pair index silently truncated | `lo=1.5` is refused. |
| Zero pair or single-band adjacent overlap accepted | Both reviewed zero-overlap controls are now refused; the smooth band passes after refinement. |
| k1 / final single-band sewing | Still missing acceptance gates: zero k1 closure returns normally, and a zero single-band final sewn overlap returns `(0, 2 meV)`. |
| Invalid threshold inputs | NaN gap tolerance returns normally; a negative overlap threshold permits a zero-overlap Wilson result. |
| Loop isolation and boundary single band | The nonisolated-loop routine returns a zero winding without refusal; the valid highest single band fails with an out-of-range eigensolver request. |

These are labeled synthetic software controls. The nonisolated loop returns winding zero, not an accepted unit-charge prediction; it does not show a mislabeled physical node. The coordinate control holds frames constant and makes no charge prediction. The new `pair_charges` still returns endpoint metadata rather than complete sampled arrays, although its uniform meshes are reconstructible from the returned parameters.

The new Wilson code checks M and Mᵀ for the k2 sewing link. Their singular values are identical, so this does not cover the independent k1 sewing direction. Root checks, full loop isolation, positive finite policy validation, and all required closure/transport gates remain important adoption boundaries. The public guarded implementation is not automatically used by these partner routines.

## Sparse change

The reviewed 2×2 matrix with eigenvalues −1,+1 now produces an **unavailable** inertia result instead of the old wrong count 0, because the row and column permutations differ. The positive symmetric kernel returns the expected count. All six native N4 review windows also agree with native absolute ordered bands; maximum observed energy error is **{s['sparse_samples']['maximum_native_energy_error_meV']:.3g} meV**.

Those native comparisons were performed by this reviewer. The bundled `window` does not enforce a native dense comparison at every acceptance. Its `_fact` docstring promises a reconstruction-residual check that the source does not perform. Matching permutations and nonzero scaled pivots do not establish that additional numerical accuracy claim. The header still says “Closes F01–F06,” while its caveat says the checks do not close those contracts, and the window docstring still uses “proved.” This review does not add a general floating-point inertia certificate or demonstrate a new native window misclassification.

## Evidence and reproducibility

Base commit: `02bbe167f01b2197b07f6b52e388bb7b5946f481`. Input archive SHA256: `b3e1b362baf67423477a26170c78bddeb4d7a56b056d0bf9629f85e531231c21`.

- [PLAN.json](PLAN.json), [INPUT_MANIFEST.json](INPUT_MANIFEST.json), [SOURCE_COMPARISON.json](SOURCE_COMPARISON.json), [SOURCE.diff](SOURCE.diff): frozen scope, input identity and source changes.
- [REPLAY_METAMORPHIC.json](REPLAY_METAMORPHIC.json), [REPLAY_BASIS_DEPENDENCE.json](REPLAY_BASIS_DEPENDENCE.json), [SUMMARY.json](SUMMARY.json): fresh results and reconciliation.
- [CONTRACT_PROBES.json](CONTRACT_PROBES.json), [LINT_REPLAY.log](LINT_REPLAY.log): full fixture text, referenced values, process outcomes, topology controls and sparse review checks.
- [METAMORPHIC_EVALUATIONS.jsonl.gz](METAMORPHIC_EVALUATIONS.jsonl.gz), [BASIS_DEPENDENCE_CHECK_EVALUATIONS.jsonl.gz](BASIS_DEPENDENCE_CHECK_EVALUATIONS.jsonl.gz): {eigensolves:,} recorded eigensolves, measurement inputs/results and refinement returns. Higher-level measurement rows are not additional solves.
- [METAMORPHIC_MODELS.json](METAMORPHIC_MODELS.json), [BASIS_DEPENDENCE_CHECK_MODELS.json](BASIS_DEPENDENCE_CHECK_MODELS.json): {model_count} constructor records with complete defaults, ordered basis lists, hashes and the active ħv value.
- [EXECUTIONS.json](EXECUTIONS.json), the producer RUN/log files, [CLEAN_SMOKE.json](CLEAN_SMOKE.json), [CLEAN_EVIDENCE.zip](CLEAN_EVIDENCE.zip): execution status, environment, source binding and fresh-source contract-probe repeat.

The producers ran in separate fresh extractions with supplied result JSON removed only from those disposable copies. Instrumentation logs returned values and does not change numerical returns. Recorded producer times are {s['producers']['METAMORPHIC']['elapsed_s']:.2f} s and {s['producers']['BASIS_DEPENDENCE_CHECK']['elapsed_s']:.2f} s in this environment, including instrumentation; these are not speed benchmarks. Eigenvectors and full Hamiltonian matrices are not retained in these ledgers.

From this folder in a fresh disposable checkout, use Python 3.12 and [REQUIREMENTS.txt](REQUIREMENTS.txt):

```sh
python -m pip install -r REQUIREMENTS.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python run_replays.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python contract_probes.py
python report.py
python clean_smoke.py
```

`run_replays.py` refuses an existing replay directory. The full producer budgets are 240 s and 600 s; any failures/timeouts are retained. For record reconciliation without rerunning producers, use `python reconcile.py`. For the targeted fresh-source repeat, use `python clean_smoke.py`; it does not repeat the full numerical scans.

**Scope remains finite-model numerical consistency and software-contract review.** No node inventory, continuous-path proof, physical validation, signed Euler relation, novelty claim or change to an earlier campaign is added.
'''
    (ROOT/'README.md').write_text(text)
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11, 'axes.titlesize':13, 'axes.labelsize':11,
                         'axes.spines.top':False, 'axes.spines.right':False, 'svg.fonttype':'none'})
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 6.8))
    fig.subplots_adjust(left=.09, right=.975, bottom=.22, top=.74, wspace=.25)
    fig.text(.075, .94, 'Basis choice changes the finite-model discrepancy', fontsize=21, weight='bold', color='#173650')
    fig.text(.075, .885, 'Strain direction 17° vs 77° · bandwidth grid 8×8 · remote-gap seed grid 10×10 + refinement', fontsize=11.5, color='#526576')
    for ax, field, title in zip(axes, ['d_bandwidth_meV', 'd_remote_gap_meV'], ['Bandwidth difference', 'Remote-gap difference']):
        for mode, label, color, marker in [('native per angle', 'Each angle’s native basis', '#196e91', 'o'), ('common union', 'Common union basis', '#c27228', 'D')]:
            rr = [x for x in b if x['basis'] == mode]
            ax.plot([x['N'] for x in rr], [x[field] for x in rr], marker=marker, color=color, markersize=7, linewidth=1.7, label=label)
        ax.set_yscale('log'); ax.set_ylim(1e-13, .2); ax.set_xlim(3.6, 8.4); ax.set_xticks([4, 6, 8])
        ax.set_title(title, loc='left', weight='bold', pad=14, color='#173650')
        ax.set_xlabel('Declared cutoff parameter N'); ax.set_ylabel('Absolute discrepancy (meV)')
        ax.grid(axis='y', color='#e5ebf0', linewidth=.8)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(.5, .10), ncol=2, frameon=False)
    fig.text(.075, .035, 'N=8 common-basis case was not run. Small differences are sampled consistency, not an exact symmetry or accuracy bound.', fontsize=10, color='#526576')
    fig.savefig(ROOT/'basis_sensitivity.png', dpi=180, facecolor='white'); fig.savefig(ROOT/'basis_sensitivity.svg', facecolor='white'); plt.close(fig)
    (ROOT/'FIGURE.json').write_text(json.dumps(dict(generator_sha256=sha(ROOT/'report.py'), sources={f:sha(ROOT/f) for f in ['REPLAY_BASIS_DEPENDENCE.json', 'SUMMARY.json', 'CONTRACT_PROBES.json']},
                                                outputs={f:sha(ROOT/f) for f in ['README.md', 'basis_sensitivity.png', 'basis_sensitivity.svg']},
                                                scope='Retained basis-diagnostic values; no generated or invented numerical data'), indent=2)+'\n')


if __name__ == '__main__': run()
