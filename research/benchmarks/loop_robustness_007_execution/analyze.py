"""Derive summary and plot from strict-replayed retained states; zero eigensolves."""
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);batch=json.loads((p/'BATCH.json').read_text());h=json.loads((p/'HOLONOMY.json').read_text());rows=json.loads((p/'MAP.json').read_text())['samples']
s={**batch,'scope':h['scope'],'loops':{},'max_nested_residual_meV':max(max(r['nested_residual_meV'].values()) for r in rows),'max_eigenpair_residual_meV':max(max(r['eigenpair_residual_meV'].values()) for r in rows),'max_job_seconds':max(json.loads(f.read_text())['elapsed_seconds'] for f in p.glob('job*/RECEIPT.json')),'regression':json.loads((p/'REGRESSION.json').read_text())}
for name,l in h['loops'].items():
 s['loops'][name]={'vertices':len(l['geometry']['point_indices']),'cutoffs':{k:{g:{key:v[key] for key in ['sign','valid','raw_determinant','polar_determinant','min_step_singular_value','minimum_sampled_external_gap_meV','bands_zero_based']} for g,v in c.items()} for k,c in l['cutoffs'].items()}}
(p/'SUMMARY.json').write_text(json.dumps(s,indent=2,sort_keys=True,allow_nan=False)+'\n')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,2,figsize=(12,4.8),layout='constrained');colors={'a':'#2a78d6','b':'#eb6834','c':'#1baf7a'}
for k in 'abc':
 ns=[16,32,64];ds=[s['loops'][f'center_c_r1_{n}']['cutoffs'][k]['hi']['raw_determinant'] for n in ns]
 ax[0].plot(ns,ds,'o-',label=k,color=colors[k]);ax[0].annotate(f'{ds[-1]:+.3f}',(64,ds[-1]),xytext=(5,8 if k!='b' else -15),textcoords='offset points')
ax[0].axhline(0,lw=.8,color='#888');ax[0].set(xticks=[16,32,64],xlabel='Vertices on original-radius square',ylabel='Product of real overlaps, band hi',title='The b/c negative sign survives finer sampling',ylim=(-1.15,1.15),xlim=(12,75));ax[0].legend(title='Cutoff',frameon=False)
from fractions import Fraction as F
origin=list(map(F,h['loops']['center_c_r1_64']['geometry']['center']));scale=2**20
for name,color,label in [('center_c_r1_64','#555','original radius: b/c −1'),('center_c_rhalf_32','#1baf7a','half radius: b/c −1'),('offnode_xplus4r_32','#2a78d6','off-node control: b/c +1')]:
 idx=h['loops'][name]['geometry']['point_indices'];pts=[[float((F(v)-origin[j])*scale) for j,v in enumerate(rows[i]['center'])] for i in idx];pts.append(pts[0]);ax[1].plot([x[0] for x in pts],[x[1] for x in pts],'-',color=color,label=label)
ax[1].plot(0,0,'+',color='#1baf7a',ms=9);ax[1].set(aspect='equal',xlabel='x − rounded c candidate (units of 2⁻²⁰)',ylabel='y offset (same units)',title='Radius change and translated control');ax[1].set(ylim=(-1.4,2.5));ax[1].legend(loc='upper center',frameon=False,fontsize=9)
fig.suptitle('LOOP-ROBUSTNESS-007 • 128 momentum points, 384 eigensolves',fontsize=14)
fig.supxlabel('96 new coordinates + 32 regression repeats. Finite cutoffs; sampled numerical evidence. Independent review pending.',fontsize=9)
fig.savefig(p/'loop-robustness.png',dpi=150);plt.close(fig)
print(json.dumps({'jobs':s['jobs'],'solves':s['eigensolver_starts'],'seconds':s['summed_job_seconds'],'max_job_seconds':s['max_job_seconds'],'regression':s['regression']}))
