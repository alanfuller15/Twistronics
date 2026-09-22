"""Render saved results only; does not run eigensolvers."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent
cross=json.loads((p/'CROSSING.json').read_text())
fig,ax=plt.subplots(1,2,figsize=(11,4.8),gridspec_kw={'width_ratios':[1.2,1]})
fig.patch.set_facecolor('#fafafa')
for N,color in [(4,'#2166ac'),(6,'#b35806')]:
 rows=[x for x in cross['rows'] if x['N']==N and x['engine']=='bm']
 ax[0].plot([x['D_meV'] for x in rows],[x['offset'] for x in rows],'-o',color=color,label=f'N{N} (BM; ref overlaps)')
ax[0].axhline(0,color='#555555',lw=1)
ax[0].set(xlabel='D: layer potential amplitude (meV)',ylabel='Signed offset (fractional momentum)',title='Local crossing bracket survives N6',xticks=[38,39])
ax[0].legend(fontsize=9);ax[0].grid(alpha=.15)
ax[0].text(.02,.04,'Two sampled stations; lines guide the eye.\nSegment coordinate t = 0.725–0.730.',transform=ax[0].transAxes,fontsize=9)
ax[1].axis('off')
ax[1].set_title('Endpoint relative-charge labels')
rows=[]
for name,title in [('N4_baseline','N4 baseline'),('N4_refined','N4 refined'),('N6_refined','N6 refined')]:
 r=json.loads((p/(name+'.json')).read_text());labels=[next(x['label'] for x in r['rows'] if x['D_meV']==d and x['engine']=='bm') for d in [36,42]];rows.append([title,*labels])
t=ax[1].table(cellText=rows,colLabels=['Settings','D = 36','D = 42'],cellLoc='center',bbox=[0,.35,1,.5]);t.auto_set_font_size(False);t.set_fontsize(10)
for (i,j),cell in t.get_celld().items():
 cell.set_edgecolor('#dddddd')
 if i==0:cell.set_facecolor('#e9eef3')
ax[1].text(.5,.2,'BM and reference agree in every row.\nModel: 0.7% strain, 15° direction, 1.00° twist.',ha='center',fontsize=10,transform=ax[1].transAxes)
fig.suptitle('R1 candidate: reproduced numerical evidence',fontsize=16,y=.99)
fig.text(.5,.02,'Not full braid acceptance • No annihilation proof • Experimental calibration remains open',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.06,1,.94));fig.savefig(p/'r1-checkpoint.png',dpi=180);plt.close(fig)
