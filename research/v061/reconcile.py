"""Read-only reconciliation of N8 event records and retained cutoff evidence."""
from pathlib import Path
import sys
import numpy as np
from evidence import read,sha,require,write,finite,pair_distance,safe
from run_event import frozen
from fold import margin,require_character,separation_law
from search import acceptance,projected_gradient
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'recovery'))
from run_recovery import recovery_plan
from search_recovery import curvature_agreement


def diagnostics(row):
    require(row['max_eigen_residual']<1e-10 and row['max_reality']<1e-9 and row['max_hermitian']<1e-9,'eigen/basis guard failed')


def validate_open(row,p):
    require(len(row['trials'])==2,'two opening meshes required');attempts=0;retries=0
    for trial,ng,ne in zip(row['trials'],p['grids'],p['edge_grids']):
        require(trial['grid']==ng and trial['boundary']['segments']==ne,'opening mesh changed')
        grid=trial['grid_values'];require(len(grid)==ng+1 and all(len(q)==ng+1 for q in grid),'opening grid incomplete')
        require(trial['grid_min']==min(min(q) for q in grid),'opening grid minimum mismatch')
        edges=trial['boundary']['edges'];require(len(edges)==4 and {(e['axis'],e['fixed']) for e in edges}=={(0,0.),(0,1.),(1,0.),(1,1.)},'opening edges incomplete')
        for edge in edges:
            require(len(edge['values'])==ne+1,'edge mesh incomplete')
            require(edge['minimum']==min(edge['candidates'],key=lambda q:q['gap']),'edge minimum mismatch')
            require(edge['minimum']['gap']<=min(edge['values'])+p['thresholds']['nonworsening'],'edge worsens grid')
            for q in edge['candidates']:
                require(q['f'][edge['axis']]==edge['fixed'],'edge point left edge')
                if q['kind']=='optimized':require(q['success'] and q['valid'],'failed edge result promoted')
        require(trial['boundary']['minimum']==min(e['minimum']['gap'] for e in edges),'boundary minimum mismatch')
        require(trial['refinements'] and trial['minimum']==min(trial['refinements'],key=lambda q:q['gap']),'selected opening minimum mismatch')
        for q in trial['refinements']:
            a=q['attempts'][-1];attempts+=len(q['attempts']);retries+=len(q['attempts'])-1
            require(a['success'] and a['valid'],'failed final opening optimizer')
            require(q['gap']==a['checked_value'] and q['f']==a['f'],'stale opening result metadata')
            require(abs(q['gap']-a['optimizer_value'])<=p['thresholds']['value_consistency'],'opening value mismatch')
            require(margin(q['f'],p['box'])>=0 and q['gap']<=q['initial']+p['thresholds']['nonworsening'],'opening escaped or worsened seed')
            require(q['projected_gradient']==a['projected_gradient']==projected_gradient(q['f'],q['gradient']) and q['projected_gradient']<=p['thresholds']['projected_gradient'],'opening stationarity failed')
        require(trial['minimum']['gap']<=min(trial['grid_min'],trial['boundary']['minimum'])+p['thresholds']['nonworsening'],'minimum worsens sample')
        require([q['step'] for q in trial['curvature']]==p['thresholds']['curvature_steps'] and all(min(q['eigenvalues'])>0 for q in trial['curvature']),'opening curvature failed')
    for trial in row['trials']:
        require(trial['curvature_agreement']==curvature_agreement(trial['curvature'],p['thresholds']),'stale curvature agreement')
        for q in trial['refinements']:
            a=q['attempts'][-1]
            if a['method']=='Newton-gradient':
                require(a['polish_steps'] and a['polish_steps'][-1]['f']==a['f'] and a['polish_steps'][-1]['gap']==a['checked_value'] and a['polish_steps'][-1]['projected_gradient']==a['projected_gradient'],'stale Newton metadata')
    result=acceptance(row['trials'],p['thresholds']);require(all(row[k]==v for k,v in result.items()),'stale opening acceptance')
    diagnostics(row['diagnostics']);return dict(T=row['T'],**result,optimizer_attempts=attempts,fallback_attempts=retries,newton_polishes=sum(a['method']=='Newton-gradient' for t in row['trials'] for q in t['refinements'] for a in q['attempts']),sampled_points=row['sampled_points'])


