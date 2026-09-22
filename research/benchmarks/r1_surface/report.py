"""Independent reconstruction of saved trees, interior bounds and parent bindings."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from scipy.linalg import eigh
ROOT=Path(__file__).resolve().parent;P=json.loads((ROOT/'PLAN.json').read_text());T=P['thresholds']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def value(c,u,t):return np.einsum('i,j,ijk->k',np.array([1-t,t]),np.array([1-u,u]),c)
def main():
    controls=json.loads((ROOT/'CONTROLS.json').read_text());assert controls['all_controls_pass'] and controls['plan_sha256']==sha(ROOT/'PLAN.json')
    assert all(sha(ROOT/n)==h for n,h in controls['source_hashes'].items())
    previous=json.loads((ROOT.parent/'r1_temporal'/'SUMMARY.json').read_text());assert previous['all_numerical_checks_pass']
    assert all(sha(ROOT.parent/'r1_temporal'/n)==h for n,h in previous['source_hashes'].items())
    sys.path.insert(0,str(ROOT.parent/'r1_holonomy'));from measure import Family
    errors={'center':0.,'delta':0.,'gap_lower':0.,'operator_norm':0.,'native_spectrum_meV':0.,'summary':0.,'cross_engine_affine_spectrum_meV':0.}
    cases=[];audits=[];files=[ROOT/n for n in ['PLAN.json','surface.py','sweep.py','controls.py','CONTROLS.json','report.py','BM.json','REF.json']]
    families={};raw={};sample_coords=[]
    for engine in P['engines']:
        d=json.loads((ROOT/(engine.upper()+'.json')).read_text());raw[engine]=d
        assert d['status']!='RUNNING' and not d['errors'];assert d['plan_sha256']==sha(ROOT/'PLAN.json')
        assert all(sha(ROOT.parent/n)==h for n,h in d['source_hashes'].items())
        fam=Family(engine);families[engine]=fam
        norms=np.array([np.abs(eigh(a,eigvals_only=True)).max() for a in fam.A]);errors['operator_norm']=max(errors['operator_norm'],float(np.max(np.abs(norms-d['operator_norms_meV']))))
        parent=json.loads((ROOT.parent/'r1_temporal'/(engine.upper()+'.json')).read_text());bounds=np.array(parent['bounds'])
        tracks=json.loads((ROOT.parent/'r1_holonomy'/(engine.upper()+'.json')).read_text())
        for case in d['cases']:
            path=ROOT/case['arrays_file'];files.append(path);assert sha(path)==case['arrays_sha256'];arr=np.load(path)
            allrows=arr['rows'];patches=arr['corners'];offsets=arr['offsets'];assert offsets[0]==0 and offsets[-1]==len(allrows) and len(offsets)==len(patches)+1
            assert np.array_equal(arr['operator_norms'],norms)
            cfg=next(c for c in P['mesh_levels'] if c['name']==case['mesh']);assert len(patches)==cfg['track_intervals']*(cfg['polygon_edges']+2)==len(case['faces'])
            stations=tracks['tracks'][str(cfg['track_intervals'])]['stations'];verts=[]
            # Reconstruct parent geometry independently, including exact closure.
            for s in stations:
                p,q,u=[np.array(r['f']) for r in s['roots']];e=(q-p)/np.linalg.norm(q-p);normal=np.array([-e[1],e[0]])
                theta=np.arctan2(-e[1],-e[0])+np.linspace(0,2*np.pi,cfg['polygon_edges']+1)
                ring=q+case['radius']*np.c_[np.cos(theta),np.sin(theta)];ring[-1]=ring[0]
                verts.append(np.c_[np.array([p+.55*(q-p),u-.006*normal,*ring]),np.full(cfg['polygon_edges']+3,s['D_meV'])])
            leaf_total=0;bad_total=0;actual_min=float('inf');center_min=float('inf');maxdepth=0
            for fi,c in enumerate(patches):
                meta=case['faces'][fi];j,k=divmod(fi,cfg['polygon_edges']+2);assert (j,k)==(meta['interval'],meta['edge'])
                expected=np.array([verts[j][k:k+2],verts[j+1][k:k+2]]);assert np.max(np.abs(c-expected))<1e-14
                assert np.all(c>=bounds[0]-1e-14) and np.all(c<=bounds[1]+1e-14)
                rows=allrows[offsets[fi]:offsets[fi+1]];assert rows.shape[1]==22
                assert np.array_equal(rows[0,:6],[0,1,0,1,0,-1])
                reached=set();stack=[0]
                while stack:
                    ni=stack.pop();assert ni not in reached and 0<=ni<len(rows);reached.add(ni);r=rows[ni]
                    a,b,t0,t1,depth,parent_i,left,right,state=r[:9]
                    assert 0<=a<b<=1 and 0<=t0<t1<=1
                    v=value(c,(a+b)/2,(t0+t1)/2)
                    cc=np.array([value(c,u,t) for t in [t0,t1] for u in [a,b]])
                    delta=float(np.max(np.sum(np.abs(cc-v)*norms,axis=1)));lower=np.diff(r[12:17])-2*delta-T['floating_allowance_meV']
                    errors['center']=max(errors['center'],float(np.max(np.abs(v-r[9:12]))));errors['delta']=max(errors['delta'],abs(delta-r[17]));errors['gap_lower']=max(errors['gap_lower'],float(np.max(np.abs(lower-r[18:22]))))
                    if state==0:
                        li,ri=int(left),int(right);assert left==li and right==ri and ni<li<ri<len(rows)
                        l,h=rows[li],rows[ri];assert l[5]==h[5]==ni and l[4]==h[4]==depth+1
                        split_u=np.array_equal(l[:4],[a,(a+b)/2,t0,t1]) and np.array_equal(h[:4],[(a+b)/2,b,t0,t1])
                        split_t=np.array_equal(l[:4],[a,b,t0,(t0+t1)/2]) and np.array_equal(h[:4],[a,b,(t0+t1)/2,t1])
                        assert split_u or split_t;stack.extend([li,ri])
                    else:
                        assert left==right==-1 and state in [1,-2,-3,-4]
                        assert (state==1)==bool(lower.min()>T['gap_margin_meV'])
                assert len(reached)==len(rows)
                leaf=rows[rows[:,8]!=0];bad=int(np.sum(leaf[:,8]!=1));area=float(np.sum((leaf[:,1]-leaf[:,0])*(leaf[:,3]-leaf[:,2])))
                assert area==1. and meta['evaluations']==len(rows) and meta['leaves']==len(leaf) and meta['unresolved_leaves']==bad and meta['pass']==(bad==0)
                low=float(leaf[:,18:22].min());cg=float(np.diff(rows[:,12:17],axis=1).min());md=int(rows[:,4].max())
                for got,want in [(meta['minimum_lower_meV'],low),(meta['minimum_center_gap_meV'],cg),(meta['leaf_parameter_area'],area),(meta['maximum_depth'],md)]:errors['summary']=max(errors['summary'],abs(got-want))
                leaf_total+=len(leaf);bad_total+=bad;actual_min=min(actual_min,low);center_min=min(center_min,cg);maxdepth=max(maxdepth,md)
            assert leaf_total==case['leaves'] and bad_total==case['unresolved_leaves'] and len(allrows)==case['evaluations'] and abs(actual_min-case['minimum_lower_meV'])<1e-12
            # Native matrix spectra at most restrictive and central diagnostic locations.
            leaves=allrows[allrows[:,8]!=0]
            selected=[leaves[int(np.argmin(leaves[:,18:22].min(axis=1)))],allrows[int(np.argmin(np.diff(allrows[:,12:17],axis=1).min(axis=1)))],allrows[len(allrows)//2]]
            from track import model
            for r in selected:
                v=r[9:12];native=model(engine,P['N'],float(v[2]));wn=eigh(native.H(fam.k(v[:2])),eigvals_only=True,subset_by_index=(fam.lo-1,fam.lo+3))
                errors['native_spectrum_meV']=max(errors['native_spectrum_meV'],float(np.max(np.abs(wn-r[12:17]))))
                if engine=='bm':sample_coords.append(v.copy())
            cases.append({'engine':engine,'mesh':case['mesh'],'radius':case['radius'],'faces':len(patches),'evaluations':len(allrows),'leaves':leaf_total,'unresolved_leaves':bad_total,'minimum_lower_meV':actual_min,'minimum_center_gap_meV':center_min,'maximum_depth':maxdepth,'pass':bad_total==0})
        for cfg in P['mesh_levels']:
            ss=tracks['tracks'][str(cfg['track_intervals'])]['stations']
            for k,name in enumerate(['p','q','upper']):
                rr=[s['roots'][k] for s in ss];assert all(r['accepted'] for r in rr)
                audits.append({'engine':engine,'mesh':cfg['name'],'node':name,'sample_count':len(rr),'maximum_residual_gap_meV':max(r['gap_meV'] for r in rr),'minimum_sampled_jacobian_singular_value':min(min(r['jacobian_singular_values']) for r in rr),'minimum_anchor_overlap':min(r['min_anchor_overlap'] for r in rr),'maximum_sample_step_distance':max(r['step_distance'] for r in rr),
                               'continuous_identity_certified':False,'reason':'Sampled Jacobians are not uniform derivative or uniqueness enclosures between stations.'})
    for v in sample_coords:
        w=[eigh(families[e].H(v),eigvals_only=True,subset_by_index=(families[e].lo-1,families[e].lo+3)) for e in P['engines']]
        errors['cross_engine_affine_spectrum_meV']=max(errors['cross_engine_affine_spectrum_meV'],float(np.max(np.abs(w[0]-w[1]))))
    assert max(errors.values())<T['reconciliation_error'],errors
    comparisons=[]
    for cfg in P['mesh_levels']:
        for r in P['radii']:
            aa,bb=[c for c in cases if c['mesh']==cfg['name'] and c['radius']==r]
            comparisons.append({'mesh':cfg['name'],'radius':r,'same_leaf_count':aa['leaves']==bb['leaves'],'minimum_lower_difference_meV':abs(aa['minimum_lower_meV']-bb['minimum_lower_meV']),'both_pass':aa['pass'] and bb['pass']})
    ok=len(cases)==8 and all(c['pass'] for c in cases)
    summary={'status':'RECONCILED_FULL_DECLARED_SURFACES_CONDITIONAL' if ok else 'UNRESOLVED_FACES_RETAINED','all_surface_checks_pass':ok,'new_analytic_controls':len(controls['controls']),'cases':cases,'engine_comparisons':comparisons,
      'totals':{k:sum(c[k] for c in cases) for k in ['faces','evaluations','leaves','unresolved_leaves']},'minimum_lower_meV':min(c['minimum_lower_meV'] for c in cases),'minimum_center_gap_meV':min(c['minimum_center_gap_meV'] for c in cases),
      'reconstruction_errors':errors,'root_identity_audit':audits,'prior_charge_result_reused':'+k on transported contours; no new charge measurement','scope':P['scope'],
      'source_hashes':{str(f.relative_to(ROOT)):sha(f) for f in files}}
    (ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k not in ['source_hashes','root_identity_audit','cases']},indent=2))
    return 0 if ok else 1
if __name__=='__main__':raise SystemExit(main())
