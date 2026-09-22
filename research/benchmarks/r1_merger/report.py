"""Summarize preserved baseline and targeted refinement; never erase failures."""
from pathlib import Path
import json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'PLAN.json').read_text());RP=json.loads((ROOT/'REFINEMENT_PLAN.json').read_text())
R={N:json.loads((ROOT/f'N{N}.json').read_text()) for N in P['N_values']}
F={N:json.loads((ROOT/f'REFINED_N{N}.json').read_text()) for N in P['N_values']}
if any(not r['status'].startswith('LOCAL_MERGER_DIAGNOSTICS') for r in R.values()) or any(not r['status'].startswith('TARGETED_REFINEMENT') for r in F.values()):raise SystemExit('Incomplete source reports')
S={'scope':'Numerical evidence for a local upper-node fold/annihilation in the declared finite model; not a rigorous absence or full braid certificate','cutoffs':{}}
for N,r in R.items():
 c={'original_status':r['status'],'original_warnings':r['warnings'],'refinement_status':F[N]['status'],'refinement_warnings':F[N]['warnings'],'engines':{}}
 for e,a in r['engines'].items():
  b=F[N]['engines'][e];fold=a['folds'][-1];fw=a['sweeps']['forward'];pair=[x for x in fw if len(x['roots'])==2];absent=[x for x in fw if len(x['roots'])==0]
  loops=[l for x in b['node_indices'] for l in x['loops']]+b['enclosing_indices']
  mins=[x for row in b['minima'] for x in row['attempts']]
  baseline_mins=[x for row in a['post_event_minima'] for x in row['attempts']]
  comparisons=a['direction_comparisons'];valid_diffs=[x['coordinate_difference'] for x in comparisons if x['coordinate_difference'] is not None]
  c['engines'][e]={
    'sweep_rows':sum(len(x) for x in a['sweeps'].values()),'direction_comparisons':len(comparisons),
    'direction_disagreements':sum(x['coordinate_difference'] is None or x['coordinate_difference']>P['coordinate_agreement'] for x in comparisons),'max_direction_coordinate_difference':max(valid_diffs),
    'last_recovered_pair_D_meV':max(x['D_meV'] for x in pair),'first_unrecovered_D_meV':min(x['D_meV'] for x in absent),
    'fold_D_meV':fold['D_meV'],'fold_f':fold['f'],'fold_gap_meV':fold['gap_meV'],'fold_trials_passed':sum(x['criteria_pass'] for x in a['folds']),'fold_trials_total':len(a['folds']),
    'fold_D_derivative_spread_meV':a['fold_refinement']['D_spread_meV'],'fold_parameter_coefficient':fold['metrics']['parameter_coefficient'],'fold_curvature_coefficient':fold['metrics']['curvature_coefficient'],
    'original_minimum_optimizer_failures':sum(not x['optimizer_success'] for x in baseline_mins),
    'refined_loop_checks_passed':sum(x['sampling_checks_pass'] for x in loops),'refined_loop_checks_total':len(loops),'max_refined_phase_step':max(x['max_phase_step'] for x in loops),
    'stationary_minimum_checks_passed':sum(x['criteria_pass'] for x in mins),'stationary_minimum_checks_total':len(mins),'maximum_gradient_norm':max(x['gradient_norm'] for x in mins),'minimum_gap_Hessian_eigenvalue':min(min(ev) for x in mins for ev in x['gap_Hessian_eigenvalues']),
    'minimum_sampled_subspace_overlap':min(a['all_evaluations']['minimum_anchor_overlap'],b['all_evaluations']['minimum_anchor_overlap']),
    'minimum_sampled_exterior_gap_meV':min(a['all_evaluations']['minimum_sampled_exterior_gap_meV'],b['all_evaluations']['minimum_sampled_exterior_gap_meV']),
    'post_event_minima':[{'D_meV':row['D_meV'],'gap_meV':row['attempts'][0]['gap_meV'],'f':row['attempts'][0]['f']} for row in b['minima']]}
 c['engine_fold_D_difference_meV']=abs(c['engines']['bm']['fold_D_meV']-c['engines']['ref']['fold_D_meV'])
 S['cutoffs'][str(N)]=c
