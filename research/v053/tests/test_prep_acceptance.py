from pathlib import Path
import sys,json,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from prep_acceptance import validate
from protocol import frozen_protocol
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'results/prep_bm_lab_N4'

def test_complete_n4_frame_replay_is_publishable():
    assert validate(SOURCE,frozen_protocol())['status']=='ACCEPT'

@pytest.mark.parametrize('fault',['pilot','partial','missing_coarse','wrong_gap','missing_frame_transport','wrong_endpoint_orientation'])
def test_incomplete_or_misreported_replay_rejected(tmp_path,fault):
    dest=tmp_path/'case';shutil.copytree(SOURCE,dest);r=json.loads((dest/'summary.json').read_text());changed=None
    if fault=='pilot':r['pilot']=True
    elif fault=='partial':r['status']='PARTIAL'
    elif fault=='missing_coarse':changed=2;r['states'][2]['parameter_mesh_check']=None
    elif fault=='wrong_gap':changed=1;r['states'][1]['nodes'][0]['index']=2
    elif fault=='missing_frame_transport':changed=1;r['states'][1]['temporal_transport']=[]
    elif fault=='wrong_endpoint_orientation':changed=18;r['states'][18]['endpoint_join']['relative_orientation']=-1
    if changed is not None:(dest/f'step_{changed:03d}/record.json').write_text(json.dumps(r['states'][changed]))
    (dest/'summary.json').write_text(json.dumps(r))
    with pytest.raises(ValueError):validate(dest,frozen_protocol())
