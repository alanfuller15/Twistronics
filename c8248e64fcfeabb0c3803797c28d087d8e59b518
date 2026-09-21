"""Reconcile saved roots, frames and labels; no Hamiltonian is executed here."""
from pathlib import Path
import numpy as np
from evidence import read,sha,require,write,finite,safe
from numerics import margin
from run_window import frozen
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]


def close(a,b,message,tol=1e-12):require(np.allclose(a,b,atol=tol,rtol=0),message)

def diagnostics(row):
    require(row['max_eigen_residual']<1e-10 and row['max_reality']<1e-9 and row['max_hermitian']<1e-9,'eigen/basis guard failed')


def node(n,index,box):
    require(n['success'] and n['status']>0 and n['nfev']>0 and n['index']==index,'failed final root metadata')
    require(n['residual']<1e-6 and 0<=n['gap']<1e-6 and margin(n['f'],box)>.005,'root residual/gap/domain failed')
    close(n['domain_margin'],margin(n['f'],box),'stale domain margin')


def loop(q):
    require(abs(q['charge'])==1 and abs(q['winding']-q['charge'])<.05 and q['max_phase_step']<np.pi/2 and q['min_loop_gap']>1e-6 and q['min_chart_overlap']>.1,'unresolved charge loop')


def charge(row,p):
    m=row['charge'];trials=m['trials'];require(len(trials)==3,'loop refinements missing')
    meshes=[t['points'] for t in trials];require(meshes in p['loop_meshes'],'loop meshes changed')
    rejected=m['rejected_stages']
    require((not rejected and meshes==p['loop_meshes'][0]) or (len(rejected)==1 and rejected[0]['reason']=='loop phase steps unresolved' and meshes==p['loop_meshes'][1]),'unjustified loop retry')
    for t,radius in zip(trials,[p['radius'],p['radius'],p['radius']/2]):
        require(t['radius']==radius,'loop radius changed')
        for k in ['a','b','spatial_b']:loop(t[k])
        require(t['spatial_b']['charge']==row['rectangle_orientation']*t['b']['charge'],'rectangle charge mismatch')
        label='SAME' if t['a']['charge']*t['spatial_b']['charge']>0 else 'OPPOSITE'
        require(t['label']==row['label']==label,'spatial label mismatch')
    require(all(len({t[k]['charge'] for t in trials})==1 for k in ['a','b','spatial_b']),'mesh/radius charge disagreement')
    return [trials[0][k]['charge'] for k in ['a','b']]


def path(trial,steps):
    require(trial['steps']==steps and trial['min_overlap']>.1 and trial['min_external_gap']>1e-5,'spatial path rejected')
    ts=trial['initial_t'];gaps=np.asarray(trial['initial_exterior_gaps']);require(ts==sorted(set(ts)) and ts[0]==0 and ts[-1]==1 and gaps.shape==(len(ts),2) and gaps.min()>1e-5,'spatial grid incomplete')
    require(trial['samples']>=len(ts),'spatial refinement missing')
    for q in trial['located_gap_minima']:
        require(q['gap_index'] in [3,5] and q['success'] and q['status']==0 and q['valid'] and q['nfev']>0,'failed spatial optimizer promoted')
        require(q['bracket'][0]<=q['t']<=q['bracket'][1] and 1e-5<q['gap']<=q['initial']+1e-7,'located spatial gap rejected')
        require(trial['min_external_gap']<=q['gap']+1e-10,'located minimum omitted from path')
    # Every sampled local minimum in either exterior gap must have a refinement.
    for col,index in enumerate([3,5]):
        expected=[[ts[j-1],ts[j+1]] for j in range(1,len(ts)-1) if gaps[j,col]<=min(gaps[j-1,col],gaps[j+1,col])]
        actual=[q['bracket'] for q in trial['located_gap_minima'] if q['gap_index']==index]
        require(expected==actual,'an exterior minimum was not refined')


