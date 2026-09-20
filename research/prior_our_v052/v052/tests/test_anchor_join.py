from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
import run_lower
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'anchors/early_bm_lab_N4.json'

def test_lower_roots_join_retained_early_route():
    r=json.loads(SOURCE.read_text());join=run_lower.anchor_join('bm_lab',4,[r['nodes']['L1'],r['nodes']['L2']])
    assert join['max_distance']==0

@pytest.mark.parametrize('fault',['state','geometry','status','engine','N','shifted_root'])
def test_incompatible_anchor_cannot_join(tmp_path,monkeypatch,fault):
    r=json.loads(SOURCE.read_text());nodes=[dict(r['nodes']['L1']),dict(r['nodes']['L2'])]
    if fault=='state':r['state']['B']=-.24
    elif fault=='geometry':r['geometry']='exact'
    elif fault=='status':r['status']='REJECTED'
    elif fault=='engine':r['engine']='ref_lab'
    elif fault=='N':r['N']=6
    elif fault=='shifted_root':nodes[0]['f']=[nodes[0]['f'][0]+.01,nodes[0]['f'][1]]
    (tmp_path/'anchors').mkdir();(tmp_path/'anchors/early_bm_lab_N4.json').write_text(json.dumps(r))
    monkeypatch.setattr(run_lower,'ROOT',tmp_path)
    with pytest.raises(ValueError):run_lower.anchor_join('bm_lab',4,nodes)
