import sys,json,copy
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import reconcile as r
from evidence import read,write,sha
ROOT=Path(__file__).resolve().parents[1]


def fixture_case(engine='bm_lab'):
    return read(ROOT/'results'/f'second_{engine}_N8.json'),read(ROOT/'NUMERICAL_PLAN.json'),sha(ROOT/'NUMERICAL_PLAN.json')


@pytest.mark.parametrize('engine',['bm_lab','ref_lab'])
def test_completed_window_reconciles_with_saved_frames(engine):
    c,p,h=fixture_case(engine);result=r.validate_case(c,engine,p,h)
    assert result['measured_states']==11 and result['new_states']==10 and result['roots']==66 and result['coarse_checks']==5 and result['frame_checkpoints']==11
    assert result['labels']==['OPPOSITE']*11 and result['temporal_charges']==p['anchors'][engine]['temporal_charges']


@pytest.mark.parametrize('fault',['rejected','missing_state','wrong_state','wrong_plan','runtime','node_failure','node_gap','node_seed','root_jump','rectangle','mesh','charge','radius','retry','gap_minimum','coarse','anchor','missing_join','join_root','join_basis','join_gauge'])
def test_corrupted_evidence_cannot_be_promoted(fault):
    c,p,h=fixture_case();row=c['states'][0]
    if fault=='rejected':c['status']='REJECT'
    elif fault=='missing_state':c['states'].pop()
    elif fault=='wrong_state':c['state']['B']=0
    elif fault=='wrong_plan':c['numerical_plan_sha256']='wrong'
    elif fault=='runtime':c['runtime_after']={}
    elif fault=='node_failure':row['nodes']['U1']['success']=False
    elif fault=='node_gap':row['nodes']['U1']['gap']=.01
    elif fault=='node_seed':row['nodes']['U1']['seed'][1]-=1
    elif fault=='root_jump':row['max_jump']=.9
    elif fault=='rectangle':row['rectangle_orientation']*=-1
    elif fault=='mesh':row['spatial_mesh_determinant']=-1
    elif fault=='charge':row['charge']['trials'][0]['a']['charge']=0
    elif fault=='radius':row['charge']['trials'][0]['radius']*=2
    elif fault=='retry':row['charge']['rejected_stages']=[dict(reason='unresolved loop gap')]
    elif fault=='gap_minimum':row['spatial_transport'][0]['located_gap_minima'].pop()
    elif fault=='coarse':c['states'][2]['coarse_check']=None
    elif fault=='anchor':c['anchor']['temporal_charges']=[0,0]
    elif fault=='missing_join':row['join']=None
    elif fault=='join_root':row['join']['root_shifts']['U1']=.1
    elif fault=='join_basis':row['join']['subspace_overlaps']['frame_a']=.5
    elif fault=='join_gauge':row['join']['aligned_max_errors']['a']=.1
    with pytest.raises(ValueError):r.validate_case(c,'bm_lab',p,h)


def frame_fixture(tmp_path):
    arrays={k:np.eye(4)[:,:2] for k in ['frame_a','frame_b','spatial','spatial_fast','coarse_a','coarse_b']}
    np.savez_compressed(tmp_path/'frames.npz',**arrays)
    row=dict(frames_sha256=sha(tmp_path/'frames.npz'),rectangle_determinant=1.,spatial_mesh_determinant=1.,temporal_overlaps=[1.,1.],coarse_check=None)
    write(tmp_path/'record.json',row);return arrays,row


@pytest.mark.parametrize('fault',['hash','record','shape','nonfinite','orthogonality','rectangle','spatial_mesh','initial_frame'])
def test_saved_frame_failures_reject(tmp_path,fault):
    arrays,row=frame_fixture(tmp_path);previous={k:v.copy() for k,v in arrays.items()};r.frames(tmp_path,row,4,previous)
    if fault=='hash':row['frames_sha256']='wrong';write(tmp_path/'record.json',row)
    elif fault=='record':write(tmp_path/'record.json',dict(row,extra=True))
    else:
        if fault=='shape':arrays['frame_a']=np.eye(3)[:,:2]
        elif fault=='nonfinite':arrays['frame_a']=arrays['frame_a'].copy();arrays['frame_a'][0,0]=np.nan
        elif fault=='orthogonality':arrays['frame_a']=2*arrays['frame_a']
        elif fault=='rectangle':row['rectangle_determinant']=-1.
        elif fault=='spatial_mesh':row['spatial_mesh_determinant']=-1.
        elif fault=='initial_frame':arrays['coarse_a']=-arrays['coarse_a']
        np.savez_compressed(tmp_path/'frames.npz',**arrays);row['frames_sha256']=sha(tmp_path/'frames.npz');write(tmp_path/'record.json',row)
    with pytest.raises(ValueError):r.frames(tmp_path,row,4,previous)


def test_reconciliation_matches_hashed_historical_targets():
    result=r.build()
    assert len(result['cutoff_comparisons'])==4
    assert all(x['distinct_states']==15 for x in result['combined_braid2_chain'])
    assert all(len(c['common_states'])==10 and all(q['saved_label']==q['N8_label'] for q in c['common_states']) for c in result['cutoff_comparisons'])


def test_reflected_temporal_frame_is_not_a_valid_polar_transport(tmp_path):
    arrays,row=frame_fixture(tmp_path);prior={k:a.copy() for k,a in arrays.items()}
    arrays['frame_a']=arrays['frame_a'].copy();arrays['frame_a'][:,0]*=-1
    # Singular values still equal one; the orientation/alignment gate must reject.
    np.savez_compressed(tmp_path/'frames.npz',**arrays);row['frames_sha256']=sha(tmp_path/'frames.npz');write(tmp_path/'record.json',row)
    with pytest.raises(ValueError,match='polar alignment'):r.frames(tmp_path,row,4,prior)


def test_actual_runtime_alias_join_preserves_original_records():
    current=read(ROOT/'results/second_bm_lab_N8.json')['runtime_before'];p=read(ROOT/'NUMERICAL_PLAN.json')
    prior=read(r.REPO/p['anchors']['bm_lab']['aggregate'])['runtime_after']
    result=r.runtime_join(prior,current)
    assert result['other_runtime_fields_equal'] and prior['executable']!=current['executable']


@pytest.mark.parametrize('fault',['package','native_binary','thread_environment','executable'])
def test_runtime_alias_does_not_hide_real_environment_change(tmp_path,fault):
    current=read(ROOT/'results/second_bm_lab_N8.json')['runtime_before'];prior=copy.deepcopy(current)
    if fault=='package':current['packages'].append(['fabricated-package','0'])
    elif fault=='native_binary':current['native_libraries'][0]['binary_sha256']='changed'
    elif fault=='thread_environment':current['thread_environment']['OMP_NUM_THREADS']='2'
    else:
        path=tmp_path/'other-python';path.write_bytes(b'wrong executable');current['executable']=str(path)
    with pytest.raises(ValueError,match='differs'):r.runtime_join(prior,current)
