"""Verify/materialize reviewer evidence and replay energy/gap/frame comparisons; zero solves."""
import base64,hashlib,io,json,sys,tarfile,importlib.util
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];WORK=ROOT.parent
read=lambda p:json.loads(p.read_bytes());sha=lambda b:hashlib.sha256(b).hexdigest()
m=read(HERE/'MANIFEST.json');chunks=[]
for p in m['parts']:
 b=base64.b64decode((HERE/p['path']).read_bytes(),validate=True);assert sha(b)==p['decoded_sha256'];chunks.append(b)
b=b''.join(chunks);assert sha(b)==m['archive_sha256']
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz') as t:
 assert {p.name for p in t.getmembers()}==set(m['files'])
 for p in t.getmembers():
  assert p.isfile() and not Path(p.name).is_absolute() and '..' not in Path(p.name).parts
  b=t.extractfile(p).read();assert sha(b)==m['files'][p.name]['sha256'];f=out/p.name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
s=importlib.util.spec_from_file_location('r',ROOT/'docs/audits/controls022-cutoff023/retained_review.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
cfg=read(HERE.parent/'SPEC.json');case=r.shells();count=exact=0;cache={}
for j,ids in enumerate(cfg['jobs']):
 d=out/f'job{j:03}';receipt=read(d/'RECEIPT.json');assert receipt['exit_code']==0 and receipt['process_group_empty'] and receipt['termination']=='NORMAL_EXIT'
 for p,h in receipt['files'].items():assert sha((d/p).read_bytes())==h['sha256']
 z=dict(np.load(d/'STATES.npz',allow_pickle=False));rows=read(d/'RESULTS.json');assert [x['record'] for x in rows]==ids
 for row in rows:
  i=row['record'];rec=cfg['records'][i];k=rec['cutoff'];p=WORK/rec['file'];assert sha(p.read_bytes())==cfg['input_sha256'][rec['file']]
  if str(p) not in cache:cache[str(p)]=r.unpack(p) if p.suffix=='.pack' else dict(np.load(p,allow_pickle=False))
  ref=cache[str(p)][k+'_energies'][rec['row']];E=z[f'r{i}_energies'];V=z[f'r{i}_vectors'];lo,hi=case[k]['selected_bands_zero_based']
  err=float(np.max(abs(E-ref)));g=lambda e:np.array([e[lo]-e[lo-1],e[hi+1]-e[hi],e[hi]-e[lo]])
  ge=float(np.max(abs(g(E)-g(ref))));assert err==row['energy_error_meV'] and ge==row['gap_error_meV']
  assert E.shape==(case[k]['dimension'],) and V.shape==(case[k]['dimension'],4)
  if rec['mode']=='exact_evr':assert E.tobytes()==ref.tobytes() and V.tobytes()==cache[str(p)][k+'_vectors'][rec['row']].tobytes();exact+=1
  count+=1
assert count==200 and exact==64
print(json.dumps(dict(status='PASS',files=len(m['files']),spectra_replayed=count,exact_regressions=exact,physical_eigensolves=0,progress_recovery=read(out/'PROGRESS_RECOVERY.json'))))
