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
import re
import stat
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


STATE_VERSION = 2
PROTOCOL = "TWISTRONICS-ACCEPTANCE/1"
MAX_REVIEW_EXCHANGES = 2
REVIEWERS = frozenset({"ASTRA", "CLAUDE"})
REVIEW_ORDER = ("ASTRA", "CLAUDE")
REVIEW_VERDICTS = frozenset(
    {"PASS", "CONDITIONAL_PASS", "BLOCKED", "STALE", "INVALID", "MATERIAL_FINDING"}
)
CLAIM_SCOPE = "RETAINED_EVIDENCE_ONLY"
TERMINAL_STATUSES = frozenset({"ACCEPTED", "BLOCKED", "MATERIAL_FINDING"})
RESERVED_PACKAGE_PATHS = frozenset({"MANIFEST.json", "PACKAGE.sha256"})
GATE_IDS = tuple(f"G{index:02d}" for index in range(18))
PREPACKAGE_GATE_IDS = tuple(
    gate_id for gate_id in GATE_IDS if gate_id not in {"G04", "G16", "G17"}
)
POSTPACKAGE_GATE_IDS = ("G04", "G16", "G17")
GATE_STATUSES = frozenset({"PASS", "FAIL", "ERROR", "SKIPPED", "MISSING", "NOT_RUN"})
CONTROL_IDS = (
    "source_byte_flip", "missing_source_identity", "added_source",
    "changed_expectations", "source_mutation_during_build", "missing_evidence",
    "extra_evidence", "tampered_evidence", "manifest_self_reference",
    "unsafe_zip_path", "unsafe_zip_link", "altered_finished_zip",
    "readme_claim_drift", "missing_test", "failing_test", "unapproved_skip",
    "log_count_tampering", "malformed_checker_arguments", "broken_harness_configuration",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


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


def _portable_archive_name(raw_path: str) -> str:
    """Return a canonical portable ZIP member name or fail closed."""

    if "\\" in raw_path or "\x00" in raw_path or ":" in raw_path:
        raise GateError(f"unsafe archive path: {raw_path!r}")
    rel = PurePosixPath(raw_path)
    if rel.is_absolute() or not rel.parts or any(
        part in {"", ".", ".."} or part.endswith((" ", ".")) for part in rel.parts
    ):
        raise GateError(f"unsafe archive path: {raw_path!r}")
    canonical = unicodedata.normalize("NFC", rel.as_posix())
    if canonical != raw_path:
        raise GateError(f"non-canonical archive path: {raw_path!r}")
    return canonical


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


def build_evidence_bindings(evidence_root: Path) -> list[dict[str, Any]]:
    """Bind the exact packageable evidence inventory."""

    root = evidence_root.resolve(strict=True)
    bindings: list[dict[str, Any]] = []
    collision_keys: set[str] = set()
    for rel in enumerate_regular_files(root):
        if rel in RESERVED_PACKAGE_PATHS:
            continue
        canonical = _portable_archive_name(rel)
        collision_key = unicodedata.normalize("NFC", canonical).casefold()
        if collision_key in collision_keys:
            raise GateError(f"portable archive path collision: {canonical}")
        collision_keys.add(collision_key)
        _, candidate = _safe_relative_file(root, canonical)
        digest, size = hash_file(candidate)
        bindings.append({"path": canonical, "sha256": digest, "size": size})
    if not bindings:
        raise GateError("evidence tree has no packageable files")
    return bindings


def _validate_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise GateError(f"{label} must be lowercase 64-hex")
    return value


def _validate_commit(value: Any, label: str) -> str:
    if not isinstance(value, str) or not COMMIT_RE.fullmatch(value):
        raise GateError(f"{label} must be lowercase 40-hex")
    return value


def _validate_result_ledger(
    results: Mapping[str, Any],
    required_ids: Sequence[str],
    label: str,
    evidence_bindings: Sequence[Mapping[str, Any]],
) -> None:
    if set(results) != set(required_ids):
        raise GateError(f"{label} results do not contain the exact required set")
    evidence = {str(item["path"]): str(item["sha256"]) for item in evidence_bindings}
    for result_id in required_ids:
        result = results[result_id]
        if not isinstance(result, Mapping) or set(result) != {
            "status", "evidence_refs", "detail", "receipt"
        }:
            raise GateError(f"{result_id} result shape is invalid")
        if result["status"] not in GATE_STATUSES:
            raise GateError(f"{result_id} has an unsupported status")
        refs = result["evidence_refs"]
        if not isinstance(refs, list) or not refs:
            raise GateError(f"{result_id} must retain evidence references")
        for ref in refs:
            if not isinstance(ref, Mapping) or set(ref) != {"path", "sha256"}:
                raise GateError(f"{result_id} evidence reference shape is invalid")
            if evidence.get(ref["path"]) != ref["sha256"]:
                raise GateError(f"{result_id} references unbound evidence: {ref.get('path')}")
        if not isinstance(result["detail"], str) or not result["detail"].strip():
            raise GateError(f"{result_id} detail must be non-empty")
        receipt = result["receipt"]
        if not isinstance(receipt, Mapping) or set(receipt) != {"path", "sha256"}:
            raise GateError(f"{result_id} receipt reference shape is invalid")
        if evidence.get(receipt["path"]) != receipt["sha256"]:
            raise GateError(f"{result_id} receipt is not byte-bound evidence")


def _validate_gate_results(
    gate_results: Mapping[str, Any], evidence_bindings: Sequence[Mapping[str, Any]]
) -> None:
    _validate_result_ledger(gate_results, GATE_IDS, "gate", evidence_bindings)


def _validate_negative_controls(
    controls: Mapping[str, Any], evidence_bindings: Sequence[Mapping[str, Any]]
) -> None:
    _validate_result_ledger(controls, CONTROL_IDS, "negative control", evidence_bindings)


def _verify_typed_receipts(state: Mapping[str, Any], evidence_root: Path) -> list[str]:
    """Verify distinct retained execution receipts for every gate and control."""

    root = evidence_root.resolve(strict=True)
    issues: list[str] = []
    seen_paths: set[str] = set()
    evidence = {
        str(item["path"]): str(item["sha256"])
        for item in state["evidence_bindings"]
    }
    source = {
        str(item["path"]): str(item["sha256"])
        for item in state["source_bindings"]
    }
    bound_inputs = {**evidence, **source}
    ledgers = (
        (state["gate_results"], "gate"),
        (state["negative_controls"], "negative_control"),
    )
    required = {
        "schema_version", "record_type", "record_id", "checker",
        "inputs", "argv", "cwd", "runtime", "started_at", "finished_at",
        "exit_code", "result", "outputs",
    }
    for ledger, kind in ledgers:
        for record_id, result in ledger.items():
            receipt_ref = result["receipt"]
            path = str(receipt_ref["path"])
            if path in seen_paths:
                issues.append(f"receipt reused by multiple results: {path}")
                continue
            seen_paths.add(path)
            try:
                _, candidate = _safe_relative_file(root, path)
                receipt = json.loads(candidate.read_text(encoding="utf-8"))
            except (GateError, OSError, json.JSONDecodeError) as exc:
                issues.append(f"invalid receipt {path}: {exc}")
                continue
            if not isinstance(receipt, Mapping) or set(receipt) != required:
                issues.append(f"receipt has invalid shape: {path}")
                continue
            expected_type = f"{kind}/{record_id}"
            if receipt["schema_version"] != 1 or receipt["record_type"] != expected_type:
                issues.append(f"receipt type mismatch: {path}")
            if receipt["record_id"] != record_id or receipt["result"] != result["status"]:
                issues.append(f"receipt result mismatch: {path}")
            checker = receipt["checker"]
            if not isinstance(checker, Mapping) or set(checker) != {"id", "owner", "path", "sha256"}:
                issues.append(f"receipt checker shape invalid: {path}")
            else:
                if checker["id"] != f"{kind}/{record_id}":
                    issues.append(f"gate-specific checker ID mismatch: {path}")
                if checker["owner"] not in {"HARNESS", "REVIEWER"}:
                    issues.append(f"receipt checker owner invalid: {path}")
                if kind == "gate" and int(record_id[1:]) >= 11 and checker["owner"] != "REVIEWER":
                    issues.append(f"reviewer-owned checker required: {path}")
                if source.get(checker["path"]) != checker["sha256"]:
                    issues.append(f"checker is not bound to the approved source: {path}")
            if not isinstance(receipt["argv"], list) or not all(isinstance(v, str) for v in receipt["argv"]):
                issues.append(f"receipt argv invalid: {path}")
            if not isinstance(receipt["inputs"], list) or not receipt["inputs"]:
                issues.append(f"receipt inputs missing: {path}")
            if not isinstance(receipt["outputs"], list) or not receipt["outputs"]:
                issues.append(f"receipt outputs missing: {path}")
            for item in receipt["inputs"]:
                if not isinstance(item, Mapping) or set(item) != {"path", "sha256"}:
                    issues.append(f"receipt input shape invalid: {path}")
                    continue
                try:
                    _validate_sha256(item["sha256"], "receipt input sha256")
                except GateError as exc:
                    issues.append(f"{path}: {exc}")
                if bound_inputs.get(item["path"]) != item["sha256"]:
                    issues.append(f"receipt input is not bound: {path}")
            for item in receipt["outputs"]:
                if not isinstance(item, Mapping) or set(item) != {"path", "sha256"}:
                    issues.append(f"receipt output shape invalid: {path}")
                    continue
                if evidence.get(item["path"]) != item["sha256"]:
                    issues.append(f"receipt output is unbound evidence: {path}")
            if receipt["exit_code"] != 0 or not isinstance(receipt["cwd"], str) or not isinstance(receipt["runtime"], str):
                issues.append(f"receipt execution metadata invalid: {path}")
            for timestamp in (receipt["started_at"], receipt["finished_at"]):
                if not isinstance(timestamp, str) or re.fullmatch(
                    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?Z",
                    timestamp,
                ) is None:
                    issues.append(f"receipt timestamp invalid: {path}")
                    break
    return issues


def _descriptor_payload(state: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "protocol": state["protocol"],
        "round_id": state["round_id"],
        "baseline_sha": state["baseline_sha"],
        "reviewed_commit": state["reviewed_commit"],
        "artifact_sha256": state["artifact_sha256"],
        "claim_scope": state["claim_scope"],
        "source_label": state["source_label"],
        "source_bindings": state["source_bindings"],
        "source_binding_digest": state["source_binding_digest"],
        "evidence_bindings": state["evidence_bindings"],
        "evidence_binding_digest": state["evidence_binding_digest"],
        "gate_results": state["gate_results"],
        "negative_controls": state["negative_controls"],
    }


def descriptor_digest(state: Mapping[str, Any]) -> str:
    return _sha256_bytes(_canonical_json(_descriptor_payload(state)))


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
    source_root: Path,
    paths: Iterable[str],
    *,
    source_label: str,
    evidence_root: Path,
    round_id: str,
    baseline_sha: str,
    reviewed_commit: str,
    artifact_sha256: str,
    gate_results: Mapping[str, Any],
    negative_controls: Mapping[str, Any],
) -> dict[str, Any]:
    bindings = build_source_bindings(source_root, paths)
    evidence_bindings = build_evidence_bindings(evidence_root)
    _validate_commit(baseline_sha, "baseline_sha")
    _validate_commit(reviewed_commit, "reviewed_commit")
    _validate_sha256(artifact_sha256, "artifact_sha256")
    expected_round = rf"^TWI-ACC-v079p-R[0-9]{{2}}-{artifact_sha256[:12]}$"
    if not isinstance(round_id, str) or re.fullmatch(expected_round, round_id) is None:
        raise GateError("round_id does not bind the artifact digest prefix")
    _validate_gate_results(gate_results, evidence_bindings)
    _validate_negative_controls(negative_controls, evidence_bindings)
    state: dict[str, Any] = {
        "schema_version": STATE_VERSION,
        "protocol": PROTOCOL,
        "round_id": round_id,
        "baseline_sha": baseline_sha,
        "reviewed_commit": reviewed_commit,
        "artifact_sha256": artifact_sha256,
        "source_label": source_label,
        "status": "DRAFT",
        "claim_scope": CLAIM_SCOPE,
        "source_bindings": bindings,
        "source_binding_digest": binding_digest(bindings),
        "evidence_bindings": evidence_bindings,
        "evidence_binding_digest": binding_digest(evidence_bindings),
        "gate_results": json.loads(json.dumps(gate_results)),
        "negative_controls": json.loads(json.dumps(negative_controls)),
        "descriptor_digest": "",
        "reviews": [],
        "exchange_count": 0,
        "max_exchanges": MAX_REVIEW_EXCHANGES,
        "gate": {
            "actual_bytes_verified": True,
            "issues": [],
        },
        "notification": _notification("DRAFT", ""),
    }
    state["descriptor_digest"] = descriptor_digest(state)
    return evaluate_state(state, source_root, evidence_root)


