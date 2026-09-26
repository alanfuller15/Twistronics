"""Lossless, bounded standard-library packaging for the diagnostic journal.

These helpers check byte identity and exact package membership.  They make no
numerical calls and do not replace the event/arithmetic verifier: callers must
validate a raw run before hosting, and run check-only verification after
materialization.  RESULTS and the supervisor receipt are copied byte-for-byte.
"""

import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import zlib


RAW_BYTES_MAX = 268435456
COMPRESSED_BYTES_MAX = RAW_BYTES_MAX + 1048576
METADATA_BYTES_MAX = 16777216
PART_BYTES = 500000
PART_PREFIX = "EVENTS.ndjson.gz.part"
RAW_NAMES = frozenset(("EVENTS.ndjson", "RESULTS.json", "SUPERVISOR_RECEIPT.json"))
MANIFEST_NAME = "MANIFEST.json"


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value):
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False).encode("ascii") + b"\n"


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY:" + key)
        result[key] = value
    return result


def _json_load(data):
    def invalid_constant(value):
        raise ValueError("NONFINITE_JSON:" + value)
    result = json.loads(data, object_pairs_hook=_unique_object, parse_constant=invalid_constant)
    if not isinstance(result, dict):
        raise ValueError("JSON_ROOT_NOT_OBJECT")
    return result


def _read_regular(path, cap):
    """Read once through a non-following descriptor and enforce byte limits."""
    path = Path(path)
    if path.is_symlink():
        raise ValueError("PACKAGE_SYMLINK:" + path.name)
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > cap:
            raise ValueError("PACKAGE_FILE_TYPE_OR_SIZE:" + path.name)
        data = stream.read(cap + 1)
        after = os.fstat(stream.fileno())
    if len(data) > cap or len(data) != before.st_size or (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("PACKAGE_FILE_CHANGED_OR_TOO_LARGE:" + path.name)
    return data


def _directory_names(path):
    path = Path(path)
    if path.is_symlink() or not path.is_dir():
        raise ValueError("PACKAGE_DIRECTORY_REQUIRED")
    names = set()
    for child in path.iterdir():
        if child.is_symlink() or not child.is_file():
            raise ValueError("PACKAGE_SYMLINK_OR_NONFILE:" + child.name)
        names.add(child.name)
    return names


def _manifest(files):
    return {
        "schema_version": 1,
        "entries": [{"path": name, "bytes": len(data), "sha256": _sha(data)} for name, data in sorted(files.items())],
    }


def _verify_manifest(data, files):
    expected = _manifest(files)
    if _json_load(data) != expected or data != _json_bytes(expected):
        raise ValueError("MANIFEST_BINDING_OR_FORMAT_MISMATCH")


def _write_files(destination, files):
    destination = Path(destination)
    # An existing directory is never repurposed, even if it looks empty.
    destination.mkdir(parents=True, exist_ok=False)
    for name, data in sorted(files.items()):
        if Path(name).name != name or name in ("", ".", ".."):
            raise ValueError("UNSAFE_OUTPUT_NAME")
        with (destination / name).open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    return destination


def package_plan(raw, part_bytes=PART_BYTES):
    """Return deterministic gzip metadata and contiguous numbered parts.

    Nondefault part sizes are available for isolated helper controls only;
    production hosting/materialization enforce the protocol's 500000 bytes.
    """
    if not isinstance(raw, bytes) or len(raw) > RAW_BYTES_MAX:
        raise ValueError("RAW_LOG_TYPE_OR_SIZE")
    if type(part_bytes) is not int or not 0 < part_bytes <= PART_BYTES:
        raise ValueError("INVALID_PART_SIZE")
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, compresslevel=9, mtime=0) as stream:
        stream.write(raw)
    compressed = buffer.getvalue()
    if len(compressed) > COMPRESSED_BYTES_MAX:
        raise ValueError("COMPRESSED_LOG_TOO_LARGE")
    parts = {
        PART_PREFIX + f"{index:03d}": compressed[offset:offset + part_bytes]
        for index, offset in enumerate(range(0, len(compressed), part_bytes))
    }
    metadata = {
        "raw_bytes": len(raw), "raw_sha256": _sha(raw),
        "compressed_bytes": len(compressed), "compressed_sha256": _sha(compressed),
        "parts": [{"path": name, "bytes": len(data), "sha256": _sha(data)} for name, data in parts.items()],
    }
    return metadata, parts


def _validate_metadata(metadata):
    expected = {"raw_bytes", "raw_sha256", "compressed_bytes", "compressed_sha256", "parts"}
    if not isinstance(metadata, dict) or set(metadata) != expected:
        raise ValueError("EVENT_PACKAGE_SCHEMA")
    for key, cap, minimum in (("raw_bytes", RAW_BYTES_MAX, 0), ("compressed_bytes", COMPRESSED_BYTES_MAX, 1)):
        if type(metadata[key]) is not int or not minimum <= metadata[key] <= cap:
            raise ValueError("EVENT_PACKAGE_SIZE:" + key)
    for key in ("raw_sha256", "compressed_sha256"):
        if not isinstance(metadata[key], str) or re.fullmatch("[0-9a-f]{64}", metadata[key]) is None:
            raise ValueError("EVENT_PACKAGE_DIGEST:" + key)
    entries = metadata["parts"]
    expected_count = (metadata["compressed_bytes"] + PART_BYTES - 1) // PART_BYTES
    if not isinstance(entries, list) or len(entries) != expected_count:
        raise ValueError("EVENT_PACKAGE_PART_COUNT")
    for index, entry in enumerate(entries):
        expected_size = min(PART_BYTES, metadata["compressed_bytes"] - index * PART_BYTES)
        if not isinstance(entry, dict) or set(entry) != {"path", "bytes", "sha256"}:
            raise ValueError("EVENT_PACKAGE_PART_SCHEMA")
        if entry["path"] != PART_PREFIX + f"{index:03d}" or type(entry["bytes"]) is not int or entry["bytes"] != expected_size:
            raise ValueError("EVENT_PACKAGE_PART_CONTIGUITY_OR_SIZE")
        if not isinstance(entry["sha256"], str) or re.fullmatch("[0-9a-f]{64}", entry["sha256"]) is None:
            raise ValueError("EVENT_PACKAGE_PART_DIGEST")
    return entries


