"""Read-only byte comparison and AST inventory; no imported project code."""
from pathlib import Path
import ast,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
old=BASE/'team-v047';new=BASE/'team-v049';rows=[]
for p in sorted(new.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts:continue
 rel=p.relative_to(new);data=p.read_bytes();prior=old/rel
 status='added' if not prior.exists() else ('unchanged' if prior.read_bytes()==data else 'changed')
 row=dict(path=str(rel),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),change=status)
 if status!='unchanged' and p.suffix=='.py':
  tree=ast.parse(data,filename=str(rel));row['imports']=sorted({n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)}|{a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names})
  row['calls']=sorted({ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n,ast.Call)})
 rows.append(row)
with zipfile.ZipFile(BASE/'upload/twistronics_v023-v049.zip') as z:
 archive=dict(entries=len(z.infolist()),files=sum(not x.is_dir() for x in z.infolist()),sha256=hashlib.sha256((BASE/'upload/twistronics_v023-v049.zip').read_bytes()).hexdigest())
(ROOT/'provenance/inventory.json').write_text(json.dumps(dict(archive=archive,files=rows),indent=2)+'\n')
print(json.dumps(dict(archive=archive,changes=[x['path'] for x in rows if x['change']!='unchanged']),indent=2))
