"""Plot retained sampled metrics only; never interpolate or imply area coverage."""
import argparse,json
from fractions import Fraction
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('map',type=Path);p.add_argument('output',type=Path);a=p.parse_args();m=json.loads(a.map.read_text());rows=m['samples'];x=np.array([float(Fraction(r['point']['center'][0])) for r in rows]);y=np.array([float(Fraction(r['point']['center'][1])) for r in rows]);fields=[('pair','min_singular_value','Selected pair similarity',0,1,'viridis'),('four','min_singular_value','Four-state group similarity',0,1,'viridis'),('pair','mean_added_component_weight','Pair weight in added components',0,1,'magma'),(None,'upper_gap_change_b_minus_a_microeV','Upper gap change: b − a (μeV)',None,None,'coolwarm')]
fig,axes=plt.subplots(2,2,figsize=(10,9),layout='constrained')
for ax,(group,key,title,lo,hi,cmap) in zip(axes.flat,fields):
 z=np.array([r['metrics'][group][key] if group else r['metrics'][key] for r in rows])
 if group is None:hi=max(float(abs(z).max()),1e-12);lo=-hi
 sc=ax.scatter(x,y,c=z,s=65,marker='s',edgecolors='#101820',linewidths=.3,cmap=cmap,vmin=lo,vmax=hi);ax.set_title(title);ax.set_xlabel('x, in k = xG₁ + yG₂');ax.set_ylabel('y');ax.set_aspect('equal');ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(axis='x',rotation=30);fig.colorbar(sc,ax=ax,shrink=.85)
fig.suptitle('State comparison at64 saved coordinates — sampled diagnostics\nNo interpolation, certified correspondence or cutoff-convergence claim',fontsize=12)
a.output.parent.mkdir(parents=True,exist_ok=True);fig.savefig(a.output,dpi=180);plt.close(fig)
