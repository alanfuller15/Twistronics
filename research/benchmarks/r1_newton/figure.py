"""Render the measured solver comparison and its limited acceptance scope."""
from pathlib import Path
import json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
S=json.loads((ROOT/'SUMMARY.json').read_text());R=json.loads((ROOT/'RESULTS.json').read_text())
assert S['all_checks_pass']
assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in S['source_hashes'].items())
navy='#173047';teal='#087f86';gray='#8494a5';paper='#f7f9fb';orange='#be7837'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':navy,'axes.labelcolor':navy,'axes.edgecolor':'#bdc8d3','xtick.color':navy,'ytick.color':navy,'svg.fonttype':'none'})
fig=plt.figure(figsize=(12,8.4),facecolor=paper)
fig.text(.065,.943,'Same sampled roots. Fewer eigensolves.',fontsize=25,weight='bold')
fig.text(.065,.898,'Guarded projected Newton  /  R1 N=8  /  two Hamiltonian implementations',fontsize=12,color='#5b6f82')
fig.text(.065,.857,'204 matched cases  ·  bounded search  ·  isolation and conditioning checks  ·  retained fallback',fontsize=11,color='#5b6f82')
ax=fig.add_axes([.075,.405,.54,.34]);groups=[(e,n) for e in ['bm','ref'] for n in ['p','q','upper']]
old=[];new=[];ratios=[]
for e,n in groups:
 rows=[r for r in R['primary'] if r['engine']==e and r['node']==n]
 old.append(1000*np.median([r['reference']['seconds'] for r in rows]));new.append(1000*np.median([r['variant']['seconds'] for r in rows]));ratios.append(np.median([r['reference']['seconds']/r['variant']['seconds'] for r in rows]))
x=np.arange(6);ax.bar(x-.18,old,.34,color=gray,label='Existing bounded least squares');ax.bar(x+.18,new,.34,color=teal,label='Guarded Newton')
for i,(h,ratio) in enumerate(zip(old,ratios)):ax.text(i,h+12,f'{ratio:.1f}×',ha='center',fontsize=10,weight='bold')
ax.set_xticks(x,[e.upper()+'\n'+n for e,n in groups]);ax.set_ylabel('Median solve time (ms)');ax.set_ylim(0,max(old)*1.28);ax.set_axisbelow(True);ax.grid(axis='y',alpha=.15);ax.legend(frameon=False,fontsize=8,loc='upper left',ncol=2);ax.spines[['top','right']].set_visible(False)
fig.text(.075,.78,'A  Median wall time by engine and node',fontsize=12,weight='bold')
ax2=fig.add_axes([.72,.405,.23,.34]);xx=np.arange(2)
for dx,key,color,label in [(-.18,'reference_total_eigensolves',gray,'Existing'),(.18,'variant_total_eigensolves',teal,'Newton')]:
 vals=[p[key] for p in S['performance']];ax2.bar(xx+dx,vals,.34,color=color,label=label)
 for i,v in enumerate(vals):ax2.text(i+dx,v+35,f'{v:,}',ha='center',fontsize=9)
ax2.set_xticks(xx,['BM','REF']);ax2.set_ylabel('Total eigensolves / 102 cases');ax2.set_ylim(0,1900);ax2.set_axisbelow(True);ax2.grid(axis='y',alpha=.15);ax2.spines[['top','right']].set_visible(False)
fig.text(.72,.78,'B  Work performed',fontsize=12,weight='bold')
ax3=fig.add_axes([.075,.125,.54,.17])
for e,color,marker in [('bm',teal,'o'),('ref','#456baf','x')]:
 ds=sorted(set(r['D_meV'] for r in R['primary']));ys=[max(r['root_distance'] for r in R['primary'] if r['engine']==e and r['D_meV']==d) for d in ds]
 ax3.plot(ds,ys,color=color,marker=marker,ms=4,lw=.8,label=e.upper())
