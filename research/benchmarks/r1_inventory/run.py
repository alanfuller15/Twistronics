"""Continuous local interior inventory in both engines, with all failures retained."""
import json
import platform
import sys
import time
import traceback
import numpy as np
import scipy
from scipy.linalg import eigh
from inventory import ROOT, PLAN, T, COLUMNS, STATES, sha, primitives, core_capture, outer_guard, cover
from sources import load
sys.path.insert(0, str(ROOT.parent/'r1_holonomy'))
from measure import Family
from track import model

def main():
    dest = ROOT/'RESULTS.json'
    if dest.exists():
        raise SystemExit('Refusing overwrite of retained inventory')
    controls = json.loads((ROOT/'CONTROLS.json').read_text())
    assert controls['all_controls_pass'] and controls['plan_sha256'] == sha(ROOT/'PLAN.json')
    assert all(sha(ROOT/n) == h for n, h in controls['source_hashes'].items())
    tasks, source_hashes = load()
    source_hashes.update({str((ROOT/n).relative_to(ROOT.parent)): sha(ROOT/n) for n in ['PLAN.json', 'inventory.py', 'controls.py', 'CONTROLS.json', 'sources.py', 'run.py']})
    out = {'status': 'RUNNING', 'plan_sha256': sha(ROOT/'PLAN.json'), 'source_hashes': source_hashes,
           'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__, 'blas_threads': 1},
           'columns': COLUMNS, 'states': STATES, 'families': [], 'campaigns': [], 'errors': []}
    def save():
        dest.write_text(json.dumps(out, indent=2, allow_nan=False)+'\n')
    save()
    try:
        for engine in PLAN['engines']:
            family = Family(engine)
            out['families'].append({'engine': engine, 'dimension': family.dim, 'affine_checks': family.checks})
            for grid in PLAN['continuation_grids']:
                name = f'{engine.upper()}_{grid}.npz'; archive = ROOT/name
                if archive.exists():
                    raise RuntimeError('Refusing overwrite '+name)
                arrays = {}; campaign = {'engine': engine, 'grid': grid, 'arrays_file': name, 'references': []}
                out['campaigns'].append(campaign); started = time.perf_counter()
                for task in [t for t in tasks if t['engine'] == engine and t['grid'] == grid]:
                    p = primitives(family, task['raw'], task['frame'])
                    native_model = model(engine, PLAN['N'], p['D_meV'])
                    native = native_model.H(family.k(np.array(p['y'][:2])))
                    error = float(np.max(abs(family.U.conj().T @ native @ family.U-family.H([*p['y'][:2], p['D_meV']]))))
                    w = eigh(native, eigvals_only=True, subset_by_index=(p['lo']-1, p['lo']+3))
                    specerr = float(max(abs(w-p['w5'])))
                    native_ok = error < T['matrix_tolerance_meV'] and specerr < T['reconciliation_tolerance'] and p['complement_spectrum_error'] < T['reconciliation_tolerance']
                    radii = task['parent_certificate']['radii']; h = task['halfwidth']; R = task['outer_radii']
                    bridge = core_capture(p, radii, h); other = outer_guard(p, R, h)
                    rows, result = cover(p, R, radii[:2], h); arrays[task['key']] = rows
                    entry = {k: v for k, v in task.items() if k not in ['raw', 'frame']}
                    entry.update(primitives=p, native={'matrix_error_meV': error, 'spectrum_error_meV': specerr, 'w5': w.tolist(), 'pass': bool(native_ok)},
                                 core_energy_capture=bridge, other_gaps=other, cover=result,
                                 **{'pass': bool(native_ok and bridge['pass'] and other['pass'] and result['pass'])})
                    campaign['references'].append(entry)
                    np.savez_compressed(archive, **arrays); campaign['arrays_sha256'] = sha(archive); save()
                    print('REFERENCE', task['key'], 'rows', len(rows), 'unresolved', result['unresolved_leaves'], 'energy_capture', bridge['pass'], 'other_gaps', other['pass'], 'pass', entry['pass'], 'seconds', round(time.perf_counter()-started, 1), flush=True)
                campaign['pass'] = all(r['pass'] for r in campaign['references']); save()
        out['status'] = 'CONDITIONAL_SINGLE_NODE_INTERIOR_INVENTORY_PASS' if len(out['campaigns']) == 4 and all(c['pass'] for c in out['campaigns']) else 'UNRESOLVED_INTERIOR_REGIONS_RETAINED'
    except Exception:
        out['status'] = 'UNRESOLVED_INTERIOR_REGIONS_RETAINED'; out['errors'].append(traceback.format_exc())
        print(out['errors'][-1], flush=True)
    save(); print('STATUS', out['status'], flush=True)
    return 0 if out['status'] == 'CONDITIONAL_SINGLE_NODE_INTERIOR_INVENTORY_PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
