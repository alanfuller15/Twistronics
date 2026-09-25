"""Physical runtime collection and standard-library-only offline validation.

Collection hashes actual loaded/installed binaries. Offline validation checks the
locked wheel members and the complete Python/NumPy/BLAS build identities against
NATIVE_LOCK.json rather than inferring native identity from version labels.
No native package is imported by this module or by verify().
"""
from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import os
import platform
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
THREAD_VARIABLES = (
    "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
)


def _fail(label: str) -> None:
    raise ValueError("RUNTIME_IDENTITY_" + label)


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def _record(path: Path, member: str) -> dict:
    return {"member": member, "sha256": _digest(path), "bytes": path.stat().st_size}


def _native(name: str) -> bool:
    return name.endswith(".so") or ".so." in name


def _locks() -> tuple[dict, dict]:
    wheel = json.loads((ROOT / "research/benchmarks/certification_s1a_hardening_001/WHEEL_LOCK.json").read_text())
    native = json.loads((HERE / "NATIVE_LOCK.json").read_text())
    if native.get("schema_version") != 1 or native.get("wheel") != wheel:
        _fail("NATIVE_LOCK_BINDING")
    _inventory(native.get("native_members"), "flint")
    names = [r["member"] for r in native["native_members"]]
    required = sorted(n for n in names if n.startswith("python_flint.libs/"))
    if native.get("required_mapped_members") != required or not required:
        _fail("NATIVE_LOCK_MAPPED_SET")
    if native.get("loaded_extension_member") not in names:
        _fail("NATIVE_LOCK_EXTENSION")
    return wheel, native


def _safe_text(value, *, token: bool = False) -> bool:
    return (isinstance(value, str) and 0 < len(value) <= 256
            and not any(c in value for c in ("/", "\\", "\n", "\r", "\x00"))
            and (not token or re.fullmatch(r"[A-Za-z0-9_.+() -]+", value) is not None))


def _inventory(rows, namespace: str | None = None) -> dict[str, dict]:
    if not isinstance(rows, list) or not rows:
        _fail("EMPTY_BINARY_INVENTORY")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"member", "sha256", "bytes"}:
            _fail("BINARY_RECORD_SCHEMA")
        name = row["member"]
        if not isinstance(name, str) or not name or len(name) > 256:
            _fail("BINARY_MEMBER_NAME")
        path = PurePosixPath(name)
        if path.is_absolute() or any(p in (".", "..") for p in path.parts) or "\\" in name:
            _fail("BINARY_MEMBER_PATH")
        if path.as_posix() != name or any(c in name for c in ("\x00", "\n", "\r")):
            _fail("BINARY_MEMBER_PATH")
        if namespace == "flint" and not (name.startswith("flint/") or name.startswith("python_flint.libs/")):
            _fail("FLINT_MEMBER_NAMESPACE")
        if namespace == "numpy" and not (name.startswith("numpy/") or name.startswith("numpy.libs/")):
            _fail("NUMPY_MEMBER_NAMESPACE")
        if namespace is None and len(path.parts) != 1:
            _fail("BINARY_BASENAME_REQUIRED")
        if name in result or not isinstance(row["sha256"], str) or re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is None:
            _fail("BINARY_DIGEST_OR_DUPLICATE")
        if type(row["bytes"]) is not int or row["bytes"] <= 0:
            _fail("BINARY_SIZE")
        result[name] = row
    if list(result) != sorted(result):
        _fail("BINARY_INVENTORY_ORDER")
    return result


def _mapped_paths() -> set[Path]:
    path = Path("/proc/self/maps")
    if not path.is_file():
        _fail("PROC_MAPS_REQUIRED")
    mapped = set()
    for line in path.read_text().splitlines():
        parts = line.split(maxsplit=5)
        if len(parts) == 6 and parts[5].startswith("/"):
            if parts[5].endswith(" (deleted)"):
                _fail("MAPPED_BINARY_DELETED")
            mapped.add(Path(parts[5]).resolve())
    return mapped


def _distribution_binaries(name: str) -> tuple[dict, dict[str, Path]]:
    dist = importlib.metadata.distribution(name)
    paths = {}
    for item in dist.files or []:
        member = str(item)
        if _native(member):
            if member in paths:
                _fail("DUPLICATE_DISTRIBUTION_MEMBER")
            paths[member] = Path(dist.locate_file(item)).resolve(strict=True)
    return {"version": dist.version}, paths