S['cutoff_fold_D_difference_meV']=abs(S['cutoffs']['4']['engines']['bm']['fold_D_meV']-S['cutoffs']['6']['engines']['bm']['fold_D_meV'])
S['all_refinement_reports_pass']=all(x['status']=='TARGETED_REFINEMENT_DIAGNOSTICS_PASS_NOT_CERTIFICATE' for x in F.values())
S['all_fold_trials_pass']=all(a['criteria_pass'] for r in R.values() for e in r['engines'].values() for a in e['folds'])
S['direction_disagreements']=sum(e['direction_disagreements'] for c in S['cutoffs'].values() for e in c['engines'].values())
(ROOT/'SUMMARY.json').write_text(json.dumps(S,indent=2)+'\n')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#25364c','text.color':'#182f49','xtick.color':'#46586c','ytick.color':'#46586c','axes.edgecolor':'#adbac8','grid.color':'#dce3eb','figure.facecolor':'#f7f9fc','axes.facecolor':'white'})
colors={4:'#247ac4',6:'#df693d'}
fig,axs=plt.subplots(2,2,figsize=(14,10),layout='constrained')
fig.suptitle('R1: numerical evidence for a local node-pair merger',fontsize=21,fontweight='bold',x=.035,ha='left')
ax=axs[0,0]
for N in P['N_values']:
 rec=R[N]['engines']['bm'];fold=rec['folds'][-1];Dstar=fold['D_meV']
 for direction,marker in [('forward','o'),('reverse','x')]:
  vals=[(row['D_meV'],np.linalg.norm(np.array(row['roots'][0]['f'])-row['roots'][1]['f'])**2) for row in rec['sweeps'][direction] if len(row['roots'])==2]
  ax.plot([x[0] for x in vals],[x[1]*1e4 for x in vals],'-' if direction=='forward' else 'none',marker=marker,ms=4.5,c=colors[N],label=f'N={N}, {direction}')
 ds=np.linspace(Dstar-.08,Dstar,50);ax.plot(ds,fold['metrics']['separation_squared_slope']*(ds-Dstar)*1e4,':',c=colors[N],lw=2)
 ax.scatter([Dstar],[0],c=colors[N],marker='D',s=45,zorder=5)
 ax.annotate(f'{Dstar:.4f}',xy=(Dstar,0),xytext=(Dstar-.035 if N==4 else Dstar+.02,1.6 if N==4 else 1.3),ha='center',color=colors[N],fontsize=10,arrowprops={'arrowstyle':'-','color':colors[N]})
ax.set(xlabel='Potential-energy amplitude D (meV)',ylabel=r'Pair separation squared ($10^{-4}$ fractional units²)',title='A  Finer sweeps approach the calculated merger',ylim=(-.75,4.9),xlim=(39.99,40.43));ax.grid(alpha=.5)
ax.legend(frameon=False,fontsize=9,loc='upper right');ax.text(.02,.05,'Diamonds: fold solutions. Dotted guides: local prediction.',transform=ax.transAxes,fontsize=9)
ax=axs[0,1]
for N in P['N_values']:
 rec=F[N]['engines']['bm'];fold=R[N]['engines']['bm']['folds'][-1];Dstar=fold['D_meV'];ds=[x['D_meV']-Dstar for x in rec['minima']];g=[x['attempts'][0]['gap_meV'] for x in rec['minima']]
 ax.plot(ds,g,'o-',c=colors[N],label=f'N={N}, checked stationary minima');pred=np.linspace(0,.05,30);ax.plot(pred,abs(fold['metrics']['parameter_coefficient'])*pred,':',c=colors[N],lw=2)
