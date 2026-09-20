"""Publish only complete, source-checked frame replays and verified joins."""
from pathlib import Path
import json,hashlib
from prep_acceptance import validate
from protocol import frozen_protocol
from ledger_guard import accepted,grid,kinetic
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PRIOR=BASE/'lower-preparation-v052' if (BASE/'lower-preparation-v052').is_dir() else BASE/'prior_our_v052/v052'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,data):(ROOT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def main():
 protocol=frozen_protocol();kinetic(json.loads((ROOT/'PLAN.json').read_text()));records=[];rows=[];sources={}
 for folder in sorted((ROOT/'results').glob('prep_*_N*')):
  if not folder.is_dir():continue
  r=validate(folder,protocol);records.append(r);sources[str((folder/'summary.json').relative_to(ROOT))]=sha(folder/'summary.json')
  states=r['states'];j=states[-1]['endpoint_join'];fine=[t for s in states for t in s['temporal_transport']];coarse=[t for s in states if s['parameter_mesh_check'] for t in s['parameter_mesh_check']['transport']]
  row=dict(engine=r['engine'],N=r['N'],geometry=states[0]['geometry'],states=len(states),labels=r['labels'],carried_charges=r['temporal_charges'],min_parameter_overlap=min(t['min_overlap'] for t in fine),min_coarse_parameter_overlap=min(t['min_overlap'] for t in coarse),max_basis_norm_loss=max(max(t['old_norm_loss'],t['new_norm_loss']) for t in fine+coarse),min_spatial_overlap=min(t['min_overlap'] for s in states for t in s['spatial_transport']),min_spatial_external_gap=min(t['min_external_gap'] for s in states for t in s['spatial_transport']),parameter_mesh_checks=sum(s['parameter_mesh_check'] is not None for s in states),min_parameter_orientation_det=min(min(s['parameter_mesh_check']['orientation']) for s in states if s['parameter_mesh_check']),root_join=j['root_join']['max_distance'],min_endpoint_plane_overlap=min(x['min_overlap'] for x in j['frame_joins']),endpoint_relative_orientation=j['relative_orientation'],endpoint_common_orientation=j['common_orientation'],loop_fallback_states=sum(bool(s['rejected_loop_stages']) for s in states),source=str((folder/'summary.json').relative_to(ROOT)))
  rows.append(row)
 grid(rows)
 prior=accepted(PRIOR/'SUMMARY.json')
 if prior['fold_windows']!=4 or prior['scope']!='FULL_CHART_LOWER_GAP_SEARCH':raise ValueError('unexpected prior lower-birth scope')
 resume=accepted(ROOT/'provenance/resume_check.json')
 for name,h in resume['files'].items():
  if sha(ROOT/name)!=h:raise ValueError('resumed checkpoint changed')
 allstates=[s for r in records for s in r['states']];labels=sorted({s['label'] for s in allstates})
 summary=dict(version='our_v053',status='ACCEPT',scope='ORIGINAL_FLAT_PAIR_SAMPLED_FRAME_REPLAY',kinetic='lab_nn_full',protocol_sha256=protocol,cases=rows,accepted_states=len(allstates),charged_states=len(allstates),parameter_mesh_checks=sum(x['parameter_mesh_checks'] for x in rows),labels=labels,all_carried_charges_constant=all(all(len(c)==1 for c in r['temporal_charges'].values()) for r in records),max_root_join=max(x['root_join'] for x in rows),min_endpoint_plane_overlap=min(x['min_endpoint_plane_overlap'] for x in rows),min_parameter_overlap=min(x['min_parameter_overlap'] for x in rows),min_coarse_parameter_overlap=min(x['min_coarse_parameter_overlap'] for x in rows),min_spatial_overlap=min(x['min_spatial_overlap'] for x in rows),min_sampled_path_external_gap=min(x['min_spatial_external_gap'] for x in rows),max_basis_norm_loss=max(x['max_basis_norm_loss'] for x in rows),loop_fallback_states=sum(x['loop_fallback_states'] for x in rows),tests_this_batch=18,resume=resume,prior_v052=dict(sha256=sha(PRIOR/'SUMMARY.json'),fold_windows=4),source_sha256=sources,remaining=['separate lower unlink collision'],limits=['Sampled parameter/spatial transport, not an interval certificate','Relative frame orientation, not a gauge-independent SO(2) rotation or laboratory time evolution','Flat pair is not globally isolated after remote-band contacts; no continued Euler class','Unchanged engines/shared measurement harness; no physical validation'])
 if summary['accepted_states']!=76 or summary['parameter_mesh_checks']!=36:raise ValueError('incomplete scheduled coverage')
 dump('SUMMARY.json',summary)
 table=['| engine / geometry | N | states | labels | min fine/coarse parameter overlap | root join | endpoint plane overlap | relative orientation |','|---|---:|---:|---|---:|---:|---:|---:|']
 for r in rows:table.append(f"| {r['engine']} / {r['geometry']} | {r['N']} | {r['states']} | {','.join(r['labels'])} | {r['min_parameter_overlap']:.6f} / {r['min_coarse_parameter_overlap']:.6f} | {r['root_join']:.2e} | {r['min_endpoint_plane_overlap']:.12f} | {r['endpoint_relative_orientation']:+d} |")
 table='\n'.join(table)
 stats=f"Minimum sampled comparison-path external gap: {summary['min_sampled_path_external_gap']:.8f} meV. Minimum spatial-transport overlap: {summary['min_spatial_overlap']:.8f}. Maximum measured basis-norm loss: {summary['max_basis_norm_loss']:.3g}. Loop-fallback states: {summary['loop_fallback_states']}."
 (ROOT/'REPORT.md').write_text('''# Our v053 — original-flat-pair preparation frame replay

[self-tested] The preparation route now joins the accepted v044 start state through both roots and relative frame orientation in both engines at N4/N6. Each engine/cutoff covers A:0→0.2 at B=0, then B:0→−0.25 at A=0.2. There are 19 states per case, 76 in total, all with mesh/radius charge checks. Carried individual charges remain constant; observed spatial labels: '''+', '.join(labels)+'''.

'''+table+'\n\n'+stats+'''

## Evidence and what the join means

The accepted grid has eight A intervals and ten B intervals; a coarser frame route uses every second fine state, giving nine parameter-orientation comparisons per case, 36 in total. The eleven-state BM N4 pilot is preserved separately and excluded from all accepted counts. Both N4 replays passed before N6 began. The primary protocol and sources were frozen after the pilot and before the accepted runs.

At each state, both original roots are continued, both frames are carried using the declared real Fourier-coefficient basis, the spatial comparison path is checked/refined, and loops at two meshes plus half radius must agree. The strain-defined basis is constant on these A/B legs and its labels are explicitly checked. Local frame isolation along these sampled nodes/paths does not restore global flat-pair isolation after the previously measured remote-band contacts.

At the endpoint, saved v044 frame bytes must match their recorded digest and basis labels. Root positions must agree within 1e−6; both two-planes must overlap above 0.999999. Charge transformation must match each frame's orientation, and the pair's relative orientation must agree. A common overall orientation flip is allowed and tested: an arbitrary absolute gauge sign is not a physical discrepancy. The join does not claim a gauge-independent SO(2) angle or laboratory-coordinate time evolution.

## Validation

18 tests pass: eight endpoint-frame tests, three checkpoint-integrity tests and seven publication-acceptance tests. A common orientation flip and consistent root permutation pass; a one-sided flip, wrong charge, wrong basis/state, corrupted anchor bytes, missing coarse/temporal frames and pilot/partial records reject publication. Hamiltonian sources are unchanged from v052; historical supplied regression results are retained but were not rerun or recounted.

The BM N4 production run stopped after three committed states and resumed in a new process. All six existing checkpoint files kept their original hashes, and the resumed run completed all 19 states and its endpoint join. This exercises checkpoint restoration; no separate uninterrupted numerical replay was run for a bitwise trajectory comparison.

## Coverage and limits

Preparation event windows (v050–v052) and this original-pair frame replay now connect the baseline to the accepted v044 start. The separate lower unlink collision remains the outstanding numerical coverage item. No established campaign label was revised.

This is sampled continuation and transport, not a proof of behavior between all parameter/momentum samples. Fine/coarse comparison checks the orientation relevant to charge; it does not certify a unique accumulated SO(2) rotation. No Euler class is continued through loss of global two-band isolation. Two engines with a shared measurement harness do not exclude a shared conceptual error. Infinite-cutoff error bounds and physical-bilayer validation remain outside measured coverage. Recipient consumption is [unconfirmed].
''')
 (ROOT/'LEDGER.md').write_text('''# Accepted preparation frame ledger — our v053

Generated only after checking all frame checkpoints, source/protocol identity, actual endpoint frame bytes and the complete engine/cutoff grid.

'''+table+'''

New: 76 accepted and charge-checked states; 36 fine/coarse parameter-orientation checks; four root/relative-frame joins into v044. All individual carried charges are constant. See SUMMARY.json for overlaps, labels and gauge signs.

Retained: v050 upper-pair birth, v051 extra flat-pair birth/annihilation and v052 lower-pair birth; previously measured later route segments. Those event gates keep their original global/local scope.

The preparation route is now connected to v044 at the sampled-frame level. Outstanding numerical coverage: the separate lower unlink collision. No continuous-interval proof, globally extended Euler class, infinite-cutoff bound or physical validation claim.
''')
 (ROOT/'TEAM_SHARE_v053.md').write_text('''TEAM SHARE — our v053

Preparation now joins v044 through frames as well as roots. Both engines at N4/N6 complete A:0→0.2 and B:0→−0.25: 76 accepted states, every state mesh/radius charge-checked, 36 fine/coarse parameter-orientation comparisons. Carried individual charges stay constant; observed labels: '''+', '.join(labels)+'''.

'''+table+'\n\n'+stats+'''

Four endpoint joins pass the plane-overlap, root and relative-orientation gates. A common overall frame flip is permitted; no arbitrary absolute sign is asserted. The BM N4 stop/resume preserved all six committed files. Eighteen frame/checkpoint/publication tests pass; Hamiltonian sources are unchanged.

Together with v050–v052's preparation event windows, this closes the preparation-to-v044 connection at the sampled-frame level. Next is the separate lower unlink collision. The flat pair is not globally isolated after remote contacts, so no Euler class is carried through that region. No physical-bilayer validation or interval-proof claim.
''')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
