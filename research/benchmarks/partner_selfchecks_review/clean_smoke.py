"""Repeat only software-contract/native-window probes in a fresh source copy."""
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
    with tempfile.TemporaryDirectory(prefix='v076p_clean_') as td:
        p = Path(td)
        files = ['contract_probes.py', 'forced_failure_worker.py', 'review_inputs.py', 'PLAN.json', 'INPUT_MANIFEST.json', 'partner_v076p.zip']
        for name in files: shutil.copy2(ROOT/name, p/name)
        env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
        r = subprocess.run([sys.executable, 'contract_probes.py'], cwd=p, env=env, text=True, capture_output=True, timeout=120)
        if r.returncode:
            (ROOT/'CLEAN_FAILURE.log').write_text(r.stdout+r.stderr); raise RuntimeError('clean contract probes failed')
        a = json.loads((ROOT/'CONTRACT_PROBES.json').read_text()); b = json.loads((p/'CONTRACT_PROBES.json').read_text())
        comparisons = {}
        for name in ('linter_fixtures', 'readme_generator', 'topology_controls'):
            comparisons[name] = a[name] == b[name]
        comparisons['supplied_linter'] = a['supplied_readme_lint']['findings'] == b['supplied_readme_lint']['findings'] and a['supplied_readme_lint']['returncode'] == b['supplied_readme_lint']['returncode']
        comparisons['forced_failure'] = a['forced_metamorphic_failure']['rows'] == b['forced_metamorphic_failure']['rows'] and a['forced_metamorphic_failure']['returncode'] == b['forced_metamorphic_failure']['returncode']
        comparisons['native_sparse_results'] = [x['result'] for x in a['native_sparse_samples']] == [x['result'] for x in b['native_sparse_samples']]
        comparisons['sources'] = a['source_sha256'] == b['source_sha256'] and a['probe_source_sha256'] == b['probe_source_sha256']
        if not all(comparisons.values()): raise RuntimeError('clean results changed: '+str(comparisons))
        (p/'PROBES.log').write_text(r.stdout+r.stderr)
        with zipfile.ZipFile(ROOT/'CLEAN_EVIDENCE.zip', 'w', zipfile.ZIP_DEFLATED) as z:
            for name in ('CONTRACT_PROBES.json', 'PROBES.log', 'LINT_REPLAY.log'): z.write(p/name, name)
        result = dict(command=[sys.executable, 'contract_probes.py'], returncode=r.returncode, copied_files={f: sha(ROOT/f) for f in files},
                       no_inherited_result_files=True, comparisons=comparisons, evidence_zip_sha256=sha(ROOT/'CLEAN_EVIDENCE.zip'),
                       scope='Contract probes plus six native sparse samples; full producer runs not repeated')
        (ROOT/'CLEAN_SMOKE.json').write_text(json.dumps(result, indent=2)+'\n'); print(json.dumps(result, indent=2))


if __name__ == '__main__': run()
