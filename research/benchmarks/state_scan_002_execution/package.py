"""Package a retained execution directory as reproducible archive parts."""
import base64,gzip,hashlib,io,json,sys,tarfile
from pathlib import Path
root=Path(sys.argv[1]);out=Path(sys.argv[2]);files={};buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w') as t:
 for p in sorted(root.rglob('*')):
  if not p.is_file():continue
  name=p.relative_to(root).as_posix();data=p.read_bytes();files[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644;t.addfile(info,io.BytesIO(data))
raw=gzip.compress(buf.getvalue(),mtime=0);parts=[]
for i,start in enumerate(range(0,len(raw),400000)):
 data=raw[start:start+400000];name=f'parts/part{i:03}.b64';(out/name).parent.mkdir(exist_ok=True);(out/name).write_bytes(base64.b64encode(data));parts.append({'path':name,'decoded_sha256':hashlib.sha256(data).hexdigest()})
m={'implementation_commit':'8dee23377371702df88d998ac29bd9c89304456e','archive_sha256':hashlib.sha256(raw).hexdigest(),'parts':parts,'files':files};(out/'MANIFEST.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');print(len(files),len(raw),len(parts))
