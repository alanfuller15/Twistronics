"""Independent reconstruction of the crossing inequalities and whole-D cover."""
import json
import numpy as np
from scipy.linalg import eigh, qr
from crossing import ROOT, PLAN, T, CFG, sha, load, Family, model

def main():
    data=json.loads((ROOT/'RESULTS.json').read_text());cont,cases,sources=load()
    assert data['plan_sha256']==sha(ROOT/'PLAN.json')
    assert all(sha(ROOT.parent/n)==h for n,h in data['source_hashes'].items())
    assert all(data['source_hashes'][n]==h for n,h in sources.items())
    assert data['frames_sha256']==sha(ROOT/'FRAMES.npz')
    frames=np.load(ROOT/'FRAMES.npz');assert set(frames.files)==set(data['centers'])
    controls=json.loads((ROOT/'CONTROLS.json').read_text())
    assert controls['all_controls_pass'] and controls['plan_sha256']==data['plan_sha256']
    assert all(sha(ROOT/n)==h for n,h in controls['source_hashes'].items())
    errors={};native_max=0.;spectrum_max=0.
    def close(name,a,b):
        a,b=np.asarray(a),np.asarray(b);assert a.shape==b.shape
        err=float(np.max(abs(a-b)));errors[name]=max(errors.get(name,0.),err)
        assert np.isfinite(err) and err<=T['reconstruction_tolerance'],(name,err)
    def comp(M):return np.array([(M[0,0]+M[1,1])/2,(M[0,0]-M[1,1])/2,M[0,1]])
    def norm(M):return float(np.linalg.norm(M,2))
    def cross(a,b):return float(a[0]*b[1]-a[1]*b[0])
    for engine in PLAN['engines']:
        family=Family(engine)
        for key,c in data['centers'].items():
            if c['engine']!=engine:continue
            assert c['pass'] and c['root']['accepted']
            r=c['raw'];D=r['D_meV'];y=np.array(r['y']);v=np.array(r['velocity']);F=frames[key];Q=qr(F,mode='full')[0][:,2:]
            H=family.H([*y[:2],D]);K=Q.T@H@Q-y[2]*np.eye(family.dim-2);kw=eigh(K,eigvals_only=True)
            J=np.array([comp(F.T@A@F) for A in family.A[:2]]+[np.array([-1.,0.,0.])]).T
            gD=comp(F.T@family.A[2]@F);C=np.linalg.inv(J)
            V=family.A[2]+v[0]*family.A[0]+v[1]*family.A[1]
            values={'J':J,'C':C,'gD':gD,'velocity':-C@gD,'g0':comp(F.T@H@F-y[2]*np.eye(2)),
                    'G0':min(abs(kw))-CFG['energy_allowance_meV'],'complement_eigenvalues_meV':kw,
                    'cross_center':norm(Q.T@H@F)+CFG['norm_allowance'],
                    'cross_axes':[norm(Q.T@A@F)+CFG['norm_allowance'] for A in family.A[:2]],
                    'axis_norms':[max(abs(eigh(A,eigvals_only=True)))+CFG['norm_allowance'] for A in family.A[:2]],
                    'cross_velocity':norm(Q.T@V@F)+CFG['norm_allowance'],
                    'complement_velocity':max(abs(eigh(V-v[2]*np.eye(family.dim),eigvals_only=True)))+CFG['norm_allowance'],
                    'w4':eigh(H,eigvals_only=True,subset_by_index=(297,300))}
            for n,x in values.items():close('primitive_'+n,x,r[n])
            assert sum(kw<0)==298 and sum(kw>0)==family.dim-300
            native=model(engine,8,D).H(family.k(y[:2]));nw=eigh(native,eigvals_only=True,subset_by_index=(297,300))
            ne=float(np.max(abs(family.U.conj().T@native@family.U-H)));se=float(max(abs(nw-values['w4'])))
            assert ne<=CFG['matrix_tolerance_meV'] and se<=CFG['native_spectrum_tolerance_meV'] and nw[2]-nw[1]<=CFG['native_spectrum_tolerance_meV']
            close('native_w4',nw,c['native']['w4']);native_max=max(native_max,ne);spectrum_max=max(spectrum_max,se)

    def audit_certificate(raw,s):
        C=np.array(raw['C']);c=np.sum(abs(C),axis=1);h=s['halfwidth']
        gl=raw['G0']-h*raw['complement_velocity'];bl=raw['cross_center']+h*raw['cross_velocity']
        Y=abs(C@raw['g0'])+h*abs(C@(np.array(raw['gD'])+np.array(raw['J'])@raw['velocity']))+c*(bl**2/gl+CFG['energy_allowance_meV'])
        radius=max(CFG['minimum_rho_meV'],CFG['radius_factor']*max(Y/c))*c
        G=gl-np.array(raw['axis_norms'])@radius[:2]-radius[2];B=bl+np.array(raw['cross_axes'])@radius[:2]
        nonlin=np.r_[2*np.array(raw['cross_axes'])*B/G+B**2*np.array(raw['axis_norms'])/G**2,B**2/G**2]
        matrix=(abs(np.eye(3)-C@raw['J'])+CFG['dimensionless_allowance']+c[:,None]*nonlin[None,:])*radius[None,:]/radius[:,None]
        q=max(matrix.sum(axis=1));yn=max(Y/radius);beta=yn/(1-q)
        for n,x in [('radii',radius),('Gfull',G),('bfull',B),('q',q),('Ynorm',yn),('inner_radii',beta*radius)]:close('certificate_'+n,x,s[n])
        assert bool(G>CFG['complement_margin_meV'] and q<=CFG['contraction_max'] and yn+q<=CFG['self_map_max'])==s['pass']

    def audit_identity(r,s,p,lo,hi,stored):
        margins=[]
        old=cont['centers'][p['center']]['raw'];pc=p['certificate']
        for D in [lo,hi]:
            newc=np.array(r['y'])+(D-r['D_meV'])*np.array(r['velocity'])
            oldc=np.array(old['y'])+(D-old['D_meV'])*np.array(old['velocity'])
            margins.append(np.minimum(newc-np.array(s['radii'])-(oldc-np.array(pc['radii'])),oldc+np.array(pc['radii'])-(newc+np.array(s['radii']))))
        close('identity_margins',margins,stored['margins']);assert stored['pass']==bool(np.min(margins)>T['identity_margin'])

    def audit_geometry(case,r,s,lo,hi,g):
        # Reconstruct the affine path from original station vertices; sample
        # only to recover its exactly quadratic coefficients, then bound analytically.
        mid=(lo+hi)/2;stations=case['geometry']
        j=next(j for j in range(len(stations)-1) if stations[j]['D_meV']<=mid<=stations[j+1]['D_meV'])
        l,z=stations[j:j+2];x0=np.array(l['vertices'])[[0,2]];x1=np.array(z['vertices'])[[0,2]]
        av=(x1[0]-x0[0])/(z['D_meV']-l['D_meV']);bv=(x1[1]-x0[1])/(z['D_meV']-l['D_meV'])
        pvals=[];ee=[];ww=[]
        for D in [lo,mid,hi]:
            frac=(D-l['D_meV'])/(z['D_meV']-l['D_meV']);a,b=(1-frac)*x0+frac*x1
            e=b-a;w=np.array(r['y'][:2])+(D-r['D_meV'])*np.array(r['velocity'][:2])-a
            ee.append(e);ww.append(w);pvals.append([cross(e,w),e@w,e@e])
        pvals=np.array(pvals);q2=2*(pvals[2]-2*pvals[1]+pvals[0]);q1=pvals[2]-pvals[0]-q2
        coeff=np.array([pvals[0],q1,q2]).T
        def extrema(q):
            points=[0.,1.]
            if q[2]!=0 and 0 < -q[1]/(2*q[2]) < 1:points.append(-q[1]/(2*q[2]))
            vals=[q[0]+q[1]*x+q[2]*x*x for x in points];return min(vals),max(vals)
        for n,q in zip(['side_coefficients','dot_coefficients','length_coefficients'],coeff):close('geometry_'+n,q,g[n])
        rpos=np.array(s['inner_radii'][:2]);corners=[np.array([x,y])*rpos for x in [-1,1] for y in [-1,1]]
        se=max(abs(cross(e,p)) for e in [ee[0],ee[2]] for p in corners)+T['geometry_allowance']
        de=max(abs(e@p) for e in [ee[0],ee[2]] for p in corners)+T['geometry_allowance']
        C=np.array(r['C']);rad=np.array(s['radii']);B=s['bfull'];G=s['Gfull']
        nt=2*r['cross_velocity']*B/G+B**2*r['complement_velocity']/G**2
        force=abs(C@(np.array(r['gD'])+np.array(r['J'])@r['velocity']))+abs(C).sum(axis=1)*nt
        vr=rad*max(force/rad)/(1-s['q'])+T['derivative_allowance']
        close('velocity_radius',vr,g['velocity']['velocity_radius'])
        slopevals=[cross(bv-av,w)+cross(e,np.array(r['velocity'][:2])-av) for e,w in zip([ee[0],ee[2]],[ww[0],ww[2]])]
        vpoints=[np.array([x,y])*vr[:2] for x in [-1,1] for y in [-1,1]]
        slopeerr=max(abs(cross(bv-av,p)) for p in corners)+max(abs(cross(e,v)) for e in [ee[0],ee[2]] for v in vpoints)+T['derivative_allowance']
        slope=[min(slopevals)-slopeerr,max(slopevals)+slopeerr]
        close('slope_bounds',slope,g['slope_bounds']);close('side_error',se,g['side_error'])
        # Check conservative Bernstein endpoints and also exact polynomial extrema.
        bc=np.c_[coeff[:,0],coeff[:,0]+coeff[:,1]/2,coeff.sum(axis=1)]
        side=[min(bc[0])-se,max(bc[0])+se];num=[min(bc[1])-de,max(bc[1])+de];den=[min(bc[2])-T['geometry_allowance'],max(bc[2])+T['geometry_allowance']]
        along=[min(n/d for n in num for d in den),max(n/d for n in num for d in den)]
        for name,calc in [('side_bounds',side),('along_bounds',along),('numerator_bounds',num),('denominator_bounds',den)]:close('geometry_'+name,calc,g[name])
        for q,bounds in zip(coeff,[side,num,den]):
            ex=extrema(q);assert ex[0]>=bounds[0]-1e-12 and ex[1]<=bounds[1]+1e-12
        assert den[0]>0
        return side,slope,along

    totals={'attempts':0,'accepted_leaves':0,'failed_parents':0,'unresolved_leaves':0,'point_checks':0,'new_centers':len(data['centers'])}
    rows=[];minimum_segment=1.;maximum_event_slope=-np.inf;minimum_outside_side=np.inf
    assert len(data['cases'])==len(cases)==8
    for result,case in zip(data['cases'],cases):
        assert (result['engine'],result['mesh'],result['radius'])==(case['engine'],case['mesh'],case['radius'])
        lookup={p['id']:p for p in case['paths']['upper']};attempts=result['attempts'];leafset=set(result['leaf_ids'])
        for i,a in enumerate(attempts):
            assert a['id']==i;parent=lookup[a['inherited_tube']];assert parent['a']<=a['a']<a['b']<=parent['b']
            raw=(cont['centers'] if a['origin']=='inherited' else data['centers'])[a['center']]['raw']
            if a['origin']=='inherited':assert a['certificate']==parent['certificate'] and a['center']==parent['center']
            else:audit_certificate(raw,a['certificate']);audit_identity(raw,a['certificate'],parent,a['a'],a['b'],a['identity'])
            side,slope,along=audit_geometry(case,raw,a['certificate'],a['a'],a['b'],a['geometry'])
            inside=a['a']>=PLAN['event_window_meV'][0] and a['b']<=PLAN['event_window_meV'][1]
            assert inside==(a['region']=='event_window')
            passed=slope[1]<-T['strict_slope_margin'] and along[0]>T['segment_interior_margin'] and along[1]<1-T['segment_interior_margin'] if inside else side[0]>T['strict_side_margin'] or side[1]<-T['strict_side_margin']
            assert passed==a['pass']
            if a['children']:
                assert not a['pass'] and i not in leafset
                l,r=[attempts[j] for j in a['children']]
                assert l['parent']==r['parent']==i and (l['a'],l['b'],r['a'],r['b'])==(a['a'],(a['a']+a['b'])/2,(a['a']+a['b'])/2,a['b'])
            else:assert i in leafset
        leaves=sorted([attempts[i] for i in leafset],key=lambda a:a['a'])
        assert leaves[0]['a']==38 and leaves[-1]['b']==39 and all(l['b']==r['a'] for l,r in zip(leaves[:-1],leaves[1:]))
        assert all(a['pass'] for a in leaves)
        for a in leaves:
            if a['region']=='event_window':
                minimum_segment=min(minimum_segment,a['geometry']['along_bounds'][0],1-a['geometry']['along_bounds'][1]);maximum_event_slope=max(maximum_event_slope,a['geometry']['slope_bounds'][1])
            else:minimum_outside_side=min(minimum_outside_side,max(a['geometry']['side_bounds'][0],-a['geometry']['side_bounds'][1]))
        for p in result['points']:
            raw=data['centers'][p['center']]['raw'];audit_certificate(raw,p['certificate'])
            audit_identity(raw,p['certificate'],lookup[p['inherited_tube']],p['D_meV'],p['D_meV'],p['identity'])
            audit_geometry(case,raw,p['certificate'],p['D_meV'],p['D_meV'],p['geometry']);assert p['pass']
        lp,rp=result['points'][:2];assert [lp['D_meV'],rp['D_meV']]==PLAN['event_window_meV']
        assert lp['geometry']['side_bounds'][0]>T['strict_side_margin'] and rp['geometry']['side_bounds'][1]<-T['strict_side_margin']
        es=[a['geometry']['slope_bounds'] for a in leaves if a['region']=='event_window'];slope=[min(x[0] for x in es),max(x[1] for x in es)]
        close('event_slope',slope,result['event_slope_bounds']);assert slope[1]<0
        interval=PLAN['event_window_meV'].copy()
        for step in result['event_steps']:
            close('event_before',interval,step['before']);p=result['points'][step['point_index']];m=sum(interval)/2;assert p['D_meV']==m
            candidates=[m-s/d for s in p['geometry']['side_bounds'] for d in slope]
            interval=[max(interval[0],min(candidates)-T['geometry_allowance']),min(interval[1],max(candidates)+T['geometry_allowance'])]
            close('event_after',interval,step['interval']);assert interval[0]<=interval[1] and step['pass']
        close('event_final',interval,result['event_interval_meV']);assert interval[1]-interval[0]<=PLAN['target_event_width_meV']
        assert result['one_transverse_crossing'] and result['pass'] and result['unresolved_leaves']==0
        totals['attempts']+=len(attempts);totals['accepted_leaves']+=len(leaves);totals['failed_parents']+=len(attempts)-len(leaves);totals['point_checks']+=len(result['points'])
        rows.append({k:result[k] for k in ['name','engine','mesh','radius','event_interval_meV','event_width_meV','event_slope_bounds','unresolved_leaves','pass']})
    supplement=json.loads((ROOT/'VELOCITY_CONTROLS.json').read_text())
    assert supplement['all_controls_pass']
    assert all(sha(ROOT/n)==h for n,h in supplement['source_hashes'].items())
    for c in supplement['controls']:
        r,s=c['raw'],c['certificate'];audit_certificate(r,s)
        C=np.array(r['C']);rad=np.array(s['radii']);B=s['bfull'];G=s['Gfull']
        nt=2*r['cross_velocity']*B/G+B**2*r['complement_velocity']/G**2
        force=abs(C@(np.array(r['gD'])+np.array(r['J'])@r['velocity']))+abs(C).sum(axis=1)*nt
        vr=rad*max(force/rad)/(1-s['q'])+T['derivative_allowance']
        close('supplement_velocity_radius',vr,c['bound']['velocity_radius'])
        vals=[]
        for D in [c['a'],c['b']]:
            d=D-38;dx=d/(2*np.sqrt(25+d*d/2));vals.append([dx,0.,-dx])
        lo=np.min(vals,axis=0);hi=np.max(vals,axis=0)
        close('supplement_analytic_extrema',[lo,hi],c['analytic_velocity_bounds'])
        assert np.all(lo>np.array(r['velocity'])-vr) and np.all(hi<np.array(r['velocity'])+vr) and c['pass']
    union=[min(r['event_interval_meV'][0] for r in rows),max(r['event_interval_meV'][1] for r in rows)]
    names=['PLAN.json','crossing.py','controls.py','CONTROLS.json','run.py','RESULTS.json','FRAMES.npz','METHOD.md','report.py','VELOCITY_CONTROL_PLAN.json','velocity_control.py','VELOCITY_CONTROLS.json']
    summary={'status':'RECONCILED_CONDITIONAL_UNIQUE_TRACKED_NODE_STEM_CROSSING_PASS','all_checks_pass':True,'controls':len(controls['controls'])+len(supplement['controls']),
             'initial_controls':len(controls['controls']),'post_production_velocity_controls':len(supplement['controls']),
             'totals':totals,'cases':rows,'union_of_case_enclosures_meV':union,
             'minimum_segment_endpoint_clearance_in_t':minimum_segment,'least_negative_event_slope_upper':maximum_event_slope,
             'minimum_outside_area_clearance':minimum_outside_side,'maximum_native_matrix_error_meV':native_max,'maximum_native_spectrum_error_meV':spectrum_max,
             'reconstruction_errors':errors,'source_hashes':{n:sha(ROOT/n) for n in names},'scope':PLAN['scope']}
    (ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(summary['status']);print(json.dumps(totals));print('UNION',union);print('MAX RECONSTRUCTION ERROR',max(errors.values()))

if __name__=='__main__':main()
