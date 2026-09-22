"""Finite-cutoff comparison from preserved results; no extrapolated limit."""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.optimize import linear_sum_assignment
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'PLAN.json').read_text())
NEW={e:json.loads((ROOT/f'{e.upper()}.json').read_text()) for e in P['engines']}
if any(not r['status'].startswith('N8_LOCAL_DIAGNOSTICS') for r in NEW.values()):raise SystemExit('N8 source runs incomplete')
OLD={N:json.loads((ROOT.parent/'r1_merger'/f'N{N}.json').read_text()) for N in [4,6]}
REF={N:json.loads((ROOT.parent/'r1_merger'/f'REFINED_N{N}.json').read_text()) for N in [4,6]}
def distance(a,b):
 if len(a)!=len(b):return None
 if not a:return 0.
 c=np.array([[np.linalg.norm(np.array(x['f'])-y['f']) for y in b] for x in a]);i,j=linear_sum_assignment(c);return float(max(c[i,j]))
def fold(N,e):return (NEW[e] if N==8 else OLD[N]['engines'][e])['folds'][-1]
def sweeps(N,e):return (NEW[e] if N==8 else OLD[N]['engines'][e])['sweeps']
def minima(N,e):return (NEW[e] if N==8 else REF[N]['engines'][e])['minima']
def fixed_min(N,e):return next(x for x in minima(N,e) if x['D_meV']==40.5)['attempts'][0]
S={'scope':'Observed finite-cutoff sensitivity of a previously identified local merger; no infinite-cutoff error estimate','N8':{},'comparison':{},'engine_root_comparisons':[]}
for e,r in NEW.items():
 loops=[l for row in r['node_indices'] for l in row['loops']]+r['enclosing_indices'];mins=[a for row in r['minima'] for a in row['attempts']];candidates=[a for row in r['minima'] for a in row['candidates']]
 direction=r['direction_comparisons']
 S['N8'][e]={'status':r['status'],'warnings':r['warnings'],'dimension':r['dimension'],'nG':r['nG'],'sweep_rows':sum(map(len,r['sweeps'].values())),'direction_comparisons':len(direction),'direction_disagreements':sum(x['coordinate_difference'] is None or x['coordinate_difference']>P['engine_match_thresholds']['coordinates'] for x in direction),'max_direction_coordinate_difference':max(x['coordinate_difference'] for x in direction if x['coordinate_difference'] is not None),'fold_trials_passed':sum(x['criteria_pass'] for x in r['folds']),'fold_trials_total':len(r['folds']),'fold_refinement':r['fold_refinement'],'loop_checks_passed':sum(x['sampling_checks_pass'] for x in loops),'loop_checks_total':len(loops),'maximum_phase_step':max(x['max_phase_step'] for x in loops),'stationary_minima_passed':sum(x['criteria_pass'] for x in mins),'stationary_minima_total':len(mins),'maximum_gradient_norm':max(x['gradient_norm'] for x in mins),'candidate_optimizer_failures':sum(not x['optimizer_success'] for x in candidates),'minimum_anchor_overlap':r['all_evaluations']['minimum_anchor_overlap'],'minimum_sampled_exterior_gap_meV':r['all_evaluations']['minimum_sampled_exterior_gap_meV'],'max_affine_matrix_error_meV':max(x['matrix_error_meV'] for x in r['affine_checks']),'native_fold_check':r['native_fold_check']}
 vals=[]
 for N in [4,6,8]:
  f=fold(N,e);m=fixed_min(N,e);fw=sweeps(N,e)['forward'];vals.append({'N':N,'fold_D_meV':f['D_meV'],'fold_f':f['f'],'fixed_D40_5_gap_meV':m['gap_meV'],'fixed_D40_5_minimum_f':m['f'],'last_recovered_pair_D':max(x['D_meV'] for x in fw if len(x['roots'])==2),'first_unrecovered_D':min(x['D_meV'] for x in fw if len(x['roots'])==0)})
 shifts=[]
 for a,b in zip(vals[:-1],vals[1:]):
  shifts.append({'from_N':a['N'],'to_N':b['N'],'signed_fold_D_change_meV':b['fold_D_meV']-a['fold_D_meV'],'absolute_fold_D_change_meV':abs(b['fold_D_meV']-a['fold_D_meV']),'fold_coordinate_change':float(np.linalg.norm(np.array(b['fold_f'])-a['fold_f'])),'signed_fixed_D_gap_change_meV':b['fixed_D40_5_gap_meV']-a['fixed_D40_5_gap_meV'],'absolute_fixed_D_gap_change_meV':abs(b['fixed_D40_5_gap_meV']-a['fixed_D40_5_gap_meV'])})
 ratios={k:(shifts[1][k]/shifts[0][k] if shifts[0][k] else None) for k in ['absolute_fold_D_change_meV','fold_coordinate_change','absolute_fixed_D_gap_change_meV']}
 shared=[]
 for N0,N1 in [(4,6),(6,8)]:
  for a,b in zip(sweeps(N0,e)['forward'],sweeps(N1,e)['forward']):
   assert a['D_meV']==b['D_meV'];shared.append({'from_N':N0,'to_N':N1,'D_meV':a['D_meV'],'counts':[len(a['roots']),len(b['roots'])],'maximum_matched_coordinate_change':distance(a['roots'],b['roots'])})
 S['comparison'][e]={'values':vals,'successive_shifts':shifts,'second_over_first_change_ratios':ratios,'shared_station_root_changes':shared}
