import sys,copy
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import coverage
from evidence import read
ROOT=Path(__file__).resolve().parents[1]

def test_coverage_keeps_all_historical_families_and_open_limits():
    c=coverage.build(read(ROOT/'IMPACT.json'));old=read(coverage.REPO/'research/v056/results/campaign_map.json')
    expected={x['family'] for x in old['claim_rows'] if x['role']!='superseded_replay'}
    assert {x['family'] for x in c['rows']}==expected
    rows={x['family']:x for x in c['rows']}
    assert rows['cleanup']['N8_batch']=='Not extended'
    assert rows['braid2']['N8_batch']=='v060 + v062'
    assert 'w1 was not extended' in rows['endpoint_checkpoint']['remaining']

def test_incomplete_braid_chain_cannot_get_full_sampled_extent():
    current=read(ROOT/'IMPACT.json');current['combined_braid2_chain'][0]['distinct_states']=14
    with pytest.raises(ValueError,match='coverage count'):coverage.build(current)
