"""Generate the ledger and report from accepted, complete, source-bound records."""
import json
from pathlib import Path
from checkpoints import digest,save_json
from protocol import frozen_protocol
from ledger_guard import accepted,grid,kinetic
ROOT=Path(__file__).resolve().parent

def read(rel):return json.loads((ROOT/rel).read_text())
def acc(rel):return accepted(ROOT/rel)
def fmt(x):return f'{x:.10f}'

def main():
    protocol=frozen_protocol();plan=read('PLAN.json');kinetic(plan)
    for name,h in read('REVIEW_SOURCES.json').items():assert digest(ROOT/name)==h
    hist={v:acc('history/'+v+'.json') for v in ['v042','v043','v044','v046']}
    for v in hist:kinetic(read('history/'+v+'_PLAN.json'))
    grid(hist['v043']['cases'],['pre_ann','post_ann']);grid(hist['v044']['cases']);grid(hist['v046']['folds'])
    assert set(hist['v042']['engines'])=={'bm_lab','ref_lab'}
    assert all(set(x)=={'4','6'} for x in hist['v042']['engines'].values())
    old_cleanup=[acc(f'history/v046_cleanup_{e}_N{n}.json') for e in ['bm_lab','ref_lab'] for n in [4,6]]
    grid(old_cleanup)
    cleanup_count={(r['engine'],r['N']):len(r['states']) for r in old_cleanup}
    for v in ['v043','v044']:assert hist[v]['protocol_sha256']==digest(ROOT/'history'/f'{v}_PLAN.json')
    assert hist['v046']['primary_protocol_sha256']==digest(ROOT/'history/v046_PLAN.json')
    folds=[];connectors=[];sources={}
    def bind(rel):sources[rel]=digest(ROOT/rel)
    for f in (ROOT/'history').glob('*.json'):bind(str(f.relative_to(ROOT)))
    for eng in ['bm_lab','ref_lab']:
        for N in [4,6]:
            for case in ['flat_birth','final_ann']:
                rel=f'results/{case}_{eng}_N{N}_refined.json';r=acc(rel);bind(rel)
                assert r['protocol_sha256']==protocol and r['nondegeneracy']['status']=='PASS' and len(r['states'])==9
                assert all(x['measurement']['label']=='OPPOSITE' for x in r['charges'])
                assert all(t['minimum']['gap']>1e-5 for c in r['gapped_checks'] for t in c['trials'])
                if case=='final_ann':assert r['birth_pair_join']['max_distance']<1e-6
                folds.append(r)
            rel=f'results/gapped_{eng}_N{N}/summary.json';r=acc(rel);bind(rel)
            assert r['protocol_sha256']==protocol and len(r['states'])==8 and r['w1_constant']
            for i,s in enumerate(r['states']):
                rel2=f'results/gapped_{eng}_N{N}/state_{i:03d}.json';raw=acc(rel2);bind(rel2)
                assert raw==s and s['protocol_sha256']==protocol
                assert all(t['minimum']['gap']>1e-5 for ts in s['gaps'].values() for t in ts)
            assert [s['anchor_join']['name'] for s in r['states'] if 'anchor_join' in s]==['bridge','endpoint']
            connectors.append(r)
    grid(folds,['flat_birth','final_ann']);grid(connectors)
    bind('PLAN.json');bind('provenance/preparation_join.json')
    prep=read('provenance/preparation_join.json')
    assert prep['status']=='PASS' and prep['source_sha256']==digest(ROOT/'preparation_join_probe.py')
    prep_join=max(r['join']['max_distance'] for r in prep['rows']);prep_round=max(r['rounded_input_error'] for r in prep['rows'])
    lower=read('provenance/lower_inventory_probe.json')
    assert lower['status']=='PASS' and lower['source_sha256']==digest(ROOT/'lower_inventory_probe.py')
    assert all(r['separation']>.001 and all(n['gap']<1e-6 for n in r['nodes']) for r in lower['rows'])
    bind('provenance/lower_inventory_probe.json')
    cases=[]
    for r in folds:
        trials=[t for c in r['charges'] for t in c['measurement']['trials']]
        cases.append(dict(engine=r['engine'],N=r['N'],case=r['case'],parameter=r['event']['parameter'],pair_label='OPPOSITE',root_states=len(r['states']),charge_stations=len(r['charges']),just_open_gap=r['gapped_checks'][0]['trials'][-1]['minimum']['gap'],min_chart_overlap=min(t[s]['min_chart_overlap'] for t in trials for s in ['a','b']),loop_fallbacks=sum(len(c['measurement']['rejected_stages']) for c in r['charges']),birth_join=r.get('birth_pair_join')))
    gs=[s for r in connectors for s in r['states']]
    minimum=min(t['minimum']['gap'] for s in gs for ts in s['gaps'].values() for t in ts)
    seam=min(t['seam_overlap'] for s in gs for rows in s['cycles'].values() for row in rows for t in row['trials'])
    maxjoin=max(abs(x) for s in gs if 'anchor_join' in s for x in s['anchor_join']['gap_differences'].values())
    gapped_cases=[]
    for r in connectors:
        rs=r['states']
        gapped_cases.append(dict(engine=r['engine'],N=r['N'],geometry=plan['engines'][r['engine']]['geometry'],cutoff_tol=plan['engines'][r['engine']]['cutoff_tol'],states=len(rs),min_gap=min(t['minimum']['gap'] for s in rs for ts in s['gaps'].values() for t in ts),min_seam_overlap=min(t['seam_overlap'] for s in rs for rows in s['cycles'].values() for row in rows for t in row['trials']),w1=rs[0]['w1'],w1_constant=r['w1_constant'],anchor_joins=[s['anchor_join'] for s in rs if 'anchor_join' in s],source=f"results/gapped_{r['engine']}_N{r['N']}/summary.json"))
    summary=dict(status='ACCEPT',version='v048',verification_tier='self-tested',delivery_status='unconfirmed',kinetic='lab_nn_full',protocol_sha256=protocol,folds=cases,gapped_cases=gapped_cases,fold_windows=len(folds),root_states=sum(x['root_states'] for x in cases),charge_stations=sum(x['charge_stations'] for x in cases),gapped_states=len(gs),minimum_sampled_gap=minimum,min_cycle_seam_overlap=seam,max_anchor_gap_difference=maxjoin,w1=gs[0]['w1'],supplied_tests=31,targeted_guard_tests=22,source_sha256=sources)
    save_json(ROOT/'SUMMARY.json',summary)
    L=['# Campaign ledger — v048','', 'Generated from accepted summaries and current raw records. The numerical rows are self-tested; finite sampling is not a completeness proof. Exact source paths and SHA256 values are in LEDGER_SOURCES.json. The incoming partner v046 and our v046 are separate contributions.','',
    '## Earlier accepted records','', '| Record | Engine | N | Scope | Recorded states / event parameters |','|---|---|---:|---|---|']
    for r in hist['v044']['cases']:L.append(f"| our v044 | {r['engine']} ({r['geometry']}) | {r['N']} | early braid/deepening/unlinking legs | {r['states']} states; center B={r['center_crossing']:.10f} |")
    for r in hist['v043']['cases']:L.append(f"| our v043 | {r['engine']} | {r['N']} | {r['case']} | {r['states']} states; labels={','.join(r['labels'])} |")
    for eng,rs in hist['v042']['engines'].items():
        for N,r in rs.items():L.append(f"| v042 | {eng} | {N} | braid 2 / first annihilation | ratio={r['braid_crossing']:.10f}; T={r['annihilation']:.10f} |")
    for r in hist['v046']['folds']:L.append(f"| our v046 | {r['engine']} | {r['N']} | cleanup / upper collision | {cleanup_count[r['engine'],r['N']]} cleanup states; ratio={r['ratio']:.10f} |")
    L+=['','## New late-event windows','', '| Case | Engine | Geometry | N | Critical parameter | Root states | Charge stations | Just-open gap (meV) |','|---|---|---|---:|---:|---:|---:|---:|']
    for r in cases:L.append(f"| {r['case']} | {r['engine']} | {plan['engines'][r['engine']]['geometry']} | {r['N']} | {r['parameter']:.10f} | {r['root_states']} | {r['charge_stations']} | {r['just_open_gap']:.8f} |")
    L+=['','## Sampled gapped connections','', '| Engine | N | States | Smallest sampled gap (meV) | Minimum cycle seam overlap | Anchor joins |','|---|---:|---:|---:|---:|---|']
    for r in connectors:
        m=min(t['minimum']['gap'] for s in r['states'] for ts in s['gaps'].values() for t in ts)
        c=min(t['seam_overlap'] for s in r['states'] for rows in s['cycles'].values() for row in rows for t in row['trials'])
        L.append(f"| {r['engine']} | {r['N']} | {len(r['states'])} | {m:.8f} | {c:.8f} | "+', '.join(s['anchor_join']['name'] for s in r['states'] if 'anchor_join' in s)+' |')
    L+=['','Per-band/group w1, reproduced at every newly sampled gapped state:','', '| Band/group | k1 | k2 |','|---|---:|---:|']
    for k,v in summary['w1'].items():L.append(f'| {k} | {v[0]} | {v[1]} |')
    coverage=[dict(item='post-braid-2 late windows and gapped checkpoint joins',status='sampled and accepted',evidence=list(sources.keys())),dict(item='preparation A/B legs',status='anchors and candidate brackets only; continuous replay open'),dict(item='separate lower unlink collision',status='not measured here'),dict(item='N>6 path / global N8 minima / microscopic bilayer validation',status='not established')]
    save_json(ROOT/'COVERAGE.json',coverage)
    L+=['','## Coverage qualifications','']+[f"- {r['item']}: {r['status']}." for r in coverage]
    L+=['','Historical summaries are retained as historical accepted evidence; this generator does not rerun every earlier computation. Preparation anchors are not promoted to accepted fold windows. Model and scope annotations involve reviewed metadata; they are not numerical discoveries made by the formatter.']
    (ROOT/'LEDGER.md').write_text('\n'.join(L)+'\n');save_json(ROOT/'LEDGER_SOURCES.json',sources)
    roots='\n'.join(f"| {r['case']} | {r['engine']} | {r['N']} | {r['parameter']:.10f} |" for r in cases)
    report=f'''# v048 — later folds and gapped joins

All {len(folds)} late-event windows and {len(gs)} sampled gapped states pass the declared gate in both engines at N4/N6. The flat pair is OPPOSITE at both measured charge stations in each birth/annihilation window. Its initial roots match between the birth and final-annihilation records. The gapped connections reproduce the accepted bridge and endpoint gaps and their per-band w1. Numerical evidence is [self-tested]; delivery consumption is [unconfirmed].

| Event | Engine | N | Critical parameter |
|---|---|---:|---:|
{roots}

The birth parameter is w0/w1 at A=−0.35; the final-annihilation parameter is A at w0/w1=1.1. Both use B=−0.4, T=−1.8, phi=80 degrees, eps=0.003. Each window has nine two-seed root states, charge checks at the start and near the event, derivative-step refinement, rank-one Jacobian, nonzero null curvature/transverse parameter slope and positive open-side gap searches. Charge was not separately measured at every interior root state. A failed search was never interpreted as a disappearance.

Five gapped samples per engine/cutoff connect the upper collision's open side through ratio 1.04 to the flat birth's open side; three connect the final annihilation's open side to A=−0.30. Each checks five band gaps on bounded 18/24-grid multistart searches with edge seeds, and five band/group cycle signs on 64/128 meshes at two offsets in each direction. The smallest sampled gap is {minimum:.10f} meV; minimum cycle-seam overlap is {seam:.10f}. Maximum gap difference at the preserved bridge/endpoint anchors is {maxjoin:.3g} meV at stored floating-point precision. Flat1 and the flat pair retain w1=(1,0); flat2 and the two neighboring individual bands retain (0,0). Euler class is not assigned to the nonorientable flat pair.

Primary BM retains linear reciprocal geometry and cutoff_tol=1e-6; TBG retains exact geometry and cutoff_tol=1e-9. Both explicitly use lab_nn_full. The incoming cutoff API is exercised without changing the historical truncations. The shared measurement harness limits estimator independence. All 31 supplied tests pass; 22 targeted cases cover the adopted cutoff API, optional finite-tunneling guard and ledger rejection behavior. The optional patch is not used in the primary measurements.

v047 preparation anchors were also checked at their common B=−0.25 start. Fresh matched-model roots join our v044 records within {prep_join:.3g}. The four-decimal seeds themselves are about {prep_round:.3g} away; a claimed 2e-5 residual is not below the actual 1e-6 join tolerance. The specific old unrounded B-sweep roots were not saved, so we cannot attribute their old residual. Exact/exact agreement is about {prep["exact_cross_engine_difference"]:.3g} here; linear/exact displacement is about {prep["linear_exact_difference"]:.3g}. This confirms one state, not the preparation path or its candidate births/deaths. A separate lower-gap probe resolves two distinct roots where the supplied B-sweep output lists only one; their exact-geometry separation is {lower["rows"][1]["separation"]:.8f}. The birth location and global inventory completeness remain unresolved.

LEDGER.md is generated from source-bound accepted records, with a separate provisional-coverage list. The original v047 ledger reproduces byte for byte, but its hardcoded footer is stale and it does not validate accepted status. Both v046 contributions remain separate. Our v046's tunneling-law and local-convergence qualifications still apply; no new physical model is inferred from ledger generation.

The post-braid-2 route now has measured late-event windows and sampled joins to the endpoint. The preparation leg, its candidate events and the separate lower unlink collision remain explicit gaps in the whole-campaign record. No N>6 path replay, global N8 search, mathematical continuum completeness or physical-bilayer validation is claimed. See SOURCE_REVIEW.md for the ranked findings and deep-read cutoff.
'''
    (ROOT/'REPORT.md').write_text(report)
    share=f'''# TEAM SHARE — our v048

The later flat-pair birth and final annihilation pass in both engines at N4/N6: {len(folds)} fold windows, {summary['root_states']} root-continuation states and {summary['charge_stations']} charge stations. Both stations in each window are OPPOSITE, with nondegenerate-fold and open-gap checks. The pair roots join between the two windows.

{roots}

The {len(gs)} sampled gapped states also pass. They join the upper collision through the ratio-1.04 bridge to the birth window, and the final annihilation to the endpoint. All five measured band/group w1 labels reproduce; the smallest sampled gap is {minimum:.8f} meV. Evidence is self-tested with a shared measurement harness, under the preserved geometry/cutoff choices.

Your cutoff_tol adoption passes the full-operator/default/invalid-input checks. The 31 supplied tests and 22 targeted assertions pass. Your ledger reproduces byte for byte; the updated ledger adds accepted-status/schema checks, source digests and these new rows. Its coverage section keeps preparation candidates separate from accepted events. For your reader: SUMMARY.json now has folds[] with case/parameter, gapped_cases[] with per-engine/cutoff margins and joins, and source_sha256; SCHEMA.md describes the keys.

One version distinction: your v046 adopts our v044; our separate v046 contains the cleanup/upper collision and the v045 claim qualifications. Both are preserved. In v047 §2, 2e-5 is above our 1e-6 join threshold, and our BM primary geometry was linear. Fresh same-model roots join to roundoff; old unrounded B-sweep roots were not saved, so their specific residual remains unattributed.

A further preparation inventory correction: at B=−0.25, two seeded lower-gap roots resolve in all three checked model variants; exact-geometry separation is {lower["rows"][1]["separation"]:.8f}. The supplied one-node count is incomplete. This does not locate the birth.

Next is the preparation route and its event candidates, then the separate lower unlink collision. The post-braid-2 late windows and sampled joins are covered; the entire campaign is not yet fully replayed. The constant-tunneling approximation, local-only N8 convergence and physical-validation limits remain explicit.
'''
    # A proper table header accompanies the data rows in the short note.
    share=share.replace('\n'+roots+'\n','\n| Event | Engine | N | Critical parameter |\n|---|---|---:|---:|\n'+roots+'\n')
    (ROOT/'TEAM_SHARE_v048.md').write_text(share)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
