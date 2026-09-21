"""Reconcile fresh accepted records/frames against the unchanged v053 baseline."""
import json
from pathlib import Path
import numpy as np
from checkpoints import digest, save_json
from prep_acceptance import validate
from protocol import frozen_protocol
from measure import require
from impact_replay import forbidden_surface_names

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / 'v053'


def compare():
    baseline = json.loads((ROOT / 'BASELINE.json').read_text())
    require(digest(OLD / 'PLAN.json') == baseline['protocol_sha256'], 'baseline protocol changed')
    require(digest(OLD / 'SUMMARY.json') == baseline['summary_sha256'], 'baseline summary changed')
    protocol = frozen_protocol()
    cases, differences = [], []
    for cutoff in (4, 6):
        for engine in ('bm_lab', 'ref_lab'):
            name = f'prep_{engine}_N{cutoff}'
            folder, old_folder = ROOT / 'results' / name, OLD / 'results' / name
            new = validate(folder, protocol)
            old = validate(old_folder, baseline['protocol_sha256'])
            guard = json.loads((folder / 'guard_summary.json').read_text())
            require(guard['status'] == 'ACCEPT' and guard['fresh_start'] and guard['states'] == 19, 'missing fresh complete replay guard')
            require(guard['engine'] == engine and guard['N'] == cutoff and guard['protocol_sha256'] == protocol, 'wrong replay guard identity')
            require(set(guard['forbidden_calls']) == forbidden_surface_names() and not any(guard['forbidden_calls'].values()), 'forbidden legacy call observed or missing guard inventory')
            rows = []
            for before, after in zip(old['states'], new['states']):
                step = after['step']
                require(before['step'] == step and before['state'] == after['state'], 'comparison state mismatch')
                root_error = max(float(np.linalg.norm(np.asarray(a['f']) - b['f'])) for a, b in zip(after['nodes'], before['nodes']))
                frames = []
                with np.load(old_folder / f'step_{step:03d}/frames.npz', allow_pickle=False) as a, np.load(folder / f'step_{step:03d}/frames.npz', allow_pickle=False) as b:
                    require(np.array_equal(a['labels'], b['labels']), 'comparison basis changed')
                    for side, key in zip(('a', 'b'), ('e1', 'e2')):
                        overlap = b[key].T @ a[key]
                        singular = np.linalg.svd(overlap, compute_uv=False)
                        det = float(np.linalg.det(overlap))
                        require(singular.min() > .999999 and abs(det) > .999999, 'replayed plane differs')
                        sign = int(np.sign(det))
                        require(after['temporal_trials'][1][side]['charge'] == sign * before['temporal_trials'][1][side]['charge'], 'replayed charge differs after frame alignment')
                        frames.append(dict(min_overlap=float(singular.min()), orientation=sign))
                if before['label'] != after['label']:
                    differences.append(dict(engine=engine, N=cutoff, step=step, before=before['label'], after=after['label']))
                require(root_error < 1e-6, 'replayed roots differ beyond join tolerance')
                rows.append(dict(step=step, label_before=before['label'], label_after=after['label'], root_difference=root_error, frame_comparison=frames,
                    external_gap_difference=max(abs(a['min_external_gap'] - b['min_external_gap']) for a, b in zip(after['spatial_transport'], before['spatial_transport']))))
            require(len(rows) == 19, 'incomplete comparison')
            cases.append(dict(engine=engine, N=cutoff, states=rows, forbidden_calls=guard['forbidden_calls'],
                new_summary_sha256=digest(folder / 'summary.json'), old_summary_sha256=digest(old_folder / 'summary.json'), guard_sha256=digest(folder / 'guard_summary.json')))
    return dict(version='our_v054', status='ACCEPT', scope='V053_PREPARATION_ROUTE_AUDIT_IMPACT_REPLAY',
        baseline_protocol_sha256=baseline['protocol_sha256'], protocol_sha256=protocol,
        states_compared=sum(len(c['states']) for c in cases), label_changes=differences, cases=cases,
        max_root_difference=max(s['root_difference'] for c in cases for s in c['states']),
        max_external_gap_difference=max(s['external_gap_difference'] for c in cases for s in c['states']),
        min_frame_overlap=min(f['min_overlap'] for c in cases for s in c['states'] for f in s['frame_comparison']),
        limits=['Impact conclusion covers the 76-state v053 preparation replay, not every historical measurement',
                'Forbidden-call instrumentation and shared-engine agreement do not establish physical correctness',
                'Finite sampled replay does not prove continuous-path or infinite-cutoff behavior'])


if __name__ == '__main__':
    result = compare()
    save_json(ROOT / 'IMPACT.json', result)
    print(json.dumps({k: v for k, v in result.items() if k != 'cases'}, indent=2))
