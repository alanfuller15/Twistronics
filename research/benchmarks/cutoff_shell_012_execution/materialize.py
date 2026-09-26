"""Restore original evidence including failure; run the separately bound stable verifier."""
import argparse,base64,hashlib,io,json,os,subprocess,sys,tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--repo',type=Path,required=True);a=p.parse_args();here=Path(__file__).resolve().parent;m=json.loads((here/'MANIFEST.json').read_text());out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
parts=[]
for entry in m['parts']:
 data=base64.b64decode((here/entry['path']).read_bytes(),validate=True);assert hashlib.sha256(data).hexdigest()==entry['decoded_sha256'];parts.append(data)
raw=b''.join(parts);assert hashlib.sha256(raw).hexdigest()==m['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:
 for member in t.getmembers():assert member.isfile() and (out/member.name).resolve().is_relative_to(out)
 t.extractall(out,filter='data')
assert {str(p.relative_to(out)) for p in out.rglob('*') if p.is_file()}==set(m['files'])
for name,item in m['files'].items():
 data=(out/name).read_bytes();assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
expected={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['MAP.json','REGRESSION.json','SUMMARY.json','LEGACY_DISTANCE_CHECKS.json','REPLAY.json']}
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
subprocess.run([sys.executable,'-B',str(a.repo.resolve()/'research/benchmarks/cutoff_shell_012/replay_stable.py'),'replay','--commit',m['implementation_commit'],'--verification-commit',m['verification_commit'],'--output',str(out)],check=True,env=env,timeout=90)
for name,h in expected.items():assert hashlib.sha256((out/name).read_bytes()).hexdigest()==h,name
print(json.dumps({'status':'ALL_BYTES_AND_ADDITIVE_REPLAY_MATCH','implementation_commit':m['implementation_commit'],'verification_commit':m['verification_commit'],'files':len(m['files']),'derived_json':'BYTE_IDENTICAL','physical_eigensolves':0,'original_failed_replay':'PRESERVED'}))
