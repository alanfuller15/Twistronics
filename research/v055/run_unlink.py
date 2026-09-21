"""Fresh-only lower unlink window, with retained roots and full-chart searches."""
import argparse,json,time
from pathlib import Path
from dataclasses import asdict,replace
import numpy as np
from lower_case import CASES
from lower_fold import locate
from fold_character import check
from local_domain import bounded_node,inside_margin,boundary_minimum,gap_objective,require_positive_agreement
from measure import Sample,require,geometry
from pair_measure import refined_pair
from boundary_audit import seeds as boundary_seeds
from checkpoints import save_json
from protocol import frozen_protocol,match
ROOT=Path(__file__).resolve().parent

def anchor_join(engine,N,nodes):
    a=json.loads((ROOT/'anchors'/f'unlink_{engine}_N{N}.json').read_text())
    require(a['status']=='ACCEPT' and a['kinetic']=='lab_nn_full' and a['engine']==engine and a['N']==N,'invalid unlink anchor')
    p=CASES['lower_unlink']['p']
    require(all(a['state'][k]==getattr(p,k) for k in ['A','B','T','phi','ratio','theta','eps']),'anchor state mismatch')
    require(a['geometry']==('linear' if engine=='bm_lab' else 'exact'),'anchor geometry mismatch')
    require(all(a['nodes'][k]['index']==2 for k in ['L1','L2']),'anchor gap mismatch')
    return match(nodes,[a['nodes'][k] for k in ['L1','L2']])

def run(engine,N,path):
    if path.exists(): raise ValueError('refusing to overwrite a recorded window')
    protocol=frozen_protocol();c=CASES['lower_unlink']
    if N==6:
        from unlink_acceptance import validate
        for e in ['bm_lab','ref_lab']: validate(ROOT/'results'/f'lower_unlink_{e}_N4.json',protocol)
    r=dict(status='RUNNING',scope='FULL_CHART_LOWER_GAP_SEARCH',engine=engine,N=N,geometry='linear' if engine=='bm_lab' else 'exact',kinetic='lab_nn_full',case='lower_unlink',protocol_sha256=protocol,definition={**c,'p':asdict(c['p'])},states=[],charges=[],open_checks=[])
    path.parent.mkdir(exist_ok=True);save_json(path,r)
    event=locate(engine,N,c);r['event']=event
    require(inside_margin(event['f'],c['box'])>.005,'fold outside chart')
    r['nondegeneracy']=check(engine,N,r['case'],r)
    r['v044_lower_root_join']=anchor_join(engine,N,event['initial_nodes']);save_json(path,r)
    print(engine,N,'FOLD',event['parameter'],event['f'],flush=True)
    near=event['parameter']+c['delta'];after=event['parameter']-c['delta']
    require(c['gapped_at']<after<event['parameter']<near<c['pair_at'],'unlink ordering')
    seeds=[n['f'] for n in event['initial_nodes']]
    a=json.loads((ROOT/'anchors'/f'unlink_{engine}_N{N}.json').read_text())
    flat=[a['nodes'][k]['f'] for k in ['F1','F3']]
    for T in np.linspace(c['pair_at'],near,9):
        s=Sample(engine,N,replace(c['p'],T=float(T)))
        nodes=[bounded_node(s,f,2,c['box']) for f in seeds]
        sep=float(np.linalg.norm(np.array(nodes[0]['f'])-nodes[1]['f']))
        jump=max(float(np.linalg.norm(np.array(n['f'])-f)) for n,f in zip(nodes,seeds))
        require(sep>.001 and jump<.06,'unresolved lower pair or root jump')
        flat_nodes=[bounded_node(s,f,3,c['box']) for f in flat];flat=[n['f'] for n in flat_nodes]
        offsets=[geometry(np.array(flat[0]),np.array(flat[1]),np.array(n['f'])) for n in nodes]
        r['states'].append(dict(T=float(T),nodes=nodes,separation=sep,max_jump=jump,flat_nodes=flat_nodes,lower_to_flat_segment=offsets,diagnostics=s.metrics))
        save_json(path,r);seeds=[n['f'] for n in nodes]
        print(engine,N,'ROOT_STATE',len(r['states']),sep,flush=True)
    require(r['states'][-1]['separation']<r['states'][0]['separation'],'pair does not approach fold')
    for row in [r['states'][0],r['states'][-1]]:
        s=Sample(engine,N,replace(c['p'],T=row['T']));radius=min(.002,row['separation']/8)
        measurement=refined_pair(s,[n['f'] for n in row['nodes']],2,radius)
        require(measurement['label']=='OPPOSITE','lower pair is not opposite at charge station')
        r['charges'].append(dict(T=row['T'],measurement=measurement,root_join=match(measurement['nodes'],row['nodes'])));save_json(path,r)
        print(engine,N,'CHARGE',row['T'],measurement['label'],flush=True)
    for T in [after,c['gapped_at']]:
        s=Sample(engine,N,replace(c['p'],T=float(T)));trials=[]
        for grid in [18,24]:
            row=s.minimum(2,grid,extra=boundary_seeds(s,2,[event['f']]))
            require(row['minimum']['gap']>1e-5,'lower full-chart opening unresolved');trials.append(row)
        require(abs(trials[0]['minimum']['gap']-trials[1]['minimum']['gap'])<.01,'lower opening fails grid refinement')
        fn=gap_objective(s,2);boundary=[boundary_minimum(fn,c['box'],grid) for grid in [24,48]]
        require_positive_agreement(boundary,'boundary')
        r['open_checks'].append(dict(T=float(T),trials=trials,boundary=boundary,diagnostics=s.metrics));save_json(path,r)
        print(engine,N,'OPEN',T,trials[-1]['minimum']['gap'],flush=True)
    r['status']='ACCEPT';save_json(path,r)
    from unlink_acceptance import validate
    validate(path,protocol)
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True);p.add_argument('--N',type=int,choices=[4,6],required=True);a=p.parse_args()
    path=ROOT/'results'/f'lower_unlink_{a.engine}_N{a.N}.json'
    if path.exists(): raise SystemExit('refusing to overwrite a recorded window')
    start=time.time()
    try:r=run(a.engine,a.N,path)
    except Exception as error:
        r=json.loads(path.read_text()) if path.exists() else dict(engine=a.engine,N=a.N,case='lower_unlink')
        r.update(status='REJECTED',error=type(error).__name__+': '+str(error))
    r['seconds']=time.time()-start;save_json(path,r);print('FINAL',a.engine,a.N,r['status'],r.get('error'),flush=True)
    raise SystemExit(int(r['status']!='ACCEPT'))
