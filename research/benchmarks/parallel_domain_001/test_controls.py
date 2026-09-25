#!/usr/bin/env python3
"""Synthetic process controls and adversarial partition/replay checks."""
import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import parallel as p


def rejected(fn):
    try:
        fn()
    except (RuntimeError, ValueError):
        return
    raise AssertionError('fault was accepted')


def main():
    states = {q: p.initial(q) for q in p.QUADRANTS}
    p.validate_partition(states)
    assert sum((p.area(s['accepted']) for s in states.values()), p.Fraction()) == p.Fraction(29663,262144)
    fault = copy.deepcopy(states); fault['q00']['frontier'].append(fault['q00']['frontier'][0])
    rejected(lambda: p.validate_partition(fault))
    fault = copy.deepcopy(states); fault['q00']['frontier'].pop()
    rejected(lambda: p.validate_partition(fault))
    fault = copy.deepcopy(states); fault['q00']['frontier'][0] = (4,8,0)
    rejected(lambda: p.validate_partition(fault))
    fault = copy.deepcopy(states); fault['q00']['frontier'].append((3,0,0))
    rejected(lambda: p.validate_partition(fault))
    with tempfile.TemporaryDirectory(prefix='parallel-controls-') as tmp:
        args = SimpleNamespace(output=Path(tmp)/'normal', synthetic=True,
            fault='none', implementation_commit='synthetic-control', wheel=None, review_receipt=None)
        normal = p.supervise(args)
        assert all(q['attempts'] == 64 for q in normal['quadrants'].values())
        assert normal['test_mode'] and normal['status'] == 'SYNTHETIC_CONTROLS_ONLY'
        p.verify(args.output, args.implementation_commit, True)
        raw_path = args.output/'q00/ATTEMPTS.ndjson'
        raw = raw_path.read_bytes()
        # A complete malformed/hash-invalid record must fail, even after rebinding receipt.
        raw_path.write_bytes(raw+b'{"kind":"attempt"}\n')
        receipt = args.output/'q00/RECEIPT.json'
        original = receipt.read_bytes()
        r = json.loads(original); r['log_sha256'] = p.durable.sha256_file(raw_path)
        r['raw_bytes'] = r['durable_bytes'] = raw_path.stat().st_size
        receipt.write_text(json.dumps(r))
        rejected(lambda: p.verify(args.output, args.implementation_commit, True))
        raw_path.write_bytes(raw); receipt.write_bytes(original)
        # Physical replay cannot accept synthetic evidence.
        rejected(lambda: p.verify(args.output, args.implementation_commit, False))
        # Wrong source identity cannot replay the same log.
        rejected(lambda: p.verify(args.output, 'wrong-commit', True))
        args.output = Path(tmp)/'killed'; args.fault = 'partial'
        killed = p.supervise(args)
        assert all(q['attempts'] == 0 and q['termination_reason'] == 'WATCHDOG_TIMEOUT'
                   for q in killed['quadrants'].values())
        assert killed['accepted_fraction_of_full_domain'] == '29663/262144'
        for q in p.QUADRANTS:
            r = json.loads((args.output/q/'RECEIPT.json').read_text())
            assert r['group_empty'] and r['exit_code'] == -9 and r['raw_bytes'] > r['durable_bytes']
        p.verify(args.output, args.implementation_commit, True)
    print(json.dumps({'status':'PASS','controls':[
        'baseline exact full-domain partition', 'duplicate rejected', 'gap rejected',
        'wrong quadrant rejected', 'ancestor overlap rejected',
        'four concurrent normal workers and 256 synthetic attempts',
        'read-only deterministic replay', 'complete corrupt line rejected',
        'synthetic forbidden in physical replay', 'wrong commit rejected',
        'four real SIGKILL partial-log recoveries', 'unchanged accepted area after interruption'],
        'physical_calls':0}, indent=2))


if __name__ == '__main__':
    main()
