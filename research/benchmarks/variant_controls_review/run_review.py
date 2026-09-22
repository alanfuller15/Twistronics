"""Bounded orchestrator. Run in a disposable copy to retain original published outputs."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time
from variant_inputs import ROOT,extract
plan=json.loads((ROOT/'PLAN.json').read_text())
env=os.environ.copy()
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
original=extract(ROOT/'original')
records=[]
def command(name,args,cwd,timeout):
    start=time.perf_counter()
    with (ROOT/(name+'.log')).open('w') as log:
        try:
            p=subprocess.run(args,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
            status={'exit_code':p.returncode,'timed_out':False}
        except subprocess.TimeoutExpired:
            status={'exit_code':None,'timed_out':True}
    row={'name':name,'argv':[Path(x).name if str(ROOT) in str(x) else x for x in args],'timeout_s':timeout,'elapsed_s':time.perf_counter()-start,**status}
    records.append(row);(ROOT/'EXECUTIONS.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(row),flush=True)
    return status
command('SUPPLIED_TESTS',[sys.executable,'-m','pytest','-q','-p','no:cacheprovider','test_valley_chiral.py','--junitxml='+str(ROOT/'SUPPLIED_TESTS.xml')],original,plan['supplied_tests']['timeout_s'])
command('PROBES',[sys.executable,str(ROOT/'probes.py')],ROOT,120)
work=ROOT/'replay_work'
if work.exists(): raise RuntimeError('replay_work exists; use a fresh disposable review copy')
extract(work)
status=command('PARTNER_REPLAY',[sys.executable,str(ROOT/'replay_worker.py'),str(work),str(ROOT/'REPLAY_CALLS.json')],work,plan['replay']['timeout_s'])
results={}
for name in ('CHIRAL_CONTROL.json','VALLEY_MIRROR.json'):
    b=(work/name).read_bytes(); src=(original/name).read_bytes()
    (ROOT/('REPLAY_'+name)).write_bytes(b)
    results[name]={'original_sha256':hashlib.sha256(src).hexdigest(),'after_sha256':hashlib.sha256(b).hexdigest(),'changed':b!=src,'complete_process_exit_zero':status['exit_code']==0}
(ROOT/'REPLAY_OUTPUTS.json').write_text(json.dumps(results,indent=2)+'\n')