def _validate_state_shape(state: Mapping[str, Any]) -> None:
    required = {
        "schema_version", "protocol", "round_id", "baseline_sha", "reviewed_commit",
        "artifact_sha256", "source_label", "status", "claim_scope", "source_bindings",
        "source_binding_digest", "evidence_bindings", "evidence_binding_digest",
        "gate_results", "negative_controls", "descriptor_digest", "reviews", "exchange_count",
        "max_exchanges", "gate", "notification",
    }
    if set(state) != required:
        raise GateError("state has missing or undeclared fields")
    if state.get("schema_version") != STATE_VERSION:
        raise GateError("unsupported state schema version")
    if state.get("protocol") != PROTOCOL:
        raise GateError("unsupported protocol")
    if state.get("claim_scope") != CLAIM_SCOPE:
        raise GateError("state exceeds retained-evidence claim scope")
    _validate_commit(state.get("baseline_sha"), "baseline_sha")
    _validate_commit(state.get("reviewed_commit"), "reviewed_commit")
    artifact_sha256 = _validate_sha256(state.get("artifact_sha256"), "artifact_sha256")
    if re.fullmatch(
        rf"TWI-ACC-v079p-R[0-9]{{2}}-{artifact_sha256[:12]}",
        str(state.get("round_id", "")),
    ) is None:
        raise GateError("round_id does not bind the artifact digest prefix")
    bindings = state.get("source_bindings")
    if not isinstance(bindings, list) or not bindings:
        raise GateError("state has no source bindings")
    if state.get("source_binding_digest") != binding_digest(bindings):
        raise GateError("source binding digest does not match declared bindings")
    evidence_bindings = state.get("evidence_bindings")
    if not isinstance(evidence_bindings, list) or not evidence_bindings:
        raise GateError("state has no evidence bindings")
    if state.get("evidence_binding_digest") != binding_digest(evidence_bindings):
        raise GateError("evidence binding digest does not match declared bindings")
    gate_results = state.get("gate_results")
    if not isinstance(gate_results, Mapping):
        raise GateError("state gate results must be an object")
    _validate_gate_results(gate_results, evidence_bindings)
    negative_controls = state.get("negative_controls")
    if not isinstance(negative_controls, Mapping):
        raise GateError("state negative controls must be an object")
    _validate_negative_controls(negative_controls, evidence_bindings)
    if state.get("descriptor_digest") != descriptor_digest(state):
        raise GateError("state descriptor digest is stale or foreign")
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
        _validate_review_against_state(review, state)
        if review["source_id"] in source_ids:
            raise GateError("state contains a duplicate review source_id")
        if review["reviewer"] in reviewers:
            raise GateError("state contains more than one review from the same reviewer")
        source_ids.add(review["source_id"])
        reviewers.add(review["reviewer"])


