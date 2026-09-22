"""Derive tables and scientific figures from preserved event-interval reports."""
from pathlib import Path
import json,hashlib
from collections import Counter
import numpy as np
from scipy.optimize import linear_sum_assignment
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'PLAN.json').read_text())
R={N:json.loads((ROOT/f'N{N}.json').read_text()) for N in P['N_values']}
if any(not r['status'].startswith('BOUNDED_TRACKING_COMPLETE') for r in R.values()):
    raise SystemExit('Refusing a completion report from incomplete runs')
summary={'scope':'Sampled finite-seed inventory and local crossing bracket; not a complete braid or root-count proof','cutoffs':{},'sampled_sign_changes':[],'image_changes':[],'unmatched_tracks':[],'engine_comparisons':[]}
for N,r in R.items():
    grids=[v['grid_agreement'] for s in r['stations'] for v in s['gaps'].values() if v['grid_agreement'] is not None]
    attempts=[a for s in r['stations'] for v in s['gaps'].values() for a in v['attempts']]
    accepted=[a for a in attempts if a['accepted']]
    flat=[a for s in r['stations'] for a in s['flat']]
    links=[a for s in r['stations'] for v in s['gaps'].values() for a in v['tracking']['links']]
    summary['cutoffs'][str(N)]={
      'status':r['status'],'stations':len(r['stations']),
      'grid_comparisons':len(grids),'grid_agreements':sum(grids),
      'adjacent_seed_attempts':len(attempts),'rejected_seed_attempts':len(attempts)-len(accepted),
      'max_accepted_adjacent_gap_meV':max(a['gap_meV'] for a in accepted),
      'max_flat_gap_meV':max(a['gap_meV'] for a in flat),
      'max_matched_step':max(a['distance'] for a in links),
      'ambiguous_links':sum(a['ambiguous'] for a in links),
      'warning_reasons':dict(Counter(a['reason'] for a in r['coverage_warnings'])),
      'crossing_brackets':{e:c['bracket_D_meV'] for e,c in r['crossing_refinements'].items()},
      'inventories':[{k:s[k] for k in ['engine','D_meV']}|{g:len(v['roots']) for g,v in s['gaps'].items()} for s in r['stations']]}
    by_engine={e:[s for s in r['stations'] if s['engine']==e] for e in P['engines']}
    for a,b in zip(by_engine['bm'],by_engine['ref']):
      assert a['D_meV']==b['D_meV']
      for gap in P['adjacent_gaps']:
        x,y=a['gaps'][gap]['roots'],b['gaps'][gap]['roots'];dist=None
        if len(x)==len(y) and x:
          C=np.array([[np.linalg.norm(np.array(u['f'])-v['f']) for v in y] for u in x]);i,j=linear_sum_assignment(C);dist=float(max(C[i,j]))
        elif not x and not y:dist=0.
        summary['engine_comparisons'].append({'N':N,'D_meV':a['D_meV'],'gap':gap,'counts':[len(x),len(y)],'max_coordinate_difference':dist})
    for engine,stations in by_engine.items():
      for old,new in zip(stations[:-1],stations[1:]):
        for gap in P['adjacent_gaps']:
          ov,nv=old['gaps'][gap],new['gaps'][gap]
          for track in nv['tracking']['unmatched_previous']:
            summary['unmatched_tracks'].append({'N':N,'engine':engine,'gap':gap,'track':track,'D_interval_meV':[old['D_meV'],new['D_meV']]})
          for link in nv['tracking']['links']:
            a=ov['roots'][link['from_index']]['geometry'];b=nv['roots'][link['to_index']]['geometry']
            base={'N':N,'engine':engine,'gap':gap,'track':link['track'],'D_interval_meV':[old['D_meV'],new['D_meV']]}
            if not np.allclose(a['image_shift'],b['image_shift'],atol=1e-10):
              summary['image_changes'].append(base);continue
            if a['offset']*b['offset']<0:
              summary['sampled_sign_changes'].append(base|{'endpoint_offsets':[a['offset'],b['offset']],'endpoint_t':[a['t'],b['t']],'both_inside_segment':0<a['t']<1 and 0<b['t']<1,'ambiguous_link':link['ambiguous']})
