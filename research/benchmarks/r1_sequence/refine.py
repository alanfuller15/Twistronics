"""Frozen transport-mesh refinement; preserves all original failed rows."""
from pathlib import Path
import argparse, json, traceback, time
import numpy as np
import sequence as original

ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT / 'REFINEMENT_PLAN.json').read_text())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', choices=P['engines'], required=True)
    args = ap.parse_args()
    dest = ROOT / ('REFINED_' + args.engine.upper() + '.json')
    if dest.exists():
        raise SystemExit('Refusing overwrite')
    raw = {e: json.loads((ROOT / (e.upper() + '.json')).read_text()) for e in P['engines']}
    assert all(d['status'] != 'RUNNING' for d in raw.values()), 'Original reports must finish first'
    assert P['original_plan_sha256'] == original.sha(ROOT / 'PLAN.json')
    Ds = list(P['D_stations_meV'])
    if any(not r['diagnostics_pass'] for d in raw.values() for s in d['matched_path_stations'] if s['D_meV'] == 39. for r in s['trials']):
        Ds.append(39.)
    source_files = [ROOT / 'refine.py', ROOT / 'sequence.py', ROOT / 'PLAN.json', ROOT / 'BM.json', ROOT / 'REF.json']
    result = {'status': 'RUNNING', 'engine': args.engine, 'N': P['N'], 'selected_D_meV': Ds,
              'plan_sha256': original.sha(ROOT / 'REFINEMENT_PLAN.json'),
              'source_hashes': {str(f.relative_to(ROOT.parent)): original.sha(f) for f in source_files},
              'runtime': raw[args.engine]['runtime'], 'stations': [], 'errors': []}
    def save():
        dest.write_text(json.dumps(result, indent=2) + '\n')
    save()
    for D in Ds:
        try:
            src = next(s for s in raw[args.engine]['matched_path_stations'] if s['D_meV'] == D)
            assert src['roots_pass']
            m = original.model(args.engine, P['N'], D)
            mon = original.Monitor(m, args.engine)
            station = {'D_meV': D, 'roots_source': args.engine.upper() + '.json',
                       'affine_checks': mon.affine_checks, 'affine_spectrum_errors': mon.spectral_checks, 'trials': []}
            result['stations'].append(station)
            for path in P['paths']:
                for nt in P['transport_points']:
                    start = time.time()
                    # Only in-memory sampling configuration changes. Both plans and
                    # the original runner remain byte-for-byte preserved on disk.
                    original.P['matched_path_config'] = {**original.P['matched_path_config'], 'transport_points': nt}
                    row = original.matched_trial(mon, [np.array(r['f']) for r in src['roots']], path)
                    row['seconds'] = time.time() - start
                    station['trials'].append(row)
                    save()
                    print('REFINED', args.engine, D, path, nt, row['label'], 'pass', row['diagnostics_pass'],
                          'transport_smin', row['conditioning']['transport_step_smin'], 'seconds', round(row['seconds'], 1), flush=True)
            station['mesh_labels_agree'] = all(len({r['label'] for r in station['trials'] if r['path'] == path}) == 1 for path in P['paths'])
            mon.cache.clear()
        except Exception:
            result['errors'].append({'D_meV': D, 'error': traceback.format_exc()})
            print(result['errors'][-1]['error'], flush=True)
        save()
    rows = [r for s in result['stations'] for r in s['trials']]
    passed = not result['errors'] and len(rows) == len(Ds)*4 and all(r['diagnostics_pass'] for r in rows)
    passed = passed and all(s['mesh_labels_agree'] for s in result['stations'])
    result['status'] = 'REFINED_TRANSPORT_DIAGNOSTICS_PASS_NOT_FULL_BRAID_ACCEPTANCE' if passed else 'UNRESOLVED_CHECKS_RETAINED'
    save()
    return 0 if passed else 1

if __name__ == '__main__':
    raise SystemExit(main())
