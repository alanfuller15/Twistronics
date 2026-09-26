"""Derive SUMMARY.json and neighborhood-refine.png from a replayed NEIGHBORHOOD-REFINE-005 output (no eigensolves)."""
import json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
p=Path(sys.argv[1]);review=sys.argv[2] if len(sys.argv)>2 else 'PENDING'
rows=json.loads((p/'MAP.json').read_text())['samples'];batch=json.loads((p/'BATCH.json').read_text())
ALIAS={'a':('ab','a'),'b':('ab','b'),'c':('bc','b')}
def gap(r,k,side=1):l,al=ALIAS[k];return 1000*r['comparisons'][l]['metrics']['pair'][al+'_external_gaps_meV'][side]
def grid(f):return np.array([f(r) for r in rows]).reshape(9,9)  # [dy+4, dx+4]
off=np.array([r['offset'] for r in rows]).reshape(9,9,2);assert (off[...,0]==np.arange(-4,5)[None,:]).all() and (off[...,1]==np.arange(-4,5)[:,None]).all()
G={k:grid(lambda r,k=k:gap(r,k)) for k in 'abc'};s={'implementation_commit':batch['implementation_commit'],'independent_review':review,'points':81,'eigensolver_starts':batch['eigensolver_starts'],'offset_unit':'1/1048576 in fractional x and y; k = x G1 + y G2; origin = x 720143/1048576, y 94421/131072 (NEIGHBORHOOD-2D-004 coarse offset (+7/8,+1))','cutoffs':{},'comparisons':{}}
for k in 'abc':
 i=np.unravel_index(G[k].argmin(),G[k].shape);s['cutoffs'][k]={'minimum_sampled_upper_gap_microeV':float(G[k].min()),'minimum_offset_dx_dy':[int(i[1])-4,int(i[0])-4],'center_upper_gap_microeV':float(G[k][4,4]),'upper_gap_microeV_rows_dy_minus4_to_plus4':G[k].tolist(),'minimum_sampled_lower_gap_microeV':float(grid(lambda r,k=k:gap(r,k,0)).min())}
for link in ['ab','bc']:
 m=[r['comparisons'][link] for r in rows];pa=grid(lambda r:max(r['comparisons'][link]['metrics']['pair']['principal_angles_degrees']))
 s['comparisons'][link]={'max_pair_angle_deg':float(pa.max()),'max_pair_angle_offset_dx_dy':[int(np.unravel_index(pa.argmax(),pa.shape)[1])-4,int(np.unravel_index(pa.argmax(),pa.shape)[0])-4],'max_four_angle_deg':max(max(x['metrics']['four']['principal_angles_degrees']) for x in m),'min_pair_in_four':min(x['minimum_pair_weight_in_four'] for x in m),'max_abs_upper_gap_change_microeV':max(abs(x['metrics']['upper_gap_change_b_minus_a_microeV']) for x in m),'pair_angle_deg_rows':pa.tolist()}
D=abs(G['c']-G['b']);s['comparisons']['bc']['max_relative_upper_gap_change']=float((D/G['c']).max())
s['max_residual_meV']=max(max(r['eigenpair_residual_meV'].values()) for r in rows);s['max_nested_residual_meV']=max(max(r['nested_residual_meV'].values()) for r in rows)

def cone_fit(Z):
 """Least-squares fit gap^2 = Q(dx,dy) (general quadratic): the local two-band (cone) form. Descriptive only."""
 d=[(dx,dy) for dy in range(-4,5) for dx in range(-4,5)];X=np.array([[x*x,y*y,x*y,x,y,1] for x,y in d],float);Y=np.array([Z[y+4,x+4]**2 for x,y in d])
 c,*_=np.linalg.lstsq(X,Y,rcond=None);A=np.array([[2*c[0],c[2]],[c[2],2*c[1]]]);x0=np.linalg.solve(A,-c[3:5]);m=float(c[5]+0.5*c[3:5]@x0);w,U=np.linalg.eigh(A/2)
 return {'model':'gap^2 = quadratic in (dx,dy); least squares over all 81 samples','node_offset_fine_steps':x0.tolist(),'node_fractional_k_float':[(720143+x0[0])/1048576,(755368+x0[1])/1048576],'fitted_minimum_gap_squared_microeV2':m,'principal_slopes_microeV_per_step':np.sqrt(np.clip(w,0,None)).tolist(),'principal_directions_dx_dy':U.T.tolist(),'max_abs_gap_residual_microeV':float(np.abs(np.sqrt(np.abs(X@c))-np.sqrt(Y)).max()),'coefficients_xx_yy_xy_x_y_1':c.tolist()}
