"""SHA-bound, job-local retained-state loading for new frozen workflows.

Preflight checks every declared reused file. Each worker verifies the exact
bytes it decodes for its own points, avoiding repeated reads of unrelated jobs.
This module performs no Hamiltonian assembly or eigensolve. The physical worker
must still rebuild H, check nested/eigenpair residuals, and perform the frozen
byte-identical regression solves. Historical 023 code remains unchanged.
"""
import hashlib
import io
import json
from pathlib import Path

import numpy as np

try:
    from fast_pipeline.fast_pipeline import unpack_states
except ImportError:
    from research.tools.fast_pipeline.fast_pipeline import unpack_states


def _read_bound(root, relative, expected):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('REUSE_PATH_MUST_BE_RELATIVE')
    raw = (Path(root)/path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('REUSED_FILE_SHA256_MISMATCH:' + relative)
    return raw


def preflight(spec, roots):
    count, total = 0, 0
    for source, item in spec['reuse']['sources'].items():
        for relative, expected in item['files'].items():
            raw = _read_bound(roots[source], relative, expected)
            count += 1; total += len(raw)
    return {'status': 'PASS', 'files_checked': count, 'bytes_hashed': total,
            'physical_eigensolves': 0}


def load_job(spec, point_indices, roots):
    """Return point -> (full spectrum, retained four-state frame), plus I/O counts.

    All returned arrays are read-only owned copies. No state is cached between
    invocations or workers, and source bytes are hashed and decoded only once
    per needed source job. Preflight success never substitutes for these checks.
    """
    indices = tuple(point_indices)
    if not indices or len(indices) != len(set(indices)):
        raise ValueError('EMPTY_OR_DUPLICATE_REUSE_POINTS')
    cutoff = spec['reuse']['cutoff']
    dimension = spec['additional_cutoff_' + cutoff]['dimension']
    sources = spec['reuse']['sources']
    cache, states, files, byte_count = {}, {}, [], 0
    for index in indices:
        if not isinstance(index, int) or not 0 <= index < len(spec['points']):
            raise ValueError('REUSE_POINT_OUT_OF_RANGE')
        source, directory, row = spec['reuse']['point_source'][str(index)]
        key = source, directory
        item = sources[source]
        if key not in cache:
            filename = {'pack': 'STATES.pack', 'npz': 'STATES.npz'}[item['format']]
            payloads = {}
            for name in ('SAMPLES.json', filename):
                relative = directory + '/' + name
                raw = _read_bound(roots[source], relative, item['files'][relative])
                payloads[name] = raw; files.append(source + ':' + relative); byte_count += len(raw)
            rows = json.loads(payloads['SAMPLES.json'])
            if item['format'] == 'pack':
                arrays = unpack_states(payloads[filename])
            else:
                with np.load(io.BytesIO(payloads[filename]), allow_pickle=False) as archive:
                    arrays = {cutoff+'_'+kind: archive[cutoff+'_'+kind] for kind in ('energies','vectors')}
            energies, vectors = arrays[cutoff+'_energies'], arrays[cutoff+'_vectors']
            if energies.shape != (len(rows),dimension) or vectors.shape != (len(rows),dimension,4):
                raise ValueError('REUSE_ARRAY_SHAPE')
            if energies.dtype != np.dtype('<f8') or vectors.dtype != np.dtype('<f8'):
                raise ValueError('REUSE_ARRAY_DTYPE')
            cache[key] = rows, energies, vectors
        rows, energies, vectors = cache[key]
        if not isinstance(row,int) or not 0 <= row < len(rows):
            raise ValueError('REUSE_ROW_OUT_OF_RANGE')
        if rows[row]['center'] != spec['points'][index] or rows[row]['label'] != spec['labels'][index]:
            raise ValueError('REUSE_POINT_BINDING')
        E, V = energies[row].copy(), vectors[row].copy()
        if not (np.isfinite(E).all() and np.isfinite(V).all() and np.all(np.diff(E)>=0)):
            raise ValueError('INVALID_RETAINED_ARRAY')
        if np.max(abs(V.T@V-np.eye(4))) >= 1e-10:
            raise ValueError('RETAINED_FRAME_NOT_ORTHONORMAL')
        E.flags.writeable = False; V.flags.writeable = False
        states[index] = E, V
    return states, {'points':len(indices),'files_checked':len(files),'bytes_hashed':byte_count,
                    'files':files,'physical_eigensolves':0}