summary['max_engine_root_difference']=max(x['max_coordinate_difference'] for x in summary['engine_comparisons'] if x['max_coordinate_difference'] is not None)
summary['engine_inventory_count_disagreements']=sum(x['counts'][0]!=x['counts'][1] for x in summary['engine_comparisons'])
(ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#243449','text.color':'#172b43','xtick.color':'#42536a','ytick.color':'#42536a','axes.edgecolor':'#b4c1ce','grid.color':'#dce3eb','figure.facecolor':'#f7f9fc','axes.facecolor':'white'})
colors={4:'#2879c5',6:'#e06a39'}
fig,axs=plt.subplots(2,2,figsize=(14,10),gridspec_kw={'width_ratios':[1.15,1]},layout='constrained')
fig.suptitle('R1 event interval: where the nodes move',fontsize=22,fontweight='bold',x=.035,ha='left')
ax=axs[0,0]
s6=[s for s in R[6]['stations'] if s['engine']=='bm']
for gap,color,marker in [('lower','#8c67a3','s'),('upper','#177e8e','o')]:
    for track in sorted({r['track'] for s in s6 for r in s['gaps'][gap]['roots']}):
      pts=[(s['D_meV'],r['f']) for s in s6 for r in s['gaps'][gap]['roots'] if r['track']==track]
      f=np.array([x[1] for x in pts]);ax.plot(f[:,0],f[:,1],c=color,lw=2,alpha=.8)
      ax.scatter(*f[0],c='white',edgecolors=color,marker=marker,s=55,zorder=4)
      ax.scatter(*f[-1],c=color,marker=marker,s=35,zorder=5)
for D,style in [(36,':'),(42,'--')]:
    s=next(s for s in s6 if s['D_meV']==D);f=np.array([r['f'] for r in s['flat']]);ax.plot(f[:,0],f[:,1],style,c='#556779',lw=1.4);ax.scatter(f[:,0],f[:,1],c='#263b52',marker='x',s=48)
    ax.annotate(f'D={D}',xy=f[0],xytext=(.432,.736 if D==36 else .767),fontsize=9,arrowprops={'arrowstyle':'-','color':'#7d8a99'})
c=R[6]['crossing_refinements']['bm']['evaluations'][-1]['upper']['f']
ax.scatter(*c,marker='*',s=160,c='#df9224',edgecolors='#633d00',zorder=6)
ax.annotate('local crossing',xy=c,xytext=(.68,.67),arrowprops={'arrowstyle':'->','color':'#5b6b7c'},fontsize=10)
ax.set(xlim=(.42,.93),ylim=(.52,.84),xlabel=r'Fractional momentum $f_1$',ylabel=r'Fractional momentum $f_2$',title='A  Sampled node trajectories · N=6, BM')
ax.legend(handles=[Line2D([],[],c='#177e8e',marker='o',label='Upper gap'),Line2D([],[],c='#8c67a3',marker='s',label='Lower gap'),Line2D([],[],c='#556779',ls='--',marker='x',label='Flat-node segment')],loc='upper left',fontsize=9,frameon=False)
ax.text(.02,.02,'Open marker: D=36. Filled: last recovered station.\nLines connect samples; they do not certify branch identity.',transform=ax.transAxes,fontsize=9,va='bottom')
ax=axs[0,1]
for N in P['N_values']:
    stations=[s for s in R[N]['stations'] if s['engine']=='bm'];first=stations[0]['gaps']['upper']['roots']
    for j,seed in enumerate(P['known_upper_seeds_at_D36']):
      track=min(first,key=lambda r:np.linalg.norm(np.array(r['f'])-seed))['track']
      pts=[(s['D_meV'],r['geometry']['offset']) for s in stations for r in s['gaps']['upper']['roots'] if r['track']==track]
      ax.plot([x[0] for x in pts],[x[1] for x in pts],'-' if j==0 else '--',marker='o' if N==4 else 'x',ms=5,c=colors[N],label=f'N={N}, '+('crossing node' if j==0 else 'nearby node'))
ax.axhline(0,c='#66778b',lw=1)
ax.set(xlim=(35.9,42.1),xlabel='Potential-energy amplitude D (meV)',ylabel='Signed offset in fractional coordinates',title='B  Local upper-gap motion · BM')
ax.legend(fontsize=9,frameon=False,loc='center left',bbox_to_anchor=(.01,.49));ax.grid(alpha=.45)
ax.text(.99,.98,'Offset = 0: node on comparison line\nSegment-interior test is recorded separately',transform=ax.transAxes,ha='right',va='top',fontsize=9)
ax=axs[1,0]
for i,N in enumerate(P['N_values']):
    a,b=R[N]['crossing_refinements']['bm']['bracket_D_meV'];ax.plot([a,b],[i,i],c=colors[N],lw=8,solid_capstyle='butt');ax.plot([a,b],[i,i],'|',c=colors[N],ms=20)
    ax.text((a+b)/2,i+.16,f'{a:.7f}–{b:.7f} meV',ha='center',fontsize=11)
ax.set(yticks=[0,1],yticklabels=['N=4','N=6'],ylim=(-.4,1.55),xlabel='D (meV)',title='C  Refined sign-change brackets · both engines')
ax.ticklabel_format(useOffset=False,axis='x');ax.grid(axis='x',alpha=.5)
ax.text(.02,.97,'Horizontal bars are retained brackets, not statistical error bars.',transform=ax.transAxes,va='top',fontsize=9)
ax=axs[1,1]
for N in P['N_values']:
    stations=[s for s in R[N]['stations'] if s['engine']=='bm']
    for gap,ls in [('lower','--'),('upper','-')]:
      ax.plot([s['D_meV'] for s in stations],[len(s['gaps'][gap]['roots']) for s in stations],ls,marker='o' if N==4 else 'x',ms=6,c=colors[N],label=f'N={N}, {gap}')
ax.set(xlabel='D (meV)',ylabel='Roots recovered in the searched chart',yticks=[0,1,2,3,4,5],ylim=(-.1,5.1),title='D  Search inventory · BM; reference counts checked')
ax.legend(frameon=False,ncol=2,fontsize=9,loc='upper left');ax.grid(alpha=.4)
ax.text(.02,.05,'A missing root is a search result.\nIt does not establish annihilation.',transform=ax.transAxes,fontsize=10,color='#94472a')
fig.get_layout_engine().set(rect=(0,.055,1,.96),h_pad=.16,w_pad=.15)
fig.text(.035,.02,'Declared finite continuum model • layer potentials ±D (difference 2D) • shared measurement framework • no experimental calibration or full braid claim',fontsize=10)
fig.savefig(ROOT/'events.png',dpi=170);fig.savefig(ROOT/'events.svg');plt.close(fig)

tables=[]
for N,c in summary['cutoffs'].items():
    a,b=c['crossing_brackets']['bm'];tables.append(f"| {N} | {c['stations']} | {c['grid_agreements']}/{c['grid_comparisons']} | {c['rejected_seed_attempts']}/{c['adjacent_seed_attempts']} | {a:.7f}–{b:.7f} |")
lost='; '.join(f"N={N}: "+', '.join(f"D={a:g}–{b:g}" for a,b in sorted({tuple(x['D_interval_meV']) for x in summary['unmatched_tracks'] if x['N']==N})) for N in P['N_values'])
text=f'''# R1 adjacent-node event interval

**The local upper-gap crossing is reproduced in both engines and both cutoffs, with refined D brackets below. Some upper-gap roots are subsequently not recovered; this is not an annihilation result.**

![Sampled trajectories, offsets, crossing brackets and recovered-root counts](events.png)

This follows the [endpoint validation](../r1_validation/README.md) and [R1 reproduction](../r1_reproduction/README.md). Their source and result files are unchanged. The same strained continuum model uses layer potentials ±D: D is an energy amplitude in meV, the layer-potential difference is 2D, and no experimental displacement-field calibration is supplied.

## Results

| Cutoff N | Engine/station rows | Coarse/fine inventory agreements | Rejected seed attempts / all adjacent attempts | Local crossing bracket D (meV) |
| --- | ---: | ---: | ---: | --- |
{chr(10).join(tables)}

Each cutoff has 13 stations from D=36 to 42 in steps of 0.5 meV, evaluated in both engines. Coarse/fine inventory comparisons cover both gaps at six stations per engine. The two grid inventories share continuation seeds; agreement is correlated evidence and does not prove a complete inventory. Rejected attempts can be multiple failed starts near the same root or a positive local minimum, so their count is not a count of missing roots. Every attempted refinement is retained.

Both engines return the same inventory counts at every compared station: {summary['engine_inventory_count_disagreements']} count disagreements. Their largest matched-root coordinate difference is {summary['max_engine_root_difference']:.3g} in the fractional chart. The engines share this solver and measurement framework, so agreement is internal numerical evidence.

The sampled records contain {len(summary['sampled_sign_changes'])} signed-offset reversals in total: the same upper branch once per engine/cutoff, between D=38 and 38.5. All four reversals have interior segment coordinates and no flagged assignment ambiguity. No other reversal is observed on the retained sampled tracks, and there are no recorded image changes. This does not exclude an event between samples or on a root missed by the searches.

Previously tracked roots become unmatched over {lost}. The tables in `SUMMARY.json` retain each affected track, gap and engine. No root absence, fold or annihilation is certified. Endpoint root counts and sampled tracks are finite-seed search outputs, not topological counts.

`SUMMARY.json` also lists every sampled signed-offset reversal, segment-interior test, ambiguous link and periodic-image change. A sign reversal is only compared within the same image lift. The targeted crossing refinement starts from the previously known D=38–39 bracket, bisects it seven times, and requires accepted flat/upper roots, interior segment coordinates and opposite retained endpoint offsets. Its bracket width is 0.0078125 meV. Differences between N=4 and N=6 remain cutoff dependence, not a statistical uncertainty estimate or demonstrated cutoff convergence.

## Search and identity rules

`PLAN.json` was frozen before these campaign runs, after the earlier endpoint and crossing results were known. This is a follow-up plan, not discovery preregistration. The search chart is [0,1]² in fractional momentum. Each station uses a 25×25 gap grid. D=36,38,39,40,41,42 also use 37×37 grids. Up to 12 local grid minima per gap seed bounded root searches, alongside continuation seeds and the two previously known upper roots at the first station. Grid arrays are preserved in `N4.npz` and `N6.npz`; each named array has axes f1, f2, gap (lower, upper), including both chart boundaries.

The solver recomputes the actual two-band eigenframe at every evaluation, aligns it to the seed frame using a polar decomposition, and solves its two real traceless Hamiltonian components. Acceptance requires successful optimization, residual gap below 1e-6 meV and minimum anchor overlap above 0.1. Searches remain within ±0.08 of their seeds and the chart. Roots are deduplicated within 1e-5; inventory matches use 1e-4. These are numerical gates, not root existence/uniqueness certificates.

Between adjacent D stations, global Euclidean assignment is thresholded at a 0.06 step. A row's alternative-neighbor distance margin below 0.002 is flagged as ambiguous; this is a heuristic, not a proof of unique assignment. New and unmatched tracks remain explicit. There is no periodic seam stitching. Geometry uses the same shortest-image flat-node segment as the earlier checkpoint; this coordinate choice does not assert exact finite-cutoff periodicity. Lines in the figure only connect sampled roots. No interpolation is used as evidence of continuous identity.

The affine real Hamiltonian evaluator is reused unchanged from the endpoint validation, with direct matrix and spectrum comparisons at every station. `test_tracking.py` checks permuted identities, a distant root that must remain unmatched, an ambiguous association, and a known actual-model root against the original complex Hamiltonian spectrum. Four controls pass; the log is preserved. Controls do not certify the entire research result.

## Reproduce and inspect

From the repository root, with NumPy, SciPy and Matplotlib installed:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_events/test_tracking.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_events/track.py --N 4 --output replay_N4.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_events/track.py --N 6 --output replay_N6.json
python research/benchmarks/r1_events/report.py
```

The runner refuses to overwrite an existing JSON or grid archive. A computation or flat-root failure stops that cutoff and retains the partial report. Adjacent-root search failures are warnings and remain visible. `report.py` reads the preserved N4/N6 files, not replay filenames, and refuses incomplete runs. JSON reports bind source/plan hashes and software versions; `MANIFEST.json` binds the completed files except itself. The figure uses BM trajectories to avoid drawing duplicate engine traces; numerical engine comparisons are in the summary. SVG and PNG are generated from the same preserved data.

## What remains open

The apparent loss of the nearby upper pair needs a dedicated local study with smaller D steps, bidirectional continuation and a controlled local gap minimum/root-count analysis. Completeness outside the searched seeds, continuous branch identity, other possible events between stations and full campaign acceptance remain unresolved. This does not establish a complete braid, Euler-obstruction removal, a second braid, novelty or an experimental prediction. The separate Vafek-paper convention discrepancy remains open.
'''
(ROOT/'README.md').write_text(text)
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.iterdir()) if p.is_file() and p.name!='MANIFEST.json'}
(ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['cutoffs','engine_comparisons']},indent=2))
