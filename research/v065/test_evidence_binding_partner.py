"""Rejection assertions for test_evidence_bound.py v2 (partner v065p). Each reviewer counterexample of v064p has a
rejection assertion here; passing means the intended EvidenceError is raised. Synthetic suites; no numerical replay."""
import os, sys, json, shutil, importlib, pytest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import test_evidence_bound as teb
def make_root(tmp, a="def test_a():\n    assert True\n", b="def test_b():\n    assert True\n", nested=None):
    root = tmp / 'root'; root.mkdir(parents=True)
    (root / 'test_regression.py').write_text(a); (root / 'test_tbg_ref.py').write_text(b); (root / 'requirements.txt').write_text('numpy\n')
    for f in ('test_evidence_bound.py', 'evidence_plugin.py'): shutil.copy(os.path.join(HERE, f), root / f)
    if nested:
        (root / 'helper_pkg').mkdir(); (root / 'helper_pkg' / '__init__.py').write_text(''); (root / 'helper_pkg' / 'values.py').write_text(nested)
    return root
def _tree(root):
    return {os.path.join(d, f): os.path.getmtime(os.path.join(d, f)) for d, _, fs in os.walk(root) for f in fs}
def ok(root, **kw):
    out = teb.record(str(root), **kw); return out, teb.gate(out, str(root))
def test_import_creates_and_modifies_nothing():
    before = _tree(HERE); importlib.reload(teb); assert _tree(HERE) == before
def test_passing_run_certifies_with_derived_count_and_scope(tmp_path):
    out, c = ok(make_root(tmp_path)); assert c['certified'] and c['passed'] == 2 and 'not the archive' in c['scope'] and c['bound_inputs'] >= 5
def test_failure_error_timeout_reject(tmp_path):
    with pytest.raises(teb.EvidenceError): teb.gate(teb.record(str(make_root(tmp_path / 'f', a="def test_a():\n    assert False\n"))), str(tmp_path / 'f' / 'root'))
    with pytest.raises(teb.EvidenceError): teb.gate(teb.record(str(make_root(tmp_path / 'e', a="def test_a():\n    raise RuntimeError()\n"))), str(tmp_path / 'e' / 'root'))
    r = make_root(tmp_path / 't', a="import time\ndef test_a():\n    time.sleep(30)\n"); out = teb.record(str(r), timeout=2)
    assert json.load(open(os.path.join(out, 'evidence.json')))['timed_out']
    with pytest.raises(teb.EvidenceError, match='timed out'): teb.gate(out, str(r))
def test_skip_xfail_and_nonstrict_xpass_reject(tmp_path):
    for name, body in (('skip', "import pytest\n@pytest.mark.skip\ndef test_a():\n    pass\n"), ('xfail', "import pytest\n@pytest.mark.xfail\ndef test_a():\n    assert False\n"), ('xpass', "import pytest\n@pytest.mark.xfail(strict=False)\ndef test_a():\n    assert True\n")):
        r = make_root(tmp_path / name, a=body); out = teb.record(str(r))
        with pytest.raises(teb.EvidenceError, match='non-passing|xfail|xpass|missing or duplicate calls'): teb.gate(out, str(r))
def test_undeclared_filter_via_PYTEST_ADDOPTS_cannot_hide_a_failing_selected_test(tmp_path, monkeypatch):
    r = make_root(tmp_path, b="def test_b():\n    assert False\n"); monkeypatch.setenv('PYTEST_ADDOPTS', '-k test_a')
    out = teb.record(str(r))                                       # the recorder removes the filter, so the failing test runs
    with pytest.raises(teb.EvidenceError): teb.gate(out, str(r))
    monkeypatch.delenv('PYTEST_ADDOPTS'); r2 = make_root(tmp_path / 'ok'); out2 = teb.record(str(r2)); monkeypatch.setenv('PYTEST_ADDOPTS', '-k nothing')
    with pytest.raises(teb.EvidenceError, match='PYTEST_ADDOPTS'): teb.gate(out2, str(r2))   # current-environment filter also rejects
