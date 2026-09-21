"""Fresh v053 route replay with forbidden legacy surfaces instrumented to fail."""
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import time
from replay_prep import run
from protocol import frozen_protocol
from checkpoints import save_json
import bm_strain
import euler
import braid
import knobs
import tbg_ref

ROOT = Path(__file__).resolve().parent


def legacy_surfaces():
    surfaces = [(bm_strain.BM, n) for n in ('refine', 'find_nodes', 'min_remote')]
    surfaces += [(euler, n) for n in ('real_frame', 'euler')]
    surfaces += [(braid, n) for n in ('real_frame', 'node_winding', 'transport', 'adjacent_nodes')]
    surfaces += [(knobs, 'analyse'), (tbg_ref.TBG, 'refine')]
    return surfaces


def forbidden_surface_names():
    return {obj.__name__ + '.' + name for obj, name in legacy_surfaces()}


@contextmanager
def forbid_legacy_calls():
    surfaces = legacy_surfaces()
    calls, originals = {}, []
    for obj, name in surfaces:
        key = obj.__name__ + '.' + name
        calls[key] = 0
        originals.append((obj, name, getattr(obj, name)))
        def forbidden(*args, _key=key, **kwargs):
            calls[_key] += 1
            raise RuntimeError('forbidden legacy measurement surface reached: ' + _key)
        setattr(obj, name, forbidden)
    try:
        yield calls
    finally:
        for obj, name, original in originals:
            setattr(obj, name, original)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--engine', choices=['bm_lab', 'ref_lab'], required=True)
    parser.add_argument('--N', type=int, choices=[4, 6], required=True)
    args = parser.parse_args()
    folder = ROOT / 'results' / f'prep_{args.engine}_N{args.N}'
    if folder.exists():
        raise ValueError('fresh impact replay refuses existing case; preserve it and use a separate copy')
    protocol = frozen_protocol()
    start = time.time()
    with forbid_legacy_calls() as calls:
        try:
            result = run(args.engine, args.N)
            if result['status'] != 'ACCEPT' or any(calls.values()):
                raise ValueError('impact replay did not qualify')
            guard = dict(status='ACCEPT', engine=args.engine, N=args.N, protocol_sha256=protocol,
                states=result['completed'], fresh_start=True, forbidden_calls=calls,
                scope='Dynamic call exclusion for this complete preparation route only', seconds=time.time()-start)
        except Exception as error:
            folder.mkdir(parents=True, exist_ok=True)
            save_json(folder / 'guard_failure.json', dict(status='REJECTED', forbidden_calls=calls, error=repr(error)))
            raise
    save_json(folder / 'guard_summary.json', guard)
    print(json.dumps(guard, indent=2))


if __name__ == '__main__':
    main()
