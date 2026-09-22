"""Read and bind existing evidence, without rerunning Hamiltonian calculations."""
import json
import numpy as np
from geometry import ROOT, PLAN, T, sha

def read_inputs():
    parent = ROOT.parent
    sources = {}
    def bind(path):
        sources[str(path.relative_to(parent))] = sha(path)
    def checked_json(path, source_root=None, source_key='source_hashes'):
        bind(path)
        data = json.loads(path.read_text())
        if source_root is not None:
            for name, expected in data[source_key].items():
                path = source_root/name
                assert sha(path) == expected, str(path)
                bind(path)
        return data
    cs = checked_json(parent/'r1_continuation/SUMMARY.json', parent/'r1_continuation')
    ss = checked_json(parent/'r1_surface/SUMMARY.json', parent/'r1_surface')
    ts = checked_json(parent/'r1_temporal/SUMMARY.json', parent/'r1_temporal')
    assert cs['all_checks_pass'] and ss['all_surface_checks_pass'] and ts['all_numerical_checks_pass']
    cont = checked_json(parent/'r1_continuation/RESULTS.json', parent)
    assert cont['status'] == 'CONDITIONAL_LOCAL_CONTINUATION_PASS'
    campaigns = {(c['engine'], c['initial_intervals']): c for c in cont['campaigns']}
    assert all(c['pass'] for c in campaigns.values())
    cases = []
    for engine in PLAN['engines']:
        surface = checked_json(parent/'r1_surface'/(engine.upper()+'.json'), parent)
        temporal = checked_json(parent/'r1_temporal'/(engine.upper()+'.json'), parent, 'sources')
        assert surface['status'] == 'FULL_DECLARED_SURFACE_ISOLATION_PASS_CONDITIONAL'
        assert temporal['status'] == 'GUARDED_TEMPORAL_GRID_AND_CONJUGATION_PASS_NOT_FULL_BRAID'
        assert sha(parent/'r1_temporal'/(engine.upper()+'.npz')) == temporal['arrays_sha256']
        for cfg in PLAN['mesh_levels']:
            for radius in PLAN['radii']:
                sc = next(c for c in surface['cases'] if c['mesh'] == cfg['name'] and c['radius'] == radius)
                assert sc['pass'] and sc['unresolved_leaves'] == 0
                archive = parent/'r1_surface'/sc['arrays_file']
                assert sha(archive) == sc['arrays_sha256']; bind(archive)
                with np.load(archive) as a:
                    faces = a['corners'].copy()
                count = cfg['polygon_edges']+2
                assert faces.shape == (cfg['track_intervals']*count, 2, 2, 3)
                stations = sorted([s for s in temporal['stations'] if s['mesh'] == cfg['name'] and s['radius'] == radius], key=lambda s: s['D_meV'])
                assert len(stations) == cfg['track_intervals']+1
                geometry = []
                for s in stations:
                    g = s['geometry']
                    vertices = np.array([g['base'], g['kink'], *g['ring']])
                    assert s['diagnostics_pass'] and s['charge']['accepted_label'] == '+k'
                    assert np.array_equal(vertices[2], vertices[-1])
                    geometry.append({'D_meV': s['D_meV'], 'vertices': vertices[:, :2].tolist()})
                maxerr = 0.
                for j in range(cfg['track_intervals']):
                    a, b = geometry[j:j+2]
                    for k in range(count):
                        expected = np.array([[[*a['vertices'][k], a['D_meV']], [*a['vertices'][k+1], a['D_meV']]],
                                             [[*b['vertices'][k], b['D_meV']], [*b['vertices'][k+1], b['D_meV']]]])
                        maxerr = max(maxerr, float(np.max(np.abs(expected-faces[j*count+k]))))
                assert maxerr <= T['geometry_reconstruction_tolerance']
                campaign = campaigns[(engine, cfg['track_intervals'])]
                paths = {}
                cuts = {g['D_meV'] for g in geometry}
                for name in PLAN['nodes']:
                    p = campaign['nodes'][name]
                    assert p['pass'] and all(x['pass'] for x in p['joins'])
                    leaves = [p['attempts'][i] for i in p['leaf_ids']]
                    assert all(c['certificate']['pass'] for c in leaves)
                    paths[name] = leaves
                    cuts.update(v for c in leaves for v in [c['a'], c['b']])
                cases.append({'engine': engine, 'mesh': cfg['name'], 'track_intervals': cfg['track_intervals'],
                              'polygon_edges': cfg['polygon_edges'], 'radius': radius, 'geometry': geometry,
                              'geometry_source_error': maxerr, 'common_partition': sorted(cuts), 'paths': paths,
                              'inherited_surface_case': sc['name'], 'inherited_surface_gap_lower_meV': sc['minimum_lower_meV'],
                              'inherited_loop_labels': [s['charge']['accepted_label'] for s in stations]})
    return cont, cases, sources

def cell_data(cont, case, a, b):
    mid = (a+b)/2
    geometry = case['geometry']
    j = next(j for j in range(len(geometry)-1) if geometry[j]['D_meV'] <= mid <= geometry[j+1]['D_meV'])
    left, right = geometry[j:j+2]
    assert a >= left['D_meV'] and b <= right['D_meV']
    vertices = []
    for D in [a, b]:
        t = (D-left['D_meV'])/(right['D_meV']-left['D_meV'])
        vertices.append((1-t)*np.array(left['vertices'])+t*np.array(right['vertices']))
    boxes = {}
    for name in PLAN['nodes']:
        cells = [c for c in case['paths'][name] if c['a'] <= mid <= c['b']]
        assert len(cells) == 1
        cell = cells[0]
        assert a >= cell['a'] and b <= cell['b']
        raw = cont['centers'][cell['center']]['raw']
        centers = [np.array(raw['y'][:2])+(D-raw['D_meV'])*np.array(raw['velocity'][:2]) for D in [a, b]]
        boxes[name] = {'centers': np.array(centers), 'radii': np.array(cell['certificate']['radii'][:2]),
                       'tube_id': cell['id'], 'center_key': cell['center']}
    return np.array(vertices), boxes, j
