"""Verify every retained byte against MANIFEST.json, then re-derive MAP/REGRESSION/HOLONOMY/SUMMARY with
the frozen implementation's replay (zero physical eigensolves) in a scratch copy and require byte equality.

Usage (repository root, frozen commit object available):
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/loop_lower_014_execution/check_replay.py
"""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((HERE/'MANIFEST.json').read_text())
present={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file()}-{'MANIFEST.json','check_replay.py','README.md'}
assert present==set(m['files']),sorted(present^set(m['files']))
for name,item in m['files'].items():assert sha(HERE/name)==item['sha256'] and (HERE/name).stat().st_size==item['bytes'],name
derived=['MAP.json','REGRESSION.json','HOLONOMY.json','SUMMARY.json']
with tempfile.TemporaryDirectory() as t:
 out=Path(t)/'run';out.mkdir()
 for p in HERE.iterdir():
  if p.is_dir():shutil.copytree(p,out/p.name)
 shutil.copy(HERE/'BATCH.json',out/'BATCH.json')
 env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
 subprocess.run([sys.executable,'-B',str(ROOT/'research/benchmarks/loop_lower_014/run.py'),'replay','--commit',m['implementation_commit'],'--output',str(out)],check=True,env=env,timeout=900)
 for name in derived:assert sha(out/name)==sha(HERE/name),name
print(json.dumps({'status':'ALL_BYTES_AND_REPLAY_MATCH','implementation_commit':m['implementation_commit'],'files':len(m['files']),'derived':derived,'physical_eigensolves':0}))
