"""N8 endpoint and crossing follow-up, with explicitly matched path controls.

Original model, native winding/transport routines, and endpoint orchestrator
remain unchanged. The new matched_trial changes only the comparison path.
Run engines in separate processes: frame instrumentation changes module globals.
"""
from pathlib import Path
import sys, json, hashlib, time, traceback, argparse, platform
import numpy as np
import scipy

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'r1_validation'))
from validate import Monitor, model, trial, T, braid, classify, frac_dist
sys.path.insert(0, str(ROOT.parent / 'r1_events'))
from track import crossing
P = json.loads((ROOT / 'PLAN.json').read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def roots(m, engine):
    k = m.frac_to_k if engine == 'bm' else m.k
    fn = (lambda f: m.gaps(k(f))[0]) if engine == 'bm' else m.flat_gap
    records = []
    for seed in [[.4779, .7396], [.8769, .589]]:
        if engine == 'bm':
            f, gap, meta = m.refine(np.array(seed), fn, return_result=True)
        else:
            f, gap = m.refine(np.array(seed), fn)
            meta = {'success': True, 'native_refine_raises_on_failure': True}
        records.append({'f': f.tolist(), 'gap_meV': float(gap), 'optimizer': meta})
    accepted = all(r['optimizer']['success'] and r['gap_meV'] < T['root_gap_meV'] for r in records)
    accepted = accepted and frac_dist(*[np.array(r['f']) for r in records]) >= T['root_separation']
    return records, bool(accepted)

def matched_trial(mon, points, path):
    """Same native routines and diagnostic gates as trial(), explicit shared path."""
    m, U, k, lo, engine = mon.m, mon.U, mon.k, mon.lo, mon.engine
    p, q = points
    d = (q - p + .5) % 1 - .5
    q = p + d
    cfg = P['matched_path_config']
    r, n, nt = cfg['radius'], cfg['loop_points'], cfg['transport_points']
    if path == 'shifted_x':
        a, b = p + np.array([r, 0]), q + np.array([r, 0])
    elif path == 'collinear':
        off = -1.5 * r * d / np.linalg.norm(d)
        a, b = p + off, q - off
    else:
        raise ValueError(path)
    base = mon.data(k(a))[0].copy()
    braid.real_frame = lambda m, u, k: mon.frame(k)
    m.real_frame = lambda u, k, band, nb=2: mon.frame(k)
    diags = {}
    mon.begin(base)
    w1 = (braid.node_winding(m, U, p, r, n, base, exploratory=True) if engine == 'bm'
          else m.node_charge(U, p, lo, base, r=r, npts=n))
    diags['loop1_step_smin'] = min(mon.overlaps)
    diags['loop1_fixed_frame_smin'] = None if engine == 'bm' else m.last_smin
    mon.begin(base)
    end = (braid.transport(m, U, [a, b], base, nstep=nt, exploratory=True) if engine == 'bm'
           else m.transport(U, lo, a, b, base, n=nt))
    diags['transport_step_smin'] = min(mon.overlaps)
    mon.begin(end)
    w2 = (braid.node_winding(m, U, q, r, n, end, exploratory=True) if engine == 'bm'
          else m.node_charge(U, q, lo, end, r=r, npts=n))
    diags['loop2_step_smin'] = min(mon.overlaps)
    diags['loop2_fixed_frame_smin'] = None if engine == 'bm' else m.last_smin
    for name, center in [('loop1', p), ('loop2', q)]:
        first = mon.data(k(center + r * np.array([1., 0])))[0]
        last = mon.data(k(center + r * np.array([np.cos(2*np.pi*(n-1)/n), np.sin(2*np.pi*(n-1)/n)])))[0]
        diags[name + '_closure_smin'] = float(np.linalg.svd(first.T @ last, compute_uv=False).min())
    isolation = {'transport': mon.segment_bound(a, b), 'loop1': mon.circle_bound(p, r), 'loop2': mon.circle_bound(q, r)}
    label = classify(w1, w2) if w1 is not None and w2 is not None else 'INDETERMINATE'
    passed = label != 'INDETERMINATE' and all(v >= T['step_overlap_smin'] for v in diags.values() if v is not None)
    passed = passed and all(x['pass'] for x in isolation.values())
    return {'path': path, 'configuration': cfg, 'path_start': a.tolist(), 'path_end': b.tolist(),
            'windings': [w1, w2], 'label': label, 'conditioning': diags, 'isolation': isolation, 'diagnostics_pass': bool(passed)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', choices=P['engines'], required=True)
    args = ap.parse_args()
    dest = ROOT / (args.engine.upper() + '.json')
    if dest.exists():
        raise SystemExit('Refusing overwrite')
    source_files = [ROOT / 'sequence.py', ROOT.parent / 'r1_validation/validate.py', ROOT.parent / 'r1_validation/PLAN.json',
                    ROOT.parent / 'r1_events/track.py', ROOT.parent / 'r1_events/PLAN.json',
                    *sorted((ROOT.parent / 'r1_reproduction').glob('*.py')), ROOT.parent / 'r1_reproduction/PLAN.json']
    result = {'status': 'RUNNING', 'N': P['N'], 'engine': args.engine, 'plan_sha256': sha(ROOT / 'PLAN.json'),
              'source_hashes': {str(f.relative_to(ROOT.parent)): sha(f) for f in source_files},
              'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
              'endpoints': [], 'matched_path_stations': [], 'crossing': None, 'errors': []}
    def save():
        dest.write_text(json.dumps(result, indent=2) + '\n')
    save()
    for group, Ds in [('endpoints', P['endpoint_D_meV']), ('matched_path_stations', P['matched_path_D_meV'])]:
        for D in Ds:
            try:
                print('START', args.engine, group, D, flush=True)
                m = model(args.engine, P['N'], D)
                rr, accepted = roots(m, args.engine)
                station = {'D_meV': D, 'dimension': m.dim, 'roots': rr, 'roots_pass': accepted, 'trials': []}
                result[group].append(station)
                save()
                if not accepted:
                    result['errors'].append({'group': group, 'D_meV': D, 'error': 'root gate failed'})
                    save()
                    continue
                mon = Monitor(m, args.engine)
                station.update(affine_checks=mon.affine_checks, affine_spectrum_errors=mon.spectral_checks)
                for cfg in (P['endpoint_trials'] if group == 'endpoints' else P['matched_paths']):
                    start = time.time()
                    points = [np.array(x['f']) for x in rr]
                    row = trial(mon, points, cfg) if group == 'endpoints' else matched_trial(mon, points, cfg)
                    row['seconds'] = time.time() - start
                    if group == 'endpoints':
                        row['expected_label_pass'] = row['label'] == P['expected_endpoint_labels'][str(D)]
                    station['trials'].append(row)
                    save()
                    print('RESULT', args.engine, group, D, cfg['name'] if isinstance(cfg, dict) else cfg,
                          row['label'], 'pass', row['diagnostics_pass'], 'seconds', round(row['seconds'], 1), flush=True)
                mon.cache.clear()
            except Exception:
                error = {'group': group, 'D_meV': D, 'error': traceback.format_exc()}
                result['errors'].append(error)
                print(error['error'], flush=True)
                save()
    try:
        result['crossing'] = crossing(P['N'], args.engine)
        print('CROSSING', args.engine, result['crossing']['bracket_D_meV'], flush=True)
    except Exception:
        result['errors'].append({'group': 'crossing', 'error': traceback.format_exc()})
    rows = [r for group in ['endpoints', 'matched_path_stations'] for s in result[group] for r in s['trials']]
    passed = len(rows) == 12 and not result['errors'] and all(r['diagnostics_pass'] and r.get('expected_label_pass', True) for r in rows)
    result['status'] = 'N8_SEQUENCE_DIAGNOSTICS_PASS_NOT_FULL_BRAID_ACCEPTANCE' if passed else 'UNRESOLVED_CHECKS_RETAINED'
    save()
    print('STATUS', result['status'], flush=True)
    return 0 if passed else 1

if __name__ == '__main__':
    raise SystemExit(main())
