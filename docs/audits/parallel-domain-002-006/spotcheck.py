"""Bounded independent audit at original recorded shifts, never a coverage run."""
import hashlib
import ctypes
import importlib.metadata
import importlib.util
import json
import platform
import signal
import sys
import time
import zipfile
from fractions import Fraction
from pathlib import Path

import numpy as np
import scipy
from flint import arb, arb_mat, ctx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def reviewer_provenance(wheel, lock):
    """Bind installed and loaded wheel objects without requiring /proc access.

    This restricted reviewer environment does not expose /proc/self/maps.
    glibc's loader inventory supplies the loaded object paths instead. This is
    reviewer-only provenance; no producer source or recorded flag is changed.
    """
    import flint
    assert wheel.name == lock['filename']
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == lock['sha256']
    assert flint.__version__ == lock['python_flint_version']
    assert flint.__FLINT_VERSION__ == lock['native_flint_version']
    dist = importlib.metadata.distribution('python-flint')
    with zipfile.ZipFile(wheel) as archive:
        members = {name: hashlib.sha256(archive.read(name)).hexdigest()
                   for name in archive.namelist() if name.endswith('.so') or '.so.' in name}
    installed = {name: Path(dist.locate_file(name)).resolve() for name in members}
    for name, path in installed.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == members[name]
    extension = Path(importlib.import_module('flint.pyflint').__file__).resolve()
    assert extension in installed.values()
    class Info(ctypes.Structure):
        _fields_ = [('addr', ctypes.c_void_p), ('name', ctypes.c_char_p)]
    callback_type = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(Info), ctypes.c_size_t, ctypes.c_void_p)
    loaded = set()
    @callback_type
    def collect(info, size, data):
        name = info.contents.name
        if name and name.startswith(b'/'):
            loaded.add(Path(name.decode()).resolve())
        return 0
    libc = ctypes.CDLL(None)
    libc.dl_iterate_phdr.argtypes = [callback_type, ctypes.c_void_p]
    libc.dl_iterate_phdr.restype = ctypes.c_int
    assert libc.dl_iterate_phdr(collect, None) == 0
    required = {path for name, path in installed.items() if 'python_flint.libs/' in name}
    assert len(required) >= 3 and required <= loaded
    assert extension in loaded
    return {'wheel': lock, 'loaded_extension_bound_to_wheel': True,
            'installed_native_member_count': len(installed),
            'mapped_native_library_count': len(required),
            'mapped_native_libraries_bound_to_wheel': True,
            'proc_maps_checked': False, 'loaded_object_inventory': 'glibc dl_iterate_phdr',
            'native_member_sha256': members}


def main():
    spec = json.loads((HERE / 'SPOTCHECK_SPEC.json').read_text())
    signal.alarm(spec['wall_seconds'])
    started = time.monotonic()
    ctx.prec = spec['precision_bits']
    ctx.threads = spec['native_threads']
    base = load(ROOT / 'research/benchmarks/certification_s1b_001/check.py', 'audit_base')
    assembly = base.load_parent()
    case = json.loads((ROOT / 'docs/certification-readiness/CASE.json').read_text())
    lock = json.loads((ROOT / 'research/benchmarks/certification_s1a_hardening_001/WHEEL_LOCK.json').read_text())
    provenance = reviewer_provenance(Path(sys.argv[1]).resolve(), lock)
    assembly.validate_case(case)
    cutoff = case['cutoffs']['a']
    coefficients, _ = assembly.assemble_coefficients(cutoff['ordered_indices'], case)
    c0, cx, cy = map(arb_mat, coefficients)
    selected = cutoff['selected_bands_zero_based']
    expected = {'lower': selected[0], 'upper': selected[1] + 1}
    results = []
    full = []
    factors = 0
    assert len(spec['samples']) == spec['max_cells'] == 20
    for sample in spec['samples']:
        cell = sample['cell']
        d, ix, iy = (cell[k] for k in ('depth', 'ix', 'iy'))
        den = 1 << d
        x, y = Fraction(2 * ix + 1, 2 * den), Fraction(2 * iy + 1, 2 * den)
        radius = Fraction(1, 2 * den)
        delta = base.exact_arb(-radius).union(base.exact_arb(radius))
        center = c0 + base.exact_arb(x) * cx + base.exact_arb(y) * cy
        midpoint = np.array([[float(center[i, j].mid()) for j in range(196)] for i in range(196)])
        _, vectors = np.linalg.eigh(midpoint)
        record = {'batch': sample['batch'], 'shard': sample['shard'],
                  'cell': cell, 'source_record_sha256': sample['record_sha256'], 'attempts': []}
        for digits in (17, 10):
            v = arb_mat([[arb(format(float(a), f'.{digits}g')) for a in row] for row in vectors])
            vt = v.transpose()
            gram = vt * v
            margins = [gram[i, i] - sum((abs(gram[i, j]) for j in range(196) if j != i), arb(0)) for i in range(196)]
            assert all(m > 0 for m in margins), 'GRAM_NOT_POSITIVE'
            boxed = vt * center * v + delta * (vt * cx * v) + delta * (vt * cy * v)
            attempt = {'digits': digits, 'gram_margins': [base.endpoint(m) for m in margins], 'endpoints': []}
            for name in ('lower', 'upper'):
                window = sample['window_definitions'][name]
                assert window['expected_negative'] == expected[name]
                assert Fraction(window['right']) - Fraction(window['left']) == Fraction(window['width_meV'])
                for side in ('left', 'right'):
                    shift = Fraction(window[side])
                    result = base.interval_ldl(boxed - base.exact_arb(shift) * gram)
                    factors += 1
                    assert factors <= spec['max_endpoint_factorizations']
                    assert result['status'] == 'CERTIFIED', (sample, digits, name, side)
                    assert result['negative'] == expected[name]
                    assert len(result['pivots']) == 196
                    # Independently count signs from exact rational endpoints.
                    signs = []
                    for lo, hi in result['pivots']:
                        lo, hi = Fraction(lo), Fraction(hi)
                        assert lo <= hi and (lo > 0 or hi < 0)
                        signs.append(hi < 0)
                    assert sum(signs) == expected[name]
                    attempt['endpoints'].append({'window': name, 'side': side, 'shift': str(shift), **result})
            record['attempts'].append(attempt)
        full.append(record)
        result = {k: record[k] for k in ('batch', 'shard', 'cell', 'source_record_sha256')}
        result.update(status='PASS', endpoint_factorizations=8,
                      minimum_gram_margin=min(float(Fraction(m[0])) for a in record['attempts'] for m in a['gram_margins']))
        results.append(result)
        print(json.dumps(result), flush=True)
    import gzip
    payload = json.dumps(full, sort_keys=True, separators=(',', ':')).encode() + b'\n'
    (HERE / 'SPOTCHECK_EVIDENCE.json.gz').write_bytes(gzip.compress(payload, mtime=0))
    report = {'status': 'PASS', 'spec_sha256': hashlib.sha256((HERE / 'SPOTCHECK_SPEC.json').read_bytes()).hexdigest(),
              'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__,
              'runtime_provenance': provenance, 'endpoint_factorizations': factors,
              'wall_seconds': time.monotonic() - started, 'samples': results,
              'evidence_uncompressed_sha256': hashlib.sha256(payload).hexdigest(),
              'limitation': 'Independent process and harness with fresh eigensystems; reuses the reviewed coefficient assembly and interval-LDL primitive. This is a sample audit, not an independent implementation of the full mathematics.'}
    (HERE / 'SPOTCHECK_RESULTS.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
