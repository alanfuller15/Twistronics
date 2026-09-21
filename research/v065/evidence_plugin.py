"""pytest plugin loaded by the recorder (-p evidence_plugin). Writes an INDEPENDENT execution log (not derived from
JUnit): collected node ids, deselected node ids, per-phase outcomes with wasxfail, effective invocation args, env
filters, plugins. Output path from EVIDENCE_EXEC_LOG."""
import json, os, sys
LOG = {'collected': [], 'deselected': [], 'reports': [], 'config': {}}
def pytest_configure(config):
    LOG['config'] = dict(invocation_args=list(config.invocation_params.args), rootdir=str(config.rootdir), inifile=str(config.inipath) if config.inipath else None,
                         plugins=sorted(str(p) for p in config.pluginmanager.get_plugins() if not str(p).startswith('<_pytest')),
                         PYTEST_ADDOPTS=os.environ.get('PYTEST_ADDOPTS'), keyword=config.getoption('keyword', default=None), markexpr=config.getoption('markexpr', default=None),
                         deselect_opt=config.getoption('deselect', default=None), strict_xfail=bool(config.getini('xfail_strict')) if 'xfail_strict' in config._parser._inidict else None)
def pytest_collection_finish(session): LOG['collected'] = [i.nodeid for i in session.items]
def pytest_deselected(items): LOG['deselected'] += [i.nodeid for i in items]
def pytest_runtest_logreport(report):
    LOG['reports'].append(dict(nodeid=report.nodeid, when=report.when, outcome=report.outcome, wasxfail=hasattr(report, 'wasxfail'), duration=report.duration))
def pytest_sessionfinish(session, exitstatus):
    LOG['exitstatus'] = int(exitstatus); LOG['testsfailed'] = session.testsfailed; LOG['testscollected'] = session.testscollected
    p = os.environ.get('EVIDENCE_EXEC_LOG')
    if p:
        with open(p, 'w') as f: json.dump(LOG, f, indent=1)
