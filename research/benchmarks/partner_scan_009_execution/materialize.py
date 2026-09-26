"""Restore every retained byte, replay strict verification without physical eigensolves, and re-derive SUMMARY."""
import argparse,base64,hashlib,io,json,os,subprocess,sys,tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--repo',type=Path,required=True);a=p.parse_args();here=Path(__file__).resolve().parent;m=json.loads((here/'MANIFEST.json').read_text());out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
parts=[]
for item in m['parts']:
 data=base64.b64decode((here/item['path']).read_bytes(),validate=True);assert hashlib.sha256(data).hexdigest()==item['decoded_sha256'];parts.append(data)
raw=b''.join(parts);assert hashlib.sha256(raw).hexdigest()==m['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:
 for member in t.getmembers():assert member.isfile() and (out/member.name).resolve().is_relative_to(out)
 t.extractall(out,filter='data')
assert {str(p.relative_to(out)) for p in out.rglob('*') if p.is_file()}==set(m['files'])
for name,entry in m['files'].items():assert sha(out/name)==entry['sha256'] and (out/name).stat().st_size==entry['bytes'],name
expected={name:sha(out/name) for name in ['MAP.json','REGRESSION.json','PLAQUETTES.json','SUMMARY.json']}
env=dict(os.environ);env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
subprocess.run([sys.executable,'-B',str(a.repo.resolve()/'research/benchmarks/partner_scan_009/run.py'),'replay','--commit',m['implementation_commit'],'--output',str(out)],check=True,env=env,timeout=1200)
review=json.loads((out/'SUMMARY.json').read_text())['independent_review']
subprocess.run([sys.executable,'-B',str(here/'analyze.py'),str(out),review],check=True,env=env,timeout=600,stdout=subprocess.DEVNULL)
for name,h in expected.items():assert sha(out/name)==h,name
print(json.dumps({'status':'ALL_BYTES_AND_STRICT_REPLAY_MATCH','implementation_commit':m['implementation_commit'],'files':len(m['files']),'replayed_points':255,'physical_eigensolves':0,'map_regression_plaquettes_summary':'BYTE_IDENTICAL'}))
