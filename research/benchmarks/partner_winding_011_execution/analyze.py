"""Derive SUMMARY.json and partner-winding.png from a replayed PARTNER-WINDING-011 output (no eigensolves)."""
import json,sys
from fractions import Fraction
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(sys.argv[1]);review=sys.argv[2] if len(sys.argv)>2 else 'PENDING'
rows=json.loads((p/'MAP.json').read_text())['samples'];batch=json.loads((p/'BATCH.json').read_text());hol=json.loads((p/'HOLONOMY.json').read_text())
ALIAS={'a':('ab','a'),'b':('ab','b'),'c':('bc','b')}
def gap(r,k):l,al=ALIAS[k];return 1000*r['comparisons'][l]['metrics']['pair'][al+'_external_gaps_meV'][1]
by={r['label']:r for r in rows};loop=[r for r in rows if r['label'].startswith('loop_')]
s={'implementation_commit':batch['implementation_commit'],'independent_review':review,'points':len(rows),'eigensolver_starts':batch['eigensolver_starts'],
 'upper_gap_at_fitted_nodes_microeV':{n:{k:gap(by['fitted_node_'+n],k) for k in 'abc'} for n in 'bc'},
 'loop':{'points':len(loop),'min_upper_gap_microeV':{k:min(gap(r,k) for r in loop) for k in 'abc'},'max_upper_gap_microeV':{k:max(gap(r,k) for r in loop) for k in 'abc'}},
 'holonomy':hol['cutoffs'],
 'max_residual_meV':max(max(r['eigenpair_residual_meV'].values()) for r in rows),'max_nested_residual_meV':max(max(r['nested_residual_meV'].values()) for r in rows),
 'claim_ceiling':'Floating-point finite-cutoff evidence: small gaps at fitted rational node points and a -1 real-gauge holonomy on one resolved loop, in all three cutoffs. The b/c node separation is below this fit resolution. Not an interval certificate; no infinite-cutoff claim.'}
(p/'SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n')

# Retained upstream values (cited, not recomputed here): smallest sampled upper gap at cutoff c per iteration.
HISTORY=[('loop around R1\n(008)',501.9861609235079),('17×15, 2⁻¹¹\n(009)',41.988942923026684),('9×9, 2⁻¹⁵\n(010)',1.8027690793118722),('fitted node\n(011)',s['upper_gap_at_fitted_nodes_microeV']['c']['c'])]
INK='#0b0b0b';INK2='#52514e';CAT={'a':'#2a78d6','b':'#eb6834','c':'#1baf7a'}
plt.rcParams.update({'font.size':11,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK2,'ytick.color':INK2,'axes.edgecolor':'#c9c8c3'})
fig,ax=plt.subplots(1,3,figsize=(17,5.8),layout='constrained')
# 1: geometry of loop and nodes, in units of 2^-20 relative to the c node
c0=[Fraction(v) for v in by['fitted_node_c']['center']];u=2**16
def rel(r):return [float((Fraction(v)-c0[i])*u) for i,v in enumerate(r['center'])]
L=np.array([rel(r) for r in loop]);a=ax[0];a.plot(*np.vstack([L,L[:1]]).T,'-',color='#c9c8c3',lw=2,zorder=1)
sc=a.scatter(L[:,0],L[:,1],c=[gap(r,'c') for r in loop],cmap='Blues',vmin=0,s=70,edgecolors='white',linewidths=1.5,zorder=2);cb=fig.colorbar(sc,ax=a,shrink=.8);cb.set_label('c upper gap on loop (µeV)');cb.outline.set_visible(False)
for n,mk in [('b','x'),('c','+')]:
 q=rel(by['fitted_node_'+n]);a.plot(*q,mk,color=CAT[n],ms=13,mew=3,zorder=3,label=f'fitted node {n}')
a.annotate('start (counterclockwise)',L[0],xytext=(-4,-16),textcoords='offset points',ha='left',color=INK2,fontsize=9)
a.set(aspect='equal',xlim=(-1.4,1.4),ylim=(-1.4,1.4),xlabel='x − partner node c (units of 2⁻¹⁶)',ylabel='y − partner node c (units of 2⁻¹⁶)',title='32-point loop around the fitted partner nodes');a.legend(frameon=False,loc='upper right',fontsize=9)
# 2: how the smallest c gap fell with each compute iteration
a=ax[1];y=[v for _,v in HISTORY];a.plot(range(4),y,'-',color='#c9c8c3',lw=2,zorder=1);a.plot(range(4),y,'o',color=CAT['c'],ms=10,mec='white',mew=1.5,zorder=2)
for i,v in enumerate(y):a.annotate(f'{v:.3g} µeV',(i,v),xytext=(8,4),textcoords='offset points',fontsize=10,color=INK)
a.set(yscale='log',xticks=range(4),xlim=(-.4,3.8),ylabel='Smallest computed upper gap, cutoff c (µeV)',title='Zooming in on the partner in region R1');a.set_xticklabels([h for h,_ in HISTORY],fontsize=10);a.grid(alpha=.25,which='both')
# 3: holonomy determinant of band hi around the loop
a=ax[2]
for k in 'abc':
 d=s['holonomy'][k]['hi']
 a.bar(k,d['determinant'],color=CAT[k],width=.55)
 a.annotate(f"{d['determinant']:+.3f}\nsign {d['sign']:+d}",(k,d['determinant']),xytext=(0,6 if d['determinant']>0 else -30),textcoords='offset points',ha='center',fontsize=10,color=INK)
a.axhline(0,color=INK2,lw=.8);a.set(ylim=(-1.15,1.55),ylabel='det of loop holonomy, band hi',title='Does band hi come back with its sign flipped?')
a.text(.98,.97,f"steps valid: min overlap ≥ {min(s['holonomy'][k]['hi']['min_step_singular_value'] for k in 'abc'):.2f} (required 0.5)\nfour-state group: +1 in a, b, c",transform=a.transAxes,fontsize=9,color=INK2,ha='right',va='top')
fig.suptitle('The partner node in region R1: near-zero gap at the fitted point, sign flip around it',fontsize=15,fontweight='bold')
fig.supxlabel(f'35 computed momentum points × 3 nested cutoffs (middle panel cites retained minima of 008–010). Momentum space, not time. Floating-point evidence, not an interval certificate. Independent review: {review}.',fontsize=9.5,color=INK2)
fig.savefig(p/'partner-winding.png',dpi=150,facecolor='#fcfcfb');plt.close(fig)
print(json.dumps({'node_gaps':s['upper_gap_at_fitted_nodes_microeV'],'hi_signs':{k:s['holonomy'][k]['hi']['sign'] for k in 'abc'}}))
