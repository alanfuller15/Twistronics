"""Restore authorized audit evidence, check every byte and reproduce review/verification with zero physical eigensolves."""
import argparse,base64,hashlib,io,json,os,subprocess,sys,tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
here=Path(__file__).resolve().parent;root=here.parents[2];packet=here/'authorized-execution';m=json.loads((packet/'MANIFEST.json').read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
parts=[]
for item in m['parts']:
 b=base64.b64decode((packet/item['path']).read_bytes(),validate=True);assert sha(b)==item['decoded_sha256'];parts.append(b)
b=b''.join(parts);assert sha(b)==m['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz') as t:
 for member in t.getmembers():assert member.isfile() and (out/member.name).resolve().is_relative_to(out)
 t.extractall(out,filter='data')
assert {str(p.relative_to(out)) for p in out.rglob('*') if p.is_file()}==set(m['files'])
for name,item in m['files'].items():assert sha((out/name).read_bytes())==item['sha256'] and (out/name).stat().st_size==item['bytes'],name
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
subprocess.run([sys.executable,'-B',str(here/'verify_retained.py'),str(out)],check=True,env=env,timeout=300)
subprocess.run([sys.executable,'-B',str(here/'recompute.py'),'collect','--commit',m['reviewer_implementation_commit'],'--input',str(root/'research/benchmarks'),'--output',str(out)],check=True,env=env,timeout=300,stdout=subprocess.DEVNULL)
for name,item in m['files'].items():assert sha((out/name).read_bytes())==item['sha256'],name
print(json.dumps({'status':'ALL_BYTES_AND_REVIEW_REPLAY_MATCH','files':len(m['files']),'physical_eigensolves':0,'derived':['REVIEW.json','VERIFICATION.json']}))
