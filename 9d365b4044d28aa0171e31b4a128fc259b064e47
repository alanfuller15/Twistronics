"""Publish a bounded replay with matching test, source and runtime evidence."""
import argparse,itertools,json
from pathlib import Path
import attribution,probe_evidence
from evidence import read,sha,require,write
from protocol import frozen_protocol
from test_evidence import read_evidence
ROOT=Path(__file__).resolve().parent

def historical_comparison(c,target,tol):
    v=c['variants'][1];nodes=[n[1] for n in v['resolved_nodes']]
    delta=min(max(abs(x-y) for a,b in zip(nodes,p) for x,y in zip(a,b)) for p in itertools.permutations(target['nodes']))
    differences=dict(nodes=delta,remote_gap=abs(v['remote_gap']-target['remote']),bandwidth=abs(v['bandwidth']-target['bandwidth']),endpoint_lower=abs(v['endpoint_gap']-target['endpoint_lower']))
    agrees=delta<=tol['printed_baseline_node'] and differences['remote_gap']<=tol['printed_baseline_gap'] and differences['bandwidth']<=tol['printed_baseline_gap'] and differences['endpoint_lower']<=tol['printed_endpoint_gap'] and abs(c['euler']['gated'][0]['euler'])==target['euler_abs']
    return dict(N=c['N'],agrees_with_rounded_targets=agrees,differences=differences,scope='rounded log agreement, not original execution attribution')

def collect(evidence):
    tests=read_evidence(ROOT,evidence);protocol=frozen_protocol()
    m=read(ROOT/'IMPACT.json');a=read(ROOT/'results/attribution.json')
    require(m==probe_evidence.build(),'stale numerical reconciliation')
    require(a==attribution.build(),'stale source-to-log attribution')
    targets=read(ROOT/'HISTORICAL_TARGETS.json');partner=ROOT.parent/'incoming_partner_v054'
    for name,h in targets['sources'].items():require(sha(partner/name)==h,'historical target source changed')
    comparisons=[historical_comparison(c,targets['cases'][str(c['N'])],read(ROOT/'NUMERICAL_PLAN.json')['comparison_tolerances']) for c in m['cases']]
    return dict(version='our_v057',status='BOUNDED_CONTROLLED_REPLAY_COMPLETE',protocol_sha256=protocol,numerical_plan_sha256=m['numerical_plan_sha256'],kinetic='none',scope='historical baseline and lower|flat1 endpoint recipes at N4/N6; baseline Euler in two gated meshes',
      attribution_rows=len(a['rows']),refinement_calls=m['refinement_calls'],second_attempt_calls=m['second_attempt_calls'],changed_comparisons=m['changed_comparisons'],cases=m['cases'],historical_comparisons=comparisons,
      retained_v035_N4_gap_difference=abs(m['cases'][0]['variants'][1]['endpoint_gap']-a['retained_v035_endpoint']['lower_gap']),tests=tests,test_evidence=Path(evidence).resolve().relative_to(ROOT).as_posix(),
      input_sha256={'IMPACT.json':sha(ROOT/'IMPACT.json'),'results/attribution.json':sha(ROOT/'results/attribution.json'),'HISTORICAL_TARGETS.json':sha(ROOT/'HISTORICAL_TARGETS.json')},limits=m['limits']+a['limits'])

