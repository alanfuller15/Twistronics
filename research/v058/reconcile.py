"""Reconcile stored numerical diagnostics; never rerun an eigensolver."""
from pathlib import Path
import math
from evidence import read,sha,require,write
from run_endpoint import frozen
from search import acceptance,projected_gradient
ROOT=Path(__file__).resolve().parent


def validate_case(c, engine, p, plan_hash):
    require(c['status']=='ACCEPT_SAMPLED_ENDPOINT_GAPS','case rejected or incomplete')
    require(c['engine']==engine and c['N']==8 and c['state']==p['state'],'case identity mismatch')
    require(c['numerical_plan_sha256']==plan_hash,'case plan mismatch')
    require(c['geometry']==p['geometry'][engine] and c['cutoff_tol']==p['cutoff_tol'][engine],'model convention mismatch')
    require(c['runtime_before']==c['runtime_after'],'numerical runtime changed')
    require(all(v=='1' for v in c['runtime_before']['thread_environment'].values()),'numerical thread limits changed')
    require(c['affine_residual']<p['thresholds']['affine_residual'],'affine check failed')
    require(c['diagnostics']['max_eigen_residual']<1e-10 and c['diagnostics']['max_hermitian']<1e-9 and c['diagnostics']['max_reality']<1e-9,'sample diagnostics failed')
    require(set(c['gaps'])=={'lower','flat','upper','next'},'gap set incomplete')
    attempts=0;fallbacks=0;refinements=0;out={}
    for index,(name,row) in enumerate(c['gaps'].items()):
        require(row['index_in_eight_bands']=={'lower':2,'flat':3,'upper':4,'next':5}[name],'gap band mapping changed')
        require(row['gradient_check']['max_error']<p['thresholds']['gradient_check'],'gradient check failed')
        require(len(row['trials'])==2,'missing search trial')
        for trial,ng,ne in zip(row['trials'],p['grids'],p['edge_grids']):
            require(trial['grid']==ng and trial['boundary']['segments']==ne,'search resolution changed')
            grid=trial['grid_values'];require(len(grid)==ng+1 and all(len(r)==ng+1 for r in grid),'grid shape changed')
            require(trial['grid_min']==min(min(r) for r in grid),'grid minimum mismatch')
            edges=trial['boundary']['edges'];require({(e['axis'],e['fixed']) for e in edges}=={(0,0.),(0,1.),(1,0.),(1,1.)} and len(edges)==4,'edge coverage incomplete')
            for edge in edges:
                require(len(edge['values'])==ne+1,'edge mesh incomplete')
                require(edge['minimum']==min(edge['candidates'],key=lambda a:a['gap']),'edge minimum mismatch')
                require(edge['minimum']['gap']<=min(edge['values'])+p['thresholds']['nonworsening'],'edge worsens sample')
                for candidate in edge['candidates']:
                    require(candidate['f'][edge['axis']]==edge['fixed'],'edge point left edge')
                    if candidate['kind']=='optimized':require(candidate['success'] and candidate['valid'],'failed edge promoted')
            require(trial['boundary']['minimum']==min(e['minimum']['gap'] for e in edges),'boundary aggregation mismatch')
            require(trial['refinements'] and trial['minimum']==min(trial['refinements'],key=lambda x:x['gap']),'selected minimum mismatch')
            for r in trial['refinements']:
                final=r['attempts'][-1];attempts+=len(r['attempts']);refinements+=1;fallbacks+=len(r['attempts'])-1
                require(final['success'] and final['valid'],'failed final optimizer promoted')
                require(r['gap']==final['checked_value'] and r['f']==final['f'],'stale final result metadata')
                require(abs(r['gap']-final['optimizer_value'])<=p['thresholds']['value_consistency'],'optimizer value mismatch')
                require(all(0<=f<=1 for f in r['f']) and r['gap']<=r['initial']+p['thresholds']['nonworsening'],'refinement escaped or worsened')
                require(r['projected_gradient']==final['projected_gradient']==projected_gradient(r['f'],r['gradient']) and r['projected_gradient']<=p['thresholds']['projected_gradient'],'stationarity failed')
            require(trial['minimum']['gap']<=min(trial['grid_min'],trial['boundary']['minimum'])+p['thresholds']['nonworsening'],'selected gap worsens sample')
            require([r['step'] for r in trial['curvature']]==p['thresholds']['curvature_steps'] and all(min(r['eigenvalues'])>0 for r in trial['curvature']),'curvature failed')
        recomputed=acceptance(row['trials'],p['thresholds'])
        require(all(row[k]==v for k,v in recomputed.items()),'stale acceptance summary')
        best=min(row['trials'],key=lambda t:t['minimum']['gap'])['minimum']
        out[name]=dict(**recomputed,f=best['f'],projected_gradient=best['projected_gradient'],curvature_min=min(v for t in row['trials'] for r in t['curvature'] for v in r['eigenvalues']))
    return dict(engine=engine,N=8,dimension=c['dimension'],geometry=c['geometry'],cutoff_tol=c['cutoff_tol'],gaps=out,refinements=refinements,optimizer_attempts=attempts,fallback_attempts=fallbacks,sampled_points=c['sampled_points'],seconds=c['seconds'],diagnostics=c['diagnostics'])