def test_deselection_in_the_effective_configuration_rejects(tmp_path):
    r = make_root(tmp_path); out = teb.record(str(r)); ex = json.load(open(os.path.join(out, 'execution.json')))
    ex['deselected'] = ['test_tbg_ref.py::test_b']; json.dump(ex, open(os.path.join(out, 'execution.json'), 'w')); ev = json.load(open(os.path.join(out, 'evidence.json'))); ev['artifacts']['execution.json'] = teb.sha(os.path.join(out, 'execution.json')); json.dump(ev, open(os.path.join(out, 'evidence.json'), 'w'))
    with pytest.raises(teb.EvidenceError, match='deselected|match'): teb.gate(out, str(r))
def test_missing_stdout_or_stderr_rejects(tmp_path):
    r = make_root(tmp_path); out, _ = ok(r); ev = json.load(open(os.path.join(out, 'evidence.json')))
    for a in ('stdout.txt', 'stderr.txt'):
        ev2 = dict(ev, artifacts={k: v for k, v in ev['artifacts'].items() if k != a}); v = tmp_path / ('variant_' + a); shutil.copytree(out, v); os.rename(v / a, v / (a + '.withheld')); json.dump(ev2, open(v / 'evidence.json', 'w'))
        with pytest.raises(teb.EvidenceError, match='required artifact'): teb.gate(str(v), str(r))
def test_imported_subpackage_change_rejects(tmp_path):
    r = make_root(tmp_path, a="from helper_pkg.values import VALUE\ndef test_a():\n    assert VALUE == 1\n", nested='VALUE = 1\n'); out, c = ok(r); assert c['certified']
    (r / 'helper_pkg' / 'values.py').write_text('VALUE = 2\n')
    with pytest.raises(teb.EvidenceError, match='stale'): teb.gate(out, str(r))
def test_current_runtime_change_rejects(tmp_path, monkeypatch):
    r = make_root(tmp_path); out, c = ok(r); assert c['certified']; monkeypatch.setenv('OMP_NUM_THREADS', '7')
    with pytest.raises(teb.EvidenceError, match='current runtime'): teb.gate(out, str(r))
def test_adding_or_changing_any_bound_input_rejects_and_historical_mode_is_not_a_certificate(tmp_path):
    r = make_root(tmp_path); out, c = ok(r); assert c['certified']
    (r / 'new_helper.py').write_text('X=1\n')
    with pytest.raises(teb.EvidenceError, match='stale'): teb.gate(out, str(r))
    h = teb.historical_consistency(out); assert h['historical_consistent'] and h['certified'] is False and h['passed'] == 2
    with pytest.raises(teb.EvidenceError, match='explicit source root'): teb.gate(out, None)
def test_tampered_artifacts_and_old_schema_reject(tmp_path):
    r = make_root(tmp_path); out, _ = ok(r)
    with open(os.path.join(out, 'junit.xml'), 'a') as f: f.write('\n<!-- t -->\n')
    with pytest.raises(teb.EvidenceError, match='tampered'): teb.gate(out, str(r))
    r2 = make_root(tmp_path / 'old'); out2, _ = ok(r2); ev = json.load(open(os.path.join(out2, 'evidence.json'))); ev['schema'] = 'partner_test_evidence_v1'; json.dump(ev, open(os.path.join(out2, 'evidence.json'), 'w'))
    with pytest.raises(teb.EvidenceError, match='schema'): teb.gate(out2, str(r2))
def test_reported_count_comes_from_the_execution_log_not_prose(tmp_path):
    r = make_root(tmp_path, b="def test_b():\n    assert True\ndef test_c():\n    assert True\n"); out, c = ok(r); assert c['passed'] == 3
    ex = json.load(open(os.path.join(out, 'execution.json'))); assert len([x for x in ex['reports'] if x['when'] == 'call']) == 3