def _validate_review_message(message: Mapping[str, Any]) -> None:
    required = {
        "schema_version", "protocol", "round_id", "source_id", "in_reply_to",
        "reviewer", "responder_marker", "exchange", "reviewed_commit",
        "artifact_sha256", "reviewed_descriptor_digest", "status", "claim_scope",
        "evidence_refs", "blockers", "limitations", "next_action", "reply_required",
        "transport_receipt",
    }
    if set(message) != required:
        raise GateError("review message has missing or undeclared fields")
    if message["schema_version"] != 2:
        raise GateError("unsupported reviewer message schema version")
    if message["protocol"] != PROTOCOL:
        raise GateError("review protocol mismatch")
    if message["reviewer"] not in REVIEWERS:
        raise GateError("reviewer must be ASTRA or CLAUDE")
    if message["status"] not in REVIEW_VERDICTS:
        raise GateError("unsupported review status")
    if message["claim_scope"] != CLAIM_SCOPE:
        raise GateError("review exceeds retained-evidence claim scope")
    if not isinstance(message["source_id"], str) or not message["source_id"].strip():
        raise GateError("review source_id must be non-empty")
    if re.fullmatch(r"(?:issuecomment|pullrequestreview)-[0-9]+", message["source_id"]) is None:
        raise GateError("review source_id must be a retained GitHub source ID")
    if not isinstance(message["exchange"], int) or not 1 <= message["exchange"] <= 2:
        raise GateError("review exchange must be 1 or 2")
    expected_marker = f"[{message['reviewer']}]" + (
        "[HANDOFF]" if message["reviewer"] == "ASTRA" else "[REVIEW]"
    )
    if message["responder_marker"] != expected_marker:
        raise GateError("review marker does not match reviewer role")
    for key in ("evidence_refs", "limitations"):
        if not isinstance(message[key], list) or not all(isinstance(value, str) for value in message[key]):
            raise GateError(f"review {key} must be a list of strings")
    if not message["evidence_refs"]:
        raise GateError("review evidence_refs must retain at least one accessible reference")
    if not message["limitations"]:
        raise GateError("review limitations must retain at least one explicit boundary")
    if not isinstance(message["blockers"], list):
        raise GateError("review blockers must be a list")
    if not isinstance(message["next_action"], str) or not message["next_action"].strip():
        raise GateError("review next_action must be non-empty")
    if not isinstance(message["reply_required"], bool):
        raise GateError("review reply_required must be boolean")
    _validate_commit(message["reviewed_commit"], "reviewed_commit")
    _validate_sha256(message["artifact_sha256"], "artifact_sha256")
    _validate_sha256(message["reviewed_descriptor_digest"], "reviewed_descriptor_digest")