def main(evidence):
    s=collect(evidence);t=s['tests'];a=read(ROOT/'results/attribution.json')
    table='| N | Baseline remote gap (meV) | Endpoint lower gap (meV) | Second attempts per variant | Gated baseline e2, both meshes |\n|---:|---:|---:|---:|---:|\n'
    for c in s['cases']:
        v=c['variants'][1];table+=f"| {c['N']} | {v['remote_gap']:.12f} | {v['endpoint_gap']:.12f} | {v['second_attempt_calls']} | {c['euler']['gated'][0]['euler']} |\n"
    failures=sum(not c['agrees_with_rounded_targets'] for c in s['historical_comparisons'])
    max_change=max(v for c in s['cases'] for v in c['differences'].values())
    all_attempts_succeeded=all(q['success'] for c in s['cases'] for v in c['variants'] for r in v['second_attempt_records'] for q in r['attempts'])
    note=f'''# TEAM SHARE — our v057

The historical impact check now reaches the real wrapped re-refinement branch that v056 did not exercise. We repeated the retained baseline search and the endpoint lower-remote|flat1 search at N4 and N6, changing only BM.refine between the defective and repaired variants. The static Hamiltonian bytes match, and both variants share the Hamiltonian-building code and parameters. This is the historical kinetic='none' model, with constant tunnelling amplitudes; the current lab_nn_full campaign remains a separately recorded model.

{table}
Across both variants there are **{s['refinement_calls']} recorded refinement calls, including {s['second_attempt_calls']} second-attempt calls**. The same selected seed/cutoff cases are repeated under each helper, so repeated helper variants are not independent physical events. Changed comparisons above the frozen tolerances: **{s['changed_comparisons']}**; maximum root-coordinate/gap/bandwidth difference: **{max_change:.3g}**. All observed first/second attempts in the wrapped cases succeeded: **{all_attempts_succeeded}**. The stale metadata therefore happens to describe the final outcome correctly in these cases. This closes the scoped branch-exercised comparison; it does not establish that a failed second attempt never affected another historical result. Synthetic tests separately force differing first/final outcomes and confirm the repaired helper follows the final attempt.

The N4 endpoint search starts at a grid seed on f1=0, first locates a minimum outside the cell, then re-refines its canonical representative. It reproduces the v035 correction from the roughly 22.68 meV first minimum to 22.537986 meV. Difference from the retained machine-readable v035 N4 lower-gap result: {s['retained_v035_N4_gap_difference']:.3g} meV. Rounded historical target disagreements across the two cutoffs: {failures}. This is numerical agreement with identified sources, not proof of their original execution history.

The baseline Euler result was computed separately: the original exploratory Wilson routine and the retained numerical gate at 24×40 and 32×56 meshes. Both cutoffs pass finite-sample reality, Hermiticity, eigen-residual, external-isolation, link-overlap, sewing, orientability and phase-resolution checks; both gated meshes return the values in the table. No BM.refine call occurs in the Euler computation. The global sign depends on orientation convention; |e2| is the meaningful comparison here. Baseline local-minimum candidate counts (N4/N6, repaired variant): {[c['variants'][1]['node_candidates'] for c in s['cases']]}; only two per cutoff have root residual below 1e-6 meV. Positive-gap candidates are not counted as nodes.

The **{s['attribution_rows']}-row source-to-log ledger** distinguishes the remaining consumers. `transfer.py` and `flat_e2.py` define their own Euler routines, so repairing `euler.py` alone does not gate those routines. `transfer.py` also has a local frame helper that drops the imaginary part without a guard. However, v029 explicitly withholds an Euler-class conclusion because isolation fails, and v032–v033 explicitly correct the earlier e2=0 prediction to undefined for the nonorientable pair. Those recorded refusals and corrections are preserved. The broader scalar/mass/angle sweeps and braid detours remain impact-unverified.

**{t['passed']} tests passed in bound run `{t['run_id']}`**, evidence SHA256 `{t['record_sha256']}`. The count is read from actual collection, execution and JUnit, bound to source/tests/inputs/runtime. The two numerical workers record matching before/after runtime identities and run under the separately frozen numerical plan. All prior tracked files are preserved; the previous top-level README is retained in provenance.

Limits: retained snapshots are not proven to be the precise source used for early log entries. v034 declares a different runtime; retained v035 endpoint direct package versions match this session but lack complete native-build provenance. Finite searches and two meshes do not prove global isolation, continuous-path completeness, infinite-cutoff accuracy or physical-bilayer validity. No comprehensive security clearance or whole-history no-impact claim is made.

Next: a bounded N>6 endpoint-gap comparison under the modern declared lab_nn_full model, with explicit boundary seeds and reference-engine comparison. Physical magnitude claims still require the inventor's intended acceptance target and a named microscopic tunnelling strain law. Preserve the remaining historical attribution gaps instead of treating repeated agreement as universal clearance.

Start in `research/v057/` with REPORT.md, ATTRIBUTION.md, SUMMARY.json, IMPACT.json, NUMERICAL_PLAN.json and README.md. The ZIP includes prior campaign evidence, audits and partner shares.
'''
    ledger=['# Historical consumer attribution','','Source/log association is contextual. Code presence is not execution evidence; this is a bounded review. Full paths, hashes and snapshot copies are in results/attribution.json.','','| ID | Consumer | Logged claim | Source finding | Disposition |','|---|---|---|---|---|']
    for row in a['rows']:
        vals=[row['id'],Path(row['source']).name,row['log_claim'],row['consumer'],row['disposition']]
        ledger.append('| '+' | '.join(x.replace('|','\\|') for x in vals)+' |')
    ledger+=['','The retained v035 endpoint JSON and five copied-engine hashes match their provenance records. Matching hashes do not prove authenticity or timing.','',*['- '+x for x in a['limits']]]
    write(ROOT/'SUMMARY.json',s)
    (ROOT/'TEAM_SHARE_v057.md').write_text(note)
    (ROOT/'REPORT.md').write_text(note.replace('# TEAM SHARE — our v057','# Our v057: historical consumers and branch-exercised replay',1))
    (ROOT/'ATTRIBUTION.md').write_text('\n'.join(ledger)+'\n')
    print(json.dumps(dict(status=s['status'],tests=t,second_attempt_calls=s['second_attempt_calls'],changed_comparisons=s['changed_comparisons']),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test-evidence',type=Path,required=True);main(p.parse_args().test_evidence)
