"""Rejection assertions for the two reviewer reproductions and nearby incomplete records."""
from pathlib import Path
import json,shutil,pytest,threadpoolctl
import test_evidence_bound as t
from test_evidence_binding_partner import make_root,ok
HERE=Path(__file__).resolve().parent
def unavailable():raise RuntimeError('review-injected native capture failure')
def test_native_capture_failure_rejects_at_record_validation(tmp_path,monkeypatch):
    root=make_root(tmp_path);monkeypatch.setattr(threadpoolctl,'threadpool_info',unavailable)
    bundle=t.record(str(root))
    with pytest.raises(t.EvidenceError,match='native identity'):t.gate(bundle,str(root))
def test_current_native_capture_failure_rejects(tmp_path,monkeypatch):
    root=make_root(tmp_path);bundle,_=ok(root);monkeypatch.setattr(threadpoolctl,'threadpool_info',unavailable)
    with pytest.raises(t.EvidenceError,match='native identity'):t.gate(bundle,str(root))
@pytest.mark.parametrize('kind',['empty','missing_hash'])
def test_incomplete_recorded_native_identity_rejects(tmp_path,kind):
    root=make_root(tmp_path);bundle,_=ok(root);path=Path(bundle)/'evidence.json';ev=json.loads(path.read_text())
    for key in ['runtime_before','runtime_after']:
        if kind=='empty':ev[key]['native']=[]
        else:ev[key]['native'][0]['sha256']=None
    path.write_text(json.dumps(ev))
    with pytest.raises(t.EvidenceError,match='native identity'):t.historical_consistency(bundle)
@pytest.mark.parametrize('variant',['missing_setup','missing_teardown','duplicate_setup','unknown_phase','unknown_node'])
def test_incomplete_or_extraneous_phase_records_reject(tmp_path,variant):
    root=make_root(tmp_path);bundle,_=ok(root);p=Path(bundle);ex=json.loads((p/'execution.json').read_text())
    if variant.startswith('missing_'):ex['reports']=[r for r in ex['reports'] if r['when']!=variant.split('_')[1]]
    else:
        row=dict(next(r for r in ex['reports'] if r['when']=='setup'))
        if variant=='unknown_phase':row['when']='unknown'
        if variant=='unknown_node':row['nodeid']='test_absent.py::test_absent'
        ex['reports'].append(row)
    (p/'execution.json').write_text(json.dumps(ex));ev=json.loads((p/'evidence.json').read_text());ev['artifacts']['execution.json']=t.sha(p/'execution.json');(p/'evidence.json').write_text(json.dumps(ev))
    with pytest.raises(t.EvidenceError,match='setup/call/teardown'):t.gate(bundle,str(root))
def test_session_collection_count_disagreement_rejects(tmp_path):
    root=make_root(tmp_path);bundle,_=ok(root);p=Path(bundle);ex=json.loads((p/'execution.json').read_text());ex['testscollected']+=1;(p/'execution.json').write_text(json.dumps(ex))
    ev=json.loads((p/'evidence.json').read_text());ev['artifacts']['execution.json']=t.sha(p/'execution.json');(p/'evidence.json').write_text(json.dumps(ev))
    with pytest.raises(t.EvidenceError,match='testscollected'):t.gate(bundle,str(root))
