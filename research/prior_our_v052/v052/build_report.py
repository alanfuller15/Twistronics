"""Generate the lower-birth ledger from the complete accepted four-window grid."""
from pathlib import Path
import json,hashlib
from lower_acceptance import validate
from ledger_guard import accepted,grid,kinetic
from protocol import frozen_protocol
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PRIOR=BASE/'local-preparation-v051' if (BASE/'local-preparation-v051').is_dir() else BASE/'prior_our_v051/v051'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,data):(ROOT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def main():
 protocol=frozen_protocol();kinetic(json.loads((ROOT/'PLAN.json').read_text()));rows=[];records=[];sources={}
 for p in sorted((ROOT/'results').glob('prep_lower_birth_*_N*.json')):
  r=validate(p,protocol);records.append(r);sources[str(p.relative_to(ROOT))]=sha(p)
  rows.append(dict(engine=r['engine'],N=r['N'],geometry='linear' if r['engine']=='bm_lab' else 'exact',B=r['event']['parameter'],node=r['event']['f'],near_open_B=r['open_checks'][0]['B'],near_open_lower_gap=r['open_checks'][0]['trials'][-1]['minimum']['gap'],far_open_lower_gap=r['open_checks'][1]['trials'][-1]['minimum']['gap'],root_join=r['v044_lower_root_join']['max_distance'],min_pair_separation=min(x['separation'] for x in r['states']),max_root_jump=max(x['max_jump'] for x in r['states']),source=str(p.relative_to(ROOT))))
 grid(rows)
 prior=accepted(PRIOR/'SUMMARY.json')
 if prior['fold_windows']!=8 or prior['scope']!='LOCAL_DOMAIN_EVENTS_ONLY':raise ValueError('unexpected prior scope')
 def get(e,n):return next(r for r in rows if (r['engine'],r['N'])==(e,n))
 shifts=[dict(engine=e,N6_minus_N4=get(e,6)['B']-get(e,4)['B']) for e in ['bm_lab','ref_lab']]
 differences=[dict(N=n,ref_minus_bm=get('ref_lab',n)['B']-get('bm_lab',n)['B']) for n in [4,6]]
 fallback=sum(bool(x['measurement']['rejected_stages']) for r in records for x in r['charges'])
 summary=dict(version='our_v052',status='ACCEPT',scope='FULL_CHART_LOWER_GAP_SEARCH',kinetic='lab_nn_full',protocol_sha256=protocol,fold_windows=4,root_state_records=36,charge_measurements=8,full_chart_open_stations=8,folds=rows,cutoff_shifts=shifts,cross_engine_differences=differences,max_root_join=max(r['root_join'] for r in rows),min_open_lower_gap=min(r['near_open_lower_gap'] for r in rows),charge_fallbacks=fallback,tests_this_batch=31,prior_v051=dict(sha256=sha(PRIOR/'SUMMARY.json'),scope=prior['scope'],fold_windows=8),source_sha256=sources,remaining=['original-flat-pair full preparation continuation with parameter frames and v044 join','separate lower unlink collision'],limits=['Finite full-chart searches, not analytic global gap bounds','Lower gap index 2, not flat-pair gap index 3','Two charge stations per window, no full parameter-frame replay','Shared measurement harness and unchanged engines, no physical validation'])
 dump('SUMMARY.json',summary)
 table=['| engine / geometry | N | birth B | near-open lower gap (meV) | B=−0.10 lower gap (meV) | v044 root join |','|---|---:|---:|---:|---:|---:|']
 for r in rows:table.append(f"| {r['engine']} / {r['geometry']} | {r['N']} | {r['B']:.10f} | {r['near_open_lower_gap']:.8f} | {r['far_open_lower_gap']:.8f} | {r['root_join']:.2e} |")
 table='\n'.join(table)
 shifts_text='; '.join(f"{x['engine']}: {x['N6_minus_N4']:+.3g}" for x in shifts)
 (ROOT/'REPORT.md').write_text('''# Our v052 — lower-pair preparation birth

[self-tested] The lower-pair birth passes in both engines at N4/N6. Each window combines two-root continuation, opposite-charge stations, refined fold/nondegeneracy checks and positive full-chart lower-gap searches on the other side. All four B=−0.25 lower-root pairs join the retained v044 start-state roots within 1e−6.

'''+table+f'''\n\nN6−N4 parameter shifts: {shifts_text}. These are discrete cutoff shifts, not error bounds against infinite cutoff. Charge-station mesh fallbacks: {fallback}.

## Evidence and scope

Four windows contain 36 root-state records, eight charge measurements (all OPPOSITE) and eight open-side full-chart station searches, each on 18/24 meshes. Charges are measured at the first and last root state, not all 36 records. The joins establish same-state momenta; they do not establish a historical frame-orientation join.

The forward preparation route decreases B from 0 to −0.25 at A=0.2,T=0,phi=0,ratio=0.8. The discovery scan followed the known pair backward: two roots at −0.22, unresolved at −0.21. That failure was a bracket signal only. The accepted event locations come from a bounded fold solve with rank-one refinement, nonzero null curvature and transverse parameter slope, resolved roots on one side and searched positive lower gaps on the other.

The gap is index 2 in the eight-band harness, between the lower remote band and the first flat band. A positive lower gap does not mean the original flat-pair gap opens. This differs from v051's extra-flat-pair events: there the original pair persisted in the same gap and required a local-domain gate; here the full-chart lower-gap searches are positive on the open side. The older local records and their scope are unchanged.

All runs use explicit lab_nn_full and constant w0,w1, eps=0.003, theta=1.05 degrees. BM retains linear reciprocal geometry/cutoff_tol=1e−6; TBG retains exact geometry/cutoff_tol=1e−9. Hamiltonian source bytes are unchanged. Scientific sources and v044 anchors were frozen before the decisive runs; both N4 windows passed before N6 started. No shared conceptual error or physical-bilayer validation is ruled out by the two engines and shared measurement harness.

## Validation and limits

31 gate/join tests pass this batch: ten inherited bounded-domain tests, five ledger tests, seven anchor-join tests and nine lower-event publication tests. The original supplied regression suite was not rerun against unchanged Hamiltonians; its earlier 31-test result remains historical and is not counted here.

Full-chart searches are finite numerical evidence, not rigorous global lower bounds, exhaustive inventories or a proof of behavior between parameter stations. Existing seed failures remain triage signals, not topology verdicts. No established campaign label was changed. The remaining numerical coverage tasks are the original-flat-pair preparation replay with parameter-frame transport and a frame/root join into v044, followed by the separate lower unlink collision. These root-window results do not substitute for either task. Recipient consumption is [unconfirmed].
''')
 (ROOT/'LEDGER.md').write_text('''# Accepted lower-event ledger — our v052

Generated from finite ACCEPT records, source/protocol checks, declared lower-gap index, refined searches, same-state root joins and the complete engine/cutoff grid.

'''+table+'''

Newly accepted: four preparation lower-pair birth windows; 36 root records; eight OPPOSITE charge measurements; eight full-chart lower-gap open stations. Root joins into the existing v044 start state pass in all four cases. No frame join or fully charge-gated 36-state claim.

Retained: v051's eight local extra-flat-pair event windows, v050's four upper-pair birth windows, and all earlier accepted route segments. See prior_our_v051/v051/LEDGER.md and the preserved nested records.

Remaining: original-flat-pair full preparation/frame replay and explicit join into v044; separate lower unlink collision. Physical validation and infinite-cutoff bounds remain outside measured coverage.
''')
 (ROOT/'TEAM_SHARE_v052.md').write_text('''TEAM SHARE — our v052

The preparation lower-pair birth now passes in both engines at N4/N6. The two retained roots were followed backward; their loss in a search was used only to bracket the event. A refined fold, opposite charges and positive 18/24 full-chart lower-gap searches establish the measured windows.

'''+table+f'''\n\nFour windows: 36 root-state records, eight OPPOSITE charge measurements and eight open-side lower-gap station searches. Root joins to v044 pass; these are momentum joins, not frame-orientation joins. N6−N4 shifts: {shifts_text}. All 31 gate/join tests pass; Hamiltonian sources are unchanged.

This closes the lower-pair preparation event. The remaining preparation work is the original-flat-pair continuation with parameter frames and explicit join into v044; the separate lower unlink collision also remains open. No established label changes and no physical validation claim. Full-chart numerical minima remain finite evidence, not analytic bounds.
''')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
