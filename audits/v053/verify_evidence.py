#!/usr/bin/env python3
"""Read-only artifact checks. Does not import or execute the audited project.

Usage: python -B verify_evidence.py /path/to/twistronics_v053_reconciled
Prints observations as JSON. Does not reproduce scientific computations or tests.
"""
import ast
import hashlib
import json
import sys
from pathlib import Path


def inspect(root):
    root = Path(root).resolve()
    current = root / 'v053'

    def child(base, name):
        path = (base / name).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Evidence path escapes project root')
        return path

    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def read(path):
        return json.loads(path.read_text())

    def hash_check(base, entries):
        return {'entries': len(entries), 'mismatches': [
            name for name, digest in entries.items()
            if not child(base, name).is_file() or sha(child(base, name)) != digest
        ]}

    manifest = read(root / 'MANIFEST.json')
    out = {'manifest': hash_check(root, {n: e['sha256'] for n, e in manifest['files'].items()})}
    out['manifest']['size_mismatches'] = [
        n for n, e in manifest['files'].items()
        if not child(root, n).is_file() or child(root, n).stat().st_size != e['bytes']
    ]
    out['manifest']['extra_files'] = sorted(
        str(p.relative_to(root)) for p in root.rglob('*')
        if p.is_file() and str(p.relative_to(root)) not in manifest['files']
        and p != root / 'MANIFEST.json'
    )
    plan = read(current / 'PLAN.json')
    protocol = sha(current / 'PLAN.json')
    out['plan'] = {key: hash_check(current, plan[key]) for key in ('source_sha256', 'anchor_sha256')}
    summary = read(current / 'SUMMARY.json')
    out['summary_source_hashes'] = hash_check(current, summary['source_sha256'])
    out['prior_summary_hash_matches'] = (
        sha(root / 'prior_our_v052/v052/SUMMARY.json') == summary['prior_v052']['sha256']
    )
    out['cases'] = []
    all_rows = []
    for folder in sorted((current / 'results').glob('prep_*')):
        saved = read(folder / 'summary.json')
        rows = [read(f) for f in sorted(folder.glob('step_*/record.json'))]
        all_rows.extend(rows)
        out['cases'].append({
            'folder': folder.name, 'records': len(rows), 'status': saved['status'],
            'summary_equals_records': saved['states'] == rows,
            'protocols_match': saved['protocol_sha256'] == protocol and all(
                d['protocol_sha256'] == protocol for d in rows),
            'frame_hash_mismatches': [d['step'] for d in rows if
                sha(folder / f"step_{d['step']:03d}/frames.npz") != d['frames_sha256']],
            'steps': [d['step'] for d in rows],
            'coarse_checks': sum(d['parameter_mesh_check'] is not None for d in rows),
            'nonaccepted': sum(d['status'] != 'ACCEPT' or d['pilot'] for d in rows),
            'charges': {side: sorted({t[side]['charge'] for d in rows
                for t in d['temporal_trials']}) for side in ('a', 'b')},
            'endpoint_join_present': 'endpoint_join' in rows[-1],
        })
    out['saved_records'] = {
        'states': len(all_rows),
        'mesh_checks': sum(d['parameter_mesh_check'] is not None for d in all_rows),
        'loop_trials': sum(len(d['temporal_trials']) for d in all_rows),
        'labels': sorted({d['label'] for d in all_rows}),
        'min_external_gap': min(t['min_external_gap'] for d in all_rows for t in d['spatial_transport']),
    }
    out['resume_hashes'] = hash_check(current, read(current / 'provenance/resume_check.json')['files'])
    out['packager_prior_zip_exists'] = (root / 'sequence-outputs/twistronics_v052_reconciled.zip').exists()
    out['packager_output_parent_exists'] = (root / 'sequence-outputs').is_dir()
    out['test_log'] = (current / 'provenance/frame_tests.txt').read_text()
    out['current_syntax'] = {'files': 0, 'failures': []}
    for path in sorted(current.rglob('*.py')):
        try:
            ast.parse(path.read_bytes(), filename=str(path))
            out['current_syntax']['files'] += 1
        except SyntaxError as error:
            out['current_syntax']['failures'].append({
                'file': str(path.relative_to(current)), 'line': error.lineno, 'message': error.msg,
            })
    out['limits'] = [
        'Hash agreement checks internal consistency, not authenticity or chronology.',
        'Saved numerical values are not recomputed.',
        'NPZ files are hashed as opaque bytes; their arrays are not evaluated.',
        'Project modules and tests are not executed.',
    ]
    return out


if __name__ == '__main__':
    print(json.dumps(inspect(sys.argv[1]), indent=2))
