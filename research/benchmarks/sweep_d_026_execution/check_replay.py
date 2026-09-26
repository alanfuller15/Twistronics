"""Verify every retained byte against MANIFEST.json, then re-derive both batch MAPs and the combined
REGRESSION/SUMMARY with the frozen implementation (zero physical eigensolves); require byte equality.
Usage (repository root): OPENBLAS_NUM_THREADS=1 python research/benchmarks/sweep_d_026_execution/check_replay.py
"""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];RUN=ROOT/'research/benchmarks/sweep_d_026/run.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((HERE/'MANIFEST.json').read_text())
present={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file()}-{'MANIFEST.json','check_replay.py','README.md'}
assert present==set(m['files']),sorted(present^set(m['files']))
for name,item in m['files'].items():assert sha(HERE/name)==item['sha256'] and (HERE/name).stat().st_size==item['bytes'],name
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1');c=m['implementation_commit']
with tempfile.TemporaryDirectory() as t:
 out=Path(t)/'run';out.mkdir()
 for b in ('A','B'):
  shutil.copytree(HERE/b,out/b,ignore=shutil.ignore_patterns('MAP.json'))
  subprocess.run([sys.executable,'-B',str(RUN),'replay','--batch',b,'--commit',c,'--output',str(out/b)],check=True,env=env,timeout=1800)
  assert sha(out/b/'MAP.json')==sha(HERE/b/'MAP.json'),b
 subprocess.run([sys.executable,'-B',str(RUN),'combine','--commit',c,'--output',str(out)],check=True,env=env,timeout=900)
 for name in ('REGRESSION.json','SUMMARY.json'):assert sha(out/name)==sha(HERE/name),name
print(json.dumps({'status':'ALL_BYTES_AND_REPLAY_MATCH','implementation_commit':c,'files':len(m['files']),'derived':['A/MAP.json','B/MAP.json','REGRESSION.json','SUMMARY.json'],'physical_eigensolves':0}))