ax.set(xlabel=r'Distance above calculated merger $D-D_*$ (meV)',ylabel='Local upper-gap minimum (meV)',title='B  A positive local gap develops afterward');ax.grid(alpha=.5)
ax.legend(frameon=False,fontsize=9,loc='upper left');ax.text(.98,.04,'Three starting candidates checked at each point.\nThese are local minima, not global lower bounds.',transform=ax.transAxes,ha='right',fontsize=9)
ax=axs[1,0]
for N in P['N_values']:
 row=next(x for x in F[N]['engines']['bm']['node_indices'] if x['radius_fraction']==.1 and x['points']==2048)
 for i,loop in enumerate(row['loops']):
  z=np.array(loop['components']);phase=np.unwrap(np.angle(np.r_[z[:,0]+1j*z[:,1],z[0,0]+1j*z[0,1]]));phase=(phase-phase[0])/(2*np.pi)
  ax.plot(np.linspace(0,1,len(phase)),phase,'-' if N==6 else '--',c='#168581' if round(loop['index'])==1 else '#8956aa',lw=1.6,label=f'N={N}, index {round(loop["index"]):+d}')
ax.set(xlabel='Fraction of the loop traversed',ylabel=r'Accumulated phase / $2\pi$',title='C  Opposite local winding indices before merger',yticks=[-1,-.5,0,.5,1]);ax.grid(alpha=.5)
ax.legend(frameon=False,fontsize=9,loc='upper left');ax.text(.03,.05,'D = D* − 0.01 meV · 2,048 samples\nAnchored map; radius = 0.1 × separation',transform=ax.transAxes,ha='left',fontsize=9)
ax=axs[1,1];V=np.load(ROOT/'N6.npz')['bm_D40.5'][:,:,0];box=np.array(P['box_fractional'])
mesh=ax.pcolormesh(np.linspace(*box[0],V.shape[0]),np.linspace(*box[1],V.shape[1]),V.T,cmap='magma_r',norm=LogNorm(vmin=.02,vmax=float(V.max())),shading='nearest',rasterized=True)
cb=fig.colorbar(mesh,ax=ax,pad=.025);cb.set_label('Upper gap (meV)')
minimum=next(x for x in F[6]['engines']['bm']['minima'] if x['D_meV']==40.5)['attempts'][0];f=minimum['f'];ax.scatter(*f,marker='+',s=110,c='#057974',lw=2)
ax.annotate(f"Checked local minimum\n{minimum['gap_meV']:.6f} meV",xy=f,xytext=(.767,.625),color='white',fontsize=10,arrowprops={'arrowstyle':'->','color':'white'})
ax.set(xlabel=r'Fractional momentum $f_1$',ylabel=r'Fractional momentum $f_2$',title='D  Sampled gap in the local box · N=6, D=40.5')
fig.get_layout_engine().set(rect=(0,.055,1,.96),h_pad=.16,w_pad=.18)
fig.text(.035,.021,'BM curves shown; reference engine checked numerically • finite model, layer potentials ±D • sampled local evidence, not an absence certificate or full braid claim',fontsize=9.7)
fig.savefig(ROOT/'merger.png',dpi=170);fig.savefig(ROOT/'merger.svg');plt.close(fig)

rows=[]
for N,c in S['cutoffs'].items():
 e=c['engines']['bm'];gap=e['post_event_minima'][-1]['gap_meV']
 rows.append(f"| {N} | {e['last_recovered_pair_D_meV']:.2f}–{e['first_unrecovered_D_meV']:.2f} | {e['fold_D_meV']:.7f} | {c['engine_fold_D_difference_meV']:.2g} | {gap:.9f} |")