def collect(wheel: Path) -> dict:
    """Collect only inside the bounded physical worker before basis generation."""
    wheel_lock, native_lock = _locks()
    wheel = Path(wheel).resolve(strict=True)
    if wheel.name != wheel_lock["filename"] or _digest(wheel) != wheel_lock["sha256"]:
        _fail("WHEEL_LOCK_MISMATCH")
    with zipfile.ZipFile(wheel) as archive:
        names = [name for name in archive.namelist() if _native(name)]
        if len(names) != len(set(names)):
            _fail("DUPLICATE_WHEEL_MEMBER")
        members = [{"member": name, "bytes": len(archive.read(name)),
                    "sha256": hashlib.sha256(archive.read(name)).hexdigest()}
                   for name in sorted(names)]
    if members != native_lock["native_members"]:
        _fail("WHEEL_NATIVE_LOCK_MISMATCH")
    # These imports initialize native libraries; no eigensolver or LDL is called.
    flint = importlib.import_module("flint")
    np = importlib.import_module("numpy")
    importlib.import_module("numpy.linalg")
    pools_module = importlib.import_module("threadpoolctl")
    flint_meta, flint_paths = _distribution_binaries("python-flint")
    numpy_meta, numpy_paths = _distribution_binaries("numpy")
    if flint_meta["version"] != flint.__version__ or numpy_meta["version"] != np.__version__:
        _fail("DISTRIBUTION_VERSION_DISAGREES")
    flint_records = [_record(p, n) for n, p in sorted(flint_paths.items())]
    if flint_records != native_lock["native_members"]:
        _fail("INSTALLED_FLINT_NATIVE_SET_OR_BYTES")
    np_records = [_record(p, n) for n, p in sorted(numpy_paths.items())]
    _inventory(np_records, "numpy")
    extension = Path(importlib.import_module("flint.pyflint").__file__).resolve(strict=True)
    if extension != flint_paths[native_lock["loaded_extension_member"]]:
        _fail("LOADED_FLINT_EXTENSION_PATH")
    # Query the actual loaded library, not build-time package metadata.
    pools = pools_module.threadpool_info()
    mapped = _mapped_paths()
    mapped_flint = [_record(p, n) for n, p in sorted(flint_paths.items()) if p in mapped]
    mapped_numpy = [_record(p, n) for n, p in sorted(numpy_paths.items()) if p in mapped]
    blas = []
    for pool in pools:
        if pool.get("user_api") != "blas":
            continue
        p = Path(pool["filepath"]).resolve(strict=True)
        member = next((n for n, installed in numpy_paths.items() if p == installed), None)
        if member is None or p not in mapped:
            _fail("BLAS_NOT_BOUND_TO_MAPPED_NUMPY")
        blas.append({"member": member, "sha256": _digest(p), "bytes": p.stat().st_size,
                     "version": pool.get("version"), "num_threads": pool.get("num_threads"),
                     "internal_api": pool.get("internal_api"), "user_api": "blas",
                     "threading_layer": pool.get("threading_layer"),
                     "architecture": pool.get("architecture")})
    exe = Path(sys.executable).resolve(strict=True)
    python_shared = sorted({p for p in mapped if p.name.startswith("libpython")}, key=lambda p: p.name)
    pool_source = Path(pools_module.__file__).resolve(strict=True)
    provenance = {
        "schema_version": 1,
        "wheel": wheel_lock,
        "wheel_native_members": members,
        "installed_native_members": flint_records,
        "installed_native_member_count": len(flint_records),
        "mapped_flint_members": mapped_flint,
        "mapped_flint_member_count": len(mapped_flint),
        "loaded_extension_member": native_lock["loaded_extension_member"],
        "loaded_extension_bound_to_wheel": True,
        "mapped_native_libraries_bound_to_wheel": True,
        "proc_maps_checked": True,
        "python_flint_version": flint.__version__,
        "native_flint_version": flint.__FLINT_VERSION__,
        "python": {"version": platform.python_version(), "implementation": platform.python_implementation(),
                   "cache_tag": sys.implementation.cache_tag, "executable": _record(exe, exe.name),
                   "shared_library_mapping": "MAPPED_RETAINED" if python_shared else "NONE_MAPPED",
                   "mapped_shared_libraries": [_record(p, p.name) for p in python_shared]},
        "numpy": {"version": np.__version__, "installed_native_members": np_records,
                  "installed_native_member_count": len(np_records),
                  "mapped_native_members": mapped_numpy, "mapped_native_member_count": len(mapped_numpy)},
        "blas": sorted(blas, key=lambda record: record["member"]),
        "threadpool_inspector": {"version": importlib.metadata.version("threadpoolctl"),
                                 "source": _record(pool_source, pool_source.name)},
        "settings": {"native_threads": 1, "thread_environment": {n: os.environ.get(n) for n in THREAD_VARIABLES},
                     "initial_precision_bits": int(flint.ctx.prec), "allowed_precision_bits": [128, 256],
                     "flint_threads": int(flint.ctx.threads)},
    }
    verify(provenance)
    return provenance


