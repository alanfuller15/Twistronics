"""Render only retained signed-side bounds and conditional event enclosures."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.patches import Patch
from crossing import ROOT, sha

S=json.loads((ROOT/'SUMMARY.json').read_text());assert S['all_checks_pass']
assert all(sha(ROOT/n)==h for n,h in S['source_hashes'].items())
data=json.loads((ROOT/'RESULTS.json').read_text())
case=next(c for c in data['cases'] if c['engine']=='bm' and c['mesh']=='fine' and c['radius']==.003)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
fig=plt.figure(figsize=(13.6,9.2),facecolor='#fafbf9')
dark='#203540';blue='#477f9b';teal='#128186';gray='#536872'
fig.text(.065,.943,'ONE CROSSING BY THE TRACKED UPPER NODE',fontsize=22,weight='bold',color=dark)
fig.text(.065,.902,'Exact declared straight stems  ·  both engines, meshes and radii  ·  N = 8  ·  D = 38–39 meV',fontsize=11.5,color=gray)
fig.text(.065,.847,'140 interval bounds     /     64 point checks     /     0 unresolved intervals',fontsize=16,weight='bold',color=teal)

ax=fig.add_axes([.08,.335,.425,.425])
def band(axis):
    for i in case['leaf_ids']:
        row=case['attempts'][i];q=np.array(row['geometry']['side_coefficients']);t=np.linspace(0,1,50)
        D=row['a']+(row['b']-row['a'])*t;p=q[0]+q[1]*t+q[2]*t*t;err=row['geometry']['side_error']
        axis.fill_between(D,1000*(p-err),1000*(p+err),color=blue,alpha=.35,lw=0)
        axis.plot(D,1000*(p-err),color=blue,lw=.65);axis.plot(D,1000*(p+err),color=blue,lw=.65)
    axis.axhline(0,color=dark,lw=.9)
band(ax)
ax.axvspan(38.0625,38.125,color=teal,alpha=.09,zorder=-1)
ax.set(xlim=(38,39),xlabel='Layer-potential amplitude D (meV)',ylabel='Signed area × 1,000 (fractional-coordinate units²)')
ax.set_title('The tracked node changes sides once',loc='left',fontsize=13,weight='bold',pad=14)
ax.text(.02,.06,'BM · fine geometry · r = 0.003\nRibbon encloses the actual root’s signed side.',transform=ax.transAxes,color=gray,fontsize=9)
ax.grid(alpha=.12)
zoom=ax.inset_axes([.46,.5,.51,.44]);band(zoom)
zoom.set_xlim(38.0625,38.125);zoom.set_ylim(-.045,.025)
zoom.axvspan(*case['event_interval_meV'],color=teal,alpha=.65)
zoom.set_xticks([38.065,38.09,38.12]);zoom.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
zoom.tick_params(labelsize=8);zoom.set_title('Event window enlarged',fontsize=9)
zoom.grid(alpha=.12)

ax=fig.add_axes([.695,.335,.25,.425])
for i,c in enumerate(S['cases']):
    a,b=c['event_interval_meV'];color=blue if c['engine']=='bm' else teal
    ax.plot([a,b],[i,i],color=color,lw=4,solid_capstyle='butt');ax.plot([a,a],[i-.12,i+.12],color=color,lw=1.3);ax.plot([b,b],[i-.12,i+.12],color=color,lw=1.3)
ax.set_yticks(range(8),[f"{c['engine'].upper()} · {c['mesh']} · {c['radius']:g}" for c in S['cases']],fontsize=9)
ax.invert_yaxis();ax.set_xlim(38.07788,38.077985);ax.set_xticks([38.0779,38.07794,38.07798]);ax.xaxis.set_major_formatter(FormatStrFormatter('%.5f'))
ax.set_xlabel('Event D (meV)');ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
ax.set_title('Conditional event intervals',loc='left',fontsize=13,weight='bold',pad=14);ax.grid(axis='x',alpha=.15)
fig.text(.695,.265,'Lines show enclosures; no point estimate is drawn.',fontsize=9,color=gray)

fig.text(.065,.235,'WHY THIS COUNTS AS ONE TRANSVERSE SEGMENT CROSSING',fontsize=12,weight='bold',color=dark)
fig.text(.065,.19,'Inside the event window, the side derivative stays negative and the node stays strictly between the stem endpoints.',fontsize=10.5,color=dark)
fig.text(.065,.157,'Outside that window, the continued node stays away from the entire supporting line throughout D = 38–39.',fontsize=10.5,color=dark)
fig.text(.065,.102,'Inherited charge evidence: the detoured contour retains +k; the straight-stem endpoints are +k and −k.',fontsize=10.5,color=dark)
fig.text(.065,.065,'Conditional floating-point bounds. Other nodes on the swept stem remain uncounted. No new charge, full braid or Euler-class result.',fontsize=9.5,color=gray)
for ext in ['png','svg']:fig.savefig(ROOT/f'stem_crossing.{ext}',dpi=190,facecolor=fig.get_facecolor())
print('Rendered source-bound stem crossing:',S['status'])
