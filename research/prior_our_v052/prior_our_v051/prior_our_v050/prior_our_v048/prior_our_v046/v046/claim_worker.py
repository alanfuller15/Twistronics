"""Validate the recorded protocols, then run the two independent claim probes."""
import argparse,json,subprocess,sys
from pathlib import Path
from checkpoints import digest
from replay import frozen_protocol
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--only',choices=['endpoint_probe.py','sensitivity_probe.py']);args=parser.parse_args()
    plan=json.loads((ROOT/'PROBE_PLAN.json').read_text())
    if frozen_protocol()!=plan['primary_protocol_sha256']:raise ValueError('primary protocol changed')
    for path,h in plan['source_sha256'].items():
        if digest(ROOT/path)!=h:raise ValueError('probe source changed: '+path)
    for name in ([args.only] if args.only else ['endpoint_probe.py','sensitivity_probe.py']):
        subprocess.run([sys.executable,str(ROOT/name)],check=True,cwd=ROOT)
