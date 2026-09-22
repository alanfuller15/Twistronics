"""Reconcile saved contour evidence and render figures without model reruns."""
from pathlib import Path
import json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
P=read(ROOT/'PLAN.json');raw={e:read(ROOT/(e.upper()+'.json')) for e in P['engines']}
controls=read(ROOT/'CONTROLS.json')
summary={'scope':'Closed-contour orientation holonomy and sampled continuation, not full braid acceptance',
         'engines':{},'loop_comparisons':[],'controls_passed':sum(x['control_pass'] for x in controls['cases']),
         'controls_total':len(controls['cases']),'reconciliation':{},'input_sha256':{}}
for e,d in raw.items():
    assert d['status']!='RUNNING'
    assert d['plan_sha256']==sha(ROOT/'PLAN.json')
    for name,digest in d['source_hashes'].items():assert sha(ROOT.parent/name)==digest,name
    fp=ROOT/(e.upper()+'.npz');assert d['frames_sha256']==sha(fp)
    arrays=np.load(fp,allow_pickle=False)
    maximum_orthogonality=max(float(np.max(np.abs(a.T@a-np.eye(2)))) for a in arrays.values())
    max_frame_record_error=0.
    for j,c in enumerate(d['continuation_comparisons']):
        calculated=[float(np.linalg.det(arrays[f'track_8_station_{j}_flat_{n}'].T@arrays[f'track_16_station_{2*j}_flat_{n}'])) for n in [0,1]]
        max_frame_record_error=max(max_frame_record_error,float(np.max(np.abs(np.array(calculated)-c['temporal_frame_determinants']))))
    max_product_error=0.;max_bound_error=0.;leaf_count=0
    for r in d['loops']:
        cfg=next(c for c in P['mesh_levels'] if c['name']==r['mesh'])
        W=np.eye(2)
        assert len(r['links'])==r['sample_points']-1
        leaf_smins=[]
        for edge in r['edges']:
            samples={x['t']:x['exterior_gap_meV'] for x in edge['samples']}
            for leaf in edge['leaves']:
                variation=edge['Hamiltonian_variation_norm_meV']*(leaf['b']-leaf['a'])
                lower=min(samples[leaf['a']],samples[leaf['b']])-variation-P['thresholds']['floating_allowance_meV']
                max_bound_error=max(max_bound_error,abs(lower-leaf['lower_estimate_meV']))
                assert leaf['resolved'] and lower>P['thresholds']['exterior_gap_margin_meV']
                assert variation/lower<=cfg['variation_over_lower_gap_max']*(1+1e-12)
                assert leaf['step_smin']>=cfg['target_step_smin']
                leaf_smins.append(leaf['step_smin']);leaf_count+=1
        assert len(leaf_smins)==len(r['links'])
        for smin,link in zip(leaf_smins,r['links']):
            Q=np.array(link['Q']);assert np.max(np.abs(Q.T@Q-np.eye(2)))<1e-8
            assert abs(smin-min(link['singular_values']))<1e-10
            W=W@Q
        max_product_error=max(max_product_error,float(np.max(np.abs(W-r['holonomy_matrix']))))
        assert abs(np.linalg.det(W)-r['determinant'])<1e-8
        assert r['accepted_sign']==int(np.sign(np.linalg.det(W)))
    assert maximum_orthogonality<1e-8 and max_frame_record_error<1e-10 and max_product_error<1e-8 and max_bound_error<1e-10
    summary['reconciliation'][e]={'stored_frame_arrays':len(arrays.files),'maximum_frame_orthogonality_error':maximum_orthogonality,
        'maximum_frame_comparison_record_error':max_frame_record_error,'maximum_link_product_record_error':max_product_error,
        'maximum_bound_record_error_meV':max_bound_error,'resolved_leaf_intervals':leaf_count,'pass':True}
    roots=[r for t in d['tracks'].values() for s in t['stations'] for r in s['roots']]
    summary['engines'][e]={'status':d['status'],'dimension':d['dimension'],'errors':d['errors'],
        'continuation_station_evaluations':sum(len(t['stations']) for t in d['tracks'].values()),
        'unique_D_stations':len(d['tracks']['16']['stations']),'root_refinements':len(roots),
        'maximum_root_gap_meV':max(r['gap_meV'] for r in roots),'maximum_root_step':max(r['step_distance'] for r in roots),
        'maximum_coarse_fine_root_difference':max(x for c in d['continuation_comparisons'] for x in c['root_coordinate_differences']),
        'minimum_coarse_fine_frame_determinant':min(x for c in d['continuation_comparisons'] for x in c['temporal_frame_determinants']),
        'minimum_temporal_step_smin':min(t['minimum_temporal_step_smin'] for t in d['tracks'].values()),
        'minimum_contour_step_smin':min(r['minimum_step_smin'] for r in d['loops']),
        'minimum_contour_isolation_lower_meV':min(r['minimum_isolation_lower_meV'] for r in d['loops']),
        'maximum_holonomy_cross_check_error':max(x for r in d['loops'] for x in r['cross_checks'].values()),
        'maximum_native_affine_matrix_error_meV':max(c['matrix_error_meV'] for c in d['affine_checks']),
        'maximum_native_affine_spectrum_error_meV':max(c['spectrum_error_meV'] for c in d['affine_checks']),
        'contours_passed':sum(r['diagnostics_pass'] for r in d['loops']),'contours_total':len(d['loops']),
        'all_hypotheses_match':d['all_hypotheses_match']}
    arrays.close()
