#!/usr/bin/env python3
"""Reconstruct lossless batch-002 logs and replay them without physical calls.

Replay runs replay_002.py: the unchanged parallel_domain_002 verifier with one
Alan-authorized tolerance fix for float deadline arithmetic (see README.md).
"""
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMPLEMENTATION = '7494c36022f163a427df2e513e57e534cb84c885'


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
    for q in ('q00', 'q01', 'q10', 'q11'):
        src = HERE / 'HOSTED' / q
        out = destination / q
        out.mkdir()
        for name in ('RECEIPT.json', 'WORKER.log'):
            (out / name).write_bytes((src / name).read_bytes())
        parts = sorted(src.glob('ATTEMPTS.ndjson.gz.part*'))
        if [p.name for p in parts] != [f'ATTEMPTS.ndjson.gz.part{i:03d}' for i in range(len(parts))]:
            raise RuntimeError('PART_ORDER')
        raw = gzip.decompress(b''.join(p.read_bytes() for p in parts))
        receipt = json.loads((out / 'RECEIPT.json').read_text())
        if len(raw) != receipt['durable_bytes'] or sha(raw) != receipt['log_sha256']:
            raise RuntimeError('RECONSTRUCTED_LOG')
        (out / 'ATTEMPTS.ndjson').write_bytes(raw)
    for name in ('RESULTS.json', 'PARTITION.json'):
        (destination / name).write_bytes((HERE / 'HOSTED' / name).read_bytes())
    return subprocess.run([sys.executable, '-B', str(HERE / 'replay_002.py'), 'verify',
                           '--output', str(destination), '--implementation-commit',
                           IMPLEMENTATION], check=False).returncode


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=Path)
    raise SystemExit(materialize(parser.parse_args().destination.resolve()))
