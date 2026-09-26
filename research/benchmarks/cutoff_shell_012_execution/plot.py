"""Plot finite-cutoff comparisons from retained summary; no physical calls."""
import json,sys,numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(sys.argv[1]);s=json.loads((p/'SUMMARY.json').read_text());fig,axes=plt.subplots(1,2,figsize=(11.5,4.5),layout='constrained');colors=['#eb6834','#1baf7a']
for i,(name,label) in enumerate([('original_R3','Original candidate (R3)'),('candidate_R1','Second candidate (R1)')]):
 patch=s['patches'][name];v=[patch['comparisons'][link]['maximum_abs_upper_gap_shift_microeV'] for link in ['bc','cd']]
 axes[0].plot([0,1],v,'o-',label=label,color=colors[i]);
 for j,x in enumerate(v):axes[0].annotate(f'{x:.3g}',(j,x),xytext=(6,5),textcoords='offset points',fontsize=9)
 f=[patch['comparisons'][link]['maximum_four_angle_degrees'] for link in ['bc','cd']];axes[1].plot([0,1],f,'o-',label=label,color=colors[i])
 for j,x in enumerate(f):axes[1].annotate(f'{x:.3g}°',(j,x),xytext=(6,5),textcoords='offset points',fontsize=9)
for ax in axes:ax.set(yscale='log',xticks=[0,1],xticklabels=['b → c (308 → 444)','c → d (444 → 604)'],xlim=(-.2,1.6));ax.grid(alpha=.2)
axes[0].set(title='Upper gaps change less on the next shell',ylabel='Maximum |gap shift| on each 3×3 patch (µeV)');axes[0].legend(frameon=False,fontsize=9)
axes[1].set(title='The four-state subspace changes less, too',ylabel='Maximum four-state principal angle (degrees)')
fig.suptitle('CUTOFF-SHELL-012 • fourth finite cutoff, 72 eigensolves',fontsize=14)
fig.supxlabel('Two local patches, step 2⁻²²; index-based comparisons. Original-site pair angle still reaches 51.8°. No infinite-cutoff claim. Review pending.',fontsize=9)
fig.savefig(p/'cutoff-shell.png',dpi=150);plt.close(fig)
