"""Restore all bytes and replay finite-box checks, without eigensolver calls."""
import argparse,base64,gzip,hashlib,importlib.util,io,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--repo',type=Path);p.add_argument('--coarse',type=Path);p.add_argument('--replay-output',type=Path);a=p.parse_args()
here=Path(__file__).resolve().parent;m=json.loads((here/'MANIFEST.json').read_text());out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
chunks=[]
for entry in m['parts']:
 raw=base64.b64decode((here/entry['path']).read_bytes(),validate=True);assert hashlib.sha256(raw).hexdigest()==entry['decoded_sha256'];chunks.append(raw)
archive=b''.join(chunks);assert hashlib.sha256(archive).hexdigest()==m['archive_sha256']
with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as t:
 for member in t.getmembers():assert member.isfile() and (out/member.name).resolve().is_relative_to(out)
 t.extractall(out,filter='data')
assert {str(p.relative_to(out)) for p in out.rglob('*') if p.is_file()}==set(m['files'])
for name,entry in m['files'].items():assert sha(out/name)==entry['sha256'] and (out/name).stat().st_size==entry['bytes'],name
batch=json.loads((out/'BATCH_RECEIPT.json').read_text());assert batch['failure'] is None and batch['jobs_completed']==205 and batch['elapsed_seconds']<=900 and batch['implementation_commit']==m['implementation_commit']
seen=[];worst_seconds=0
for j in range(205):
 d=out/f'job{j:03}';receipt=json.loads((d/'RECEIPT.json').read_text());result=json.loads((d/'RESULTS.json').read_text());indices=list(range(j*20,min(4096,j*20+20)))
 assert receipt['job']==result['job']==j and receipt['indices']==result['indices']==indices and result['eigensolver_starts']==len(indices)
 assert receipt['implementation_commit']==result['implementation_commit']==m['implementation_commit']
 assert receipt['termination']=='NORMAL_EXIT' and receipt['exit_code']==0 and receipt['process_group_empty'] and receipt['elapsed_seconds']<=90
 assert {p.name for p in d.iterdir()}==set(receipt['files'])|{'RECEIPT.json'}
 for name,entry in receipt['files'].items():assert sha(d/name)==entry['sha256'] and (d/name).stat().st_size==entry['bytes']
 assert sha(d/'MODES.npz')==result['modes_sha256'] and result['max_eigenpair_residual_meV']<1e-8
 runtime=result['runtime'];assert runtime['loaded_extension_bound_to_wheel'] and runtime['mapped_native_libraries_bound_to_wheel'] and runtime['wheel']['sha256']==m['wheel_sha256']
 assert runtime['installed_native_member_count']==42 and runtime['mapped_native_library_count']==3 and runtime['loaded_object_inventory']=='glibc dl_iterate_phdr'
 seen+=indices;worst_seconds=max(worst_seconds,receipt['elapsed_seconds'])
assert seen==list(range(4096))
for name,entry in json.loads((out/'render/MANIFEST.json').read_text()).items():assert sha(out/'render'/name)==entry['sha256'] and (out/'render'/name).stat().st_size==entry['bytes']
report={'status':'ALL_BYTES_AND_RECEIPTS_MATCH','files':len(m['files']),'jobs':205,'eigensolver_starts':4096,'maximum_job_seconds':worst_seconds,'implementation_commit':m['implementation_commit'],'physical_replay_calls':0,'independent_review':'PENDING'}
if a.coarse:
 assert a.repo and a.replay_output and not a.replay_output.exists();replay=a.replay_output.resolve();replay.mkdir(parents=True)
 for d in sorted(out.glob('job*')):shutil.copytree(d,replay/d.name)
 runner=a.repo.resolve()/'research/benchmarks/dynamics_002/run.py'
 env=dict(os.environ);env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
 subprocess.run([sys.executable,'-B',str(runner),'render','--commit',m['implementation_commit'],'--coarse',str(a.coarse.resolve()),'--output',str(replay)],check=True,env=env,timeout=610)
 names={p.name for p in (out/'render').iterdir()};assert names=={p.name for p in (replay/'render').iterdir()}
 for name in names:assert sha(out/'render'/name)==sha(replay/'render'/name),name
 report['render_replay']='BYTE_IDENTICAL';report['render_files_replayed']=len(names)
print(json.dumps(report,sort_keys=True))
