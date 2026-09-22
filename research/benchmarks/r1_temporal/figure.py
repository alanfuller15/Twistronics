"""Generate a scientific figure and README from reconciled evidence."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parent
S=json.loads((ROOT/'SUMMARY.json').read_text());assert S['all_numerical_checks_pass']
data={n:json.loads((ROOT/(n.upper()+'.json')).read_text()) for n in ['bm','ref']}
prior=json.loads((ROOT.parent/'r1_holonomy'/'BM.json').read_text())['tracks']['16']['stations']
lookup={s['D_meV']:s for s in prior};cross=S['crossing_D_meV']['bm']
blue='#286bcc';orange='#d46a30';green='#14816d';navy='#19304e';gray='#66758a';red='#a5515d'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':navy,'axes.labelcolor':navy,'axes.edgecolor':'#becada','xtick.color':gray,'ytick.color':gray,'axes.spines.top':False,'axes.spines.right':False})
fig=plt.figure(figsize=(16,11),facecolor='#f7f9fc');gs=fig.add_gridspec(2,2,left=.065,right=.96,top=.80,bottom=.15,wspace=.28,hspace=.60,height_ratios=[1.05,.8])
space=fig.add_subplot(gs[0,0],projection='3d');sign=fig.add_subplot(gs[0,1]);tableax=fig.add_subplot(gs[1,0]);gap=fig.add_subplot(gs[1,1])
fig.text(.065,.953,'TWISTRONICS  /  R1  /  TEMPORAL GRID',fontsize=12,fontweight='bold',color=blue)
fig.text(.065,.9,'Carry the contour through the crossing',fontsize=27,fontweight='bold')
fig.text(.065,.856,'A carried charge stays fixed while the straight-path convention changes sign.',fontsize=14,color=gray)

def coords(vertices,D):
    p,q=[np.array(x['f']) for x in lookup[D]['roots'][:2]];d=q-p;L=np.linalg.norm(d);e=d/L;n=np.array([-e[1],e[0]])
    f=np.asarray(vertices)[:,:2]-p
    return np.c_[f@e/L,1000*(f@n),np.asarray(vertices)[:,2]]

fine=[r for r in data['bm']['stations'] if r['mesh']=='fine' and r['radius']==.003]
for row in fine:
    D=row['D_meV'];g=row['geometry'];v=np.array([g['base'],g['kink'],g['ring'][0]])
    vv=coords(v,D);ring=coords(g['ring'],D);end=D in [38.,39.]
    space.plot(*vv.T,color=blue,alpha=1 if end else .20,lw=2 if end else 1)
    space.plot(*ring.T,color=blue,alpha=.9 if end else .15,lw=1.3 if end else .6)
plane=[(.55,0,38),(.995,0,38),(.995,0,39),(.55,0,39)]
space.add_collection3d(Poly3DCollection([plane],facecolor='#9baec5',edgecolor='#b3c0d0',alpha=.13,linewidth=.7))
upper=np.array([[s['upper_geometry']['t'],1000*s['upper_geometry']['normal_offset'],s['D_meV']] for s in prior])
space.plot(*upper.T,color=orange,lw=3,label='Upper-node samples');space.scatter(*upper[::4].T,color=orange,s=20)
lo,hi=lookup[38.0625],lookup[38.125];fraction=(cross-38.0625)/.0625
pq=[(1-fraction)*np.array(a['f'])+fraction*np.array(b['f']) for a,b in zip(lo['roots'][:2],hi['roots'][:2])]
crossroot=np.array(data['bm']['crossing_control']['evaluations'][-1]['upper']['f']);delta=pq[1]-pq[0]
cross_t=float((crossroot-pq[0])@delta/(delta@delta))
space.scatter([cross_t],[0],[cross],marker='*',s=115,color=red,edgecolor='white',linewidth=.6,depthshade=False,zorder=8)
space.plot([1,1],[0,0],[38,39],color=blue,lw=2)
space.text(upper[-1,0],upper[-1,1],39.05,'Upper node',color=orange,fontsize=10)
space.text(1.0,0,39.05,'Flat q',color=blue,fontsize=10)
space.set_xlim(.53,1.03);space.set_ylim(-11.2,3.3);space.set_zlim(38,39.08)
space.set_xticks([.55,.75,1.]);space.set_yticks([-10,-5,0]);space.set_zticks([38,38.5,39])
space.set_xlabel('Position along p → q',labelpad=6);space.set_ylabel('Normal offset × 1,000',labelpad=7);space.set_zlabel('D (meV)',labelpad=5)
space.view_init(elev=21,azim=-62);space.set_box_aspect((1.45,1,1),zoom=1.18);space.tick_params(labelsize=9,pad=0)
fig.text(.065,.825,'A   A moving stem avoids the adjacent node',fontsize=14,fontweight='bold')
fig.text(.065,.803,'Blue: T at 17 stations. Gray: straight-stem plane. Star: rejected crossing.',fontsize=9,color=gray)

for radius,marker in [(.003,'o'),(.0015,'s')]:
    rows=[r for r in fine if r['radius']==radius] if radius==.003 else [r for r in data['bm']['stations'] if r['mesh']=='fine' and r['radius']==radius]
    q0=np.array(rows[0]['charge']['quaternion']);values=[float(np.dot(q0,r['charge']['quaternion'])) for r in rows]
    sign.plot([r['D_meV'] for r in rows],values,color=blue,lw=1.8 if radius==.003 else 0,marker=marker,ms=5 if radius==.003 else 7,mfc=blue if radius==.003 else 'none',label='Transported T' if radius==.003 else 'Half-radius T')
endpoints=[r for r in data['bm']['endpoint_comparisons'] if r['mesh']=='fine' and r['radius']==.003]
q0=np.array(fine[0]['charge']['quaternion']);ss=[float(q0@np.array(r['S']['quaternion'])) for r in endpoints]
sign.scatter([38,39],ss,color=orange,s=75,marker='D',label='Straight S, endpoints',zorder=6)
sign.axvline(cross,color=red,ls='--',lw=1.2)
sign.annotate('Straight stem crosses a node\nand must be rejected',xy=(cross,.1),xytext=(38.28,.05),arrowprops={'arrowstyle':'->','color':red},fontsize=10,color=red)
sign.axhline(0,color='#c1ccd9',lw=.7);sign.set_xlim(37.97,39.03);sign.set_ylim(-1.3,1.65)
sign.set_yticks([-1,0,1]);sign.set_xlabel('Model parameter D (meV)');sign.set_ylabel('Charge sign relative to T at D = 38')
sign.set_title('B   One carried base frame makes signs comparable',loc='left',fontsize=14,fontweight='bold',pad=17)
sign.text(0,1.02,'T: fine-grid samples. S: measured at the two endpoints only.',transform=sign.transAxes,fontsize=9,color=gray)
sign.legend(frameon=False,fontsize=9,loc='upper right');sign.grid(axis='y',alpha=.15)

tableax.axis('off');tableax.set_title('C   The endpoint difference is conjugation',loc='left',fontsize=14,fontweight='bold',pad=21)
tableax.text(0,1.015,'Every row includes both radii and both resolutions.',transform=tableax.transAxes,fontsize=9,color=gray)
rows=[]
for D in [38.,39.]:
    for engine in ['bm','ref']:
        checks=[c for c in data[engine]['endpoint_comparisons'] if c['D_meV']==D]
        st=[r for r in data[engine]['stations'] if r['D_meV']==D]
        sets=[{r['charge']['nearest_label'] for r in st},{r['S']['nearest_label'] for r in checks},{r['C']['nearest_label'] for r in checks}]
        assert all(len(x)==1 for x in sets)
        rows.append([f'{int(D)} / {engine.upper()}',*[next(iter(x)).replace('-','−') for x in sets],f'{sum(c["pass"] for c in checks)}/4'])
tab=tableax.table(cellText=rows,colLabels=['D / engine','T, carried','S, straight','C','Conjugation'],cellLoc='center',bbox=[0,.2,1,.75],colWidths=[.24,.20,.20,.13,.23]);tab.auto_set_font_size(False);tab.set_fontsize(11)
for (r,c),cell in tab.get_celld().items():
    cell.set_edgecolor('#dce4ef');cell.set_linewidth(.6);cell.set_facecolor('#e7eef8' if r==0 else ('white' if r%2 else '#f0f4fa'))
    if r==0:cell.set_text_props(weight='bold')
    if r>0 and c==1:cell.set_text_props(color=blue,weight='bold')
tableax.text(0,.04,'Directly measured:  q(T) = q(C) q(S) q(C)⁻¹',transform=tableax.transAxes,fontweight='bold',fontsize=12,color=green)
tableax.text(0,-.065,'Signed labels use the recorded, continuously carried base-frame convention.',transform=tableax.transAxes,fontsize=9,color=gray)
report_rows=rows.copy()

def spatial_min(row):return min(l['gap_lower_meV'] for key in ['stem','circle'] for e in row['paths'][key]['edges'] for l in e['leaves'])
for radius,color in [(.003,blue),(.0015,green)]:
    rows=[r for r in data['bm']['stations'] if r['mesh']=='fine' and r['radius']==radius]
    gap.plot([r['D_meV'] for r in rows],[spatial_min(r) for r in rows],color=color,lw=1.5,label=f'Spatial T, r = {radius}')
    ref=[r for r in data['ref']['stations'] if r['mesh']=='fine' and r['radius']==radius]
    gap.scatter([r['D_meV'] for r in ref],[spatial_min(r) for r in ref],color=orange,marker='x',s=20,label='Reference engine' if radius==.003 else None)
times=sorted({r['station'] for r in data['bm']['temporal_edges'] if r['mesh']=='fine'});vals=[]
for j in times:
    es=[r for r in data['bm']['temporal_edges'] if r['mesh']=='fine' and r['station']==j]
    vals.append(min(l['gap_lower_meV'] for e in es for l in e['edge']['leaves']))
gap.plot([38+(j-.5)/16 for j in times],vals,color=gray,ls='--',lw=1.2,label='Temporal-edge minimum')
gap.axhline(.001,color=red,ls=':',lw=1,label='Acceptance margin');gap.set_yscale('log');gap.set_xlabel('Model parameter D (meV)');gap.set_ylabel('Conditional gap lower estimate (meV)')
gap.set_title('D   Every recorded grid edge passes its gap gate',loc='left',fontsize=14,fontweight='bold',pad=21)
gap.text(0,1.015,'Fine-grid results; temporal minima are placed at interval midpoints.',transform=gap.transAxes,fontsize=9,color=gray)
gap.grid(axis='y',alpha=.18);gap.legend(frameon=False,fontsize=8.5,loc='center left',ncol=2,handlelength=1.7)

counts=S['counts'];fig.text(.065,.07,f'{counts["transported_station_loops"]} transported station loops  ·  {counts["temporal_edges"]:,} temporal edges  ·  {counts["endpoint_comparisons"]} endpoint conjugation checks',fontsize=11,fontweight='bold',color=green)
fig.text(.065,.04,'Edges are guarded; moving-contour face interiors and continuous root identity remain uncertified. No full braid or Euler-class claim.',fontsize=10,color=gray)
fig.text(.065,.018,'Finite N8 continuum model. Both engines share the diagnostic. Strain is fixed; D supplies layer potentials ±D meV.',fontsize=10,color=gray)
for ext in ['png','svg']:fig.savefig(ROOT/('temporal_transport.'+ext),dpi=180,facecolor=fig.get_facecolor())

mini=S['minimum_conditional_estimates'];err=max(S['reconstruction_errors'][n] for n in ['frame_lift','carried_frame','shared_base_frames','SU2_conjugation'])
table='\n'.join('| '+' | '.join(row)+' |' for row in report_rows)
readme=f'''# R1: sampled temporal transport and charge conjugation

**Both engines reproduce the predicted relation in the carried base-frame
convention.** The transported contour T retains +k throughout both sampled
D grids. The nominal straight-path charge is +k at D38 and −k at D39.
The comparison loop C changes from +1 to +i, and direct traversal of
C S C⁻¹ reproduces T. Both loop radii and both resolutions agree.

**This is a guarded temporal-grid result, not full braid acceptance.** The
intervening two-dimensional moving-contour faces and continuous root identity
are not certified. No Euler-class change is computed. The two Hamiltonian
implementations share the diagnostic and its assumptions.

![Moving contour, carried charge and numerical checks](temporal_transport.png)

## What the comparison means

T follows a stem that moves with a fixed offset below the sampled adjacent
node, goes around flat node q, and retraces that stem. S uses a straight
stem. Both use the same basepoint and the same local polygon at each station.
C traverses T's outgoing stem and returns along S's stem. All endpoint
charges use the base eigenframe carried from D38. The measured relation is

q(T) = q(C) q(S) q(C)⁻¹.

| D / engine | T, carried | S, straight | C | Conjugation cases |
|---|---|---|---|---|
{table}

Each row includes radii 0.003 and 0.0015 and both resolutions. Signed i/k
labels refer to the recorded base-frame convention. These symbols label
quaternion elements, not momentum coordinates.

The nominal straight stem crosses the upper node at
**D = {cross:.10f} meV**, using the fine-track interpolation specified in
the plan. Both engines locate this crossing, and the diagnostic rejects the
stem there. It therefore receives no accepted charge at that event. The
nominal endpoint sign change is not presented as continuously gapped
transport along the straight convention.

## Numerical checks

- {counts['transported_station_loops']} transported station loops pass across the two engines, two radii,
  and 9/17-station D grids. There are 17 unique original D stations per
  engine; coarse and fine runs repeat shared stations.
- {counts['temporal_edges']:,} temporal grid-edge checks pass, plus {counts['base_edges']} base-frame transport edges.
  Base and kink connections are repeated across the radius grids. These
  counts include reused samples and are not independent experiments.
- {counts['endpoint_comparisons']} endpoint conjugation comparisons pass. Each includes S, C and
  the explicitly concatenated C S C⁻¹ path.
- Ten new analytic control cases pass, including imposed eigenvector
  sign changes and required rejection of a degenerate transport edge.
  Eight core cases are supplemented by two explicit D-axis degeneracy
  rejection cases. Source bindings of eighteen parent analytic controls are verified;
  those eighteen control results are reused, not rerun here.
- Both adaptive box covers pass exterior-band isolation and reference-chart
  checks. The smallest conditional exterior-gap lower estimate is
  {mini['volume_exterior_gap_meV']:.8g} meV; the smallest chart singular-value lower estimate
  is {mini['volume_chart_smin']:.8g}, above the 0.6 gate.
- The smallest conditional spatial-path gap lower estimate is
  {mini['spatial_gap_meV']:.8g} meV. The corresponding temporal/base-edge minimum is
  {mini['temporal_gap_meV']:.8g} meV. Both exceed the 0.001 meV margin.
- Independent reconstruction checks saved bounds, coordinates, base-frame
  signs, quaternion-to-frame rotations, and SU(2) conjugation products.
  The largest dimensionless frame/conjugation matrix discrepancy is {err:.3g}. Small algebraic
  discrepancies are not physical error bars.

The volume checks concern the triple's exterior gaps and chart rank.
The grid-edge checks additionally cover both internal gaps. **Exterior
isolation over the volume does not certify the two internal gaps in the
unmeasured moving-contour face interiors.** All bounds are conditional on
floating-point eigensolutions and matrix norms, not interval arithmetic.

## Model and method

The R1 Hamiltonians are unchanged: θ = 1°, strain magnitude 0.007, strain
angle 15°, w₁ = 110 meV, w₀ = 88 meV, exact geometry, `lab_nn_full`, N8,
149 reciprocal vectors and dimension 596. Bands 297–299 use zero-based
energy ordering. Strain remains fixed. D supplies layer potentials ±D meV;
no calibration to laboratory displacement field is supplied.

The p, q and upper-node station coordinates come from
[r1_holonomy](../r1_holonomy/README.md). The unchanged lift and adaptive-edge
routines come from [r1_three_band](../r1_three_band/README.md), parent commit
`d32b6f728afabc4a80b71389f99e77f69548e723`. The new code supplies a single
three-dimensional chart, carried base frames, moving paths, temporal edges
and the crossing control. [METHOD.md](METHOD.md) derives the construction,
bounds and conventions and links the scientific basis.

[SURVEY.json](SURVEY.json) retains the preliminary geometry survey with an
initial-base reference. [PLAN.json](PLAN.json) was then frozen before the
temporal charge calculations and specifies the production reference at the
containing box center. Predictions remain separate from numerical validity.

## Evidence and reproduction

`BM/REF.json` retain every adaptive volume leaf, station contour, temporal
edge, base-transport check, endpoint comparison and crossing evaluation.
`BM/REF.npz` retain the fixed reference, carried base frames, sampled
coordinates, five-band eigenvalues, projected eigenframes, anchor overlaps
and quaternion paths. `SUMMARY.json` and the logs record reconciliation.
`MANIFEST.json` binds all delivered files except itself.

With NumPy, SciPy and Matplotlib installed, run these commands from this
folder in a working copy where recorded BM/REF JSON and NPZ files have first
been moved aside. The sweep refuses to overwrite those evidence files.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python controls.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python temporal_axis_controls.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python sweep.py --engine bm
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python sweep.py --engine ref
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python report.py
python figure.py
```

The figure uses saved results only. Panel A shows sampled paths in coordinates
relative to each station's p–q segment; the gray plane is a geometric guide.
Panel B shows T on the fine grid and S at the endpoints only. Panel D places
temporal minima at their interval midpoints. No data are generated for
unmeasured face interiors.

The remaining acceptance gap is control of the entire moving-contour
surface and continuous node identity, followed by connection to the full
braiding and Euler-class argument. This checkpoint establishes neither
novelty, an infinite-cutoff result, nor experimental feasibility.
'''
(ROOT/'README.md').write_text(readme)
print('Generated temporal_transport.png/svg and README.md from reconciled evidence.')