def _validate_transport_receipt(message: Mapping[str, Any], state: Mapping[str, Any]) -> None:
    receipt = message["transport_receipt"]
    required = {
        "event_type", "source_id", "url", "created_at", "body_sha256",
        "fetched_commit", "envelope_sha256", "connector_verified",
    }
    if not isinstance(receipt, Mapping) or set(receipt) != required:
        raise GateError("transport receipt shape is invalid")
    if receipt["event_type"] not in {"issue_comment", "pull_request_review"}:
        raise GateError("transport event type is invalid")
    if receipt["source_id"] != message["source_id"]:
        raise GateError("transport source ID mismatch")
    if receipt["fetched_commit"] != state["reviewed_commit"]:
        raise GateError("transport commit mismatch")
    if receipt["connector_verified"] is not True:
        raise GateError("transport was not verified by the authorized connector")
    if not isinstance(receipt["url"], str) or not receipt["url"].startswith(
        "https://github.com/alanfuller15/Twistronics/"
    ):
        raise GateError("transport URL is outside the authorized repository")
    if not isinstance(receipt["created_at"], str) or re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z",
        receipt["created_at"],
    ) is None:
        raise GateError("transport timestamp is invalid")
    _validate_sha256(receipt["body_sha256"], "body_sha256")
    normalized = {key: value for key, value in message.items() if key != "transport_receipt"}
    if receipt["envelope_sha256"] != _sha256_bytes(_canonical_json(normalized)):
        raise GateError("transport envelope hash mismatch")


