"""Frozen geometric attachment run; retain failed bounds and their subdivisions."""
import json
import platform
import traceback
import numpy as np
from geometry import ROOT, PLAN, T, sha, evaluate
from inputs import read_inputs, cell_data

def main():
    dest = ROOT/'RESULTS.json'
    if dest.exists():
        raise SystemExit('Refusing overwrite of retained results')
    controls = json.loads((ROOT/'CONTROLS.json').read_text())
    assert controls['all_controls_pass'] and controls['plan_sha256'] == sha(ROOT/'PLAN.json')
    assert all(sha(ROOT/n) == h for n, h in controls['source_hashes'].items())
    cont, cases, sources = read_inputs()
    sources.update({str((ROOT/n).relative_to(ROOT.parent)): sha(ROOT/n) for n in ['PLAN.json', 'geometry.py', 'inputs.py', 'controls.py', 'CONTROLS.json', 'run.py']})
    out = {'status': 'RUNNING', 'plan_sha256': sha(ROOT/'PLAN.json'), 'source_hashes': sources,
           'runtime': {'python': platform.python_version(), 'numpy': np.__version__}, 'cases': [], 'errors': [],
           'new_hamiltonian_evaluations': 0, 'new_charge_measurements': 0}
    def save():
        dest.write_text(json.dumps(out, indent=2, allow_nan=False)+'\n')
    save()
    try:
        for case in cases:
            record = {k: v for k, v in case.items() if k not in ['paths', 'geometry']}
            record.update(attempts=[], leaf_ids=[])
            out['cases'].append(record)
            def visit(a, b, depth, parent=None):
                vertices, boxes, station = cell_data(cont, case, a, b)
                bound = evaluate(vertices, boxes)
                idx = len(record['attempts'])
                entry = {'id': idx, 'parent': parent, 'a': a, 'b': b, 'depth': depth, 'contour_interval': station,
                         'node_tubes': {n: {'tube_id': x['tube_id'], 'center_key': x['center_key']} for n, x in boxes.items()},
                         'bound': bound, 'children': []}
                record['attempts'].append(entry)
                if bound['pass'] or depth >= T['maximum_depth']:
                    record['leaf_ids'].append(idx)
                    entry['state'] = 'accepted' if bound['pass'] else 'unresolved_depth_limit'
                else:
                    entry['state'] = 'split'
                    m = (a+b)/2
                    entry['children'] = [visit(a, m, depth+1, idx), visit(m, b, depth+1, idx)]
                return idx
            for a, b in zip(case['common_partition'][:-1], case['common_partition'][1:]):
                visit(a, b, 0)
            leaves = [record['attempts'][i] for i in record['leaf_ids']]
            record['pass'] = all(x['bound']['pass'] for x in leaves)
            record['unresolved_leaves'] = sum(not x['bound']['pass'] for x in leaves)
            record['geometric_winding_if_pass'] = {'p': 0, 'q': 1, 'upper': 0} if record['pass'] else None
            save()
            print('CASE', case['engine'], case['mesh'], case['radius'], 'attempts', len(record['attempts']), 'leaves', len(leaves), 'unresolved', record['unresolved_leaves'], 'pass', record['pass'], flush=True)
        out['status'] = 'CONDITIONAL_TRACKED_NODE_CONTOUR_ATTACHMENT_PASS' if len(out['cases']) == 8 and all(c['pass'] for c in out['cases']) else 'UNRESOLVED_GEOMETRY_RETAINED'
    except Exception:
        out['status'] = 'UNRESOLVED_GEOMETRY_RETAINED'
        out['errors'].append(traceback.format_exc())
        print(out['errors'][-1], flush=True)
    save()
    print('STATUS', out['status'], flush=True)
    return 0 if out['status'] == 'CONDITIONAL_TRACKED_NODE_CONTOUR_ATTACHMENT_PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