for a,b in zip(NEW['bm']['sweeps']['forward'],NEW['ref']['sweeps']['forward']):
 assert a['D_meV']==b['D_meV'];S['engine_root_comparisons'].append({'D_meV':a['D_meV'],'counts':[len(a['roots']),len(b['roots'])],'maximum_matched_coordinate_difference':distance(a['roots'],b['roots'])})
S['engine_comparison']={'fold_D_difference_meV':abs(fold(8,'bm')['D_meV']-fold(8,'ref')['D_meV']),'fold_coordinate_difference':float(np.linalg.norm(np.array(fold(8,'bm')['f'])-fold(8,'ref')['f'])),'fixed_D_gap_difference_meV':abs(fixed_min(8,'bm')['gap_meV']-fixed_min(8,'ref')['gap_meV']),'count_disagreements':sum(x['counts'][0]!=x['counts'][1] for x in S['engine_root_comparisons']),'max_matched_coordinate_difference':max(x['maximum_matched_coordinate_difference'] for x in S['engine_root_comparisons'] if x['maximum_matched_coordinate_difference'] is not None)}
T=P['engine_match_thresholds'];c=S['engine_comparison'];S['engine_criteria_pass']=c['fold_D_difference_meV']<T['fold_D_meV'] and c['fold_coordinate_difference']<T['coordinates'] and c['fixed_D_gap_difference_meV']<T['fixed_D_gap_meV'] and c['count_disagreements']==0 and c['max_matched_coordinate_difference']<T['coordinates']
S['all_N8_diagnostics_pass']=all(x['status']=='N8_LOCAL_DIAGNOSTICS_PASS_NOT_CONVERGENCE_CERTIFICATE' for x in NEW.values())
S['input_sha256']={str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'BM.json',ROOT/'REF.json',*[ROOT.parent/'r1_merger'/f'{prefix}N{N}.json' for N in [4,6] for prefix in ['', 'REFINED_']]]}
(ROOT/'SUMMARY.json').write_text(json.dumps(S,indent=2)+'\n')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#26384e','text.color':'#1d334d','xtick.color':'#455a70','ytick.color':'#455a70','axes.edgecolor':'#aebdcb','grid.color':'#dee5ed','figure.facecolor':'#f7f9fc','axes.facecolor':'white'})
colors={4:'#277bc2',6:'#dc713d',8:'#19867d'}
fig,axs=plt.subplots(2,2,figsize=(14,10),layout='constrained');fig.suptitle('R1: testing the local merger at a larger cutoff',fontsize=22,fontweight='bold',x=.035,ha='left')
vals=S['comparison']['bm']['values'];shifts=S['comparison']['bm']['successive_shifts'];Ns=[v['N'] for v in vals]
ax=axs[0,0];ys=[v['fold_D_meV'] for v in vals];ax.plot(Ns,ys,c='#92a2b2',lw=1.6)
for N,y in zip(Ns,ys):
 ax.scatter(N,y,s=70,c=colors[N],zorder=4);ax.annotate(f'{y:.7f}',xy=(N,y),xytext=(0,13 if N!=6 else -23),textcoords='offset points',ha='center',color=colors[N],fontsize=11)
