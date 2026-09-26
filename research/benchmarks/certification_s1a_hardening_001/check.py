#!/usr/bin/env python3
"""Bounded S1a hardening bridge for FC49-77-K-Bm025-v2.

This packet assembles the two declared finite Hamiltonians with Arb balls,
checks the nested principal-submatrix identity, and compares midpoint matrices
to the archived floating assembler at the three predeclared bridge points.
It binds the case constants and harmonic semantics, refuses unsupported
constructor values, executes the archived harmonic helper, and binds the
exact python-flint wheel/native version. It performs no domain subdivision,
inertia certification, projector work,
transport, seam calculation, topology, or parameter sweep.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

import numpy as np
from flint import arb, ctx

HERE = Path(__file__).resolve()
PACKET_DIR = HERE.parent
REMOTE_ROOT = HERE.parents[3] if len(HERE.parents) > 3 else HERE.parents[1]
ROOT = REMOTE_ROOT if (REMOTE_ROOT / "docs/certification-readiness/CASE.json").exists() else HERE.parents[1]
CASE_PATH = (ROOT / "docs/certification-readiness/CASE.json" if
             (ROOT / "docs/certification-readiness/CASE.json").exists() else ROOT / "CASE.json")
ARCHIVE_PATH = (ROOT / "research/benchmarks/migration_contract_review/partner_v078p.zip" if
                (ROOT / "research/benchmarks/migration_contract_review/partner_v078p.zip").exists()
                else ROOT / "partner_v078p.zip")
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else PACKET_DIR / "RUN")
WHEEL_PATH = Path(sys.argv[2]) if len(sys.argv) > 2 else None
WHEEL_LOCK_PATH = PACKET_DIR / "WHEEL_LOCK.json"
REVIEWED_COMMIT = "38984059e5a6a755c0a9c24400f2030100ad024a"
ARCHIVE_IMPORT_CLOSURE = (
    "bm_strain.py", "knobs.py", "braid.py", "euler.py", "gate.py",
    "fast_engine.py", "tbg_ref.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(s: str | int) -> arb:
    return arb(str(s))


def rot(t: arb):
    c, s = t.cos(), t.sin()
    return ((c, -s), (s, c))


def mm(A, B):
    return tuple(tuple(sum((A[i][k] * B[k][j] for k in range(len(B))), arb(0))
                       for j in range(len(B[0]))) for i in range(len(A)))


def mv(A, v):
    return tuple(sum((A[i][k] * v[k] for k in range(len(v))), arb(0))
                 for i in range(len(A)))


def tr(A):
    return tuple(zip(*A))


def addv(a, b):
    return tuple(x + y for x, y in zip(a, b))


def subv(a, b):
    return tuple(x - y for x, y in zip(a, b))


def scalev(a, x):
    return tuple(x * y for y in a)


def inv2(A):
    d = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    if d.contains(0):
        raise RuntimeError("GEOMETRY_DENOMINATOR_UNRESOLVED")
    return ((A[1][1] / d, -A[0][1] / d), (-A[1][0] / d, A[0][0] / d)), d


def zeros(n):
    return [[arb(0) for _ in range(n)] for _ in range(n)]


def add_block(H, r, c, B):
    for i in range(2):
        for j in range(2):
            H[r + i][c + j] += B[i][j]


def transpose_block(B):
    return ((B[0][0], B[1][0]), (B[0][1], B[1][1]))


def validate_case(case):
    if case.get("case_id") != "FC49-77-K-Bm025-v2":
        raise RuntimeError("UNSUPPORTED_CASE_ID")
    model = case.get("model", {})
    p = model.get("constructor", {})
    expected = {
        "phi_deg": "0", "mass": "0", "Dfield": "0", "w_kappa": "0",
        "w_mode": "average", "geometry": "exact", "kinetic": "lab_nn_full",
    }
    for key, value in expected.items():
        if p.get(key) != value:
            raise RuntimeError("UNSUPPORTED_CONSTRUCTOR_" + key.upper())
    if model.get("valley") != 1:
        raise RuntimeError("UNSUPPORTED_VALLEY")
    if model.get("harmonic") != {
        "mat": "sz", "use_sin": True, "layer_sign": 1, "which": [0, 1, 2]
    }:
        raise RuntimeError("UNSUPPORTED_HARMONIC_SEMANTICS")
    if case.get("model", {}).get("index_set_supplied_explicitly") is not True:
        raise RuntimeError("EXPLICIT_INDEX_SET_REQUIRED")
    constants = model.get("constants", {})
    for key in ("HBARV_meV_angstrom", "A_LAT_angstrom"):
        if key not in constants:
            raise RuntimeError("MISSING_CONSTANT_" + key.upper())
        q(constants[key])
    q(model["B"])
    return expected


def guard_mutation_controls(case):
    import copy
    controls = {}
    mutations = {
        "phi_deg": "1", "mass": "1", "Dfield": "1", "w_kappa": "1",
        "w_mode": "raw", "geometry": "legacy", "kinetic": "unsupported",
    }
    for key, value in mutations.items():
        changed = copy.deepcopy(case)
        changed["model"]["constructor"][key] = value
        try:
            validate_case(changed)
        except RuntimeError as exc:
            controls[key] = str(exc) == "UNSUPPORTED_CONSTRUCTOR_" + key.upper()
        else:
            controls[key] = False
    for name, mutate, expected in (
        ("valley", lambda c: c["model"].__setitem__("valley", -1), "UNSUPPORTED_VALLEY"),
        ("harmonic", lambda c: c["model"]["harmonic"].__setitem__("use_sin", False), "UNSUPPORTED_HARMONIC_SEMANTICS"),
        ("explicit_index", lambda c: c["model"].__setitem__("index_set_supplied_explicitly", False), "EXPLICIT_INDEX_SET_REQUIRED"),
    ):
        changed = copy.deepcopy(case); mutate(changed)
        try:
            validate_case(changed)
        except RuntimeError as exc:
            controls[name] = str(exc) == expected
        else:
            controls[name] = False
    return controls


def model_geometry(p, constants):
    pi = arb.pi()
    theta = pi * q(p["theta_deg"]) / q(180)
    eps, nu, beta = q(p["eps"]), q(p["nu"]), q(p["beta"])
    alat = q(constants["A_LAT_angstrom"])
    E = ((eps, arb(0)), (arb(0), -eps * nu))
    Es = [tuple(tuple(-x / 2 for x in row) for row in E),
          tuple(tuple(x / 2 for x in row) for row in E)]
    ths = [-theta / 2, theta / 2]
    KD = (q(4) * pi / (q(3) * alat), arb(0))

    def lat(El, th, v):
        Iplus = ((q(1) + El[0][0], El[0][1]), (El[1][0], q(1) + El[1][1]))
        inv, den = inv2(Iplus)
        return mv(tr(inv), mv(rot(th), v)), den

    Kl, Al, denoms = [], [], []
    root3 = q(3).sqrt()
    for El, th in zip(Es, ths):
        kval, den = lat(El, th, KD)
        Kl.append(kval); denoms.append(den)
        Ec = mm(mm(rot(-th), El), rot(th))
        Ac = (root3 * beta / (q(2) * alat) * (Ec[0][0] - Ec[1][1]),
              root3 * beta / (q(2) * alat) * (-q(2) * Ec[0][1]))
        Al.append(mv(rot(th), Ac))
    qs = []
    for j in range(3):
        Kj = mv(rot(q(2) * pi * q(j) / q(3)), KD)
        K1, d1 = lat(Es[0], ths[0], Kj)
        K2, d2 = lat(Es[1], ths[1], Kj)
        denoms += [d1, d2]
        qs.append(subv(K1, K2))
    G1, G2 = subv(qs[1], qs[0]), subv(qs[2], qs[0])
    Ms = []
    for El, th in zip(Es, ths):
        V = ((q(1) + (q(1) - beta) * El[0][0], (q(1) - beta) * El[0][1]),
             ((q(1) - beta) * El[1][0], q(1) + (q(1) - beta) * El[1][1]))
        Ms.append(mm(rot(-th), V))
    return dict(pi=pi, theta=theta, Es=Es, ths=ths, KD=KD, Kl=Kl, Al=Al,
                qs=qs, G1=G1, G2=G2, Ms=Ms, denominators=denoms)


def assemble_coefficients(indices, case):
    model = case["model"]
    p, constants, harmonic = model["constructor"], model["constants"], model["harmonic"]
    geo = model_geometry(p, constants)
    nG, D = len(indices), 4 * len(indices)
    pos = {tuple(v): i for i, v in enumerate(indices)}
    H0, Hx, Hy = zeros(D), zeros(D), zeros(D)
    w1, ratio = q(p["w1"]), q(p["ratio"])
    w0, hbarv = ratio * w1, q(constants["HBARV_meV_angstrom"])
    pi = geo["pi"]

    # Interlayer tunnelling, directly in the declared real basis:
    # I -> I, sx -> sz, sy -> -sx.
    for j, shift in enumerate(((0, 0), (1, 0), (0, 1))):
        phi = q(2) * pi * q(j) / q(3)
        c, s = phi.cos(), phi.sin()
        T = ((w0 + w1 * c, -w1 * s), (-w1 * s, w0 - w1 * c))
        for mn, i in pos.items():
            target = (mn[0] + shift[0], mn[1] + shift[1])
            if target in pos:
                i2 = pos[target]
                r, col = 2 * nG + 2 * i2, 2 * i
                add_block(H0, r, col, T)
                add_block(H0, col, r, transpose_block(T))

    # Scalar cosine moire potential.
    Vscalar = q("0.5") * q(p["A_scalar"]) * w1
    for lay in range(2):
        off = 2 * nG * lay
        for mn, i in pos.items():
            for dm, dn in ((1, 0), (-1, 0), (0, 1), (0, -1), (-1, 1), (1, -1)):
                target = (mn[0] + dm, mn[1] + dn)
                if target in pos:
                    j = pos[target]
                    add_block(H0, off + 2 * j, off + 2 * i,
                              ((Vscalar, arb(0)), (arb(0), Vscalar)))

    # Sine-sigma_z harmonic. In the real basis each directed block is
    # sign*c*[[0,1],[-1,0]], c=B*w1/2.
    c_harm = q("0.5") * q(model["B"]) * w1
    directions = ((1, 0), (0, 1), (-1, 1))
    for lay in range(2):
        off = 2 * nG * lay
        layer_factor = q(1 if lay == 0 else harmonic["layer_sign"])
        for j in harmonic["which"]:
            dm, dn = directions[j]
            for sign in (1, -1):
                B = ((arb(0), layer_factor * q(sign) * c_harm),
                     (-layer_factor * q(sign) * c_harm, arb(0)))
                for mn, i in pos.items():
                    target = (mn[0] + sign * dm, mn[1] + sign * dn)
                    if target in pos:
                        add_block(H0, off + 2 * pos[target], off + 2 * i, B)

    # Affine kinetic blocks in fractional coordinates.
    for lay in range(2):
        M, Al = geo["Ms"][lay], geo["Al"][lay]
        shift = geo["qs"][0] if lay == 1 else (arb(0), arb(0))
        dpx, dpy = mv(M, geo["G1"]), mv(M, geo["G2"])
        off = 2 * nG * lay
        for i, (m, n) in enumerate(indices):
            G = addv(scalev(geo["G1"], q(m)), scalev(geo["G2"], q(n)))
            pp0 = mv(M, subv(addv(G, shift), Al))
            for H, pp in ((H0, pp0), (Hx, dpx), (Hy, dpy)):
                a, b = hbarv * pp[0], hbarv * pp[1]
                add_block(H, off + 2 * i, off + 2 * i, ((a, -b), (-b, -a)))
    return (H0, Hx, Hy), geo


def mid_float(H):
    return np.array([[float(x.mid()) for x in row] for row in H], dtype=float)


def radius_frobenius(H):
    s = arb(0)
    for row in H:
        for x in row:
            r = x.rad()
            s += r * r
    return float(s.sqrt().upper())


def matrix_ball_digest(Hs):
    h = hashlib.sha256()
    for name, H in zip(("H0", "Hx", "Hy"), Hs):
        h.update(name.encode() + b"\0")
        for row in H:
            for x in row:
                h.update(str(x.lower()).encode() + b"," + str(x.upper()).encode() + b"\n")
    return h.hexdigest()


def contains_zero(x):
    return x.contains(0)


def compare_nested(A, B, mapping):
    worst = 0.0
    failures = 0
    for name_i, (Ha, Hb) in enumerate(zip(A, B)):
        for i, bi in enumerate(mapping):
            for j, bj in enumerate(mapping):
                d = Ha[i][j] - Hb[bi][bj]
                if not contains_zero(d):
                    failures += 1
                worst = max(worst, float(abs(d).upper()))
    return failures, worst


def float_bridge(case, coeffs, src):
    sys.path.insert(0, str(src))
    from bm_strain import BM, sz
    from fast_engine import realify
    from knobs import add_harmonic
    p = case["model"]["constructor"]
    kwargs = dict(N=int(p["N"]), eps=float(p["eps"]), phi_deg=float(p["phi_deg"]),
                  theta_deg=float(p["theta_deg"]), A_scalar=float(p["A_scalar"]),
                  ratio=float(p["ratio"]), w1=float(p["w1"]), nu=float(p["nu"]),
                  beta=float(p["beta"]), kinetic=p["kinetic"], geometry=p["geometry"],
                  cutoff_tol=float(p["cutoff_tol"]), mass=float(p["mass"]),
                  Dfield=float(p["Dfield"]), w_kappa=float(p["w_kappa"]),
                  w_mode=p["w_mode"], valley=case["model"]["valley"])
    results = {}
    for key in ("a", "b"):
        idx = case["cutoffs"][key]["ordered_indices"]
        m = BM(index_set=idx, **kwargs)
        harmonic = case["model"]["harmonic"]
        matrices = {"sz": sz}
        add_harmonic(m, float(case["model"]["B"]), mat=matrices[harmonic["mat"]],
                     layer_sign=harmonic["layer_sign"], which=tuple(harmonic["which"]),
                     use_sin=harmonic["use_sin"])
        mids = [mid_float(H) for H in coeffs[key]]
        rows = []
        pair = case["cutoffs"][key]["selected_bands_zero_based"]
        for x, y in ((0, 0), (1, 0), (0, 1)):
            exact_mid = mids[0] + x * mids[1] + y * mids[2]
            archived = realify(m.H(m.frac_to_k(np.array([x, y], float)))).real
            w = np.linalg.eigvalsh(archived)
            lo, hi = pair
            rows.append(dict(point=[x, y], max_abs_midpoint_difference_meV=float(np.max(np.abs(exact_mid - archived))),
                             archived_imaginary_residual_meV=float(np.max(np.abs(realify(m.H(m.frac_to_k(np.array([x, y], float)))).imag))),
                             diagnostic_lower_external_gap_meV=float(w[lo] - w[lo - 1]),
                             diagnostic_upper_external_gap_meV=float(w[hi + 1] - w[hi])))
        results[key] = rows
    return results


def main():
    case = json.loads(CASE_PATH.read_text())
    expected_guards = validate_case(case)
    mutation_controls = guard_mutation_controls(case)
    if not all(mutation_controls.values()):
        raise RuntimeError("GUARD_MUTATION_CONTROL_FAILED")
    if WHEEL_PATH is None or not WHEEL_PATH.is_file():
        raise RuntimeError("EXACT_PYTHON_FLINT_WHEEL_REQUIRED")
    wheel_lock = json.loads(WHEEL_LOCK_PATH.read_text())
    if WHEEL_PATH.name != wheel_lock["filename"] or sha256(WHEEL_PATH) != wheel_lock["sha256"]:
        raise RuntimeError("PYTHON_FLINT_WHEEL_LOCK_MISMATCH")
    flint = __import__("flint")
    if flint.__version__ != wheel_lock["python_flint_version"]:
        raise RuntimeError("PYTHON_FLINT_VERSION_MISMATCH")
    if flint.__FLINT_VERSION__ != wheel_lock["native_flint_version"]:
        raise RuntimeError("NATIVE_FLINT_VERSION_MISMATCH")
    OUT.mkdir(parents=True, exist_ok=False)
    if sha256(ARCHIVE_PATH) != case["basis_of_declaration"]["archive_sha256"]:
        raise RuntimeError("ARCHIVE_HASH_MISMATCH")
    ctx.prec = 128
    coeffs, geos = {}, {}
    for key in ("a", "b"):
        coeffs[key], geos[key] = assemble_coefficients(case["cutoffs"][key]["ordered_indices"], case)
    mapping = case["inclusion"]["column_to_row"]
    nested_failures, nested_worst = compare_nested(coeffs["a"], coeffs["b"], mapping)
    with zipfile.ZipFile(ARCHIVE_PATH) as outer:
        nested = outer.read("partner_v074p.zip")
    member_hashes = {}
    with zipfile.ZipFile(BytesIO(nested)) as inner, tempfile.TemporaryDirectory(prefix="s1a_source_") as td:
        src = Path(td)
        for name in ARCHIVE_IMPORT_CLOSURE:
            data = inner.read(name)
            member_hashes[name] = hashlib.sha256(data).hexdigest()
            (src / name).write_bytes(data)
        bridge = float_bridge(case, coeffs, src)
    radii = {k: dict(zip(("H0", "Hx", "Hy"), map(radius_frobenius, coeffs[k]))) for k in ("a", "b")}
    domain_radius = {k: radii[k]["H0"] + radii[k]["Hx"] + radii[k]["Hy"] for k in ("a", "b")}
    max_bridge = max(r["max_abs_midpoint_difference_meV"] for v in bridge.values() for r in v)
    max_imag = max(r["archived_imaginary_residual_meV"] for v in bridge.values() for r in v)
    denom_ok = all(not d.contains(0) for g in geos.values() for d in g["denominators"])
    checks = {
        "archive_sha256_matches": True,
        "dimensions_match": all(len(coeffs[k][0]) == case["cutoffs"][k]["dimension"] for k in ("a", "b")),
        "geometry_denominators_exclude_zero": denom_ok,
        "nested_affine_coefficients_overlap": nested_failures == 0,
        "assembly_radius_target_met": max(domain_radius.values()) <= 1e-8,
        "three_point_float_bridge_under_1e-9_meV": max_bridge <= 1e-9,
        "archived_real_basis_residual_under_1e-9_meV": max_imag <= 1e-9,
        "case_semantics_bound": bool(expected_guards),
        "unsupported_constructor_mutations_refused": all(mutation_controls.values()),
        "archived_harmonic_helper_executed": True,
        "python_flint_wheel_and_native_version_bound": True,
    }
    status = "PASS_PHYSICAL_AFFINE_ASSEMBLY_BRIDGE" if all(checks.values()) else "INCONCLUSIVE_OR_FAILED"
    result = {
        "schema": "twistronics_s1a_hardening_v1",
        "case_id": case["case_id"],
        "reviewed_commit": REVIEWED_COMMIT,
        "status": status,
        "claim_ceiling": "PHYSICAL_AFFINE_ASSEMBLY_ONLY_NO_UNIFORM_ISOLATION_OR_TOPOLOGY",
        "checks": checks,
        "case_binding": {
            "constructor_guards": expected_guards,
            "guard_mutation_controls": mutation_controls,
            "constants": case["model"]["constants"],
            "B": case["model"]["B"],
            "harmonic": case["model"]["harmonic"],
            "archived_helper": "knobs.add_harmonic",
        },
        "runtime_binding": wheel_lock,
        "cutoffs": {k: {"dimension": len(coeffs[k][0]), "coefficient_ball_sha256": matrix_ball_digest(coeffs[k]),
                         "coefficient_frobenius_radius_upper_meV": radii[k],
                         "whole_domain_arithmetic_radius_upper_meV": domain_radius[k],
                         "diagnostic_bridge": bridge[k]} for k in ("a", "b")},
        "nested_identity": {"nonoverlap_count": nested_failures, "worst_difference_abs_upper_meV": nested_worst},
        "limits": ["No interval inertia or uniform external-gap certificate was attempted.",
                   "Three floating eigensolver evaluations per cutoff are diagnostics only.",
                   "No projector, transport, seam, integer, relative-class, cutoff-convergence, or experimental claim."],
    }
    (OUT / "RESULTS.json").write_text(json.dumps(result, indent=2) + "\n")
    env = {"python": platform.python_version(), "platform": platform.platform(),
           "python_flint": flint.__version__, "native_flint": flint.__FLINT_VERSION__,
           "python_flint_wheel": wheel_lock, "arb_precision_bits": ctx.prec,
           "worker_processes": 1, "physical_cases": 1, "parameter_sweeps": 0}
    (OUT / "ENVIRONMENT.json").write_text(json.dumps(env, indent=2) + "\n")
    sources = {
        "docs/certification-readiness/CASE.json": sha256(CASE_PATH),
        "research/benchmarks/migration_contract_review/partner_v078p.zip": sha256(ARCHIVE_PATH),
        **{f"research/benchmarks/migration_contract_review/partner_v078p.zip!partner_v074p.zip!{name}": digest
           for name, digest in member_hashes.items()},
        "research/benchmarks/certification_s1a_hardening_001/check.py": sha256(Path(__file__)),
        "research/benchmarks/certification_s1a_hardening_001/verify.py": sha256(Path(__file__).with_name("verify.py")),
        "research/benchmarks/certification_s1a_hardening_001/README.md": sha256(Path(__file__).with_name("README.md")),
        "research/benchmarks/certification_s1a_hardening_001/WHEEL_LOCK.json": sha256(WHEEL_LOCK_PATH),
        "external-wheel://" + WHEEL_PATH.name: sha256(WHEEL_PATH),
    }
    (OUT / "SOURCE_BINDINGS.json").write_text(json.dumps(sources, indent=2) + "\n")
    manifest = {p.name: sha256(p) for p in sorted(OUT.iterdir())}
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(status)
    print(json.dumps({"max_bridge_meV": max_bridge, "domain_radius_meV": domain_radius,
                      "nested_nonoverlap": nested_failures}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
