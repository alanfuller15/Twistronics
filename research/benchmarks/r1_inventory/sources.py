"""Source-bound domains enclosing both meshes and both contour radii."""
import json
import sys
import numpy as np
from inventory import ROOT, PLAN, T, sha
sys.path.insert(0, str(ROOT.parent/'r1_attachment'))
from inputs import read_inputs as read_attachment_inputs

def load():
    attachment = json.loads((ROOT.parent/'r1_attachment/SUMMARY.json').read_text())
    assert attachment['all_checks_pass']
    sources = {}
    for name, expected in attachment['source_hashes'].items():
        path = ROOT.parent/'r1_attachment'/name
        assert sha(path) == expected
        sources[str(path.relative_to(ROOT.parent))] = expected
    ar = json.loads((ROOT.parent/'r1_attachment/RESULTS.json').read_text())
    assert ar['status'] == 'CONDITIONAL_TRACKED_NODE_CONTOUR_ATTACHMENT_PASS'
    for name, expected in ar['source_hashes'].items():
        assert sha(ROOT.parent/name) == expected
        sources[name] = expected
    cont, cases, inherited = read_attachment_inputs(); sources.update(inherited)
    sources['r1_attachment/SUMMARY.json'] = sha(ROOT.parent/'r1_attachment/SUMMARY.json')
    frames = np.load(ROOT.parent/'r1_continuation/FRAMES.npz')
    tasks = []
    for engine in PLAN['engines']:
        for grid in PLAN['continuation_grids']:
            campaign = next(c for c in cont['campaigns'] if c['engine'] == engine and c['initial_intervals'] == grid)
            assert campaign['pass']
            path = campaign['nodes']['q']; assert path['pass']
            for i in path['leaf_ids']:
                tube = path['attempts'][i]; raw = cont['centers'][tube['center']]['raw']
                assert tube['certificate']['pass'] and tube['certificate']['beta'] < 1
                a, b = tube['a'], tube['b']; c0 = np.array(raw['y'][:2]); v = np.array(raw['velocity'][:2]); D0 = raw['D_meV']
                samples = []; maximum = np.zeros(2); clipped = 0
                for case in cases:
                    if case['engine'] != engine:
                        continue
                    for left, right in zip(case['geometry'][:-1], case['geometry'][1:]):
                        start, end = max(a, left['D_meV']), min(b, right['D_meV'])
                        if start >= end:
                            continue
                        clipped += 1
                        for D in [start, end]:
                            t = (D-left['D_meV'])/(right['D_meV']-left['D_meV'])
                            ring = (1-t)*np.array(left['vertices'][2:-1])+t*np.array(right['vertices'][2:-1])
                            offset = ring-(c0+(D-D0)*v)
                            extent = np.max(abs(offset), axis=0); maximum = np.maximum(maximum, extent)
                            samples.append({'mesh': case['mesh'], 'radius': case['radius'], 'D_meV': D, 'maximum_absolute_offset': extent.tolist()})
                R = maximum+T['geometry_padding']
                assert np.all(R > np.array(tube['certificate']['radii'][:2]))
                tasks.append({'key': f'{engine}_{grid}_{i}', 'engine': engine, 'grid': grid, 'tube_id': i,
                              'a': a, 'b': b, 'halfwidth': (b-a)/2, 'center_key': tube['center'],
                              'raw': raw, 'frame': frames[tube['center']], 'parent_certificate': tube['certificate'],
                              'outer_radii': R.tolist(), 'containment_endpoints': samples, 'clipped_contour_intervals': clipped})
    return tasks, sources
