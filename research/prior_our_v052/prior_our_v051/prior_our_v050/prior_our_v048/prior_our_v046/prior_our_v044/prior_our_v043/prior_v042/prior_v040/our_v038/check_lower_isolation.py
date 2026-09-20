"""Global finite search below the lower remote band for its cycle interpretation."""
import argparse,json,time
from pathlib import Path
from models import State
from measure import Sample,require
from replay_second import save
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=['original','partner'],required=True);ap.add_argument('--N',type=int,choices=[4,6],required=True);a=ap.parse_args();rows=[]
    for which in ['bridge','endpoint']:
        source=json.loads((ROOT/'results'/f'{which}_{a.engine}_N{a.N}.json').read_text());require(source['status']=='ACCEPT','gapped state not accepted')
        s=Sample(a.engine,a.N,State(**source['state']));trials=[s.minimum(1,n) for n in [18,24]]
        require(min(z['minimum']['gap'] for z in trials)>1e-5,'lower remote outer gap unresolved')
        require(abs(trials[0]['minimum']['gap']-trials[1]['minimum']['gap'])<.01,'outer gap grid refinement')
        rows.append(dict(which=which,trials=trials));print(a.engine,a.N,which,trials[-1]['minimum']['gap'],flush=True)
    save(ROOT/'results'/f'outer_isolation_{a.engine}_N{a.N}.json',dict(status='ACCEPT',engine=a.engine,N=a.N,rows=rows))