for name in P['hypotheses']:
    rows={e:[r for r in d['loops'] if r['name']==name] for e,d in raw.items()}
    signs={e:[r['accepted_sign'] for r in rr] for e,rr in rows.items()}
    summary['loop_comparisons'].append({'name':name,'signs':signs,'hypothesis_sign':P['hypotheses'][name],
        'meshes_and_engines_agree':len({x for a in signs.values() for x in a})==1,
        'all_diagnostics_pass':all(r['diagnostics_pass'] for rr in rows.values() for r in rr),
        'minimum_isolation_lower_meV':min(r['minimum_isolation_lower_meV'] for rr in rows.values() for r in rr)})
summary['maximum_engine_root_difference']=max(float(np.linalg.norm(np.array(a['f'])-b['f']))
    for interval in ['8','16'] for x,y in zip(raw['bm']['tracks'][interval]['stations'],raw['ref']['tracks'][interval]['stations']) for a,b in zip(x['roots'],y['roots']))
summary['all_diagnostics_pass']=(controls['all_controls_pass'] and all(d['status']=='CLOSED_CONTOUR_DIAGNOSTICS_PASS_NOT_FULL_BRAID' for d in raw.values())
    and all(r['meshes_and_engines_agree'] and r['all_diagnostics_pass'] for r in summary['loop_comparisons'])
    and summary['maximum_engine_root_difference']<P['shared_root_match_tolerance'])
for p in [ROOT/'PLAN.json',ROOT/'BM.json',ROOT/'REF.json',ROOT/'BM.npz',ROOT/'REF.npz',ROOT/'CONTROLS.json']:
    summary['input_sha256'][p.name]=sha(p)
(ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))

navy,teal,blue,orange,muted='#172c43','#087f7d','#426fb4','#b66b1d','#61748b'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':navy,'axes.labelcolor':navy,
                     'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
fig=plt.figure(figsize=(14.5,10.5),facecolor='#f6f8fb')
gs=fig.add_gridspec(2,2,left=.035,right=.96,top=.84,bottom=.16,wspace=.22,hspace=.5,width_ratios=[1.18,1])
fig.text(.055,.951,'Closed-loop frame test at N8',fontsize=25,weight='bold')
fig.text(.055,.912,'Two implementations  •  coarse/fine continuation  •  guarded adaptive contour sampling',fontsize=12)
track=raw['bm']['tracks']['16']['stations']
Ds=np.array([s['D_meV'] for s in track])
ps=np.array([s['roots'][0]['f'] for s in track]);qs=np.array([s['roots'][1]['f'] for s in track])
def coordinates(v):
    f=np.array(v[:2]);D=v[2]
    p=np.array([np.interp(D,Ds,ps[:,i]) for i in [0,1]])
    q=np.array([np.interp(D,Ds,qs[:,i]) for i in [0,1]])
    d=q-p;n=np.array([-d[1],d[0]])/np.linalg.norm(d)
    return [float((f-p)@d/(d@d)),float((f-p)@n*1000),D]
ax=fig.add_subplot(gs[:,0],projection='3d');ax.set_facecolor('#f6f8fb')
for name,color,label in [('center_ribbon',teal,'Center contour'),('shifted_ribbon',blue,'Shifted contour')]:
    row=next(r for r in raw['bm']['loops'] if r['name']==name and r['mesh']=='fine')
    xyz=np.array([coordinates(v) for v in row['vertices']])
    ax.plot(*xyz.T,color=color,lw=2.3,label=label)
    shift=0. if name=='center_ribbon' else P['path_radius']
    panels=[]
    for j in range(len(track)-1):
        corners=[[* (ps[j]+[shift,0]),Ds[j]],[*(qs[j]+[shift,0]),Ds[j]],
                 [*(qs[j+1]+[shift,0]),Ds[j+1]],[*(ps[j+1]+[shift,0]),Ds[j+1]]]
        panels.append([coordinates(v) for v in corners])
    ax.add_collection3d(Poly3DCollection(panels,facecolors=color,alpha=.075,edgecolors='none'))
    ax.text(.5,0 if name=='center_ribbon' else 1.7,39.04,'det W = '+('−1' if row['accepted_sign']==-1 else '+1'),color=color,fontsize=11,ha='center',weight='bold')
