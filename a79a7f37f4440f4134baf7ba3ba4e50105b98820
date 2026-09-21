"""Reconcile saved roots, frames and labels; no Hamiltonian is executed here."""
from pathlib import Path
import numpy as np
from evidence import read,sha,require,write,finite,safe
from numerics import margin
from run_window import frozen
from joins import anchor,arrays_at
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
    arrays=arrays_at(folder,row,dimension)
    close(np.linalg.det(arrays['spatial'].T@arrays['frame_b']),row['rectangle_determinant'],'saved rectangle differs')
    close(np.linalg.det(arrays['spatial_fast'].T@arrays['spatial']),row['spatial_mesh_determinant'],'saved spatial mesh differs')
    if previous is not None:
        overlaps=[float(np.linalg.svd(arrays[k].T@previous[k],compute_uv=False).min()) for k in ['frame_a','frame_b']]
        close(overlaps,row['temporal_overlaps'],'saved temporal overlap differs')
        for k in ['frame_a','frame_b']:
            gram=arrays[k].T@previous[k]
            require(np.max(np.abs(gram-gram.T))<1e-8 and np.linalg.eigvalsh(gram).min()>.1,'saved temporal polar alignment differs')
        if row['coarse_check'] is None:
            for k in ['coarse_a','coarse_b']:require(np.array_equal(arrays[k],previous[k]),'coarse frame changed at fine-only state')
        else:
            c=row['coarse_check'];dets=[float(np.linalg.det(arrays['coarse_'+k].T@arrays['frame_'+k])) for k in ['a','b']]
            overlap=[float(np.linalg.svd(arrays[k].T@previous[k],compute_uv=False).min()) for k in ['coarse_a','coarse_b']]
            close(dets,c['determinants'],'saved coarse determinant differs');close(overlap,c['overlaps'],'saved coarse overlap differs')
            for k in ['coarse_a','coarse_b']:
                gram=arrays[k].T@previous[k]
                require(np.max(np.abs(gram-gram.T))<1e-8 and np.linalg.eigvalsh(gram).min()>.1,'saved coarse polar alignment differs')
    else:
        raise ValueError('continuation requires predecessor frames')
    return arrays


def geometry(a,b,q):
    a=np.asarray(a);d=np.asarray(b)-a;v=np.asarray(q)-a;length=np.linalg.norm(d)
    require(length>1e-8,'collapsed segment');return dict(t=float(v@d/length**2),offset=float(v@np.array([-d[1],d[0]])/length))


def validate_join(row,arrays,old,prior,p):
    j=row['join'];require(isinstance(j,dict),'missing anchor join')
    shifts={k:float(np.linalg.norm(np.asarray(n['f'])-old['nodes'][k]['f'])) for k,n in row['nodes'].items()}
    require(set(j['root_shifts'])==set(shifts),'incomplete root join')
    close(list(shifts.values()),list(j['root_shifts'].values()),'stale root join')
    require(max(shifts.values())<p['join_root_tolerance'],'anchor root join failed')
    overlaps={};errors={}
    for k in ['a','b']:
        for prefix in ['frame_','coarse_']:
            name=prefix+k;overlaps[name]=float(np.linalg.svd(arrays['frame_'+k].T@prior[name],compute_uv=False).min())
        errors[k]=float(np.max(np.abs(arrays['frame_'+k]-prior['frame_'+k])))
    require(set(j['subspace_overlaps'])==set(overlaps) and set(j['aligned_max_errors'])==set(errors),'incomplete frame join')
    for k,v in overlaps.items():close(v,j['subspace_overlaps'][k],'stale subspace join')
    for k,v in errors.items():close(v,j['aligned_max_errors'][k],'stale aligned frame join')
    require(min(overlaps.values())>1-p['join_frame_tolerance'] and max(errors.values())<p['join_frame_tolerance'],'anchor basis/frame join failed')
    require(row['label']==old['label'],'anchor label changed')


def runtime_join(prior,current):
    a=dict(prior);b=dict(current);old=Path(a.pop('executable'));new=Path(b.pop('executable'))
    require(a==b,'runtime differs from predecessor beyond executable alias')
    require(old.resolve()==new.resolve() and sha(old)==sha(new),'Python executable differs from predecessor')
    return dict(prior_executable=str(old),current_executable=str(new),resolved_executable=str(new.resolve()),binary_sha256=sha(new),other_runtime_fields_equal=True,scope='Executable paths were resolved and hashed during reconciliation; the original runtime records retain their distinct invocation names.')


