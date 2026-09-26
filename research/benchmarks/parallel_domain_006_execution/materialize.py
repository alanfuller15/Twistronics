#!/usr/bin/env python3
"""Rebuild all eight slots' lossless shard logs and replay the merged batch-006 result.

No physical evaluations are performed. The replay is parallel_domain_006's own
merged verifier over all thirty-two shards (full-square 1024x1024 occupancy raster).
"""
import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IMPLEMENTATION = '9cfa9129de73c25ce6d5c3f7bf18919836bffbba'
SHARDS = {f'{q}h{h}': f'slot{h}' for h in range(8) for q in ('q00', 'q01', 'q10', 'q11')}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def materialize(destination):
    manifest = json.loads((HERE / 'MANIFEST.json').read_text())
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts}
    if actual != set(manifest['files']) | {'MANIFEST.json'}:
        raise RuntimeError('PACKAGE_FILE_SET')
    for name, record in manifest['files'].items():
        data = (HERE / name).read_bytes()
        if len(data) != record['bytes'] or sha(data) != record['sha256']:
            raise RuntimeError('HASH:' + name)
    if destination.exists():
        raise RuntimeError('DESTINATION_EXISTS')
    destination.mkdir(parents=True)
    for shard, host in SHARDS.items():
        src = HERE / host / shard
        out = destination / shard
        out.mkdir()
        for name in ('RECEIPT.json', 'WORKER.log'):
            (out / name).write_bytes((src / name).read_bytes())
        parts = sorted(src.glob('ATTEMPTS.ndjson.gz.part*'))
        if [p.name for p in parts] != [f'ATTEMPTS.ndjson.gz.part{i:03d}' for i in range(len(parts))]:
            raise RuntimeError('PART_ORDER:' + shard)
        raw = gzip.decompress(b''.join(p.read_bytes() for p in parts))
        receipt = json.loads((out / 'RECEIPT.json').read_text())
        if len(raw) != receipt['durable_bytes'] or sha(raw) != receipt['log_sha256']:
            raise RuntimeError('RECONSTRUCTED_LOG:' + shard)
        (out / 'ATTEMPTS.ndjson').write_bytes(raw)
    for name in ('RESULTS.json', 'PARTITION.json'):
        (destination / name).write_bytes((HERE / name).read_bytes())
    sys.path.insert(0, str(ROOT / 'research/benchmarks/parallel_domain_006'))
    import parallel
    print(json.dumps(parallel.verify(destination, IMPLEMENTATION), sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=Path)
    materialize(parser.parse_args().destination.resolve())