ax3.axhline(1e-9,ls=':',color=orange,lw=1);ax3.text(38.99,1.4e-9,'Frozen match tolerance',ha='right',fontsize=8,color=orange)
ax3.set_yscale('log');ax3.set_ylim(1e-15,5e-9);ax3.set_xlim(38,39);ax3.set_xlabel('D (meV)');ax3.set_ylabel('Largest root difference\n(fractional coordinates)');ax3.legend(loc='lower right',frameon=False,fontsize=8,ncol=2);ax3.grid(axis='y',alpha=.15);ax3.spines[['top','right']].set_visible(False)
fig.text(.075,.326,'C  Agreement with the current solver',fontsize=12,weight='bold')
fig.text(.70,.326,'D  Validation checks',fontsize=12,weight='bold')
for y,text in [(.278,'204 / 204  primary comparisons'),(.241,'6 / 6  forced fallback cases'),(.204,'14 / 14  analytic controls'),(.167,'6 / 6  near-merger expectations')]:fig.text(.70,y,text,fontsize=11)
fig.text(.70,.124,'Post-merger candidates remain rejected.\nRejection does not prove root absence.',fontsize=9,color='#5b6f82')
fig.text(.075,.052,'Timings: this single-thread workload; labels show median paired speedups. No hardware-independent speed claim.',fontsize=9,color='#5b6f82')
fig.text(.075,.025,'Solver validation only. Continuous node identity, full braid acceptance and Euler-class change remain open.',fontsize=10,weight='bold')
fig.savefig(ROOT/'guarded_newton.png',dpi=190,facecolor=paper);fig.savefig(ROOT/'guarded_newton.svg',facecolor=paper);plt.close(fig)
perf='\n'.join(f"| {p['engine'].upper()} | {p['cases']} | {p['reference_total_eigensolves']:,} | {p['variant_total_eigensolves']:,} | {p['median_per_case_speedup']:.2f}× | {p['primary_fallbacks']} |" for p in S['performance'])
readme=f'''# R1: guarded Newton solver variant

**The new variant matches all 204 sampled N8 root comparisons in both engines.** Median per-case speedups over the current bounded least-squares solver are {S['performance'][0]['median_per_case_speedup']:.2f}× (BM) and {S['performance'][1]['median_per_case_speedup']:.2f}× (reference) on this single-thread workload. Median eigensolve counts fall from 14 to 4 in both engines. This is a solver-validation batch, not a new topology measurement.

![Measured solve time, eigensolve counts, root agreement and validation](guarded_newton.png)

## What was implemented

The variant adapts the partner study's projected-derivative Newton idea to the **existing real affine R1 Hamiltonians**. It adds a bounded search, trust-limited backtracking on the actual gap, finite/real/symmetric coefficient checks, pair isolation and anchor-overlap checks, and final Jacobian rank/conditioning gates. A guarded bounded least-squares fallback retains the original seed anchor and box.

The original exhausted-iteration position/gap mismatch is fixed in the new implementation: every returned pair points to its exact saved evaluation. The supplied partner implementation is preserved unchanged for a regression comparison and attribution.

**Callers must check `accepted`.** A small gap or optimizer-success flag alone does not accept a root. The precise API and its thresholds are in [METHOD.md](METHOD.md); the implementation is [solver.py](solver.py).

## Measured comparison

| Engine | Primary cases | Existing eigensolves | Variant eigensolves | Median paired speedup | Primary fallbacks |
|---|---:|---:|---:|---:|---:|
{perf}

The primary cases cover 17 D stations from 38 to 39 meV, roots p/q/upper, two seed choices, and both engines. The current solver and candidate receive identical seeds. Counts include reference evaluations for numerical Jacobians; timings include candidate guards and recording. Common family construction and subsequent native checks are outside the timed solver calls. These are local measurements, not general speed guarantees.

The maximum root-coordinate difference from the current solver is **{S['maximum_root_difference']:.3g}**, below the frozen 1e-9 fractional-coordinate tolerance. The largest native-complex-Hamiltonian residual gap is **{S['maximum_native_gap_meV']:.3g} meV**; the maximum native/affine four-band spectrum discrepancy is {S['maximum_native_spectrum_error_meV']:.3g} meV. Small numerical differences are not physical error bars.

## Guard and fallback evidence

- **14/14 analytic controls pass.** They include basis/sign covariance, the original failure-record bug, corrected exhaustion behavior, successful fallback, singular/ill-conditioned roots, isolation rejection, bounded search and invalid matrices/inputs.
- **6/6 forced fallback cases pass** with Newton disabled, covering all three N8 roots at D38 in both engines.
- **6/6 near-merger behavior checks match expectations.** Both engines recover the two tested roots at D40.38. Both reject the candidate search at D40.40; its positive gap is about 0.00263135 meV and the final Jacobian gate also fails. Rejection is a failed local search, not proof of absence.
- Independent reconciliation checks **{S['recorded_evaluations']:,} saved evaluations**, {S['newton_trials']} Newton trials, case coverage, acceptance gates, derivative-step equations, local boxes and returned-position/gap consistency. It freshly diagonalizes every final primary/fallback/stress position and recomputes projected Jacobian singular values.

## Scope and next use

The result supports using this **explicitly declared solver variant** for further sampled R1 continuation with the existing scientific acceptance checks. Its projected Jacobian is a local frozen-frame linearization; it is not inserted as the Jacobian of the fallback's changing anchored residual. Exact Hamiltonian derivatives and rapid root convergence do not supply the uniform uniqueness neighborhoods needed for continuous node identity.

Strain is fixed, layer potentials are ±D meV, and N=8 has dimension 596. There is no new charge or Euler-class calculation, full braid acceptance, experimental calibration, infinite-cutoff conclusion or independent physical validation. Both Hamiltonian implementations share this diagnostic. The current [surface-isolation checkpoint](../r1_surface/README.md) retains its separately stated numerical meaning.

## Sources and reproduction

- [Frozen plan](PLAN.json), [method and commands](METHOD.md), [runner](run.py), [independent report](report.py), [figure source](figure.py).
- [Complete measurements and histories](RESULTS.json), [reconciled summary](SUMMARY.json), [controls](CONTROLS.json), and their logs.
- [Original partner study ZIP](partner_engine_study.zip) and byte-identical [partner fast-engine source](partner_fast_engine.py). Credit: the partner study supplied by Alan Fuller. The original archive includes its own measurements against older solver paths; those speedups are distinct from this comparison.
- [Manifest](MANIFEST.json) binds the delivered files. The results additionally bind the current sources, frozen plan and inherited model/measurement inputs.

Parent commit: `0a8561d63524925f85e3a2c71e79b6553fb4df17`. The new checkpoint lives entirely in this directory; historical evidence remains available at its original paths.
'''
(ROOT/'README.md').write_text(readme)
print('Wrote guarded_newton.png, guarded_newton.svg and README.md from reconciled records.')
