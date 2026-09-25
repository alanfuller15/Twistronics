"""Derived display only, from exact accepted/frontier/unresolved partitions."""
from pathlib import Path
from fractions import Fraction
import json,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Patch
root=Path(sys.argv[1]); run=Path(sys.argv[2]); out=Path(sys.argv[3]);out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(root/'research/benchmarks/parallel_domain_001'))
import parallel as p
before={q:p.initial(q) for q in p.QUADRANTS}
after=json.loads((run/'PARTITION.json').read_text())
results=json.loads((run/'RESULTS.json').read_text())
p.validate_partition({q:{k:[tuple(c) for c in cells] for k,cells in state.items()} for q,state in after.items()})
base={tuple(c) for s in before.values() for c in s['accepted']}
colors={'old':'#148478','new':'#3782f6','frontier':'#e5e9ef','unresolved':'#e55a46'}
fig,axes=plt.subplots(1,2,figsize=(12,7.2))
fig.patch.set_facecolor('#f7f9fc')
fig.subplots_adjust(left=.055,right=.99,bottom=.24,top=.82,wspace=.19)
for ax,states,title in zip(axes,[before,after],['Retained baseline','After four concurrent workers']):
    for q,state in states.items():
        for kind,cells in state.items():
            for d,ix,iy in cells:
                size=2**(-d)
                color=colors['old' if (d,ix,iy) in base else 'new'] if kind=='accepted' else colors[kind]
                ax.add_patch(Rectangle((ix*size,iy*size),size,size,facecolor=color,edgecolor='none'))
        fraction=4*p.area(state['accepted'])
        qx,qy=int(q[1]),int(q[2])
        ax.text(qx*.5+.02,qy*.5+.46,f'{q.upper()}  {float(fraction):.1%}',va='top',fontsize=10,
                bbox=dict(boxstyle='round,pad=.25',fc='white',ec='none',alpha=.9))
    for x in [.5]:ax.axvline(x,color='#243854',linewidth=.8);ax.axhline(x,color='#243854',linewidth=.8)
    ax.set(xlim=(0,1),ylim=(0,1),aspect='equal',xlabel='x  (fraction of G₁)',ylabel='y  (fraction of G₂)')
    ax.set_xticks([0,.25,.5,.75,1]);ax.set_yticks([0,.25,.5,.75,1])
    total=sum((p.area(s['accepted']) for s in states.values()),Fraction())
    ax.set_title(f'{title}\n{float(total):.2%} accepted full-square area',loc='left',pad=12,fontweight='bold')
fig.suptitle('Twistronics • Full-domain coverage campaign',fontsize=20,fontweight='bold',x=.025,ha='left')
fig.legend(handles=[Patch(color=colors[k],label=l) for k,l in [('old','Previously accepted'),('new','Newly accepted'),('frontier','Queued / unprocessed'),('unresolved','Unresolved at depth limit')]],loc='lower center',bbox_to_anchor=(.5,.105),ncol=4,frameon=False)
fig.supxlabel('k = xG₁ + yG₂ • Fractional momentum coordinates, not real-space positions.\nCell side = 2⁻ᵈ; full-square area = 4⁻ᵈ. Quadrant labels use each quadrant’s own area.',fontsize=10,y=.025)
fig.savefig(out/'coverage.png',dpi=170)
fig.savefig(out/'coverage.svg')