ax.scatter(Ns,[v['fold_D_meV'] for v in S['comparison']['ref']['values']],s=100,marker='x',c='#22364c',lw=1.2,label='Reference engine (overlaps BM)',zorder=5)
ax.set(xlabel='Momentum cutoff N',ylabel='Calculated local merger D* (meV)',title='A  Merger location at three cutoffs',xticks=Ns,xlim=(3.4,8.6));ax.ticklabel_format(axis='y',useOffset=False);ax.margins(y=.2);ax.grid(alpha=.5);ax.legend(loc='lower right',fontsize=9,frameon=False)
ax=axs[0,1];changes=[x['absolute_fold_D_change_meV'] for x in shifts]
ax.bar(['N4 → N6','N6 → N8'],changes,color=[colors[6],colors[8]],width=.5)
if all(x>0 for x in changes):ax.set_yscale('log');ax.set_ylim(min(changes)/4,max(changes)*5)
for i,(y,sh) in enumerate(zip(changes,shifts)):
 ax.annotate(f"{sh['signed_fold_D_change_meV']:+.8f} meV",xy=(i,y),xytext=(0,9),textcoords='offset points',ha='center',fontsize=11)
ax.set(ylabel='Magnitude of successive D* change (meV)',title='B  Successive shifts · labels retain their signs');ax.grid(axis='y',alpha=.5);ax.set_axisbelow(True)
ratio=S['comparison']['bm']['second_over_first_change_ratios']['absolute_fold_D_change_meV']
if ratio and ratio<1:ax.text(.97,.94,f'{1/ratio:,.0f}× smaller second change',transform=ax.transAxes,ha='right',va='top',fontsize=12,fontweight='bold',color=colors[8])
ax.text(.03,.03,'Two increments do not establish an infinite-cutoff error bound.',transform=ax.transAxes,fontsize=9)
ax=axs[1,0];g=[v['fixed_D40_5_gap_meV'] for v in vals];ax.plot(Ns,g,'-',c='#92a2b2',lw=1.6)
for N,y in zip(Ns,g):
 ax.scatter(N,y,c=colors[N],s=70);ax.annotate(f'{y:.8f}',xy=(N,y),xytext=(0,-24 if N==6 else 13),textcoords='offset points',ha='center',color=colors[N],fontsize=11)
ax.scatter(Ns,[v['fixed_D40_5_gap_meV'] for v in S['comparison']['ref']['values']],s=95,marker='x',c='#22364c',lw=1.2)
ax.set(xlabel='Momentum cutoff N',ylabel='Checked local upper-gap minimum (meV)',title='C  Same D=40.5 meV at every cutoff',xticks=Ns,xlim=(3.4,8.6));ax.ticklabel_format(axis='y',useOffset=False);ax.margins(y=.25);ax.grid(alpha=.5)
ax.text(.97,.92,'Positive stationary minima; no global lower bound.',transform=ax.transAxes,ha='right',fontsize=9)
ax=axs[1,1]
for N0,N1,color in [(4,6,colors[6]),(6,8,colors[8])]:
 rows=[x for x in S['comparison']['bm']['shared_station_root_changes'] if x['from_N']==N0 and x['to_N']==N1 and x['counts']==[2,2]]
 ax.plot([x['D_meV'] for x in rows],[x['maximum_matched_coordinate_change'] for x in rows],'o-',c=color,ms=4,label=f'N{N0} → N{N1}')