def frames(folder,row,dimension,previous):
    folder=Path(folder);require(read(folder/'record.json')==row,'checkpoint record differs from aggregate')
    require(sha(folder/'frames.npz')==row['frames_sha256'],'frame hash mismatch')
    with np.load(folder/'frames.npz',allow_pickle=False) as stored:arrays={k:stored[k].copy() for k in stored.files}
    require(set(arrays)=={'frame_a','frame_b','spatial','spatial_fast','coarse_a','coarse_b'},'frame set incomplete')
    for a in arrays.values():require(a.shape==(dimension,2) and np.isfinite(a).all() and np.max(np.abs(a.T@a-np.eye(2)))<1e-8,'invalid saved frame')
    close(np.linalg.det(arrays['spatial'].T@arrays['frame_b']),row['rectangle_determinant'],'saved rectangle differs')
    close(np.linalg.det(arrays['spatial_fast'].T@arrays['spatial']),row['spatial_mesh_determinant'],'saved spatial mesh differs')
    if previous is not None:
        overlaps=[float(np.linalg.svd(arrays[k].T@previous[k],compute_uv=False).min()) for k in ['frame_a','frame_b']]
        close(overlaps,row['temporal_overlaps'],'saved temporal overlap differs')
        if row['coarse_check'] is None:
            for k in ['coarse_a','coarse_b']:require(np.array_equal(arrays[k],previous[k]),'coarse frame changed at fine-only state')
        else:
            c=row['coarse_check'];dets=[float(np.linalg.det(arrays['coarse_'+k].T@arrays['frame_'+k])) for k in ['a','b']]
            overlap=[float(np.linalg.svd(arrays[k].T@previous[k],compute_uv=False).min()) for k in ['coarse_a','coarse_b']]
            close(dets,c['determinants'],'saved coarse determinant differs');close(overlap,c['overlaps'],'saved coarse overlap differs')
    else:
        for k in ['a','b']:close(arrays['coarse_'+k],arrays['frame_'+k],'initial coarse frame differs')
        close(arrays['frame_b'],arrays['spatial'],'initial comparison frame differs')
    return arrays


def geometry(a,b,q):
    a=np.asarray(a);d=np.asarray(b)-a;v=np.asarray(q)-a;length=np.linalg.norm(d)
    require(length>1e-8,'collapsed segment');return dict(t=float(v@d/length**2),offset=float(v@np.array([-d[1],d[0]])/length))


