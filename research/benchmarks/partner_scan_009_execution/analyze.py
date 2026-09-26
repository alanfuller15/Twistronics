"""Derive SUMMARY.json and a figure from a replayed grid packet (engine PARTNER-SCAN-007); no eigensolves.

The packet id is read from this directory's name; grid geometry comes from the packet's frozen SPEC."""
import json,sys
from fractions import Fraction
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PKT=HERE.name.replace('_execution','')
p=Path(sys.argv[1]);review=sys.argv[2] if len(sys.argv)>2 else 'PENDING'
spec=json.loads((ROOT/f'research/benchmarks/{PKT}/SPEC.json').read_text())
rows=json.loads((p/'MAP.json').read_text())['samples'];batch=json.loads((p/'BATCH.json').read_text());P=json.loads((p/'PLAQUETTES.json').read_text());nx,ny=P['nx'],P['ny']
ALIAS={'a':('ab','a'),'b':('ab','b'),'c':('bc','b')}
def gap(r,k):l,al=ALIAS[k];return 1000*r['comparisons'][l]['metrics']['pair'][al+'_external_gaps_meV'][1]
G={k:np.array([gap(r,k) for r in rows]).reshape(ny,nx) for k in 'abc'}
X=np.array([float(Fraction(r['center'][0])) for r in rows]).reshape(ny,nx);Y=np.array([float(Fraction(r['center'][1])) for r in rows]).reshape(ny,nx)
V={k:[] for k in 'abc'}
for f in sorted(p.glob('job*/STATES.npz')):
 d=np.load(f)
 for k in 'abc':V[k]+=list(d[k+'_vectors'])
def box(i0,j0,i1,j1):return [j0*nx+i for i in range(i0,i1)]+[j*nx+i1 for j in range(j0,j1)]+[j1*nx+i for i in range(i1,i0,-1)]+[j*nx+i0 for j in range(j1,j0,-1)]
def hol(k,loop,cols):
 M=np.eye(len(cols));m=1.0
 for a,b in zip(loop,loop[1:]+loop[:1]):O=V[k][a][:,cols].T@V[k][b][:,cols];M=M@O;m=min(m,float(np.linalg.svd(O,compute_uv=False).min()))
 d=float(np.linalg.det(M));return {'determinant':d,'min_step_singular_value':m,'sign':(1 if d>0 else -1) if m>=P['min_step_overlap_required'] else None}
def cone_fit(Z,i,j,R):
 pts=[(dx,dy) for dy in range(-R,R+1) for dx in range(-R,R+1) if 0<=i+dx<nx and 0<=j+dy<ny];A_=np.array([[x*x,y*y,x*y,x,y,1] for x,y in pts],float);b=np.array([Z[j+y,i+x]**2 for x,y in pts])
 c,*_=np.linalg.lstsq(A_,b,rcond=None);A=np.array([[2*c[0],c[2]],[c[2],2*c[1]]]);x0=np.linalg.solve(A,-c[3:5])
 h=float(Fraction(rows[1]['center'][0])-Fraction(rows[0]['center'][0]))
 return {'window_half_width_steps':R,'points':len(pts),'node_offset_steps_from_min':x0.tolist(),'node_fractional_k_float':[X[j,i]+x0[0]*h,Y[j,i]+x0[1]*h],'fitted_minimum_gap_squared_microeV2':float(c[5]+.5*c[3:5]@x0),'max_abs_gap_residual_microeV':float(np.abs(np.sqrt(np.abs(A_@c))-np.sqrt(b)).max()),'principal_slopes_microeV_per_step':np.sqrt(np.clip(np.linalg.eigvalsh(A/2),0,None)).tolist()}
