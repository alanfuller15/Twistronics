"""Publish dynamic measured claims after bound tests and artifact checks."""
import argparse,json
from pathlib import Path
from evidence import read,sha,write,require
from protocol import frozen_protocol
from test_evidence import read_evidence
import reconcile,coverage
ROOT=Path(__file__).resolve().parent

def collect(evidence):
    tests=read_evidence(ROOT,evidence);protocol=frozen_protocol();r=reconcile.build()
    require(r==read(ROOT/'IMPACT.json'),'stale continuation reconciliation')
    ledger=coverage.build(r);require(ledger==read(ROOT/'COVERAGE.json'),'stale coverage ledger')
    return dict(r,protocol_sha256=protocol,tests=tests,test_evidence=Path(evidence).resolve().relative_to(ROOT).as_posix(),impact_sha256=sha(ROOT/'IMPACT.json'),coverage_sha256=sha(ROOT/'COVERAGE.json'))

def main(evidence):
    s=collect(evidence);t=s['tests'];baseline=read(ROOT/'BASELINE.json')
    state_table='| Ratio w0/w1 | BM N8 | Reference N8 |\n|---:|---|---|\n'
    for j,ratio in enumerate(s['ratios']):state_table+=f"| {ratio:.5f} | {s['cases'][0]['labels'][j]} | {s['cases'][1]['labels'][j]} |\n"
    compare='| Engine | Retained cutoff | Common ratios | Labels match | Maximum root displacement |\n|---|---:|---:|---|---:|\n'
    for c in s['cutoff_comparisons']:compare+=f"| {c['engine']} | N{c['saved_cutoff']} | {len(c['common_states'])} | {c['labels_match']} | {c['max_node_displacement']:.9g} |\n"
    nstates=sum(c['measured_states'] for c in s['cases']);new=sum(c['new_states'] for c in s['cases']);ncoarse=sum(c['coarse_checks'] for c in s['cases'])
    gap=min(c['min_comparison_gap'] for c in s['cases']);overlap=min(c['min_comparison_overlap'] for c in s['cases']);retries=sum(c['loop_retry_stages'] for c in s['cases'])
    root_join=max(max(c['join']['root_shifts'].values()) for c in s['cases']);frame_join=max(max(c['join']['aligned_max_errors'].values()) for c in s['cases'])
    note=f'''# TEAM SHARE — our v062

The N8 braid-2 U-pair continuation now reaches ratio 1.00000 in both lab_nn_full engines. This batch starts from the retained v060 ratio=.99100 roots and temporal/coarse frames. It measures the join again and carries both individual node orientations through ten new states per engine. Combined with retained v060, the sampled braid-2 chain spans .99000–1.00000 at fifteen distinct ratios per engine. The earlier crossing calculation remains the v060 measurement; it was not rerun here.

{state_table}
Each engine preserves its inherited temporal charges: BM **{s['cases'][0]['temporal_charges']}**, reference **{s['cases'][1]['temporal_charges']}**. Those absolute signs depend on the initial gauge. The directly transported spatial comparison is a separate observable. Cross-engine spatial label agreement: **{s['cross_engine_labels_match']}**.

The repeated join moved roots by at most **{root_join:.9g}** in fractional reciprocal coordinates and aligned temporal frame entries by at most **{frame_join:.9g}**. Raw node subspaces were checked against both predecessor temporal and coarse frames. Saved frames also pass orthonormality, temporal polar-alignment, orientation and coarse/fine checks. The unwrapped chart remains [0,1] × [0,1.1]; U2 is not silently wrapped below f2=1.

Fresh evidence: **{nstates} measured states**, including two repeated joins and **{new} new states**, **{nstates*6} refined roots**, **{ncoarse} coarse/fine parameter-frame comparisons**, **{nstates} frame checkpoints** and **{nstates*3} mesh/radius trial sets**. Each trial set includes both temporal charges and the spatial B charge. The first parameter comparison uses .0005 fine/.001 coarse spacing; the remaining four per engine use .001 fine/.002 coarse, including the 1.000 endpoint. Spatial transport uses 128/256 base steps, adjacent-node seeds and refinement of sampled interior minima in both exterior gaps. Minimum sampled/located comparison gap: **{gap:.9g} meV**; minimum spatial overlap: **{overlap:.9g}**. Phase-only retry stages used: **{retries}**.

{compare}
All six named roots are compared at the ten common retained ratios .991 through 1.000. The .9915 checkpoint is new sampling. Maximum BM/reference endpoint-root displacement: **{s['cross_engine_max_endpoint_node_distance']:.9g}**. This reflects the declared model conventions; no cross-engine coordinate equality was forced.

Held state: A=0, B=−.4, T=−.8, phi=80°, theta=1.05°, eps=.003, w_kappa=0 and w_mode=average. The model keeps w1=110 meV and w0=110 times the varied ratio. BM uses linear reciprocal geometry/cutoff_tol=1e-6; reference uses exact reciprocal geometry/cutoff_tol=1e-9. Dimension is 1060 in both engines. All earlier v061 diagnostic/recovery evidence and failures remain unchanged.

Runtime records are stable within each new run. The predecessor used the invocation name `python`; this batch used `python3`. Reconciliation verifies that both names resolve to the same executable and SHA-256, and that every other recorded runtime field matches. The original records retain both names; this is not claimed as literal record equality.

Publication uses **{t['passed']} actual assertion passes** from complete-suite run `{t['run_id']}`, bound to code, tests, inputs, results and runtime. The numerical plan was frozen before workers; the publication plan was frozen after measurements and before this test run. All **{baseline['preserved_files']}** prior tracked files are preserved, with the previous README retained in provenance. The ZIP contains the complete research, audit and team history.

The coverage ledger (`COVERAGE.md` / `COVERAGE.json`) maps retained N4/N6 campaign families to the specific N8 work now available. The next bounded workflow is the first cleanup connection after braid 2, starting at this ratio=1.000 checkpoint, under a separately frozen budget and inherited frame/seed joins. Completing this ratio leg does not complete the N8 campaign.

Limits:

'''+''.join('- '+x+'\n' for x in s['limits'])+'''
Start with `research/v062/REPORT.md`, `SUMMARY.json`, `IMPACT.json`, `COVERAGE.md`, `NUMERICAL_PLAN.json` and `METHOD.md`. Full measurements and frame arrays are in `results/`; the exact prior checkpoint references are in the numerical plan. Tests and worker output are in `provenance/`.
'''
    ledger=read(ROOT/'COVERAGE.json');md='# N8 campaign coverage at v062\n\n'+ledger['scope']+'\n\n| Family | Retained cutoffs | N8 batch | N8 evidence | Remaining limit |\n|---|---|---|---|---|\n'
    for row in ledger['rows']:md+='| '+row['family']+' | '+', '.join('N'+str(n) for n in row['historical_cutoffs'])+' | '+row['N8_batch']+' | '+row['N8_scope']+' | '+row['remaining']+' |\n'
    md+='\n'+''.join('- '+x+'\n' for x in ledger['additional_open'])
    write(ROOT/'SUMMARY.json',s);(ROOT/'COVERAGE.md').write_text(md);(ROOT/'TEAM_SHARE_v062.md').write_text(note);(ROOT/'REPORT.md').write_text(note.replace('# TEAM SHARE — our v062','# Our v062: N8 braid-2 continuation',1))
    print(json.dumps(dict(status=s['status'],tests=t,measured_states=nstates,new_states=new,min_comparison_gap=gap),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test-evidence',type=Path,required=True);main(p.parse_args().test_evidence)