def validate_transport(t,steps,index):
    require(t['steps']==steps and t['min_external_gap']>1e-5 and t['min_overlap']>.1,'comparison path unresolved')
    ts=t['initial_t'];gaps=np.asarray(t['initial_exterior_gaps']);require(ts==sorted(set(ts)) and ts[0]==0 and ts[-1]==1 and gaps.shape==(len(ts),2) and gaps.min()>1e-5,'spatial sample grid incomplete')
    require(t['samples']>=len(ts),'spatial refinement missing')
    for q in t['located_gap_minima']:
        require(q['gap_index'] in [index-1,index+1] and q['success'] and q['status']==0 and q['valid'] and q['nfev']>0,'failed spatial minimum promoted')
        require(q['bracket'][0]<=q['t']<=q['bracket'][1] and 1e-5<q['gap']<=q['initial']+1e-7,'invalid located gap')
        require(t['min_external_gap']<=q['gap']+1e-10,'located gap omitted from transport')
    for col,gi in enumerate([index-1,index+1]):
        expected=[[ts[j-1],ts[j+1]] for j in range(1,len(ts)-1) if gaps[j,col]<=min(gaps[j-1,col],gaps[j+1,col])]
        require(expected==[q['bracket'] for q in t['located_gap_minima'] if q['gap_index']==gi],'exterior minimum not refined')


def validate_pair(m,index,radius,label,p):
    require(m['label']==label and len(m['nodes'])==2,'pair label/root count mismatch')
    for n in m['nodes']:
        require(n['success'] and n['status']>0 and n['nfev']>0 and n['index']==index and n['residual']<1e-6 and 0<=n['gap']<1e-6 and margin(n['f'],p['box'])>.005,'pair root unresolved')
        require(n['domain_margin']==margin(n['f'],p['box']),'root domain margin mismatch')
    separation=float(np.linalg.norm(np.array(m['nodes'][0]['f'])-m['nodes'][1]['f']))
    require(separation==m['separation'] and 0<radius<separation/3,'pair loops overlap or separation mismatch')
    require(m['spatial_mesh_determinant']>.99 and len(m['spatial_transport'])==2,'spatial mesh disagreement')
    for t,steps in zip(m['spatial_transport'],[128,256]):validate_transport(t,steps,index)
    trials=m['trials'];require(len(trials)==3,'charge refinements missing');meshes=[t['points'] for t in trials]
    require(meshes in [[256,512,512],[1024,2048,2048]],'wrong charge meshes')
    if meshes[0]==1024:require(len(m['rejected_stages'])==1 and m['rejected_stages'][0]['reason']=='loop phase steps unresolved','unjustified loop retry')
    else:require(not m['rejected_stages'],'unexpected loop retry')
    for t,r in zip(trials,[radius,radius,radius/2]):
        require(t['radius']==r and t['label']==label,'loop radius or label mismatch')
        for side in ['a','b']:
            q=t[side];require(abs(q['charge'])==1 and abs(q['winding']-q['charge'])<.05 and q['max_phase_step']<np.pi/2 and q['min_loop_gap']>1e-6 and q['min_chart_overlap']>.1,'loop charge unresolved')
        require(t['a']['charge']*t['b']['charge']==(1 if label=='SAME' else -1),'charge signs disagree with label')
    require(all(len({t[side]['charge'] for t in trials})==1 for side in ['a','b']),'charge mesh/radius disagreement');diagnostics(m['diagnostics'])
    return dict(label=label,separation=separation,meshes=meshes,rejected_stages=len(m['rejected_stages']),min_comparison_gap=min(t['min_external_gap'] for t in m['spatial_transport']),min_overlap=min(t['min_overlap'] for t in m['spatial_transport']),sampled_points=m['sampled_points'])


def validate_charge(row,state,p):
    require(row['T']==state['T'],'wrong charge station');m=row['measurement'];radius=min(.002,state['separation']/8)
    join=pair_distance(m['nodes'],state['nodes']);require(row['root_join']==join and join<1e-6,'charge root join mismatch')
    require([n['seed'] for n in m['nodes']]==[n['f'] for n in state['nodes']],'charge seeds differ from continued roots')
    return dict(T=row['T'],root_join=join,**validate_pair(m,p['gap_index'],radius,'OPPOSITE',p))


