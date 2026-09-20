from pathlib import Path
import sys,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from anchor_quality import classify_anchor

def row():return dict(bm_roots=[[.1,.2],[.3,.4]],ref_roots=[[.1,.2],[.3,.4]],bm_gaps=[1e-10,1e-10],ref_gaps=[1e-10,1e-10],label='OPPOSITE')
def test_zero_gap_duplicate_is_not_pair():
    x=row();x['bm_roots'][1]=x['bm_roots'][0]
    assert classify_anchor(x)=='DUPLICATE_OR_UNRESOLVED'
def test_coincident_positive_gap_is_not_tracker_collapse_at_zero():
    x=row();x['bm_roots'][1]=x['bm_roots'][0];x['bm_gaps']=[1.26,1.26]
    assert classify_anchor(x)=='NONZERO_RESIDUAL_CANDIDATES'
def test_ungated_label_is_not_promoted():
    assert classify_anchor(row())=='TWO_LOCAL_ROOTS_UNGATED_CHARGE'
@pytest.mark.parametrize('value',[float('nan'),float('inf'),-.1])
def test_invalid_gap_rejected(value):
    x=row();x['ref_gaps'][1]=value
    with pytest.raises(ValueError):classify_anchor(x)
