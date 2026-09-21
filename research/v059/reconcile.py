"""Read-only reconciliation of N8 event records and retained cutoff evidence."""
from pathlib import Path
import numpy as np
from evidence import read,sha,require,write,finite,pair_distance
from run_event import frozen
from fold import margin,require_character,separation_law
from search import acceptance,projected_gradient
ROOT=Path(__file__).resolve().parent


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
    result=acceptance(row['trials'],p['thresholds']);require(all(row[k]==v for k,v in result.items()),'stale opening acceptance')
    diagnostics(row['diagnostics']);return dict(T=row['T'],**result,optimizer_attempts=attempts,fallback_attempts=retries,sampled_points=row['sampled_points'])


def validate_charge(row,state,p):
    m=row['measurement'];radius=min(.002,state['separation']/8)
    require(row['T']==state['T'] and m['label']=='OPPOSITE','wrong charge station or label')
    join=pair_distance(m['nodes'],state['nodes']);require(row['root_join']==join and join<1e-6,'charge root join mismatch')
    require(len(m['nodes'])==2 and all(n['index']==2 and 0<=n['gap']<1e-6 for n in m['nodes']),'charge root unresolved')
    require(m['spatial_mesh_determinant']>.99,'spatial orientation mismatch')
    require(len(m['spatial_transport'])==2,'two spatial meshes required')
    for t in m['spatial_transport']:
        require(t['min_external_gap']>1e-5 and t['min_overlap']>.1,'comparison path unresolved')
        require(all(q['gap']>1e-5 for q in t['located_gap_minima']),'located isolation failed')
    trials=m['trials'];require(len(trials)==3,'charge mesh/radius refinement missing')
    meshes=[t['points'] for t in trials];require(meshes in [[256,512,512],[1024,2048,2048]],'wrong loop meshes')
    if meshes[0]==1024:require(len(m['rejected_stages'])==1 and m['rejected_stages'][0]['reason']=='loop phase steps unresolved','unjustified phase retry')
    else:require(not m['rejected_stages'],'unexpected rejected charge stage')
    for t,radius_expected in zip(trials,[radius,radius,radius/2]):
        require(abs(t['radius']-radius_expected)<1e-12 and t['label']=='OPPOSITE','wrong loop radius or label')
        require(t['a']['charge']*t['b']['charge']==-1,'charges not opposite')
        for side in ['a','b']:
            q=t[side];require(abs(q['charge'])==1 and abs(q['winding']-q['charge'])<.05 and q['max_phase_step']<np.pi/2 and q['min_loop_gap']>1e-6 and q['min_chart_overlap']>.1,'loop charge unresolved')
    require(all(len({t[side]['charge'] for t in trials})==1 for side in ['a','b']),'charge changes with radius or mesh')
    diagnostics(m['diagnostics'])
    return dict(T=row['T'],label=m['label'],root_join=join,meshes=meshes,min_comparison_gap=min(t['min_external_gap'] for t in m['spatial_transport']),min_overlap=min(t['min_overlap'] for t in m['spatial_transport']))