engines=[e for c in S['cutoffs'].values() for e in c['engines'].values()]
totalrows=sum(e['sweep_rows'] for e in engines);comparisons=sum(e['direction_comparisons'] for e in engines);failedmins=sum(e['original_minimum_optimizer_failures'] for e in engines)
ref_loops=sum(e['refined_loop_checks_total'] for e in engines);ref_pass=sum(e['refined_loop_checks_passed'] for e in engines);mins=sum(e['stationary_minimum_checks_total'] for e in engines);minpass=sum(e['stationary_minimum_checks_passed'] for e in engines)
text=f'''# R1 local upper-node merger study

**The finer sweeps, fold solutions, opposite local indices and positive stationary gap minima provide numerical evidence consistent with a local node-pair annihilation in the declared finite model. This is not a rigorous root-absence certificate or full braid acceptance.**

![Separation, local gap reopening, opposite indices and a sampled gap map](merger.png)

This follows the [event-interval inventory](../r1_events/README.md). It examines the two upper-gap roots that were recovered at D=40 but not at D=40.5. Earlier checkpoint sources/results remain unchanged. The model still uses ε=0.007, φ=15°, θ=1°, w1=110 meV, w0=88 meV and uniform layer potentials ±D. D is a potential-energy amplitude; the layer difference is 2D. There is no laboratory displacement-field calibration.

## What changed

| Cutoff N | Last pair / first unrecovered station, D (meV) | Calculated local fold D* (meV) | BM/reference D* difference (meV) | Checked local gap at D=40.5 (meV) |
| --- | --- | ---: | ---: | ---: |
{chr(10).join(rows)}

There are {totalrows} sweep rows: 27 D stations, two directions, two engines and two cutoffs. All {comparisons} forward/reverse inventory comparisons agree under the declared coordinate tolerance; the maximum matched coordinate difference is {max(e['max_direction_coordinate_difference'] for e in engines):.3g}. Missing roots remain failed searches; their absence is not the argument for annihilation. The added evidence is the local fold calculation, opposite local map indices and positive stationary gap minima beyond that fold.

All 12 fold trials meet the declared numerical criteria. They solve the two real components of the actual upper two-band Hamiltonian together with a vanishing momentum-Jacobian determinant. Each engine/cutoff repeats this using momentum derivative steps 1e-5, 5e-6 and 2.5e-6. The largest D* spread across those steps is {max(e['fold_D_derivative_spread_meV'] for e in engines):.3g} meV. This finite-difference agreement is not a formal error bound. The N4-to-N6 shift is **{S['cutoff_fold_D_difference_meV']:.6f} meV**; cutoff convergence is not established.

At the calculated fold, one Jacobian singular value is small while the other remains nonzero. In the left/right null directions, the measured parameter and quadratic momentum coefficients are nonzero and have the sign predicting two local roots below D*. These diagnostics support a generic local fold conditional on the smooth isolated two-band description. They do not prove a global root count.

## Initial failures and their targeted resolution

The original `N4.json` and `N6.json` runs retain unresolved-check status. Near D*−0.01, the 128/256-point loops yielded nominal ±1 indices but exceeded the frozen maximum phase increment; the initial 128-point enclosing loop also failed its phase-step check. In addition, {failedmins} of the 36 Nelder-Mead attempts hit their iteration limit. Such outputs were not promoted to successful checks.

After these issues were observed, `REFINEMENT_PLAN.json` declared a separate supplement. The original reports, thresholds and failed attempts were preserved. Near-fold node loops and the affected enclosing loop were reevaluated at 1,024 and 2,048 points. **{ref_pass}/{ref_loops} refined loop checks pass**, retaining opposite ±1 node indices and zero net enclosing index. The maximum refined phase step is {max(e['max_refined_phase_step'] for e in engines):.6f} radians, below π/4. The zero enclosing index alone cannot rule out an unresolved opposite-index pair.

The supplement also checks each candidate minimum using the exact eigenvalue first derivative of the affine Hamiltonian, then numerical Hessians at two step sizes. **{minpass}/{mins} stationary-minimum checks pass**: positive gap, small gradient, positive Hessian, agreement under derivative refinement and a small displacement from the original candidate. Maximum gradient norm is {max(e['maximum_gradient_norm'] for e in engines):.3g} meV per fractional-coordinate unit. This directly checks stationarity without changing a failed Nelder-Mead termination flag. The candidates share the original searches, so these are distinct local diagnostics, not independent global searches.

The smallest sampled two-band/anchor overlap over both stages is {min(e['minimum_sampled_subspace_overlap'] for e in engines):.6f}; the smallest sampled exterior-band gap is {min(e['minimum_sampled_exterior_gap_meV'] for e in engines):.6f} meV. These are sampled conditioning measurements, not bounds everywhere in momentum and D.

## Definition and scope of the local calculation

The local box is f1∈[0.765,0.793], f2∈[0.585,0.632]. The two-band anchor is at f=(0.779,0.6075), D=40.25. At every evaluation the actual eigenpair subspace is recomputed and aligned to that anchor using a polar decomposition. Its two real traceless components are (h11−h22, 2h12); their Euclidean norm is the upper gap. The reported indices are windings of this common anchored component map. Individual signs depend on the anchor orientation and can reverse between engines/cutoffs; the opposite-index relation is the comparison target. They are not a computed global Euler class.

The Hamiltonian family is affine in fractional momentum and D. Its precomputed matrices are checked against each engine's original complex Hamiltonian at the box corners/center and both D endpoints, including direct spectrum comparisons. Neither engine source is edited. Both engines share this local solver, analysis and diagnostics; their agreement is internal numerical evidence.

The sweep uses the union of 40–40.5 in 0.05 steps and 40.25–40.45 in 0.01 steps. Both directions begin with the two known D=40 seeds, retaining the last accepted pair across failures. Thus the reverse run tests recovery while decreasing D; it does not presume roots above the event. Local searches and branch matching are finite and do not certify identity between samples.

For fold interpretation, let a be the left-null projection of the D derivative and b the left-null projection of the second derivative in the null momentum direction. The local expansion is a(D−D*) + bq²/2. Its leading prediction for pair separation squared is −8a(D−D*)/b. The dotted guide in panel A uses those measured coefficients; it is not a fitted discovery result. Panel B's dotted guide uses |a|(D−D*). Plotted solid lines connect computed points. Panel D shows a 41×41 sampled local gap map; it is not an exclusion bound. The exact checked stationary point is overlaid separately.

## Provenance and reproduction

`PLAN.json` was frozen before the original local study; the parent event results were already known. `REFINEMENT_PLAN.json` was frozen after the initial numerical warnings and before the supplement. Neither is a discovery preregistration. Both original and refined JSON reports record hashes; all failed attempts and logs are preserved. `SUMMARY.json` and the figures derive from those saved reports. `MANIFEST.json` covers this directory's completed files except itself.

Four initial controls check an analytic fold, opposite map indices, an analytic post-fold Hessian and a known native-model root. A fifth control compares the eigenvalue gradient with a direct finite difference of the native-model gap. All five pass; both test logs are retained.

With NumPy, SciPy and Matplotlib installed, from the repository root:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_merger/test_study.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_merger/test_refine.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_merger/study.py --N 4 --output replay_N4.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_merger/study.py --N 6 --output replay_N6.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_merger/refine.py --N 4 --output replay_REFINED_N4.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_merger/refine.py --N 6 --output replay_REFINED_N6.json
python research/benchmarks/r1_merger/report.py
```

Runners refuse to overwrite existing outputs. The refinement reads the preserved `N4.json`/`N6.json`, not replay filenames; its recorded parent hash identifies the input. The report builder likewise reads the preserved source reports. The NPZ files hold arrays [f1 index, f2 index, (gap, exterior gap, overlap)] for each named engine/D map, with both box endpoints included.

## Remaining limits

A rigorous local root-count or absence certificate, broader cutoff convergence, continuous identity/isolation over the full path and the historical campaign's remaining acceptance gates are still open. This checkpoint concerns the local upper pair; it does not establish global Euler-obstruction removal, a complete or second braid, experimental feasibility or novelty. The earlier D≈38.08 segment crossing is a separate event. The projected-THF/Vafek-paper convention discrepancy is unchanged.
'''
if not S['all_refinement_reports_pass'] or not S['all_fold_trials_pass'] or S['direction_disagreements']:
 raise SystemExit('Outcome differs from the pass-qualified narrative: retain summary, revise narrative before publication')
(ROOT/'README.md').write_text(text)
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.iterdir()) if p.is_file() and p.name!='MANIFEST.json'}
(ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'all_refinements_pass':S['all_refinement_reports_pass'],'folds_pass':S['all_fold_trials_pass'],'direction_disagreements':S['direction_disagreements'],'sweep_rows':totalrows,'refined_loops':[ref_pass,ref_loops],'stationary_minima':[minpass,mins],'initial_minimizer_failures':failedmins,'cutoff_D_shift_meV':S['cutoff_fold_D_difference_meV']},indent=2))
