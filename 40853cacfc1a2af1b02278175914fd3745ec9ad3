"""Publish only reconciled saved evidence and source-bound test outcomes."""
import argparse,json
from pathlib import Path
import campaign_map,compare_impact,legacy_trace
from evidence import read,require,sha,write
from protocol import frozen_protocol
from test_evidence import read_evidence
ROOT=Path(__file__).resolve().parent

def collect(evidence):
    tests=read_evidence(ROOT,evidence)
    protocol=frozen_protocol()
    outputs={}
    for name,build in [('results/campaign_map.json',campaign_map.build),('results/legacy_trace.json',legacy_trace.build),('IMPACT.json',compare_impact.build)]:
        saved=read(ROOT/name);require(saved==build(),'stale publication input: '+name);outputs[name]=sha(ROOT/name)
    m=read(ROOT/'results/campaign_map.json');i=read(ROOT/'IMPACT.json');trace=read(ROOT/'results/legacy_trace.json')
    return dict(version='our_v056',status='CONSISTENT_SAVED_EVIDENCE_AND_CONTROLLED_PROBE',protocol_sha256=protocol,
      scope='versioned claim map plus five historical helper-only comparisons',outputs=outputs,
      canonical_batches=m['batch_count'],claim_rows=len(m['claim_rows']),frozen_checks=m['frozen_checks'],frame_files=m['frame_arrays_hashed'],
      root_links=len(m['root_links']),max_root_join=max(r['max_distance'] for r in m['root_links']),counts_by_role=m['counts_by_role'],
      historical_probe_label_changes=i['label_changes'],historical_probe_cases=i['cases'],second_attempt_calls=i['second_attempt_calls_by_variant'],
      trace_files=trace['files'],canonical_direct_suspect_calls=trace['canonical_top_level_calls'],tests=tests,
      test_evidence=Path(evidence).resolve().relative_to(ROOT).as_posix(),limits=m['limits']+i['limits']+trace['limits'])

