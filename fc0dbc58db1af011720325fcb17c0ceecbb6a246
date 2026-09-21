"""Publish only after matching actual tests and reconciling numerical evidence."""
import argparse,json
from pathlib import Path
from evidence import read,sha,write,require
from protocol import frozen_protocol
from test_evidence import read_evidence
import reconcile
ROOT=Path(__file__).resolve().parent


def collect(evidence):
    tests=read_evidence(ROOT,evidence);protocol=frozen_protocol();r=reconcile.build()
    require(r==read(ROOT/'IMPACT.json'),'stale numerical reconciliation')
    return dict(r,protocol_sha256=protocol,tests=tests,test_evidence=Path(evidence).resolve().relative_to(ROOT).as_posix(),impact_sha256=sha(ROOT/'IMPACT.json'))


def main(evidence):
    s=collect(evidence);t=s['tests'];table='| Engine | Gap | N4 saved | N6 saved | N8 fresh | N8 − N6 |\n|---|---|---:|---:|---:|---:|\n'
    for r in s['cutoff_comparisons']:table+=f"| {r['engine']} | {r['gap']} | {r['N4_saved']:.9f} | {r['N6_saved']:.9f} | {r['N8_fresh']:.9f} | {r['N8_minus_N6']:+.9f} |\n"
    partner_agrees=all(x['agrees_with_rounded_output'] for x in s['partner_comparisons'])
    note=f'''# TEAM SHARE — our v058

Completed a fresh N8 endpoint-gap comparison in both modern engines under the frozen lab_nn_full model: A=−0.30, B=−0.40, T=−1.8, phi=80°, w0/w1=1.10, theta=1.05°, eps=0.003. Constant w1=110 meV and w0=121 meV are the declared approximation. BM retains linear reciprocal geometry and cutoff_tol=1e-6; reference retains exact reciprocal geometry and cutoff_tol=1e-9. They share the guarded eight-band measurement harness.

{table}
All table values are meV. N4/N6 are retained, hashed v048 measurements; N8 is fresh. Largest absolute N6→N8 difference across these eight gap comparisons: **{s['maximum_abs_N8_N6_gap_change']:.9g} meV**. Largest BM/reference N8 difference: **{s['maximum_cross_engine_gap_difference']:.9g} meV**; the retained geometry conventions differ. Each of the four located gaps in each engine passes the finite-sample positivity and refinement checks. No new topological label is assigned.

Search scope is broader than the partner's original one-seed N8 refinement: 12×12 and 24×24 interval grids including both faces (13×13 and 25×25 points), all four edges split into 24 and 48 intervals, bounded refinements of sampled local minima, corners, inward edge seeds and retained N4/N6/partner positions with two diagonal offsets. Every seed must yield a successful finite non-worsening result with projected gradient ≤1e-4; failed attempts are retained before fallback. Final selected minima have positive local curvature at two step sizes; grid/edge minimum differences must be ≤0.001 meV. Reality, Hermiticity, eigen-residual, affine-Hamiltonian and analytic-gradient checks run explicitly. No silent coordinate wrapping is used.

Recorded N8 dimensions: {[c['dimension'] for c in s['cases']]}. Distinct sampled coordinates per engine: {[c['sampled_points'] for c in s['cases']]}. Recorded refinements: {sum(c['refinements'] for c in s['cases'])}; optimizer attempts: {sum(c['optimizer_attempts'] for c in s['cases'])}; fallback attempts retained: {sum(c['fallback_attempts'] for c in s['cases'])}. Both workers record matching runtime identities before and after execution with one BLAS thread each. The numerical plan was frozen before these workers; the publication plan was frozen after results and tests were authored. Hash agreement is internal consistency, not independent attestation.

All four reference results agree with the supplied rounded N8 output within the predeclared value/coordinate tolerances: **{partner_agrees}**. The original v045 log explicitly describes N6-located, N8-refined minima. v048 later narrows its wording to local cutoff stability and adds per-start logging. {s['partner_run_binding']} No original failure or fresh pass is inferred from that missing provenance. The fresh two-mesh/edge results are their own evidence.

**{t['passed']} tests passed in bound run `{t['run_id']}`**, evidence SHA256 `{t['record_sha256']}`. The report reads actual collected, executed and JUnit outcomes tied to source/tests/inputs/runtime. Tests cover nonfinite/escaped/stale/failed optimization outcomes, projected gradients, edge failure, mesh rejection, evidence tampering and packaging. Prior tracked artifacts are preserved; the old top-level README is retained in provenance.

Limits: {' '.join(s['limits'])}

Next: choose a bounded N8 continuation through a previously gated critical event, with retained N4/N6 roots and the same model conventions. The present endpoint comparison does not resolve the remaining historical scalar/mass/angle and exploratory braid impact questions. Physical magnitude claims still require the inventor's intended acceptance target and a named microscopic tunnelling strain law.

Start with `research/v058/REPORT.md`, `SUMMARY.json`, `IMPACT.json`, `NUMERICAL_PLAN.json`, `HISTORICAL_TARGETS.json` and the two raw files in `results/`. The ZIP preserves prior team notes, audit findings, test evidence and numerical records.
'''
    write(ROOT/'SUMMARY.json',s);(ROOT/'TEAM_SHARE_v058.md').write_text(note);(ROOT/'REPORT.md').write_text(note.replace('# TEAM SHARE — our v058','# Our v058: N8 endpoint gaps in both modern engines',1))
    print(json.dumps(dict(status=s['status'],tests=t,max_cutoff_change=s['maximum_abs_N8_N6_gap_change']),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test-evidence',type=Path,required=True);main(p.parse_args().test_evidence)
