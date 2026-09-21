"""Publish the bounded event only with matching test and measurement evidence."""
import argparse,json
from pathlib import Path
from checkpoints import digest,save_json
from protocol import frozen_protocol
from unlink_acceptance import validate
from test_evidence import read_evidence
ROOT=Path(__file__).resolve().parent

def collect(evidence):
    tests=read_evidence(ROOT,evidence)
    protocol=frozen_protocol();cases=[]
    for engine in ['bm_lab','ref_lab']:
        for N in [4,6]:
            path=ROOT/'results'/f'lower_unlink_{engine}_N{N}.json';r=validate(path,protocol)
            cases.append(dict(engine=engine,N=N,geometry=r['geometry'],parameter=r['event']['parameter'],momentum=r['event']['f'],root_states=len(r['states']),charge_stations=len(r['charges']),label='OPPOSITE',just_open_gap=r['open_checks'][0]['trials'][-1]['minimum']['gap'],endpoint_lower_gap=r['open_checks'][1]['trials'][-1]['minimum']['gap'],minimum_boundary_gap=min(b['minimum'] for q in r['open_checks'] for b in q['boundary']),anchor_join=r['v044_lower_root_join']['max_distance'],minimum_sampled_segment_offset=min(g['offset'] for s in r['states'] for g in s['lower_to_flat_segment']),loop_fallbacks=sum(len(x['measurement']['rejected_stages']) for x in r['charges']),seconds=r['seconds'],record=str(path.relative_to(ROOT)),record_sha256=digest(path)))
    return dict(version='our_v055',status='ACCEPT',scope='lower unlink fold with sampled two-root continuation and finite full-chart lower-gap searches',kinetic='lab_nn_full',protocol_sha256=protocol,cases=cases,root_states=sum(c['root_states'] for c in cases),charge_stations=sum(c['charge_stations'] for c in cases),open_stations=2*len(cases),tests=tests,test_evidence=str(Path(evidence).resolve().relative_to(ROOT)),partner_archive_sha256=digest(ROOT/'provenance/incoming_partner_v054.zip'),limits=['Finite numerical searches are not rigorous global gap bounds or continuous-interval proofs.','Only the first and last root stations have loop charges; root stations are not all charge stations.','The two engines share a measurement harness; no independent conceptual or physical validation.','N4/N6 agreement does not establish infinite-cutoff accuracy.','Historical legacy-helper consumers outside v054 preparation remain impact-unverified.'])

def main(evidence):
    s=collect(evidence);t=s['tests']
    table='| Engine | N | Fold T | Gap at fold−0.001 (meV) | Gap at T=−0.4 (meV) |\n|---|---:|---:|---:|---:|\n'
    for c in s['cases']:table+=f"| {c['engine']} | {c['N']} | {c['parameter']:.10f} | {c['just_open_gap']:.8f} | {c['endpoint_lower_gap']:.8f} |\n"
    note=f'''# TEAM SHARE — our v055: lower unlink fold

Partner v054 is preserved and reconciled with our published repair batch. BM.refine is byte-identical in both trees; the reference engine and gate also match. The partner supplied no new numerical result. Their 33-test statement remains a supplied historical claim in this batch. Their Euler/braid opt-in is policy only in the supplied source, and the copied v048 ledger/COVERAGE are historical snapshots; our active runtime guards and versioned records remain authoritative for this batch. See RECONCILIATION.md.

The lower unlink collision now passes the declared event gate in both engines at N4/N6, starting with both N4 cases. A=0.2, B=−0.4, phi=0, w0/w1=0.8, kinetic=lab_nn_full; constant tunnelling amplitudes. BM uses linear reciprocal geometry; the reference uses exact reciprocal geometry.

{table}
Each case has nine two-seed root stations joined to the retained v044 step_028 lower-root inventory, two OPPOSITE charge stations with mesh/radius agreement, derivative-refined fold location, nonzero null curvature and transverse parameter slope, and two positive full-chart searched lower gaps with separate edge refinement. Aggregate: {s['root_states']} root states, {s['charge_stations']} charge stations, {s['open_stations']} open-side stations. No failed search is counted as evidence of annihilation. This concerns the lower remote/flat1 gap, not a fully gapped four-band system.

All sampled lower-node offsets from the flat pair's straight segment are positive. That supports the sampled no-crossing observation; it does not prove absence of an intervening crossing. No absolute charge is transported through the fold.

**{t['passed']} tests passed in bound run `{t['run_id']}`**, evidence SHA256 `{t['record_sha256']}`. The count comes from collection, execution and JUnit, bound to source/tests/inputs/runtime. This is recorded execution, not a promise that regenerating a report reruns tests.

The remaining work changes from locating this candidate to reviewing the complete campaign's claim/evidence links and historical legacy-helper consumers. No continuous-path proof, infinite-cutoff bound, microscopic tunnelling strain law, comprehensive security clearance or physical-bilayer validation is claimed. Frozen v053/v054 evidence is unchanged.

Start in research/v055 with REPORT.md, SUMMARY.json, METHOD.md, PLAN.json and the four raw results; the complete incoming partner ZIP and reconciliation are included.
'''
    save_json(ROOT/'SUMMARY.json',s)
    (ROOT/'REPORT.md').write_text(note.replace('# TEAM SHARE — our v055:', '# Our v055:',1))
    (ROOT/'TEAM_SHARE_v055.md').write_text(note)
    (ROOT/'LEDGER.md').write_text('# v055 lower unlink ledger\n\n'+table+'\nAccepted scope: sampled event gate. See SUMMARY.json for exact source identities and limits. Earlier records remain in their original versioned directories.\n')
    print(json.dumps(s,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test-evidence',type=Path,required=True);main(p.parse_args().test_evidence)
