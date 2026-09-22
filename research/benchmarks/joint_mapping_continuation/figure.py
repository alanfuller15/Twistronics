"""Draw retained conditional enclosures; no new scientific calculation."""
import hashlib,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FormatStrFormatter
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=json.loads((ROOT/'SUMMARY.json').read_text())
assert s['all_checks_pass']
for name,h in s['source_hashes'].items():assert sha(ROOT.parent/name)==h,name
leaf=s['leaf_bounds']
camp=next(c for c in s['campaigns'] if c['engine']=='bm' and c['mesh']==8)
ends=camp['endpoint_enclosures'];sx=np.array([p['strain'] for p in ends]);dy=np.array([np.mean(p['D_enclosure_meV']) for p in ends])
def chord(x):return np.interp(x,sx,dy)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelcolor':'#172c42','text.color':'#172c42',
                     'xtick.color':'#475a6e','ytick.color':'#475a6e','axes.spines.top':False,'axes.spines.right':False,
                     'axes.edgecolor':'#b7c4ce','svg.hashsalt':'joint-mapping-continuation'})
fig=plt.figure(figsize=(13.8,8.6),facecolor='#f6f8fa')
fig.text(.065,.947,'ONE LOCAL EVENT BRANCH',fontsize=23,weight='bold')
fig.text(.065,.908,'Conditional continuation across 0.70–0.71% strain · fixed 87-vector basis · dimension 348',fontsize=12,color='#475a6e')
grid=fig.add_gridspec(2,2,left=.075,right=.96,bottom=.22,top=.80,width_ratios=[1.16,1],wspace=.28,hspace=.51)
a=fig.add_subplot(grid[:,0]);b=fig.add_subplot(grid[0,1]);c=fig.add_subplot(grid[1,1]);colors={'bm':'#006e85','ref':'#d66636'}
for ax in [a,b,c]:
 ax.set_facecolor('white');ax.grid(color='#dfe6eb',linewidth=.65,alpha=.85);ax.set_axisbelow(True)
 ax.set_xlim(sx[0]*100,sx[1]*100);ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
 ax.set_xlabel('Strain (%)')
a.set_title('A   Event parameter D(s)',loc='left',weight='bold',pad=12)
a.set_ylabel('Opposite layer-potential amplitude D (meV)')
b.set_title('B   Same enclosures, magnified',loc='left',weight='bold',pad=12)
b.set_ylabel('D − endpoint chord (µeV)')
c.set_title('C   Contraction bound on each cell',loc='left',weight='bold',pad=12)
c.set_ylabel('q');c.set_ylim(0,.56)
for engine in ['bm','ref']:
 rows=sorted((r for r in leaf if r['engine']==engine and r['mesh']==8),key=lambda r:r['a'])
 for r in rows:
  x=np.array([r['a'],r['b']]);d=np.array(r['D_predictor_ends']);radius=r['D_inner_radius']
  a.fill_between(x*100,d-radius,d+radius,color=colors[engine],alpha=.19,linewidth=0)
  a.plot(x*100,d,color=colors[engine],lw=1.7,ls='-' if engine=='bm' else '--')
  yy=(d-chord(x))*1000;rr=radius*1000
  b.fill_between(x*100,yy-rr,yy+rr,color=colors[engine],alpha=.18,linewidth=0)
  b.plot(x*100,yy,color=colors[engine],lw=1.3,ls='-' if engine=='bm' else '--')
 for mesh,ls in [(4,'-'),(8,'--')]:
  rr=sorted((r for r in leaf if r['engine']==engine and r['mesh']==mesh),key=lambda r:r['a'])
  xx=np.array([r['a'] for r in rr]+[rr[-1]['b']])*100;yy=[r['q'] for r in rr]+[rr[-1]['q']]
  c.step(xx,yy,where='post',color=colors[engine],lw=1.6,ls=ls)
b.axhline(0,color='#74889b',lw=.8,ls=':')
c.axhline(.5,color='#9f4d49',lw=1,ls=':');c.text(sx[0]*100+.00025,.507,'acceptance limit 0.5',color='#9f4d49',fontsize=9)
a.legend(handles=[Line2D([0],[0],color=colors['bm'],label='BM predictor'),Line2D([0],[0],color=colors['ref'],ls='--',label='REF predictor'),Patch(facecolor='#006e85',alpha=.2,label='Conditional inner enclosures')],loc='upper left',frameon=True,facecolor='white',edgecolor='#dfe6eb',fontsize=9)
a.text(.97,.045,'Both engines overlap at this scale.\nPanels A–B use the 8-cell starting mesh.',transform=a.transAxes,ha='right',fontsize=9,color='#475a6e')
c.text(.035,.075,'Solid: 4 initial cells · dashed: 8\nBoth meshes finish with 32 cells per engine.',transform=c.transAxes,fontsize=8.7,color='#475a6e')
fig.text(.075,.145,f"{s['accepted_leaves']} accepted cells   /   {s['endpoint_joins']} endpoint joins   /   {s['controls']} controls   /   {s['unresolved_cells_or_joins']} unresolved",fontsize=13,weight='bold',color='#006e85')
fig.text(.075,.102,'Enclosures assume the declared floating-point allowances; no outward-rounded arithmetic is used.',fontsize=10.2)
fig.text(.075,.069,'Local root/segment geometry only. D is a model parameter; no braid, Euler-class change or experimental validation follows.',fontsize=9.7,color='#475a6e')
fig.text(.075,.035,'Source: retained SUMMARY.json + RESULTS.json, source hashes checked. Reference chord joins located endpoint centers.',fontsize=8.5,color='#6d7d8d')
for ext in ['png','svg']:fig.savefig(ROOT/f'event_branch.{ext}',dpi=180,facecolor=fig.get_facecolor(),metadata={'Title':'Conditional fixed-basis local event branch'} if ext=='svg' else None)
plt.close(fig)
provenance={'source_hashes':{'SUMMARY.json':sha(ROOT/'SUMMARY.json'),'figure.py':sha(ROOT/'figure.py')},'outputs':{f'event_branch.{e}':sha(ROOT/f'event_branch.{e}') for e in ['png','svg']},'scope':s['scope'],'matplotlib':matplotlib.__version__}
(ROOT/'FIGURE.json').write_text(json.dumps(provenance,indent=2)+'\n')
print('Rendered PNG and SVG from retained conditional enclosures; source hashes verified.')
