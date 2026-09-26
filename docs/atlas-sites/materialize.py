"""Restore the exact Sites source at version 18, 19, 20, 21, 22, 23, 24 or 25 for independent review."""
import base64,gzip,hashlib,io,json,subprocess,sys,tarfile
from pathlib import Path
here=Path(__file__).resolve().parent;m=json.loads((here/'MANIFEST.json').read_text());out=Path(sys.argv[1]).resolve();version=sys.argv[2] if len(sys.argv)>2 else '25'
assert version in ['18','19','20','21','22','23','24','25'];assert not out.exists();out.mkdir(parents=True)
parts=[]
for item in m['parts']:
 data=base64.b64decode((here/item['path']).read_text());assert hashlib.sha256(data).hexdigest()==item['decoded_sha256'];parts.append(data)
raw=b''.join(parts);assert hashlib.sha256(raw).hexdigest()==m['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(gzip.decompress(raw))) as t:
 for member in t.getmembers():
  assert not member.issym() and not member.islnk() and (out/member.name).resolve().is_relative_to(out)
 t.extractall(out,filter='data')
for item in m['versions']:
 if item['patch']:subprocess.run(['git','apply',str(here/item['patch'])],cwd=out,check=True)
 for name,sha in item['file_sha256'].items():assert hashlib.sha256((out/name).read_bytes()).hexdigest()==sha,name
 if item['version']==version:
  print(json.dumps({'version':version,'sites_source_commit':item['sites_source_commit'],'files_checked':len(item['file_sha256']),'path':str(out)}));break
