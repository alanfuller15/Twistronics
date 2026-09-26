"""Derive SUMMARY.json and partner-loops.png from a replayed PARTNER-LOOPS-008 output (no eigensolves)."""
import json,sys
from fractions import Fraction
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(sys.argv[1]);review=sys.argv[2] if len(sys.argv)>2 else 'PENDING';ROOT=Path(__file__).resolve().parents[3]
rows=json.loads((p/'MAP.json').read_text())['samples'];batch=json.loads((p/'BATCH.json').read_text());H=json.loads((p/'HOLONOMY.json').read_text())
spec=json.loads((ROOT/'research/benchmarks/partner_loops_008/SPEC.json').read_text())
ALIAS={'a':('ab','a'),'b':('ab','b'),'c':('bc','b')}
def gaps(r,k):l,al=ALIAS[k];return r['comparisons'][l]['metrics']['pair'][al+'_external_gaps_meV']
def reading(sg):
 lo,hi,pr=sg['lo'],sg['hi'],sg['selected_pair']
 if None in (lo,hi,pr):return 'unresolved'
 return {(1,1,1):'no odd node count',(1,-1,-1):'odd hi/hi+1 node count',(-1,1,-1):'odd lo-1/lo node count',(-1,-1,1):'odd lo/hi (in-pair) node count'}.get((lo,hi,pr),'mixed parity')
s={'implementation_commit':batch['implementation_commit'],'independent_review':review,'points':len(rows),'eigensolver_starts':batch['eigensolver_starts'],'loops':{}}
for L in spec['loops']:
 rs=[rows[i] for i in L['point_indices']];h=H['loops'][L['name']]['cutoffs']
 s['loops'][L['name']]={'points':len(rs),'depth10_box_x0_y0_x1_y1':L['depth10_box_x0_y0_x1_y1'],'cutoffs':{k:{'signs':{g:h[k][g]['sign'] for g in h[k]},'determinants':{g:h[k][g]['determinant'] for g in h[k]},'min_step_singular_value':min(h[k][g]['min_step_singular_value'] for g in h[k]),'reading':reading({g:h[k][g]['sign'] for g in h[k]}),'min_upper_gap_meV_on_loop':min(gaps(r,k)[1] for r in rs),'min_lower_gap_meV_on_loop':min(gaps(r,k)[0] for r in rs)} for k in 'abc'}}
s['max_residual_meV']=max(max(r['eigenpair_residual_meV'].values()) for r in rows);s['max_nested_residual_meV']=max(max(r['nested_residual_meV'].values()) for r in rows)
s['claim_ceiling']='Floating-point finite-cutoff loop holonomies: parities of node counts inside each loop, not node positions or interval certificates.'
(p/'SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n')
INK='#0b0b0b';INK2='#52514e';COL={'odd hi/hi+1 node count':'#eb6834','odd lo-1/lo node count':'#1964ad','no odd node count':'#8a8984'}
plt.rcParams.update({'font.size':11,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK2,'ytick.color':INK2,'axes.edgecolor':'#c9c8c3'})
part=json.loads((ROOT/'research/benchmarks/parallel_domain_006_execution/PARTITION.json').read_text());un=[c for st in part.values() for c in st['unresolved']]
fig,ax=plt.subplots(figsize=(10.5,9.5),layout='constrained')
for d,x,y in un:ax.add_patch(plt.Rectangle((x/2**d,y/2**d),1/2**d,1/2**d,color='#52514e',lw=0))
for L in spec['loops']:
 x0,y0,x1,y1=[v/1024 for v in L['depth10_box_x0_y0_x1_y1']];rd=s['loops'][L['name']]['cutoffs']['c']['reading'];sg=s['loops'][L['name']]['cutoffs']['c']['signs']
 pad=.012;ax.add_patch(plt.Rectangle((x0-pad,y0-pad),x1-x0+2*pad,y1-y0+2*pad,fill=False,ec=COL[rd],lw=2.5))
 ax.annotate(f"{L['name'].split('_')[0]}{' (known node)' if 'control' in L['name'] else ''}\nlo {sg['lo']:+d}, hi {sg['hi']:+d}, pair {sg['selected_pair']:+d}\n{rd}",(x1+pad,(y0+y1)/2),xytext=(8,-14 if L['name'].startswith('R4') else (10 if L['name'].startswith('R2') else 0)),textcoords='offset points',va='center',fontsize=10,color=INK)
ax.plot([],[],'s',color='#52514e',label=f'cutoff-a unresolved depth-10 cells ({len(un)} cells, {100*sum(4.0**-d for d,_,_ in un):.3f}% of area; the rest is accepted by the cutoff-a external-gap partition)')
for k,v in COL.items():
 if any(L['cutoffs']['c']['reading']==k for L in s['loops'].values()):ax.plot([],[],'-',color=v,lw=2.5,label=f'loop: {k}')
ax.set(xlim=(0,1),ylim=(0,1),aspect='equal',xlabel='x (fractional, k = x G₁ + y G₂)',ylabel='y (fractional)',title='Where are the band touchings? Loop signs around every unresolved region (model c; a and b agree)')
ax.legend(frameon=False,loc='lower left',fontsize=9.5)
fig.supxlabel(f'Loops are drawn enlarged for visibility; actual loops follow each cluster box at step 1/2048.\n264 computed points × 3 cutoffs. Momentum space, not time. Independent review: {review}.',fontsize=9,color=INK2)
fig.savefig(p/'partner-loops.png',dpi=140,facecolor='#fcfcfb');plt.close(fig)
print(json.dumps({n:v['cutoffs']['c']['reading'] for n,v in s['loops'].items()}))
