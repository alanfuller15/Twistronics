"""Generate the event handoff only from matching tests and reconciled evidence."""
import argparse,json
from pathlib import Path
from evidence import read,sha,write,require
from protocol import frozen_protocol
from test_evidence import read_evidence
import reconcile
ROOT=Path(__file__).resolve().parent


def collect(evidence):
    tests=read_evidence(ROOT,evidence);protocol=frozen_protocol();r=reconcile.build()
    require(r==read(ROOT/'IMPACT.json'),'stale event reconciliation')
    return dict(r,protocol_sha256=protocol,tests=tests,test_evidence=Path(evidence).resolve().relative_to(ROOT).as_posix(),impact_sha256=sha(ROOT/'IMPACT.json'))


def main(evidence):
    s=collect(evidence);t=s['tests'];table='| Engine | N4 saved fold T | N6 saved fold T | N8 fresh fold T | N8 − N6 |\n|---|---:|---:|---:|---:|\n'
    gaps='| Engine | Gap at own fold − 0.001, N8 | Gap at fixed T=−0.4, N8 | Fixed-T gap change from N6 |\n|---|---:|---:|---:|\n'
    for c in s['cutoff_comparisons']:
        table+=f"| {c['engine']} | {c['N4_saved_fold']:.12f} | {c['N6_saved_fold']:.12f} | {c['N8_fresh_fold']:.12f} | {c['N8_minus_N6_fold']:+.3e} |\n"
        gaps+=f"| {c['engine']} | {c['near_open_gap_N8_fresh']:.12f} | {c['far_open_gap_N8_fresh']:.12f} | {c['far_open_gap_difference']:+.3e} |\n"
    errors=[q['relative_error'] for c in s['cases'] for q in c['separation_law']]
    retries=sum(q['fallback_attempts'] for c in s['cases'] for q in c['openings'])
    attempts=sum(q['optimizer_attempts'] for c in s['cases'] for q in c['openings'])
    labels_match=all(c['charge_labels_match_saved'] for c in s['cutoff_comparisons'])
    note=f'''# TEAM SHARE — our v059

The lower unlink collision now has a bounded N8 replay in both lab_nn_full engines. The held state is A=0.2, B=−0.4, phi=0°, w0/w1=0.8, theta=1.05°, eps=0.003, with T running from 0 to −0.4 and the lower-remote|flat1 gap selected. Constant w1=110 meV and w0=88 meV remain the declared approximation. BM keeps linear reciprocal geometry and cutoff_tol=1e-6; reference keeps exact reciprocal geometry and cutoff_tol=1e-9. This is the separate lower unlink event, not the final endpoint studied in v058.

{table}
Largest absolute N6→N8 fold shift: **{s['max_abs_N8_N6_fold_shift']:.9g}** in dimensionless T. BM minus reference at N8: **{s['cross_engine_N8_fold_difference']:.9g}**; those engines retain different geometry approximations. N4/N6 are hashed v055 evidence, not fresh runs here.

Each N8 engine passes two derivative-resolution fold solves, rank-one Jacobian and external-isolation checks, and two finite-difference checks of nonzero null curvature and transverse parameter slope. Both predict the pair on the T>fold side. **{sum(c['root_states'] for c in s['cases'])} bounded root stations** track the pair in total. In addition to the original nine-station layout, each engine samples fold+0.004 and fold+0.00025. At offsets 0.004, 0.001 and 0.00025, observed squared node separation agrees with the local fold coefficient times offset within the frozen 2% tolerance. Largest measured relative discrepancy across the six checks: **{max(errors):.6%}**. This tests the local square-root closing law numerically.

The two charge stations in each engine are T=0 and that engine's fold+0.001. All four are **OPPOSITE** under the retained mesh/radius gate: 256/512 loops at the same radius, 512 at half radius, with 128/256 spatial transport, located exterior-gap minima and orientation checks. Only unresolved phase steps permit the recorded finer fallback. Agreement with the saved N6 station labels: **{labels_match}**. Absolute charges are not transported through annihilation, and the closest extra root station at fold+0.00025 is a root/separation check, not an additional charge measurement.

{gaps}
Gap values and differences are meV. Opening checks use 18/24 interval grids including both chart faces, explicit 24/48 edge searches, corner/inward/fold seeds and bounded optimization. Every selected result passes finite-value, non-worsening, projected-gradient and local-curvature checks, and both meshes agree within 0.001 meV. Opening searches record **{attempts} optimizer attempts**, including **{retries} rejected attempts before accepted fallback**. Near-fold gaps are compared at the same offset from each cutoff's own fold; the fixed-T=−0.4 gap is a same-parameter cutoff comparison. Positive finite searches are not a rigorous global no-node proof.

**{t['passed']} tests passed in bound run `{t['run_id']}`**, evidence SHA256 `{t['record_sha256']}`. Tests exercise normal forms, wrong fold side, nonfinite/failed optimization, separation scaling, corrupted event/charge/gap records, test-evidence binding and deterministic packaging. The published count comes from actual collection/execution/JUnit tied to current source/tests/inputs/runtime. Two single-thread numerical workers record matching runtime identities before and after execution. NUMERICAL_PLAN.json was frozen before the workers; PLAN.json is the later publication freeze. Prior tracked records and the previous README are preserved.

Coverage gained: one N8 critical event in each engine, in addition to v058's endpoint-gap comparison. The historical N4/N6 campaign coverage stays unchanged. The entire N8 braid sequence has not been replayed, and this batch does not extend the flat-pair frame path, Euler class or endpoint w1 to N8.

Limits: {' '.join(s['limits'])}

Next bounded numerical target: the braid-2 critical window at N8, selected from its retained N4/N6 brackets and continued with two seeds in each engine under a separately frozen plan. Broader historical consumer-impact questions remain open. Any physical magnitude claim still needs the inventor's intended acceptance target, a microscopic tunnelling strain law and independent reference or measurement evidence.

Start with `research/v059/REPORT.md`, `SUMMARY.json`, `IMPACT.json`, `NUMERICAL_PLAN.json`, `HISTORICAL_TARGETS.json` and both complete event records in `results/`. The ZIP includes prior campaign/audit/team history and the v055 handoff correction.
'''
    write(ROOT/'SUMMARY.json',s);(ROOT/'TEAM_SHARE_v059.md').write_text(note);(ROOT/'REPORT.md').write_text(note.replace('# TEAM SHARE — our v059','# Our v059: bounded N8 lower unlink event',1))
    print(json.dumps(dict(status=s['status'],tests=t,max_fold_shift=s['max_abs_N8_N6_fold_shift']),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test-evidence',type=Path,required=True);main(p.parse_args().test_evidence)
