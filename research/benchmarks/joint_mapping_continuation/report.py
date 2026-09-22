"""Fresh native/frame reconstruction and audit of all intervals and joins.

Uses the published bound functions; this is not an independently coded proof.
"""
import gzip,hashlib,json
from pathlib import Path
import numpy as np
from deformation import ROOT,PLAN,CFG,make_family,model
from coupled import center_data,certificate,containment,enclosure

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def discrepancy(a,b):
    if isinstance(a,dict):
        assert set(a)==set(b),(set(a)-set(b),set(b)-set(a))
        return max((discrepancy(a[k],b[k]) for k in a),default=0.)
    if isinstance(a,list):
        assert len(a)==len(b);return max((discrepancy(x,y) for x,y in zip(a,b)),default=0.)
    if isinstance(a,(float,int)) and not isinstance(a,bool):
        return abs(a-b)/max(1.,abs(a),abs(b))
    assert a==b,(a,b);return 0.

def main():
    data=json.loads((ROOT/'RESULTS.json').read_text());frames=np.load(ROOT/'FRAMES.npz')
    if (ROOT/'RESULTS_PRODUCER.json.gz').exists():
        assert json.loads(gzip.decompress((ROOT/'RESULTS_PRODUCER.json.gz').read_bytes()))==data
    for name,h in data['source_hashes'].items():assert sha(ROOT.parent/name)==h,name
    controls=json.loads((ROOT/'CONTROLS.json').read_text());assert controls['all_controls_pass']
    fresh={};families={};maxdiff=0.;maxnative=0.;maxgap=0.;cost=0
    centers=list(data['centers'].items())
    for index,(key,old) in enumerate(centers):
        if not old['pass_check']:continue
        loc=old['locator'];e=loc['event'];d0=sum(loc['bracket'])/2
        family=make_family(old['engine'],old['s'],d0)
        # Keep only the light geometry state after each certificate reconstruction.
        families[key]=family
        raw,F=center_data([family]*3,old['s'],e['D'],e['roots'],frames=[frames[key+'_'+str(k)] for k in range(3)])
        err=discrepancy(raw,old['raw']);maxdiff=max(maxdiff,err);assert err<CFG['reconciliation_tolerance'],(key,err)
        assert loc['cost']==sum(m['result']['cost'] for m in loc['measurements'])
        cost+=loc['cost']
        for m in loc['measurements']:
            assert loc['bracket'][0]<=m['D']<=loc['bracket'][1]
            assert m['result']['cost']==sum(r['eigensolves'] for r in m['result']['roots'])+sum(c['eigensolves'] for c in m['result']['native'])
        assert abs(e['offset'])<=PLAN['locator']['event_offset_tolerance']
        for k in range(3):
            check=family.native_check(e['D'],np.array(e['roots'][k]),raw['pairs'][k]['lo']);assert check['ok']
            maxnative=max(maxnative,check['matrix_error_meV']);maxgap=max(maxgap,check['gap_meV'])
        fresh[key]=raw
        if index%32==0:print('RECONSTRUCT',index+1,'of',len(centers),flush=True)
    campaigns=[];leaf_bounds=[];total_attempts=0;failed_parents=0;unresolved=0;joins_count=0;points_count=0
    def recheck(key,h):
        raw=fresh[key];f=families[key]
        rem=[f.remainder_bounds(raw['y'][3*k:3*k+2],raw['velocity'][3*k:3*k+3],h) for k in range(3)]
        return certificate(raw,h,rem)
    for campaign in data['campaigns']:
        cs=[]
        for a in campaign['attempts']:
            total_attempts+=1
            if a['center'] not in fresh:
                assert not a['certificate']['pass_check'];continue
            check=recheck(a['center'],(a['b']-a['a'])/2)
            err=discrepancy(check,a['certificate']);maxdiff=max(maxdiff,err);assert err<CFG['reconciliation_tolerance']
            if a['children']:
                assert not a['certificate']['pass_check'];failed_parents+=1
                kids=[campaign['attempts'][i] for i in a['children']]
                assert kids[0]['a']==a['a'] and kids[-1]['b']==a['b'] and kids[0]['b']==kids[1]['a']
        leaves=[campaign['attempts'][i] for i in campaign['leaf_ids']]
        assert leaves[0]['a']==PLAN['strain_interval'][0] and leaves[-1]['b']==PLAN['strain_interval'][1]
        assert all(a['b']==b['a'] for a,b in zip(leaves[:-1],leaves[1:]))
        for a in leaves:
            cert=a['certificate'];ok=cert['pass_check']
            unresolved+=int(not ok)
            if not ok:continue
            raw=fresh[a['center']];r=np.array(cert['inner_radii']);v=np.array(raw['velocity']);y=np.array(raw['y'])
            Dends=[float(y[9]+v[9]*(s-raw['s'])) for s in [a['a'],a['b']]]
            leaf_bounds.append(dict(engine=campaign['engine'],mesh=campaign['initial_intervals'],a=a['a'],b=a['b'],
                center=a['center'],D_predictor_ends=Dends,D_inner_radius=float(r[9]),q=cert['q'],self_map=cert['self_map'],
                complement_margin=min(p['Gfull'] for p in cert['pairs']),along=cert['geometry']['along'],
                pair_separation_min=min(cert['geometry']['pair_separation_margins'])))
        for key,old in campaign['points'].items():
            points_count+=1
            if key in fresh:
                pc=recheck(key,0);err=discrepancy(pc,old);maxdiff=max(maxdiff,err);assert err<CFG['reconciliation_tolerance']
        for j in campaign['joins']:
            joins_count+=1
            leaf=campaign['attempts'][j['leaf']];pc=campaign['points'][j['point']]
            if j['point'] in fresh:
                check=containment(fresh[j['point']],pc,fresh[leaf['center']],leaf['certificate'],j['s'])
                err=discrepancy(check,j['check']);maxdiff=max(maxdiff,err);assert err<CFG['reconciliation_tolerance']
            unresolved+=int(not j['check']['pass_check'])
        endpoints=[]
        for s in PLAN['strain_interval']:
            match=next((j for j in campaign['joins'] if j['s']==s),None)
            if match:
                raw=fresh[match['point']];pc=campaign['points'][match['point']];lo,hi=enclosure(raw,pc,s,True)
                endpoints.append(dict(strain=s,D_enclosure_meV=[float(lo[9]),float(hi[9])],center=match['point']))
        campaigns.append(dict(engine=campaign['engine'],mesh=campaign['initial_intervals'],leaves=len(leaves),
                              passed=campaign['pass_check'],endpoint_enclosures=endpoints))
    shared=[]
    bm={r['s']:r for r in data['centers'].values() if r['engine']=='bm' and r['pass_check']}
    ref={r['s']:r for r in data['centers'].values() if r['engine']=='ref' and r['pass_check']}
    for s in sorted(set(bm)&set(ref)):
        a,b=bm[s],ref[s];shared.append(dict(strain=s,D_difference=abs(a['raw']['y'][9]-b['raw']['y'][9]),
            coordinate_difference=float(np.max(abs(np.array(a['locator']['event']['roots'])-b['locator']['event']['roots'])))))
    allpass=bool(unresolved==0 and len(campaigns)==4 and all(c['passed'] for c in campaigns))
    out=dict(status='RECONCILED_CONDITIONAL_EVENT_BRANCH_PASS' if allpass else 'RECONCILED_UNRESOLVED_CONTINUATION',
             all_checks_pass=allpass,campaigns=campaigns,centers=len(fresh),controls=len(controls['controls']),
             attempted_cells=total_attempts,accepted_leaves=len(leaf_bounds),failed_parents=failed_parents,
             unresolved_cells_or_joins=unresolved,point_certificates=points_count,endpoint_joins=joins_count,
             max_reconstruction_discrepancy=maxdiff,max_native_matrix_error_meV=maxnative,max_native_gap_meV=maxgap,
             locator_eigensolves=cost,producer_additional_native_eigensolves=6*len(fresh),
             report_native_eigensolves=6*len(fresh),leaf_bounds=leaf_bounds,cross_engine_shared_centers=shared,
             max_engine_D_difference_meV=max((v['D_difference'] for v in shared),default=None),
             max_engine_coordinate_difference=max((v['coordinate_difference'] for v in shared),default=None),
             source_hashes=dict(data['source_hashes']),scope=PLAN['scope'])
    for n in ['RESULTS.json','FRAMES.npz','report.py','PACKAGING.json','RESULTS_PRODUCER.json.gz']:
        if (ROOT/n).exists():out['source_hashes']['joint_mapping_continuation/'+n]=sha(ROOT/n)
    (ROOT/'SUMMARY.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(out['status'],flush=True)
    for k in ['centers','controls','attempted_cells','accepted_leaves','failed_parents','unresolved_cells_or_joins','point_certificates','endpoint_joins','max_native_matrix_error_meV','max_native_gap_meV','max_engine_D_difference_meV','max_reconstruction_discrepancy']:
        print(k,out[k],flush=True)
    for c in campaigns:print(c,flush=True)

if __name__=='__main__':main()
