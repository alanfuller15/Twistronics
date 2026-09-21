"""Publish only accepted fresh replays with matching complete-suite evidence."""
import argparse
import json
from pathlib import Path
from checkpoints import digest, save_json
from compare_results import compare
from protocol import frozen_protocol
from prep_acceptance import validate
from test_evidence import read_evidence

ROOT = Path(__file__).resolve().parent


def collect(evidence):
    tests = read_evidence(ROOT, evidence)
    protocol = frozen_protocol()
    impact = compare()
    if impact != json.loads((ROOT / 'IMPACT.json').read_text()):
        raise ValueError('saved impact report differs from revalidated records')
    cases = []
    for item in impact['cases']:
        folder = ROOT / 'results' / f"prep_{item['engine']}_N{item['N']}"
        r = validate(folder, protocol)
        cases.append(dict(engine=r['engine'], N=r['N'], states=len(r['states']), labels=r['labels'],
            parameter_mesh_checks=sum(s['parameter_mesh_check'] is not None for s in r['states']),
            min_external_gap=min(t['min_external_gap'] for s in r['states'] for t in s['spatial_transport']),
            legacy_calls=sum(item['forbidden_calls'].values()), endpoint_relative_orientation=r['states'][-1]['endpoint_join']['relative_orientation']))
    return dict(version='our_v054', status='ACCEPT', scope=impact['scope'], protocol_sha256=protocol,
        cases=cases, accepted_states=sum(c['states'] for c in cases), parameter_mesh_checks=sum(c['parameter_mesh_checks'] for c in cases),
        tests=tests, test_evidence=str(Path(evidence).resolve().relative_to(ROOT)), impact_sha256=digest(ROOT / 'IMPACT.json'),
        label_changes=impact['label_changes'], max_root_difference=impact['max_root_difference'],
        max_external_gap_difference=impact['max_external_gap_difference'], min_frame_overlap=impact['min_frame_overlap'],
        remaining=['separate lower unlink collision', 'effect of legacy helper defects on historical campaigns outside this preparation replay'], limits=impact['limits'])


def main(evidence):
    summary = collect(evidence)  # All gates precede any publication writes.
    tests = summary['tests']
    change = ('No preparation label changed.' if not summary['label_changes'] else f"{len(summary['label_changes'])} preparation labels changed; see SUMMARY.json.")
    table = '| Engine | N | Fresh states | Labels | Parameter checks | Legacy calls |\n|---|---:|---:|---|---:|---:|\n'
    for row in summary['cases']:
        table += f"| {row['engine']} | {row['N']} | {row['states']} | {', '.join(row['labels'])} | {row['parameter_mesh_checks']} | {row['legacy_calls']} |\n"
    note = f'''# TEAM SHARE — our v054: audit repairs and measured impact

The audit defects are repaired in a new version; v053 and its recorded evidence remain unchanged. The corrected BM helper retains both optimizer attempts and reports the final attempt's termination fields, rejects failed/nonfinite plain-call outcomes, and returns a checked canonical coordinate/value pair. Report publication now requires a complete-suite test artifact bound to source, tests, numerical inputs and runtime. Packaging uses an explicit verified prior-tree contract, without pretending to reconstruct the original prior ZIP. Legacy Euler/braid entry points require exploratory opt-in, and real-frame/harmonic guards survive Python optimization.

All {summary['accepted_states']} preparation states were recomputed in both engines at N4/N6, with {summary['parameter_mesh_checks']} fine/coarse parameter checks and four endpoint frame joins. {change} The suspect helper and legacy measurement entry points were instrumented to fail if called: every case completed with zero such calls. This supports non-use on this route; it does not clear every historical result.

{table}
Maximum root difference from v053: {summary['max_root_difference']:.3g}. Maximum comparison-path external-gap difference: {summary['max_external_gap_difference']:.3g} meV. Minimum old/new frame-plane overlap: {summary['min_frame_overlap']:.12f}. Frame signs were compared explicitly; an arbitrary common gauge flip is not treated as a physical change.

**{tests['passed']} tests passed in the bound run `{tests['run_id']}`**, started {tests['started_utc']}. Counts are read from collection, execution records and JUnit, not a fixed passing-test statement. The evidence digest is `{tests['record_sha256']}`. This is a recorded run for this source/input/environment identity, not a claim that every later report regeneration reruns tests.

The next numerical coverage item remains the separate lower unlink collision. Keep that batch bounded, start with both N4 engines, then qualify N6. Older campaign uses of legacy helpers remain a separate impact-review task. No continuous-interval proof, infinite-cutoff bound, comprehensive dependency clearance or physical-bilayer validation is claimed.

Start with REPORT.md, IMPACT.json, PLAN.json and the referenced test evidence. SOURCE_REVIEW.md records the source-based findings and limits. Reproduction commands are in README.md. Frozen source and input hashes are consistency evidence; they do not prove independent authorship or physical truth.
'''
    save_json(ROOT / 'SUMMARY.json', summary)
    (ROOT / 'TEAM_SHARE_v054.md').write_text(note)
    (ROOT / 'REPORT.md').write_text(note.replace('# TEAM SHARE — our v054:', '# Our v054:', 1))
    (ROOT / 'LEDGER.md').write_text('# v054 audit-repair and impact ledger\n\n' + table + '\n' + change + '\n\nNew evidence: fresh preparation replay and source-bound tests. Retained historical evidence: v053 and earlier event windows. Open: separate lower unlink collision; earlier legacy-helper consumers.\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-evidence', type=Path, required=True)
    main(parser.parse_args().test_evidence)