def _validate_review_against_state(message: Mapping[str, Any], state: Mapping[str, Any]) -> None:
    if message["round_id"] != state["round_id"]:
        raise GateError("review round is stale or foreign")
    if message["reviewed_commit"] != state["reviewed_commit"]:
        raise GateError("review commit is stale or foreign")
    if message["artifact_sha256"] != state["artifact_sha256"]:
        raise GateError("review artifact is stale or foreign")
    if message["reviewed_descriptor_digest"] != state["descriptor_digest"]:
        raise GateError("review descriptor is stale or foreign")
    expected_reviewer = REVIEW_ORDER[message["exchange"] - 1]
    if message["reviewer"] != expected_reviewer:
        raise GateError("reviewer order must be Astra first and Claude second")
    if message["exchange"] == 1 and message["in_reply_to"] is not None:
        raise GateError("Astra handoff must not reply to another review")
    if message["exchange"] == 1 and message["status"] != "PASS":
        raise GateError("Astra handoff status must be PASS")
    if message["exchange"] == 2:
        reviews = state.get("reviews", [])
        if not reviews or message["in_reply_to"] != reviews[0]["source_id"]:
            raise GateError("Claude review must reply to the Astra source ID")
    evidence_paths = {str(item["path"]) for item in state["evidence_bindings"]}
    for ref in message["evidence_refs"]:
        if ref not in evidence_paths:
            raise GateError(f"review references unbound evidence: {ref}")
    if message["status"] == "PASS" and message["blockers"]:
        raise GateError("PASS review cannot retain blockers")
    if message["status"] != "PASS" and not message["blockers"]:
        raise GateError("non-PASS review must retain blockers")
    _validate_transport_receipt(message, state)


