#!/usr/bin/env python3
"""Reconstruct lossless logs and check retained evidence without physical calls."""
import argparse,gzip,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def sha(data):return hashlib.sha256(data).hexdigest()

def materialize(destination):
    manifest=json.loads((HERE/'MANIFEST.json').read_text())
    actual={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    if actual != set(manifest['files'])|{'MANIFEST.json'}:raise RuntimeError('PACKAGE_FILE_SET')
    for name,record in manifest['files'].items():
        data=(HERE/name).read_bytes()
        if len(data)!=record['bytes'] or sha(data)!=record['sha256']:raise RuntimeError('HASH:'+name)
    if destination.exists():raise RuntimeError('DESTINATION_EXISTS')
    destination.mkdir(parents=True)
    for q in ('q00','q01','q10','q11'):
        src=HERE/'HOSTED'/q; out=destination/q;out.mkdir()
        for name in ('RECEIPT.json','WORKER.log'):
            (out/name).write_bytes((src/name).read_bytes())
        parts=sorted(src.glob('ATTEMPTS.ndjson.gz.part*'))
        if [p.name for p in parts] != [f'ATTEMPTS.ndjson.gz.part{i:03d}' for i in range(len(parts))]:raise RuntimeError('PART_ORDER')
        raw=gzip.decompress(b''.join(p.read_bytes() for p in parts))
        receipt=json.loads((out/'RECEIPT.json').read_text())
        if len(raw)!=receipt['durable_bytes'] or sha(raw)!=receipt['log_sha256']:raise RuntimeError('RECONSTRUCTED_LOG')
        (out/'ATTEMPTS.ndjson').write_bytes(raw)
    for name in ('RESULTS.json','PARTITION.json'):
        (destination/name).write_bytes((HERE/'HOSTED'/name).read_bytes())
    sys.path.insert(0,str(ROOT/'research/benchmarks/parallel_domain_001'))
    import parallel
    result=parallel.verify(destination,manifest['implementation_commit'])
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('destination',type=Path)
    materialize(parser.parse_args().destination.resolve())
