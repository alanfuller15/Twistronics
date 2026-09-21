"""Reconcile numerical probe records; never infer acceptance from a status alone."""
import math
from pathlib import Path
from evidence import read,sha,safe,require,finite,write
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
STAGES=['baseline_nodes','baseline_remote','baseline_bandwidth','endpoint_lower']

def numeric(x):
    require(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x),'nonfinite or nonnumeric measurement')
    return x

def maxdiff(a,b):
    require(len(a)==len(b),'different numeric shape')
    return max((maxdiff(x,y) if isinstance(x,list) else abs(numeric(x)-numeric(y)) for x,y in zip(a,b)),default=0.)

def validate(r,plan,protocol):
    finite(r)
    require(r['schema']==1 and r['status']=='COMPLETE' and r['plan_sha256']==protocol,'incomplete or wrong probe identity')
    require(r['N'] in plan['cutoffs'] and r['kinetic']=='none','wrong probe model')
    require(r['runtime_before']==r['runtime_after'],'runtime changed during probe')
    require([v['variant'] for v in r['variants']]==['defective','repaired'],'missing or reordered variants')
    tol=plan['comparison_tolerances'];summaries=[]
    for v in r['variants']:
        for k in STAGES:require(v[k]['status']=='COMPLETED','rejected stage has no accepted measurement: '+k)
        calls=v['refine_calls'];require(calls,'no optimizer evidence')
        for c in calls:
            require(c['status']=='RETURNED' and c['stage'] in STAGES and len(c['attempts']) in [1,2],'invalid optimizer record')
            require(len(c['coordinate'])==2 and all(0<=numeric(x)<1 for x in c['coordinate']),'invalid returned coordinate')
            require(abs(numeric(c['returned_value'])-numeric(c['recomputed_value']))<=tol['canonical_value_meV'],'returned value lacks canonical support')
            for a in c['attempts']:
                numeric(a['value']);require(len(a['x'])==2 and isinstance(a['success'],bool) and isinstance(a['status'],int),'invalid optimizer attempt')
            if v['variant']=='repaired':
                info=c['metadata'];last=c['attempts'][-1]
                require(info['optimizer_success']==last['success'] and info['status']==last['status'] and info['message']==last['message'],'stale repaired metadata')
                require(len(info['attempts'])==len(c['attempts']),'missing repaired attempt history')
        nodes=v['baseline_nodes']['value'];node_calls=[c for c in calls if c['stage']=='baseline_nodes']
        require(nodes and len(node_calls)>=len(nodes),'missing baseline refinement evidence')
        for value,coord in nodes:
            require(any(c['coordinate']==coord and c['returned_value']==value for c in node_calls),'baseline node/candidate detached from optimizer record')
        resolved=[n for n in nodes if 0<=numeric(n[0])<1e-6]
        require(len(resolved)==2 and math.dist(resolved[0][1],resolved[1][1])>.01,'baseline root pair unresolved')
        remote=v['baseline_remote']['value'];require(numeric(remote[0])>1e-5,'baseline remote gap unresolved')
        rem_calls=[c for c in calls if c['stage']=='baseline_remote'];require(any(c['coordinate']==remote[1] and c['returned_value']==remote[0] for c in rem_calls),'remote gap detached from optimizer record')
        require(remote[0]==min(c['returned_value'] for c in rem_calls),'remote minimum selection inconsistent')
        numeric(v['baseline_bandwidth']['value'])
        end=v['endpoint_lower']['value'];require([g['grid'] for g in end['grids']]==[24,36],'endpoint grids changed')
        candidates=end['candidates'];require(candidates and end['best'] in candidates,'missing selected endpoint candidate')
        require(sum(len(g['seeds']) for g in end['grids'])==len(candidates),'missing endpoint seed result')
        expected=[(g['grid'],seed[1:]) for g in end['grids'] for seed in g['seeds']]
        require([(c['grid'],c['seed']) for c in candidates]==expected,'endpoint seed selection changed')
        for c in candidates:
            require(0<=c['call_index']<len(calls),'invalid call index');observed=calls[c['call_index']]
            require(observed['stage']=='endpoint_lower' and observed['coordinate']==c['coordinate'] and observed['returned_value']==c['value'] and observed['metadata']==c['metadata'],'endpoint detached from optimizer record')
            require(abs(numeric(c['value'])-numeric(c['recomputed_value']))<=tol['canonical_value_meV'],'endpoint canonical gap mismatch')
        require(end['best']['value']==min(c['value'] for c in candidates) and end['best']['value']>1e-5,'selected endpoint minimum invalid')
        require(all(c['metadata']['success'] and c['attempts'][-1]['success'] for c in calls),'optimizer failure cannot support accepted probe diagnostics')
        summaries.append(dict(variant=v['variant'],node_candidates=len(nodes),resolved_nodes=resolved,remote_gap=remote[0],bandwidth=v['baseline_bandwidth']['value'],endpoint_gap=end['best']['value'],endpoint_coordinate=end['best']['coordinate'],refinement_calls=len(calls),second_attempt_calls=sum(len(c['attempts'])==2 for c in calls),second_attempt_records=[c for c in calls if len(c['attempts'])==2],reported_metadata_mismatches=sum(any(c['metadata'][k]!=c['attempts'][-1][k] for k in ['success','status','message']) for c in calls)))
    a,b=r['variants'];sa,sb=summaries
    for key in ['baseline_model_sha256','endpoint_model_sha256','baseline_dimension','endpoint_dimension']:require(a[key]==b[key],'Hamiltonian or dimension changed across helper comparison')
    differences=dict(root_coordinates=maxdiff([n[1] for n in sa['resolved_nodes']],[n[1] for n in sb['resolved_nodes']]),remote_gap=abs(sa['remote_gap']-sb['remote_gap']),bandwidth=abs(sa['bandwidth']-sb['bandwidth']),endpoint_gap=abs(sa['endpoint_gap']-sb['endpoint_gap']))
    e=r['euler'];require(e['raw']['status']=='COMPLETED' and not e['refine_calls'],'Euler execution failed or unexpectedly called BM.refine')
    raw=e['raw']['value'];require(raw['mesh']==[24,40] and len(raw['phases'])==len(raw['determinants'])==24,'incomplete raw Euler record')
    require(len(e['gated'])==len(plan['euler_meshes']),'Euler mesh comparison incomplete')
    gated=[]
    for row,mesh in zip(e['gated'],plan['euler_meshes']):
        require(row['status']=='COMPLETED','Euler gate rejected measurement');v=row['value'];m=v['measurement']
        require(v['mesh']==mesh and len(m['phases'])==len(m['loop_determinants'])==mesh[0],'Euler phase mesh incomplete')
        require(m['k1_cycle']['sign']==1 and min(m['loop_determinants'])>0,'Euler bundle nonorientable')
        require(m['min_external_gap']>1e-5 and m['min_overlap']>=.1 and m['min_seam_overlap']>=.95,'Euler isolation/overlap unresolved')
        require(m['k1_cycle']['seam_overlap']>=.95 and m['k1_cycle']['seam_norm_error']<=.02,'Euler cycle sewing unresolved')
        increments=[math.atan2(math.sin(b-a),math.cos(b-a)) for a,b in zip(m['phases'],m['phases'][1:]+m['phases'][:1])]
        require(abs(sum(increments)/(2*math.pi)-m['winding'])<1e-12 and abs(m['winding']-m['euler'])<.05,'Euler phase/winding inconsistency')
        require(max(abs(x) for x in increments)<math.pi/2 and abs(max(abs(x) for x in increments)-m['max_phase_increment'])<1e-12,'Euler phase mesh unresolved')
        require(v['metrics']['real_residual']<=1e-9 and v['metrics']['hermitian_residual']<=1e-9 and v['metrics']['eigen_relative_residual']<=1e-10,'Euler numerical residuals unresolved')
        gated.append(dict(mesh=mesh,euler=m['euler'],min_external_gap=m['min_external_gap'],min_overlap=m['min_overlap'],min_seam_overlap=m['min_seam_overlap'],max_phase_increment=m['max_phase_increment'],points=v['points']))
    require(len({g['euler'] for g in gated})==1,'Euler mesh labels disagree')
    return dict(N=r['N'],variants=summaries,differences=differences,comparison_changed=any(differences[k]>(tol['root_coordinate'] if k=='root_coordinates' else tol['gap_meV']) for k in differences),euler=dict(raw_winding=raw['winding'],raw_closure=raw['closure'],raw_min_determinant=min(raw['determinants']),gated=gated,raw_absolute_label_agrees=abs(round(raw['winding']))==abs(gated[0]['euler'])),runtime_sha256=__import__('hashlib').sha256(__import__('json').dumps(r['runtime_before'],sort_keys=True).encode()).hexdigest())

