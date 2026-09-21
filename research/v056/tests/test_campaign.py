import copy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
import campaign_map as cm
from evidence import read,sha,safe,pair_distance


def record(family):
    i=read(cm.ROOT/'SOURCE_INDEX.json')
    f,v,a,p,role,scope,n=next(x for x in cm.FAMILIES if x[0]==family)
    folder=cm.REPO/i['batches'][v]
    return read(folder/p.format(engine='bm_lab',N=4)),a,n,sha(folder/'PLAN.json')


def test_complete_map_reproduces_saved_observations():
    actual=cm.build();assert actual==read(cm.ROOT/'results/campaign_map.json')
    assert len(actual['claim_rows'])==80 and len(actual['root_links'])==44
    assert actual['counts_by_role']['superseded_replay']['frame_stations']==76
    assert actual['counts_by_role']['primary']['frame_stations']==496


@pytest.mark.parametrize('fault',['status','protocol','engine','count','step','label','trials','orientation'])
def test_incomplete_frame_records_rejected(fault):
    r,a,n,p=record('preparation')
    if fault=='status':r['status']='RUNNING'
    elif fault=='protocol':r['protocol_sha256']='bad'
    elif fault=='engine':r['engine']='unknown'
    elif fault=='count':r['states'].pop()
    elif fault=='step':r['states'][1]['step']=0
    elif fault=='label':r['states'][1]['label']=None
    elif fault=='trials':r['states'][1]['temporal_trials'].pop()
    else:r['states'][1]['spatial_mesh_determinant']=-1
    with pytest.raises(ValueError):cm.validate_record(r,a,n,p)


@pytest.mark.parametrize('fault',['root','charge','nondegenerate','derivative','open_gap','open_mesh','scope'])
def test_invalid_fold_evidence_rejected(fault):
    r,a,n,p=record('lower_unlink')
    if fault=='root':r['states'][0]['nodes'][0]['gap']=1
    elif fault=='charge':r['charges'][0]['measurement']['label']='SAME'
    elif fault=='nondegenerate':r['nondegeneracy']['status']='FAIL'
    elif fault=='derivative':r['event']['fold_trials'][1]['parameter']+=.1
    elif fault=='open_gap':r['open_checks'][0]['trials'][0]['minimum']['gap']=0
    elif fault=='open_mesh':r['open_checks'][0]['trials'].pop()
    else:r['scope']='LOCAL_DOMAIN_EVENT'
    with pytest.raises(ValueError):cm.validate_record(r,a,n,p)


@pytest.mark.parametrize('fault',['box','boundary','global_claim'])
def test_local_domain_never_promoted_to_global(fault):
    r,a,n,p=record('extra_flat_birth')
    if fault=='box':r['definition']['box']=[[0,1],[0,1]]
    elif fault=='boundary':r['states'][0]['boundary']['trials'][0]['minimum']=0
    else:r['scope']='FULL_CHART_LOWER_GAP_SEARCH'
    with pytest.raises(ValueError):cm.validate_record(r,a,n,p,gap_grids=((17,25),(17,25)))


def test_old_single_grid_station_is_not_misrepresented_as_refined():
    r,a,n,p=record('first_ann')
    with pytest.raises(ValueError,match='grid'):cm.validate_record(r,a,n,p,False)
    assert cm.validate_record(r,a,n,p,False,((18,),(18,24)))['open_stations']==2


@pytest.mark.parametrize('fault',['sign','seam','axis','label'])
def test_cycle_diagnostics_cannot_support_false_w1(fault):
    r,*_=record('endpoint_checkpoint')
    if fault=='sign':r['cycles']['flat1'][0]['trials'][0]['sign']*= -1
    elif fault=='seam':r['cycles']['flat1'][0]['trials'][0]['seam_overlap']=0
    elif fault=='axis':r['cycles']['flat1'].pop()
    else:r['w1']={'wrong':[0,0]}
    with pytest.raises(ValueError):cm.cycles(r)


def test_join_requires_state_identity_and_two_roots():
    with pytest.raises(ValueError):cm.state_equal({'A':0},{'A':1})
    with pytest.raises(ValueError):pair_distance([],[])
    a=[{'f':[0,0]},{'f':[1,1]}];assert pair_distance(a,list(reversed(a)))==0
    assert pair_distance(a,[{'f':[0,0]},{'f':[1,1.1]}])>.09


@pytest.mark.parametrize('body',['{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}'])
def test_nonfinite_or_ambiguous_json_rejected(tmp_path,body):
    p=tmp_path/'bad.json';p.write_text(body)
    with pytest.raises(ValueError):read(p)


@pytest.mark.parametrize('name',['../escape','/absolute','a\\b'])
def test_unsafe_evidence_path_rejected(tmp_path,name):
    with pytest.raises(ValueError):safe(tmp_path,name)


def test_unknown_batch_rejected():
    i=read(cm.ROOT/'SOURCE_INDEX.json');i['batches']['v999']='missing'
    with pytest.raises(ValueError):cm.build(index=i)
