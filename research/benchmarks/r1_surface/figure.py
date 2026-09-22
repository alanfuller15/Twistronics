"""Scientific figures use only recorded geometry and reconciled bounds."""
import json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));from surface import point,sha
S=json.loads((ROOT/'SUMMARY.json').read_text());B=json.loads((ROOT/'BM.json').read_text());R=json.loads((ROOT/'REF.json').read_text())
assert S['all_surface_checks_pass']
assert all(sha(ROOT/n)==h for n,h in S['source_hashes'].items())
tracks=json.loads((ROOT.parent/'r1_holonomy'/'BM.json').read_text())['tracks']['16']['stations']
navy='#162b42';teal='#128b8b';blue='#3668b3';orange='#c67b33';paper='#f7f8fa';gray='#637285'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':navy,'axes.labelcolor':navy,'xtick.color':gray,'ytick.color':gray,'axes.edgecolor':'#c1cbd4','axes.titleweight':'bold','svg.fonttype':'none'})
fig=plt.figure(figsize=(14,10.4),facecolor=paper)
fig.text(.055,.963,'Checking the space between the contours',fontsize=25,weight='bold')
counts=S['totals'];fig.text(.056,.922,f"{counts['faces']:,} swept faces  ·  {counts['leaves']:,} accepted leaf cells  ·  {counts['unresolved_leaves']} unresolved  ·  two Hamiltonian implementations",fontsize=12,color=gray)
fig.text(.056,.892,'R1 / N = 8  |  fixed strain  |  layer potentials ±D  |  D = 38–39 meV',fontsize=10,color=gray)
case=next(c for c in B['cases'] if c['mesh']=='fine' and c['radius']==.003)
arr=np.load(ROOT/case['arrays_file']);patches=arr['corners']
p0,q0=[np.array(r['f']) for r in tracks[0]['roots'][:2]];direction=q0-p0;length=np.linalg.norm(direction);e=direction/length;n=np.array([-e[1],e[0]])
def coords(v):return np.array([(v[:2]-p0)@e/length,1000*(v[:2]-p0)@n,v[2]])
def style3(ax):
    ax.set_facecolor(paper)
    for axis in [ax.xaxis,ax.yaxis,ax.zaxis]:
        axis.pane.fill=False;axis._axinfo['grid']['color']=(.75,.80,.84,.35)
    ax.tick_params(labelsize=8,pad=0)
ax=fig.add_axes([.035,.46,.52,.385],projection='3d');style3(ax)
quads=[]
for c,meta in zip(patches,case['faces']):
    if meta['edge']>=2:continue
    for a,b in zip(np.linspace(0,1,13)[:-1],np.linspace(0,1,13)[1:]):
        quads.append([coords(point(c,u,t)) for u,t in [(a,0),(b,0),(b,1),(a,1)]])
ax.add_collection3d(Poly3DCollection(quads,facecolor=teal,edgecolor='#64aaaa',linewidth=.35,alpha=.60))
# Ring surface is included; node traces remain explicitly sampled guides.
ringquads=[[coords(v) for v in c.reshape(4,3)[[0,1,3,2]]] for c,meta in zip(patches,case['faces']) if meta['edge']>=2]
ax.add_collection3d(Poly3DCollection(ringquads,facecolor=blue,edgecolor='none',alpha=.5))
for s in tracks:
    upper=coords(np.r_[s['roots'][2]['f'],s['D_meV']]);ax.scatter(*upper,color=orange,s=14,depthshade=False)
upper=np.array([coords(np.r_[s['roots'][2]['f'],s['D_meV']]) for s in tracks]);ax.plot(*upper.T,color=orange,lw=1.4,ls='--')
for j in [0,16]:
    sub=patches[:130] if j==0 else patches[-130:];v=np.array([coords(c[0 if j==0 else 1,0]) for c in sub]+[coords(sub[-1][0 if j==0 else 1,1])]);ax.plot(*v.T,color=navy,lw=1.1)
