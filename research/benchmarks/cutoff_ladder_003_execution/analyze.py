import json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(sys.argv[1]);rows=json.loads((p/'MAP.json').read_text())['samples'];s={'implementation_commit':json.loads((p/'BATCH.json').read_text())['implementation_commit'],'independent_review':'PENDING','comparisons':{},'cutoffs':{}}
for link in ['ab','bc']:
 m=[r['comparisons'][link] for r in rows];s['comparisons'][link]={'max_pair_angle_deg':max(max(r['metrics']['pair']['principal_angles_degrees']) for r in m),'max_four_angle_deg':max(max(r['metrics']['four']['principal_angles_degrees']) for r in m),'min_pair_in_four':min(r['minimum_pair_weight_in_four'] for r in m),'max_abs_upper_gap_change_microeV':max(abs(r['metrics']['upper_gap_change_b_minus_a_microeV']) for r in m)}
for k,link,alias in [('a','ab','a'),('b','ab','b'),('c','bc','b')]:
 gaps=[1000*r['comparisons'][link]['metrics']['pair'][alias+'_external_gaps_meV'][1] for r in rows];i=int(np.argmin(gaps));s['cutoffs'][k]={'minimum_sampled_upper_gap_microeV':min(gaps),'minimum_offset':i-8,'gaps_microeV':gaps}
s['max_residual_meV']=max(max(r['eigenpair_residual_meV'].values()) for r in rows);s['max_nested_residual_meV']=max(max(r['nested_residual_meV'].values()) for r in rows)
(p/'SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n')
fig,axs=plt.subplots(2,1,figsize=(10,9),layout='constrained');colors=['#1964ad','#d15b0b','#007c65']
for k,d,c in zip(['a','b','c'],[196,308,444],colors):axs[0].plot(range(-8,9),s['cutoffs'][k]['gaps_microeV'],'-o',label=f'{k}: {d} matrix dimension',color=c)
axs[0].set(ylabel='Upper pair gap (μeV)',title='Does the narrow gap persist as the model grows?');axs[0].legend()
for link,c in zip(['ab','bc'],colors):axs[1].plot(range(-8,9),[max(r['comparisons'][link]['metrics']['pair']['principal_angles_degrees']) for r in rows],'-o',label=f'{link[0]} → {link[1]}: selected pair',color=c)
axs[1].set(ylabel='Largest pair angle (degrees)',ylim=(0,90),title='How much does the selected pair change?');axs[1].legend()
for ax in axs:ax.grid(alpha=.2);ax.set_xlabel('Momentum offset (steps of 1/131072 in x; k = xG₁ + yG₂)');ax.set_xticks([-8,-4,0,4,8])
fig.suptitle('Three nested models, the same 17 momentum points',fontsize=18,fontweight='bold');fig.supxlabel('Dots are computed samples; lines guide the eye. Post-execution review pending.',fontsize=11);fig.savefig(p/'cutoff-ladder.png',dpi=160);plt.close(fig);print(json.dumps(s))
