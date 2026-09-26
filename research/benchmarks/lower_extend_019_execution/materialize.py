"""Restore all retained spectra/vectors and receipts; replay with zero eigensolves and compare every derived byte."""
import argparse,base64,gzip,hashlib,io,json,os,subprocess,sys,tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--repo',type=Path,required=True);a=p.parse_args();here=Path(__file__).resolve().parent;m=json.loads((here/'MANIFEST.json').read_text());assert not a.output.exists();a.output.mkdir(parents=True)
def sha(b):return hashlib.sha256(b).hexdigest()
parts=[]
for item in m['parts']:
 b=base64.b64decode((here/item['path']).read_bytes(),validate=True);assert sha(b)==item['decoded_sha256'];parts.append(b)
b=b''.join(parts);assert sha(b)==m['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz') as t:
 for i in t.getmembers():assert i.isfile() and (a.output/i.name).resolve().is_relative_to(a.output.resolve())
 t.extractall(a.output,filter='data')
for n,h in m['files'].items():assert sha((a.output/n).read_bytes())==h['sha256']
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
subprocess.run([sys.executable,'-B',str(a.repo.resolve()/'research/benchmarks/lower_extend_019/run.py'),'replay','--commit',m['implementation_commit'],'--output',str(a.output.resolve())],check=True,env=env,timeout=600)
for n,h in m['files'].items():assert sha((a.output/n).read_bytes())==h['sha256'],n
print(json.dumps({'status':'ALL_BYTES_AND_REPLAY_MATCH','files':len(m['files']),'physical_eigensolves':0}))
