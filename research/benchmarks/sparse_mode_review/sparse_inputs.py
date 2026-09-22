"""Verify and extract the exact supplied archive; never patch its contents."""
from pathlib import Path
import hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parent
PLAN=json.loads((ROOT/'PLAN.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def originals():
 m=json.loads((ROOT/'INPUT_MANIFEST.json').read_text());zpath=ROOT/'partner_v071p.zip'
 assert sha(zpath)==m['archive_sha256']==PLAN['input_archive_sha256']
 out=ROOT/'original';out.mkdir(exist_ok=True)
 with zipfile.ZipFile(zpath) as z:
  assert set(z.namelist())==set(m['files'])
  for n,h in m['files'].items():
   assert Path(n).name==n;b=z.read(n);assert hashlib.sha256(b).hexdigest()==h
   if (out/n).exists():assert sha(out/n)==h
   else:(out/n).write_bytes(b)
 sys.path.insert(0,str(out));return out

def binding(extra):
 return {n:sha(ROOT/n) for n in ['PLAN.json','INPUT_MANIFEST.json','partner_v071p.zip','sparse_inputs.py',*extra]}
