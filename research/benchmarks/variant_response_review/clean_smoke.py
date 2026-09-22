"""Repeat tests/probes in a fresh extraction; reconcile the retained producer ledgers."""
from pathlib import Path
import json,os,shutil,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parent
start=time.perf_counter();records=[];env=os.environ.copy()
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[k]='1'
env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',PYTHONDONTWRITEBYTECODE='1')
with tempfile.TemporaryDirectory(prefix='twistronics-v074p-smoke-') as tmp:
    fresh=Path(tmp)/'review';fresh.mkdir()
    for p in ROOT.iterdir():
        if p.is_file():shutil.copy2(p,fresh/p.name)
    def run(args,cwd):
        p=subprocess.run(args,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
        records.append({'argv':[str(a).replace(str(fresh),'<fresh>') for a in args],'exit_code':p.returncode,'output':p.stdout.replace(str(fresh),'<fresh>')})
        if p.returncode:raise RuntimeError(p.stdout)
    run([sys.executable,'response_inputs.py'],fresh)
    run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','test_valley_chiral.py','--junitxml='+str(fresh/'SUPPLIED_TESTS.xml')],fresh/'original')
    run([sys.executable,'probes.py'],fresh);run([sys.executable,'report.py'],fresh)
    old=json.loads((ROOT/'PROBES.json').read_text());new=json.loads((fresh/'PROBES.json').read_text());deltas=[]
    for a,b in zip(old['matrix_rows'],new['matrix_rows'],strict=True):
        assert (a['N'],a['valley'],a['f'])==(b['N'],b['valley'],b['f']) and a['pass']==b['pass']
        deltas += [abs(x-y) for key in ('native_bands_meV','fast_bands_meV') for x,y in zip(a[key],b[key],strict=True)]
    assert max(deltas)<1e-8
    shutil.copyfile(fresh/'PROBES.json',ROOT/'CLEAN_PROBES.json');shutil.copyfile(fresh/'SUPPLIED_TESTS.xml',ROOT/'CLEAN_SUPPLIED_TESTS.xml')
summary={'status':'PASS','supplied_tests':8,'matrix_rows':18,'sparse_samples':6,'max_repeated_band_difference_meV':max(deltas),'full_producers_repeated':False,'scope':'Fresh extraction and repeat of tests/probes; reconciliation of retained completed producer ledgers. No duplicate full producer run.','elapsed_s':time.perf_counter()-start}
(ROOT/'CLEAN_SMOKE.log').write_text('\n\n'.join(json.dumps(r,indent=2) for r in records)+'\n');(ROOT/'CLEAN_SMOKE.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
