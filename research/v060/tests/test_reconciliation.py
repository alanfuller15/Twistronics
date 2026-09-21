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
    assert result['states']==5 and result['roots']==30 and result['coarse_checks']==2 and result['frame_checkpoints']==5
    assert result['labels'][0]=='SAME' and result['labels'][-1]=='OPPOSITE'


@pytest.mark.parametrize('fault',['rejected','missing_state','wrong_state','wrong_plan','runtime','node_failure','node_gap','node_seed','root_jump','rectangle','mesh','charge','radius','retry','gap_minimum','coarse','event_tolerance','event_failure','singular_reason','stale_event'])
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
    elif fault=='event_tolerance':c['event']['trials'][0]['xtol']=.1
    elif fault=='event_failure':c['event']['trials'][-1]['converged']=False
    elif fault=='singular_reason':c['event']['rejection_reason']='eigen residual'
    elif fault=='stale_event':c['event']['nodes']['X1']['gap']=.01
    with pytest.raises(ValueError):r.validate_case(c,'bm_lab',p,h)


def frame_fixture(tmp_path):
    arrays={k:np.eye(4)[:,:2] for k in ['frame_a','frame_b','spatial','spatial_fast','coarse_a','coarse_b']}
    np.savez_compressed(tmp_path/'frames.npz',**arrays)
    row=dict(frames_sha256=sha(tmp_path/'frames.npz'),rectangle_determinant=1.,spatial_mesh_determinant=1.)
    write(tmp_path/'record.json',row);return arrays,row


@pytest.mark.parametrize('fault',['hash','record','shape','nonfinite','orthogonality','rectangle','spatial_mesh','initial_frame'])
def test_saved_frame_failures_reject(tmp_path,fault):
    arrays,row=frame_fixture(tmp_path);r.frames(tmp_path,row,4,None)
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
    with pytest.raises(ValueError):r.frames(tmp_path,row,4,None)


def test_reconciliation_matches_hashed_historical_targets():
    result=r.build()
    assert len(result['cutoff_comparisons'])==2
    assert all(len(c['common_states'])==2 and all(q['N6_label']==q['N8_label'] for q in c['common_states']) for c in result['cutoff_comparisons'])
