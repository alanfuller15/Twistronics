"""Derive SUMMARY.json and partner-scan.png from a replayed PARTNER-SCAN-007 output (no eigensolves).

Box-boundary holonomies are recomputed here from the retained vectors (pure linear algebra)."""
import json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
p=Path(sys.argv[1]);review=sys.argv[2] if len(sys.argv)>2 else 'PENDING'
rows=json.loads((p/'MAP.json').read_text())['samples'];batch=json.loads((p/'BATCH.json').read_text());P=json.loads((p/'PLAQUETTES.json').read_text());nx,ny=P['nx'],P['ny'];I0,J0=1390,1468
ALIAS={'a':('ab','a'),'b':('ab','b'),'c':('bc','b')}
def gap(r,k):l,al=ALIAS[k];return 1000*r['comparisons'][l]['metrics']['pair'][al+'_external_gaps_meV'][1]
G={k:np.array([gap(r,k) for r in rows]).reshape(ny,nx) for k in 'abc'}
jobs=sorted(p.glob('job*/STATES.npz'));V={k:[] for k in 'abc'}
for f in jobs:
 d=np.load(f)
 for k in 'abc':V[k]+=list(d[k+'_vectors'])
def box(i0,j0,i1,j1):return [j0*nx+i for i in range(i0,i1)]+[j*nx+i1 for j in range(j0,j1)]+[j1*nx+i for i in range(i1,i0,-1)]+[j*nx+i0 for j in range(j1,j0,-1)]
def hol(k,loop,cols):
 M=np.eye(len(cols));m=1.0
 for a,b in zip(loop,loop[1:]+loop[:1]):O=V[k][a][:,cols].T@V[k][b][:,cols];M=M@O;m=min(m,float(np.linalg.svd(O,compute_uv=False).min()))
 return {'determinant':float(np.linalg.det(M)),'min_step_singular_value':m,'sign':(1 if np.linalg.det(M)>0 else -1) if m>=P['min_step_overlap_required'] else None}
BOXES={'whole_grid':(0,0,nx-1,ny-1),'inner_14x8':(10,3,24,11),'inner_5x3_around_node':(14,6,19,9),'left_part_excluding_node':(0,0,12,ny-1),'right_part_excluding_node':(20,0,nx-1,ny-1)}
s={'implementation_commit':batch['implementation_commit'],'independent_review':review,'points':len(rows),'eigensolver_starts':batch['eigensolver_starts'],'grid':{'nx':nx,'ny':ny,'step':'1/2048','x_numerator_range':[I0,I0+nx-1],'y_numerator_range':[J0,J0+ny-1]},'cutoffs':{},'boxes':{}}
for k in 'abc':
 i=np.unravel_index(G[k].argmin(),G[k].shape)
 s['cutoffs'][k]={'minimum_sampled_upper_gap_microeV':float(G[k].min()),'minimum_at_numerators_over_2048':[I0+int(i[1]),J0+int(i[0])],'plaquettes':{g:{'minus_one':P['cutoffs'][k][g]['minus_one'],'invalid':P['cutoffs'][k][g]['invalid'],'valid_plus_one':sum(1 for c in P['cutoffs'][k][g]['plaquettes'] if c['sign']==1)} for g in P['cutoffs'][k]}}
for name,b in BOXES.items():s['boxes'][name]={'plaquette_box_i0_j0_i1_j1':list(b),'cutoffs':{k:{'hi':hol(k,box(*b),[2]),'selected_pair':hol(k,box(*b),[1,2])} for k in 'abc'}}
s['max_residual_meV']=max(max(r['eigenpair_residual_meV'].values()) for r in rows);s['max_nested_residual_meV']=max(max(r['nested_residual_meV'].values()) for r in rows)
s['claim_ceiling']='Floating-point finite-cutoff grid. Plaquette signs count hi/hi+1 (and lo/hi) nodes mod 2 only where every edge overlap is resolved; unresolved plaquettes are reported, not interpreted.'
(p/'SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n')

INK='#0b0b0b';INK2='#52514e'
plt.rcParams.update({'font.size':11,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK2,'ytick.color':INK2,'axes.edgecolor':'#c9c8c3'})
blue=LinearSegmentedColormap.from_list('blue',['#cde2fb','#86b6ef','#3987e5','#1c5cab','#0d366b'])
fig,ax=plt.subplots(2,1,figsize=(14,10),layout='constrained')
ext=((I0-.5)/2048,(I0+nx-.5)/2048,(J0-.5)/2048,(J0+ny-.5)/2048)
a=ax[0];im=a.imshow(G['c']/1000,origin='lower',extent=ext,cmap=blue,vmin=0,interpolation='nearest',aspect='auto');cb=fig.colorbar(im,ax=a,shrink=.9);cb.set_label('c upper gap (meV)');cb.outline.set_visible(False)
node=(0.6867821353,0.7203754149);a.plot(*node,'+',color='white',ms=16,mew=4);a.plot(*node,'+',color='#1baf7a',ms=14,mew=2,label='known node (NODE-WINDING-006, c)')
a.set(title='Upper gap over the unresolved cluster, model c (444×444): one valley, one minimum',xlabel='x (fractional, k = x G₁ + y G₂)',ylabel='y (fractional)');a.legend(frameon=False,loc='upper left',labelcolor='white')
a=ax[1];S=np.zeros((ny-1,nx-1))
for c in P['cutoffs']['c']['hi']['plaquettes']:S[c['j'],c['i']]={1:0,-1:1,None:2}[c['sign']]
cm=LinearSegmentedColormap.from_list('sgn',['#e7e6e1','#eb6834','#52514e'],N=3)
a.imshow(S,origin='lower',extent=((I0)/2048,(I0+nx-1)/2048,J0/2048,(J0+ny-1)/2048),cmap=cm,vmin=0,vmax=2,interpolation='nearest',aspect='auto')
for name,(i0,j0,i1,j1) in BOXES.items():
 if name in ('whole_grid','inner_5x3_around_node'):
  sg=s['boxes'][name]['cutoffs']['c']['hi']['sign'];xs=np.array([i0,i1,i1,i0,i0])+I0;ys=np.array([j0,j0,j1,j1,j0])+J0;a.plot(xs/2048,ys/2048,'-',color='#eb6834' if sg==-1 else '#1964ad',lw=2.5)
  inner=name!='whole_grid';a.annotate(f"{'inner' if inner else 'whole-grid'} boundary loop: {sg:+d}",((i0+I0)/2048,((j1 if inner else j0)+J0)/2048),xytext=(4,4 if inner else 8),textcoords='offset points',color=INK,fontsize=10,fontweight='bold')
a.plot(*node,'+',color='#1baf7a',ms=14,mew=2)
a.set(title='Band-hi loop sign on every grid square (light: +1, dark: step too coarse to resolve) and on two boundary loops',xlabel='x (fractional)',ylabel='y (fractional)')
fig.suptitle('Partner search, stage 1: the box contains an odd number of nodes, so the partner lies outside it',fontsize=15,fontweight='bold')
fig.supxlabel(f'495 computed momentum points (step 1/2048) × 3 nested cutoffs; maps for a and b are nearly identical at this scale. Momentum space, not time. Independent review: {review}.',fontsize=10,color=INK2)
fig.savefig(p/'partner-scan.png',dpi=140,facecolor='#fcfcfb');plt.close(fig)
print(json.dumps({k:s['boxes'][k]['cutoffs']['c']['hi']['sign'] for k in BOXES}))
