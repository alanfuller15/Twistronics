"""Copy sources + original input only, then run tests and a bounded fresh smoke."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run():
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    with tempfile.TemporaryDirectory(prefix='twistronics_guard_clean_') as td:
        dst = Path(td)
        inputs = sorted(ROOT.glob('*.py')) + [ROOT/x for x in ('partner_v074p.zip', 'INPUT_MANIFEST.json', 'PLAN.json')]
        for p in inputs: shutil.copy2(p, dst/p.name)
        rec = dict(copied_sources={p.name: sha(p) for p in inputs}, inherited_results=False, commands=[])
        commands = [[sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'test_guards.py', '--junitxml=CLEAN_TESTS.xml'],
                    [sys.executable, 'run_campaign.py', '--smoke', '--output', 'smoke']]
        for j, command in enumerate(commands):
            done = subprocess.run(command, cwd=dst, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=240)
            (dst/f'command_{j}.log').write_text(done.stdout)
            rec['commands'].append(dict(argv=command, returncode=done.returncode))
            if done.returncode:
                (ROOT/'CLEAN_FAILURE.log').write_text(done.stdout)
                raise RuntimeError('clean command failed; see CLEAN_FAILURE.log')
        old = json.loads((ROOT/'RESULTS.json').read_text())
        fresh = json.loads((dst/'smoke/RESULTS.json').read_text())
        byid = {r['id']: r for r in old['outcomes']}
        comparisons = []
        for r in fresh['outcomes']:
            other = byid[r['id']]
            if r['result']['status'] != other['result']['status']: raise RuntimeError('smoke status changed')
            fields = ['label', 'code']
            for key in fields:
                if r['result'].get(key) != other['result'].get(key): raise RuntimeError('smoke decision changed')
            import numpy as np
            errors = {}
            for key in ('windings', 'node_gaps_meV', 'energies_meV'):
                if key in r['result']:
                    errors[key] = float(np.max(np.abs(np.asarray(r['result'][key])-other['result'][key])))
                    if errors[key] > 1e-9: raise RuntimeError('smoke numerical mismatch')
            comparisons.append(dict(id=r['id'], status=r['result']['status'], max_abs_differences=errors))
        rec['comparisons'] = comparisons
        rec['original_archive_unchanged'] = sha(dst/'partner_v074p.zip') == sha(ROOT/'partner_v074p.zip')
        rec['core_source_hashes_match_full_run'] = all(fresh['sources'][f] == old['sources'][f] for f in ('guarded_topology.py', 'guarded_sparse.py', 'run_campaign.py', 'response_inputs.py'))
        with zipfile.ZipFile(ROOT/'CLEAN_EVIDENCE.zip', 'w', zipfile.ZIP_DEFLATED) as z:
            for p in sorted((dst/'smoke').glob('*')): z.write(p, 'smoke/'+p.name)
            for name in ('CLEAN_TESTS.xml', 'command_0.log', 'command_1.log'): z.write(dst/name, name)
        rec['evidence_zip_sha256'] = sha(ROOT/'CLEAN_EVIDENCE.zip')
        (ROOT/'CLEAN_SMOKE.json').write_text(json.dumps(rec, indent=2)+'\n')
        print(json.dumps(rec, indent=2))


if __name__ == '__main__': run()
