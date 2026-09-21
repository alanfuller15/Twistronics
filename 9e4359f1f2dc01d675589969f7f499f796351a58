from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import ast,types
import numpy as np
import pytest
from scipy.optimize import OptimizeResult,minimize
from evidence import read,sha,require
ROOT=Path(__file__).resolve().parents[1]
plan=read(ROOT/'NUMERICAL_PLAN.json');source=ROOT.parents[1]/plan['paths']['repaired']
require(sha(source)==plan['inputs'][plan['paths']['repaired']],'repaired source changed')
cls=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.ClassDef) and n.name=='BM')
fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='refine')
bm_strain=types.ModuleType('tested_refine_only');bm_strain.np=np;bm_strain.minimize=minimize
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(source),'exec'),bm_strain.__dict__)
bm_strain.BM=type('BM',(),{'refine':bm_strain.refine})


def result(x=(.2, .3), fun=.13, success=True, status=0, message='done', nfev=7):
    return OptimizeResult(x=np.asarray(x), fun=fun, success=success, status=status, message=message, nfev=nfev)


def model(monkeypatch, outcomes):
    calls = iter(outcomes)
    monkeypatch.setattr(bm_strain, 'minimize', lambda *a, **k: next(calls))
    return bm_strain.BM.__new__(bm_strain.BM)


@pytest.mark.parametrize('first_ok,last_ok', [(True, False), (False, True), (True, True), (False, False)])
def test_wrapped_retry_controls_metadata(monkeypatch, first_ok, last_ok):
    m = model(monkeypatch, [result(x=(1.2, .3), success=first_ok, message='first', nfev=5),
        result(success=last_ok, status=0 if last_ok else 2, message='final', nfev=9)])
    f, value, meta = m.refine([1.2, .3], lambda f: float(f @ f), return_result=True)
    assert meta['success'] is last_ok and meta['optimizer_success'] is last_ok
    assert meta['status'] == (0 if last_ok else 2) and meta['message'] == 'final'
    assert meta['nfev'] == 14 and meta['final_nfev'] == 9
    assert [x['message'] for x in meta['attempts']] == ['first', 'final']
    assert value == pytest.approx(float(f @ f))


def test_plain_call_rejects_failed_final_attempt(monkeypatch):
    m = model(monkeypatch, [result(x=(1.2, .3)), result(success=False, status=2)])
    with pytest.raises(ValueError, match='did not converge'):
        m.refine([1.2, .3], lambda f: float(f @ f))


@pytest.mark.parametrize('bad', [result(x=(np.nan, .3)), result(x=(np.inf, .3)), result(fun=np.nan), result(fun=np.inf)])
def test_nonfinite_final_result_is_explicitly_rejected(monkeypatch, bad):
    m = model(monkeypatch, [result(x=(1.2, .3)), bad])
    _, _, meta = m.refine([1.2, .3], lambda f: float(f @ f), return_result=True)
    assert not meta['success'] and 'nonfinite final coordinate or objective' in meta['rejection_reasons']
    assert len(meta['attempts']) == 2 and not meta['attempts'][-1]['finite']


def test_nonfinite_canonical_evaluation_rejected(monkeypatch):
    m = model(monkeypatch, [result()])
    with pytest.raises(ValueError, match='nonfinite'):
        m.refine([.2, .3], lambda f: float('nan'))


def test_wrap_value_mismatch_is_rejected(monkeypatch):
    m = model(monkeypatch, [result(x=(1.2, .3)), result(x=(1.2, .3), fun=1.53)])
    with pytest.raises(ValueError, match='periodic wrap'):
        m.refine([1.2, .3], lambda f: float(f @ f))


def test_returned_value_belongs_to_returned_coordinate(monkeypatch):
    m = model(monkeypatch, [result(fun=.13000001)])
    f, value, meta = m.refine([.2, .3], lambda f: float(f @ f), return_result=True)
    assert value == float(f @ f) and meta['attempts'][0]['value'] == .13000001


def test_real_optimizer_smoke():
    m = bm_strain.BM.__new__(bm_strain.BM)
    target = np.array([.27, .61])
    f, value, meta = m.refine([.3, .6], lambda f: float(np.sum((f-target)**2)), return_result=True)
    assert meta['success'] and np.linalg.norm(f-target) < 1e-6 and value < 1e-12