ax.set_xlim(.53,1.025);ax.set_ylim(-11,4);ax.set_zlim(38,39)
ax.set_xticks([.55,.7,.85,1]);ax.set_yticks([-10,-5,0]);ax.set_zticks([38,38.5,39])
ax.set_xlabel('Along initial p–q segment',labelpad=5);ax.set_ylabel('Normal / 10⁻³',labelpad=5);ax.set_zlabel('D (meV)',labelpad=4)
ax.view_init(elev=24,azim=-62);ax.set_box_aspect((1.7,1,1.15),zoom=1.02)
fig.text(.056,.845,'A  The complete swept stem and circle',weight='bold',fontsize=12)
fig.text(.071,.417,'Teal: checked stem interior. Orange: sampled upper node; dashed guide.',fontsize=9,color=gray)
ax2=fig.add_axes([.592,.48,.345,.36],projection='3d');style3(ax2)
for rad,color in [(.003,blue),(.0015,teal)]:
    ca=next(c for c in B['cases'] if c['mesh']=='fine' and c['radius']==rad);cs=np.load(ROOT/ca['arrays_file'])['corners'];polys=[]
    for c,meta in zip(cs,ca['faces']):
        if meta['edge']<2:continue
        j=meta['interval'];qleft=np.array(tracks[j]['roots'][1]['f']);qright=np.array(tracks[j+1]['roots'][1]['f']);vs=[]
        for ii,jj in [(0,0),(0,1),(1,1),(1,0)]:
            vv=c[ii,jj];shift=vv[:2]-(qleft if ii==0 else qright);vs.append([1000*shift[0],1000*shift[1],vv[2]])
        polys.append(vs)
    ax2.add_collection3d(Poly3DCollection(polys,facecolor=color,edgecolor='none',alpha=.20))
    for si in [0,4,8,12,16]:
        ringcs=cs[si*130:(si+1)*130] if si<16 else cs[-130:];side=0 if si<16 else 1;q=np.array(tracks[si]['roots'][1]['f']);vv=np.array([c[side,0] for c in ringcs[2:]]+[ringcs[-1][side,1]]);xy=1000*(vv[:,:2]-q);ax2.plot(xy[:,0],xy[:,1],vv[:,2],color=color,lw=.6)
ax2.plot([0,0],[0,0],[38,39],ls='--',color=orange,lw=1);ax2.scatter(np.zeros(17),np.zeros(17),[s['D_meV'] for s in tracks],color=orange,s=11,depthshade=False)
ax2.set_xlim(-3.5,3.5);ax2.set_ylim(-3.5,3.5);ax2.set_zlim(38,39);ax2.set_xticks([-3,0,3]);ax2.set_yticks([-3,0,3]);ax2.set_zticks([38,38.5,39]);ax2.set_xlabel('Δf₁ / 10⁻³',labelpad=4);ax2.set_ylabel('Δf₂ / 10⁻³',labelpad=4);ax2.set_zlabel('D (meV)',labelpad=4);ax2.view_init(elev=22,azim=-56);ax2.set_box_aspect((1,1,1.3))
fig.text(.609,.845,'B  Two checked circle surfaces',weight='bold',fontsize=12)
fig.text(.605,.417,'Coordinates relative to interpolated q samples; node identity is open.',fontsize=9,color=gray)
ca=next(c for c in B['cases'] if c['mesh']=='fine' and c['radius']==.0015)
heat=np.array([[x['minimum_lower_meV'] for x in ca['faces'] if x['interval']==j and x['edge']>=2] for j in range(16)])
ax3=fig.add_axes([.075,.137,.405,.22]);im=ax3.imshow(heat,origin='lower',aspect='auto',extent=[0,128,38,39],norm=LogNorm(vmin=.001,vmax=max(.1,heat.max())),cmap='viridis',interpolation='nearest');ax3.set_xlabel('Circle polygon edge');ax3.set_ylabel('D interval (meV)');ax3.set_yticks([38,38.25,38.5,38.75,39]);ax3.set_xticks([0,32,64,96,128]);cb=fig.colorbar(im,cax=fig.add_axes([.494,.137,.012,.22]));cb.set_label('Gap lower estimate (meV)',fontsize=9);cb.ax.tick_params(labelsize=8)
fig.text(.075,.379,'C  Interior bounds, fine grid / r = 0.0015 / BM',weight='bold',fontsize=11)
ax4=fig.add_axes([.635,.137,.305,.22]);ax4.set_facecolor('white')
for mesh,ls in [('coarse','--'),('fine','-')]:
    for rad,color in [(.003,blue),(.0015,teal)]:
        for engine,d in [('BM',B),('REF',R)]:
            ca=next(c for c in d['cases'] if c['mesh']==mesh and c['radius']==rad);nn=8 if mesh=='coarse' else 16
            yy=[min(f['minimum_lower_meV'] for f in ca['faces'] if f['interval']==j) for j in range(nn)];xx=38+(np.arange(nn)+.5)/nn
            if engine=='BM':ax4.plot(xx,yy,ls=ls,color=color,lw=1.1,label=f'{mesh}, r={rad:g}')
            else:ax4.plot(xx,yy,ls='none',marker='x',markersize=3,color=color,alpha=.6)