def build():
    p=frozen();ph=sha(ROOT/'NUMERICAL_PLAN.json');targets=read(ROOT/'HISTORICAL_TARGETS.json');cases=[];hashes={};rows=[]
    for engine in p['engines']:
        path=ROOT/'results'/f'{engine}_N8.json';raw=read(path);case=validate_case(raw,engine,p,ph);cases.append(case);hashes[path.relative_to(ROOT).as_posix()]=sha(path)
        for gap,new in case['gaps'].items():
            old4=targets['cases'][engine]['4']['gaps'][gap];old6=targets['cases'][engine]['6']['gaps'][gap]
            rows.append(dict(engine=engine,gap=gap,N4_saved=old4['gap'],N6_saved=old6['gap'],N8_fresh=new['gap'],N8_minus_N6=new['gap']-old6['gap'],N6_minus_N4=old6['gap']-old4['gap'],N8_N6_coordinate_distance=math.dist(new['f'],old6['f'])))
    partner=[]
    for gap,old in targets['partner_N8'].items():
        new=cases[1]['gaps'][gap];dv=new['gap']-old['printed_gap'];df=math.dist(new['f'],old['f'])
        partner.append(dict(gap=gap,printed_gap=old['printed_gap'],fresh_gap=new['gap'],difference=dv,coordinate_distance=df,agrees_with_rounded_output=abs(dv)<=p['comparison_tolerances']['partner_printed_gap'] and df<=p['comparison_tolerances']['partner_coordinate']))
    return dict(version='our_v058',status='BOUNDED_N8_ENDPOINT_COMPARISON_COMPLETE',numerical_plan_sha256=ph,kinetic=p['kinetic'],state=p['state'],cases=cases,cutoff_comparisons=rows,partner_comparisons=partner,
      maximum_abs_N8_N6_gap_change=max(abs(x['N8_minus_N6']) for x in rows),maximum_cross_engine_gap_difference=max(abs(cases[0]['gaps'][g]['gap']-cases[1]['gaps'][g]['gap']) for g in cases[0]['gaps']),
      input_sha256=hashes,partner_run_binding=targets['partner_run_binding'],limits=[
      'N8 alone is freshly executed. N4/N6 values are read from hashed retained v048 endpoint records, not rerun here.',
      'Whole-chart grids, edge brackets and multistart cover finite samples; they do not certify a global minimum, continuous isolation or infinite-cutoff error.',
      'Both engines use lab_nn_full with constant w1=110 meV, w0=121 meV, kappa=0; BM uses linear and reference exact reciprocal geometry. They share this measurement harness.',
      'No N8 path replay, node-charge, Euler or w1 measurement is performed. Previous topology labels are retained without a new N8 certification.',
      'The supplied historical stdout is not bound to the current instrumented source or an independently established runtime; no original optimizer-failure claim is inferred.',
      'Physical-bilayer validation and a microscopic tunnelling strain law remain outside the measured model.'])


if __name__=='__main__':
    r=build();write(ROOT/'IMPACT.json',r);print(r['status'])
