"""Separate full retained-spectrum inventory; no producer summary helper or physical calls."""
import importlib.util,json,hashlib,sys
from fractions import Fraction as F
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('decode',ROOT/'docs/audits/controls022-cutoff023/retained_review.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
source=Path(sys.argv[1]);b=source/'research/benchmarks';cfg=r.read(b/'sweep_d_024/SPEC.json');d=b/'sweep_d_024_execution';manifest=r.manifest(d)
for p,h in cfg['dependencies'].items():assert r.sha((source/p).read_bytes())==h
case=r.shells();data={k:[] for k in ['a','d']};points=[]
for j,ids in enumerate(cfg['jobs']):
 z=r.unpack(d/f'job{j:03}'/'STATES.pack');rows=r.read(d/f'job{j:03}'/'SAMPLES.json')
 assert [p['index'] for p in rows]==ids
 for n,row in enumerate(rows):
  i=row['index'];assert row['center']==cfg['points'][i] and row['label']==cfg['labels'][i];points.append(i)
  for k in data:
   E=z[k+'_energies'][n];lo,hi=case[k]['selected_bands_zero_based'];assert E.shape==(case[k]['dimension'],) and np.isfinite(E).all() and (np.diff(E)>=0).all()
   g=dict(lower_meV=float(E[lo]-E[lo-1]),upper_meV=float(E[hi+1]-E[hi]),pair_meV=float(E[hi]-E[lo]));assert g==row['gaps'][k];data[k].append(g)
assert points==list(range(4104))
for j in range(64):
 for i in range(64):assert cfg['points'][64*j+i]==[str(F(2*i+1,128)),str(F(2*j+1,128))]
summary=r.read(d/'SUMMARY.json');candidates={k:np.array(list(map(float,v))) for k,v in cfg['candidates'].items()};out=dict(status='PASS',physical_eigensolves=0,points=4104,full_spectra=8208,manifest_files=len(manifest['files']),maps={},changes={},minima={},flags=[])
for k in data:
 for g in ['lower_meV','upper_meV','pair_meV']:
  a=np.array([v[g] for v in data[k][:4096]]);i=int(a.argmin());result=dict(min=float(a.min()),max=float(a.max()),median=float(np.median(a)),argmin_label=cfg['labels'][i],argmin_center=cfg['points'][i]);assert result==summary['maps'][k+'_'+g];out['maps'][k+'_'+g]=result
for g in ['lower_meV','upper_meV','pair_meV']:
 a=np.array([v[g] for v in data['a'][:4096]]);d0=np.array([v[g] for v in data['d'][:4096]]);diff=np.abs(d0-a);result=dict(max_abs=float(diff.max()),at_label=cfg['labels'][int(diff.argmax())],median_abs=float(np.median(diff)));assert result==summary['changes_a_to_d'][g];out['changes'][g]=result
 if g=='pair_meV':continue
 grid=d0.reshape(64,64);mask=np.ones((64,64),bool)
 for dy in [-1,0,1]:
  for dx in [-1,0,1]:
   if dx or dy:mask &= grid<np.roll(grid,(dy,dx),(0,1))
 minima=[]
 for i in np.flatnonzero(mask):
  p=np.array([float(F(c)) for c in cfg['points'][i]]);dist={}
  for c,q in candidates.items():
   v=np.abs(p-q)%1;dist[c]=float(np.linalg.norm(np.minimum(v,1-v)))
  c=min(dist,key=dist.get);row=dict(label=cfg['labels'][i],center=cfg['points'][i],gap_d_meV=float(d0[i]),gap_a_meV=float(a[i]),nearest_candidate=c,distance=dist[c]);minima.append(row)
  if row['gap_d_meV']<1 and row['distance']>2/64:out['flags'].append(dict(row,gap=g))
 minima.sort(key=lambda x:x['gap_d_meV']);saved=summary['local_minima_d'][g];assert saved['count']==len(minima)
 for x,y in zip(minima,saved['minima']):
  assert abs(x['distance']-y['distance'])<1e-15
  assert {k:v for k,v in x.items() if k!='distance'}=={k:v for k,v in y.items() if k!='distance'}
 out['minima'][g]=minima
assert out['flags']==summary['new_region_flags']==[]
errors=[]
for key in ['lower','upper']:
 for k,rows in cfg['regression'][key+'_gap_meV'].items():
  for i,e in rows.items():errors.append(abs(data[k][int(i)][key+'_meV']-e))
assert len(errors)==32 and max(errors)<1e-9
out['historical_regression_values']=len(errors);out['max_regression_error_meV']=max(errors)
out['scope']='All 4096 grid points have lower/upper d gaps above 1 meV, so zero <1-meV flags is not evidence that unsampled features do not exist. Five sampled strict periodic minima; no complete basin/candidate inventory, continuous isolation or coverage increment.'
Path(sys.argv[2]).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['maps','changes','minima']}))