def validate_case(c,engine,p,ph):
    finite(c);require(c['status']=='ACCEPT_SAMPLED_LOWER_UNLINK','case incomplete or rejected')
    require(c['engine']==engine and c['N']==8 and c['case']=='lower_unlink' and c['state']==p['state'],'case identity changed')
    require(c['numerical_plan_sha256']==ph,'plan identity changed')
    require(c['kinetic']=='lab_nn_full' and c['geometry']==p['geometry'][engine] and c['cutoff_tol']==p['cutoff_tol'][engine],'model convention changed')
    require(c['runtime_before']==c['runtime_after'] and all(v=='1' for v in c['runtime_before']['thread_environment'].values()),'runtime changed')
    event=c['event'];value=event['parameter'];trials=event['fold_trials']
    require(p['T_window'][1]<value-p['opening_offset']<value<0,'fold outside window')
    require([q['h'] for q in trials]==[2e-5,1e-5],'fold derivative meshes changed')
    require(value==trials[-1]['parameter'] and event['f']==trials[-1]['f'],'fold final result mismatch')
    require(abs(trials[0]['parameter']-trials[1]['parameter'])<1e-6,'fold refinement failed')
    for q in trials:
        require(q['success'] and q['nfev']>0,'failed fold optimizer promoted')
        require(np.linalg.norm(q['residual'][:2])<1e-6 and 0<=q['gap']<1e-6,'fold unresolved')
        require(q['singular_values'][-1]<1e-3 and q['singular_values'][0]>1 and q['external_gap']>1e-5 and margin(q['f'],p['box'])>.005,'fold rank/isolation/domain failed');diagnostics(q['diagnostics'])
    nd=c['nondegeneracy'];require(nd['status']=='PASS' and [q['step'] for q in nd['trials']]==[2e-4,1e-4],'nondegeneracy meshes missing');require_character(nd['trials'],1.)
    stations=sorted(set(np.linspace(0,value+p['regular_last_offset'],p['regular_states']).tolist()+[value+off for off in p['extra_root_offsets']]),reverse=True)
    require(len(c['states'])==p['root_states']==len(stations),'root stations incomplete')
    previous=event['initial_nodes'];laws=[]
    require(len(previous)==2 and all(n['success'] and n['index']==2 and n['residual']<1e-6 for n in previous),'initial roots failed')
    for T,row in zip(stations,c['states']):
        require(row['T']==T and len(row['nodes'])==2,'wrong root station')
        for n in row['nodes']:require(n['success'] and n['index']==2 and n['residual']<1e-6 and 0<=n['gap']<1e-6 and margin(n['f'],p['box'])>.005,'root gate failed')
        separation=float(np.linalg.norm(np.array(row['nodes'][0]['f'])-row['nodes'][1]['f']));jump=max(float(np.linalg.norm(np.array(n['f'])-old['f'])) for n,old in zip(row['nodes'],previous))
        require(separation==row['separation'] and jump==row['max_jump'] and separation>p['minimum_separation'] and jump<p['max_root_jump'],'root jump/separation mismatch');diagnostics(row['diagnostics'])
        if any(abs(T-value-off)<1e-12 for off in p['law_offsets']):
            law=separation_law(separation,T-value,nd['trials'][-1]['squared_separation_coefficient'],p['law_tolerance']);require(row['separation_law']==law,'separation law mismatch');laws.append(law)
        previous=row['nodes']
    require(len(laws)==len(p['law_offsets']) and c['states'][-1]['separation']<c['states'][0]['separation'],'pair not closing or law stations missing')
    require(len(c['charges'])==p['charge_stations'] and len(c['open_checks'])==p['open_stations'],'event witnesses incomplete')
    charges=[]
    for row,T in zip(c['charges'],[0,value+p['charge_offset']]):
        state=next(q for q in c['states'] if q['T']==T);charges.append(validate_charge(row,state,p))
    openings=[]
    for row,T in zip(c['open_checks'],[value-p['opening_offset'],p['T_window'][1]]):
        require(row['T']==T,'wrong opening station');openings.append(validate_open(row,p))
    return dict(engine=engine,N=8,dimension=c['dimension'],geometry=c['geometry'],fold_parameter=value,fold_f=event['f'],fold_external_gap=trials[-1]['external_gap'],fold_derivative_difference=abs(trials[0]['parameter']-trials[1]['parameter']),
                normal_form_coefficient=nd['trials'][-1]['squared_separation_coefficient'],root_states=len(c['states']),separation_law=laws,charges=charges,openings=openings,seconds=c['seconds'])


def build():
    p=frozen();ph=sha(ROOT/'NUMERICAL_PLAN.json');targets=read(ROOT/'HISTORICAL_TARGETS.json');cases=[];comparisons=[];hashes={}
    for engine in p['engines']:
        path=ROOT/'results'/f'lower_unlink_{engine}_N8.json';raw=read(path);case=validate_case(raw,engine,p,ph);cases.append(case);hashes[path.relative_to(ROOT).as_posix()]=sha(path)
        old=targets['cases'][engine];c6=old['6'];c4=old['4']
        comparisons.append(dict(engine=engine,N4_saved_fold=c4['event']['parameter'],N6_saved_fold=c6['event']['parameter'],N8_fresh_fold=case['fold_parameter'],
          N8_minus_N6_fold=case['fold_parameter']-c6['event']['parameter'],N6_minus_N4_fold=c6['event']['parameter']-c4['event']['parameter'],initial_N8_N6_root_distance=pair_distance(raw['event']['initial_nodes'],c6['event']['initial_nodes']),
          near_open_gap_N6_saved=c6['near_open_gap'],near_open_gap_N8_fresh=case['openings'][0]['gap'],near_open_gap_difference=case['openings'][0]['gap']-c6['near_open_gap'],
          far_open_gap_N6_saved=c6['far_open_gap'],far_open_gap_N8_fresh=case['openings'][1]['gap'],far_open_gap_difference=case['openings'][1]['gap']-c6['far_open_gap'],
          charge_labels_match_saved=[q['label'] for q in case['charges']]==c6['charges']))
    return dict(version='our_v059',status='BOUNDED_N8_LOWER_UNLINK_COMPLETE',numerical_plan_sha256=ph,state=p['state'],cases=cases,cutoff_comparisons=comparisons,input_sha256=hashes,
      max_abs_N8_N6_fold_shift=max(abs(c['N8_minus_N6_fold']) for c in comparisons),cross_engine_N8_fold_difference=cases[0]['fold_parameter']-cases[1]['fold_parameter'],
      limits=['N8 is fresh; N4/N6 are hashed retained v055 evidence. Near-event charge/opening stations use each cutoff\'s own fold offset, not identical absolute T.',
      'This covers one N8 event with finite root, loop, transport and gap samples, not the complete N8 campaign or a continuous-interval proof.',
      'Positive finite chart/edge searches do not certify a global zero count; square-root agreement and derivative refinement are local numerical evidence.',
      'Both engines share the measurement harness and constant-tunnelling lab_nn_full approximation; BM linear and reference exact reciprocal geometry are kept distinct.',
      'Absolute charge is not transported through the collision. The flat-pair frame path, Euler class and endpoint w1 are not remeasured here.',
      'Infinite-cutoff accuracy, microscopic tunnelling strain dependence, physical-bilayer validation and remaining historical consumer impact are not established.'])


if __name__=='__main__':
    r=build();write(ROOT/'IMPACT.json',r);print(r['status'])