def main(evidence):
    s=collect(evidence);t=s['tests'];m=read(ROOT/'results/campaign_map.json');i=read(ROOT/'IMPACT.json')
    counts=m['counts_by_role']['primary'];max_coord=max(c['max_coordinate_change'] for c in i['cases']);max_value=max(c['max_value_change'] for c in i['cases']);max_winding=max(c['max_winding_change'] for c in i['cases'])
    table='| Recipe | Original | Repaired | Maximum coordinate change |\n|---|---|---|---:|\n'
    for c in i['cases']:table+=f"| {c['recipe']} | {c['old_label']} | {c['new_label']} | {c['max_coordinate_change']:.3g} |\n"
    note=f'''# TEAM SHARE — our v056

The selected primary campaign families now have a checked map of {s['claim_rows']} case records across {s['canonical_batches']} canonical batches, v042–v055. All {s['frozen_checks']} frozen source/anchor checks match; {s['frame_files']} saved frame-file hashes match; {s['root_links']} paired-root joins agree within {s['max_root_join']:.3g}. The map reconciles selected recorded diagnostics, labels and counts without executing historical builders or numerical engines. Frame arrays were hashed as opaque bytes. It is an evidence index, not a new numerical acceptance certificate.

Primary records contain {counts['frame_stations']} frame stations, {counts['root_stations']} fold root stations across {sum('fold' in r['adapter'] for r in m['claim_rows'] if r['role']=='primary')} event windows, {counts['charge_stations']} charge stations (including those frame stations and fold/checkpoint measurements), {counts['gapped_stations']} gapped connection stations and {counts['open_stations']} open-side gap stations. These categories overlap and are not a count of unique physical states. The 76 v053 preparation states are explicitly marked superseded by v054; eight v042 bridge/endpoint checkpoints are corroborating records. Local extra-flat-pair folds retain their bounded-domain scope. Older first/upper/late folds have only grid 18 at the near-open station; later full-chart checks use 18/24 and local checks use 17/25. No uniform modern gate is retroactively claimed.

**A historical consumer correction matters:** `incoming_partner_v054/v023_code/gated_rerun.py`, in `pair()`, asserts `ia['success'] and ib['success']` from BM.refine. The blanket claim that no historical acceptance decision read the stale field is contradicted by this source. Presence does not prove when the script ran. `lowergap_check.py` prints the field; `run_baseline_convergence.py` reaches refinement through BM methods; `ref_v023.py` uses a different receiver, TBG. The mechanical inventory covers {s['trace_files']} files and finds no direct suspect calls in canonical top-level campaign modules, but it does not establish transitive runtime nonuse.

We ran five controlled historical charge recipes using the retained v041 BM Hamiltonian, N4 and kinetic='none', changing only BM.refine between the defective and repaired variants. Both variants preserve the historical success assertion. Observed changes: {i['label_changes']} labels; maximum coordinate change {max_coord:.3g}, value change {max_value:.3g} and winding change {max_winding:.3g}. Each returned value matches its logged recomputation.

{table}
Recorded calls: {i['calls_by_variant']}; calls reaching a second attempt: {i['second_attempt_calls_by_variant']}. A zero count means the defective second-attempt branch was not exercised. This does not clear every historical conclusion. It is not a byte-identical replay of the original runtime, nor does the older winding check provide every modern isolation/refinement guarantee. The v054 dynamically instrumented, lab_nn_full preparation replay remains the separate measured no-impact result for its 76 states. Synthetic second-attempt regression tests remain in v054/v055 and were not rerun as part of this batch's new suite.

**{t['passed']} tests passed in bound run `{t['run_id']}`**, evidence SHA256 `{t['record_sha256']}`. Publication rechecks source/test/input/runtime identity, test collection, outcomes, JUnit and saved-output reconciliation. The count is read from that run. Preserved prior repository files remain unchanged; the previous top-level README is included in provenance.

Next: trace the remaining historical baseline/Euler consumers to their recorded outputs before expanding no-impact claims; then agree the intended physical acceptance target and a named microscopic tunnelling strain law before calling model magnitudes physical. N>6 and independent reference/physical validation remain separate. This batch adds no continuous-path proof, infinite-cutoff bound, complete security clearance or physical-bilayer validation.

Start in `research/v056/` with REPORT.md, CLAIM_MAP.md, SUMMARY.json, IMPACT.json, METHOD.md and README.md. The ZIP preserves the earlier campaign, audits, partner shares and failure history.
'''
    lines=['# Campaign claim-to-evidence map','', 'Each row is a saved-record claim, not a fresh numerical verdict. Counts overlap. Exact paths, hashes, protocols, scopes and selected checks are in results/campaign_map.json.','', '| Family | Batch | Role | Per-case records | BM N4 | Ref N4 | BM N6 | Ref N6 |','|---|---|---|---:|---:|---:|---:|---:|']
    for family in dict.fromkeys(r['family'] for r in m['claim_rows']):
        rs=[r for r in m['claim_rows'] if r['family']==family];r=rs[0]
        vals=[]
        for e,n in [('bm_lab',4),('ref_lab',4),('bm_lab',6),('ref_lab',6)]:
            q=next(x for x in rs if x['engine']==e and x['N']==n)
            val=f"{q['parameter']:.9f}" if 'parameter' in q else '/'.join(q.get('labels',[])) or q.get('pair_label','w1 matched')
            vals.append(val)
        count=r['counts']['root_stations'] or r['counts']['frame_stations'] or r['counts']['gapped_stations'] or r['counts']['charge_stations']
        lines.append(f"| {family} | {r['batch']} | {r['role']} | {count} | "+' | '.join(vals)+' |')
    lines+=['','Fold entries show the declared parameter (T, ratio, A or B), not a common physical unit. BM reciprocal geometry is linear; reference geometry is exact. Both use lab_nn_full. v042 protocol/held-state linkage is contextual; later records embed protocol hashes.','',*['- '+x for x in m['limits']]]
    write(ROOT/'SUMMARY.json',s)
    (ROOT/'TEAM_SHARE_v056.md').write_text(note)
    (ROOT/'REPORT.md').write_text(note.replace('# TEAM SHARE — our v056','# Our v056: campaign map and historical helper probe',1))
    (ROOT/'CLAIM_MAP.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(status=s['status'],tests=t,claim_rows=s['claim_rows'],label_changes=s['historical_probe_label_changes']),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test-evidence',type=Path,required=True);main(p.parse_args().test_evidence)
