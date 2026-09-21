"""Revalidate recorded lower-event diagnostics before reporting acceptance."""
from dataclasses import asdict
import numpy as np
from ledger_guard import accepted
from lower_case import CASES
from measure import require
from local_domain import inside_margin
from protocol import match

def validate(path,protocol):
    r=accepted(path);c=CASES['lower_unlink'];box=c['box']
    require(r.get('scope')=='FULL_CHART_LOWER_GAP_SEARCH','wrong gap scope')
    require(r.get('case')=='lower_unlink' and r.get('protocol_sha256')==protocol,'case/protocol mismatch')
    require(r['engine'] in ['bm_lab','ref_lab'] and r['N'] in [4,6],'unknown model/cutoff')
    require(r['kinetic']=='lab_nn_full' and r['geometry']==('linear' if r['engine']=='bm_lab' else 'exact'),'wrong model tag')
    require(r['definition']=={**c,'p':asdict(c['p'])},'changed event definition')
    require(len(r['states'])==9 and len(r['charges'])==2 and len(r['open_checks'])==2,'incomplete event stations')
    ev=r['event'];value=ev['parameter'];fold=ev['fold_trials']
    require(c['gapped_at']<value-c['delta']<value+c['delta']<c['pair_at'],'fold parameter outside window')
    require([x['h'] for x in fold]==[2e-5,1e-5],'derivative refinement missing')
    require(ev['parameter']==fold[-1]['parameter'] and ev['f']==fold[-1]['f'],'fold result mismatch')
    require(abs(fold[0]['parameter']-fold[1]['parameter'])<1e-6,'derivative refinement fails')
    for trial in fold:
        require(inside_margin(trial['f'],box)>.005,'fold outside chart')
        require(np.linalg.norm(trial['residual'][:2])<1e-6 and 0<=trial['gap']<1e-6,'unresolved fold')
        require(trial['singular_values'][-1]<1e-3 and trial['singular_values'][0]>1. and trial['external_gap']>1e-5,'fold rank/isolation failure')
    nd=r['nondegeneracy'];require(nd['status']=='PASS' and nd['engine']==r['engine'] and nd['N']==r['N'] and nd['case']=='lower_unlink','nondegeneracy identity missing')
    trials=nd['trials'];require([t['step'] for t in trials]==[2e-4,1e-4],'nondegeneracy refinement missing')
    for t in trials:
        curvature=t['curvature'];slope=t['parameter_slope']
        require(abs(curvature)>1 and abs(slope)>.01 and -2*slope/curvature>0,'wrong fold character or side')
        require(np.isclose(t['squared_separation_coefficient'],-8*slope/curvature,rtol=1e-12,atol=0),'fold coefficient mismatch')
    for key in ['curvature','parameter_slope']:
        require(abs(trials[1][key]-trials[0][key])<.01*abs(trials[1][key]),'fold character refinement')
    from run_unlink import anchor_join
    actual_join=anchor_join(r['engine'],r['N'],ev['initial_nodes'])
    require(r['v044_lower_root_join']==actual_join,'anchor join mismatch')
    stations=np.linspace(c['pair_at'],value+c['delta'],9);previous=ev['initial_nodes']
    for station,row in zip(stations,r['states']):
        require(row['T']==float(station),'wrong root station')
        require(len(row['nodes'])==2,'missing lower root')
        for n in row['nodes']:
            require(n['index']==2 and 0<=n['gap']<1e-6 and inside_margin(n['f'],box)>.005,'wrong index or unresolved root')
        distance=float(np.linalg.norm(np.array(row['nodes'][0]['f'])-row['nodes'][1]['f']))
        jump=max(float(np.linalg.norm(np.array(n['f'])-p['f'])) for n,p in zip(row['nodes'],previous))
        require(distance>.001 and jump<.06,'duplicate roots or excessive jump')
        require(abs(distance-row['separation'])<1e-12 and abs(jump-row['max_jump'])<1e-12,'root diagnostics disagree')
        require(row['diagnostics']['max_eigen_residual']<1e-10 and row['diagnostics']['max_reality']<1e-9 and row['diagnostics']['max_hermitian']<1e-9,'eigen/basis guard failed')
        previous=row['nodes']
    require(r['states'][-1]['separation']<r['states'][0]['separation'],'roots do not approach fold')
    for row,state in zip(r['charges'],[r['states'][0],r['states'][-1]]):
        m=row['measurement'];radius=min(.002,state['separation']/8)
        require(row['T']==state['T'] and m['label']=='OPPOSITE','charge measured wrong station/label')
        require(row['root_join']==match(m['nodes'],state['nodes']),'charge root join mismatch')
        require(all(n['index']==2 and 0<=n['gap']<1e-6 for n in m['nodes']),'charge measured wrong gap')
        require(m['spatial_mesh_determinant']>.99,'spatial mesh orientation disagreement')
        require(len(m['spatial_transport'])==2 and all(t['min_external_gap']>1e-5 and t['min_overlap']>.1 for t in m['spatial_transport']),'spatial comparison not isolated/resolved')
        require(len(m['trials'])==3,'charge refinement missing')
        meshes=[t['points'] for t in m['trials']]
        require(meshes in [[256,512,512],[1024,2048,2048]],'wrong loop mesh')
        if meshes[0]==1024:
            require(len(m['rejected_stages'])==1 and m['rejected_stages'][0]['reason']=='loop phase steps unresolved','unjustified loop fallback')
        else:require(not m['rejected_stages'],'unexpected loop failure')
        for t,rad in zip(m['trials'],[radius,radius,radius/2]):
            require(abs(t['radius']-rad)<1e-12 and t['label']=='OPPOSITE','radius/label mismatch')
            require(t['a']['charge']*t['b']['charge']==-1,'charges not opposite')
            for side in ['a','b']:
                q=t[side]
                require(abs(q['charge'])==1 and abs(q['winding']-q['charge'])<.05 and q['min_loop_gap']>1e-6 and q['max_phase_step']<np.pi/2 and q['min_chart_overlap']>.1,'unresolved loop charge')
        for side in ['a','b']:require(len({t[side]['charge'] for t in m['trials']})==1,'charge disagreement')
    for row,T in zip(r['open_checks'],[value-c['delta'],c['gapped_at']]):
        require(row['T']==T,'wrong open-side station')
        require([t['grid'] for t in row['trials']]==[18,24],'open-side mesh refinement missing')
        vals=[]
        for t in row['trials']:
            require(t['refinements'],'missing gap refinements')
            for q in t['refinements']:
                require(inside_margin(q['f'],box)>=-1e-12 and q['attempts'][-1]['success'],'gap optimizer failed or escaped chart')
            require(t['minimum']==min(t['refinements'],key=lambda q:q['gap']),'selected minimum mismatch')
            require(t['minimum']['gap']<=t['grid_min']+1e-7,'minimum worse than sampled grid')
            vals.append(t['minimum']['gap'])
        require(min(vals)>1e-5 and abs(vals[0]-vals[1])<.01,'opening unresolved or grid disagreement')
        require([b['grid'] for b in row['boundary']]==[24,48],'boundary refinement missing')
        vals=[]
        for b in row['boundary']:
            require(b['box']==box and len(b['edges'])==4,'missing chart boundary')
            require({(e['fixed_axis'],e['fixed']) for e in b['edges']}=={(i,v) for i in [0,1] for v in [0.,1.]},'incomplete boundary edges')
            require(b['minimum']==min(e['minimum']['gap'] for e in b['edges']),'boundary minimum mismatch')
            vals.append(b['minimum'])
        require(min(vals)>1e-5 and abs(vals[0]-vals[1])<.01,'boundary unresolved or grid disagreement')
    return r
