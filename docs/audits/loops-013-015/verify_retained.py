"""Additive zero-physical-solve verification of the unchanged authorized audit.
Checks receipts/retained spectra, exact producer packet hashes, geometry and independent gauge controls.
Does not assemble a Hamiltonian or call a physical eigensolver.
"""
import argparse,hashlib,importlib.util,json,subprocess
from fractions import Fraction as F
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();out=a.output
s=importlib.util.spec_from_file_location('frozen_audit',HERE/'recompute.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert subprocess.check_output(['git','show','d0ac63cbb700c6025c4ffa536bf44518e6dace0c:docs/audits/loops-013-015/recompute.py'],cwd=ROOT)==(HERE/'recompute.py').read_bytes()
assert m.binding()==read(out/'SOURCE_BINDING.json')
sched=m.schedule();rows=[];arrays={};elapsed=[]
for j in range(101):
 d=out/f'job{j:03}';r=read(d/'RECEIPT.json');owned=sched[j*6:(j+1)*6]
 assert r['exit_code']==0 and r['termination']=='NORMAL_EXIT' and r['process_group_empty'] and r['elapsed_seconds']<=90
 assert r['points']==[list(x) for x in owned] and r['eigensolves']==len(owned)
 assert set(r['sha256'])=={p.name for p in d.iterdir()}-{'RECEIPT.json'}
 for n,h in r['sha256'].items():assert sha(d/n)==h,n
 runtime=read(d/'RUNTIME.json');assert runtime['wheel']['sha256']=='376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76'
 assert runtime['loaded_extension_bound_to_wheel'] and runtime['mapped_native_libraries_bound_to_wheel']
 rr=read(d/'POINTS.json');assert [(v['run'],v['index']) for v in rr]==owned;rows+=rr;elapsed.append(r['elapsed_seconds'])
 with np.load(d/'STATES.npz') as z:arrays.update({k:z[k] for k in z.files})
b=read(out/'BATCH.json');assert b['points']==b['eigensolves']==601 and b['jobs']==101 and b['wall_seconds']<=1800
assert sum(elapsed)<=b['wall_seconds'] and [(r['run'],r['index']) for r in rows]==sched
by={(r['run'],r['index']):r for r in rows};checks={};rng=np.random.default_rng(13141528)
def closed_sign(vs):
 return int(np.prod([np.linalg.slogdet(v.T@vs[(i+1)%len(vs)])[0] for i,v in enumerate(vs)]))
for run,(name,impl,exe,directory) in m.TARGETS.items():
 cfg=read(ROOT/'research/benchmarks'/name/'SPEC.json');prod=ROOT/'research/benchmarks'/directory;manifest=read(prod/'MANIFEST.json')
 for n,item in manifest['files'].items():assert sha(prod/n)==item['sha256'] and (prod/n).stat().st_size==item['bytes'],n
 k='e' if run=='015' else 'd';dim=788 if k=='e' else 604;lo=dim//2-1;hi=lo+1;errors=[]
 for j,indices in enumerate(cfg['jobs']):
  with np.load(prod/f'job{j:03}'/'STATES.npz') as z:
   for local,i in enumerate(indices):
    E=arrays[f'{run}_{i}_{k}_E'];V=arrays[f'{run}_{i}_{k}_V'];r=by[(run,i)]
    assert E.shape==(dim,) and V.shape==(dim,4) and np.isfinite(E).all() and np.isfinite(V).all()
    assert np.all(np.diff(E)>=0) and np.max(abs(V.T@V-np.eye(4)))<1e-10
    assert r['center']==cfg['points'][i]
    assert float(max(abs(E-z[k+'_energies'][local])))==r['full_spectrum_max_error_meV']
    assert float(E[lo]-E[lo-1])==r['lower_gap_meV'] and float(E[hi+1]-E[hi])==r['upper_gap_meV']
    errors.append(r['full_spectrum_max_error_meV'])
 geometry={}
 for loop in cfg['loops']:
  if 'center' in loop:
   cx,cy=map(F,loop['center']);rad=F(loop['half_width']);x0,y0,x1,y1=cx-rad,cy-rad,cx+rad,cy+rad;step=2*rad/loop['points_per_side']
  else:x0,y0,x1,y1=[F(v,1024) for v in loop['depth10_box_x0_y0_x1_y1']];step=F(loop['step'])
  pts=[]
  corners=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
  for i,start in enumerate(corners):
   end=corners[(i+1)%4];n=max(abs(end[0]-start[0]),abs(end[1]-start[1]))/step;assert n.denominator==1
   pts.extend([[str(start[c]+(end[c]-start[c])*j/n) for c in range(2)] for j in range(int(n))])
  assert pts==[cfg['points'][i] for i in loop['point_indices']]
  controls=0
  for cols in [[0],[1],[2],[3],[1,2],[0,1,2,3]]:
   vs=[arrays[f'{run}_{i}_{k}_V'][:,cols] for i in loop['point_indices']];base=closed_sign(vs)
   # Explicit reflections and independent signs, including one-dimensional groups.
   gauge=[v@(np.linalg.qr(rng.normal(size=(len(cols),len(cols))))[0]*rng.choice([-1.,1.],size=len(cols))) for v in vs]
   assert closed_sign(gauge)==closed_sign(vs[::-1])==base;controls+=1
  geometry[loop['id']]={'points':len(pts),'exact_counterclockwise_closed_rectangle':'PASS','sign_flip_reflection_reversal_groups':controls}
 if run=='013':
  loops=cfg['loops']
  for i in [0,3]:
   c=list(map(F,loops[i]['center']));off=list(map(F,loops[i+2]['center']));assert off==[c[0]+4*F(loops[i]['half_width']),c[1]]
   assert F(loops[i+1]['half_width'])==F(loops[i]['half_width'])/2
 if run=='014':
  old=read(ROOT/'research/benchmarks/partner_loops_008/SPEC.json');unres=json.loads(subprocess.check_output(['git','show','c389e345597e66eff81bf2f1219dd4272adf2bd6:research/benchmarks/refinement_012_execution/PARTITION.json'],cwd=ROOT))['unresolved']
  for loop in cfg['loops']:
   if loop['source_008_loop']:
    orig=next(l for l in old['loops'] if l['name']==loop['source_008_loop']);assert [cfg['points'][i] for i in loop['point_indices']]==[old['points'][i] for i in orig['point_indices']]
   else:
    x0,y0,x1,y1=[F(v,1024) for v in loop['depth10_box_x0_y0_x1_y1']]
    assert not any(max(x0,F(x,2**d))<=min(x1,F(x+1,2**d)) and max(y0,F(y,2**d))<=min(y1,F(y+1,2**d)) for d,x,y in unres)
 if run=='015':
  patch=cfg['patches'][0];cx,cy=map(F,patch['center']);h=F(patch['step']);assert [cfg['points'][i] for i in patch['point_indices']]==[[str(cx+x*h),str(cy+y*h)] for y in [-1,0,1] for x in [-1,0,1]]
  old=read(ROOT/'research/benchmarks/loop_cutoff_d_013/SPEC.json');orig=next(l for l in old['loops'] if l['id']=='R3_r1_32');assert [cfg['points'][i] for i in cfg['loops'][0]['point_indices']]==[old['points'][i] for i in orig['point_indices']]
 checks[run]={'producer_files_checked':len(manifest['files']),'independent_spectra_rechecked':len(errors),'maximum_full_spectrum_error_meV':max(errors),'geometry_and_gauge':geometry}
report={'status':'PASS','physical_eigensolves':0,'reviewer_implementation':'d0ac63cbb700c6025c4ffa536bf44518e6dace0c','jobs':101,'points':601,'longest_job_seconds':max(elapsed),'summed_job_seconds':sum(elapsed),'checks':checks}
(out/'VERIFICATION.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','jobs':101,'points':601,'longest_job_seconds':max(elapsed),'physical_eigensolves':0}))
