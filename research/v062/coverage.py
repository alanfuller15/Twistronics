"""Scope ledger from retained campaign records and named N8 batches."""
from pathlib import Path
from evidence import read,sha,require,write
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]

def build(current):
    source=REPO/'research/v056/results/campaign_map.json';old=read(source)
    groups={}
    for row in old['claim_rows']:
        if row['role']=='superseded_replay':continue
        groups.setdefault(row['family'],[]).append(row)
    notes={
        'braid2':('v060 + v062','Fifteen distinct sampled ratios per engine over .990–1.000; inherited U frames, crossing rejection, mesh/radius checks.','No continuous-interval proof or other connecting leg.'),
        'first_ann':('v061','N8 fold, opposite pre-event pair, opening witnesses and post-event upper SAME checkpoint; original rejects and separate recovery retained.','No continuous charge-transfer proof through the collision or full pre/post connection.'),
        'lower_unlink':('v059','N8 local lower-pair fold, charge and opening witnesses.','No complete N8 preparation path or global zero-count proof.'),
        'endpoint_checkpoint':('v058','N8 endpoint lower/flat/upper/next gap searches.','Per-band w1 was not extended to N8 in that gap batch.')}
    rows=[]
    for family,records in groups.items():
        batch,scope,remaining=notes.get(family,('Not extended','Retained N4/N6 evidence only for this family.','N8 replay and the stated family-specific frame/topology gates remain open.'))
        rows.append(dict(family=family,historical_cutoffs=sorted({x['N'] for x in records}),historical_sources=[dict(path=x['record'],sha256=x['record_sha256']) for x in records],N8_batch=batch,N8_scope=scope,remaining=remaining))
    inputs={source.relative_to(REPO).as_posix():sha(source)}
    for version,status in [('v058','BOUNDED_N8_ENDPOINT_COMPARISON_COMPLETE'),('v059','BOUNDED_N8_LOWER_UNLINK_COMPLETE'),('v061','BOUNDED_N8_FIRST_ANN_COMPLETE')]:
        path=REPO/'research'/version/'SUMMARY.json';summary=read(path)
        require(summary['status']==status,'unexpected coverage source status')
        require(all(x['N']==8 for x in summary['cases']),'coverage cutoff changed')
        inputs[path.relative_to(REPO).as_posix()]=sha(path)
    require(all(x['distinct_states']==15 for x in current['combined_braid2_chain']),'braid coverage count mismatch')
    return dict(version='our_v062',scope='Evidence coverage by the retained v056 campaign families; old numerical calculations were not rerun to make this ledger.',rows=rows,source_sha256=inputs,additional_open=['Initial Euler-class and flat-pair frame/topology checks at N8 are not established by these U-pair/critical-event/endpoint-gap batches.','Every continuous-path, infinite-cutoff and physical-validation claim remains outside this finite sampled coverage.','Unlisted historical scalar/mass/angle and exploratory consumers remain impact-unverified.'])

if __name__=='__main__':
    r=build(read(ROOT/'IMPACT.json'));write(ROOT/'COVERAGE.json',r);print('Coverage families:',len(r['rows']))
