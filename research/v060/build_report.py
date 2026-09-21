"""Publish measured claims only after matching tests and evidence reconciliation."""
import argparse,json
from pathlib import Path
from evidence import read,sha,write,require
from protocol import frozen_protocol
from test_evidence import read_evidence
import reconcile
ROOT=Path(__file__).resolve().parent


def collect(evidence):
    tests=read_evidence(ROOT,evidence);protocol=frozen_protocol();r=reconcile.build()
    require(r==read(ROOT/'IMPACT.json'),'stale window reconciliation')
    return dict(r,protocol_sha256=protocol,tests=tests,test_evidence=Path(evidence).resolve().relative_to(ROOT).as_posix(),impact_sha256=sha(ROOT/'IMPACT.json'))


def main(evidence):
    s=collect(evidence);t=s['tests'];table='| Engine | N4 saved crossing | N6 saved crossing | N8 fresh crossing | N8 − N6 |\n|---|---:|---:|---:|---:|\n'
    for c in s['cutoff_comparisons']:table+=f"| {c['engine']} | {c['N4_saved_ratio']:.12f} | {c['N6_saved_ratio']:.12f} | {c['N8_fresh_ratio']:.12f} | {c['N8_minus_N6']:+.3e} |\n"
    state_table='| Ratio w0/w1 | BM N8 | Reference N8 |\n|---:|---|---|\n'
    for j,ratio in enumerate(s['ratios']):state_table+=f"| {ratio:.5f} | {s['cases'][0]['labels'][j]} | {s['cases'][1]['labels'][j]} |\n"
    nstates=sum(c['states'] for c in s['cases']);nroots=sum(c['roots'] for c in s['cases']);ncoarse=sum(c['coarse_checks'] for c in s['cases']);retry=sum(c['loop_retry_stages'] for c in s['cases']);min_gap=min(c['min_comparison_gap'] for c in s['cases'])
    match=all(q['N6_label']==q['N8_label'] for c in s['cutoff_comparisons'] for q in c['common_states']);node_shift=max(q['max_node_displacement'] for c in s['cutoff_comparisons'] for q in c['common_states'])
    note=f'''# TEAM SHARE — our v060

The braid-2 critical window now has a fresh N8 replay in both lab_nn_full engines, with a separately frozen numerical plan. At five ratio values from 0.99000 through 0.99100, both engines reproduce the change in the spatial charge comparison. Each individually carried temporal node charge stays constant. The comparison path becomes singular when the upper-next node X1 crosses the U1–U2 segment; the isolation gate explicitly rejects that singular comparison.

{table}
Largest absolute N6→N8 crossing shift: **{s['max_abs_N8_N6_crossing_shift']:.9g}** in w0/w1. N8 BM minus reference: **{s['cross_engine_N8_ratio_difference']:.9g}**. N4/N6 values come from retained v042 records. The held-state linkage of those historical records is contextual through the retained runner and State definition; it was not embedded in the old raw records.

{state_table}
Held state: A=0, B=−0.4, T=−0.8, phi=80°, theta=1.05°, eps=0.003, w_kappa=0 and w_mode=average. The approximation keeps w1=110 meV while w0=110 times the ratio. BM retains linear reciprocal geometry with cutoff_tol=1e-6; reference retains exact reciprocal geometry with cutoff_tol=1e-9. The root chart is explicitly unwrapped: [0,1] × [0,1.1]. U2 remains above f2=1; no periodic wrap is applied to a finite-cutoff Hamiltonian.

Evidence: **{nstates} states, {nroots} continued roots, {ncoarse} coarse/fine parameter-frame comparisons, {nstates} saved frame checkpoints and {nstates*3} loop/radius trials**. Each loop/radius trial measures both temporal charges and the directly transported spatial B charge. Spatial transport is compared at 128/256 base steps, with explicit adjacent-node seeds and located minima of both exterior gaps. Minimum accepted sampled/located comparison gap: **{min_gap:.9g} meV**. This positive off-event minimum is distinct from the rejected zero-gap crossing. Phase-only loop retry stages used: **{retry}**.

Each crossing is solved at two Brent tolerances, with final optimizer metadata and all distinct evaluations retained. The point on the U segment has exterior gap below 1e-5 meV and fails specifically with `selected group loses isolation`. Saved frames are checked for hash/record agreement, shape, finiteness, orthonormality, temporal overlaps, spatial orientation and coarse/fine determinants. These artifact checks do not recompute the eigensolver.

At the common retained N6 ratios 0.99000 and 0.99100, labels agree: **{match}**. Largest displacement among the six tracked roots at those common ratios: **{node_shift:.9g}** in fractional reciprocal coordinates. Values at the three intervening N8 states are new finer sampling, not matched N6 measurements.

Publication evidence: **{t['passed']} assertion cases pass**, actual complete-suite run `{t['run_id']}`, bound to source, tests, numerical inputs, result files and runtime identity. The numerical source plan was frozen before the workers. The separate publication plan is frozen after measurements and before the bound test run. Neither hash timing nor a self-authored test suite is independent attestation. All 3,149 preserved prior tracked files are retained unchanged; prior README is copied into this batch's provenance.

Limits:

'''+''.join('- '+x+'\n' for x in s['limits'])+'''
Next bounded target: the first-annihilation critical event at N8 in both engines, starting from retained N4/N6 roots and fold diagnostics under a new frozen plan. A complete N8 campaign would still require the connecting legs, longer braid-2 leg and relevant frame/topological checks. Any physical magnitude claim still needs a microscopic tunnelling strain law and independent reference or measurement evidence.

Start with `research/v060/REPORT.md`, `SUMMARY.json`, `IMPACT.json`, `NUMERICAL_PLAN.json`, and `HISTORICAL_TARGETS.json`. Complete records and ten frame checkpoints are in `results/`; test evidence and worker logs are in `provenance/`. This ZIP also retains prior campaign, audit and team history.
'''
    write(ROOT/'SUMMARY.json',s);(ROOT/'TEAM_SHARE_v060.md').write_text(note);(ROOT/'REPORT.md').write_text(note.replace('# TEAM SHARE — our v060','# Our v060: bounded N8 braid-2 critical window',1))
    print(json.dumps(dict(status=s['status'],tests=t,max_crossing_shift=s['max_abs_N8_N6_crossing_shift']),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test-evidence',type=Path,required=True);main(p.parse_args().test_evidence)
