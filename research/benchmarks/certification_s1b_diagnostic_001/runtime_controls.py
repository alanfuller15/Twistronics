#!/usr/bin/env python3
"""Exercise runtime collection and offline mutations without model calculations."""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import tempfile
from pathlib import Path

import runtime_identity as runtime


def run(wheel: Path) -> dict:
    # Match worker startup before importing any native runtime. This control
    # is standalone and must not depend on the caller's BLAS thread defaults.
    for name in runtime.THREAD_VARIABLES:
        os.environ[name] = "1"
    import flint
    import numpy as np
    flint.ctx.prec = 128
    flint.ctx.threads = 1
    # An accidental eigensolver call in this provenance check is a test failure.
    original_eigh = np.linalg.eigh
    def forbidden_eigh(*args, **kwargs):
        raise AssertionError("RUNTIME_CONTROLS_MUST_NOT_CALL_EIGENSOLVER")
    np.linalg.eigh = forbidden_eigh
    try:
        retained = runtime.collect(wheel)
    finally:
        np.linalg.eigh = original_eigh
    controls = [{"name": "actual_locked_runtime_collect_without_eigh", "pass": True}]
    runtime.verify(retained)
    controls.append({"name": "offline_exact_build_identity_accepts", "pass": True})

    def reject(name, mutation):
        changed = copy.deepcopy(retained)
        mutation(changed)
        try:
            runtime.verify(changed)
        except (ValueError, TypeError, KeyError) as exc:
            controls.append({"name": name, "pass": True, "rejection_type": type(exc).__name__})
        else:
            raise AssertionError("MUTATION_NOT_REJECTED:" + name)

    reject("wrong_wheel_digest", lambda p: p["wheel"].update(sha256="0" * 64))
    reject("wrong_wheel_version", lambda p: p["wheel"].update(python_flint_version="99.0"))
    reject("wrong_installed_native_digest", lambda p: p["installed_native_members"][0].update(sha256="0" * 64))
    reject("missing_installed_native", lambda p: (p["installed_native_members"].pop(), p.update(installed_native_member_count=p["installed_native_member_count"]-1)))
    reject("changed_locked_native_inventory", lambda p: p["wheel_native_members"].pop())
    required = runtime._locks()[1]["required_mapped_members"][0]
    reject("missing_mapped_flint_library_with_adjusted_count", lambda p: (p.update(mapped_flint_members=[r for r in p["mapped_flint_members"] if r["member"] != required]), p.update(mapped_flint_member_count=p["mapped_flint_member_count"]-1)))
    reject("wrong_mapped_native_digest", lambda p: p["mapped_flint_members"][0].update(sha256="0" * 64))
    reject("binding_boolean_not_true", lambda p: p.update(loaded_extension_bound_to_wheel=1))
    reject("maps_not_checked", lambda p: p.update(proc_maps_checked=False))
    reject("loaded_extension_identity", lambda p: p.update(loaded_extension_member="flint/fake.so"))
    reject("native_flint_version", lambda p: p.update(native_flint_version="0.0"))
    reject("python_build_digest", lambda p: p["python"]["executable"].update(sha256="0" * 64))
    reject("python_unredacted_path", lambda p: p["python"]["executable"].update(member="/home/private/python"))
    reject("python_cache_tag", lambda p: p["python"].update(cache_tag="cpython-999"))
    reject("python_shared_mapping", lambda p: p["python"].update(shared_library_mapping="WRONG"))
    reject("numpy_version", lambda p: p["numpy"].update(version="0.0"))
    mapped_numpy = {r["member"] for r in retained["numpy"]["mapped_native_members"]}
    not_mapped = next(r["member"] for r in retained["numpy"]["installed_native_members"] if r["member"] not in mapped_numpy)
    reject("missing_unmapped_numpy_member_with_adjusted_count", lambda p: (p["numpy"].update(installed_native_members=[r for r in p["numpy"]["installed_native_members"] if r["member"] != not_mapped]), p["numpy"].update(installed_native_member_count=p["numpy"]["installed_native_member_count"]-1)))
    reject("numpy_binary_digest", lambda p: p["numpy"]["installed_native_members"][0].update(sha256="0" * 64))
    reject("missing_mapped_numpy_linalg", lambda p: (p["numpy"].update(mapped_native_members=[r for r in p["numpy"]["mapped_native_members"] if "_umath_linalg" not in r["member"]]), p["numpy"].update(mapped_native_member_count=p["numpy"]["mapped_native_member_count"]-1)))
    reject("missing_blas_identity", lambda p: p.update(blas=[]))
    reject("blas_version", lambda p: p["blas"][0].update(version="0.0"))
    reject("blas_digest", lambda p: p["blas"][0].update(sha256="0" * 64))
    reject("blas_thread_count", lambda p: p["blas"][0].update(num_threads=2))
    reject("blas_boolean_thread_count", lambda p: p["blas"][0].update(num_threads=True))
    reject("inspector_digest", lambda p: p["threadpool_inspector"]["source"].update(sha256="0" * 64))
    reject("wrong_precision", lambda p: p["settings"].update(initial_precision_bits=256))
    reject("floating_precision", lambda p: p["settings"].update(initial_precision_bits=128.0))
    reject("floating_allowed_precision", lambda p: p["settings"].update(allowed_precision_bits=[128.0, 256]))
    reject("boolean_flint_threads", lambda p: p["settings"].update(flint_threads=True))
    reject("wrong_native_thread_setting", lambda p: p["settings"]["thread_environment"].update(BLIS_NUM_THREADS="2"))
    reject("unapproved_environment_keys", lambda p: p["settings"]["thread_environment"].update(HOME="redacted"))
    reject("unexpected_provenance_field", lambda p: p.update(hostname="private"))
    reject("boolean_schema_version", lambda p: p.update(schema_version=True))
    with tempfile.TemporaryDirectory(prefix="diagnostic-runtime-negative-") as directory:
        bad = Path(directory) / wheel.name
        bad.write_bytes(b"this is not the locked wheel")
        try:
            runtime.collect(bad)
        except ValueError:
            controls.append({"name": "collector_rejects_actual_wrong_wheel_bytes", "pass": True})
        else:
            raise AssertionError("COLLECTOR_ACCEPTED_BAD_WHEEL")
    return {"schema_version": 1, "scope": "Native imports, binary hashing and provenance mutations only; no CASE, model, eigensolver or interval-LDL execution",
            "passed": len(controls), "controls": controls, "observed_locked_runtime_provenance": retained}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--flint-site", type=Path,
                        help="optional existing flint installation for provenance-only controls")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.flint_site is not None:
        sys.path.append(str(args.flint_site.resolve(strict=True)))
    result = run(args.wheel.resolve(strict=True))
    data = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)
    print(json.dumps({"status": "PASS_RUNTIME_PROVENANCE_CONTROLS", "passed": result["passed"],
                      "model_or_numerical_calls": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
