"""Check seed basins and bracket geometry before freezing the replay plan."""
import json
from pathlib import Path
from models import State
from measure import Sample,geometry

ROOT=Path(__file__).resolve().parent
def run():
    rows=[];pilots=json.loads((ROOT/'results/discovery.json').read_text())
    for engine in ['bm_lab','ref_lab']:
        pilot=next(r for r in pilots if r['engine']==engine)
        for ratio in [.99,1.]:
            s=Sample(engine,4,State(ratio=ratio))
            u=[s.node(r['f'],4) for r in pilot['U']]
            x=[s.node(r['f'],5) for r in pilot['next']]
            rows.append(dict(engine=engine,N=4,ratio=ratio,U=u,next=x,geometry=[geometry(u[0]['f'],u[1]['f'],q['f']) for q in x]))
    return rows

if __name__=='__main__':
    r=run();(ROOT/'results/preflight.json').write_text(json.dumps(r,indent=2)+'\n')
    for q in r:print(q['engine'],q['ratio'],'X1 offset',q['geometry'][0]['offset'])
