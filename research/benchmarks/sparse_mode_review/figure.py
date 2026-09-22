"""Retained timing and band-window review figure; no new model calculation."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((ROOT/'REGRESSIONS.json').read_text());t=json.loads((ROOT/'TIMINGS.json').read_text());s=json.loads((ROOT/'SUMMARY.json').read_text())
for n,h in r['source_hashes'].items():assert sha(ROOT/n)==h
for n,h in s['source_hashes'].items():assert sha(ROOT/n)==h
assert sha(ROOT/'SOLVER_PROBE.log')==t['source_log_sha256']
x=np.arange(3);rows=t['rows'];w=r['cases']['shifted_window_mislabels_absolute_bands']['evidence'];assert w['accepted']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':'#172c42','axes.labelcolor':'#172c42','axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#b6c4cf','xtick.color':'#475a6e','ytick.color':'#475a6e','svg.hashsalt':'sparse-mode-review'})
fig,ax=plt.subplots(1,2,figsize=(13.8,7.4),gridspec_kw={'width_ratios':[.9,1.3]},facecolor='#f6f8fa')
fig.subplots_adjust(left=.07,right=.96,top=.76,bottom=.28,wspace=.3)
fig.text(.07,.925,'Sparse-mode review',size=25,weight='bold')
fig.text(.07,.865,'Useful kernel speedup · a reproduced band-label failure · ten dense candidate checks pass',size=12,color='#475a6e')
a,b=ax
for axis in ax:axis.set_facecolor('white');axis.grid(axis='y',color='#dfe6eb');axis.set_axisbelow(True)
a.bar(x-.18,[v['dense_ms'] for v in rows],width=.34,color='#006e85',label='Dense subset')
a.bar(x+.18,[v['sparse_ms'] for v in rows],width=.34,color='#e58a44',label='Sparse shift-invert')
a.set_xticks(x,[f"N{v['N']}\ndim {v['dimension']}" for v in rows]);a.set_ylim(0,105);a.set_ylabel('Solve time on a preassembled matrix (ms)')
a.set_title('A   Kernel timings in this environment',loc='left',weight='bold',pad=14)
a.legend(frameon=False,fontsize=9,loc='upper left')
for i,v in enumerate(rows):a.text(i,v['dense_ms']+3,f"{v['ratio']:.1f}×",ha='center',weight='bold',size=11,color='#006e85')
b.set_title('B   Bracketing σ does not fix band indices',loc='left',weight='bold',pad=14)
b.set_xlim(-125,190);b.set_ylim(-.35,1.5);b.set_yticks([1,0],['Requested\n171–176','Returned\n173–178']);b.set_xlabel('Energy (meV)');b.axvline(100,color='#74889b',ls=':',lw=1)
b.text(102,1.32,'σ = 100 meV',fontsize=10,color='#475a6e')
b.hlines([1,0],[-107,-15.9],[134.5,168.1],color=['#006e85','#d66636'],alpha=.28,lw=3)
for y,vals,ids,col in [(1,w['target'],w['target_indices'],'#006e85'),(0,w['returned'],w['matched_indices'],'#d66636')]:
 b.scatter(vals,np.full(6,y),s=66,color=col,zorder=3)
 for val,i in zip(vals,ids):
  offset=-.18 if y==0 and i==177 else .13
  b.text(val,y+offset,str(i),ha='center',fontsize=9,color=col)
b.text(.04,.56,'Guard accepts this shifted window.\nAbsolute-band comparison differs by 108.2 meV.',transform=b.transAxes,fontsize=10.5,color='#a54a26',bbox={'facecolor':'#fff6ef','edgecolor':'none','pad':7})
fig.text(.07,.17,'9 supplied tests pass. The added checks expose gaps those tests do not cover.',fontsize=13,weight='bold',color='#006e85')
fig.text(.07,.12,'Timing: two calls per kernel; excludes setup and acceptance checks. It is not an end-to-end campaign speedup.',fontsize=10)
fig.text(.07,.079,'Window example: N6, strain 0.70%, D = 38 meV, f = (0.31, 0.27). No mismatch on the tested 25-point σ = 0 grid.',fontsize=10)
fig.text(.07,.038,'Source hashes checked. Separate dense rechecks cover N4–N12 in both engines; no continuous high-cutoff or topological claim.',fontsize=9,color='#617386')
for e in ['png','svg']:fig.savefig(ROOT/f'sparse_review.{e}',dpi=180,facecolor=fig.get_facecolor())
plt.close(fig)
meta={'inputs':{n:sha(ROOT/n) for n in ['REGRESSIONS.json','TIMINGS.json','SUMMARY.json','figure.py']},'outputs':{f'sparse_review.{e}':sha(ROOT/f'sparse_review.{e}') for e in ['png','svg']},'matplotlib':matplotlib.__version__}
(ROOT/'FIGURE.json').write_text(json.dumps(meta,indent=2)+'\n');print('Rendered retained timing and window counterexample; hashes checked.')