def verify(provenance: dict) -> None:
    """Validate retained records offline, without loading NumPy or python-flint."""
    wheel_lock, native_lock = _locks()
    keys = {"schema_version", "wheel", "wheel_native_members", "installed_native_members",
            "installed_native_member_count", "mapped_flint_members", "mapped_flint_member_count",
            "loaded_extension_member", "loaded_extension_bound_to_wheel",
            "mapped_native_libraries_bound_to_wheel", "proc_maps_checked",
            "python_flint_version", "native_flint_version", "python", "numpy", "blas",
            "threadpool_inspector", "settings"}
    if (not isinstance(provenance, dict) or set(provenance) != keys
            or type(provenance["schema_version"]) is not int or provenance["schema_version"] != 1):
        _fail("SCHEMA")
    if provenance["wheel"] != wheel_lock:
        _fail("WHEEL_LOCK_MISMATCH")
    for name in ("wheel_native_members", "installed_native_members"):
        if provenance[name] != native_lock["native_members"]:
            _fail("EXACT_NATIVE_MEMBER_SET_OR_HASH")
    if type(provenance["installed_native_member_count"]) is not int or provenance["installed_native_member_count"] != len(native_lock["native_members"]):
        _fail("INSTALLED_MEMBER_COUNT")
    installed = _inventory(provenance["installed_native_members"], "flint")
    mapped = _inventory(provenance["mapped_flint_members"], "flint")
    if type(provenance["mapped_flint_member_count"]) is not int or provenance["mapped_flint_member_count"] != len(mapped):
        _fail("MAPPED_MEMBER_COUNT")
    if any(installed.get(name) != value for name, value in mapped.items()):
        _fail("MAPPED_FLINT_HASH_BINDING")
    required = set(native_lock["required_mapped_members"] + [native_lock["loaded_extension_member"]])
    if not required.issubset(mapped) or provenance["loaded_extension_member"] != native_lock["loaded_extension_member"]:
        _fail("MAPPED_FLINT_REQUIRED_SET")
    if any(provenance[key] is not True for key in (
            "loaded_extension_bound_to_wheel", "mapped_native_libraries_bound_to_wheel", "proc_maps_checked")):
        _fail("BINDING_FLAGS")
    for key in ("python_flint_version", "native_flint_version"):
        if provenance[key] != wheel_lock[key]:
            _fail("LOCKED_VERSION")
    py = provenance["python"]
    if not isinstance(py, dict) or set(py) != {"version", "implementation", "cache_tag", "executable", "shared_library_mapping", "mapped_shared_libraries"}:
        _fail("PYTHON_SCHEMA")
    if not all(_safe_text(py[k], token=True) for k in ("version", "implementation", "cache_tag")) or py["implementation"] != "CPython":
        _fail("PYTHON_IDENTITY")
    if re.fullmatch(r"3\.[0-9]+\.[0-9]+", py["version"]) is None or int(py["version"].split(".")[1]) < 10:
        _fail("PYTHON_ABI")
    if py["cache_tag"] != "cpython-" + "".join(py["version"].split(".")[:2]):
        _fail("PYTHON_CACHE_TAG")
    _inventory([py["executable"]])
    if not isinstance(py["mapped_shared_libraries"], list):
        _fail("PYTHON_SHARED_SCHEMA")
    shared = _inventory(py["mapped_shared_libraries"]) if py["mapped_shared_libraries"] else {}
    if py["shared_library_mapping"] != ("MAPPED_RETAINED" if shared else "NONE_MAPPED"):
        _fail("PYTHON_SHARED_MAPPING")
    if not all(name.startswith("libpython") for name in shared):
        _fail("PYTHON_SHARED_IDENTITY")
    if py != native_lock["python_build"]:
        _fail("PYTHON_BUILD_LOCK")
    np = provenance["numpy"]
    if not isinstance(np, dict) or set(np) != {"version", "installed_native_members", "installed_native_member_count", "mapped_native_members", "mapped_native_member_count"} or not _safe_text(np["version"], token=True):
        _fail("NUMPY_SCHEMA")
    np_all = _inventory(np["installed_native_members"], "numpy")
    np_mapped = _inventory(np["mapped_native_members"], "numpy")
    if (type(np["installed_native_member_count"]) is not int or np["installed_native_member_count"] != len(np_all)
            or type(np["mapped_native_member_count"]) is not int or np["mapped_native_member_count"] != len(np_mapped)
            or any(np_all.get(name) != row for name, row in np_mapped.items())):
        _fail("NUMPY_COUNTS_OR_MAPPED_BINDING")
    if not any("_multiarray_umath" in name for name in np_mapped) or not any("_umath_linalg" in name for name in np_mapped):
        _fail("NUMPY_REQUIRED_LOADED_EXTENSIONS")
    if any(name.startswith("numpy.libs/") and name not in np_mapped for name in np_all):
        _fail("NUMPY_BUNDLED_NATIVE_NOT_MAPPED")
    if {key: np[key] for key in ("version", "installed_native_members", "installed_native_member_count")} != native_lock["numpy_build"]:
        _fail("NUMPY_BUILD_LOCK")
    inspector = provenance["threadpool_inspector"]
    if not isinstance(inspector, dict) or set(inspector) != {"version", "source"} or not _safe_text(inspector["version"], token=True):
        _fail("THREADPOOL_INSPECTOR_IDENTITY")
    _inventory([inspector["source"]])
    if inspector["source"]["member"] != "threadpoolctl.py":
        _fail("THREADPOOL_INSPECTOR_SOURCE")
    if inspector != native_lock["threadpool_inspector_build"]:
        _fail("THREADPOOL_INSPECTOR_BUILD_LOCK")
    blas = provenance["blas"]
    if not isinstance(blas, list) or not blas:
        _fail("BLAS_MISSING")
    seen = []
    for b in blas:
        if not isinstance(b, dict) or set(b) != {"member", "sha256", "bytes", "version", "num_threads", "internal_api", "user_api", "threading_layer", "architecture"}:
            _fail("BLAS_SCHEMA")
        identity = {key: b[key] for key in ("member", "sha256", "bytes")}
        if np_mapped.get(b["member"]) != identity or b["member"] in seen:
            _fail("BLAS_BINARY_BINDING")
        seen.append(b["member"])
        if b["user_api"] != "blas" or type(b["num_threads"]) is not int or b["num_threads"] != 1:
            _fail("BLAS_THREADS")
        if not all(_safe_text(b[key], token=True) for key in ("version", "internal_api", "threading_layer", "architecture")):
            _fail("BLAS_IDENTITY")
    if seen != sorted(seen):
        _fail("BLAS_ORDER")
    if [{key: value for key, value in row.items() if key != "num_threads"}
            for row in blas] != native_lock["blas_builds"]:
        _fail("BLAS_BUILD_LOCK")
    settings = {"native_threads": 1, "thread_environment": {n: "1" for n in THREAD_VARIABLES},
                "initial_precision_bits": 128, "allowed_precision_bits": [128, 256], "flint_threads": 1}
    if (provenance["settings"] != settings
            or any(type(provenance["settings"][key]) is not int
                   for key in ("native_threads", "initial_precision_bits", "flint_threads"))
            or any(type(value) is not int for value in provenance["settings"]["allowed_precision_bits"])):
        _fail("PRECISION_OR_THREAD_SETTINGS")