s={'packet':PKT,'implementation_commit':batch['implementation_commit'],'independent_review':review,'points':len(rows),'eigensolver_starts':batch['eigensolver_starts'],'grid':spec['grid'],'cutoffs':{},'boundary_loop':{}}
R=1 if nx>12 else 4
for k in 'abc':
 j,i=np.unravel_index(G[k].argmin(),G[k].shape)
 s['cutoffs'][k]={'minimum_sampled_upper_gap_microeV':float(G[k].min()),'minimum_at_fractional_k':[spec['points'][j*nx+i][0],spec['points'][j*nx+i][1]],'plaquettes_hi':{'minus_one':P['cutoffs'][k]['hi']['minus_one'],'invalid':P['cutoffs'][k]['hi']['invalid'],'valid_plus_one':sum(1 for c in P['cutoffs'][k]['hi']['plaquettes'] if c['sign']==1)},'cone_fit':cone_fit(G[k],int(i),int(j),R if R==4 else 1)}
 s['boundary_loop'][k]={'hi':hol(k,box(0,0,nx-1,ny-1),[2]),'selected_pair':hol(k,box(0,0,nx-1,ny-1),[1,2])}
s['max_residual_meV']=max(max(r['eigenpair_residual_meV'].values()) for r in rows);s['max_nested_residual_meV']=max(max(r['nested_residual_meV'].values()) for r in rows)
s['claim_ceiling']='Floating-point finite-cutoff grid; the cone fit is descriptive. Holonomy signs give node-count parities only where every step overlap is resolved.'
(p/'SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n')
INK='#0b0b0b';INK2='#52514e';blue=LinearSegmentedColormap.from_list('blue',['#cde2fb','#86b6ef','#3987e5','#1c5cab','#0d366b'])
plt.rcParams.update({'font.size':11,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK2,'ytick.color':INK2,'axes.edgecolor':'#c9c8c3'})
fig,a=plt.subplots(figsize=(10,8) if nx<12 else (11,9),layout='constrained');h=X[0,1]-X[0,0]
im=a.imshow(G['c'],origin='lower',extent=(X[0,0]-h/2,X[0,-1]+h/2,Y[0,0]-h/2,Y[-1,0]+h/2),cmap=blue,vmin=0,interpolation='nearest',aspect='equal');cb=fig.colorbar(im,ax=a,shrink=.85);cb.set_label('c upper gap (µeV)');cb.outline.set_visible(False)
for i,j in P['cutoffs']['c']['hi']['invalid']:a.add_patch(plt.Rectangle((X[0,i],Y[j,0]),h,h,fill=False,ec='#52514e',lw=1.5,ls='--'))
nf=s['cutoffs']['c']['cone_fit']['node_fractional_k_float'];a.plot(*nf,'+',color='white',ms=18,mew=4.5);a.plot(*nf,'+',color='#eb6834',ms=16,mew=2.2,label='cone-fit node estimate (c)')
a.plot([],[],'s',mfc='none',mec='#52514e',ls='none',ms=12,label='grid square too coarse to resolve the sign')
bl=s['boundary_loop']['c']['hi'];a.plot([X[0,0],X[0,-1],X[0,-1],X[0,0],X[0,0]],[Y[0,0],Y[0,0],Y[-1,0],Y[-1,0],Y[0,0]],'-',color='#eb6834' if bl['sign']==-1 else '#1964ad',lw=2.5,label=f"grid boundary loop, band hi: sign {bl['sign']:+d}")
a.legend(frameon=True,facecolor='white',edgecolor='none',loc='upper right',fontsize=9.5);a.ticklabel_format(useOffset=False)
a.set(xlabel='x (fractional, k = x G₁ + y G₂)',ylabel='y (fractional)',title=f"{spec['id']}: upper gap, model c, step {spec['grid']['step']}")
fig.supxlabel(f"{len(rows)} computed momentum points × 3 nested cutoffs; squares are samples. Momentum space, not time. Independent review: {review}.",fontsize=9.5,color=INK2)
fig.savefig(p/f"{PKT.replace('_','-')}.png",dpi=140,facecolor='#fcfcfb');plt.close(fig)
print(json.dumps({k:[v['minimum_sampled_upper_gap_microeV'],v['cone_fit']['node_fractional_k_float'],s['boundary_loop'][k]['hi']['sign']] for k,v in s['cutoffs'].items()}))
