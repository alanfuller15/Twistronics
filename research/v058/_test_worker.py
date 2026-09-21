"""Fixed complete-suite worker; records collection and actual call outcomes."""
import json
from pathlib import Path
import sys
import pytest


class Recorder:
    def __init__(self):
        self.collected = []
        self.calls = []

    def pytest_collection_finish(self, session):
        self.collected = [item.nodeid for item in session.items]

    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            self.calls.append(dict(nodeid=report.nodeid, outcome=report.outcome, xfail=hasattr(report, 'wasxfail')))


if __name__ == '__main__':
    folder = Path(sys.argv[1]).resolve()
    recorder = Recorder()
    result = int(pytest.main(['tests', '-q', '-p', 'no:cacheprovider', '-o', 'addopts=',
        '--junitxml=' + str(folder / 'junit.xml')], plugins=[recorder]))
    (folder / 'execution.json').write_text(json.dumps(dict(collected=recorder.collected,
        calls=recorder.calls, exit_code=result), indent=2) + '\n')
    raise SystemExit(result)