def ingest_review(
    state: Mapping[str, Any],
    message: Mapping[str, Any],
    source_root: Path,
    evidence_root: Path,
) -> dict[str, Any]:
    """Add one reviewer envelope, allowing at most one turn per reviewer."""

    _validate_state_shape(state)
    _validate_review_message(message)
    if state["status"] in TERMINAL_STATUSES:
        raise GateError("terminal state cannot accept another review")
    reviews = list(state["reviews"])
    if len(reviews) >= MAX_REVIEW_EXCHANGES:
        raise GateError("review exchange limit reached")
    expected_exchange = len(reviews) + 1
    if message["exchange"] != expected_exchange:
        raise GateError(f"expected exchange {expected_exchange}")
    _validate_review_against_state(message, state)
    if any(item["source_id"] == message["source_id"] for item in reviews):
        raise GateError("duplicate review source_id")
    if any(item["reviewer"] == message["reviewer"] for item in reviews):
        raise GateError("each reviewer may contribute only once")
    updated = json.loads(json.dumps(state))
    updated["reviews"].append(dict(message))
    updated["exchange_count"] = len(updated["reviews"])
    return evaluate_state(updated, source_root, evidence_root)


def evaluate_state(
    state: Mapping[str, Any], source_root: Path, evidence_root: Path
) -> dict[str, Any]:
    """Advance state without executing any scientific code."""

    _validate_state_shape(state)
    updated = json.loads(json.dumps(state))
    issues = verify_source_bindings(source_root, updated["source_bindings"])
    evidence_issues = verify_source_bindings(
        evidence_root, updated["evidence_bindings"]
    )
    issues.extend(f"evidence: {issue}" for issue in evidence_issues)
    issues.extend(_verify_typed_receipts(updated, evidence_root))
    nonpassing_gates = [
        gate_id
        for gate_id in PREPACKAGE_GATE_IDS
        if updated["gate_results"][gate_id]["status"] != "PASS"
    ]
    issues.extend(f"gate did not pass: {gate_id}" for gate_id in nonpassing_gates)
    for gate_id in POSTPACKAGE_GATE_IDS:
        if updated["gate_results"][gate_id]["status"] != "NOT_RUN":
            issues.append(f"{gate_id} must remain NOT_RUN until staged packaging")
    nonpassing_controls = [
        control_id
        for control_id in CONTROL_IDS
        if updated["negative_controls"][control_id]["status"] != "PASS"
    ]
    issues.extend(
        f"negative control did not pass: {control_id}"
        for control_id in nonpassing_controls
    )
    updated["gate"] = {
        "actual_bytes_verified": not issues,
        "issues": issues,
    }
    updated["exchange_count"] = len(updated["reviews"])
    if issues:
        updated["status"] = "BLOCKED"
        updated["notification"] = _notification("BLOCKED", "actual source bytes changed")
        return updated

    verdicts = [review["status"] for review in updated["reviews"]]
    if "MATERIAL_FINDING" in verdicts:
        updated["status"] = "MATERIAL_FINDING"
        updated["notification"] = _notification(
            "MATERIAL_FINDING", "reviewer reported a material retained-evidence finding"
        )
    elif any(verdict in {"CONDITIONAL_PASS", "BLOCKED", "STALE", "INVALID"} for verdict in verdicts):
        updated["status"] = "BLOCKED"
        updated["notification"] = _notification("BLOCKED", "reviewer requested changes")
    elif (
        len(updated["reviews"]) == MAX_REVIEW_EXCHANGES
        and set(review["reviewer"] for review in updated["reviews"]) == REVIEWERS
        and all(verdict == "PASS" for verdict in verdicts)
    ):
        updated["status"] = "PREPACKAGE_ACCEPTED"
        updated["notification"] = _notification(
            "PREPACKAGE_ACCEPTED",
            "both bounded reviewer exchanges accepted the prepackage descriptor",
        )
    else:
        updated["status"] = "IN_REVIEW"
        updated["notification"] = _notification("IN_REVIEW", "")
    return updated


def _iter_evidence_files(root: Path) -> list[tuple[str, Path]]:
    entries: list[tuple[str, Path]] = []
    collision_keys: set[str] = set()
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
        canonical = _portable_archive_name(rel)
        collision_key = unicodedata.normalize("NFC", canonical).casefold()
        if collision_key in collision_keys:
            raise GateError(f"portable archive path collision: {canonical}")
        collision_keys.add(collision_key)
        entries.append((canonical, path))
    if not entries:
        raise GateError("evidence tree has no packageable files")
    return entries


