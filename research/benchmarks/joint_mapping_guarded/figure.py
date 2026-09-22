"""Render retained results only, after checking the report's source hashes."""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
s=json.loads((ROOT/'SUMMARY.json').read_text())
for name,h in s['source_hashes'].items():
    assert hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==h,name
assert s['all_checks_pass']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
                     'axes.spines.right':False,'svg.fonttype':'none'})
fig=plt.figure(figsize=(12.5,8.5),facecolor='#f9fbfb')
fig.text(.075,.945,'FIXED BASIS, RECHECKED CANDIDATES',fontsize=21,weight='bold',color='#21343c')
fig.text(.075,.899,'24 controls pass  ·  30 sampled events  ·  two five-station traces complete',fontsize=13,color='#127f83',weight='bold')
fig.text(.075,.857,'Five strain values at 15°; N6 radial sets compared with explicit 87-vector and 85-vector sets.',fontsize=11,color='#5e737d')
a=fig.add_axes([.085,.455,.53,.33]);b=fig.add_axes([.70,.455,.24,.33]);c=fig.add_axes([.085,.16,.855,.19])
rows=s['comparisons'];x=np.array([r['eps']*100 for r in rows])
style=[('radial','#273d48','o','Radial cutoff'),('union','#138185','x','Fixed union: 87 vectors'),('intersection','#b37a24','+','Fixed intersection: 85 vectors')]
for name,color,marker,label in style:
    y=np.array([r[name+'_D_meV'] for r in rows])
    if marker=='o':a.scatter(x,y,s=72,facecolors='none',edgecolors=color,label=label)
    else:a.scatter(x,y,s=65,color=color,marker=marker,label=label)
a.set(xlabel='Strain magnitude (%)',ylabel='Located event D (meV)',xticks=x)
a.set_title('Candidates persist in both fixed bases',loc='left',weight='bold',fontsize=12,pad=13)
a.legend(frameon=False,fontsize=9,loc='upper left');a.grid(alpha=.15)
b.scatter(x,[r['radial_dimension'] for r in rows],s=45,c='#273d48',label='Radial')
b.scatter(x,[348]*len(x),marker='x',s=55,c='#138185',label='Union')
b.scatter(x,[340]*len(x),marker='+',s=65,c='#b37a24',label='Intersection')
b.set(xlabel='Strain (%)',ylabel='Matrix dimension',yticks=[340,348],xticks=[.70,.72,.76],ylim=(337,351))
b.set_title('Dimension is now explicit',loc='left',weight='bold',fontsize=12,pad=13);b.grid(alpha=.15)
xx=np.arange(len(rows));width=.32
c.bar(xx-width/2,[r['union_minus_radial_meV']*1000 for r in rows],width,color='#138185',label='Union − radial')
c.bar(xx+width/2,[r['intersection_minus_radial_meV']*1000 for r in rows],width,color='#b37a24',label='Intersection − radial')
c.axhline(0,color='#52656f',lw=.8);c.set_xticks(xx,[f'{v:.2f}%' for v in x]);c.set_ylabel('Event D shift (µeV)')
c.set_title('Small sampled sensitivity to retaining the two edge vectors',loc='left',weight='bold',fontsize=12,pad=12)
c.legend(frameon=False,fontsize=9,loc='lower right');c.grid(axis='y',alpha=.15)
fig.text(.075,.082,'Locations meet the declared offset tolerance. Bars are sampled differences, not certified error bounds.',fontsize=10,color='#52656f')
fig.text(.075,.042,'Fixed index sets remove the dimension jump. Continuous root identity, completeness and topology remain unproved.',fontsize=10,color='#52656f')
for ext in ('png','svg'):fig.savefig(ROOT/('fixed_basis_comparison.'+ext),dpi=155,facecolor=fig.get_facecolor())
print('Rendered',s['status'])
