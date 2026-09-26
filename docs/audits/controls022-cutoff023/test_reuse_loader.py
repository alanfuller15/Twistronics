"""Compare new job-local loading with independently decoded 023 retained data.

Usage: test_reuse_loader.py MATERIALIZED_021 OUTPUT.json
No physical computation. Negative fixtures use modified in-memory SPEC copies.
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'research/tools'))
import retained_states
from retained_review import unpack


def main():
    spec = json.loads((ROOT/'research/benchmarks/cutoff_f_023/SPEC.json').read_text())
    roots = {'022':ROOT/spec['reuse']['sources']['022']['root'],'021':Path(sys.argv[1])}
    checked = retained_states.preflight(spec,roots)
    source_cache, arrays, read_files, read_bytes = {}, 0, 0, 0
    for indices in spec['jobs']:
        states, info = retained_states.load_job(spec,indices,roots)
        read_files += info['files_checked']; read_bytes += info['bytes_hashed']
        for i in indices:
            source,directory,row = spec['reuse']['point_source'][str(i)]
            key = source,directory
            if key not in source_cache:
                path = roots[source]/directory
                source_cache[key] = unpack(path/'STATES.pack') if source=='022' else dict(np.load(path/'STATES.npz',allow_pickle=False))
            for kind, actual in zip(('energies','vectors'),states[i]):
                expected = source_cache[key]['e_'+kind][row]
                assert actual.tobytes() == expected.tobytes() and actual.shape == expected.shape
                assert not actual.flags.writeable
                arrays += 1
    rejected = []
    for name in ('bad_hash','wrong_coordinate','wrong_label','wrong_row','wrong_shape','path_traversal','duplicate_points'):
        cfg = copy.deepcopy(spec);indices = [0]
        if name == 'bad_hash': cfg['reuse']['sources']['022']['files']['job000/STATES.pack'] = '0'*64
        if name == 'wrong_coordinate': cfg['points'][0][0] = '0'
        if name == 'wrong_label': cfg['labels'][0] = 'WRONG'
        if name == 'wrong_row': cfg['reuse']['point_source']['0'][2] = 1
        if name == 'wrong_shape': cfg['additional_cutoff_e']['dimension'] += 4
        if name == 'path_traversal':
            cfg['reuse']['point_source']['0'][1] = '../job000'
            cfg['reuse']['sources']['022']['files']['../job000/SAMPLES.json'] = '0'*64
        if name == 'duplicate_points': indices = [0,0]
        try: retained_states.load_job(cfg,indices,roots)
        except ValueError: rejected.append(name)
        else: raise AssertionError('BAD_REUSE_ACCEPTED:'+name)
    assert arrays == 768
    result = {'status':'PASS','physical_eigensolves':0,'points':384,'bit_identical_arrays':arrays,
              'preflight':checked,'job_loads':len(spec['jobs']),'job_file_checks':read_files,
              'job_bytes_hashed':read_bytes,'prior_all_files_per_job_checks':checked['files_checked']*len(spec['jobs']),
              'prior_all_files_per_job_bytes_hashed':checked['bytes_hashed']*len(spec['jobs']),
              'negative_controls_rejected':rejected,
              'scope':'I/O counts and retained-array identity; not a timing benchmark or a physical-run review.',
              'loader_sha256':hashlib.sha256(Path(retained_states.__file__).read_bytes()).hexdigest()}
    Path(sys.argv[2]).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result))


if __name__ == '__main__': main()