def validate_non_self_manifest(
    entries: Sequence[Mapping[str, Any]], *, manifest_name: str = "MANIFEST.json"
) -> None:
    """Reject duplicate, unsafe, malformed, or self-referential manifest entries."""

    seen: set[str] = set()
    for item in entries:
        if not isinstance(item, Mapping) or set(item) != {"path", "sha256", "size"}:
            raise GateError("manifest entry shape is invalid")
        path = _portable_archive_name(str(item["path"]))
        if path == manifest_name:
            raise GateError("manifest must not reference itself")
        if path in seen:
            raise GateError(f"duplicate manifest entry: {path}")
        seen.add(path)
        _validate_sha256(item["sha256"], "manifest sha256")
        if not isinstance(item["size"], int) or item["size"] < 0:
            raise GateError("manifest size must be a nonnegative integer")


def package_evidence(
    evidence_root: Path,
    output_zip: Path,
    *,
    expected_bindings: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
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
    actual_bindings = build_evidence_bindings(root)
    if actual_bindings != list(expected_bindings):
        raise GateError("evidence tree does not match the accepted binding")
    manifest_files: list[dict[str, Any]] = []
    snapshots: list[tuple[str, bytes]] = []
    for rel, path in files:
        payload = path.read_bytes()
        snapshots.append((rel, payload))
        manifest_files.append(
            {"path": rel, "sha256": _sha256_bytes(payload), "size": len(payload)}
        )
    manifest = {
        "schema_version": 1,
        "hash_algorithm": "sha256",
        "excluded": sorted(RESERVED_PACKAGE_PATHS),
        "files": manifest_files,
    }
    validate_non_self_manifest(manifest_files)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(
            temporary_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            for rel, payload in snapshots:
                info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, payload)
            manifest_info = zipfile.ZipInfo(
                "MANIFEST.json", date_time=(1980, 1, 1, 0, 0, 0)
            )
            manifest_info.compress_type = zipfile.ZIP_DEFLATED
            manifest_info.external_attr = 0o100644 << 16
            archive.writestr(
                manifest_info, json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            )
        with zipfile.ZipFile(temporary_path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise GateError("finished ZIP contains duplicate member names")
            expected_names = [rel for rel, _ in snapshots] + ["MANIFEST.json"]
            if sorted(names) != sorted(expected_names):
                raise GateError("finished ZIP inventory mismatch")
            retained_manifest = json.loads(archive.read("MANIFEST.json"))
            if retained_manifest != manifest:
                raise GateError("finished ZIP manifest mismatch")
            for item in manifest_files:
                payload = archive.read(item["path"])
                if len(payload) != item["size"] or _sha256_bytes(payload) != item["sha256"]:
                    raise GateError(f"finished ZIP byte mismatch: {item['path']}")
            with tempfile.TemporaryDirectory(prefix="twistronics-clean-extract-") as clean:
                clean_root = Path(clean)
                archive.extractall(clean_root)
                extracted = build_evidence_bindings(clean_root)
                if extracted != actual_bindings:
                    raise GateError("clean extraction does not reproduce evidence inventory")
        if build_evidence_bindings(root) != actual_bindings:
            raise GateError("evidence mutated during packaging")
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
        "evidence_binding_digest": binding_digest(actual_bindings),
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
    create.add_argument("--evidence-root", type=Path, required=True)
    create.add_argument("--round-id", required=True)
    create.add_argument("--baseline-sha", required=True)
    create.add_argument("--reviewed-commit", required=True)
    create.add_argument("--artifact-sha256", required=True)
    create.add_argument("--gate-results", type=Path, required=True)
    create.add_argument("--negative-controls", type=Path, required=True)
    create.add_argument("--output", type=Path, required=True)

    verify = subparsers.add_parser("verify-state")
    verify.add_argument("--state", type=Path, required=True)
    verify.add_argument("--source-root", type=Path, required=True)
    verify.add_argument("--evidence-root", type=Path, required=True)
    verify.add_argument("--output", type=Path)

    ingest = subparsers.add_parser("ingest-review")
    ingest.add_argument("--state", type=Path, required=True)
    ingest.add_argument("--message", type=Path, required=True)
    ingest.add_argument("--source-root", type=Path, required=True)
    ingest.add_argument("--evidence-root", type=Path, required=True)
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
                args.source_root,
                source_paths,
                source_label=args.source_label,
                evidence_root=args.evidence_root,
                round_id=args.round_id,
                baseline_sha=args.baseline_sha,
                reviewed_commit=args.reviewed_commit,
                artifact_sha256=args.artifact_sha256,
                gate_results=_load_json(args.gate_results),
                negative_controls=_load_json(args.negative_controls),
            )
            _write_json(args.output, state)
            print(json.dumps({"status": state["status"], "state": str(args.output)}))
            return 0
        if args.command == "verify-state":
            state = evaluate_state(
                _load_json(args.state), args.source_root, args.evidence_root
            )
            _write_json(args.output or args.state, state)
            print(json.dumps({"status": state["status"], "gate": state["gate"]}))
            return 0 if state["gate"]["actual_bytes_verified"] else 2
        if args.command == "ingest-review":
            state = ingest_review(
                _load_json(args.state),
                _load_json(args.message),
                args.source_root,
                args.evidence_root,
            )
            _write_json(args.output or args.state, state)
            print(json.dumps({"status": state["status"], "notification": state["notification"]}))
            return 0
        if args.command == "package":
            state = evaluate_state(
                _load_json(args.state), args.source_root, args.evidence_root
            )
            if state["status"] != "PREPACKAGE_ACCEPTED":
                raise GateError(
                    f"package requires PREPACKAGE_ACCEPTED state, got {state['status']}"
                )
            output_dir = args.output.resolve(strict=False)
            if output_dir.exists():
                raise GateError("acceptance bundle output already exists")
            output_dir.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(
                prefix=f".{output_dir.name}.stage-", dir=output_dir.parent
            ) as stage:
                staged_bundle = Path(stage) / "bundle"
                staged_bundle.mkdir()
                staged_output = staged_bundle / "package.zip"
                result = package_evidence(
                    args.evidence_root,
                    staged_output,
                    expected_bindings=state["evidence_bindings"],
                )
                post = evaluate_state(state, args.source_root, args.evidence_root)
                if post["status"] != "PREPACKAGE_ACCEPTED":
                    raise GateError("accepted inputs mutated during staged packaging")
                attestation = {
                    "schema_version": 1,
                    "protocol": PROTOCOL,
                    "round_id": state["round_id"],
                    "reviewed_commit": state["reviewed_commit"],
                    "descriptor_digest": state["descriptor_digest"],
                    "artifact_sha256": result["sha256"],
                    "evidence_binding_digest": result["evidence_binding_digest"],
                    "gates": {
                        **{
                            gate_id: state["gate_results"][gate_id]["status"]
                            for gate_id in PREPACKAGE_GATE_IDS
                        },
                        "G04": "PASS",
                        "G16": "PASS",
                        "G17": "PASS",
                    },
                    "negative_controls": {
                        control_id: state["negative_controls"][control_id]["status"]
                        for control_id in CONTROL_IDS
                    },
                    "reviewers": [
                        {
                            "reviewer": review["reviewer"],
                            "source_id": review["source_id"],
                            "status": review["status"],
                            "transport_receipt": review["transport_receipt"],
                        }
                        for review in state["reviews"]
                    ],
                    "limitations": sorted(
                        {
                            limitation
                            for review in state["reviews"]
                            for limitation in review["limitations"]
                        }
                    ),
                    "status": "ACCEPTED",
                }
                detached = staged_bundle / "package.zip.sha256"
                detached.write_text(
                    f"{result['sha256']}  package.zip\n", encoding="utf-8"
                )
                attestation_path = staged_bundle / "ATTESTATION.json"
                _write_json(attestation_path, attestation)
                if _load_json(attestation_path) != attestation:
                    raise GateError("staged G17 attestation failed read-back")
                if detached.read_text(encoding="utf-8").split()[0] != result["sha256"]:
                    raise GateError("staged detached digest failed read-back")
                staged_bundle.replace(output_dir)
                result.update(
                    {
                        "bundle": str(output_dir),
                        "archive": str(output_dir / "package.zip"),
                        "detached_digest": str(output_dir / "package.zip.sha256"),
                        "attestation": str(output_dir / "ATTESTATION.json"),
                        "status": "ACCEPTED",
                    }
                )
            print(json.dumps(result, sort_keys=True))
            return 0
    except (GateError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}), file=sys.stderr)
        return 2
    parser.error("unreachable command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
