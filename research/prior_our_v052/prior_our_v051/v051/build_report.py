"""Build scoped coverage only after all eight local windows pass publication gates."""
import json,hashlib
from pathlib import Path
from local_acceptance import validate
from ledger_guard import accepted,grid,kinetic
from protocol import frozen_protocol
from local_cases import CASES
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PRIOR=BASE/'preparation-v050' if (BASE/'preparation-v050').is_dir() else BASE/'prior_our_v050/v050'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,data): (ROOT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def main():
 protocol=frozen_protocol();plan=json.loads((ROOT/'PLAN.json').read_text());kinetic(plan)
 records=[];sources={}
 for p in sorted((ROOT/'results').glob('*_N*.json')):
  r=validate(p,protocol);records.append(r);sources[str(p.relative_to(ROOT))]=sha(p)
 grid(records,cases=list(CASES))
 prior=accepted(PRIOR/'SUMMARY.json');require_prior=(prior['fold_windows']==4 and prior['root_states']==36 and prior['charge_stations']==8)
 if not require_prior:raise ValueError('unexpected prior upper-birth scope')
 rows=[]
 for r in records:
  stations=r['states']+r['open_checks']
  rows.append(dict(case=r['case'],engine=r['engine'],N=r['N'],parameter_name=CASES[r['case']]['key'],parameter=r['event']['parameter'],node=r['event']['f'],near_open_gap=r['open_checks'][1]['local_minimum'],far_open_gap=r['open_checks'][2]['local_minimum'],min_boundary_gap=min(x['boundary']['minimum'] for x in stations),min_original_distance=min(min(x['original_pair']['outside_distances']) for x in stations),max_original_residual=max(n['gap'] for x in stations for n in x['original_pair']['nodes']),root_state_records=len(r['states']),charge_measurements=len(r['charges']),shared_station_join=r.get('shared_station_join'),source=f"results/{r['case']}_{r['engine']}_N{r['N']}.json"))
 def get(case,engine,N):return next(r for r in rows if (r['case'],r['engine'],r['N'])==(case,engine,N))
 shifts=[dict(case=c,engine=e,N6_minus_N4=get(c,e,6)['parameter']-get(c,e,4)['parameter']) for c in CASES for e in ['bm_lab','ref_lab']]
 differences=[dict(case=c,N=n,ref_minus_bm=get(c,'ref_lab',n)['parameter']-get(c,'bm_lab',n)['parameter']) for c in CASES for n in [4,6]]
 stations=[x for r in records for x in r['states']+r['open_checks']]
 maxjoin=max(v['max_distance'] for r in rows if r['shared_station_join'] for v in r['shared_station_join'].values())
 fallbacks=sum(bool(x['measurement']['rejected_stages']) for r in records for x in r['charges'])
 summary=dict(version='our_v051',status='ACCEPT',scope='LOCAL_DOMAIN_EVENTS_ONLY',kinetic='lab_nn_full',protocol_sha256=protocol,box=plan['box'],fold_windows=8,root_state_records=72,charge_measurements=16,boundary_station_evaluations=len(stations),original_pair_station_evaluations=len(stations),local_open_station_evaluations=16,shared_state_duplicate_records=4,folds=rows,cutoff_shifts=shifts,cross_engine_differences=differences,min_boundary_gap=min(r['min_boundary_gap'] for r in rows),min_local_open_gap=min(min(r['near_open_gap'],r['far_open_gap']) for r in rows),min_original_distance=min(r['min_original_distance'] for r in rows),max_original_residual=max(r['max_original_residual'] for r in rows),max_shared_station_join=maxjoin,charge_fallbacks=fallbacks,new_gate_tests=24,prior_v050=dict(sha256=sha(PRIOR/'SUMMARY.json'),fold_windows=4,scope='upper-pair birth'),source_sha256=sources,remaining=['lower-pair preparation birth','original-flat-pair full preparation continuation and frame/root join into v044','separate lower unlink collision'],limits=['Finite sampled local minima/boundaries, not analytic certificates','Original nodes outside domain; no global gap claim','Charges at two stations per window only; no parameter-carried absolute charge','Unchanged engines and shared measurement harness; no physical validation'])
 dump('SUMMARY.json',summary)
 table=['| event | engine / geometry | N | fold parameter | near-open local gap (meV) |','|---|---|---:|---:|---:|']
 for r in rows:table.append(f"| {'birth A' if r['case']=='extra_flat_birth' else 'annihilation B'} | {r['engine']} / {'linear' if r['engine']=='bm_lab' else 'exact'} | {r['N']} | {r['parameter']:.10f} | {r['near_open_gap']:.8f} |")
 table='\n'.join(table)
 stats=f"Across the accepted windows, the smallest located boundary gap is {summary['min_boundary_gap']:.8f} meV, the smallest local open-side gap is {summary['min_local_open_gap']:.8f} meV, and the nearest original root is {summary['min_original_distance']:.8f} fractional-coordinate units outside the rectangle. The largest original-root residual is {summary['max_original_residual']:.3g} meV. Shared-state root joins are at most {maxjoin:.3g}. There were {fallbacks} charge-station mesh fallbacks."
 (ROOT/'REPORT.md').write_text('''# Our v051 — extra flat-pair preparation events

[self-tested] Both extra flat-pair events pass the new local-domain gate in both engines at N4/N6. The birth and annihilation windows join at A=0.2, B=0. The original flat pair remains separately resolved outside the local rectangle. These results close two preparation events, not the whole preparation route.

'''+table+'\n\n'+stats+'''

## What was measured

Eight accepted windows contain 72 root-state records, 16 mesh/radius charge measurements (all OPPOSITE), 96 boundary/original-pair station evaluations and 16 local open-side station evaluations. Each window has nine distinct two-root states, rank-one fold refinement, curvature/parameter-slope checks, two charge stations, and two bounded local open-side searches. The common A=0.2,B=0 point is measured in both windows for each engine/cutoff: counts include four repeated common-state records and charge measurements. They are not independent additional parameter coverage.

The local rectangle is f1=[0.42,0.63], f2=[0.52,0.63]. Boundaries use 24/48 edge grids and bounded minima; local interiors use closed 17/25 grids with bounded gradient refinements and explicit corner/fold seeds. Original-root controls at all 12 stations per window prevent a local opening being promoted to a global flat gap. Charge is checked at the first and last root state, not all 72 records. No parameter-carried absolute orientation is claimed.

Both engines explicitly use lab_nn_full and constant w0,w1. BM retains linear reciprocal geometry with cutoff_tol=1e−6; TBG uses exact reciprocal geometry with cutoff_tol=1e−9. Their source bytes are unchanged from v050. The two engines share the new measurement harness. Pilot locations were exploratory; source and protocol hashes were frozen before the accepted N4/N6 measurements. Both N4 engines passed before either N6 worker started.

## What changed in the gate

Using the old full-chart positive-flat-gap requirement would be invalid here: the original flat nodes remain on the open side of each extra-pair event. The new gate requires a bounded local minimum, a positive sampled/refined boundary, roots away from the boundary, and explicit original roots outside it. It is a separate, named local-event claim. The older global-gap gates and earlier accepted records are unchanged.

Twenty-four tests pass: ten local-domain synthetic/failure tests, nine publication-record acceptance/mutation tests and five inherited ledger tests. The Hamiltonians were not changed, so the 31 supplied regression tests from v050 were not repeated; that prior result is retained as historical evidence, not counted as a new test run. The new gate rejects boundary/interior zeros, optimizers escaping the domain, nonfinite values, missing records, changed scope, wrong domains and original roots entering the local rectangle.

## Limits and next work

Boundary positivity and open-side minima are finite numerical searches, not analytic interval certificates. Narrow unseeded minima or events between parameter samples cannot be ruled out. These are local fold windows and sampled root continuations, not a complete global node inventory, a full preparation frame replay or an Euler-class calculation. No established campaign topology label was revised; the new extra-pair charges are opposite at the measured stations.

Next: follow both lower-gap roots backward to locate their preparation birth, then complete the original-flat-pair preparation continuation with the frame/root join into v044, and measure the separate lower unlink collision. N4/N6 differences are sampled cutoff shifts, not infinite-cutoff error bounds. Physical-bilayer validation remains outside the campaign. Recipient consumption is [unconfirmed].
''')
 (ROOT/'LEDGER.md').write_text('''# Accepted local-event ledger — our v051

Generated from finite ACCEPT records after source/protocol, scope, full engine/cutoff grid, local-domain and control checks.

'''+table+'''

New coverage: extra flat-pair birth and annihilation, both engines at N4/N6, shared roots joined at A=0.2,B=0. 72 root-state records, 16 charge measurements, 96 boundary/control station evaluations, including shared-state repeats. All charged extra-pair stations are OPPOSITE.

Retained: v050 upper-pair preparation birth (four windows); v048 late events and sampled gapped joins; earlier accepted legs. See prior_our_v050/v050/LEDGER.md and its nested prior records. Local opening does not mean global flat gap.

Open: lower-pair preparation birth; original-flat-pair full preparation continuation and frame/root join; separate lower unlink collision. No global inventory, whole-route completion, infinite-cutoff convergence or physical validation claim.
''')
 (ROOT/'TEAM_SHARE_v051.md').write_text('''TEAM SHARE — our v051

The two extra flat-pair preparation events now pass in both engines at N4/N6 under a separately frozen local-domain gate. The original flat pair stays resolved outside the rectangle, so the claim is a local pair birth/death, never a global flat gap. Both windows join at A=0.2,B=0.

'''+table+'\n\n'+stats+'''

Eight windows: 72 root-state records, 16 charge measurements, all OPPOSITE; 96 boundary/original-pair station evaluations. Counts include the shared state repeated between windows. Rank-one, curvature, parameter slope, boundary and local open-side checks pass. Twenty-four new/inherited gate tests pass; Hamiltonian sources are unchanged. No established label changes, no physical validation claim.

Next: lower-pair birth by backward two-seed continuation, then original-flat-pair preparation with explicit frame/root join into v044, then the separate lower unlink event. The extra-pair events no longer need an exploratory location pass.
''')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
