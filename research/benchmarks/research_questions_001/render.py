"""Render retained diagnostic outputs; performs no model calculation."""
import hashlib
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--preview',type=Path,help='Optional PNG preview output')
args=parser.parse_args()
r=json.loads((root/'RESULTS.json').read_text())
s=json.loads((root/'SPECTRAL_CURVES.json').read_text())
if not r['passed'] or r['source_sha256']!=hashlib.sha256((root/'reproduce.py').read_bytes()).hexdigest():
    raise SystemExit('Refusing to render failed or source-mismatched results')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.titleweight':'bold','svg.hashsalt':'research-questions-001'})
fig,ax=plt.subplots(2,2,figsize=(12,8.8),layout='constrained')
fig.suptitle('Same energies. Different topology.',fontsize=24,fontweight='bold')
fig.get_layout_engine().set(rect=(0,.05,1,.93))
c1,c0='#146B8C','#DB7542'
for m,color,label in [('-1',c1,'Euler 2 · m = −1'),('-3',c0,'Euler 0 · m = −3')]:
    row=r['wilson_curves'][m]
    phase=np.array(row['phase']);phase-=phase[0]
    ax[0,0].plot(np.array(row['ky'])/np.pi,phase/(2*np.pi),color=color,lw=2.4,label=label)
ax[0,0].set(title='A  Frame holonomy separates the bundles',xlabel=r'$k_y/\pi$',ylabel='Unwrapped phase / 2π')
ax[0,0].legend(frameon=False)
for suffix,color,label,ls in [('euler2',c1,'Euler 2','-'),('euler0',c0,'Euler 0','--')]:
    ax[0,1].plot(s['energy'],s[suffix+'_trace'],ls,color=color,lw=2.3,label=label)
    ax[1,0].plot(s['energy'],s[suffix+'_probe'],ls,color=color,lw=2.3,label=label)
ax[0,1].set(title='B  Total spectral density is identical',xlabel='Energy (dimensionless)',ylabel='Tr A(k, E)')
ax[1,0].set(title='C  An orbital probe can distinguish this pair',xlabel='Energy (dimensionless)',ylabel='Tr[P A(k, E)]')
for a in [ax[0,1],ax[1,0]]:a.legend(frameon=False)
pilot=json.loads((root/'pilot_rejected'/'RESULTS.json').read_text())
coarse=next(x for x in pilot['bundle_results'] if x['m']==-1 and x['mesh']==24)
fine=[x for x in r['bundle_results'] if x['m']==-1]
sizes=[24]+[x['mesh'] for x in fine]
steps=[coarse['max_phase_step']]+[x['max_phase_step'] for x in fine]
ax[1,1].plot(sizes,steps,'o-',color=c1,lw=2,ms=7)
ax[1,1].axhline(np.pi/2,ls='--',color='#993A42',label='Fixed criterion: phase step < π/2')
ax[1,1].annotate('24 rejected',xy=(24,steps[0]),xytext=(31,1.72),fontsize=10,color='#993A42')
ax[1,1].set(title='D  Correct integer alone is insufficient',xlabel='Points per momentum direction',ylabel='Largest phase step (rad)',ylim=(0,1.95),xticks=sizes)
ax[1,1].legend(frameon=False,loc='lower left',fontsize=9)
for a in ax.flat:a.grid(alpha=.15)
fig.text(.02,.025,'Synthetic reference only • k = (π/2, 0), η = 0.08 in B/C • P = diag(1, 0, 0)\nNo graphene trajectory, braiding event, experimental signal or physical sign convention is established.',fontsize=10,color='#444444')
fig.savefig(root/'reference-diagnostics.svg',metadata={'Date':None})
if args.preview:
    fig.savefig(args.preview,dpi=160)
