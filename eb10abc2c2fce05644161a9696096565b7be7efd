"""Reconcile saved evidence without importing historical builders or engines."""
from pathlib import Path
from evidence import read,accepted,sha,safe,require,write,pair_distance
from catalog import ENGINES,CUTOFFS,FAMILIES,VERSIONS
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]

def charge(m):
    require(m['label'] in ['SAME','OPPOSITE'],'unresolved pair label')
    require(len(m['trials'])==3,'missing mesh/radius trials')
    for t in m['trials']:
        require(t['label']==m['label'],'inconsistent pair trials')
        for side in ['a','b']:
            q=t[side];require(abs(q['charge'])==1 and abs(q['winding']-q['charge'])<.05,'unresolved recorded winding')
        require(('SAME' if t['a']['charge']*t['b']['charge']>0 else 'OPPOSITE')==m['label'],'label contradicts charges')

def cycles(r):
    labels={}
    require(set(r['cycles'])=={'lower_remote','flat1','flat2','upper_remote','flat_pair'},'missing band cycle group')
    for band,rows in r['cycles'].items():
        require(len(rows)==4 and {(q['axis'],q['offset']) for q in rows}=={(a,o) for a in [0,1] for o in [0.,.5]},'missing cycle axis/offset')
        labels[band]=[]
        for axis in [0,1]:
            ts=[t for q in rows if q['axis']==axis for t in q['trials']]
            require(len(ts)==4 and len({t['sign'] for t in ts})==1 and ts[0]['sign'] in [-1,1],'cycle sign disagreement')
            require(all(t['seam_overlap']>0 and t['min_external_gap']>1e-5 for t in ts),'unresolved cycle isolation/seam')
            labels[band].append(int(ts[0]['sign']<0))
    if 'w1' in r:require(r['w1']==labels,'saved w1 disagrees with cycle records')
    return labels

def state_equal(a,b):
    # Only these explicitly reviewed historical defaults are normalized.
    defaults={'w_kappa':0.0,'w_mode':'average'}
    require({**defaults,**a}=={**defaults,**b},'join model-state mismatch')

def positive_trials(trials,grids=(18,24)):
    require([t['grid'] for t in trials]==list(grids),'missing gap grid refinement')
    vals=[t['minimum']['gap'] for t in trials]
    require(min(vals)>1e-5 and max(vals)-min(vals)<.01,'unresolved or inconsistent gap')
    return min(vals)

def validate_record(r,adapter,count,protocol,embedded=True,gap_grids=((18,24),(18,24))):
    require(r['status']=='ACCEPT','unaccepted record')
    require(r['engine'] in ENGINES and r['N'] in CUTOFFS,'unknown engine/cutoff')
    if embedded:require(r.get('protocol_sha256')==protocol,'record protocol mismatch')
    stats=dict(frame_stations=0,root_stations=0,charge_stations=0,gapped_stations=0,open_stations=0)
    if adapter=='frame':
        require(len(r['states'])==count,'wrong frame station count')
        for i,s in enumerate(r['states']):
            require(s['status']=='ACCEPT' and s['step']==i and s['engine']==r['engine'] and s['N']==r['N'] and s['protocol_sha256']==protocol,'frame identity/sequence mismatch')
            require(s['label'] in ['SAME','OPPOSITE'] and len(s['temporal_trials'])==3,'frame charge diagnostics incomplete')
            require(s['spatial_mesh_determinant']>.99 and len(s['spatial_transport'])==2,'spatial refinement missing')
        stats.update(frame_stations=count,charge_stations=count)
    elif adapter in ['fold','local_fold','lower_fold']:
        require(len(r['states'])==count and len(r['charges'])==2,'incomplete fold stations')
        ev=r['event'];trials=ev['fold_trials'];nd=r['nondegeneracy']
        require([t['h'] for t in trials]==[2e-5,1e-5] and abs(trials[0]['parameter']-trials[1]['parameter'])<1e-6,'fold derivative refinement missing')
        require(nd['status']=='PASS' and len(nd['trials'])==2,'missing fold nondegeneracy')
        require(all(t['singular_values'][-1]<1e-3 and t['singular_values'][0]>1 and t['external_gap']>1e-5 for t in trials),'recorded fold rank/isolation fails')
        require(all(abs(t['curvature'])>1 and abs(t['parameter_slope'])>.01 for t in nd['trials']),'degenerate recorded fold')
        for s in r['states']:
            require(len(s['nodes'])==2 and s['separation']>.001 and all(0<=n['gap']<1e-6 and n['index']==r['definition']['index'] for n in s['nodes']),'unresolved fold roots')
        for c in r['charges']:charge(c['measurement']);require(c['measurement']['label']=='OPPOSITE','fold pair is not opposite')
        opens=r.get('open_checks',r.get('gapped_checks'))
        if adapter=='local_fold':
            require(r.get('scope')=='LOCAL_DOMAIN_EVENT' and r['definition']['box']==[[.42,.63],[.52,.63]],'local-domain claim changed')
            require([s['station'] for s in opens]==['fold','near_open','far_open'],'local station selection changed')
            for s in [*r['states'],*opens]:require([t['grid'] for t in s['boundary']['trials']]==[24,48] and min(t['minimum'] for t in s['boundary']['trials'])>1e-5,'local boundary not resolved')
            opens=opens[1:]
        elif adapter=='lower_fold':require(r.get('scope')=='FULL_CHART_LOWER_GAP_SEARCH','wrong lower-gap scope')
        require(len(opens)==2,'missing opposite-side gap stations')
        for s,grids in zip(opens,gap_grids):positive_trials(s['trials'],grids)
        stats.update(root_stations=count,charge_stations=2,open_stations=2)
    elif adapter=='braid':
        require(len(r['states'])==count and r['event']['singular_path_rejected'] is True,'braid window incomplete')
        require([r['states'][0]['label'],r['states'][-1]['label']]==['SAME','OPPOSITE'],'braid endpoint labels changed')
        stats.update(frame_stations=count,charge_stations=count)
    elif adapter=='pair':charge(r['pair']);stats['charge_stations']=1
    elif adapter in ['gapped','gapped_checkpoint']:
        rows=r['states'] if adapter=='gapped' else [r]
        require(len(rows)==count,'wrong gapped station count')
        labels=[]
        for s in rows:
            for trials in s['gaps'].values():positive_trials(trials)
            labels.append(cycles(s))
        require(all(x==labels[0] for x in labels),'w1 changes between gapped stations')
        stats['gapped_stations']=count
    else:raise ValueError('unknown record schema: '+adapter)
    return stats

