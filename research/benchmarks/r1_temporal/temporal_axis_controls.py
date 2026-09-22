"""Explicit D-axis rejection cases, supplementing the eight core controls."""
import json,importlib.util
from transport import ROOT,PLAN,Chart3,edge,sha
spec=importlib.util.spec_from_file_location('temporal_core_controls',ROOT/'controls.py')
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
out={'plan_sha256':sha(ROOT/'PLAN.json'),'sources':{n:sha(ROOT/n) for n in ['temporal_axis_controls.py','controls.py','transport.py']},'rows':[]}
for cfg in PLAN['mesh_levels']:
    chart=Chart3(core.Toy(),[1.,.5,0.]);a=[0.,0.,-.2];b=[0.,0.,.2]
    report,points=edge(chart,a,b,cfg,2)
    endpoints=[min(chart.data(v)['gaps']) for v in [a,b]];middle=min(chart.data([0.,0.,0.])['gaps'])
    passed=min(endpoints)>.001 and middle<1e-12 and not report['pass']
    out['rows'].append({'name':'D_axis_degeneracy_rejected_'+cfg['name'],'endpoints_gap_meV':endpoints,'middle_gap_meV':middle,'edge':report,'accepted_charge':None,'pass':bool(passed)})
    print(out['rows'][-1]['name'],passed)
out['all_controls_pass']=all(r['pass'] for r in out['rows'])
(ROOT/'TEMPORAL_AXIS_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
if not out['all_controls_pass']:raise SystemExit(1)