def write_manifest(rawdir, check_only=False):
    """Write the exact raw manifest, or compare it without writes in check mode."""
    rawdir = Path(rawdir)
    names = _directory_names(rawdir)
    if names not in (RAW_NAMES, RAW_NAMES | {MANIFEST_NAME}):
        raise ValueError("RAW_DIRECTORY_MEMBERSHIP")
    files = {name: _read_regular(rawdir / name, RAW_BYTES_MAX if name == "EVENTS.ndjson" else METADATA_BYTES_MAX) for name in sorted(RAW_NAMES)}
    manifest = _manifest(files)
    data = _json_bytes(manifest)
    path = rawdir / MANIFEST_NAME
    if check_only:
        if MANIFEST_NAME not in names:
            raise ValueError("RAW_MANIFEST_MISSING")
        _verify_manifest(_read_regular(path, METADATA_BYTES_MAX), files)
        return manifest
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0), 0o644)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return manifest


def write_hosted(rawdir, dest):
    """Package a previously verified raw run without changing its JSON bytes."""
    rawdir = Path(rawdir)
    if _directory_names(rawdir) != RAW_NAMES | {MANIFEST_NAME}:
        raise ValueError("RAW_DIRECTORY_MEMBERSHIP")
    raw_files = {name: _read_regular(rawdir / name, RAW_BYTES_MAX if name == "EVENTS.ndjson" else METADATA_BYTES_MAX) for name in sorted(RAW_NAMES)}
    _verify_manifest(_read_regular(rawdir / MANIFEST_NAME, METADATA_BYTES_MAX), raw_files)
    results = _json_load(raw_files["RESULTS.json"])
    _json_load(raw_files["SUPERVISOR_RECEIPT.json"])
    metadata = results.get("event_package")
    _validate_metadata(metadata)
    expected_metadata, parts = package_plan(raw_files["EVENTS.ndjson"])
    if metadata != expected_metadata:
        raise ValueError("EVENT_PACKAGE_BINDING_MISMATCH")
    files = {name: raw_files[name] for name in ("RESULTS.json", "SUPERVISOR_RECEIPT.json")}
    files.update(parts)
    files[MANIFEST_NAME] = _json_bytes(_manifest(files))
    return _write_files(dest, files)


def materialize(hosted, dest):
    """Verify and decompress a hosted package into a new raw evidence directory.

    Decompression stops at the raw byte cap.  A second gzip member, padding,
    truncation, checksum failure, filename field or nonzero mtime is rejected.
    The caller next runs the offline verifier's check-only path on the result.
    """
    hosted = Path(hosted)
    names = _directory_names(hosted)
    results_bytes = _read_regular(hosted / "RESULTS.json", METADATA_BYTES_MAX)
    results = _json_load(results_bytes)
    metadata = results.get("event_package")
    entries = _validate_metadata(metadata)
    expected_names = {"RESULTS.json", "SUPERVISOR_RECEIPT.json", MANIFEST_NAME} | {entry["path"] for entry in entries}
    if names != expected_names:
        raise ValueError("HOSTED_DIRECTORY_MEMBERSHIP")
    files = {"RESULTS.json": results_bytes, "SUPERVISOR_RECEIPT.json": _read_regular(hosted / "SUPERVISOR_RECEIPT.json", METADATA_BYTES_MAX)}
    _json_load(files["SUPERVISOR_RECEIPT.json"])
    compressed = bytearray()
    for entry in entries:
        data = _read_regular(hosted / entry["path"], PART_BYTES)
        if len(data) != entry["bytes"] or _sha(data) != entry["sha256"]:
            raise ValueError("COMPRESSED_PART_BINDING_MISMATCH")
        files[entry["path"]] = data
        compressed.extend(data)
    _verify_manifest(_read_regular(hosted / MANIFEST_NAME, METADATA_BYTES_MAX), files)
    if len(compressed) != metadata["compressed_bytes"] or _sha(compressed) != metadata["compressed_sha256"]:
        raise ValueError("COMPRESSED_LOG_BINDING_MISMATCH")
    if compressed[:10] != b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff":
        raise ValueError("NONCANONICAL_GZIP_HEADER")
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    raw = decoder.decompress(compressed, RAW_BYTES_MAX + 1)
    if len(raw) > RAW_BYTES_MAX or decoder.unconsumed_tail:
        raise ValueError("RAW_LOG_TOO_LARGE")
    if not decoder.eof or decoder.unused_data:
        raise ValueError("TRUNCATED_OR_TRAILING_GZIP_DATA")
    if len(raw) != metadata["raw_bytes"] or _sha(raw) != metadata["raw_sha256"]:
        raise ValueError("RAW_LOG_BINDING_MISMATCH")
    raw_files = {"EVENTS.ndjson": raw, "RESULTS.json": files["RESULTS.json"], "SUPERVISOR_RECEIPT.json": files["SUPERVISOR_RECEIPT.json"]}
    raw_files[MANIFEST_NAME] = _json_bytes(_manifest(raw_files))
    return _write_files(dest, raw_files)
