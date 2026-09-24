"""Fail-closed orchestration for retained-evidence review.

This module hashes files, validates review envelopes, advances a small state
machine, and creates deterministic evidence archives.  It deliberately has no
facility for importing, invoking, or benchmarking scientific workloads.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


STATE_VERSION = 1
MAX_REVIEW_EXCHANGES = 2
REVIEWERS = frozenset({"ASTRA", "CLAUDE"})
REVIEW_VERDICTS = frozenset({"ACCEPT", "REQUEST_CHANGES", "MATERIAL_FINDING"})
CLAIM_SCOPE = "RETAINED_EVIDENCE_ONLY"
TERMINAL_STATUSES = frozenset({"ACCEPTED", "BLOCKED", "MATERIAL_FINDING"})
RESERVED_PACKAGE_PATHS = frozenset({"MANIFEST.json", "PACKAGE.sha256"})


class GateError(ValueError):
    """Raised when a fail-closed policy gate refuses an input."""


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def hash_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def _safe_relative_file(root: Path, raw_path: str) -> tuple[str, Path]:
    rel = PurePosixPath(raw_path.replace(os.sep, "/"))
    if rel.is_absolute() or not rel.parts or any(part in {"", ".", ".."} for part in rel.parts):
        raise GateError(f"unsafe source path: {raw_path!r}")
    candidate = root.joinpath(*rel.parts)
    try:
        candidate.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (FileNotFoundError, ValueError) as exc:
        raise GateError(f"source is missing or escapes root: {rel.as_posix()}") from exc
    mode = candidate.lstat().st_mode
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise GateError(f"source must be a regular non-symlink file: {rel.as_posix()}")
    return rel.as_posix(), candidate


def binding_digest(bindings: Sequence[Mapping[str, Any]]) -> str:
    normalized = [
        {
            "path": str(item["path"]),
            "sha256": str(item["sha256"]),
            "size": int(item["size"]),
        }
        for item in bindings
    ]
    normalized.sort(key=lambda item: item["path"])
    return _sha256_bytes(_canonical_json(normalized))


def enumerate_regular_files(source_root: Path) -> list[str]:
    """Return the exact regular-file inventory, refusing links and special files."""

    root = source_root.resolve(strict=True)
    paths: list[str] = []
    for candidate in sorted(root.rglob("*")):
        rel = candidate.relative_to(root).as_posix()
        mode = candidate.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise GateError(f"source tree contains a symlink: {rel}")
        if candidate.is_dir():
            continue
        if not stat.S_ISREG(mode):
            raise GateError(f"source tree contains a non-regular file: {rel}")
        paths.append(rel)
    if not paths:
        raise GateError("source tree has no regular files")
    return paths


def build_source_bindings(source_root: Path, paths: Iterable[str]) -> list[dict[str, Any]]:
    """Hash the actual bytes of every explicitly declared source file."""

    root = source_root.resolve(strict=True)
    requested = list(paths)
    if not requested:
        raise GateError("at least one source path is required")
    if len(set(requested)) != len(requested):
        raise GateError("duplicate source path declaration")
    bindings: list[dict[str, Any]] = []
    for raw_path in sorted(requested):
        rel, candidate = _safe_relative_file(root, raw_path)
        digest, size = hash_file(candidate)
        bindings.append({"path": rel, "sha256": digest, "size": size})
    return bindings


def verify_source_bindings(
    source_root: Path, bindings: Sequence[Mapping[str, Any]]
) -> list[str]:
    """Return every mismatch; absence or undeclared structure fails closed."""

    issues: list[str] = []
    if not bindings:
        return ["source binding set is empty"]
    seen: set[str] = set()
    for item in bindings:
        path = str(item.get("path", ""))
        if path in seen:
            issues.append(f"duplicate source binding: {path}")
            continue
        seen.add(path)
        try:
            rel, candidate = _safe_relative_file(source_root.resolve(strict=True), path)
        except (GateError, FileNotFoundError) as exc:
            issues.append(str(exc))
            continue
        actual_digest, actual_size = hash_file(candidate)
        expected_digest = item.get("sha256")
        expected_size = item.get("size")
        if actual_digest != expected_digest:
            issues.append(
                f"source byte hash mismatch: {rel} expected={expected_digest} actual={actual_digest}"
            )
        if actual_size != expected_size:
            issues.append(
                f"source size mismatch: {rel} expected={expected_size} actual={actual_size}"
            )
    try:
        actual_paths = set(enumerate_regular_files(source_root))
    except (GateError, FileNotFoundError) as exc:
        issues.append(str(exc))
    else:
        for path in sorted(actual_paths - seen):
            issues.append(f"undeclared source input: {path}")
        for path in sorted(seen - actual_paths):
            if not any(path in issue for issue in issues):
                issues.append(f"declared source input is missing: {path}")
    return issues


def _notification(status: str, reason: str) -> dict[str, Any]:
    required = status in TERMINAL_STATUSES
    return {
        "alan_notification_required": required,
        "reason": reason if required else "",
    }


def create_state(
    source_root: Path, paths: Iterable[str], *, source_label: str
) -> dict[str, Any]:
    bindings = build_source_bindings(source_root, paths)
    state: dict[str, Any] = {
        "schema_version": STATE_VERSION,
        "source_label": source_label,
        "status": "DRAFT",
        "claim_scope": CLAIM_SCOPE,
        "source_bindings": bindings,
        "binding_digest": binding_digest(bindings),
        "reviews": [],
        "exchange_count": 0,
        "max_exchanges": MAX_REVIEW_EXCHANGES,
        "gate": {
            "actual_bytes_verified": True,
            "issues": [],
        },
        "notification": _notification("DRAFT", ""),
    }
    return evaluate_state(state, source_root)


def _validate_state_shape(state: Mapping[str, Any]) -> None:
    if state.get("schema_version") != STATE_VERSION:
        raise GateError("unsupported state schema version")
    if state.get("claim_scope") != CLAIM_SCOPE:
        raise GateError("state exceeds retained-evidence claim scope")
    bindings = state.get("source_bindings")
    if not isinstance(bindings, list) or not bindings:
        raise GateError("state has no source bindings")
    if state.get("binding_digest") != binding_digest(bindings):
        raise GateError("state binding digest does not match its declared bindings")
    reviews = state.get("reviews")
    if not isinstance(reviews, list):
        raise GateError("state reviews must be a list")
    if len(reviews) > MAX_REVIEW_EXCHANGES:
        raise GateError("state exceeds the review exchange limit")
    if state.get("max_exchanges") != MAX_REVIEW_EXCHANGES:
        raise GateError("state review exchange limit is not the fixed policy limit")
    if state.get("exchange_count") != len(reviews):
        raise GateError("state exchange count does not match retained reviews")
    source_ids: set[str] = set()
    reviewers: set[str] = set()
    for index, review in enumerate(reviews, start=1):
        if not isinstance(review, Mapping):
            raise GateError("state review entry must be an object")
        _validate_review_message(review)
        if review["exchange"] != index:
            raise GateError("state review exchange sequence is invalid")
        if review["reviewed_binding_digest"] != state["binding_digest"]:
            raise GateError("state contains a review for a stale or foreign binding")
        if review["source_id"] in source_ids:
            raise GateError("state contains a duplicate review source_id")
        if review["reviewer"] in reviewers:
            raise GateError("state contains more than one review from the same reviewer")
        source_ids.add(review["source_id"])
        reviewers.add(review["reviewer"])


def _validate_review_message(message: Mapping[str, Any]) -> None:
    required = {
        "schema_version",
        "source_id",
        "reviewer",
        "exchange",
        "reviewed_binding_digest",
        "verdict",
        "claim_scope",
        "evidence_refs",
        "limitations",
        "next_actions",
    }
    missing = sorted(required.difference(message))
    if missing:
        raise GateError(f"review message missing keys: {', '.join(missing)}")
    if message["schema_version"] != 1:
        raise GateError("unsupported reviewer message schema version")
    if message["reviewer"] not in REVIEWERS:
        raise GateError("reviewer must be ASTRA or CLAUDE")
    if message["verdict"] not in REVIEW_VERDICTS:
        raise GateError("unsupported review verdict")
    if message["claim_scope"] != CLAIM_SCOPE:
        raise GateError("review exceeds retained-evidence claim scope")
    if not isinstance(message["source_id"], str) or not message["source_id"].strip():
        raise GateError("review source_id must be non-empty")
    if not isinstance(message["exchange"], int) or not 1 <= message["exchange"] <= 2:
        raise GateError("review exchange must be 1 or 2")
    for key in ("evidence_refs", "limitations", "next_actions"):
        if not isinstance(message[key], list) or not all(
            isinstance(value, str) for value in message[key]
        ):
            raise GateError(f"review {key} must be a list of strings")
    if not message["evidence_refs"]:
        raise GateError("review evidence_refs must retain at least one accessible reference")
    if not message["limitations"]:
        raise GateError("review limitations must retain at least one explicit boundary")


def ingest_review(
    state: Mapping[str, Any], message: Mapping[str, Any], source_root: Path
) -> dict[str, Any]:
    """Add one reviewer envelope, allowing at most one turn per reviewer."""

    _validate_state_shape(state)
    _validate_review_message(message)
    reviews = list(state["reviews"])
    if len(reviews) >= MAX_REVIEW_EXCHANGES:
        raise GateError("review exchange limit reached")
    expected_exchange = len(reviews) + 1
    if message["exchange"] != expected_exchange:
        raise GateError(f"expected exchange {expected_exchange}")
    if message["reviewed_binding_digest"] != state["binding_digest"]:
        raise GateError("review references a stale or foreign source binding")
    if any(item["source_id"] == message["source_id"] for item in reviews):
        raise GateError("duplicate review source_id")
    if any(item["reviewer"] == message["reviewer"] for item in reviews):
        raise GateError("each reviewer may contribute only once")
    updated = json.loads(json.dumps(state))
    updated["reviews"].append(dict(message))
    updated["exchange_count"] = len(updated["reviews"])
    return evaluate_state(updated, source_root)


def evaluate_state(state: Mapping[str, Any], source_root: Path) -> dict[str, Any]:
    """Advance state without executing any scientific code."""

    _validate_state_shape(state)
    updated = json.loads(json.dumps(state))
    issues = verify_source_bindings(source_root, updated["source_bindings"])
    updated["gate"] = {
        "actual_bytes_verified": not issues,
        "issues": issues,
    }
    updated["exchange_count"] = len(updated["reviews"])
    if issues:
        updated["status"] = "BLOCKED"
        updated["notification"] = _notification("BLOCKED", "actual source bytes changed")
        return updated

    verdicts = [review["verdict"] for review in updated["reviews"]]
    if "MATERIAL_FINDING" in verdicts:
        updated["status"] = "MATERIAL_FINDING"
        updated["notification"] = _notification(
            "MATERIAL_FINDING", "reviewer reported a material retained-evidence finding"
        )
    elif "REQUEST_CHANGES" in verdicts:
        updated["status"] = "BLOCKED"
        updated["notification"] = _notification("BLOCKED", "reviewer requested changes")
    elif (
        len(updated["reviews"]) == MAX_REVIEW_EXCHANGES
        and set(review["reviewer"] for review in updated["reviews"]) == REVIEWERS
        and all(verdict == "ACCEPT" for verdict in verdicts)
    ):
        updated["status"] = "ACCEPTED"
        updated["notification"] = _notification(
            "ACCEPTED", "both bounded reviewer exchanges accepted the same source binding"
        )
    else:
        updated["status"] = "IN_REVIEW"
        updated["notification"] = _notification("IN_REVIEW", "")
    return updated


def _iter_evidence_files(root: Path) -> list[tuple[str, Path]]:
    entries: list[tuple[str, Path]] = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise GateError(f"evidence tree contains a symlink: {rel}")
        if path.is_dir():
            continue
        if not stat.S_ISREG(mode):
            raise GateError(f"evidence tree contains a non-regular file: {rel}")
        if rel in RESERVED_PACKAGE_PATHS:
            continue
        entries.append((rel, path))
    if not entries:
        raise GateError("evidence tree has no packageable files")
    return entries


def package_evidence(evidence_root: Path, output_zip: Path) -> dict[str, Any]:
    """Create a deterministic ZIP with a non-self-referential manifest.

    MANIFEST.json is included in the ZIP but does not list itself.  The ZIP
    digest is written beside the archive as ``<archive>.sha256`` and is not
    included in the archive.
    """

    root = evidence_root.resolve(strict=True)
    output = output_zip.resolve(strict=False)
    try:
        output.relative_to(root)
    except ValueError:
        pass
    else:
        raise GateError("output archive must be outside the evidence root")
    files = _iter_evidence_files(root)
    manifest_files: list[dict[str, Any]] = []
    for rel, path in files:
        digest, size = hash_file(path)
        manifest_files.append({"path": rel, "sha256": digest, "size": size})
    manifest = {
        "schema_version": 1,
        "hash_algorithm": "sha256",
        "excluded": sorted(RESERVED_PACKAGE_PATHS),
        "files": manifest_files,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(
            temporary_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            for rel, path in files:
                info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
            manifest_info = zipfile.ZipInfo(
                "MANIFEST.json", date_time=(1980, 1, 1, 0, 0, 0)
            )
            manifest_info.compress_type = zipfile.ZIP_DEFLATED
            manifest_info.external_attr = 0o100644 << 16
            archive.writestr(
                manifest_info, json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            )
        temporary_path.replace(output)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()
    zip_digest, zip_size = hash_file(output)
    detached = output.with_name(output.name + ".sha256")
    detached.write_text(f"{zip_digest}  {output.name}\n", encoding="utf-8")
    return {
        "archive": str(output),
        "sha256": zip_digest,
        "size": zip_size,
        "detached_digest": str(detached),
        "manifest_entries": len(manifest_files),
    }


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GateError(f"JSON root must be an object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-state")
    create.add_argument("--source-root", type=Path, required=True)
    create.add_argument("--source-label", required=True)
    source_group = create.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--source", action="append")
    source_group.add_argument("--source-all", action="store_true")
    create.add_argument("--output", type=Path, required=True)

    verify = subparsers.add_parser("verify-state")
    verify.add_argument("--state", type=Path, required=True)
    verify.add_argument("--source-root", type=Path, required=True)
    verify.add_argument("--output", type=Path)

    ingest = subparsers.add_parser("ingest-review")
    ingest.add_argument("--state", type=Path, required=True)
    ingest.add_argument("--message", type=Path, required=True)
    ingest.add_argument("--source-root", type=Path, required=True)
    ingest.add_argument("--output", type=Path)

    package = subparsers.add_parser("package")
    package.add_argument("--state", type=Path, required=True)
    package.add_argument("--source-root", type=Path, required=True)
    package.add_argument("--evidence-root", type=Path, required=True)
    package.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "create-state":
            source_paths = (
                enumerate_regular_files(args.source_root) if args.source_all else args.source
            )
            state = create_state(
                args.source_root, source_paths, source_label=args.source_label
            )
            _write_json(args.output, state)
            print(json.dumps({"status": state["status"], "state": str(args.output)}))
            return 0
        if args.command == "verify-state":
            state = evaluate_state(_load_json(args.state), args.source_root)
            _write_json(args.output or args.state, state)
            print(json.dumps({"status": state["status"], "gate": state["gate"]}))
            return 0 if state["gate"]["actual_bytes_verified"] else 2
        if args.command == "ingest-review":
            state = ingest_review(
                _load_json(args.state), _load_json(args.message), args.source_root
            )
            _write_json(args.output or args.state, state)
            print(json.dumps({"status": state["status"], "notification": state["notification"]}))
            return 0
        if args.command == "package":
            state = evaluate_state(_load_json(args.state), args.source_root)
            if state["status"] != "ACCEPTED":
                raise GateError(f"package requires ACCEPTED state, got {state['status']}")
            result = package_evidence(args.evidence_root, args.output)
            print(json.dumps(result, sort_keys=True))
            return 0
    except (GateError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}), file=sys.stderr)
        return 2
    parser.error("unreachable command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