def validate_case(c,engine,p,ph):
    p=dict(p,thresholds=recovery_plan()['thresholds'])
    finite(c);require(c['status']=='ACCEPT_COMBINED_FIRST_ANN','case incomplete or rejected')
    require(c['engine']==engine and c['N']==8 and c['case']=='first_ann' and c['state']==p['state'],'case identity changed')
    require(c['numerical_plan_sha256']==ph,'plan identity changed')
    require(c['kinetic']=='lab_nn_full' and c['geometry']==p['geometry'][engine] and c['cutoff_tol']==p['cutoff_tol'][engine],'model convention changed')
    require(c['runtime_before']==c['runtime_after'] and all(v=='1' for v in c['runtime_before']['thread_environment'].values()),'runtime changed')
    event=c['event'];value=event['parameter'];trials=event['fold_trials']
    require(p['T_window'][1]<value-p['opening_offset']<value<p['state']['T'],'fold outside window')
    require([q['h'] for q in trials]==[2e-5,1e-5],'fold derivative meshes changed')
    require(value==trials[-1]['parameter'] and event['f']==trials[-1]['f'],'fold final result mismatch')
    require(abs(trials[0]['parameter']-trials[1]['parameter'])<1e-6,'fold refinement failed')
    for q in trials:
        require(q['success'] and q['nfev']>0,'failed fold optimizer promoted')
        require(np.linalg.norm(q['residual'][:2])<1e-6 and 0<=q['gap']<1e-6,'fold unresolved')
        require(q['singular_values'][-1]<1e-3 and q['singular_values'][0]>1 and q['external_gap']>1e-5 and margin(q['f'],p['box'])>.005,'fold rank/isolation/domain failed');diagnostics(q['diagnostics'])
    nd=c['nondegeneracy'];require(nd['status']=='PASS' and [q['step'] for q in nd['trials']]==[2e-4,1e-4],'nondegeneracy meshes missing');require_character(nd['trials'],1.)
    stations=sorted(set(np.linspace(p['state']['T'],value+p['regular_last_offset'],p['regular_states']).tolist()+[value+off for off in p['extra_root_offsets']]),reverse=True)
    require(len(c['states'])==p['root_states']==len(stations),'root stations incomplete')
    previous=event['initial_nodes'];laws=[]
    require(len(previous)==2 and all(n['success'] and n['index']==p['gap_index'] and n['residual']<1e-6 for n in previous),'initial roots failed')
    require([n['seed'] for n in previous]==p['seeds'][engine],'initial seeds changed')
    for T,row in zip(stations,c['states']):
        require(row['T']==T and len(row['nodes'])==2,'wrong root station')
        require(all(n['seed']==old['f'] for n,old in zip(row['nodes'],previous)),'continuation seed changed')
        for n in row['nodes']:require(n['success'] and n['index']==p['gap_index'] and n['residual']<1e-6 and 0<=n['gap']<1e-6 and margin(n['f'],p['box'])>.005,'root gate failed')
        separation=float(np.linalg.norm(np.array(row['nodes'][0]['f'])-row['nodes'][1]['f']));jump=max(float(np.linalg.norm(np.array(n['f'])-old['f'])) for n,old in zip(row['nodes'],previous))
        require(separation==row['separation'] and jump==row['max_jump'] and separation>p['minimum_separation'] and jump<p['max_root_jump'],'root jump/separation mismatch');diagnostics(row['diagnostics'])
        if any(abs(T-value-off)<1e-12 for off in p['law_offsets']):
            law=separation_law(separation,T-value,nd['trials'][-1]['squared_separation_coefficient'],p['law_tolerance']);require(row['separation_law']==law,'separation law mismatch');laws.append(law)
        previous=row['nodes']
    require(len(laws)==len(p['law_offsets']) and c['states'][-1]['separation']<c['states'][0]['separation'],'pair not closing or law stations missing')
    require(len(c['charges'])==p['charge_stations'] and len(c['open_checks'])==p['open_stations'],'event witnesses incomplete')
    charges=[]
    for row,T in zip(c['charges'],[p['state']['T'],value+p['charge_offset']]):
        state=next(q for q in c['states'] if q['T']==T);charges.append(validate_charge(row,state,p))
    openings=[]
    for row,T in zip(c['open_checks'],[value-p['opening_offset'],p['T_window'][1]]):
        require(row['T']==T,'wrong opening station');openings.append(validate_open(row,p))
    require('post_transfer' in c,'post-transfer witness missing')
    upper=c['post_transfer'];require(upper['T']==p['T_window'][1] and upper['index']==4,'wrong post-transfer station')
    post=validate_pair(upper['measurement'],4,p['upper_radius'],'SAME',p)
    require([n['seed'] for n in upper['measurement']['nodes']]==p['upper_seeds'][engine],'post-transfer seed identity changed')
    return dict(engine=engine,N=8,dimension=c['dimension'],geometry=c['geometry'],fold_parameter=value,fold_f=event['f'],fold_external_gap=trials[-1]['external_gap'],fold_derivative_difference=abs(trials[0]['parameter']-trials[1]['parameter']),
                normal_form_coefficient=nd['trials'][-1]['squared_separation_coefficient'],root_states=len(c['states']),separation_law=laws,charges=charges,openings=openings,post_transfer=dict(T=upper['T'],**post),recovery=c['recovery_provenance'],seconds=c['seconds'])