def validate_case(c,engine,p,ph,result_root=None):
    finite(c);require(c['status']=='ACCEPT_SAMPLED_BRAID2_CONTINUATION','case incomplete or rejected')
    require(c['engine']==engine and c['N']==8 and c['dimension']==p['dimension'] and c['case']==p['case'] and c['state']==p['state'] and c['numerical_plan_sha256']==ph,'case identity changed')
    require(c['kinetic']==p['kinetic'] and c['geometry']==p['geometry'][engine] and c['cutoff_tol']==p['cutoff_tol'][engine],'model convention changed')
    require(c['runtime_before']==c['runtime_after'] and all(v=='1' for v in c['runtime_before']['thread_environment'].values()),'runtime changed')
    require(c['anchor']==p['anchors'][engine],'anchor identity changed')
    old,prior=anchor(REPO,p,engine)
    runtime=runtime_join(read(safe(REPO,c['anchor']['aggregate']))['runtime_after'],c['runtime_before'])
    require([r['ratio'] for r in c['states']]==p['ratios'],'state sequence incomplete')
    seeds=p['seeds'][engine];previous=prior;initial=c['anchor']['temporal_charges'];coarse_count=0
    folder=(ROOT/'results' if result_root is None else Path(result_root))/f'{engine}_N8'
    for step,row in enumerate(c['states']):
        require(row['step']==step and row['protocol_sha256']==ph and set(row['nodes'])==set(p['node_indices']),'checkpoint identity changed')
        for name,index in p['node_indices'].items():
            n=row['nodes'][name];node(n,index,p['box']);require(n['seed']==seeds[name],'root continuation seed changed')
            for other,m in row['nodes'].items():
                if name<other and index==m['index']:require(np.linalg.norm(np.asarray(n['f'])-m['f'])>p['minimum_separation'],'duplicate roots')
        jump=max(float(np.linalg.norm(np.asarray(n['f'])-seeds[name])) for name,n in row['nodes'].items());close(jump,row['max_jump'],'root jump mismatch');require(jump<p['max_root_jump'],'root jump too large')
        a,b=[row['nodes'][k]['f'] for k in ['U1','U2']];require(np.linalg.norm(np.asarray(a)-b)>3*p['radius'],'node loops overlap')
        require(set(row['geometry'])=={k for k in p['node_indices'] if k.startswith('X')},'missing adjacent geometry')
        for name,g in row['geometry'].items():close(list(geometry(a,b,row['nodes'][name]['f']).values()),list(g.values()),'crossing geometry mismatch')
        require(row['spatial_mesh_determinant']>.99 and abs(row['rectangle_determinant'])>.99,'orientation unresolved')
        require(row['rectangle_orientation']==(1 if row['rectangle_determinant']>0 else -1),'rectangle orientation mismatch')
        require(len(row['spatial_transport'])==2,'spatial meshes missing')
        for t,steps in zip(row['spatial_transport'],p['spatial_steps']):path(t,steps)
        require(min(row['temporal_overlaps'])>.1,'temporal overlap rejected')
        check=row['coarse_check'];require((check is not None)==(step in p['coarse_checks']),'coarse mesh checkpoint missing')
        if check:require(min(check['determinants'])>.99 and min(check['overlaps'])>.1,'parameter mesh rejected');coarse_count+=1
        require(charge(row,p)==initial,'temporal charge changed from anchor')
        current=frames(folder/f'step_{step:03d}',row,c['dimension'],previous)
        if step==0:validate_join(row,current,old,prior,p)
        else:require(row['join'] is None,'join evidence at non-join state')
        previous=current;seeds={name:n['f'] for name,n in row['nodes'].items()};diagnostics(row['diagnostics'])
    require(len(list(folder.glob('step_*')))==len(c['states']),'extra saved checkpoints')
    return dict(engine=engine,N=8,dimension=c['dimension'],measured_states=len(c['states']),new_states=len(c['states'])-1,roots=len(c['states'])*6,coarse_checks=coarse_count,labels=[x['label'] for x in c['states']],temporal_charges=initial,frame_checkpoints=len(c['states']),join=c['states'][0]['join'],runtime_join=runtime,min_comparison_gap=min(t['min_external_gap'] for x in c['states'] for t in x['spatial_transport']),min_comparison_overlap=min(t['min_overlap'] for x in c['states'] for t in x['spatial_transport']),min_temporal_overlap=min(min(x['temporal_overlaps']) for x in c['states']),min_coarse_determinant=min(min(x['coarse_check']['determinants']) for x in c['states'] if x['coarse_check']),loop_retry_stages=sum(len(x['charge']['rejected_stages']) for x in c['states']),endpoint_nodes={k:n['f'] for k,n in c['states'][-1]['nodes'].items()},seconds=c['seconds'])