def validate_case(c,engine,p,ph,result_root=None):
    finite(c);require(c['status']=='ACCEPT_SAMPLED_BRAID2_WINDOW','case incomplete or rejected')
    require(c['engine']==engine and c['N']==8 and c['case']==p['case'] and c['state']==p['state'] and c['numerical_plan_sha256']==ph,'case identity changed')
    require(c['kinetic']==p['kinetic'] and c['geometry']==p['geometry'][engine] and c['cutoff_tol']==p['cutoff_tol'][engine],'model convention changed')
    require(c['runtime_before']==c['runtime_after'] and all(v=='1' for v in c['runtime_before']['thread_environment'].values()),'runtime changed')
    require([r['ratio'] for r in c['states']]==p['ratios'],'state sequence incomplete')
    old=p['seeds'][engine];previous=None;initial=None;coarse_count=0;folder=(ROOT/'results' if result_root is None else Path(result_root))/f'{engine}_N8'
    for step,row in enumerate(c['states']):
        require(row['step']==step and row['protocol_sha256']==ph and set(row['nodes'])==set(p['node_indices']),'checkpoint identity changed')
        for name,index in p['node_indices'].items():
            n=row['nodes'][name];node(n,index,p['box']);require(n['seed']==old[name],'root continuation seed changed')
            for other,m in row['nodes'].items():
                if name<other and index==m['index']:require(np.linalg.norm(np.asarray(n['f'])-m['f'])>p['minimum_separation'],'duplicate roots')
        jump=max(float(np.linalg.norm(np.asarray(n['f'])-old[name])) for name,n in row['nodes'].items());close(jump,row['max_jump'],'root jump mismatch');require(jump<p['max_root_jump'],'root jump too large')
        a,b=[row['nodes'][k]['f'] for k in ['U1','U2']];require(np.linalg.norm(np.asarray(a)-b)>3*p['radius'],'node loops overlap')
        for name,g in row['geometry'].items():close(list(geometry(a,b,row['nodes'][name]['f']).values()),list(g.values()),'crossing geometry mismatch')
        require(row['spatial_mesh_determinant']>.99 and abs(row['rectangle_determinant'])>.99,'orientation unresolved')
        require(row['rectangle_orientation']==(1 if row['rectangle_determinant']>0 else -1),'rectangle orientation mismatch')
        require(len(row['spatial_transport'])==2,'spatial meshes missing')
        for t,steps in zip(row['spatial_transport'],p['spatial_steps']):path(t,steps)
        require(min(row['temporal_overlaps'])>.1,'temporal overlap rejected')
        check=row['coarse_check'];require((check is not None)==(step>0 and step%p['coarse_stride']==0),'coarse mesh checkpoint missing')
        if check:require(min(check['determinants'])>.99 and min(check['overlaps'])>.1,'parameter mesh rejected');coarse_count+=1
        temporal=charge(row,p)
        if initial is None:initial=temporal
        require(temporal==initial,'temporal charge changed')
        previous=frames(folder/f'step_{step:03d}',row,c['dimension'],previous);old={name:n['f'] for name,n in row['nodes'].items()};diagnostics(row['diagnostics'])
    require(len(list(folder.glob('step_*')))==len(c['states']),'extra saved checkpoints')
    event=c['event'];require(event['bracket']==p['crossing_bracket'] and event['endpoint_offsets'][0]*event['endpoint_offsets'][1]<0,'crossing bracket failed')
    require([t['xtol'] for t in event['trials']]==p['crossing_xtols'],'crossing tolerances changed')
    require(event['ratio']==event['trials'][-1]['ratio'] and abs(event['ratio']-event['trials'][0]['ratio'])<1e-8,'crossing refinement disagreement')
    evaluations=c['crossing_evaluations'];require(len({x['ratio'] for x in evaluations})==len(evaluations),'duplicate crossing evaluation')
    by_ratio={x['ratio']:x for x in evaluations}
    for e in evaluations:
        require(p['crossing_bracket'][0]<=e['ratio']<=p['crossing_bracket'][1],'crossing left bracket')
        for name,index in [('U1',4),('U2',4),('X1',5)]:node(e['nodes'][name],index,p['box'])
        g=geometry(*[e['nodes'][name]['f'] for name in ['U1','U2','X1']]);close(list(g.values()),list(e['geometry'].values()),'event geometry mismatch');require(0<g['t']<1,'event outside segment');diagnostics(e['diagnostics'])
    for ratio,offset in zip(event['bracket'],event['endpoint_offsets']):close(by_ratio[ratio]['geometry']['offset'],offset,'endpoint offset mismatch')
    for t in event['trials']:
        require(t['converged'] and t['iterations']>0 and t['function_calls']>0 and abs(t['offset'])<1e-7,'crossing optimizer unresolved');close(t['offset'],by_ratio[t['ratio']]['geometry']['offset'],'crossing residual mismatch')
    for k in ['nodes','geometry','diagnostics']:require(event[k]==by_ratio[event['ratio']][k],'stale final crossing metadata')
    a,b=[np.asarray(event['nodes'][k]['f']) for k in ['U1','U2']];close(a+event['geometry']['t']*(b-a),event['segment_point'],'wrong singular witness')
    require(0<=event['external_gap']<=1e-5 and event['singular_path_rejected'] is True and event['rejection_reason']=='selected group loses isolation','singular comparison not explicitly rejected');diagnostics(event['segment_diagnostics'])
    require([row['label'] for row in c['states']]==['SAME' if ratio<event['ratio'] else 'OPPOSITE' for ratio in p['ratios']],'labels do not bracket event')
    return dict(engine=engine,N=8,dimension=c['dimension'],crossing_ratio=event['ratio'],crossing_t=event['geometry']['t'],crossing_external_gap=event['external_gap'],crossing_tolerance_difference=abs(event['trials'][0]['ratio']-event['ratio']),states=len(c['states']),roots=len(c['states'])*6,coarse_checks=coarse_count,labels=[x['label'] for x in c['states']],temporal_charges=initial,frame_checkpoints=len(c['states']),min_comparison_gap=min(t['min_external_gap'] for x in c['states'] for t in x['spatial_transport']),min_comparison_overlap=min(t['min_overlap'] for x in c['states'] for t in x['spatial_transport']),loop_retry_stages=sum(len(x['charge']['rejected_stages']) for x in c['states']),seconds=c['seconds'])


