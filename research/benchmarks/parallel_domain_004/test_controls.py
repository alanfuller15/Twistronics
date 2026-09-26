#!/usr/bin/env python3
"""Synthetic shard, merge and adversarial partition/replay checks for packet 004."""
import copy
import json
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace

import parallel as p


def rejected(fn):
    try:
        fn()
    except (RuntimeError, ValueError, KeyError):
        return
    raise AssertionError('fault was accepted')


def main():
    spec = p.spec_and_bindings()
    shards = p.shard_names(spec)
    states = {s: p.initial(s, spec) for s in shards}
    predecessor = {q: p.predecessor_quadrant(q) for q in p.QUADRANTS}

    # Ownership: shards reproduce the predecessor partition exactly, with no cell twice.
    for q in p.QUADRANTS:
        for key in ('accepted', 'unresolved', 'frontier'):
            union = sorted(c for s in shards if s.startswith(q) for c in states[s][key])
            assert union == sorted(tuple(c) for c in predecessor[q][key]), (q, key)
    p.validate_partition(states, spec)
    counts = [len(states[s]['frontier']) for s in shards]
    assert max(counts) - min(counts) <= max(len(predecessor[q]['frontier']) for q in p.QUADRANTS)

    fault = copy.deepcopy(states); fault['q11h1']['frontier'].append(fault['q11h0']['frontier'][0])
    rejected(lambda: p.validate_partition(fault, spec))
    fault = copy.deepcopy(states); fault['q11h1']['frontier'].pop()
    rejected(lambda: p.validate_partition(fault, spec))
    fault = copy.deepcopy(states); fault['q00h0']['frontier'][0] = (4, 15, 15)
    rejected(lambda: p.validate_partition(fault, spec))
    fault = copy.deepcopy(states); del fault['q11h1']
    rejected(lambda: p.validate_partition(fault, spec))

    with tempfile.TemporaryDirectory(prefix='parallel003-controls-') as tmp:
        tmp = Path(tmp)
        host_results = []
        for h in range(spec['hosts']):
            args = SimpleNamespace(output=tmp / f'host{h}', synthetic=True, fault='none',
                                   implementation_commit='synthetic-control', wheel=None, host=h)
            host_results.append(p.supervise(args))
            assert host_results[-1]['status'] == 'HOST_SHARDS_REPLAYED_MERGE_REQUIRED'
            assert all(s['attempts'] <= spec['max_attempts_per_worker'] for s in host_results[-1]['shards'].values())
            p.verify(args.output, args.implementation_commit, True, host=h)
        # Merge: shard directories from every host into one tree, then full replay.
        merged = tmp / 'merged'
        merged.mkdir()
        for h in range(spec['hosts']):
            for s in p.shard_names(spec, h):
                shutil.copytree(tmp / f'host{h}' / s, merged / s)
        result = p.verify(merged, 'synthetic-control', True, write=True)
        assert result['status'] == 'SYNTHETIC_CONTROLS_ONLY' and result['complete_disjoint_accounting']
        p.verify(merged, 'synthetic-control', True)
        # A missing host shard blocks the merge.
        broken = tmp / 'broken'
        shutil.copytree(merged, broken)
        shutil.rmtree(broken / 'q11h1')
        rejected(lambda: p.verify(broken, 'synthetic-control', True))
        # A shard attributed to the wrong host cannot replay.
        swapped = tmp / 'swapped'
        shutil.copytree(merged, swapped)
        shutil.rmtree(swapped / 'q11h1')
        shutil.copytree(merged / 'q11h0', swapped / 'q11h1')
        rejected(lambda: p.verify(swapped, 'synthetic-control', True))
        # Physical replay rejects synthetic evidence; wrong commit rejected.
        rejected(lambda: p.verify(tmp / 'host0', 'synthetic-control', False, host=0))
        rejected(lambda: p.verify(tmp / 'host0', 'wrong-commit', True, host=0))
        # Real SIGKILL partial-log recovery on one host.
        killed = SimpleNamespace(output=tmp / 'killed', synthetic=True, fault='partial',
                                 implementation_commit='synthetic-control', wheel=None, host=1)
        kr = p.supervise(killed)
        busy = [s for s in p.shard_names(spec, 1) if p.initial(s, spec)['frontier']]
        assert busy, 'SIGKILL control needs a shard with work'
        assert all(kr['shards'][s]['attempts'] == 0 and kr['shards'][s]['termination_reason'] == 'WATCHDOG_TIMEOUT'
                   for s in busy)
        assert all(kr['shards'][s]['attempts'] == 0 and kr['shards'][s]['termination_reason'] == 'NORMAL_EXIT'
                   for s in p.shard_names(spec, 1) if s not in busy)
    print(json.dumps({'status': 'PASS', 'controls': [
        'shard union equals predecessor partition exactly', 'full-square raster over all shards',
        'duplicate across hosts rejected', 'gap rejected', 'wrong quadrant rejected',
        'missing shard rejected', 'per-host synthetic runs and per-host replay',
        'merged multi-host replay', 'missing host shard blocks merge',
        'shard swapped between hosts rejected', 'synthetic forbidden in physical replay',
        'wrong commit rejected', 'real SIGKILL partial-log recovery'],
        'physical_calls': 0}, indent=2))


if __name__ == '__main__':
    main()
