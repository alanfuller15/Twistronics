"""Fault injection: failed optimizer records must survive the exception."""
import json,runpy,sys,types
from pathlib import Path
import numpy as np
import pytest
import scipy.optimize
SCRIPT=Path(__file__).resolve().parents[1]/'fixes/endpoint_locate.py'
@pytest.mark.parametrize('success,coordinate,should_raise',[(False,.5,True),(True,float('nan'),True),(True,.5,False)])
def test_optimizer_records_persist(monkeypatch,tmp_path,success,coordinate,should_raise):
    class FakeTBG:
        def __init__(self,**kwargs):pass
        def gap(self,i):return lambda f:1.
    monkeypatch.setitem(sys.modules,'tbg_ref',types.SimpleNamespace(TBG=FakeTBG))
    monkeypatch.setattr(scipy.optimize,'minimize',lambda *a,**kw:types.SimpleNamespace(success=success,fun=1.,x=np.array([coordinate,.5]),nfev=1,message='injected'))
    monkeypatch.setattr(sys,'argv',[str(SCRIPT),'4',json.dumps({str(i):[.5,.5] for i in range(1,5)})])
    monkeypatch.chdir(tmp_path)
    if should_raise:
        with pytest.raises(RuntimeError):runpy.run_path(str(SCRIPT),run_name='__main__')
    else:runpy.run_path(str(SCRIPT),run_name='__main__')
    rows=json.loads((tmp_path/'endpoint_locate_N4_gap1_starts.json').read_text())
    assert len(rows)==1 and rows[0]['success']==success and rows[0]['message']=='injected'
