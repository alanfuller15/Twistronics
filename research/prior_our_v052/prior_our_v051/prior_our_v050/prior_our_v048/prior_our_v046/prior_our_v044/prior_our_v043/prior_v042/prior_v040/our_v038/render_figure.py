"""Scientific figure from accepted results; does not interpolate gap proofs."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
def read(name):
    r=json.loads((ROOT/'results'/name).read_text())
    if r['status']!='ACCEPT':raise RuntimeError('Unaccepted '+name)
    return r
def main():
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,(a,b)=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    combinations=[('original',4),('original',6),('partner',4),('partner',6)]
    colors={'original':'#1864ab','partner':'#d9480f'};flat=[];upper=[]
    for i,(engine,N) in enumerate(combinations):
        x1=read(f'upper_ann_{engine}_N{N}.json')['event']['parameter'];x2=read(f'flat_birth_{engine}_N{N}.json')['event']['parameter']
        a.plot([x1,x2],[i,i],c=colors[engine],lw=1.5,alpha=.6)
        a.scatter(x1,i,c=colors[engine],marker='x',s=70,label='Upper-pair annihilation' if i==0 else None)
        a.scatter(x2,i,c=colors[engine],marker='o',s=45,label='Flat-pair birth' if i==0 else None)
        a.scatter(1.04,i,c='#2b8a3e',marker='D',s=45,label='Measured gapped state' if i==0 else None)
        r=read(f'boundary_bridge_{engine}_N{N}.json');flat.append(r['gaps']['flat']['new_minimum']);upper.append(r['gaps']['upper']['new_minimum'])
    a.set(yticks=range(4),yticklabels=[f'{e}, N={n}' for e,n in combinations],ylim=(3.7,-.8),xlabel='AA / AB tunneling ratio',title='A  Located events are separated')
    a.legend(loc='lower left',fontsize=8);a.set_ylim(4.8,-.8)
    x=np.arange(4);b.bar(x-.18,flat,width=.34,color='#2b8a3e',label='Flat gap');b.bar(x+.18,upper,width=.34,color='#862e9c',label='Upper gap')
    for pos,vals in [(x-.18,flat),(x+.18,upper)]:
        for xx,v in zip(pos,vals):b.text(xx,v+.025,f'{v:.3f}',ha='center',fontsize=8)
    b.set(xticks=x,xticklabels=[f'{e}\nN={n}' for e,n in combinations],ylabel='Refined gap minimum (meV)',title='B  Positive gaps at ratio 1.04',ylim=(0,max(flat+upper)*1.24));b.legend(loc='upper right',fontsize=9)
    fig.suptitle('An earlier gapped endpoint on the v032 ratio leg',fontsize=15)
    fig.supxlabel('A = -0.35, B = -0.4, T = -1.8, strain direction = 80°\nLines join located events; only the marked intermediate state is tested as gapped here.',fontsize=9)
    out=ROOT/'figures';out.mkdir(exist_ok=True);fig.savefig(out/'earlier_endpoint.png',dpi=180);plt.close(fig)
if __name__=='__main__':main()
