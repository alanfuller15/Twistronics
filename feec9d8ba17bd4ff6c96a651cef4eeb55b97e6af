import copy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
import compare_impact as ci
from evidence import read,sha
from legacy_trace import inspect_source


def test_saved_controlled_comparison_reproduces():
    r=ci.build();assert r==read(ci.ROOT/'IMPACT.json')
    assert r['label_changes']==0 and r['second_attempt_calls_by_variant']=={'defective':0,'repaired':0}


@pytest.mark.parametrize('fault',['protocol','recipe','model','state','failed','label','value','stale'])
def test_unmatched_or_invalid_probe_is_not_publishable(fault):
    a=read(ci.ROOT/'results/legacy_defective.json');b=read(ci.ROOT/'results/legacy_repaired.json');p=read(ci.ROOT/'IMPACT_PLAN.json')
    c=b['cases'][0]
    if fault=='protocol':b['impact_plan_sha256']='bad'
    elif fault=='recipe':b['cases'].pop()
    elif fault=='model':c['Hstat_sha256']='different'
    elif fault=='state':c['state']['A']=9
    elif fault=='failed':c['status']='RECIPE_REJECTED'
    elif fault=='label':c['measurement']['label']='OPPOSITE'
    elif fault=='value':c['refine_calls'][0]['recomputed_value']=1
    else:
        c['refine_calls'][0]['reported_metadata']['status']=99
        c['measurement']['metadata'][0]['status']=99
    with pytest.raises(ValueError):ci.compare(a,b,p,sha(ci.ROOT/'IMPACT_PLAN.json'))


def test_trace_resolves_imported_and_simple_assigned_aliases():
    r=inspect_source('from euler import euler as compute\nx = model.refine\ncompute()\nx()\n')
    assert [x['resolved_name'] for x in r['calls']]==['euler.euler','model.refine']


def test_trace_distinguishes_assertion_from_print_and_preserves_receiver():
    r=inspect_source("def pair():\n assert info['success']\n print(info['success'])\n tbg.refine()\n")
    assert r['success_reads'][0]['enclosing_control']==['Assert']
    assert r['success_reads'][1]['enclosing_control']==[]
    assert r['calls'][0]['call']=='tbg.refine'