if all(x['maximum_matched_coordinate_change']>0 for x in S['comparison']['bm']['shared_station_root_changes'] if x['counts']==[2,2]):ax.set_yscale('log')
ax.set(xlabel='Potential-energy amplitude D (meV)',ylabel='Largest matched root-position change',title='D  Node positions at shared two-root stations');ax.grid(alpha=.5);ax.legend(frameon=False,fontsize=10,loc='upper left')
ax.text(.97,.42,'Fractional momentum coordinates\nOnly stations recovering both roots at both cutoffs',transform=ax.transAxes,ha='right',fontsize=9)
fig.get_layout_engine().set(rect=(0,.055,1,.96),h_pad=.16,w_pad=.18)
fig.text(.035,.02,'Declared finite model, layer potentials ±D • shared measurement framework • observed cutoff sensitivity, not a convergence certificate or full braid claim',fontsize=10)
fig.savefig(ROOT/'cutoff.png',dpi=170);fig.savefig(ROOT/'cutoff.svg');plt.close(fig)

rows=[]
for v in vals:rows.append(f"| {v['N']} | {v['fold_D_meV']:.10f} | {v['fixed_D40_5_gap_meV']:.10f} | {v['last_recovered_pair_D']:.2f}–{v['first_unrecovered_D']:.2f} |")
n8=list(S['N8'].values());ne=sum(x['sweep_rows'] for x in n8);loops=sum(x['loop_checks_total'] for x in n8);lpass=sum(x['loop_checks_passed'] for x in n8);mins=sum(x['stationary_minima_total'] for x in n8);mpass=sum(x['stationary_minima_passed'] for x in n8)
reduction=1/ratio if ratio else None
text=f'''# R1 local merger: N=8 cutoff follow-up

**The local merger signature persists at N=8 in both engines. The merger-location change from N6 to N8 is much smaller than from N4 to N6, with a small reversal in direction. These are finite-cutoff numerical observations, not an infinite-cutoff convergence certificate.**

![Merger location, signed cutoff shifts, fixed-D gap and root-position changes](cutoff.png)

This extends the [local merger study](../r1_merger/README.md). Only the model's momentum cutoff changes. The local box, anchor and numerical acceptance thresholds are unchanged. The model retains ε=0.007, φ=15°, θ=1°, w1=110 meV, w0=88 meV and layer potentials ±D. D is an energy amplitude; the layer-potential difference is 2D. No experimental displacement-field calibration is supplied.

## Comparison

| Cutoff N | Calculated local fold D* (meV) | Checked local gap at D=40.5 (meV) | Last pair / first unrecovered station, D (meV) |
| --- | ---: | ---: | --- |
{chr(10).join(rows)}

The table shows BM results; the reference-engine values and every signed difference are retained in `SUMMARY.json`. N4 and N6 are read from the preserved parent reports, not rerun. The signed D* changes are **{shifts[0]['signed_fold_D_change_meV']:+.10f} meV** for N4→N6 and **{shifts[1]['signed_fold_D_change_meV']:+.10f} meV** for N6→N8. The second magnitude is about **{reduction:,.0f} times smaller**. The sign reversal means this is not a demonstrated monotone approach. No limiting value, asymptotic fit or error bar is inferred from the two increments.

The N8 engines differ in D* by {S['engine_comparison']['fold_D_difference_meV']:.3g} meV, and their largest matched-root difference over the sweep is {S['engine_comparison']['max_matched_coordinate_difference']:.3g} in fractional momentum coordinates. Both engines share the measurement framework; agreement is internal numerical evidence. Decimal digits identify the computed outputs and do not imply equivalent physical accuracy.

The fixed-D local gap and the local root positions are compared as additional observables. Panel D compares only stations where both cutoffs recover two accepted roots. It does not conceal the intervening root-count differences: every station's counts and unmatched comparison are present in the summary. A failed root search remains a failed search, not a proof of absence.

## N8 checks

Each engine uses {NEW['bm']['dimension']} Hamiltonian dimensions ({NEW['bm']['nG']} retained reciprocal-grid points, four internal components per point). There are **{ne} new sweep rows**, covering 27 D stations in both directions for both engines. All 54 forward/reverse inventory comparisons agree under the unchanged 1e-5 coordinate tolerance. The same local fold conditions pass at three derivative steps per engine, giving six passing fold trials. The final fold spectrum is additionally checked against each engine's original complex Hamiltonian.

**{lpass}/{loops} loop checks pass**, retaining opposite local node indices before the merger and zero net enclosing index at D=40 and D=40.5. Individual winding signs depend on the anchor orientation; only the opposite-index relation is compared across engines/cutoffs. Near D*−0.01, both radii are checked at 1,024 and 2,048 points. At D=40 the individual-node checks retain the parent's 128/256 points. The enclosing checks use 1,024/2,048 points at D=40 and 128/256 points at D=40.5, following the parent study and its successful refinement. No coarse near-fold mesh is promoted after failing a phase-step test.

**{mpass}/{mins} stationary-minimum checks pass** at D*+0.01, D*+0.05 and D=40.5, with three starting candidates per station/engine. The minimum conditions reuse the exact eigenvalue gradient, positive Hessian, Hessian refinement, gap, conditioning and displacement checks from `r1_merger/refine.py` without edits.

Candidate generation is explicitly different from the parent's initial Nelder-Mead stage: bounded least squares on the actual two-component map supplies candidate minima. Above the merger these outputs have positive gaps and are recorded as rejected roots. Their separate stationary-minimum checks determine whether they meet the minimum criteria. All candidate optimizer flags, gaps and final checks are retained. This avoids reusing the parent's stalled simplex termination as evidence; it does not turn an unsuccessful root search into a root or a global exclusion result.

The maximum gradient norm in the accepted minimum checks is {max(x['maximum_gradient_norm'] for x in n8):.3g} meV per fractional-coordinate unit. The minimum sampled anchor overlap is {min(x['minimum_anchor_overlap'] for x in n8):.6f}, and the minimum sampled exterior-band gap is {min(x['minimum_sampled_exterior_gap_meV'] for x in n8):.6f} meV. These conditioning measurements are sampled, not uniform bounds between all samples. Native/affine matrix and spectrum checks are retained in each engine report.

## Provenance and reproduction

`PLAN.json` was frozen before the N8 runs, after the N4/N6 results were known. This is follow-up validation, not discovery preregistration. The prior engine and diagnostic sources remain unchanged and are imported directly. Both new engine reports bind the plan, source files, N6 seed report and software versions. The summary also hashes all N4/N6/N8 result inputs. `MANIFEST.json` covers every completed file in this directory except itself. Earlier checkpoints and their failed attempts remain intact.

With NumPy, SciPy and Matplotlib installed, from the repository root:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_n8/run.py --engine bm --output replay_BM.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_n8/run.py --engine ref --output replay_REF.json
python research/benchmarks/r1_n8/report.py
```

The runner refuses to overwrite a report and preserves partial outputs on failure. The report builder reads the preserved `BM.json` and `REF.json`, not replay filenames. `cutoff.png` and `cutoff.svg` derive from the same saved data. The inherited analytic and native-model controls are documented in the parent study; this run adds direct checks at N8.

## Remaining limits

The smaller increment supports numerical stabilization of this local event across the three tested cutoffs. It does not bound the truncation error, certify exclusion of other roots, or establish uniform subspace isolation/continuous identity along the whole path. The earlier D≈38.08 comparison-segment crossing and D=36/42 relative-charge endpoint checks are not rerun at N8 in this checkpoint. Full braid acceptance, global Euler-obstruction removal, a second braid, experimental feasibility and novelty remain unestablished. The separate Vafek-paper convention discrepancy is unchanged.
'''
if not S['all_N8_diagnostics_pass'] or not S['engine_criteria_pass'] or any(x['direction_disagreements'] for x in n8):raise SystemExit('Unresolved N8 diagnostics: revise qualified narrative before publication')
if ratio is None or ratio>=1:raise SystemExit('Cutoff shift did not shrink: revise narrative before publication')
(ROOT/'README.md').write_text(text)
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.iterdir()) if p.is_file() and p.name!='MANIFEST.json'}
(ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'N8_all_pass':S['all_N8_diagnostics_pass'],'engine_criteria_pass':S['engine_criteria_pass'],'sweep_rows':ne,'loop_checks':[lpass,loops],'minimum_checks':[mpass,mins],'fold_D_values':[x['fold_D_meV'] for x in vals],'shift_ratio':ratio,'reduction_factor':reduction},indent=2))
