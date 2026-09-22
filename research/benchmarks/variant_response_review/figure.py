"""Draw finite sampled controls directly from retained, hash-bound records."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
old_path=ROOT.parent/'variant_controls_review/PROBES.json'
old=json.loads(old_path.read_text())
new=json.loads((ROOT/'PROBES.json').read_text())
ch=json.loads((ROOT/'REPLAY_CHIRAL_CONTROL.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,2,figsize=(13.5,6.5),gridspec_kw={'wspace':.28})
fig.patch.set_facecolor('#f6f8fb')
fig.text(.075,.94,'The valley correction passes. The chiral scan reproduces.',fontsize=19,weight='bold',color='#17263b')
fig.text(.075,.891,'v074p response review · retained finite-model samples · topology and sparse integration remain open',fontsize=11,color='#485a70')
a=axes[0];a.set_facecolor('white')
for N,size,fill,edge in [(6,100,'none','#197d8d'),(8,22,'#c76a3c','#c76a3c')]:
 rr=[r for r in ch['bandwidth_scan'] if r['N']==N]
 a.scatter([r['alpha'] for r in rr],[r['bandwidth_meV'] for r in rr],s=size,facecolors=fill,edgecolors=edge,linewidths=1.5,label=f'N = {N}',zorder=3)
a.axvline(.586,color='#8190a5',ls=(0,(4,3)),lw=1.2)
a.text(.5854,9.4,'reference ≈ 0.586',ha='right',fontsize=9,color='#58687b')
best=ch['sampled_minimum_N6']
a.annotate(f"sampled minimum\nα = {best['alpha']:.4f}\n{best['bandwidth_meV']:.4f} meV",xy=(best['alpha'],best['bandwidth_meV']),xytext=(.594,1.65),fontsize=10,color='#17263b',arrowprops={'arrowstyle':'->','color':'#485a70','connectionstyle':'angle3'})
a.set(xlabel='Dimensionless coupling α',ylabel='Flat-pair bandwidth (meV)',xlim=(.563,.608),ylim=(0,10.6));a.set_title('Chiral limit: 16 angle–cutoff rows',loc='left',fontsize=12,weight='bold',pad=16)
a.legend(loc='center left',bbox_to_anchor=(.035,.43),frameon=False);a.grid(axis='y',color='#e4eaf1')
fig.text(.075,.12,'100 momenta per row · θ = 1.03–1.10°, step 0.01°\nN6 and N8 symbols overlap at this scale.',fontsize=10,color='#485a70')
a=axes[1];a.set_facecolor('white')
r0=[r for r in old['rows'] if r['valley']==-1];r1=[r for r in new['matrix_rows'] if r['valley']==-1]
for x,(before,after) in enumerate(zip(r0,r1,strict=True)):
 assert (before['N'],before['f'])==(after['N'],after['f'])
 a.plot([x,x],[before['spectrum_error_meV'],after['spectrum_error_meV']],color='#cfdae4',lw=1.2,zorder=1)
a.scatter(range(9),[r['spectrum_error_meV'] for r in r0],s=43,marker='D',c='#c24b37',label='v073p',zorder=3)
a.scatter(range(9),[r['spectrum_error_meV'] for r in r1],s=43,c='#197d8d',label='v074p',zorder=3)
a.set_yscale('log');a.set_ylim(5e-15,1e4);a.set_xlim(-.5,8.5);a.axhline(1e-8,color='#8190a5',ls=(0,(4,3)),lw=1)
a.text(8.3,2e-8,'review tolerance: 10⁻⁸ meV',ha='right',fontsize=9,color='#58687b')
a.set_xticks(range(9),['A','B','C']*3);a.set_ylabel('Native / fast energy difference (meV)');a.set_title('K′ energies: the same nine points, before / after',loc='left',fontsize=12,weight='bold',pad=16)
a.legend(loc='center left',bbox_to_anchor=(.03,.64),frameon=False,ncols=2);a.grid(axis='y',color='#e4eaf1')
for x,N in [(1,3),(4,4),(7,6)]:a.text(x,-.135,f'N = {N}',transform=a.get_xaxis_transform(),ha='center',fontsize=10)
for x in (2.5,5.5):a.axvline(x,color='#e4eaf1',lw=1)
fig.text(.535,.12,'A = (0.31, 0.27) · B = (0.11, 0.43) · C = (−0.31, −0.27)\nSix central ordered energies at each fractional momentum.',fontsize=9.5,color='#485a70')
fig.subplots_adjust(left=.075,right=.97,top=.77,bottom=.28)
fig.text(.075,.04,'Sampled agreement is not an infinite-cutoff error bound, an exact magic-angle determination or physical validation.',fontsize=10,color='#485a70')
for ext in ('png','svg'):fig.savefig(ROOT/('response_review.'+ext),dpi=180,facecolor=fig.get_facecolor())
(ROOT/'FIGURE.json').write_text(json.dumps({'source_sha256':{'../variant_controls_review/PROBES.json':hashlib.sha256(old_path.read_bytes()).hexdigest(),**{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['PROBES.json','REPLAY_CHIRAL_CONTROL.json']}},'scan_rows':16,'before_after_pairs':9,'scope':'No interpolating curve; all sampled rows shown. Lines on right connect revisions of the same point, not a parameter path.'},indent=2)+'\n')
print('Rendered 16 scan rows and nine matched K-prime before/after pairs.')
