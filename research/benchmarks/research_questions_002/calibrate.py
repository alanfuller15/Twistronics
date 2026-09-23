"""Calibrate unmodified archived guarded Euler code on explicit small models.

No TBG sweep, network, subprocess or production-source modification. The only
writes are a fresh result directory and a private temporary source extraction.
The historical research_questions_001 package is imported unchanged.
"""
import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import tempfile
import zipfile

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = ROOT / "research/benchmarks/migration_contract_review/partner_v078p.zip"
REFERENCE = HERE.parent / "research_questions_001/reproduce.py"
ARCHIVE_SHA = "d703b6c027d5725ed173c69d221f450a34922e46d1320350ab1c08e3448c545e"
GUARDED_SHA = "c0330478ce1ff1098cc596b4798a4497efc0f0044b3c10cca9b1443fc88856ae"
LINK_FLOOR = 0.5  # inherited production policy; max principal angle <= pi/3
PHASE_CEILING = np.pi / 2  # unchanged stricter reference criterion


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_reference():
    spec = importlib.util.spec_from_file_location("questions001_reference", REFERENCE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_production(directory):
    if sha(ARCHIVE) != ARCHIVE_SHA:
        raise RuntimeError("archived source identity mismatch")
    with zipfile.ZipFile(ARCHIVE) as z:
        for name in ("guarded_topology.py", "response_inputs.py", "INPUT_MANIFEST.json", "partner_v074p.zip"):
            (directory / name).write_bytes(z.read(name))
    if sha(directory / "guarded_topology.py") != GUARDED_SHA:
        raise RuntimeError("guarded source identity mismatch")
    sys.path.insert(0, str(directory))
    # Its original activate() verifies/extracts the nested archive in this
    # private directory. No stub imports, replacement eigensolver or link code.
    import guarded_topology
    return guarded_topology


class Trace:
    """Streaming identity plus selected diagnostics; not a full trace archive."""
    def __init__(self):
        self.counts = Counter()
        self.digest = hashlib.sha256()
        self.min_link = None
        self.min_gap = None
        self.max_sewing_loss = None
        self.rejections = []
        self.phases = []

    def append(self, row):
        self.digest.update((json.dumps(row, sort_keys=True, allow_nan=False) + "\n").encode())
        self.counts[row['kind']] += 1
        if row['kind'] == 'link':
            if self.min_link is None or row['min_overlap'] < self.min_link['min_overlap']:
                self.min_link = row
            if row['sewing'] and (self.max_sewing_loss is None or row['sewing_loss'] > self.max_sewing_loss['sewing_loss']):
                self.max_sewing_loss = row
        if row['kind'] == 'frame' and row['external_gap_meV'] is not None:
            if self.min_gap is None or row['external_gap_meV'] < self.min_gap['external_gap_meV']:
                self.min_gap = row
        if row['kind'] == 'rejection':
            self.rejections.append(row)
        if row['kind'] == 'wilson_phases':
            self.phases.append(row)

    def summary(self):
        return dict(counts=dict(self.counts), full_stream_sha256=self.digest.hexdigest(),
                    minimum_link=self.min_link, minimum_gap=self.min_gap,
                    maximum_sewing_loss=self.max_sewing_loss, rejections=self.rejections,
                    wilson_phases=self.phases,
                    retention="Selected extrema, refusals and complete Wilson phases; full frame/link stream not retained")


class Model:
    dim = 3
    def __init__(self, ref, m=-1, kind="sphere", folds=1):
        self.ref, self.m, self.kind, self.folds = ref, m, kind, folds

    def frac_to_k(self, f):
        return 2 * np.pi * np.asarray(f) - np.pi

    def normal(self, k):
        if self.kind.startswith('mobius'):
            axis = int(self.kind[-1])
            angle = (k[axis] + np.pi) / 2
            return np.array([np.cos(angle), np.sin(angle), 0.])
        return self.ref.texture(self.folds * k[0], k[1], self.m)

    def H(self, k):
        n = self.normal(k)
        h = 2 * np.outer(n, n) - np.eye(3)
        if self.kind == 'gapless':
            return np.zeros((3, 3))
        if self.kind == 'complex':
            h = h.astype(complex)
            h[0, 1] += .01j
            h[1, 0] -= .01j
        return h


def strict_loop(ref, frames):
    minimum = min(float(np.linalg.svd(a.T @ b, compute_uv=False)[-1])
                  for a, b in zip(frames, np.roll(frames, -1, axis=0)))
    if minimum < LINK_FLOOR:
        raise ValueError("reference_link_resolution")
    return ref.loop(frames)  # original polar multiplication, unchanged


def strict_curve(ref, nx, ny, m):
    angles, minimum = [], 1.
    for y in np.linspace(-np.pi, np.pi, ny + 1):
        fs = np.array([ref.frame(ref.texture(x, y, m))[0]
                       for x in np.linspace(-np.pi, np.pi, nx, endpoint=False)])
        w, small = strict_loop(ref, fs)
        minimum = min(minimum, small)
        angles.append(ref.so_angle(w))
    phase = np.unwrap(angles)
    step = float(np.max(np.abs(np.diff(phase))))
    if step >= PHASE_CEILING:
        raise ValueError("reference_transverse_phase_resolution")
    return dict(winding=float((phase[-1] - phase[0]) / (2 * np.pi)),
                min_overlap=minimum, max_phase_step=step)


def run(out):
    out.mkdir(parents=True, exist_ok=False)
    ref = load_reference()
    plan = json.loads((HERE / 'PLAN.json').read_text())
    for name, expected in plan['sources'].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError("predeclared source mismatch: " + name)
    checks, cases = [], []

    def check(name, condition, **evidence):
        checks.append(dict(name=name, passed=bool(condition), **evidence))

    with tempfile.TemporaryDirectory(prefix='twistronics_calibration_') as temporary:
        prod = load_production(Path(temporary))
        policy = prod.Policy(phase_step_max_rad=float(PHASE_CEILING))

        class GaugedSampler(prod.Sampler):
            def __init__(self, *args, gauge='raw', **kwargs):
                super().__init__(*args, **kwargs)
                self.gauge = gauge

            def frame(self, f, lo, n=2, where='frame'):
                w, F = super().frame(f, lo, n=n, where=where)
                if self.gauge != 'raw':
                    normal = self.m.normal(self.m.frac_to_k(f))
                    F[:, 1] *= np.sign(np.dot(np.cross(F[:, 0], F[:, 1]), normal))
                    if self.gauge == 'reflected':
                        F = F @ np.diag([1., -1.])
                    if self.gauge == 'SO2':
                        x, y = self.m.frac_to_k(f)
                        F = F @ ref.rotation(.7*np.sin(x) + .4*np.cos(y))
                return w, F

        def evaluate(name, model, mesh, gauge='raw', sewings=None):
            trace = Trace()
            sampler = GaugedSampler(model, U=np.eye(3), policy=policy, ledger=trace, name=name, gauge=gauge)
            record = dict(name=name, mesh=list(mesh), gauge=gauge, model=dict(kind=model.kind, m=model.m, folds=model.folds))
            try:
                _, first = sampler.frame([0., 0.], 0, where='adapter:orientation')
                record['base_orientation'] = float(np.sign(np.dot(np.cross(first[:, 0], first[:, 1]), model.normal(model.frac_to_k([0., 0.])))))
                result = prod.euler_wilson(sampler, lo=0, nf1=mesh[0], nf2=mesh[1],
                                           sewings=(np.eye(3), np.eye(3)) if sewings is None else sewings)
                record.update(status='returned', result=result)
                # Production loops in f2 then scans f1. The reference loops kx
                # then scans ky. Interchanging these directions reverses sign.
                record['oriented_euler'] = -record['base_orientation'] * result['euler_estimate']
            except prod.Rejected as exc:
                record.update(status='rejected', rejection=exc.record)
            record['diagnostics'] = trace.summary()
            cases.append(record)
            return record

        for m, e in [(-1, 2), (-3, 0)]:
            for mesh in [48, 96]:
                name = f'sphere_m{m}_mesh{mesh}'
                case = evaluate(name, Model(ref, m), (mesh, mesh))
                check(name, case['status'] == 'returned' and abs(case.get('oriented_euler', 999) - e) < 1e-10,
                      expected=e, observed=case.get('oriented_euler'), category='production_calibration')
                strict = strict_curve(ref, mesh, mesh, m)
                check(name + '_strict_reference', abs(strict['winding'] - e) < 1e-10,
                      category='reference_calibration', **strict)

        gauged = {}
        for gauge in ['oriented', 'reflected', 'SO2']:
            case = evaluate('gauge_' + gauge, Model(ref), (48, 48), gauge=gauge)
            gauged[gauge] = case
            check('gauge_' + gauge, case['status'] == 'returned' and abs(case.get('oriented_euler', 999)-2) < 1e-10,
                  expected=2, observed=case.get('oriented_euler'), category='gauge_control')
        a, b, c = [gauged[g]['result']['euler_estimate'] for g in ['oriented', 'reflected', 'SO2']]
        check('reflection_reverses_raw_winding', abs(a + b) < 1e-10 and abs(a) > 1,
              original=a, reflected=b, category='gauge_control')
        check('SO2_preserves_raw_winding', abs(a - c) < 1e-10, original=a, gauged=c, category='gauge_control')

        controls = [
            ('coarse_axis1_links', Model(ref), (5, 48), 'overlap', None),
            ('coarse_axis2_links', Model(ref), (48, 5), 'overlap', None),
            ('coarse_transverse_phase', Model(ref), (24, 24), 'phase_resolution', None),
            ('mobius_axis1', Model(ref, kind='mobius0'), (48, 48), 'nonorientable_axis1', None),
            ('mobius_axis2', Model(ref, kind='mobius1'), (48, 48), 'nonorientable_axis2', None),
            ('complex_H', Model(ref, kind='complex'), (4, 4), 'matrix_precondition', None),
            ('external_gap_closure', Model(ref, kind='gapless'), (4, 4), 'external_gap', None),
        ]
        bad = np.array([[np.cos(.4), 0., np.sin(.4)], [0., 1., 0.], [-np.sin(.4), 0., np.cos(.4)]])
        controls.append(('wrong_sewing', Model(ref, m=-3), (48, 48), 'sewing_loss', (bad, np.eye(3))))
        for name, model, mesh, code, sewing in controls:
            case = evaluate(name, model, mesh, sewings=sewing)
            observed = case.get('rejection', {}).get('code')
            check(name + '_refused', case['status'] == 'rejected' and observed == code,
                  expected_code=code, observed_code=observed, category='refusal_control')

        for nx, ny, code in [(5, 48, 'reference_link_resolution'), (48, 24, 'reference_transverse_phase_resolution')]:
            observed = None
            try:
                strict_curve(ref, nx, ny, -1)
            except ValueError as exc:
                observed = str(exc)
            check(f'strict_reference_{nx}_{ny}_refused', observed == code,
                  expected_code=code, observed_code=observed, category='refusal_control')

        # A bounded, predeclared alias witness: 49 folds sampled on 48 intervals.
        # The two Hamiltonians agree at every sampled point, while the analytic
        # degree multiplies by 49. This demonstrates a limit, not a successful
        # measurement of the high-frequency texture's Euler number.
        fast = Model(ref, folds=49)
        slow = Model(ref)
        maximum = 0.
        for f1 in np.linspace(0, 1, 49):
            for f2 in np.linspace(0, 1, 49):
                k = fast.frac_to_k([f1, f2])
                maximum = max(maximum, float(np.max(np.abs(fast.H(k) - slow.H(k)))))
        alias = evaluate('alias_49_folds_on_48_intervals', fast, (48, 48))
        check('alias_witness_grid_identity', maximum < 1e-10, max_H_difference=maximum, category='sampling_limit')
        check('alias_witness_pass_is_not_truth', alias['status'] == 'returned' and abs(alias.get('oriented_euler', 999)-2) < 1e-10,
              analytic_euler=98, sampled_oriented_euler=alias.get('oriented_euler'),
              category='sampling_limit', interpretation='Expected false acceptance of an aliased high-frequency texture; not evidence that its Euler number is 2')

        # This benchmark's exactly degenerate pair is unsuitable for a nodal charge.
        sampler = prod.Sampler(Model(ref), U=np.eye(3), policy=policy)
        points = np.array([[.5 + .05*np.cos(t), .5 + .05*np.sin(t)] for t in np.linspace(0, 2*np.pi, 17)])
        points[-1] = points[0]
        base = sampler.frame(points[0], 0)[1]
        code = None
        try:
            prod.node_winding(sampler, points, base, 0, 'degenerate_pair')
        except prod.Rejected as exc:
            code = exc.record['code']
        check('degenerate_pair_node_charge_refused', code == 'loop_internal_gap', observed_code=code, category='scope_control')

        result = dict(schema='twistronics_reference_calibration_v1', passed=all(c['passed'] for c in checks),
                      source_sha256=sha(__file__), plan_sha256=sha(HERE/'PLAN.json'),
                      archive_sha256=sha(ARCHIVE), guarded_source_sha256=GUARDED_SHA,
                      reference_source_sha256=sha(REFERENCE), policy=asdict(policy),
                      units='Synthetic Hamiltonian energies interpreted as meV by the production API; no physical TBG parameters',
                      environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                      checks=checks, cases=cases,
                      limits=['Synthetic production-API calibration only; no physical validation or TBG rerun',
                              'Explicit identity sewings on synthetic periodic models; not a test of finite-cutoff TBG shift_matrix',
                              'Bounds guard sampled links and phases, not variations between samples; alias witness intentionally passes',
                              'The archived consumer/verifier corrections remain with Fable'])
        (out/'RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
        for c in checks:
            print(('PASS ' if c['passed'] else 'FAIL ') + c['name'])
        print(f"{sum(c['passed'] for c in checks)}/{len(checks)} checks; overall={result['passed']}")
        return 0 if result['passed'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.output))
