"""Display sampled candidates and cutoff shifts without implying surfaces."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from inputs import ROOT, sha
S=json.loads((ROOT/'SUMMARY.json').read_text());assert S['all_candidate_checks_pass']
assert all(sha(ROOT/n)==h for n,h in S['source_hashes'].items())
C=S['comparisons'];blue='#457c9b';teal='#127f83';dark='#22363f';gray='#596b76'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
fig=plt.figure(figsize=(12.8,9.8),facecolor='#fafbf9')
fig.text(.075,.944,'PARTNER CANDIDATES: RECHECKED, STILL EXPLORATORY',fontsize=20,weight='bold',color=dark)
fig.text(.075,.902,'Six supplied states  ·  two engines  ·  N4 and N6  ·  all 24 sampled checks pass',fontsize=12,color=teal,weight='bold')
fig.text(.075,.872,'BM values are plotted; REF agrees within 3.85 × 10⁻¹² meV. Markers do not establish continuity between points.',fontsize=10,color=gray)

for rect,ids,free,title in [([.08,.505,.365,.295],[0,1,2],'phi','Changing strain direction'),([.565,.505,.36,.295],[0,3,4,5],'eps','Changing strain magnitude')]:
    ax=fig.add_axes(rect)
    xx=[C[i]['x'][free]*(100 if free=='eps' else 1) for i in ids]
    for N,marker,color in [('4','o',blue),('6','x',teal)]:
        yy=[C[i]['cutoffs'][N]['BM_D_meV'] for i in ids]
        ax.scatter(xx,yy,s=70,marker=marker,facecolors='none' if marker=='o' else color,edgecolors=color,label='N'+N,zorder=3)
    ax.set_title(title,loc='left',weight='bold',fontsize=12,pad=12);ax.set_ylabel('Located event D (meV)')
    ax.set_xlabel('Strain angle (degrees)' if free=='phi' else 'Strain magnitude (%)')
    ax.set_xticks(xx);ax.grid(alpha=.16);ax.legend(frameon=False,loc='upper center',ncol=2,fontsize=9)
    if free=='phi':ax.set_ylim(37.08,38.32)
    else:
        ax.axvspan(.7003,.7197,color='#c39a37',alpha=.13,zorder=0)
        ax.text(.703,42.75,'N6 basis changes\n348 → 340 dimensions',fontsize=8.5,color='#876212',va='top')
        ax.set_ylim(37.65,43.25)

ax=fig.add_axes([.105,.205,.81,.19])
xx=np.arange(6);delta=np.array([c['N6_minus_N4_D_meV'] for c in C])
ax.bar(xx,delta*1000,width=.48,color=[teal if v>0 else blue for v in delta]);ax.axhline(0,color=dark,lw=.8)
for x,y in zip(xx,delta*1000):ax.text(x,y+(1.8 if y>=0 else -1.8),f'{y:+.2f}',ha='center',va='bottom' if y>=0 else 'top',fontsize=9)
ax.set_xticks(xx,[f"{c['x']['eps']*100:.2f}% / {c['x']['phi']:g}°" for c in C]);ax.set_ylim(-17,43)
ax.set_ylabel('N6 − N4 event D (μeV)');ax.set_title('Cutoff dependence is larger than the engine disagreement',loc='left',weight='bold',fontsize=12,pad=10)
ax.grid(axis='y',alpha=.12)
fig.text(.075,.122,'Review: eight tooling failures reproduced; the 24×24 grid also misses the known crossing node.',fontsize=11,color=dark)
fig.text(.075,.08,'D is a model layer-potential amplitude. These are candidate locations, without continuous identity, surface, braid or Euler-class acceptance.',fontsize=9.5,color=gray)
for ext in ['png','svg']:fig.savefig(ROOT/f'candidate_review.{ext}',dpi=190,facecolor=fig.get_facecolor())
print('Rendered retained candidate review:',S['status'])