for k in 'bc':s['cutoffs'][k]['cone_fit']=cone_fit(G[k])
nb=np.array(s['cutoffs']['b']['cone_fit']['node_offset_fine_steps']);nc=np.array(s['cutoffs']['c']['cone_fit']['node_offset_fine_steps']);s['comparisons']['bc']['fitted_node_shift_fine_steps']=float(np.linalg.norm(nc-nb))
s['claim_ceiling']='Sampled finite-cutoff values on a 9x9 lattice plus a descriptive quadratic gap-squared fit; a fitted near-zero minimum is consistent with, but does not prove, a band touching. No certified crossing, global-minimum or infinite-cutoff claim.'
(p/'SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n')

# Figure. Sequential single-hue ramps (blue, then orange); categorical slots 1-3 for a/b/c.
INK='#0b0b0b';INK2='#52514e';CAT={'a':'#2a78d6','b':'#eb6834','c':'#1baf7a'}
blue=LinearSegmentedColormap.from_list('blue',['#cde2fb','#86b6ef','#3987e5','#1c5cab','#0d366b'])
orange=LinearSegmentedColormap.from_list('orange',['#fde3d6','#f5a47f','#eb6834','#b8461c','#7a2b0d'])
plt.rcParams.update({'font.size':11,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK2,'ytick.color':INK2,'axes.edgecolor':'#c9c8c3'})
fig,ax=plt.subplots(2,2,figsize=(13,11),layout='constrained');ext=(-4.5,4.5,-4.5,4.5);ticks=[-4,-2,0,2,4]
def heat(a,Z,cmap,title,unit,fmt,nodes=False):
 im=a.imshow(Z,origin='lower',extent=ext,cmap=cmap,vmin=0,interpolation='nearest');cb=fig.colorbar(im,ax=a,shrink=.85);cb.set_label(unit);cb.outline.set_visible(False)
 a.set(title=title,xticks=ticks,yticks=ticks,xlabel='x offset (1/1048576)',ylabel='y offset (1/1048576)')
 i=np.unravel_index(Z.argmin() if cmap is blue else Z.argmax(),Z.shape);a.plot(i[1]-4,i[0]-4,'o',ms=14,mfc='none',mec='white',mew=2.5);a.plot(i[1]-4,i[0]-4,'o',ms=14,mfc='none',mec=INK,mew=1)
 a.annotate(fmt.format(Z[i]),(i[1]-4,i[0]-4),xytext=(14,-22) if nodes else ((12,12) if i[1]-4<2 else (-12,12)),ha='left' if i[1]-4<2 else 'right',textcoords='offset points',color=INK,fontsize=11,fontweight='bold',bbox=dict(boxstyle='round,pad=.2',fc='white',ec='none',alpha=.85))
 for kk,mk in [('b','x'),('c','+')] if nodes else []:
  n=s['cutoffs'][kk]['cone_fit']['node_offset_fine_steps'];a.plot(*n,mk,color='white',ms=11,mew=3.5);a.plot(*n,mk,color=INK,ms=10,mew=1.5)
heat(ax[0,0],G['c'],blue,'Upper gap, model c (444×444); fitted nodes: × b, + c','µeV','{:.3f} µeV (sampled min)',nodes=True)
a=ax[0,1];x=np.arange(-4,5);xf=np.linspace(-4,4,400)
for k,dim in zip('bc',[308,444]):
 f=s['cutoffs'][k]['cone_fit']['coefficients_xx_yy_xy_x_y_1'];a.plot(xf,np.sqrt(np.clip(f[0]*xf**2+f[3]*xf+f[5],0,None)),'-',color=CAT[k],lw=1.2,alpha=.7);a.plot(x,G[k][4],'o',color=CAT[k],ms=8,mec='white',mew=1.5,label=f'{k}: {dim}×{dim} samples')
a.plot([],[],'-',color=INK2,lw=1.2,label='quadratic gap² fit (all 81 points)')
a.set(title='Cut through the grid center (y offset 0)',xlabel='x offset (1/1048576)',ylabel='Upper gap (µeV)',xticks=ticks,ylim=(0,None));a.legend(frameon=False);a.grid(alpha=.25)
heat(ax[1,0],D,orange,'Change in upper gap from b to c','|Δ gap| (µeV)','max {:.4f} µeV')
heat(ax[1,1],np.array(s['comparisons']['bc']['pair_angle_deg_rows']),orange,'How much the selected pair rotates, b → c','largest principal angle (°)','max {:.3f}°')
fig.suptitle('Eight times finer: the gap valley fits a cone whose fitted minimum is ≈ 0',fontsize=17,fontweight='bold')
fig.supxlabel(f'81 computed momentum samples × 3 nested cutoffs; squares are samples, not interpolation. Momentum space, not time.\nOrigin = 2D-004 offset (+7/8, +1). The fit is descriptive, not a certificate of a crossing. Independent review: {review}.',fontsize=10,color=INK2)
fig.savefig(p/'neighborhood-refine.png',dpi=150,facecolor='#fcfcfb');plt.close(fig)
print(json.dumps({k:v['minimum_sampled_upper_gap_microeV'] for k,v in s['cutoffs'].items()}))
