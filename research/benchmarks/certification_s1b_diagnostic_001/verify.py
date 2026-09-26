#!/usr/bin/env python3
"""Offline exact-record replay. No numerical libraries or physical calls."""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import stat
from pathlib import Path

import diag_common as C
from assessments import assess


RECORD_ENVELOPE = {"kind", "sequence", "previous_record_sha256", "record_sha256"}
RECORD_PAYLOADS = {
    "HEADER": {"approved_protocol_commit", "implementation_commit", "source_bindings",
               "runtime_provenance", "runtime_provenance_digest", "test_mode",
               "evaluator", "fault", "synthetic_profile"},
    "EIGEN_STARTED": {"specimen_id"},
    "EIGEN_FINISHED": {"specimen_id", "basis", "basis_sha256"},
    "BASIS_SEALED": {"basis_hashes"},
    "CONFIG_STARTED": {"arm_id", "specimen_id", "binding"},
    "GRAM_CHECK": {"arm_id", "specimen_id", "stage", "evidence"},
    "CALL_STARTED": {"arm_id", "specimen_id", "stage", "endpoint"},
    "CALL_FINISHED": {"arm_id", "specimen_id", "stage", "endpoint",
                      "start_sequence", "evidence"},
    "CALL_SKIPPED": {"arm_id", "specimen_id", "stage", "endpoint", "reason"},
    "CONFIG_FINISHED": {"arm_id", "specimen_id"},
    "RUN_FINISHED": {"reason"},
    "RUN_ERROR": {"error_type", "message"},
}
RECEIPT_KEYS = {
    "schema_version", "approved_protocol_commit", "implementation_commit",
    "monotonic_start", "soft_deadline_at", "hard_deadline_at",
    "sigterm_sent_at_or_null", "sigkill_sent_at_or_null", "reaped_at",
    "worker_exit_code_or_signal", "post_reap_killpg_result_ESRCH",
    "durable_log_bytes", "durable_log_sha256", "termination_reason", "test_mode",
    "fault", "fault_ready_observed", "pre_trim_durable_log_bytes",
    "post_trim_durable_log_bytes",
}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def is_hash(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def reporting_fallback_contract():
    """Pinned identities for an error report, never replacement replay inputs.

    If any protocol file is unavailable or has changed, the arithmetic verifier
    must not use it. These minimal original INPUTS identities permit all seven
    explicitly unknown baseline assessments to survive that source error.
    """
    rows = [
        ("upper_left", "upper.left", 281, "492c8d1ede3833a25706b5e90276bd7debd55f5958ccd1ee798c2c2f775e47a8"),
        ("upper_right", "upper.right", 309, "ff4fba104fa85b3fc0f1fe484c1cca4216c0c9abc3ebf57237cbcd58d89a6af0"),
        ("upper_both", "upper.left+upper.right", 306, "d7a9806f25cf7f241b69863a33f12dd1a64c5ffa3c14d53b69565d106670785b"),
        ("lower_left", "lower.left", 676, "32f37166c8db151b153cbcb7919bd913eac2c39a85f523a2518a9e6ecaed8294"),
        ("lower_both", "lower.left+lower.right", 708, "fa7967168f7d8f8d362a546123fe1cdb17ac483e9f72fbcccd71842cb2395f05"),
        ("accepted_upper", "accepted", 379, "89c3bf171e0a0e3b36c6feed00986acba098a199719fbc18b08bd88421d6cacf"),
        ("accepted_lower", "accepted", 707, "65c58268f7e1c134ed69f645ac68a5d2df4ad3bcb97aba3e8f0cc3be188aac80"),
    ]
    spec = {
        "specimen_order": [row[0] for row in rows],
        "endpoint_order": ["lower.left", "lower.right", "upper.left", "upper.right"],
        "expected_negative_counts": [97, 97, 99, 99],
        "arms_in_order": [{"id": name} for name in (
            "original_128", "point_128", "point_256", "original_256",
            "original_reverse_128", "half_128", "quarter_128", "eighth_128")],
    }
    inputs = {"specimens": [{"id": sid, "historical_signature": signature,
                              "source_sequence": sequence, "source_record_sha256": sha}
                             for sid, signature, sequence, sha in rows]}
    return spec, inputs


def bounded_evidence_read(path, cap):
    """Return a bounded prefix and any read error without following symlinks."""
    data = b""
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            require(stat.S_ISREG(before.st_mode), "EVIDENCE_NOT_REGULAR_FILE")
            data = stream.read(cap + 1)
            after = os.fstat(stream.fileno())
        if len(data) > cap or before.st_size > cap:
            return data, "EVIDENCE_BYTE_CAP"
        require((before.st_size, before.st_mtime_ns, before.st_ino) ==
                (after.st_size, after.st_mtime_ns, after.st_ino) and
                len(data) == before.st_size, "EVIDENCE_CHANGED_DURING_READ")
        return data, None
    except Exception as exc:
        return data, safe_error(exc)


def checked_factor(value, expected, dimension=196):
    require(isinstance(value, dict), "FACTOR_SCHEMA")
    keys = {"status", "negative", "pivots"}
    if value.get("status") == "INCONCLUSIVE":
        keys.add("pivot_index")
    require(set(value) == keys and isinstance(value["pivots"], list), "FACTOR_SCHEMA")
    pivots = [C.interval(p) for p in value["pivots"]]
    require(0 < len(pivots) <= dimension and type(value["negative"]) is int, "PIVOT_COUNT")
    if value["status"] == "CERTIFIED":
        require(len(pivots) == dimension, "FULL_INERTIA_REQUIRES_ALL_PIVOTS")
        signed = pivots
        outcome = "EXPECTED_INERTIA_VERIFIED" if value["negative"] == expected else "OTHER_INERTIA_VERIFIED"
    else:
        require(value["status"] == "INCONCLUSIVE" and type(value["pivot_index"]) is int
                and value["pivot_index"] == len(pivots) - 1, "ZERO_PIVOT_INDEX")
        require(pivots[-1][0] <= 0 <= pivots[-1][1], "FAILED_PIVOT_MUST_CONTAIN_ZERO")
        signed = pivots[:-1]
        outcome = "ZERO_CONTAINING_PIVOT"
    require(all(lo > 0 or hi < 0 for lo, hi in signed), "EARLIER_UNSIGNED_PIVOT")
    require(value["negative"] == sum(hi < 0 for _, hi in signed), "PIVOT_NEGATIVE_COUNT")
    return outcome


class Replay:
    def __init__(self, spec, inputs, commit, bindings, allow_test_mode=False):
        self.spec, self.inputs, self.commit = spec, inputs, commit
        self.bindings, self.allow_test_mode = bindings, allow_test_mode
        self.ids = spec["specimen_order"]
        self.specimens = {x["id"]: x for x in inputs["specimens"]}
        self.order = [(a, self.specimens[s]) for a in spec["arms_in_order"] for s in self.ids]
        self.bases, self.basis_hashes, self.eigen_started = {}, {}, []
        self.sealed = False
        self.configurations, self.evidence = {}, {}
        self.config_index = 0
        self.active = None
        self.pending = None
        self.phase = None
        self.primary_count = self.repeat_count = 0
        self.header = None
        self.finished = None
        self.valid_records = 0
        self.valid_bytes = 0
        self.previous = None
        self.error = None
        self.config_start_bytes = None

    def record(self, rec):
        kind = rec["kind"]
        require(type(kind) is str and kind in RECORD_PAYLOADS and
                set(rec) == RECORD_ENVELOPE | RECORD_PAYLOADS[kind], "EXACT_RECORD_SCHEMA")
        if self.header is None:
            require(kind == "HEADER", "HEADER_REQUIRED")
            require(type(rec["implementation_commit"]) is str and
                    re.fullmatch(r"[0-9a-f]{40}", rec["implementation_commit"]) is not None,
                    "HEADER_COMMIT_FORMAT")
            require(rec["approved_protocol_commit"] == C.APPROVED_PROTOCOL_COMMIT
                    and rec["implementation_commit"] == self.commit, "HEADER_COMMIT_BINDING")
            require(C.canonical_bytes(rec["source_bindings"]) == C.canonical_bytes(self.bindings), "HEADER_SOURCE_CLOSURE")
            test = rec.get("test_mode")
            require(type(test) is bool and (not test or self.allow_test_mode), "TEST_MODE_NOT_ALLOWED")
            require(rec["evaluator"] == ("synthetic" if test else "physical"), "EVALUATOR_IDENTITY")
            provenance = rec["runtime_provenance"]
            require(C.digest(provenance) == rec["runtime_provenance_digest"], "RUNTIME_DIGEST")
            if test:
                require(provenance == {"synthetic": True, "fixture": "exact_diagonal_rational_v1",
                                       "synthetic_profile": rec["synthetic_profile"], "numerical_imports": False},
                        "SYNTHETIC_PROVENANCE")
                require(rec["synthetic_profile"] in ("default", "divergence", "control_mismatch", "gram_failure", "wrong_inertia", "mixed"), "SYNTHETIC_PROFILE")
                require(rec["fault"] in ("none", "partial_then_block"), "SYNTHETIC_FAULT")
            else:
                require(rec["fault"] == "none" and rec["synthetic_profile"] is None, "PHYSICAL_FAULT_FORBIDDEN")
                import runtime_identity
                runtime_identity.verify(provenance)
            self.header = rec
            return
        require(self.finished is None, "EVENT_AFTER_TERMINATION")
        if kind == "RUN_ERROR":
            require(isinstance(rec.get("error_type"), str) and isinstance(rec.get("message"), str), "ERROR_EVENT_SCHEMA")
            self.finished = "ERROR"
            return
        if not self.sealed:
            index = len(self.bases)
            if kind == "EIGEN_STARTED":
                require(index < 7 and len(self.eigen_started) == index
                        and rec["specimen_id"] == self.ids[index], "EIGEN_START_ORDER_OR_CAP")
                self.eigen_started.append(rec["specimen_id"])
            elif kind == "EIGEN_FINISHED":
                require(index < 7 and len(self.eigen_started) == index + 1
                        and rec["specimen_id"] == self.ids[index], "EIGEN_FINISH_ORDER")
                basis = rec["basis"]
                require(isinstance(basis, list) and len(basis) == 196
                        and all(isinstance(row, list) and len(row) == 196 for row in basis), "BASIS_DIMENSION")
                for row in basis:
                    for item in row:
                        C.rational(item)
                require(C.digest(basis) == rec["basis_sha256"], "BASIS_DIGEST")
                self.bases[rec["specimen_id"]] = basis
                self.basis_hashes[rec["specimen_id"]] = rec["basis_sha256"]
            elif kind == "BASIS_SEALED":
                require(len(self.bases) == 7 and rec["basis_hashes"] == self.basis_hashes, "BASIS_SEAL_MEMBERSHIP")
                self.sealed = True
            else:
                raise ValueError("ALL_BASES_MUST_PRECEDE_ARMS")
            return
        if self.active is None:
            if kind == "RUN_FINISHED":
                reason = rec["reason"]
                require(reason in ("COMPLETE", "RESOURCE_CAP"), "RUN_FINISH_REASON")
                if reason == "COMPLETE":
                    require(self.config_index == 56, "PREMATURE_COMPLETE")
                else:
                    # A resource stop is valid only if the next frozen admission fails.
                    require(self.config_index < 56 and
                            (self.primary_count + 4 > 224 or self.repeat_count + 4 > 224
                             or self.valid_bytes + 20 * 1048576 > 268435456), "UNJUSTIFIED_RESOURCE_CAP")
                self.finished = reason
                return
            require(kind == "CONFIG_STARTED" and self.config_index < 56, "CONFIG_START_ORDER_OR_CAP")
            arm, specimen = self.order[self.config_index]
            require(rec["arm_id"] == arm["id"] and rec["specimen_id"] == specimen["id"], "FROZEN_CONFIGURATION_ORDER")
            require(C.canonical_bytes(rec["binding"]) == C.canonical_bytes(C.config_binding(specimen, arm, self.basis_hashes[specimen["id"]])), "CONFIGURATION_BINDING")
            require(self.primary_count + 4 <= 224 and self.repeat_count + 4 <= 224
                    and self.valid_bytes + 20 * 1048576 <= 268435456, "CONFIGURATION_ADMISSION")
            self.active = (arm["id"], specimen["id"])
            self.configurations[self.active] = {"outcomes": {"primary": {}, "repeat": {}}, "completed": False,
                                               "gram_positive": {}}
            self.evidence[self.active] = {"primary": {}, "repeat": {}, "gram": {}}
            self.phase = ("gram", "primary", 0)
            self.config_start_bytes = self.valid_bytes
            return
        arm, specimen = self.order[self.config_index]
        require((rec.get("arm_id"), rec.get("specimen_id")) == self.active, "ACTIVE_CONFIGURATION_IDENTITY")
        config, ev = self.configurations[self.active], self.evidence[self.active]
        phase, stage, index = self.phase
        endpoints = self.spec["endpoint_order"]
        if phase == "gram":
            require(kind == "GRAM_CHECK" and rec["stage"] == stage, "GRAM_EVENT_ORDER")
            value = rec["evidence"]
            require(isinstance(value, dict) and set(value) == {"assembly_precision_bits", "basis_roundtrip_sha256", "gram_margins", "unpermuted_gram_sha256", "gram_matrix_sha256", "unpermuted_K_sha256", "K_sha256", "permutation"}, "GRAM_SCHEMA")
            require(type(value["assembly_precision_bits"]) is int and value["assembly_precision_bits"] == arm["precision_bits"], "FRESH_ASSEMBLY_PRECISION")
            require(value["basis_roundtrip_sha256"] == self.basis_hashes[specimen["id"]], "ARM_BASIS_BINDING")
            expected_perm = C.config_binding(specimen, arm, "")["permutation"]
            require(value["permutation"] == expected_perm and all(type(i) is int for i in value["permutation"]), "EXACT_PERMUTATION")
            require(isinstance(value["gram_margins"], list) and len(value["gram_margins"]) == 196, "GRAM_MARGIN_COUNT")
            positive = all(C.interval(x)[0] > 0 for x in value["gram_margins"])
            # Validate every interval, even after the first nonpositive margin.
            for item in value["gram_margins"]:
                C.interval(item)
            for name in ("unpermuted_gram_sha256", "gram_matrix_sha256"):
                require(is_hash(value[name]), "GRAM_HASH_FORMAT")
            for name in ("unpermuted_K_sha256", "K_sha256"):
                require(isinstance(value[name], list) and len(value[name]) == 4 and all(map(is_hash, value[name])), "K_HASH_FORMAT")
            if arm["column_order"] == "identity":
                require(value["unpermuted_gram_sha256"] == value["gram_matrix_sha256"] and value["unpermuted_K_sha256"] == value["K_sha256"], "IDENTITY_MATRIX_HASHES")
            else:
                baseline = self.evidence[("original_128", specimen["id"])]["gram"]["primary"]
                require(value["unpermuted_gram_sha256"] == baseline["unpermuted_gram_sha256"]
                        and value["unpermuted_K_sha256"] == baseline["unpermuted_K_sha256"], "REVERSE_CHANGED_CANONICAL_MATRICES")
                require(value["gram_margins"] == list(reversed(baseline["gram_margins"])), "REVERSE_GRAM_MARGIN_ORDER")
            if stage == "repeat":
                require(value == ev["gram"]["primary"], "GRAM_OR_MATRIX_REPEAT_MISMATCH")
            ev["gram"][stage] = value
            config["gram_positive"][stage] = positive
            if positive:
                self.phase = ("start", stage, 0)
            elif stage == "primary":
                self.phase = ("gram", "repeat", 0)
            else:
                self.phase = ("skip", "primary", 0)
            return
        if phase in ("start", "finish", "skip"):
            require(rec.get("stage") == stage and rec.get("endpoint") == endpoints[index], "ENDPOINT_ORDER")
            if phase == "start":
                require(kind == "CALL_STARTED" and config["gram_positive"][stage], "CALL_START_WITHOUT_GRAM")
                count = self.primary_count if stage == "primary" else self.repeat_count
                require(count < 224, "CALL_START_CAP")
                if stage == "primary":
                    self.primary_count += 1
                else:
                    self.repeat_count += 1
                self.pending = {"arm_id": arm["id"], "specimen_id": specimen["id"], "stage": stage,
                                "endpoint": endpoints[index], "start_sequence": rec["sequence"]}
                self.phase = ("finish", stage, index)
                return
            if phase == "finish":
                require(kind == "CALL_FINISHED" and type(rec["start_sequence"]) is int and
                        rec["start_sequence"] == self.pending["start_sequence"], "CALL_FINISH_START_BINDING")
                factor = rec["evidence"]
                outcome = checked_factor(factor, self.spec["expected_negative_counts"][index])
                if stage == "repeat":
                    require(factor == ev["primary"][endpoints[index]], "ENDPOINT_REPEAT_MISMATCH")
                ev[stage][endpoints[index]] = factor
                config["outcomes"][stage][endpoints[index]] = outcome
                self.pending = None
            else:
                require(kind == "CALL_SKIPPED" and rec["reason"] == "GRAM_UNCERTIFIED"
                        and config["gram_positive"] == {"primary": False, "repeat": False}, "GRAM_SKIP_CONTRACT")
                config["outcomes"][stage][endpoints[index]] = "GRAM_UNCERTIFIED"
            if index < 3:
                self.phase = ("skip" if phase == "skip" else "start", stage, index + 1)
            elif stage == "primary":
                self.phase = ("skip", "repeat", 0) if phase == "skip" else ("gram", "repeat", 0)
            else:
                self.phase = ("config_finish", "repeat", 4)
            return
        require(phase == "config_finish" and kind == "CONFIG_FINISHED", "CONFIG_FINISH_ORDER")
        config["completed"] = True
        self.config_index += 1
        self.active = None
        self.config_start_bytes = None

    def consume(self, raw):
        offset = 0
        for line in raw.splitlines(keepends=True):
            try:
                require(len(line) <= 16 * 1048576, "RECORD_SIZE_CAP")
                require(line.endswith(b"\n"), "UNTERMINATED_RECORD")
                rec = json.loads(line)
                require(isinstance(rec, dict) and C.canonical_bytes(rec) + b"\n" == line, "NONCANONICAL_RECORD")
                require(type(rec["sequence"]) is int and rec["sequence"] == self.valid_records, "RECORD_SEQUENCE")
                unsigned = {k: v for k, v in rec.items() if k != "record_sha256"}
                require(C.digest(unsigned) == rec["record_sha256"], "RECORD_SELF_HASH")
                require(rec["previous_record_sha256"] == self.previous, "RECORD_CHAIN")
                require(offset + len(line) <= 268435456, "RAW_LOG_CAP")
                if not self.sealed:
                    require(offset + len(line) <= 16 * 1048576, "BASIS_ENVELOPE_CAP")
                if self.config_start_bytes is not None and rec.get("kind") != "RUN_ERROR":
                    require(offset + len(line) - self.config_start_bytes <= 4 * 1048576, "CONFIGURATION_EVIDENCE_CAP")
                self.record(rec)
            except Exception as exc:
                self.error = "LOG_RECORD_%d:%s" % (self.valid_records, safe_error(exc))
                break
            self.valid_records += 1
            offset += len(line)
            self.valid_bytes = offset
            self.previous = C.sha256_bytes(line[:-1])
        if not raw and self.error is None:
            self.error = "EMPTY_EVENT_LOG"


def safe_error(exc):
    # Internal error codes only: no tracebacks, host paths or environment text.
    message = str(exc)
    return message if re.fullmatch(r"[A-Z0-9_:.-]{1,160}", message) else type(exc).__name__


def check_receipt(receipt, raw, commit, header, allow_test_mode):
    require(isinstance(receipt, dict) and set(receipt) == RECEIPT_KEYS and
            type(receipt.get("schema_version")) is int and receipt["schema_version"] == 1,
            "RECEIPT_SCHEMA")
    require(type(receipt["implementation_commit"]) is str and
            re.fullmatch(r"[0-9a-f]{40}", receipt["implementation_commit"]) is not None,
            "RECEIPT_COMMIT_FORMAT")
    require(receipt["approved_protocol_commit"] == C.APPROVED_PROTOCOL_COMMIT
            and receipt["implementation_commit"] == commit, "RECEIPT_COMMIT_BINDING")
    require(type(receipt["test_mode"]) is bool and (not receipt["test_mode"] or allow_test_mode), "RECEIPT_TEST_MODE")
    require(type(receipt["fault_ready_observed"]) is bool, "RECEIPT_FAULT_READY_TYPE")
    if header:
        require(receipt["test_mode"] == header["test_mode"] and receipt["fault"] == header["fault"], "RECEIPT_HEADER_MODE")
    require(type(receipt["durable_log_bytes"]) is int and receipt["durable_log_bytes"] == len(raw)
            and receipt["durable_log_sha256"] == C.sha256_bytes(raw), "RECEIPT_LOG_BINDING")
    require(receipt["post_reap_killpg_result_ESRCH"] is True, "WORKER_GROUP_NOT_REAPED")
    names = ("monotonic_start", "soft_deadline_at", "hard_deadline_at", "reaped_at")
    for name in names:
        require(type(receipt[name]) in (int, float) and math.isfinite(receipt[name]), "RECEIPT_CLOCK_FORMAT")
    start, soft, hard, reap = [receipt[n] for n in names]
    require(start <= reap and start < soft < hard, "RECEIPT_DEADLINE_ORDER")
    if not receipt["test_mode"]:
        require(abs(soft - start - 1200) < 1e-6 and abs(hard - start - 1260) < 1e-6, "PHYSICAL_DEADLINES")
        require(receipt["fault"] == "none" and receipt["fault_ready_observed"] is False, "PHYSICAL_FAULT_RECEIPT")
    term, kill = [receipt[n] for n in ("sigterm_sent_at_or_null", "sigkill_sent_at_or_null")]
    for t in (term, kill):
        require(t is None or (type(t) in (int, float) and math.isfinite(t) and start <= t <= reap), "SIGNAL_TIME_ORDER")
    if term is not None:
        require(soft <= term <= hard + 1, "SIGTERM_DEADLINE")
    if kill is not None:
        require(term is not None and term <= kill and hard <= kill <= hard + 1, "SIGKILL_DEADLINE")
    pre, post = receipt["pre_trim_durable_log_bytes"], receipt["post_trim_durable_log_bytes"]
    require(type(pre) is int and type(post) is int and pre >= post == len(raw), "TRIM_LENGTHS")
    reason, rc = receipt["termination_reason"], receipt["worker_exit_code_or_signal"]
    require(type(rc) is int, "WORKER_RETURN_CODE")
    if reason == "NORMAL_EXIT":
        require(rc == 0 and term is None and kill is None and pre == post and reap <= hard + 1, "NORMAL_RECEIPT_CONTRADICTION")
    elif reason == "WATCHDOG_TIMEOUT":
        require(term is not None or kill is not None, "WATCHDOG_WITHOUT_SIGNAL")
        require(reap <= hard + 2, "LATE_WORKER_REAP")
        expected_signal = -9 if kill is not None else -15
        require(rc in (0, expected_signal), "WATCHDOG_UNEXPECTED_WORKER_EXIT")
    else:
        require(reason == "UNEXPECTED_EXIT", "RECEIPT_TERMINATION_REASON")
        require(rc != 0 or term is not None or kill is not None, "UNEXPECTED_EXIT_WITHOUT_ERROR")
    return reason


def finalize(output, implementation_commit, allow_test_mode=False, check_only=False):
    """Always retain prefix-derived flags in RESULTS, including execution errors."""
    from package_io import package_plan, write_manifest
    output = Path(output)
    errors = []
    existing_manifest_invalid = False
    # Existing finalized evidence is an input with its own binding, not a cache
    # that a default finalization may silently replace after tampering.
    if (output / "RESULTS.json").exists() or (output / "MANIFEST.json").exists():
        try:
            write_manifest(output, check_only=True)
        except Exception as exc:
            if check_only:
                raise
            existing_manifest_invalid = True
            errors.append("EXISTING_MANIFEST:" + safe_error(exc))
    contract_valid = True
    try:
        spec, inputs = C.load_contract()
    except Exception as exc:
        contract_valid = False
        spec, inputs = reporting_fallback_contract()
        errors.append("PROTOCOL:" + safe_error(exc))
    try:
        bindings = C.verify_implementation_files() if contract_valid else None
    except Exception as exc:
        bindings = None
        errors.append("SOURCE:" + safe_error(exc))
    raw_path, receipt_path = output / "EVENTS.ndjson", output / "SUPERVISOR_RECEIPT.json"
    raw, raw_read_error = bounded_evidence_read(raw_path, 268435456)
    receipt_bytes, receipt_read_error = bounded_evidence_read(receipt_path, 16 * 1048576)
    if raw_read_error:
        errors.append("EVENTS_READ:" + raw_read_error)
    if receipt_read_error:
        errors.append("RECEIPT_READ:" + receipt_read_error)
    replay = Replay(spec, inputs, implementation_commit, bindings, allow_test_mode)
    if bindings is not None:
        replay.consume(raw)
        if replay.error:
            errors.append(replay.error)
    try:
        receipt = json.loads(receipt_bytes)
        reason = check_receipt(receipt, raw, implementation_commit, replay.header, allow_test_mode)
    except Exception as exc:
        receipt, reason = {}, "INVALID_RECEIPT"
        errors.append("RECEIPT:" + safe_error(exc))
    allowed = {"EVENTS.ndjson", "SUPERVISOR_RECEIPT.json", "RESULTS.json", "MANIFEST.json"}
    try:
        members = list(output.iterdir())
        actual = {p.name for p in members}
        membership_valid = not (actual - allowed or
                               any(p.is_symlink() or not p.is_file() for p in members))
    except Exception as exc:
        actual, membership_valid = set(), False
        errors.append("OUTPUT_READ:" + safe_error(exc))
    if not membership_valid:
        errors.append("OUTPUT_MEMBERSHIP")
    if reason == "UNEXPECTED_EXIT" or replay.finished == "ERROR":
        errors.append("WORKER_EXECUTION_ERROR")
    if not errors and reason != "WATCHDOG_TIMEOUT" and replay.finished not in ("COMPLETE", "RESOURCE_CAP"):
        errors.append("INCOMPLETE_WITHOUT_VALID_STOP")
    try:
        package, _ = package_plan(raw)
    except Exception as exc:
        package = None
        errors.append("PACKAGE:" + safe_error(exc))
    reviewed = assess(spec, inputs, replay.configurations, invalid_reason=";".join(errors) or None)
    if errors:
        status = "EXECUTION_ERROR"
    elif reason == "WATCHDOG_TIMEOUT":
        status = "DIAGNOSTIC_INCOMPLETE_WATCHDOG"
    elif replay.finished == "RESOURCE_CAP":
        status = "DIAGNOSTIC_INCOMPLETE_RESOURCE_CAP"
    elif reviewed["control_mismatch_detected"] is True:
        status = "CONTROL_MISMATCH_REVIEW_REQUIRED"
    else:
        require(replay.config_index == 56 and reviewed["control_mismatch_detected"] is False, "COMPLETE_REQUIRES_ALL_CONTROLS")
        status = "DIAGNOSTIC_COMPLETE"
    configurations = []
    pending_configs = []
    for arm, specimen in replay.order:
        key = (arm["id"], specimen["id"])
        cfg = replay.configurations.get(key)
        if cfg is None or not cfg["completed"]:
            pending_configs.append({"arm_id": key[0], "specimen_id": key[1]})
        configurations.append({"arm_id": key[0], "specimen_id": key[1],
                               "state": "NOT_STARTED" if cfg is None else "COMPLETE" if cfg["completed"] else "INCOMPLETE",
                               "outcomes": cfg["outcomes"] if cfg else {"primary": {}, "repeat": {}},
                               "gram_positive": cfg["gram_positive"] if cfg else {}})
    result = {
        "schema_version": 1, "packet_id": "S1B-DIAGNOSTIC-001",
        "approved_protocol_commit": C.APPROVED_PROTOCOL_COMMIT,
        "implementation_commit": implementation_commit,
        "status": status, "errors": errors,
        "test_mode": replay.header["test_mode"] if replay.header else receipt.get("test_mode"),
        "runtime_provenance_digest": replay.header["runtime_provenance_digest"] if replay.header else None,
        "event_package": package,
        "receipt_sha256": C.sha256_bytes(receipt_bytes),
        "validated_prefix": {"records": replay.valid_records, "bytes": replay.valid_bytes,
                             "last_complete_record_sha256": replay.previous},
        "eigensolver_calls_started": len(replay.eigen_started), "bases_retained": len(replay.bases),
        "primary_factorizations_started": replay.primary_count,
        "verification_factorizations_started": replay.repeat_count,
        "configurations_completed": replay.config_index,
        "interrupted_call": replay.pending,
        "pending_eigensolver_specimens": [s for s in replay.ids if s not in replay.bases],
        "pending_configurations": pending_configs, "configurations": configurations,
        "basis_hashes": replay.basis_hashes,
        **reviewed,
        "coverage_unchanged": "29663/65536",
        "scientific_claim": "None; fixed-specimen diagnostic only. No coverage or historical repair is established.",
        "verification_limit": "Exact rational record checks, source/runtime bindings and same-backend repeated evidence; no offline numerical recomputation.",
    }
    if check_only:
        require(actual == allowed, "RAW_EXACT_MEMBERSHIP")
        require((output / "RESULTS.json").read_bytes() == C.json_bytes(result), "RESULTS_REPLAY_MISMATCH")
        write_manifest(output, check_only=True)
    else:
        C.atomic_json(output / "RESULTS.json", result)
        try:
            if not existing_manifest_invalid:
                write_manifest(output)
        except Exception as exc:
            # A strict manifest writer must reject missing/unexpected entries,
            # but that rejection must not erase a valid prefix's review flags.
            errors.append("MANIFEST:" + safe_error(exc))
            result["status"] = "EXECUTION_ERROR"
            result.update(assess(spec, inputs, replay.configurations,
                                 invalid_reason=";".join(errors)))
            C.atomic_json(output / "RESULTS.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--implementation-commit", required=True)
    parser.add_argument("--allow-test-mode", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--hosted-output", type=Path)
    parser.add_argument("--materialize", type=Path, help="Reconstruct this hosted directory into output first")
    args = parser.parse_args()
    if args.materialize:
        from package_io import materialize
        materialize(args.materialize, args.output)
    result = finalize(args.output, args.implementation_commit, args.allow_test_mode,
                      check_only=args.check_only or bool(args.materialize))
    if args.hosted_output:
        require(result["status"] != "EXECUTION_ERROR", "DO_NOT_HOST_INVALID_PACKET")
        from package_io import write_hosted
        write_hosted(args.output, args.hosted_output)
    print(json.dumps({"status": result["status"], "configurations_completed": result["configurations_completed"]}, sort_keys=True))
    return 1 if result["status"] == "EXECUTION_ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
