"""Independent queue/ownership reconstruction and real-evidence negative controls."""
import copy
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPLAYS = Path(sys.argv[1]).resolve()


def children(c):
    d, x, y = c
    return [(d + 1, 2*x + dx, 2*y + dy) for dx in (0, 1) for dy in (0, 1)]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


reports = []
for batch in range(2, 7):
    folder = ROOT / f'research/benchmarks/parallel_domain_{batch:03}'
    p = load(folder / 'parallel.py', f'audit_parallel_{batch}')
    spec = p.spec_and_bindings()
    predecessor_path = (ROOT / 'research/benchmarks/parallel_domain_001_execution/HOSTED/PARTITION.json'
                        if batch == 2 else REPLAYS / f'replay{batch-1:03}/PARTITION.json')
    predecessor = json.loads(predecessor_path.read_text())
    actual = json.loads((REPLAYS / f'replay{batch:03}/PARTITION.json').read_text())
    hosts = spec.get('hosts', 1)
    expected = {}
    for q in ('q00', 'q01', 'q10', 'q11'):
        merged = {k: [tuple(c) for s, v in predecessor.items() if s[:3] == q for c in v[k]]
                  for k in ('accepted', 'unresolved', 'frontier')}
        if batch == 6:
            assert not merged['frontier'] and all(c[0] == 9 for c in merged['unresolved'])
            jobs = sorted(ch for c in merged['unresolved'] for ch in children(c))
        else:
            jobs = sorted(merged['frontier'])
        for h in range(hosts):
            name = q if batch == 2 else f'{q}h{h}'
            state = {'accepted': merged['accepted'][:] if h == 0 else [],
                     'unresolved': merged['unresolved'][:] if h == 0 and batch != 6 else [],
                     'frontier': jobs[h::hosts]}
            producer = p.initial(name) if batch == 2 else p.initial(name, spec)
            assert {k: sorted(v) for k, v in producer.items()} == {k: sorted(v) for k, v in state.items()}
            expected[name] = state
    first = None
    attempts = 0
    clocks = []
    for shard, state in expected.items():
        path = REPLAYS / f'replay{batch:03}' / shard
        receipt = json.loads((path / 'RECEIPT.json').read_text())
        exact = (receipt['soft_deadline'] == receipt['start'] + spec['worker_wall_seconds']
                 and receipt['hard_deadline'] == receipt['start'] + spec['worker_wall_seconds'] + spec['grace_seconds'])
        assert exact
        clocks.append({'shard': shard, 'exact_supervisor_expressions': exact,
                       'soft_difference': receipt['soft_deadline'] - receipt['start'],
                       'hard_difference': receipt['hard_deadline'] - receipt['soft_deadline'],
                       'elapsed': receipt['reaped'] - receipt['start'],
                       'termination': receipt['termination_reason']})
        with (path / 'ATTEMPTS.ndjson').open() as stream:
            header = json.loads(next(stream))
            assert header['test_mode'] is False
            for line in stream:
                r = json.loads(line)
                c = tuple(r['cell'][key] for key in ('depth', 'ix', 'iy'))
                assert c == min(state['frontier'])
                state['frontier'].remove(c)
                if r['outcome'] == p.ACCEPT:
                    state['accepted'].append(c)
                    if first is None:
                        first = r
                else:
                    assert r['outcome'] == 'INCONCLUSIVE'
                    if c[0] == spec['max_depth']:
                        state['unresolved'].append(c)
                    else:
                        assert c[0] < spec['max_depth']
                        state['frontier'].extend(children(c))
                attempts += 1
        assert {k: sorted(v) for k, v in state.items()} == {k: sorted(map(tuple, v)) for k, v in actual[shard].items()}
    # Compare complete full-square geometry independently of the producer raster.
    depth = spec['max_depth']
    side = 2**depth
    occupancy = bytearray(side * side)
    for state in expected.values():
        for cells in state.values():
            for d, x, y in cells:
                assert 0 <= x < 2**d and 0 <= y < 2**d
                scale = 2**(depth-d)
                for xx in range(x*scale, (x+1)*scale):
                    start = xx*side + y*scale
                    assert not any(occupancy[start:start+scale])
                    occupancy[start:start+scale] = b'\1' * scale
    assert all(occupancy)
    old = p.load(p.OLD / 'verify.py', f'audit_evidence_{batch}')
    c = tuple(first['cell'][k] for k in ('depth', 'ix', 'iy'))
    original = first['full_interval_evidence']
    assert p.strict_evidence(original, p.ACCEPT, spec, c, old) == (4, 4)
    mutations = []
    for kind in ('dimension', 'cell_box', 'width', 'gram', 'pivot', 'missing_recomputation', 'shift', 'inertia'):
        evidence = copy.deepcopy(original)
        if kind == 'dimension': evidence['dimension'] = 197
        if kind == 'cell_box': evidence['cell']['x'][0] = '-1'
        if kind == 'width': evidence['window_definitions']['upper']['width_meV'] = '0'
        if kind == 'gram': evidence['primary']['gram_margins'][0] = ['-1', '1']
        if kind == 'pivot': evidence['primary']['windows']['upper']['endpoints'][0]['pivots'][0] = ['-1', '1']
        if kind == 'missing_recomputation': evidence['recomputation'] = None
        if kind == 'shift': evidence['recomputation']['windows']['upper']['endpoints'][0]['shift'] = '1000'
        if kind == 'inertia': evidence['primary']['windows']['upper']['endpoints'][0]['negative'] = 0
        try:
            p.strict_evidence(evidence, p.ACCEPT, spec, c, old)
        except (RuntimeError, ValueError, KeyError, TypeError) as error:
            mutations.append({'mutation': kind, 'rejected': True, 'reason': str(error)})
        else:
            raise AssertionError(f'{batch}: accepted mutation {kind}')
    report = {'batch': batch, 'status': 'PASS', 'independently_replayed_attempts': attempts,
              'exact_shard_assignment_and_queue': True, 'descendants_remain_with_owner': True,
              'inherited_cells_only_on_slot_zero': True,
              'complete_disjoint_full_square': True,
              'accepted_area': str(sum((Fraction(1, 4**c[0]) for s in expected.values() for c in s['accepted']), Fraction())),
              'real_evidence_negative_controls': mutations, 'clocks': clocks}
    reports.append(report)
    print(json.dumps({'batch': batch, 'status': 'PASS', 'attempts': attempts}), flush=True)
(HERE / 'INDEPENDENT_RECORD_AUDIT.json').write_text(json.dumps(reports, indent=2) + '\n')