def build():
    p=frozen();ph=sha(ROOT/'NUMERICAL_PLAN.json');targets=read(ROOT/'HISTORICAL_TARGETS.json');cases=[];comparisons=[];combined=[]
    for engine in p['engines']:
        raw=read(ROOT/'results'/f'second_{engine}_N8.json');case=validate_case(raw,engine,p,ph);cases.append(case)
        for cutoff in ['4','6']:
            h=targets['cases'][engine][cutoff];source=read(safe(REPO,h['source']))
            require(sha(safe(REPO,h['source']))==h['sha256'] and source['event']==h['event'] and [x for x in source['states'] if x['ratio']>=.991]==h['common_states'],'historical target differs from source')
            rows=[]
            for historic in h['common_states']:
                row=next(x for x in raw['states'] if x['ratio']==historic['ratio'])
                rows.append(dict(ratio=row['ratio'],saved_label=historic['label'],N8_label=row['label'],max_node_displacement=max(float(np.linalg.norm(np.asarray(row['nodes'][k]['f'])-historic['nodes'][k]['f'])) for k in p['node_indices'])))
            comparisons.append(dict(engine=engine,saved_cutoff=int(cutoff),common_states=rows,labels_match=all(x['saved_label']==x['N8_label'] for x in rows),max_node_displacement=max(x['max_node_displacement'] for x in rows)))
        predecessor=read(safe(REPO,p['anchors'][engine]['aggregate']))
        chain=predecessor['states']+raw['states'][1:]
        require(len({x['ratio'] for x in chain})==len(chain) and all(a['ratio']<b['ratio'] for a,b in zip(chain,chain[1:])),'combined chain is not unique and ordered')
        combined.append(dict(engine=engine,ratios=[x['ratio'] for x in chain],labels=[x['label'] for x in chain],distinct_states=len(chain),predecessor_status=predecessor['status'],predecessor_numerical_plan_sha256=p['anchor_plan_sha256'],scope='Retained v060 evidence plus fresh v062 continuation, joined at .991. No new replay of earlier v060 measurements.'))
    hashes={f.relative_to(ROOT).as_posix():sha(f) for f in sorted((ROOT/'results').rglob('*')) if f.is_file()}
    return dict(version='our_v062',status='BOUNDED_N8_BRAID2_CONTINUATION_COMPLETE',numerical_plan_sha256=ph,state=p['state'],ratios=p['ratios'],cases=cases,cutoff_comparisons=comparisons,combined_braid2_chain=combined,input_sha256=hashes,cross_engine_labels_match=cases[0]['labels']==cases[1]['labels'],cross_engine_max_endpoint_node_distance=max(float(np.linalg.norm(np.asarray(cases[0]['endpoint_nodes'][k])-cases[1]['endpoint_nodes'][k])) for k in p['node_indices']),limits=[
        'Eleven measured states per engine include one repeated join and ten new states. Combined with v060, the finite sampled braid-2 chain spans .99000 to 1.00000, with fifteen distinct ratios per engine; this is not continuous-interval proof.',
        'The spatial charge comparison and each temporally carried individual charge are different observables. Absolute temporal signs depend on each engine\'s inherited gauge and are not compared across engines.',
        targets['scope']+' N4/N6 likewise were not rerun in v062.',
        'Two engines share this measurement harness and the constant-tunnelling lab_nn_full approximation. BM linear and reference exact reciprocal geometry remain distinct.',
        'Saved frame reconciliation checks hashes, orthogonality, joins and polar alignment; it does not independently rerun all eigenproblems or winding loops. Sampled/located gap minima are not global gap bounds.',
        'This extends only the U-pair braid-2 frame path. Remaining connecting legs, full flat-pair/Euler/endpoint-w1 coverage at N8, infinite-cutoff accuracy, a microscopic tunnelling strain law and physical validation remain open.',
        'Preserved v061 recovery and prior failure history remain unchanged. Source/test/result hashes establish internal consistency, not independent authenticity, chronology or scientific truth.'])

if __name__=='__main__':
    r=build();write(ROOT/'IMPACT.json',r);print(r['status'])