def combine(original,recovered,engine,initial_hash,recovery_hash):
    rp=recovery_plan()
    require(original['status']=='REJECT' and original['failure']['message']==rp['expected_rejections'][engine],'unexpected initial rejection')
    require(recovered['status']=='ACCEPT_RECOVERED_WITNESSES' and recovered['engine']==engine and recovered['N']==8,'recovery incomplete or rejected')
    require(recovered['initial_result_sha256']==initial_hash and recovered['recovery_plan_sha256']==sha(ROOT/'recovery/NUMERICAL_PLAN.json'),'recovery evidence identity changed')
    require(original['runtime_before']==original['runtime_after']==recovered['runtime_before']==recovered['runtime_after'],'reused and recovered runtimes differ')
    result=dict(original,status='ACCEPT_COMBINED_FIRST_ANN',open_checks=recovered['open_checks'],post_transfer=recovered['post_transfer'],seconds=original['seconds']+recovered['seconds'])
    result['recovery_provenance']=dict(initial_status=original['status'],initial_failure=original['failure']['message'],initial_result_sha256=initial_hash,recovery_status=recovered['status'],recovery_result_sha256=recovery_hash,recovery_plan_sha256=recovered['recovery_plan_sha256'],initial_seconds=original['seconds'],recovery_seconds=recovered['seconds'])
    return result


def load_case(engine):
    # recovery_plan checks the preserved rejected artifacts against its freeze.
    recovery_plan();initial=ROOT/'results'/f'first_ann_{engine}_N8.json';recovered=ROOT/'results'/f'opening_recovery_{engine}_N8.json'
    return combine(read(initial),read(recovered),engine,sha(initial),sha(recovered))