def build():
    plan=read(ROOT/'NUMERICAL_PLAN.json');protocol=sha(ROOT/'NUMERICAL_PLAN.json')
    for n,h in plan['runner_sha256'].items():require(sha(safe(ROOT,n))==h,'numerical runner changed')
    for n,h in plan['inputs'].items():require(sha(safe(REPO,n))==h,'numerical input changed')
    cases=[];sources={}
    for N in plan['cutoffs']:
        p=ROOT/'results'/f'probe_N{N}.json';r=read(p);require(r['N']==N,'filename/cutoff mismatch');cases.append(validate(r,plan,protocol));sources[p.relative_to(ROOT).as_posix()]=sha(p)
    return dict(schema=1,status='CONTROLLED_REPLAYS_RECONCILED',numerical_plan_sha256=protocol,cases=cases,sources=sources,changed_comparisons=sum(c['comparison_changed'] for c in cases),refinement_calls=sum(v['refinement_calls'] for c in cases for v in c['variants']),second_attempt_calls=sum(v['second_attempt_calls'] for c in cases for v in c['variants']),limits=['Only the baseline and lower|flat1 endpoint recipes at N4/N6 were repeated; other historical scalar, mass, angle and braid sweeps remain unverified.','Successful first and second attempts cannot test the stale-status failure when their termination metadata disagree. Synthetic regression tests cover that failure separately.','Baseline find_nodes includes gapped local-minimum candidates; only two returned candidates pass the stated root-residual threshold.','Euler gates certify finite sampled diagnostics and two meshes, not global isolation, continuous topology, infinite-cutoff accuracy or physical truth.','No exact original-source/runtime execution provenance is inferred from agreement with rounded historical logs.'])

if __name__=='__main__':
    r=build();write(ROOT/'IMPACT.json',r);print({k:r[k] for k in ['status','changed_comparisons','refinement_calls','second_attempt_calls']})
