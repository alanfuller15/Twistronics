"""Teaching figure from retained samples, with no additional physical solves."""
import json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(sys.argv[1]);rows=json.loads((root/'MAP.json').read_text())['samples'];x=np.arange(-8,9)
plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(3,1,figsize=(10,13),layout='constrained',gridspec_kw={'height_ratios':[1,1,1.45]})
fig.suptitle('The group stays similar. Its members mix.\n17 momentum positions through a sensitive region',fontsize=22,fontweight='bold')
for k,label,color in [('a','Smaller model','#1765ad'),('b','Larger model','#c9550c')]:
 axes[0].plot(x,[1000*r['metrics']['pair'][k+'_external_gaps_meV'][1] for r in rows],'-o',color=color,label=label)
axes[0].set(title='1. A small energy separation changes with position',ylabel='Upper pair gap (μeV)');axes[0].legend();axes[0].grid(alpha=.2)
for g,label,color in [('pair','Selected two-state pair','#a82165'),('four','Broader four-state group','#007d78')]:
 axes[1].plot(x,[max(r['metrics'][g]['principal_angles_degrees']) for r in rows],'-o',color=color,label=label)
axes[1].set(title='2. The pair changes much more than the group',ylabel='Largest subspace angle (degrees)',ylim=(0,90));axes[1].legend();axes[1].grid(alpha=.2)
for ax in axes[:2]:
 ax.set_xlabel('Momentum offset (steps of 1/131072 in x; k = xG₁ + yG₂)');ax.set_xticks([-8,-4,0,4,8]);ax.axvline(0,color='#777',ls=':',lw=1)
r=max(rows,key=lambda r:max(r['metrics']['pair']['principal_angles_degrees']));z=np.array(r['squared_overlaps'])*100
im=axes[2].imshow(z,cmap='Blues',vmin=0,vmax=100,aspect='equal')
for i in range(4):
 for j in range(4):axes[2].text(j,i,f'{z[i,j]:.1f}%',ha='center',va='center',fontsize=14,color='white' if z[i,j]>55 else '#102b43')
labels=['Below pair','Pair: lower','Pair: upper','Above pair'];axes[2].set_xticks(range(4),labels,rotation=15);axes[2].set_yticks(range(4),labels);axes[2].set(xlabel='Larger-model states',ylabel='Smaller-model states',title=f'3. Where states overlap most strongly (offset {r["index"]-8:+d})')
fig.colorbar(im,ax=axes[2],label='Squared overlap (%)',shrink=.8)
fig.supxlabel('Momentum scan, not motion in time. Lines connect computed samples.\nThe heatmap shows basis-dependent individual overlaps; group angles describe whole subspaces.\nFinite models • post-execution review pending',fontsize=11)
fig.savefig(root/'teaching-map.png',dpi=160);fig.savefig(root/'teaching-map.pdf');plt.close(fig)
summary={'points':17,'worst_pair_index':r['index'],'largest_pair_angle_degrees':max(max(t['metrics']['pair']['principal_angles_degrees']) for t in rows),'largest_four_angle_degrees':max(max(t['metrics']['four']['principal_angles_degrees']) for t in rows),'minimum_a_pair_weight_in_b_four':min(t['minimum_a_pair_weight_in_b_four'] for t in rows),'gap_ranges_microeV':{k:[f(1000*t['metrics']['pair'][k+'_external_gaps_meV'][1] for t in rows) for f in [min,max]] for k in ['a','b']},'independent_review':'PENDING'}
(root/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