def build(repo=REPO,index=None):
    repo=Path(repo);index=index or read(ROOT/'SOURCE_INDEX.json');require(index['schema']==1,'unknown index schema')
    require(set(index['batches'])==set(VERSIONS),'unknown/missing batch')
    batches={};sources={};frozen_checks=0;frames=0;raw_records={};rows=[]
    def bind(p):
        name=p.relative_to(repo).as_posix();sources[name]=sha(p);return name
    for ver,path in sorted(index['batches'].items()):
        folder=safe(repo,path);plan=read(folder/'PLAN.json');require(plan['version']==VERSIONS[ver],'wrong version schema')
        protocol=sha(folder/'PLAN.json');bind(folder/'PLAN.json')
        for group in ['source_sha256','anchor_sha256']:
            for name,h in plan.get(group,{}).items():
                p=safe(folder,name);require(sha(p)==h,'frozen source/input mismatch: '+str(p));bind(p);frozen_checks+=1
        sp=folder/('results/summary.json' if ver=='v042' else 'SUMMARY.json');summary=accepted(sp);bind(sp)
        if ver!='v042':require(summary.get('protocol_sha256',summary.get('primary_protocol_sha256'))==protocol,'summary protocol mismatch')
        batches[ver]=(folder,plan,summary,protocol)
    for family,ver,adapter,pattern,role,scope,count in FAMILIES:
        folder,plan,summary,protocol=batches[ver]
        for engine in ENGINES:
            for N in CUTOFFS:
                path=folder/pattern.format(engine=engine,N=N);r=accepted(path)
                require((r['engine'],r['N'])==(engine,N),'filename/record engine identity mismatch')
                gap_grids=((18,),(18,24)) if family in ['first_ann','upper_ann','flat_birth','final_ann'] else ((17,25),(17,25)) if adapter=='local_fold' else ((18,24),(18,24))
                try:stats=validate_record(r,adapter,count,protocol,ver!='v042',gap_grids)
                except (ValueError,KeyError,TypeError) as exc:raise ValueError(f'{family}/{engine}/N{N}: {exc}') from exc
                record=bind(path)
                if adapter=='frame':
                    for i,s in enumerate(r['states']):
                        raw=path.parent/f'step_{i:03d}/record.json';require(read(raw)==s,'summary differs from frame checkpoint');bind(raw)
                        array=raw.parent/'frames.npz';require(sha(array)==s['frames_sha256'],'frame array hash mismatch');bind(array);frames+=1
                elif adapter=='gapped':
                    for i,s in enumerate(r['states']):
                        raw=path.parent/f'state_{i:03d}.json';require(accepted(raw)==s,'summary differs from gapped checkpoint');bind(raw)
                row=dict(id=f'{family}/{engine}/N{N}',family=family,batch=ver,engine=engine,N=N,geometry='linear' if engine=='bm_lab' else 'exact',kinetic='lab_nn_full',role=role,scope=scope,adapter=adapter,saved_status='ACCEPT',verification='saved artifact consistency; no fresh numerical replay',record=record,record_sha256=sha(path),protocol_sha256=protocol,protocol_binding='embedded' if ver!='v042' else 'contextual: raw v042 records do not embed the PLAN hash',counts=stats)
                if 'fold' in adapter:row['open_gap_grids']=[list(g) for g in gap_grids]
                if adapter=='frame':row.update(labels=sorted({s['label'] for s in r['states']}),start=r['states'][0]['state'],end=r['states'][-1]['state'])
                elif 'fold' in adapter:row.update(parameter_name=r['definition']['key'],parameter=r['event']['parameter'],pair_label='OPPOSITE',gap_index=r['definition']['index'])
                elif adapter=='braid':row.update(parameter_name='ratio',parameter=r['event']['ratio'],labels=['SAME','OPPOSITE'])
                elif adapter=='pair':row['pair_label']=r['pair']['label']
                elif adapter.startswith('gapped'):row['w1']=cycles(r['states'][0] if adapter=='gapped' else r)
                rows.append(row);raw_records[family,engine,N]=r
    require(len({r['id'] for r in rows})==len(FAMILIES)*4,'duplicate/incomplete claim grid')
    # Compare stated aggregate counts and critical values with the independently read records.
    aggregate_fields={'v043':{'states':'frame_stations'},'v044':{'primary_states':'frame_stations'},'v046':{'cleanup_states':'frame_stations','root_continuation_states':'root_stations'},'v048':{'root_states':'root_stations','charge_stations':'fold_charge','gapped_states':'gapped_stations'},'v050':{'root_states':'root_stations','charge_stations':'fold_charge'},'v051':{'root_state_records':'root_stations','charge_measurements':'fold_charge'},'v052':{'root_state_records':'root_stations','charge_measurements':'fold_charge'},'v053':{'accepted_states':'frame_stations'},'v054':{'accepted_states':'frame_stations'},'v055':{'root_states':'root_stations','charge_stations':'fold_charge','open_stations':'open_stations'}}
    for ver,fields in aggregate_fields.items():
        for key,metric in fields.items():
            n=sum(r['counts']['charge_stations'] if metric=='fold_charge' else r['counts'][metric] for r in rows if r['batch']==ver and (metric!='fold_charge' or 'fold' in r['adapter']))
            require(batches[ver][2][key]==n,'summary count mismatch: '+ver+'/'+key)
    for row in rows:
        s=batches[row['batch']][2]
        if row['adapter']=='frame' and 'cases' in s:
            items=[x for x in s['cases'] if x['engine']==row['engine'] and x['N']==row['N'] and x.get('case',row['family'])==row['family']]
            require(len(items)==1 and items[0]['states']==row['counts']['frame_stations'] and sorted(items[0]['labels'])==row['labels'],'frame summary labels/counts mismatch')
        if 'fold' in row['adapter'] and row['batch']!='v042':
            items=[x for x in s.get('folds',s.get('cases',[])) if x['engine']==row['engine'] and x['N']==row['N'] and x.get('case',row['family'])==row['family']]
            require(len(items)==1,'missing/duplicate summary fold row')
            item=items[0];value=next(item[k] for k in ['parameter','ratio','A','B'] if k in item)
            require(value==row['parameter'],'summary fold parameter mismatch')
    # Pair identity joins do not infer absolute frame orientation across historical boundaries.
    links=[]
    def nodes(s,names=None):return [s['nodes'][k] for k in names] if names else s['nodes']
    def link(name,e,n,a,b):
        distance=pair_distance(a,b);require(distance<1e-6,'root link mismatch: '+name)
        links.append(dict(link=name,engine=e,N=n,kind='same-state root identity only',max_distance=distance))
    for e in ENGINES:
        for n in CUTOFFS:
            get=lambda f:raw_records[f,e,n]
            prep=get('preparation');early=get('early_braid');pre=get('pre_ann');post=get('post_ann');braid=get('braid2');clean=get('cleanup')
            state_pairs=[(prep['states'][-1]['state'],early['states'][0]['state']),
              (early['states'][-1]['state'],pre['states'][0]['state']),
              (pre['states'][-1]['state'],get('first_ann')['definition']['p']),
              (get('post_transfer')['state'],post['states'][0]['state']),
              (clean['states'][-1]['state'],get('upper_ann')['definition']['p']),
              (get('flat_birth')['definition']['p'],get('final_ann')['definition']['p']),
              (get('prep_lower_birth')['definition']['p'],early['states'][0]['state']),
              (get('lower_unlink')['definition']['p'],early['states'][28]['state']),
              (get('extra_flat_birth')['definition']['p'],get('extra_flat_ann')['definition']['p'])]
            for a,b in state_pairs:state_equal(a,b)
            # v042 braid records only store ratio; the remaining state is contextual
            # from reviewed replay_second.py + models.State, not embedded evidence.
            for s,b in [(post['states'][-1]['state'],braid['states'][0]),(clean['states'][0]['state'],braid['states'][-1])]:
                state_equal(s,dict(A=0,B=-.4,T=-.8,phi=80,ratio=b['ratio'],theta=1.05,eps=.003))
            old=batches['v042'][2]['engines'][e][str(n)]
            require(old['braid_crossing']==braid['event']['ratio'] and old['annihilation']==get('first_ann')['event']['parameter'],'v042 event summary mismatch')
            require(old['braid_labels']==[braid['states'][0]['label'],braid['states'][-1]['label']] and old['post_transfer_label']==get('post_transfer')['pair']['label'],'v042 label summary mismatch')
            require(old['annihilation_pair_labels']==[c['measurement']['label'] for c in get('first_ann')['charges']],'v042 fold label summary mismatch')
            for which,station in [('bridge',2),('endpoint',7)]:
                checkpoint=get(which+'_checkpoint');connection=get('gapped_connections')['states'][station]
                state_equal(checkpoint['state'],connection['state'])
                require(cycles(checkpoint)==cycles(connection)==old['w1']==batches['v048'][2]['w1'],'gapped anchor w1 mismatch')
                for gap,trials in checkpoint['gaps'].items():
                    require(old[which+'_gaps'][gap]==min(t['minimum']['gap'] for t in trials),'v042 gap summary mismatch')
                    require(trials==connection['gaps'][gap],'gapped anchor diagnostics mismatch')
            link('preparation → early',e,n,nodes(prep['states'][-1]),nodes(early['states'][0],['F1','F3']))
            link('early → pre-annihilation',e,n,nodes(early['states'][-1],['F1','F3']),nodes(pre['states'][0]))
            link('pre-annihilation → first fold',e,n,nodes(pre['states'][-1]),get('first_ann')['event']['initial_nodes'])
            link('post-transfer → post-annihilation',e,n,get('post_transfer')['pair']['nodes'],nodes(post['states'][0]))
            link('post-annihilation → braid 2',e,n,nodes(post['states'][-1]),nodes(braid['states'][0],['U1','U2']))
            link('braid 2 → cleanup',e,n,nodes(braid['states'][-1],['U1','U2']),nodes(clean['states'][0]))
            link('cleanup → upper fold',e,n,nodes(clean['states'][-1]),get('upper_ann')['event']['initial_nodes'])
            link('late birth → final annihilation',e,n,get('flat_birth')['event']['initial_nodes'],get('final_ann')['event']['initial_nodes'])
            link('lower birth → early inventory',e,n,get('prep_lower_birth')['event']['initial_nodes'],nodes(early['states'][0],['L1','L2']))
            link('lower unlink → step 028 inventory',e,n,get('lower_unlink')['event']['initial_nodes'],nodes(early['states'][28],['L1','L2']))
            link('extra flat birth → extra flat annihilation',e,n,get('extra_flat_birth')['event']['initial_nodes'],get('extra_flat_ann')['event']['initial_nodes'])
    by_kind={}
    for role in ['primary','superseded_replay','corroborating_checkpoint']:
        by_kind[role]={k:sum(r['counts'][k] for r in rows if r['role']==role) for k in rows[0]['counts']}
    return dict(schema=1,status='CONSISTENT_SAVED_EVIDENCE',scope='explicit v042–v055 primary campaign records plus identified duplicate/corroborating records',batch_count=len(batches),claim_rows=rows,root_links=links,counts_by_role=by_kind,frozen_checks=frozen_checks,frame_arrays_hashed=frames,sources=sources,limits=['No historical numerical engine or report builder was executed to construct this map.','Frame arrays were hashed as opaque bytes, not numerically re-evaluated.','Same-state root joins are not proof of absolute frame continuity.','Counts describe overlapping recorded observations, not unique physical states.','v042 PLAN linkage and braid held-parameter state are contextual; later raw records embed the protocol hash.','The map validates selected saved diagnostics against explicit version schemas, not every historical gate or summary field. Older first/upper/late folds have only grid 18 at the near-open station; local folds use grids 17/25 and a bounded domain.','Source/data consistency does not establish authenticity, timing, continuous-path completeness, infinite-cutoff accuracy or physical truth.'])

if __name__=='__main__':
    r=build();write(ROOT/'results/campaign_map.json',r);print({k:r[k] for k in ['status','batch_count','frozen_checks','frame_arrays_hashed','counts_by_role']})