ax4.axhline(.001,color=orange,lw=1,ls=':');ax4.set_yscale('log');ax4.set_xlabel('D (meV)');ax4.set_ylabel('Worst face lower estimate (meV)');ax4.set_xlim(38,39);ax4.grid(axis='y',alpha=.15);ax4.legend(fontsize=8,loc='upper right',frameon=False,ncol=2);fig.text(.635,.362,'REF crosses overlap BM; dotted line = 0.001 meV margin.',fontsize=8,color=gray)
fig.text(.635,.379,'D  Every stem and circle face passes',weight='bold',fontsize=11)
fig.text(.075,.071,'Result: the declared interpolated contour has a gapped continuous deformation, conditional on the numerical bounds.',fontsize=11,weight='bold')
fig.text(.075,.044,'Not interval arithmetic. Continuous node identity, full braid acceptance and Euler-class change remain unestablished.',fontsize=10,color=gray)
fig.savefig(ROOT/'surface_isolation.png',dpi=190,facecolor=fig.get_facecolor());fig.savefig(ROOT/'surface_isolation.svg',facecolor=fig.get_facecolor());plt.close(fig)
rows='\n'.join(f"| {c['engine'].upper()} | {c['mesh']} | {c['radius']:g} | {c['faces']:,} | {c['leaves']:,} | {c['minimum_lower_meV']:.9f} | {c['unresolved_leaves']} |" for c in S['cases'])
audit=S['root_identity_audit'];rootmin=min(a['minimum_sampled_jacobian_singular_value'] for a in audit);gapmax=max(a['maximum_residual_gap_meV'] for a in audit)
readme=f'''# R1: full swept-contour surface isolation

**Both Hamiltonian implementations pass every declared swept face on both meshes and at both radii.** The previous checkpoint checked grid edges; this one checks their intervening interiors with adaptive gap bounds. All {counts['faces']:,} faces are covered by {counts['leaves']:,} accepted leaf cells, with **{counts['unresolved_leaves']} unresolved leaves**. Seven new analytic controls pass, including degeneracies hidden inside gapped boundaries.

![Full swept-contour surfaces, interior bounds and refinement](surface_isolation.png)

## What this adds

The moving contour is now supported as a **gapped continuous deformation of the explicitly defined piecewise bilinear surface**, conditional on numerical operator norms and eigensolutions. It inherits the preceding fixed three-band chart and carried base-frame convention. The earlier transported **+k** result and endpoint conjugation are reused, not remeasured here.

This does **not** establish continuous node identity or a full braid. It is not an Euler-class computation, an interval-arithmetic proof, an infinite-cutoff result or an experimental calibration. Strain is fixed; D sets layer potentials ±D meV. The two Hamiltonian engines share the diagnostic framework.

## Numerical evidence

| Engine | Geometry | Radius | Faces | Leaf cells | Minimum gap lower estimate (meV) | Unresolved |
|---|---|---:|---:|---:|---:|---:|
{rows}

The acceptance margin was frozen at **0.001 meV**. The smallest lower estimate is **{S['minimum_lower_meV']:.9f} meV**. These conservative estimates are not measured minimum physical gaps; the smallest evaluated center gap is {S['minimum_center_gap_meV']:.6f} meV. The algorithm refines until the bound clears the fixed margin, so a lower estimate close to the margin is expected.

The report reconstructs all {counts['evaluations']:,} recorded cell evaluations, parent/child partitions, complete parameter-square coverage, interior bounds, parent chart containment and source bindings. It also checks selected spectra against the native Hamiltonian and compares the two affine engines at common coordinates. Maximum native spectrum discrepancy: {S['reconstruction_errors']['native_spectrum_meV']:.3g} meV. Full details are in [SUMMARY.json](SUMMARY.json).

## Node identity remains open

The earlier continuation contains {sum(a['sample_count'] for a in audit)} accepted root samples across the engines and two meshes; shared stations are counted repeatedly. Their largest residual gap is {gapmax:.3g} meV and smallest recorded numerical Jacobian singular value is {rootmin:.6g} meV per fractional-coordinate unit. These are **sampled diagnostics**, not uniform invertibility or uniqueness bounds between stations. Node traces in the figure are guides connecting samples.

The next substantive requirement is controlled continuation with overlapping uniqueness neighborhoods for the relevant nodes, alongside the inventory and isolation requirements for a full braid claim.

## Inspect and reproduce

- [Frozen plan](PLAN.json), [method, limits and commands](METHOD.md).
- [Surface bound implementation](surface.py), [sweep](sweep.py), [independent report](report.py), [figure source](figure.py).
- [Seven analytic controls](CONTROLS.json); complete engine records [BM.json](BM.json) and [REF.json](REF.json), with eight companion NPZ files containing every evaluated cell and full subdivision trees.
- [Root-identity audit and reconciliation](SUMMARY.json); [file hashes](MANIFEST.json).
- [Parent temporal checkpoint](../r1_temporal/README.md), unchanged.

The recorded result concerns R1 at N=8 and D=38–39 meV. It should not be conflated with the historical ratio/perturbation campaign. No parent code or results are changed.
'''
(ROOT/'README.md').write_text(readme)
print('Wrote surface_isolation.png, surface_isolation.svg and README.md from reconciled evidence.')
