"""Render recorded benchmark output; no research engine runs."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import Model
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'RESULTS.json').read_text());m=Model(r['parameters'])
fig,axs=plt.subplots(1,2,figsize=(12,5.5),gridspec_kw={'width_ratios':[1.5,1]})
fig.suptitle('Published-spectrum checks and an unresolved off-axis mismatch',fontsize=16,y=.98)
q=np.array([x['Q'] for x in r['states']]);e=np.array([x['gamma_branches_meV'] for x in r['states']]);colors=['#177E89','#42A5B3','#D18A24','#A55721']
for i,c in enumerate(colors):axs[0].plot(q,e[:,i],color=c,lw=2,label=['A−','A+','B−','B+'][i])
for Q in q[::5]:axs[0].scatter([Q]*4,np.linalg.eigvalsh(m.h([0,0],Q)),s=15,facecolors='none',edgecolors='black',zorder=5)
for name in ['Qn','Qg']:axs[0].axvline(r['thresholds'][name],c='#777',ls=':',lw=1)
axs[0].set(title='At Γ: matrix eigenvalues match Eq. 87',xlabel='Dimensionless boost Q = vq / γ',ylabel='Energy (meV)');axs[0].legend(ncol=4,fontsize=8,loc='lower left');axs[0].text(.03,.14,'Curves: published formula   ○: matrix diagonalization',transform=axs[0].transAxes,fontsize=8)
a=np.linalg.eigvalsh(m.h([.23,-.17],.5));b=np.linalg.eigvalsh(m.direct_projection([.23,-.17],.5));delta=a-b
axs[1].bar(np.arange(1,5),delta,color=['#D18A24' if d>=0 else '#177E89' for d in delta]);axs[1].axhline(0,c='#555',lw=1);axs[1].set(title='Off-axis: the two assemblies disagree',xlabel='Sorted band index',ylabel='Literal Eq. 73 − direct projection (meV)',xticks=[1,2,3,4]);axs[1].text(.04,.96,'K = (0.23, −0.17), Q = 0.5',va='top',transform=axs[1].transAxes,fontsize=9)
for ax in axs:ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15)
fig.text(.05,.025,'Reproduction diagnostic only. Off-axis conventions remain unresolved; no braid or physical-validation claim.',fontsize=10)
fig.tight_layout(rect=[0,.075,1,.92]);fig.savefig(ROOT/'benchmark-checks.png',dpi=150)
