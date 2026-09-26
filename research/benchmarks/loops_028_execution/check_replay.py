"""Verify retained bytes, re-derive L/MAP.json and SUMMARY.json with the frozen implementation (zero solves).
Usage (repository root): OPENBLAS_NUM_THREADS=1 python research/benchmarks/loops_028_execution/check_replay.py
"""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];RUN=ROOT/'research/benchmarks/loops_028/run.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((HERE/'MANIFEST.json').read_text())
present={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file()}-{'MANIFEST.json','check_replay.py','README.md'}
assert present==set(m['files']),sorted(present^set(m['files']))
for name,item in m['files'].items():assert sha(HERE/name)==item['sha256'],name
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1');c=m['implementation_commit']
with tempfile.TemporaryDirectory() as t:
 out=Path(t)/'run';out.mkdir();shutil.copytree(HERE/'L',out/'L',ignore=shutil.ignore_patterns('MAP.json'))
 subprocess.run([sys.executable,'-B',str(RUN),'replay','--batch','L','--commit',c,'--output',str(out/'L')],check=True,env=env,timeout=900)
 subprocess.run([sys.executable,'-B',str(RUN),'combine','--commit',c,'--output',str(out)],check=True,env=env,timeout=900)
 for name in ('L/MAP.json','SUMMARY.json'):assert sha(out/name)==sha(HERE/name),name
print(json.dumps({'status':'ALL_BYTES_AND_REPLAY_MATCH','implementation_commit':c,'files':len(m['files']),'physical_eigensolves':0}))
