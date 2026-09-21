from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
import build_report
import test_evidence as evidence


def fixture_run(tmp_path):
    root = tmp_path / 'project'
    root.mkdir()
    (root / 'module.py').write_text('value = 1\n')
    (root / 'tests').mkdir()
    (root / 'tests/test_case.py').write_text('def test_case(): assert True\n')
    (root / 'requirements.txt').write_text('numpy==2.3.5\n')
    (root / 'results').mkdir()
    (root / 'results/state.json').write_text('{"label":"SAME"}\n')
    folder = root / 'provenance/run'
    folder.mkdir(parents=True)
    (folder / 'stdout.txt').write_text('1 passed\n')
    (folder / 'junit.xml').write_text('<testsuites><testsuite tests="1"><testcase classname="tests.test_case" name="test_case"/></testsuite></testsuites>')
    execution = dict(collected=['tests/test_case.py::test_case'], calls=[dict(nodeid='tests/test_case.py::test_case', outcome='passed', xfail=False)], exit_code=0)
    (folder / 'execution.json').write_text(json.dumps(execution))
    identity = evidence.identity(root)
    record = dict(schema=1, scope='complete tests directory', exit_code=0, run_id='fixture', started_utc='fixture-only',
        identity_before=identity, identity_after=identity, runtime={'fixture': True}, passed=1,
        artifacts={name: evidence.sha(folder / name) for name in ('stdout.txt', 'junit.xml', 'execution.json')})
    path = folder / 'result.json'
    path.write_text(json.dumps(record))
    return root, path


def test_matching_evidence_provides_measured_count(tmp_path):
    root, path = fixture_run(tmp_path)
    assert evidence.read_evidence(root, path, {'fixture': True})['passed'] == 1


@pytest.mark.parametrize('name', ['module.py', 'tests/test_case.py', 'requirements.txt', 'results/state.json'])
def test_changed_code_tests_dependencies_or_measurements_reject_evidence(tmp_path, name):
    root, path = fixture_run(tmp_path)
    with (root / name).open('a') as f:
        f.write('\n# changed\n')
    with pytest.raises(ValueError, match='identity'):
        evidence.read_evidence(root, path, {'fixture': True})


def test_changed_runtime_rejects_evidence(tmp_path):
    root, path = fixture_run(tmp_path)
    with pytest.raises(ValueError, match='environment'):
        evidence.read_evidence(root, path, {'fixture': False})


@pytest.mark.parametrize('fault', ['failed_exit', 'wrong_count', 'tampered_junit', 'missing_artifact', 'skipped', 'missing_call'])
def test_failed_or_incomplete_evidence_cannot_publish(tmp_path, fault):
    root, path = fixture_run(tmp_path)
    record = json.loads(path.read_text())
    if fault == 'failed_exit':
        record['exit_code'] = 1
    elif fault == 'wrong_count':
        record['passed'] = 18
    elif fault == 'tampered_junit':
        (path.parent / 'junit.xml').write_text('modified')
    elif fault == 'missing_artifact':
        record['artifacts'].pop('junit.xml')
    else:
        p = path.parent / 'execution.json'
        data = json.loads(p.read_text())
        if fault == 'skipped':
            data['calls'][0]['outcome'] = 'skipped'
        else:
            data['calls'] = []
        p.write_text(json.dumps(data))
        record['artifacts']['execution.json'] = evidence.sha(p)
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        evidence.read_evidence(root, path, {'fixture': True})


def test_missing_evidence_stops_report_before_any_write(tmp_path, monkeypatch):
    monkeypatch.setattr(build_report, 'ROOT', tmp_path)
    with pytest.raises(FileNotFoundError):
        build_report.main(tmp_path / 'missing.json')
    assert not list(tmp_path.iterdir())


def test_builder_checks_evidence_before_replay_claims(tmp_path, monkeypatch):
    root, path = fixture_run(tmp_path)
    record = json.loads(path.read_text()); record['passed'] = 18; path.write_text(json.dumps(record))
    monkeypatch.setattr(build_report, 'ROOT', root)
    monkeypatch.setattr(evidence, 'runtime_identity', lambda: {'fixture': True})
    monkeypatch.setattr(build_report, 'frozen_protocol', lambda: pytest.fail('replay claims reached before rejecting false test count'))
    with pytest.raises(ValueError, match='count'):
        build_report.main(path)
    assert not (root / 'REPORT.md').exists()
