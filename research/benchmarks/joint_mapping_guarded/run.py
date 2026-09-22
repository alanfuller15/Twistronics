"""Frozen common-basis sensitivity batch and real carried-seed trace smoke."""
import copy
import hashlib
import json
import platform
import time
from pathlib import Path
import numpy as np
import scipy
import jm_model as m
import jm_trace as trace

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    root=m.ROOT;dest=root/'RESULTS.json'
    if dest.exists():raise FileExistsError('refusing overwrite of retained numerical results')
    plan=json.loads((root/'PLAN.json').read_text());n=plan['numerics']
    controls=json.loads((root/'CONTROLS.json').read_text())
    assert controls['status']=='ALL_GUARDED_RUNNER_CONTROLS_PASS'
    assert controls['source_hashes']==m.sources()
    assert controls['control_sha256']==sha(root/'controls.py')
    basis=json.loads((root/'BASIS.json').read_text())
    seed_path=root.parent/'joint_mapping_review/N6_CANDIDATE_SEEDS.json'
    old=json.loads(seed_path.read_text());strain=[s for s in old if s['x']['phi']==15]
    stations=[]
    for eps in n['eps']:
        matching=[s for s in strain if abs(s['x']['eps']-eps)<1e-12]
        if matching:
            seed=copy.deepcopy(matching[0]);rule='retained_N6_candidate'
        else:
            a,b=strain[:2];assert abs(eps-(a['x']['eps']+b['x']['eps'])/2)<1e-12
            seed=copy.deepcopy(a);seed['x']['eps']=eps;seed['x']['D']=(a['x']['D']+b['x']['D'])/2
            seed['seeds']['flat']=((np.array(a['seeds']['flat'])+b['seeds']['flat'])/2).tolist()
            seed['seeds']['node']=((np.array(a['seeds']['node'])+b['seeds']['node'])/2).tolist()
            native=m.build(seed['x'],m.config(dict(N=6)))[0]
            seed['basis_sha256']=hashlib.sha256(json.dumps(native.idx).encode()).hexdigest()
            seed['input_rows']=[a['input_rows'],b['input_rows']]
            seed['status']='INTERPOLATED_SEED_NOT_PREVIOUSLY_RECHECKED';rule='arithmetic_midpoint_seed_only'
        stations.append(dict(seed=seed,seed_rule=rule,D_bracket=[seed['x']['D']-n['D_halfwidth_meV'],seed['x']['D']+n['D_halfwidth_meV']]))
    binding=m.sources()
    for name in ('PLAN.json','BASIS.json','run.py','controls.py','CONTROLS.json'):
        binding['joint_mapping_guarded/'+name]=sha(root/name)
    binding['joint_mapping_review/N6_CANDIDATE_SEEDS.json']=sha(seed_path)
    out=dict(status='running',source_hashes=binding,stations=stations,rows=[],traces={},
             runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,blas_threads=1),
             scope=plan['scope'])
    start=time.perf_counter()
    def save():
        out['seconds']=time.perf_counter()-start
        dest.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    save()
    for i,station in enumerate(stations):
        seed=station['seed']
        for mode in n['basis_modes']:
            for engine in n['engines']:
                row=dict(station=i,mode=mode,engine=engine,result=None,status='failed')
                out['rows'].append(row)
                try:
                    cfg,conversion=trace.resolve_config(seed,dict(N=n['N'],engine=engine,
                        indices=None if mode=='radial' else basis[mode],root_radius=n['coordinate_radius']),allow_basis_reseed=True)
                    f=m.Family(seed['x'],cfg)
                    row.update(config=cfg,conversion=conversion,indices=f.indices,radial_indices=f.radial,dimension=f.dim,basis_sha256=m.digest(f.indices))
                    row['result']=trace.solve_event(seed['x'],seed['seeds'],cfg,station['D_bracket'],
                        tol=n['event_offset_tol'],xtol=n['D_xtol_meV'],maxit=n['max_bisections'])
                    row['status']=row['result']['status']
                except Exception as e:row['error']=repr(e)
                save()
                print('CANDIDATE',i,mode,engine,row['status'],row['result']['event']['D_meV'] if row.get('result') and row['result']['event'] else row.get('error'),round(out['seconds'],1),flush=True)
    for engine in n['engines']:
        tp=dict(config=dict(N=6,engine=engine,indices=basis['union'],root_radius=n['coordinate_radius']),
                allow_basis_reseed=True,tol=n['event_offset_tol'],xtol=n['D_xtol_meV'],maxit=n['max_bisections'],
                stations=[dict(knobs=dict(eps=s['seed']['x']['eps']),D_bracket=s['D_bracket']) for s in stations])
        path=root/('TRACE_'+engine.upper()+'.json')
        result=trace.run(stations[0]['seed'],tp,path)
        out['traces'][engine]=dict(file=path.name,sha256=sha(path),status=result['status'],stop_reason=result['stop_reason'],cost=result['cost'])
        save();print('TRACE',engine,result['status'],result['stop_reason'],round(out['seconds'],1),flush=True)
    out['status']='SAMPLED_COMMON_BASIS_CHECKS_COMPLETED' if all(r['status']=='candidate' for r in out['rows']) and all(t['status']=='sampled_trace_completed' for t in out['traces'].values()) else 'PARTIAL_RESULTS_RETAINED'
    save();print('STATUS',out['status'],flush=True)

if __name__=='__main__':main()