def build():
    p=frozen();ph=sha(ROOT/'NUMERICAL_PLAN.json');targets=read(ROOT/'HISTORICAL_TARGETS.json');cases=[];comparisons=[]
    for engine in p['engines']:
        raw=read(ROOT/'results'/f'second_{engine}_N8.json');case=validate_case(raw,engine,p,ph);cases.append(case);old=targets['cases'][engine]
        for cutoff in ['4','6']:
            h=old[cutoff];source=read(safe(REPO,h['source']));require(sha(safe(REPO,h['source']))==h['sha256'] and source['event']==h['event'] and [x for x in source['states'] if x['ratio']<=.991]==h['common_states'],'historical target differs from source')
        common=[]
        for h in old['6']['common_states']:
            row=next(x for x in raw['states'] if x['ratio']==h['ratio']);common.append(dict(ratio=row['ratio'],N6_label=h['label'],N8_label=row['label'],max_node_displacement=max(float(np.linalg.norm(np.asarray(row['nodes'][k]['f'])-h['nodes'][k]['f'])) for k in p['node_indices'])))
        comparisons.append(dict(engine=engine,N4_saved_ratio=old['4']['event']['ratio'],N6_saved_ratio=old['6']['event']['ratio'],N8_fresh_ratio=case['crossing_ratio'],N8_minus_N6=case['crossing_ratio']-old['6']['event']['ratio'],common_states=common))
    hashes={f.relative_to(ROOT).as_posix():sha(f) for f in sorted((ROOT/'results').rglob('*')) if f.is_file()}
    return dict(version='our_v060',status='BOUNDED_N8_BRAID2_WINDOW_COMPLETE',numerical_plan_sha256=ph,state=p['state'],ratios=p['ratios'],cases=cases,cutoff_comparisons=comparisons,input_sha256=hashes,max_abs_N8_N6_crossing_shift=max(abs(c['N8_minus_N6']) for c in comparisons),cross_engine_N8_ratio_difference=cases[0]['crossing_ratio']-cases[1]['crossing_ratio'],limits=[
        'Five finite states per engine cover ratio 0.99000 to 0.99100, not the full historical 0.99 to 1.00 braid-2 leg, a continuous interval or the entire N8 campaign.',
        'The spatial comparison changes SAME to OPPOSITE; the two temporally carried individual charges remain constant. At the crossing the spatial comparison loses isolation and is rejected.',
        targets['scope'],
        'The engines share this measurement harness and a constant-tunnelling lab_nn_full approximation; BM linear and reference exact reciprocal geometry remain distinct.',
        'Located gap minima, frame overlaps and mesh/radius agreement are finite numerical evidence, not global gap bounds or an independent scientific reference.',
        'This does not extend the flat-pair frame path, Euler class, endpoint w1, first-annihilation event or all connecting legs to N8. Infinite-cutoff accuracy, microscopic tunnelling strain dependence and physical validation remain open.',
        'Source/test/result hashes establish internal consistency, not independent authenticity, chronology or physical truth.'])

if __name__=='__main__':
    r=build();write(ROOT/'IMPACT.json',r);print(r['status'])
