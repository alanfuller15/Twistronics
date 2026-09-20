"""Generate current summary/ledger only from finite accepted source records."""
import json,hashlib
from pathlib import Path
from ledger_guard import accepted,grid,kinetic
from protocol import frozen_protocol
from anchor_quality import classify_anchor
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PRIOR=BASE/'closing-v048' if (BASE/'closing-v048').is_dir() else BASE/'prior_our_v048/v048'
INCOMING=BASE/'team-v049' if (BASE/'team-v049').is_dir() else BASE/'incoming_v049'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,obj): (ROOT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def main():
 protocol=frozen_protocol();plan=json.loads((ROOT/'PLAN.json').read_text());kinetic(plan)
 rows=[];sources={}
 for path in sorted((ROOT/'results').glob('prep_upper_birth_*_refined.json')):
  r=accepted(path)
  if r['protocol_sha256']!=protocol or r['case']!='prep_upper_birth':raise ValueError('wrong protocol/case')
  if len(r['states'])!=9 or len(r['charges'])!=2:raise ValueError('incomplete event window')
  if any(z['measurement']['label']!='OPPOSITE' for z in r['charges']):raise ValueError('unexpected charge')
  if len(r['gapped_checks'])!=2 or any([z['grid'] for z in a['trials']]!=[18,24] for a in r['gapped_checks']):raise ValueError('missing open-side mesh check')
  if any(z['minimum']['gap']<=1e-5 for a in r['gapped_checks'] for z in a['trials']):raise ValueError('gap gate')
  rows.append(dict(engine=r['engine'],N=r['N'],case=r['case'],A=r['event']['parameter'],node=r['event']['f'],root_states=len(r['states']),charge_stations=len(r['charges']),near_open_gap=r['gapped_checks'][0]['trials'][-1]['minimum']['gap'],far_open_gap=r['gapped_checks'][1]['trials'][-1]['minimum']['gap'],source=str(path.relative_to(ROOT))))
  sources[str(path.relative_to(ROOT))]=sha(path)
 grid(rows)
 probe=accepted(ROOT/'provenance/ratio_1054.json');sources['provenance/ratio_1054.json']=sha(ROOT/'provenance/ratio_1054.json')
 prior=accepted(PRIOR/'SUMMARY.json');kinetic(json.loads((PRIOR/'PLAN.json').read_text()))
 if prior['fold_windows']!=8 or prior['gapped_states']!=32:raise ValueError('prior scope mismatch')
 anchors=json.loads((INCOMING/'v023_code/anchors_final_N4.json').read_text())
 quality=[dict(window=r['window'],ratio=r['ratio'],A=r['A'],classification=classify_anchor(r),printed_label=r['label']) for r in anchors]
 dump('provenance/anchor_quality.json',quality)
 summary=dict(version='v050',status='ACCEPT',kinetic='lab_nn_full',scope='Preparation upper-pair birth only',fold_windows=4,root_states=36,charge_stations=8,folds=rows,late_missing_partner=probe,prior_our_v048=dict(status=prior['status'],fold_windows=8,gapped_states=32,sha256=sha(PRIOR/'SUMMARY.json')),protocol_sha256=protocol,source_sha256=sources,tests=dict(supplied=31,report_guards=14),limits=['Remaining preparation not replayed','Separate lower unlink collision unmeasured','Finite parameter samples and momentum searches','Shared measurement harness; not physical validation'])
 dump('SUMMARY.json',summary)
 table=['| engine / geometry | N | birth A | near-open gap (meV) | A=0.12 gap (meV) |','|---|---:|---:|---:|---:|']
 for r in rows:table.append(f"| {r['engine']} / {'linear' if r['engine']=='bm_lab' else 'exact'} | {r['N']} | {r['A']:.10f} | {r['near_open_gap']:.8f} | {r['far_open_gap']:.8f} |")
 text='\n'.join(table)
 (ROOT/'REPORT.md').write_text('''# v050 — preparation upper-pair birth and v049 reconciliation

[self-tested] Four upper-pair birth windows pass under lab_nn_full, constant w0,w1, B=T=0, phi=0, ratio=0.8, eps=0.003 and theta=1.05 degrees. This closes one preparation event, not the preparation route.

'''+text+'''

Each window includes nine distinct-root continuation states from A=0.14 toward the fold, charge measurements at two stations (start and fold+0.001), rank-one Jacobian refinement, nonzero null curvature and transverse parameter slope, and positive opposite-side gap searches at fold−0.001 and A=0.12. Both opposite-side searches use 18/24 grids with boundary seeds and bounded refinements. Total: 36 root states and eight charge stations, not 36 fully charge-gated states. The code and input hashes were frozen before the decisive runs. N4 passed in both engines before N6 began.

BM retains linear reciprocal geometry and cutoff_tol=1e-6; TBG retains exact inverse deformation and cutoff_tol=1e-9. These are the declared campaign variants, not identical matrices. Their agreement tests implementation sensitivity with a shared measurement harness, not conceptual independence.

## Reconciliation with v049

The partner's v048 disposition and our v048 measured batch are different records. Both are preserved. Our already accepted v048 supplies eight late fold windows and 32 sampled gapped states, so those late events were not rerun here. The exact N4 late birth is ratio 1.0529719221827458 near (0.67751830,0.90903862), refining v049's extrapolated 1.0534. The exact N4 final annihilation is A=−0.31777996539472003, consistent with the rounded −0.3178 anchor estimate.

At ratio 1.054, the new two-seed probe finds the missing partner at (0.67695168,0.90486606) alongside (0.67838909,0.91363691). Separation is 0.0088878553; exact BM/TBG agreement is better than 3.6e−15. This resolves the undercount. It does not isolate which detail of the old eight-start search caused the miss and adds no new charge claim.

The saved A=−0.31 row has residual gaps 1.26189219 meV in both engines. It is not the zero-gap duplicate-root signature described in v049 §2. The ratio=1.06 row really does contain duplicate zero-gap roots. The new anchor classifier keeps these cases separate and does not promote either to an event verdict.

v049's finite-twist geometric computation is consistent with the previously measured O(eps*theta) term. Its total radius shift also contains O(eps^2); exact doubling should be tested on the isolated first-order contribution, not on the full shift. No new microscopic tunnelling law or physical magnitude is established.

## Validation and limits

31 supplied tests pass; 14 reporting tests pass (six anchor-quality cases, five inherited ledger guards and three endpoint fault-injection cases). Source review covers the three changed Python files and three new Python scripts, their relevant outputs, and the new harness changes. It is an incremental review, not a reread or CVE recertification of the entire project. File inventory covers all 143 incoming files.

The positive-gap searches and nine parameter stations are finite numerical evidence, not exhaustive momentum or parameter-interval proofs. No independent physical-bilayer validation has been performed. The optional endpoint patch persists failed-start logs before raising and rejects nonfinite optimizer coordinates. It is tested with injected failed, invalid and successful outcomes; it does not replace the accepted numerical search harness.

The remaining preparation route, extra flat-pair birth/annihilation, lower-pair birth and separate lower unlink collision remain open. Recipient consumption is [unconfirmed].
''')
 (ROOT/'LEDGER.md').write_text('''# Accepted batch ledger — v050

Generated from finite ACCEPT records after protocol and engine/cutoff-grid checks. The original partner ledger is preserved unchanged under incoming_v049/.

'''+text+'''

- Newly accepted: preparation upper-pair birth, four windows, 36 root states, eight charge stations.
- Retained from our v048: eight late fold windows and 32 sampled gapped states connecting the already measured late segments. See prior_our_v048/v048/LEDGER.md and its source records.
- Provisional only: v049's fixed-parameter anchors. Their duplicate/nonzero-residual rows are classified in provenance/anchor_quality.json and are never promoted to accepted pairs.
- Still open: original-flat-pair preparation continuation and joins; extra flat-pair local events; lower-pair birth; separate lower unlink collision.
- No whole-campaign, global convergence or physical-bilayer validation claim.
''')
 (ROOT/'TEAM_SHARE_v050.md').write_text('''TEAM SHARE — v050

Your v049 anchors and our v048 late-event replay crossed in transit. Both records are retained: our v048 already closes the eight late fold windows and 32 sampled gapped states at N4/N6. The declared route beyond the v044 start remains as reported there; preparation and the separate lower unlink event are still distinct open items.

This batch advances preparation: the upper-pair birth passes in both engines at N4/N6, with 36 root-continuation states and eight mesh/radius charge stations, all OPPOSITE. Rank-one, curvature, parameter slope and two-grid open-side checks pass.

'''+text+'''

Two corrections to v049: at ratio 1.054 the missing root is (0.67695168,0.90486606), paired with (0.67838909,0.91363691), separation 0.0088878553; exact engines agree within 3.6e−15. At A=−0.31 the saved residual is 1.26189219 meV, not zero, so it is not the tracker-collapse signature reported in §2. The late birth extrapolation 1.0534 is superseded by the accepted exact N4 fold 1.0529719222. No established topology label changes.

31 supplied tests and 14 reporting/guard tests pass. The next bounded task is a separately frozen local-domain gate for the extra flat-pair birth and annihilation while retaining the original pair. A global positive-flat-gap test would be invalid for those events. Then lower-pair birth, original-pair continuation/join, and the separate lower unlink collision. Everything here is self-tested evidence for the declared model, not physical-bilayer validation.
''')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