upper=np.array([coordinates([*s['roots'][2]['f'],s['D_meV']]) for s in track])
ax.plot(*upper.T,color=orange,lw=2,marker='o',ms=3,label='Tracked adjacent node')
ax.scatter(*upper[[0,-1]].T,color=orange,s=35,marker='D')
ax.set(xlim=(-.05,1.07),ylim=(-4.5,2.),zlim=(37.97,39.13),xticks=[0,.5,1],yticks=[-4,-2,0,2],zticks=[38.,38.5,39.])
ax.set_xlabel('Along-segment position, t',labelpad=8)
ax.set_ylabel('Normal offset × 1,000',labelpad=10)
ax.set_zlabel('D (meV)',labelpad=8)
ax.set_box_aspect([1.15,1.,1.35]);ax.view_init(elev=22,azim=-54)
ax.set_title('A   Closed contours spanning D=38 to 39',loc='left',fontsize=13,weight='bold',pad=10)
ax.legend(loc='upper left',bbox_to_anchor=(.015,.96),frameon=False,fontsize=9)

ax=fig.add_subplot(gs[0,1]);ax.axis('off')
ax.set_title('B   Orientation after one closed circuit',loc='left',fontsize=13,weight='bold',pad=15)
labels={'static_D38':'Path-comparison loop\nD=38','static_D39':'Path-comparison loop\nD=39','center_ribbon':'Center contour\nD=38 → 39','shifted_ribbon':'Shifted contour\nD=38 → 39'}
cells=[]
for r in summary['loop_comparisons']:
    vals=[' / '.join('−1' if x==-1 else '+1' if x==1 else '?' for x in r['signs'][e]) for e in P['engines']]
    cells.append([labels[r['name']],*vals])
tab=ax.table(cellText=cells,colLabels=['Closed loop','BM\ncoarse / fine','Reference\ncoarse / fine'],cellLoc='center',bbox=[0,.03,1,.96],colWidths=[.46,.27,.27])
tab.auto_set_font_size(False);tab.set_fontsize(10)
for (r,c),cell in tab.get_celld().items():
    cell.set_facecolor('#e7edf5' if r==0 else 'white');cell.set_edgecolor('#dfe5ed')
    if r==0:cell.set_text_props(weight='bold')
    elif c:cell.set_text_props(weight='bold',color=teal if '−1' in cell.get_text().get_text() else blue)

ax=fig.add_subplot(gs[1,1])
row=next(r for r in raw['bm']['loops'] if r['name']=='center_ribbon' and r['mesh']=='fine')
edge=row['edges'][0]
x=np.array([v['t'] for v in edge['samples']]);g=np.array([v['exterior_gap_meV'] for v in edge['samples']])
ax.semilogy(x,g,color=teal,lw=1.8,label='Sampled exterior gap')
ends=[v['a'] for v in edge['leaves']]+[edge['leaves'][-1]['b']]
ax.stairs([v['lower_estimate_meV'] for v in edge['leaves']],ends,color=orange,lw=1.4,label='Conditional lower estimate')
ax.axhline(.001,color='#b83f49',ls=':',lw=1.3,label='Required margin')
ax.set(xlim=(.695,.755),ylim=(.0007,3),xlabel='Position along D=38 center segment, t',ylabel='Exterior gap (meV)')
ax.grid(alpha=.15,which='major');ax.legend(loc='lower left',frameon=True,facecolor='white',edgecolor='none',framealpha=.95,fontsize=8)
ax.set_title('C   Isolation along the contour: local view',loc='left',fontsize=13,weight='bold',pad=15)
fig.text(.055,.092,'−1: orientation reverses.  +1: orientation is preserved.  All 16 contour diagnostics and eight analytic controls pass.',fontsize=11,weight='bold')
fig.text(.055,.064,'Rescaled fractional momentum follows the moving flat-node segment; lines join samples. Shading does not certify interior isolation.',fontsize=10,color=muted)
fig.text(.055,.039,'Finite-model, binary orientation evidence. No full non-Abelian braid, Euler-class removal, or experimental calibration is established.',fontsize=10,color=muted)
fig.savefig(ROOT/'holonomy.png',dpi=180,facecolor=fig.get_facecolor())
fig.savefig(ROOT/'holonomy.svg',facecolor=fig.get_facecolor())
