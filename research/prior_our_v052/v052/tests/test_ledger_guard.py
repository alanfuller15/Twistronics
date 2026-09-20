from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from ledger_guard import accepted,grid,kinetic

def test_rejected_summary_cannot_be_published(tmp_path):
    p=tmp_path/'x.json';p.write_text(json.dumps(dict(status='REJECTED',states=100)))
    with pytest.raises(ValueError,match='ACCEPT'):accepted(p)

def test_nan_cannot_be_published_even_if_status_accept(tmp_path):
    p=tmp_path/'x.json';p.write_text('{"status":"ACCEPT","gap":NaN}')
    with pytest.raises(ValueError,match='nonfinite'):accepted(p)

def test_missing_cutoff_or_duplicate_case_cannot_be_published():
    rows=[dict(engine=e,N=n) for e in ['bm_lab','ref_lab'] for n in [4,6]]
    grid(rows)
    for bad in [rows[:-1],rows+[rows[0]]]:
        with pytest.raises(ValueError,match='grid'):grid(bad)

def test_changed_model_cannot_inherit_header():
    kinetic({'kinetic':'lab_nn_full'})
    with pytest.raises(ValueError,match='kinetic'):kinetic({'kinetic':'none'})
    with pytest.raises(ValueError,match='kinetic'):kinetic({'kinetic':'lab_nn_full','engines':{'bm_lab':{'kinetic':'none'}}})

def test_legacy_descriptive_engine_schema_requires_explicit_model():
    kinetic({'kinetic':'lab_nn_full','engines':{'bm_lab':'historical description'}})
    with pytest.raises(ValueError,match='kinetic'):kinetic({'engines':{'bm_lab':'historical description'}})
