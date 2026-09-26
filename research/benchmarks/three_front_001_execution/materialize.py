"""Restore complete retained evidence, with 20-cell review chunks."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
here=Path(__file__).resolve().parent;out=Path(sys.argv[1]).resolve();assert not out.exists();out.mkdir(parents=True)
transport=json.loads((here/'TRANSPORT.json').read_text());manifest=json.loads((here/'MANIFEST.json').read_text())
def read(name):
 if name in transport:
  entry=transport[name];data=b''.join((here/p).read_bytes() for p in entry['parts']);assert hashlib.sha256(data).hexdigest()==entry['sha256'];return data
 return (here/name).read_bytes()
for entry in manifest['files']:
 if entry['encoding']=='plain':data=read(entry['path'])
 elif entry['encoding']=='gzip-record-chunks+base64':data=b''.join(gzip.decompress(base64.b64decode(read(p))) for p in entry['parts'])
 elif entry['encoding']=='gzip+base64':data=gzip.decompress(b''.join(base64.b64decode(read(p)) for p in entry['parts']))
 else:raise ValueError('Unknown encoding')
 assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'],entry['path']
 dst=out/entry['path'];assert dst.resolve().is_relative_to(out);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
print(json.dumps({'status':'ALL_BYTES_MATCH','files':len(manifest['files']),'implementation_commit':manifest['implementation_commit'],'output':str(out)}))
