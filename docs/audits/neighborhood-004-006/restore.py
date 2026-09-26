"""Restore independent audit bytes; this does not repeat physical calculations."""
import base64,hashlib,io,json,sys,tarfile
from pathlib import Path
here=Path(__file__).resolve().parent;m=json.loads((here/'PACKET.json').read_text());out=Path(sys.argv[1]).resolve();assert not out.exists();out.mkdir(parents=True)
parts=[]
for p in m['parts']:
 data=base64.b64decode((here/p['path']).read_bytes(),validate=True);assert hashlib.sha256(data).hexdigest()==p['decoded_sha256'];parts.append(data)
raw=b''.join(parts);assert hashlib.sha256(raw).hexdigest()==m['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:
 for member in t.getmembers():assert member.isfile() and (out/member.name).resolve().is_relative_to(out)
 t.extractall(out,filter='data')
assert {str(p.relative_to(out)) for p in out.rglob('*') if p.is_file()}==set(m['files'])
for name,item in m['files'].items():
 data=(out/name).read_bytes();assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
assert hashlib.sha256((here/'recompute.py').read_bytes()).hexdigest()==m['reviewer_script_sha256']
print(json.dumps({'status':'ALL_AUDIT_BYTES_MATCH','files':len(m['files']),'physical_eigensolves':0}))
