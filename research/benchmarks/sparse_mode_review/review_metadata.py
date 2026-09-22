"""Compare exact archives and parse the supplied probe's rounded timing output."""
import json,re,zipfile,hashlib,difflib
from pathlib import Path
p=Path(__file__).resolve().parent;old=p.parent/'joint_mapping_review/partner_joint_mapping.zip'
with zipfile.ZipFile(old) as a,zipfile.ZipFile(p/'partner_v071p.zip') as b:
 data={'previous_archive_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'new_archive_sha256':hashlib.sha256((p/'partner_v071p.zip').read_bytes()).hexdigest(),'comparison':{}}
 for n in b.namelist():
  if n in a.namelist():
   aa=a.read(n);bb=b.read(n);data['comparison'][n]={'status':'identical' if aa==bb else 'changed','old_sha256':hashlib.sha256(aa).hexdigest(),'new_sha256':hashlib.sha256(bb).hexdigest()}
   if aa!=bb:data['comparison'][n]['diff']=''.join(difflib.unified_diff(aa.decode().splitlines(True),bb.decode().splitlines(True),fromfile='previous/'+n,tofile='v071p/'+n))
  else:data['comparison'][n]={'status':'new_to_this_comparison','new_sha256':hashlib.sha256(b.read(n)).hexdigest()}
(p/'SOURCE_COMPARISON.json').write_text(json.dumps(data,indent=2)+'\n')
pattern=r'N=(\d+) D=(\d+) build ([\d.]+)s \| density ([\d.]+)% \((\d+) nnz/row\) \| dense subset ([\d.]+) ms \| sparse shift-invert\(sigma=0\) ([\d.]+) ms \| max eigenvalue diff ([\de+.-]+) meV \| CSR assembly ([\d.]+) ms'
rows=[]
for v in re.findall(pattern,(p/'SOLVER_PROBE.log').read_text()):
 rows.append(dict(N=int(v[0]),dimension=int(v[1]),build_seconds=float(v[2]),density_percent=float(v[3]),nnz_per_row_floor=int(v[4]),dense_ms=float(v[5]),sparse_ms=float(v[6]),error_meV=float(v[7]),dense_to_csr_ms=float(v[8]),ratio=float(v[5])/float(v[6])))
assert len(rows)==3
(p/'TIMINGS.json').write_text(json.dumps({'source_log_sha256':hashlib.sha256((p/'SOLVER_PROBE.log').read_bytes()).hexdigest(),'rows':rows,'scope':'Two calls per kernel on one preassembled matrix, one BLAS thread. Values are parsed from the rounded supplied probe output. Sparse solve uses that CSR matrix; setup, per-k sparse update and acceptance checks are excluded. No end-to-end campaign speedup or scaling forecast.'},indent=2)+'\n')
print('Archive comparison and rounded kernel timing metadata retained.')
