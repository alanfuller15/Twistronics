"""Derive SUMMARY.json and neighborhood-2d.png from a replayed NEIGHBORHOOD-2D-004 output (no eigensolves)."""
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
G={k:grid(lambda r,k=k:gap(r,k)) for k in 'abc'};s={'implementation_commit':batch['implementation_commit'],'independent_review':review,'points':81,'eigensolver_starts':batch['eigensolver_starts'],'offset_unit':'1/131072 in fractional x and y; k = x G1 + y G2; origin = CUTOFF-LADDER-003 point 13','cutoffs':{},'comparisons':{}}
for k in 'abc':
 i=np.unravel_index(G[k].argmin(),G[k].shape);s['cutoffs'][k]={'minimum_sampled_upper_gap_microeV':float(G[k].min()),'minimum_offset_dx_dy':[int(i[1])-4,int(i[0])-4],'center_upper_gap_microeV':float(G[k][4,4]),'upper_gap_microeV_rows_dy_minus4_to_plus4':G[k].tolist(),'minimum_sampled_lower_gap_microeV':float(grid(lambda r,k=k:gap(r,k,0)).min())}
for link in ['ab','bc']:
 m=[r['comparisons'][link] for r in rows];pa=grid(lambda r:max(r['comparisons'][link]['metrics']['pair']['principal_angles_degrees']))
 s['comparisons'][link]={'max_pair_angle_deg':float(pa.max()),'max_pair_angle_offset_dx_dy':[int(np.unravel_index(pa.argmax(),pa.shape)[1])-4,int(np.unravel_index(pa.argmax(),pa.shape)[0])-4],'max_four_angle_deg':max(max(x['metrics']['four']['principal_angles_degrees']) for x in m),'min_pair_in_four':min(x['minimum_pair_weight_in_four'] for x in m),'max_abs_upper_gap_change_microeV':max(abs(x['metrics']['upper_gap_change_b_minus_a_microeV']) for x in m),'pair_angle_deg_rows':pa.tolist()}
D=abs(G['c']-G['b']);s['comparisons']['bc']['max_relative_upper_gap_change']=float((D/G['c']).max())
s['max_residual_meV']=max(max(r['eigenpair_residual_meV'].values()) for r in rows);s['max_nested_residual_meV']=max(max(r['nested_residual_meV'].values()) for r in rows)
s['claim_ceiling']='Sampled finite-cutoff values on a 9x9 lattice; no closure, crossing, global-minimum, off-grid or infinite-cutoff claim.'
(p/'SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n')

# Figure. Sequential single-hue ramps (blue, then orange); categorical slots 1-3 for a/b/c.
INK='#0b0b0b';INK2='#52514e';CAT={'a':'#2a78d6','b':'#eb6834','c':'#1baf7a'}
blue=LinearSegmentedColormap.from_list('blue',['#cde2fb','#86b6ef','#3987e5','#1c5cab','#0d366b'])
orange=LinearSegmentedColormap.from_list('orange',['#fde3d6','#f5a47f','#eb6834','#b8461c','#7a2b0d'])
plt.rcParams.update({'font.size':11,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK2,'ytick.color':INK2,'axes.edgecolor':'#c9c8c3'})
fig,ax=plt.subplots(2,2,figsize=(13,11),layout='constrained');ext=(-4.5,4.5,-4.5,4.5);ticks=[-4,-2,0,2,4]
def heat(a,Z,cmap,title,unit,fmt):
 im=a.imshow(Z,origin='lower',extent=ext,cmap=cmap,vmin=0,interpolation='nearest');cb=fig.colorbar(im,ax=a,shrink=.85);cb.set_label(unit);cb.outline.set_visible(False)
 a.set(title=title,xticks=ticks,yticks=ticks,xlabel='x offset (1/131072)',ylabel='y offset (1/131072)')
 i=np.unravel_index(Z.argmin() if cmap is blue else Z.argmax(),Z.shape);a.plot(i[1]-4,i[0]-4,'o',ms=14,mfc='none',mec='white',mew=2.5);a.plot(i[1]-4,i[0]-4,'o',ms=14,mfc='none',mec=INK,mew=1)
 a.annotate(fmt.format(Z[i]),(i[1]-4,i[0]-4),xytext=(12,12) if i[1]-4<2 else (-12,12),ha='left' if i[1]-4<2 else 'right',textcoords='offset points',color=INK,fontsize=11,fontweight='bold',bbox=dict(boxstyle='round,pad=.2',fc='white',ec='none',alpha=.85))
 a.axhline(0,color='white',lw=1,ls=(0,(3,3)))
heat(ax[0,0],G['c'],blue,'Upper gap, largest model c (444×444)','µeV','{:.3f} µeV (sampled min)')
ax[0,0].text(-4.3,0.15,'pilot line (1-D scan)',color='white',fontsize=9,va='bottom')
a=ax[0,1];x=np.arange(-4,5)
for k,dim in zip('abc',[196,308,444]):a.plot(x,G[k][5],'-o',color=CAT[k],lw=2,ms=8,mec='white',mew=1.5,label=f'{k}: {dim}×{dim}')
a.set(title='Cut through the minimum (y offset +1)',xlabel='x offset (1/131072)',ylabel='Upper gap (µeV)',xticks=ticks,ylim=(0,None));a.legend(frameon=False);a.grid(alpha=.25)
a.annotate('b and c overlap here',(1,G['c'][5,5]),xytext=(2.1,0.6),color=INK2,fontsize=10,arrowprops=dict(arrowstyle='-',color=INK2,lw=.8))
heat(ax[1,0],D,orange,'Change in upper gap from b to c','|Δ gap| (µeV)','max {:.4f} µeV')
heat(ax[1,1],np.array(s['comparisons']['bc']['pair_angle_deg_rows']),orange,'How much the selected pair rotates, b → c','largest principal angle (°)','max {:.3f}°')
fig.suptitle('Two-dimensional neighborhood around the shared b/c gap minimum',fontsize=17,fontweight='bold')
fig.supxlabel(f'81 computed momentum samples × 3 nested cutoffs (squares are samples, not interpolation). Momentum space, not time. Origin = pilot point +5. Independent review: {review}.',fontsize=10,color=INK2)
fig.savefig(p/'neighborhood-2d.png',dpi=150,facecolor='#fcfcfb');plt.close(fig)
print(json.dumps({k:v['minimum_sampled_upper_gap_microeV'] for k,v in s['cutoffs'].items()}))
