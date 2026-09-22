"""Render the actual retained comparison rows, with source hash binding."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'PROBES.json').read_text());rows=r['rows']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,2,figsize=(13,6.3),gridspec_kw={'wspace':.25})
fig.patch.set_facecolor('#f6f8fb')
fig.text(.07,.935,'The native valley wrapper works. The fast engine misses it.',fontsize=19,weight='bold',color='#17263b')
fig.text(.07,.885,'18 comparisons · BM model · N = 3, 4, 6 · three momenta per valley · constant tunnelling',fontsize=11,color='#485a70')
colors={1:'#167d8d',-1:'#c24b37'}
labels={1:'K: native versus fast',-1:'K′: native versus fast'}
for ax,key,title,tol in zip(axes,['matrix_error_meV','spectrum_error_meV'],['Matrix entries in the same real basis','Six central ordered energies'],[1e-9,1e-8]):
    ax.set_facecolor('white')
    for valley,shift in [(1,-.1),(-1,.1)]:
        rr=[x for x in rows if x['valley']==valley]
        ax.scatter(np.arange(9)+shift,[x[key] for x in rr],s=44,c=colors[valley],label=labels[valley],marker='o' if valley==1 else 'D',zorder=3)
    ax.axhline(tol,color='#64748b',lw=1,ls=(0,(4,3)))
    ax.text(8.45,tol*2,f'review tolerance {tol:.0e}',ha='right',fontsize=9,color='#64748b')
    for x in (2.5,5.5):ax.axvline(x,color='#e2e8f0',lw=1)
    ax.set_yscale('log');ax.set_ylim(5e-15,5e4);ax.set_xlim(-.55,8.55)
    ax.set_xticks(range(9),['A','B','C']*3)
    ax.set_ylabel('Maximum absolute difference (meV)')
    ax.set_title(title,loc='left',pad=15,fontsize=12,weight='bold')
    ax.grid(axis='y',color='#e7edf4',lw=.7)
    for x,N in ((1,3),(4,4),(7,6)):ax.text(x,-.13,f'N = {N}',ha='center',transform=ax.get_xaxis_transform(),fontsize=11)
axes[0].legend(loc='center left',bbox_to_anchor=(0,.55),frameon=True,facecolor='white',framealpha=1,fontsize=10)
fig.subplots_adjust(left=.075,right=.975,bottom=.23,top=.77)
fig.text(.075,.09,'A = (0.31, 0.27)     B = (0.11, 0.43)     C = (−0.31, −0.27)   in fractional momentum coordinates',fontsize=10,color='#485a70')
fig.text(.075,.04,'Finite sampled checks. Error measures implementation disagreement, not physical uncertainty. No interpolation is implied.',fontsize=10,color='#485a70')
for ext in ('png','svg'):fig.savefig(ROOT/('valley_review.'+ext),dpi=180,facecolor=fig.get_facecolor())
(ROOT/'FIGURE.json').write_text(json.dumps({'source':'PROBES.json','sha256':hashlib.sha256((ROOT/'PROBES.json').read_bytes()).hexdigest(),'rows':len(rows),'figure':'valley_review.png','scope':'All 18 recorded comparisons; no generated data or interpolating curves.'},indent=2)+'\n')
print('Rendered all',len(rows),'comparison rows')
