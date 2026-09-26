"""Zero-eigensolve controls for fast_pipeline.py.

usage: controls.py SRC_ROOT OUT.json [--states STATES.npz ...]
SRC_ROOT is a checkout holding the reviewed assembly and the c/d/e shell SPECs (any branch that
contains research/benchmarks/{cutoff_ladder_003,cutoff_shell_012,r1_cutoff_e_016}).

1. FastPointMatrix(x, y) is byte-identical to the reference point_matrix at every declared point
   and every cutoff a/b/c/d/e (48 control points: loop/grid coordinates from 007-021 plus
   non-dyadic rationals and domain corners). No eigensolves.
2. pack_states/unpack_states round-trips retained STATES.npz arrays bit-for-bit, and packing is
   deterministic (two packs give identical bytes).
"""
import json, sys, time, hashlib
from fractions import Fraction as F
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fast_pipeline import FastPointMatrix, pack_states, unpack_states

src, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
states = sys.argv[sys.argv.index('--states') + 1:] if '--states' in sys.argv else []
sys.path.insert(0, str(src / 'research/benchmarks/three_front_001'))
import run as R
from flint import ctx
ctx.prec = 128; ctx.threads = 1
base = R.load(src / 'research/benchmarks/certification_s1b_001/check.py', 'fp_base'); assembly = base.load_parent()
case = json.loads((src / 'docs/certification-readiness/CASE.json').read_text()); assembly.validate_case(case)
case['cutoffs']['c'] = json.loads((src / 'research/benchmarks/cutoff_ladder_003/SPEC.json').read_text())['additional_cutoff']
case['cutoffs']['d'] = json.loads((src / 'research/benchmarks/cutoff_shell_012/SPEC.json').read_text())['additional_cutoff']
case['cutoffs']['e'] = json.loads((src / 'research/benchmarks/r1_cutoff_e_016/SPEC.json').read_text())['additional_cutoff_e']

P = [
    # R3 / R1 rounded candidates and loop corners (006-016)
    (F(737426703, 2**30), F(193374303, 2**28)), (F(737426703, 2**30) - F(1, 2**20), F(193374303, 2**28) + F(1, 2**20)),
    (F(48269915, 2**27), F(19826927, 2**30)), (F(48269915, 2**27) + F(1, 2**16), F(19826927, 2**30) - F(1, 2**16)),
    # 017-021 grid and loop coordinates
    (F(673, 1024), F(655, 1024)), (F(179, 256), F(75, 128)), (F(10765, 16384), F(20955, 32768)), (F(2863, 4096), F(19195, 32768)),
    (F(705509031, 2**30), F(686641645, 2**30)), (F(375261107, 2**29), F(314495671, 2**29)),
    (F(705509031, 2**30) + F(1, 2**16), F(686641645, 2**30) - F(1, 2**17)), (F(375293875, 2**29), F(314495671, 2**29) + F(1, 2**16)),
    # domain corners/edges and non-dyadic rationals
    (F(0), F(0)), (F(1), F(1)), (F(0), F(1)), (F(1), F(0)), (F(1, 2), F(1, 2)), (F(1, 3), F(2, 3)), (F(-1, 7), F(5, 11)),
]
rng = np.random.default_rng(20260926)
while len(P) < 48:
    P.append((F(int(rng.integers(0, 2**31)), 2**31), F(int(rng.integers(0, 3**19)), 3**19)))

report = {'points': [[str(x), str(y)] for x, y in P], 'cutoffs': {}}
for k in 'abcde':
    coef = assembly.assemble_coefficients(case['cutoffs'][k]['ordered_indices'], case)[0]
    t = time.perf_counter(); fast = FastPointMatrix(base, assembly, coef); tset = time.perf_counter() - t
    t = time.perf_counter(); ref = [np.array(R.point_matrix(base, assembly, coef, x, y), dtype=float) for x, y in P]; tref = time.perf_counter() - t
    t = time.perf_counter(); new = [fast(x, y) for x, y in P]; tnew = time.perf_counter() - t
    bad = [i for i, (a, b) in enumerate(zip(ref, new)) if a.tobytes() != b.tobytes()]
    n = fast.n
    report['cutoffs'][k] = {'dimension': n, 'support_entries': fast.support, 'support_fraction': fast.support / n / n,
                            'byte_identical_points': len(P) - len(bad), 'mismatched_points': bad,
                            'setup_seconds': round(tset, 3), 'reference_ms_per_point': round(1e3 * tref / len(P), 2), 'fast_ms_per_point': round(1e3 * tnew / len(P), 3)}
    print(k, report['cutoffs'][k], flush=True)
    assert not bad, (k, bad)

rt = []
for f in states:
    z = np.load(f); arrays = {name: z[name] for name in z.files}
    a1 = pack_states(arrays); a2 = pack_states(arrays); back = unpack_states(a1)
    ok = a1 == a2 and set(back) == set(arrays) and all(back[n].tobytes() == np.ascontiguousarray(arrays[n], dtype='<f8').tobytes() and back[n].shape == arrays[n].shape for n in arrays)
    rt.append({'file': str(f), 'npz_bytes': Path(f).stat().st_size, 'packed_bytes': len(a1), 'ratio_vs_npz': len(a1) / Path(f).stat().st_size, 'deterministic_and_bit_identical': ok, 'packed_sha256': hashlib.sha256(a1).hexdigest()})
    assert ok, f
report['pack_roundtrip'] = rt
report['status'] = 'PASS'
out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(json.dumps({'status': 'PASS', 'states_checked': len(rt), 'mean_ratio_vs_npz': (sum(r['ratio_vs_npz'] for r in rt) / len(rt)) if rt else None}))
