"""Static scientific figure using only reconciled saved results and arrays."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parent
S=json.loads((ROOT/'SUMMARY.json').read_text());assert S['all_checks_pass']
D={n:json.loads((ROOT/(n.upper()+'.json')).read_text()) for n in ['bm','ref']}
z=np.load(ROOT/'BM.npz')
c=next(c for c in D['bm']['cases'] if c['key']=='D38_fine_r0.003');key=c['key']
blue='#2769cc';orange='#d66c31';navy='#182c48';green='#167666';purple='#8660b8';gray='#627084'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.labelcolor':navy,'text.color':navy,
                     'axes.edgecolor':'#bcc7d5','xtick.color':gray,'ytick.color':gray,'axes.spines.top':False,'axes.spines.right':False})
fig=plt.figure(figsize=(16,10.7),facecolor='#f7f9fc')
gs=fig.add_gridspec(2,2,left=.07,right=.96,bottom=.13,top=.81,hspace=.63,wspace=.27,height_ratios=[1.1,.85])
ax=fig.add_subplot(gs[0,0]);liftax=fig.add_subplot(gs[0,1]);tableax=fig.add_subplot(gs[1,0]);gapax=fig.add_subplot(gs[1,1])
fig.text(.07,.955,'TWISTRONICS  /  R1  /  N8',fontsize=12,fontweight='bold',color=blue)
fig.text(.07,.904,'The order of two loops changes the frame charge',fontsize=25,fontweight='bold')
fig.text(.07,.863,'Local three-band diagnostic  ·  D = 38 and 39 meV  ·  two implementations  ·  two radii  ·  two meshes',fontsize=12,color=gray)

# A: paths in the actual fractional momentum coordinates.
region=next(r for r in D['bm']['regions'] if r['D_meV']==38 and r['mesh']=='fine');bounds=np.array(region['bounds'])
ax.add_patch(Rectangle(bounds[0],*(bounds[1]-bounds[0]),facecolor='#eaf0f8',edgecolor='#bac9dd',linewidth=1))
for name,color in [('A',blue),('B',orange)]:
    p=np.array(c[name]['vertices']);ax.plot(p[:,0],p[:,1],color=color,lw=1.7)
    center=np.array(c['flat_q_root' if name=='A' else 'upper_root']['f'])
    ax.scatter(*center,s=48,color=color,edgecolor='white',linewidth=1,zorder=5)
    start=np.array(c['base_f']);end=p[1]
    a=start+.48*(end-start);b=start+.65*(end-start)
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1.8,'color':color})
base=np.array(c['base_f']);ax.scatter(*base,s=45,color=navy,zorder=6)
ax.annotate('Common base',base,xytext=(7,8),textcoords='offset points',fontsize=10)
q=np.array(c['flat_q_root']['f']);u=np.array(c['upper_root']['f'])
ax.annotate('A  ·  flat-gap node\ncharge +k',q,xytext=(-8,-33),textcoords='offset points',ha='right',color=blue,fontsize=11,fontweight='bold')
ax.annotate('B  ·  upper-gap node\ncharge +i',u,xytext=(8,12),textcoords='offset points',ha='left',color=orange,fontsize=11,fontweight='bold')
ax.set_xlim(bounds[0,0]-.009,bounds[1,0]+.007);ax.set_ylim(bounds[0,1]-.016,bounds[1,1]+.011)
ax.set_xlabel('Fractional momentum $f_1$');ax.set_ylabel('Fractional momentum $f_2$')
ax.set_title('A   Two loops with one basepoint',loc='left',fontsize=14,fontweight='bold',pad=19)
ax.text(0,1.015,'D = 38 meV, radius 0.003; shaded region has a valid three-band chart.',transform=ax.transAxes,fontsize=9,color=gray)
ax.grid(alpha=.18)

# B: actual stored lift, with each path leg rescaled to one plotting unit.
path=z[key+'_commutator_quaternion_path'];na=len(z[key+'_A_Q'])-1;nb=len(z[key+'_B_Q'])-1
lengths=[na,nb,na,nb];xx=[0.]
for j,n in enumerate(lengths):xx.extend(j+np.arange(1,n+1)/n)
assert len(xx)==len(path)
for j,label in enumerate(['A','B',r'$A^{-1}$',r'$B^{-1}$']):
    liftax.axvspan(j,j+1,color=blue if j%2==0 else orange,alpha=.065)
    liftax.text(j+.5,1.18,label,ha='center',fontsize=12,color=blue if j%2==0 else orange)
for j,(label,color,lw) in enumerate([('w',navy,2.4),('x',blue,1.3),('y',green,1.3),('z',purple,1.3)]):
    liftax.plot(xx,path[:,j],label=label,color=color,lw=lw)
liftax.scatter([0,4],[1,-1],s=55,color=navy,zorder=6)
liftax.annotate('−1',xy=(4,-1),xytext=(-18,12),textcoords='offset points',fontweight='bold',fontsize=15)
liftax.axhline(0,color='#a5b0bf',lw=.7);liftax.set_xlim(-.04,4.04);liftax.set_ylim(-1.15,1.35)
liftax.set_xticks([0,1,2,3,4]);liftax.set_yticks([-1,0,1]);liftax.set_ylabel('Unit-quaternion components')
liftax.set_xlabel('Traversal progress (each leg rescaled equally)')
liftax.set_title('B   Following the commutator returns −1',loc='left',fontsize=14,fontweight='bold',pad=19)
liftax.text(0,1.015,'Saved Spin(3) lift of A → B → A⁻¹ → B⁻¹; same D38 case as panel A.',transform=liftax.transAxes,fontsize=9,color=gray)
liftax.legend(loc='lower left',ncol=4,frameon=False,fontsize=10,handlelength=1.5)

# C: all 16 cases; every table row represents both meshes and both radii.
tableax.set_axis_off();tableax.set_title('C   The result survives every planned check',loc='left',fontsize=14,fontweight='bold',pad=22)
tableax.text(0,1.015,'Signed labels in the recorded base-frame convention; 4 cases per row.',transform=tableax.transAxes,fontsize=9,color=gray)
rows=[]
for value in [38,39]:
    for engine in ['bm','ref']:
        cases=[r for r in D[engine]['cases'] if r['D_meV']==value]
        labels=[]
        for name in ['A','B','AB','BA','commutator']:
            found={r['words'][name]['accepted_label'] for r in cases};assert len(found)==1
            labels.append(next(iter(found)).replace('-','−'))
        rows.append([f'{value} / {engine.upper()}',*labels,f'{sum(r["diagnostics_pass"] for r in cases)}/4'])
table=tableax.table(cellText=rows,colLabels=['D / engine','A','B','AB','BA','Commutator','Pass'],cellLoc='center',bbox=[0,.16,1,.8],colWidths=[.24,.09,.09,.09,.09,.23,.12])
table.auto_set_font_size(False);table.set_fontsize(11)
for (r,col),cell in table.get_celld().items():
    cell.set_edgecolor('#dce3ec');cell.set_linewidth(.6)
    cell.set_facecolor('#e7eef8' if r==0 else ('white' if r%2 else '#f0f4f9'))
    if r==0:cell.set_text_props(weight='bold',color=navy)
    if col==5 and r>0:cell.set_text_props(color=green,weight='bold')
tableax.text(0,-.01,'AB = +j, BA = −j.  Their order differs by the central element −1.',transform=tableax.transAxes,fontsize=10,fontweight='bold')

# D: minimum four-gap interval estimates, without combining incompatible units.
for engine,color,marker in [('bm',blue,'o'),('ref',orange,'x')]:
    vals=[min(r['A']['minimum_gap_lower_meV'],r['B']['minimum_gap_lower_meV']) for r in D[engine]['cases']]
    gapax.plot(np.arange(8),vals,color=color,marker=marker,ms=7,lw=1 if engine=='bm' else 0,label=engine.upper())
gapax.axhline(.001,color='#a45a61',linestyle='--',lw=1,label='Acceptance margin')
gapax.set_yscale('log');gapax.set_ylabel('Minimum contour gap lower estimate (meV)')
gapax.set_xticks(range(8),['C\n.003','C\n.0015','F\n.003','F\n.0015']*2,fontsize=9)
gapax.axvline(3.5,color='#c5cfdd',lw=.8)
gapax.text(.22,-.27,'D = 38 meV',transform=gapax.transAxes,ha='center',fontsize=10)
gapax.text(.78,-.27,'D = 39 meV',transform=gapax.transAxes,ha='center',fontsize=10)
gapax.set_title('D   Every sampled contour clears its gap gate',loc='left',fontsize=14,fontweight='bold',pad=22)
gapax.text(0,1.015,'C/F = coarse/fine mesh; values below ticks are loop radii.',transform=gapax.transAxes,fontsize=9,color=gray)
gapax.grid(axis='y',alpha=.2);gapax.legend(frameon=False,fontsize=9,loc='center right')

fig.text(.07,.055,f'18 analytic controls pass   ·   32 primitive + 48 composite loops   ·   whole-region chart lower estimate ≥ {S["minimum_region_chart_smin_lower"]:.3f}',fontsize=11,fontweight='bold',color=green)
fig.text(.07,.025,'Finite-cutoff model evidence. Temporal braiding and Euler-class change remain untested here. D sets layer potentials ±D; strain is fixed.',fontsize=10,color=gray)
for ext in ['png','svg']:fig.savefig(ROOT/('three_band.'+ext),dpi=180,facecolor=fig.get_facecolor())
print('Figure generated from SUMMARY.json, BM/REF.json, and BM.npz.')
