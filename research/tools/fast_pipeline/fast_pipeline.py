"""Shared fast pipeline for finite-cutoff runs (upgrades 1-3). Precision- and byte-preserving.

Upgrade 1 - FastPointMatrix: drop-in replacement for three_front_001/run.py:point_matrix.
    The reviewed assembly gives H(x, y) = C0 + x*C1 + y*C2 as 128-bit Arb balls, and runs use
    mid_float(H). C1 and C2 are nonzero only on the kinetic 2x2 blocks (0.25-0.45% of entries).
    Wherever C1[i][j] and C2[i][j] are exact zeros (mid 0, rad 0), Arb gives
    C0[i][j] + x*0 + y*0 == C0[i][j] exactly, so its float midpoint is fixed and is computed once.
    Only the support of C1/C2 is re-evaluated per point, with the same Arb operations in the same
    order as base.matrix_from_coefficients. The result is asserted byte-identical to the reference
    builder on declared control points (see controls.py) before any physical use.

Upgrade 2 - job sizing: with ~1-4 ms matrices, per-job setup (wheel provenance ~1.7 s, coefficient
    assembly ~0.6 s for c/d/e) dominates. Use jobs of up to 32 points; one FastPointMatrix per
    cutoff per job. Per-job isolation, receipts, rlimits and the 90 s job limit are unchanged.

Upgrade 3 - pack_states / unpack_states: deterministic container for retained float arrays.
    float64 bytes are byte-plane shuffled before zlib level 9 (~30% smaller than npz/gzip for
    eigenvectors); unpacking returns bit-identical arrays. Base64 is optional and only for
    transports that require text; binary storage avoids its +33%.
"""
import hashlib, json, struct, zlib

import numpy as np

FORMAT = 'twistronics-states-v1'


def _exact_zero(a):
    return a.mid() == 0 and a.rad() == 0


class FastPointMatrix:
    """fast(x, y) == point_matrix(base, assembly, coef, x, y), byte for byte (asserted by controls)."""

    def __init__(self, base, assembly, coef):
        C0, C1, C2 = coef
        n = len(C0)
        self.base = base
        self.n = n
        self.fixed = np.array(assembly.mid_float(C0), dtype=float)
        idx = [(i, j) for i in range(n) for j in range(n) if not (_exact_zero(C1[i][j]) and _exact_zero(C2[i][j]))]
        self.rows = np.array([i for i, _ in idx], dtype=np.intp)
        self.cols = np.array([j for _, j in idx], dtype=np.intp)
        self.terms = [(C0[i][j], C1[i][j], C2[i][j]) for i, j in idx]
        self.support = len(idx)

    def __call__(self, x, y):
        from fractions import Fraction
        X = self.base.exact_arb(Fraction(x))
        Y = self.base.exact_arb(Fraction(y))
        H = self.fixed.copy()
        # same expression and evaluation order as matrix_from_coefficients: (C0 + X*C1) + Y*C2
        H[self.rows, self.cols] = [float(((c0 + X * c1) + Y * c2).mid()) for c0, c1, c2 in self.terms]
        return H


def pack_states(arrays):
    """Deterministic bytes for {name: float64 ndarray}; header JSON + per-array shuffled zlib streams."""
    names = sorted(arrays)
    header, blobs = [], []
    for name in names:
        a = np.ascontiguousarray(arrays[name], dtype='<f8')
        raw = a.tobytes()
        shuffled = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 8).T.tobytes()
        blob = zlib.compress(shuffled, 9)
        header.append({'name': name, 'shape': list(a.shape), 'dtype': '<f8', 'raw_sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(blob)})
        blobs.append(blob)
    h = json.dumps({'format': FORMAT, 'arrays': header}, sort_keys=True, separators=(',', ':')).encode()
    return FORMAT.encode() + b'\n' + struct.pack('<Q', len(h)) + h + b''.join(blobs)


def unpack_states(data):
    magic = FORMAT.encode() + b'\n'
    assert data[:len(magic)] == magic, 'not a ' + FORMAT + ' container'
    off = len(magic)
    (hl,) = struct.unpack('<Q', data[off:off + 8]); off += 8
    header = json.loads(data[off:off + hl]); off += hl
    out = {}
    for item in header['arrays']:
        shuffled = zlib.decompress(data[off:off + item['bytes']]); off += item['bytes']
        raw = np.frombuffer(shuffled, dtype=np.uint8).reshape(8, -1).T.tobytes()
        assert hashlib.sha256(raw).hexdigest() == item['raw_sha256'], item['name']
        out[item['name']] = np.frombuffer(raw, dtype='<f8').reshape(item['shape']).copy()
    assert off == len(data)
    return out