def build():
    p=frozen();ph=sha(ROOT/'NUMERICAL_PLAN.json');targets=read(ROOT/'HISTORICAL_TARGETS.json');cases=[];comparisons=[];hashes={};repo=ROOT.parents[1]
    for engine in p['engines']:
        path=ROOT/'results'/f'first_ann_{engine}_N8.json';raw=load_case(engine);case=validate_case(raw,engine,p,ph);cases.append(case)
        old=targets['cases'][engine];c6=old['6'];c4=old['4']
        for n in ['4','6']:
            h=old[n];source=safe(repo,h['source']);original=read(source);post_source=safe(repo,h['post_transfer_source']);post=read(post_source)
            require(sha(source)==h['sha256'] and original['status']=='ACCEPT' and original['definition']==h['definition'] and original['event']==h['event'] and original['nondegeneracy']==h['nondegeneracy'],'historical event anchor mismatch')
            require(all(p['state'][k]==v for k,v in h['definition']['p'].items()) and h['definition']['index']==p['gap_index'] and h['definition']['pair_at']==p['state']['T'] and h['definition']['gapped_at']==p['T_window'][1],'historical held state mismatch')
            require(h['charges']==[q['measurement']['label'] for q in original['charges']],'historical charge mismatch')
            for prefix,row in [('near',original['gapped_checks'][0]),('far',original['gapped_checks'][-1])]:
                require(h[prefix+'_open_parameter']==row['parameter'] and h[prefix+'_open_gap']==row['trials'][-1]['minimum']['gap'],'historical opening mismatch')
            require(sha(post_source)==h['post_transfer_sha256'] and post['status']=='ACCEPT' and post['state']==h['post_transfer_state'] and post['pair']==h['post_transfer_pair'],'historical upper pair mismatch')
        comparisons.append(dict(engine=engine,N4_saved_fold=c4['event']['parameter'],N6_saved_fold=c6['event']['parameter'],N8_fresh_fold=case['fold_parameter'],N8_minus_N6_fold=case['fold_parameter']-c6['event']['parameter'],N6_minus_N4_fold=c6['event']['parameter']-c4['event']['parameter'],initial_N8_N6_root_distance=pair_distance(raw['event']['initial_nodes'],c6['event']['initial_nodes']),near_open_gap_N6_saved=c6['near_open_gap'],near_open_gap_N8_fresh=case['openings'][0]['gap'],near_open_gap_difference=case['openings'][0]['gap']-c6['near_open_gap'],far_open_gap_N6_saved=c6['far_open_gap'],far_open_gap_N8_fresh=case['openings'][1]['gap'],far_open_gap_difference=case['openings'][1]['gap']-c6['far_open_gap'],charge_labels_match_saved=[q['label'] for q in case['charges']]==c6['charges'],post_transfer_label_N6_saved=c6['post_transfer_pair']['label'],post_transfer_label_N8=case['post_transfer']['label'],post_transfer_N8_N6_root_distance=pair_distance(raw['post_transfer']['measurement']['nodes'],c6['post_transfer_pair']['nodes'])))
    hashes={f.relative_to(ROOT).as_posix():sha(f) for f in sorted((ROOT/'results').glob('*.json'))}
    return dict(recovery_plan_sha256=sha(ROOT/'recovery/NUMERICAL_PLAN.json'),version='our_v061',status='BOUNDED_N8_FIRST_ANN_COMPLETE',numerical_plan_sha256=ph,state=p['state'],cases=cases,cutoff_comparisons=comparisons,input_sha256=hashes,max_abs_N8_N6_fold_shift=max(abs(c['N8_minus_N6_fold']) for c in comparisons),cross_engine_N8_fold_difference=cases[0]['fold_parameter']-cases[1]['fold_parameter'],limits=[
      'Both initial frozen runs were rejected at the opening gate. The accepted summary combines their unchanged fold/root/flat-pair evidence with separately planned, freshly measured opening and upper-pair recovery; original REJECT records are retained.',
      targets['scope'],
      'Near-event charge/opening stations follow each cutoff own fold offset. The fixed T=-0.74 comparison uses the same parameter. Retained N4/N6 environments and numerical searches are not rerun here, so these differences are not an isolated error bound on cutoff alone.',
      'Eleven root states, finite charge loops, sampled/located comparison gaps and chart/edge searches establish a bounded numerical event witness, not a continuous-interval or global node-count proof.',
      'The upper pair is measured independently at T=-0.74. SAME there does not by itself prove a continuous transfer of topological charge across the collision.',
      'Both engines share this measurement harness and constant-tunnelling lab_nn_full approximation. BM linear and reference exact reciprocal geometry are kept distinct.',
      'Absolute charge is not transported through the collision. No new full N8 campaign, flat-pair frame path, Euler class or endpoint w1 is claimed.',
      'Infinite-cutoff accuracy, microscopic tunnelling strain dependence, physical-bilayer validation and remaining historical consumer impact remain open. Source/test/result hashes are internal consistency evidence, not independent authenticity or physical truth.'])

if __name__=='__main__':
    r=build();write(ROOT/'IMPACT.json',r);print(r['status'])
