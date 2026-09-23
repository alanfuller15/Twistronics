"""Render evidence-bound review tables and a scientific diagnostic figure."""
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parent
def load(n): return json.loads((ROOT/n).read_text())
def sha(n): return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()

def run():
    s=load('SUMMARY.json'); p=load('REPLAY_MIGRATION_RESULTS.json')['policy']; rows=s['rows']
    if s['failed_checks']: raise RuntimeError('Reconciliation has unresolved failures')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#263849','text.color':'#172e40','xtick.color':'#405767','ytick.color':'#405767','svg.fonttype':'none'})
    fig,axes=plt.subplots(1,2,figsize=(12.8,5.8),gridspec_kw={'width_ratios':[1,1.15]})
    fig.patch.set_facecolor('#f8fafb')
    fig.suptitle('One migrated consumer · eight sampled classifications',x=.065,y=.97,ha='left',fontsize=19,weight='bold')
    fig.text(.065,.90,'N = 4  /  49 reciprocal vectors  /  unchanged guarded APIs  /  both valleys',fontsize=11,color='#526879')
    ax=axes[0]
    colors={-.25:'#137e81',-.3:'#9d487e'}
    for j,r in enumerate(rows):
        x=(0 if r['B']==-.25 else 1)+(0 if r['radius']==.012 else .12)+(-.10 if r['valley']==1 else -.04)
        ax.scatter(x,np.prod(r['windings']),s=75,color=colors[r['B']],marker='o' if r['radius']==.012 else 's',facecolors=colors[r['B']] if r['valley']==1 else 'white',linewidths=1.6,zorder=4)
    ax.axhline(0,color='#b9c6cc',lw=.8)
    for y in [-1,1]: ax.axhline(y,color='#d8e0e5',ls='--',lw=1)
    ax.set(xlim=(-.35,1.35),ylim=(-1.35,1.35),xticks=[0,1],xticklabels=['B = −0.25','B = −0.30'],yticks=[-1,0,1],ylabel='Product of the two measured windings')
    ax.set_title('A  Relative charge labels',loc='left',pad=16,weight='bold')
    ax.text(0,.69,'SAME',ha='center',color=colors[-.25],weight='bold')
    ax.text(1,-.79,'OPPOSITE',ha='center',color=colors[-.3],weight='bold')
    ax.legend(handles=[Line2D([0],[0],marker='o',ls='',color='#405767',label='r .012 · 96 / 300'),Line2D([0],[0],marker='s',ls='',color='#405767',label='r .008 · 192 / 600')],loc='center',frameon=False,fontsize=9)
    ax.text(.5,-.28,'Filled: K   ·   open: K′\nSamples offset horizontally for legibility.',transform=ax.transAxes,ha='center',fontsize=9,color='#526879')
    ratios=[max(r['max_node_gap_meV'] for r in rows)/p['root_gap_meV'],p['external_gap_meV']/min(r['min_external_gap_meV'] for r in rows),p['internal_gap_meV']/min(r['min_loop_internal_gap_meV'] for r in rows),p['overlap_min']/min(r['min_link_overlap'] for r in rows),max(r['max_phase_increment_rad'] for r in rows)/p['phase_step_max_rad'],max(abs(abs(w)-1) for r in rows for w in r['windings'])/p['unit_winding_tol']]
    names=['Node gap','External isolation','Loop splitting','Frame overlap','Phase increment','Unit winding']
    ax=axes[1]
    ax.hlines(np.arange(6),1e-7,ratios,color='#b7d8d9',lw=5)
    ax.scatter(ratios,np.arange(6),color='#137e81',s=45,zorder=3)
    for y,value in enumerate(ratios): ax.annotate(f'{value:.2g}',(value,y),xytext=(-8 if value>.2 else 7,0),textcoords='offset points',ha='right' if value>.2 else 'left',va='center',fontsize=9)
    ax.axvline(1,color='#ac5048',ls='--',lw=1.2)
    ax.set(xscale='log',xlim=(1e-7,2.2),ylim=(5.6,-.65),yticks=np.arange(6),yticklabels=names,xlabel='Worst sampled ratio to the policy boundary')
    ax.set_title('B  Sampled gate margins',loc='left',pad=16,weight='bold')
    ax.text(1,-.54,'Boundary',ha='center',fontsize=8,color='#ac5048')
    ax.text(.5,-.28,'Below 1 meets the scalar gate.\nLower bounds use threshold ÷ measurement.',transform=ax.transAxes,ha='center',fontsize=9,color='#526879')
    fig.text(.065,.03,'Two coupled radius/mesh settings; sampled consistency only. No continuous-path or physical-validation claim.',fontsize=10,color='#526879')
    fig.subplots_adjust(left=.09,right=.955,top=.78,bottom=.29,wspace=.65)
    for ext in ['png','svg']: fig.savefig(ROOT/f'migration_review.{ext}',dpi=180,facecolor=fig.get_facecolor())
    plt.close(fig)
    (ROOT/'FIGURE.json').write_text(json.dumps(dict(generator_sha256=sha('report.py'),sources={n:sha(n) for n in ['SUMMARY.json','REPLAY_MIGRATION_RESULTS.json']},outputs={n:sha(n) for n in ['migration_review.png','migration_review.svg']},ratios=dict(zip(names,ratios)),scope='Actual replay scalars; visual offsets distinguish coincident samples and do not represent additional B values.'),indent=2)+'\n')
    comparison=s['comparisons']['supplied_vs_replay'];clean=s['comparisons']['replay_vs_clean']
    clean_description='matches the recorded replay exactly, excluding timings' if clean['max_abs_difference']==0 else f"agrees with the recorded replay to {clean['max_abs_difference']:.6g}, excluding timings"
    table='\n'.join(f"| {r['B']:.2f} | {r['valley']:+d} | {r['radius']:.3f} | {r['intervals']}/{r['transport_intervals']} | {r['label']} | {r['max_node_gap_meV']:.6g} | {r['min_link_overlap']:.8f} |" for r in rows)
    text=f'''# v077p migration review

**The new braid-label entry point uses the published guarded APIs and reproduces all eight supplied classifications. Its delivery contract remains incomplete.** The consumer still exits successfully when every measurement is rejected or when no pair is found. A later discovery exception loses earlier in-memory rows. These are concrete software findings, not failed graphene measurements.

![Retained migration labels and sampled scalar gates](migration_review.png)

## What was verified

The unchanged v077p attachment is `partner_v077p.zip`, SHA-256 `{load('INPUT_MANIFEST.json')['archive_sha256']}`. The five source hashes in its result record match the attachment. The guarded modules, loader, tests, negative-control recorder, prior plan and nested v074p archive are byte-identical to the published `variant-guard-repairs` release at `02bbe167f01b2197b07f6b52e388bb7b5946f481`; see `SOURCE_COMPARISON.json`.

One pass ran the unchanged entry point with passive recording; a second ran it without instrumentation in another fresh extraction. Both produced the expected eight rows. Excluding timings, {comparison['numeric_exact']} of {comparison['numeric_leaves']} numeric leaves matched the supplied results exactly; the largest difference was {comparison['max_abs_difference']:.6g}. The clean repeat {clean_description}. Labels, coordinates and source identities are unchanged. Differences at roundoff level occur in winding values.

The supplied test suite passes all 38 tests (`TESTS.log`). Its six structured negative controls replay (`NEGATIVE_NEGATIVE_CONTROLS.json`). These tests exercise the helpers. The consumer-specific failure injections below additionally exercise the new entry point.

| B | Valley | Radius | Loop/transport intervals | Label | Largest node gap (meV) | Smallest link overlap |
|---:|---:|---:|---:|---|---:|---:|
{table}

Each B/valley has **two coupled settings**: radius .012 with 96/300 intervals, and radius .008 with 192/600. Radius and resolution are not varied independently in this attachment. Winding signs depend on frame orientation; the SAME/OPPOSITE comparison uses their product.

## Evidence retained by this review

The original JSON counts {s['ledger_rows']:,} diagnostic rows but does not save them. It supplies only selected path endpoints, a basis count/hash, source hashes and policy thresholds. Contrary to the consumer docstring, it does not serialize full coordinate arrays, the ordered index list or complete model defaults for each row. The source and nested archive permit reconstruction, but reconstruction is distinct from retained run evidence.

Reviewer sidecars now retain {s['model_records']} constructor records with defaults and ordered indices, harmonic arguments, all eight geometries, and {s['ledger_rows']:,} raw diagnostics: {s['ledger_counts'].get('frame',0):,} frames, {s['ledger_counts'].get('link',0):,} links and {s['ledger_counts'].get('angle',0):,} angle increments. Two node searches and {s['refinement_records']} refinement returns are recorded; {s['refinement_failures']} of these refinements report failure. Full eigenvectors, full Hamiltonians and every optimizer evaluation are not retained.

`reconcile.py` reconstructs root/external gaps from saved spectra, winding sums from angle increments, all sampled scalar gate summaries and model/case identities. It checks the frame coordinates against complete geometry and checks exact K/K′ coordinate negation. {s['checks']:,} reconciliation checks pass. This is record reconciliation using the same underlying computations, not an independent physics engine.

## Consumer release controls

| Injected condition | Observed result | Required disposition |
|---|---|---|
| Every pair measurement raises `gt.Rejected` | Eight REJECTED rows retained; process exits 0 | Keep the rows and return nonzero for the expected-case acceptance command |
| Both node searches return no pair | Two NO_PAIR rows retained; process exits 0 | Enumerate missing expected cases and return nonzero |
| Second B discovery raises after four synthetic returns | Process exits 1; no new result JSON is written | Persist completed rows and structured discovery failure before exiting |
| MR1 is deliberately violated | METAMORPHIC JSON records false; process exits 0 | Make assertion failures affect exit status; keep diagnostics separate |

These controls use declared runtime substitutions on unchanged source in disposable directories. Their fake node/measurement results are **not scientific evidence**. Each subprocess exit and produced-file hash is in `EXECUTIONS.json`; all logs and produced records are retained.

## Remaining scope and documentation corrections

- Treat this as a new guarded braid-label entry point. The preserved `producers.py` dispatcher still calls historical topology code; running that old dispatcher does not invoke the new module.
- The included `PLAN.json` inside the attachment is the earlier API campaign plan, with Wilson/sign/sparse scopes and a statement of no new root search. This consumer actually calls `find_nodes` twice. Use a migration-specific plan; the review's separate `PLAN.json` declares its own scope and budgets.
- The metamorphic producer has only an archive-activation import added since v076; `claim_lint.py` is unchanged. The v076 release-gate and claim-binding findings therefore remain relevant. MR6 is still an unconditional diagnostic, and MR7 compares only three models.
- The numerical metamorphic replay agrees with the supplied nine rows, which comprise eight asserted rows plus one unconditional diagnostic. This does not prove an exact C3 relation from sharing an index set.
- README lint returns four findings and exit 1. They include scope wording, Unicode minus parsing and rounded node-gap matching. Four lint findings do not mean four numerical failures, and a passing prose lint would not establish correct scientific claims.
- The partner's per-row timing starts after model construction and node discovery. The prose's approximately 24.6-second sum is not an end-to-end bound. `EXECUTIONS.json` records separate reviewer wall times including setup, discovery and output; no speed comparison is claimed.

Only this consumer, this N=4 model family and these sampled settings were checked. There is no continuous-path proof, complete node inventory, Euler-class change, independent K′ implementation, cutoff-convergence claim or experimental validation. The remaining consumers and sparse Newton/event detection stay outside this migration.

## Reproduce

Use Python 3.12 with the versions in `REQUIREMENTS.txt`. `run_review.py` extracts fresh sources, removes only generated outputs in those temporary copies and applies fixed time limits. It never modifies the attachment.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python run_review.py
python reconcile.py
python report.py
python verify_package.py --results-only
```

Run `python verify_package.py` before recomputation to verify the distributed hashes. Its expected exit-code checks deliberately include the failing partner behaviors demonstrated by synthetic controls.

Review `SUMMARY.json`, `EXECUTIONS.json`, `FABLE_NEXT_PASS.md` and the raw sidecars before quoting these results. The evidence-preserving wrapper supplements the original producer; it does not repair its exit or persistence behavior.
'''
    (ROOT/'README.md').write_text(text)
    print('Wrote README and figure from retained records')

if __name__=='__main__': run()
