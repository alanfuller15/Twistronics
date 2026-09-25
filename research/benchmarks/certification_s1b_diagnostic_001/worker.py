#!/usr/bin/env python3
"""Bounded diagnostic worker; physical execution requires the separate audit gate.

The worker writes only the durable event log.  The offline verifier, never this
process, derives baseline comparisons, review flags, and the terminal outcome.
Synthetic mode uses exact diagonal fixtures and does not import a numerical
library or evaluate the physical model.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import resource
import signal
import sys
from fractions import Fraction
from pathlib import Path

import diag_common as common


PROFILES = ("default", "divergence", "control_mismatch", "gram_failure",
            "wrong_inertia", "mixed")
MIB = 1024 * 1024


class WorkerError(RuntimeError):
    """An intentionally path-free failure code safe to retain in the log."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise WorkerError(code)


def rational(value: object) -> Fraction:
    require(type(value) is str, "RATIONAL_MUST_BE_STRING")
    try:
        number = Fraction(value)
    except (ValueError, ZeroDivisionError):
        raise WorkerError("INVALID_RATIONAL") from None
    require(str(number) == value, "NONCANONICAL_RATIONAL")
    return number


def interval(value: object) -> tuple[Fraction, Fraction]:
    require(type(value) is list and len(value) == 2, "INVALID_INTERVAL_SHAPE")
    lo, hi = map(rational, value)
    require(lo <= hi, "REVERSED_INTERVAL")
    return lo, hi


def check_basis(basis: object, dimension: int) -> None:
    require(type(basis) is list and len(basis) == dimension, "INVALID_BASIS_ROWS")
    for row in basis:
        require(type(row) is list and len(row) == dimension, "INVALID_BASIS_COLUMNS")
        for value in row:
            rational(value)


def check_prepared(prepared: dict, arm: dict, basis_sha: str,
                   dimension: int) -> dict:
    evidence = prepared["evidence"]
    expected_keys = {
        "assembly_precision_bits", "basis_roundtrip_sha256", "gram_margins",
        "unpermuted_gram_sha256", "gram_matrix_sha256", "unpermuted_K_sha256",
        "K_sha256", "permutation",
    }
    require(type(evidence) is dict and set(evidence) == expected_keys,
            "PREPARED_EVIDENCE_KEYS")
    require(type(evidence["assembly_precision_bits"]) is int and
            evidence["assembly_precision_bits"] == arm["precision_bits"],
            "ASSEMBLY_PRECISION_MISMATCH")
    require(evidence["basis_roundtrip_sha256"] == basis_sha,
            "SERIALIZED_BASIS_MISMATCH")
    require(type(evidence["gram_margins"]) is list and
            len(evidence["gram_margins"]) == dimension, "GRAM_MARGIN_COUNT")
    margins = [interval(pair) for pair in evidence["gram_margins"]]
    gram_ok = all(lo > 0 for lo, _ in margins)
    require(type(prepared.get("gram_certified")) is bool and
            prepared["gram_certified"] == gram_ok, "GRAM_CERTIFICATION_MISMATCH")
    permutation = list(range(dimension))
    if arm["column_order"] == "reverse_195_to_0":
        permutation.reverse()
    else:
        require(arm["column_order"] == "identity", "UNSUPPORTED_COLUMN_ORDER")
    require(evidence["permutation"] == permutation and
            all(type(i) is int for i in evidence["permutation"]),
            "PERMUTATION_MISMATCH")
    hashes = [evidence["unpermuted_gram_sha256"], evidence["gram_matrix_sha256"]]
    for key in ("unpermuted_K_sha256", "K_sha256"):
        require(type(evidence[key]) is list and len(evidence[key]) == 4,
                "MATRIX_HASH_COUNT")
        hashes.extend(evidence[key])
    require(all(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value)
                for value in hashes), "INVALID_MATRIX_HASH")
    if arm["column_order"] == "identity":
        require(evidence["unpermuted_K_sha256"] == evidence["K_sha256"] and
                evidence["unpermuted_gram_sha256"] == evidence["gram_matrix_sha256"],
                "IDENTITY_MATRIX_HASH_MISMATCH")
    return evidence


def check_factor(evidence: dict, dimension: int) -> None:
    require(type(evidence) is dict, "INVALID_FACTOR_EVIDENCE")
    status = evidence.get("status")
    keys = {"status", "negative", "pivots"}
    if status == "INCONCLUSIVE":
        keys.add("pivot_index")
    require(set(evidence) == keys, "FACTOR_EVIDENCE_KEYS")
    require(type(evidence["pivots"]) is list, "INVALID_PIVOT_LIST")
    pivots = [interval(pair) for pair in evidence["pivots"]]
    require(1 <= len(pivots) <= dimension, "PIVOT_COUNT")
    require(type(evidence["negative"]) is int, "INVALID_NEGATIVE_COUNT")
    if status == "CERTIFIED":
        require(len(pivots) == dimension, "INCOMPLETE_CERTIFIED_PIVOTS")
        signed = pivots
    elif status == "INCONCLUSIVE":
        require(type(evidence["pivot_index"]) is int and
                evidence["pivot_index"] == len(pivots) - 1,
                "FAILED_PIVOT_INDEX")
        require(pivots[-1][0] <= 0 <= pivots[-1][1], "FAILED_PIVOT_EXCLUDES_ZERO")
        signed = pivots[:-1]
    else:
        raise WorkerError("INVALID_FACTOR_STATUS")
    require(all(lo > 0 or hi < 0 for lo, hi in signed), "UNSIGNED_PRIOR_PIVOT")
    require(evidence["negative"] == sum(hi < 0 for _, hi in signed),
            "NEGATIVE_COUNT_MISMATCH")


class SyntheticEngine:
    """Exact fixtures exercising replay states, with no physical meaning."""

    def __init__(self, spec: dict, profile: str):
        self.spec = spec
        self.profile = profile
        self.dimension = spec["dimension"]
        self.runtime_provenance = {
            "synthetic": True,
            "fixture": "exact_diagonal_rational_v1",
            "synthetic_profile": profile,
            "numerical_imports": False,
        }

    def make_basis(self, specimen: dict) -> list[list[str]]:
        return [["1" if i == j else "0" for j in range(self.dimension)]
                for i in range(self.dimension)]

    def _baseline_kind(self, specimen: dict, endpoint: str) -> str:
        sid = specimen["id"]
        if sid == "upper_left" and self.profile in ("divergence", "mixed"):
            return "pass"
        if sid == "accepted_lower" and self.profile in ("control_mismatch", "mixed"):
            return "zero" if endpoint == "lower.left" else "pass"
        if sid == "upper_left" and self.profile == "wrong_inertia":
            return "wrong" if endpoint == "upper.left" else "pass"
        failed = specimen["historical_signature"].split("+")
        return "zero" if endpoint in failed else "pass"

    @staticmethod
    def _matrix_hash(diagonal: list[list[str]]) -> str:
        # Canonical expanded matrix, deliberately matching the row-major
        # interval representation used for these synthetic diagonal fixtures.
        zero = ["0", "0"]
        matrix = [[diagonal[i] if i == j else zero for j in range(len(diagonal))]
                  for i in range(len(diagonal))]
        return common.digest(matrix)

    def prepare(self, specimen: dict, arm: dict, basis: list[list[str]]) -> dict:
        is_baseline_box = arm["id"] in ("original_128", "original_reverse_128")
        gram_failure = (is_baseline_box and specimen["id"] == "lower_both" and
                        self.profile in ("gram_failure", "mixed"))
        gram_diagonal = [["0", "0"] if gram_failure and i == 0 else ["1", "1"]
                         for i in range(self.dimension)]
        permutation = list(range(self.dimension))
        if arm["column_order"] == "reverse_195_to_0":
            permutation.reverse()
        diagonals = []
        unpermuted_hashes = []
        hashes = []
        for index, endpoint in enumerate(self.spec["endpoint_order"]):
            kind = self._baseline_kind(specimen, endpoint) if is_baseline_box else "pass"
            negative = self.spec["expected_negative_counts"][index] + (kind == "wrong")
            diagonal = [["-1", "-1"] if i < negative else ["1", "1"]
                        for i in range(self.dimension)]
            if kind == "zero":
                diagonal[0] = ["-1", "1"]
            unpermuted_hashes.append(self._matrix_hash(diagonal))
            diagonal = [diagonal[i] for i in permutation]
            hashes.append(self._matrix_hash(diagonal))
            diagonals.append(diagonal)
        gram_hash = self._matrix_hash(gram_diagonal)
        permuted_gram = [gram_diagonal[i] for i in permutation]
        evidence = {
            "assembly_precision_bits": arm["precision_bits"],
            "basis_roundtrip_sha256": common.digest(basis),
            "gram_margins": permuted_gram,
            "unpermuted_gram_sha256": gram_hash,
            "gram_matrix_sha256": self._matrix_hash(permuted_gram),
            "unpermuted_K_sha256": unpermuted_hashes,
            "K_sha256": hashes,
            "permutation": permutation,
        }
        return {"evidence": evidence, "diagonals": diagonals,
                "gram_certified": not gram_failure}

    def factor(self, prepared: dict, index: int) -> dict:
        require(prepared["gram_certified"], "FACTOR_WITH_UNCERTIFIED_GRAM")
        pivots = []
        negative = 0
        for position, pivot in enumerate(prepared["diagonals"][index]):
            pivots.append(copy.deepcopy(pivot))
            lo, hi = interval(pivot)
            if lo <= 0 <= hi:
                return {"status": "INCONCLUSIVE", "negative": negative,
                        "pivot_index": position, "pivots": pivots}
            negative += hi < 0
        return {"status": "CERTIFIED", "negative": negative, "pivots": pivots}


class BoundedJournal:
    """Apply preflight headroom and post-write exact size checks to each event."""

    def __init__(self, path: Path, cap: int):
        self.path = path
        self.cap = cap
        self.journal = common.Journal(path)
        self.configuration_start_bytes = None
        self.basis_phase = True

    @property
    def size(self) -> int:
        return self.path.stat().st_size if self.path.exists() else 0

    def emit(self, kind: str, **payload):
        # Hash/sequence envelopes fit well inside this fixed 2048-byte reserve.
        estimated = len(common.canonical_bytes({"kind": kind, **payload})) + 2048
        limit = 16 * MIB if self.basis_phase else self.cap - 1 * MIB
        require(self.size + estimated <= limit, "EVENT_EXCEEDS_RESERVED_HEADROOM")
        if self.configuration_start_bytes is not None:
            require(self.size - self.configuration_start_bytes + estimated <= 4 * MIB,
                    "CONFIGURATION_EXCEEDS_RESERVED_HEADROOM")
        result = self.journal.emit(kind, **payload)
        require(self.size <= limit, "RAW_LOG_BYTE_CAP")
        if self.configuration_start_bytes is not None:
            require(self.size - self.configuration_start_bytes <= 4 * MIB,
                    "CONFIGURATION_BYTE_CAP")
        return result

    def error(self, error: Exception) -> None:
        # Preserve the validated prefix even when the active configuration has
        # exhausted its reservation.  The global error reserve is separate.
        self.configuration_start_bytes = None
        self.basis_phase = False
        message = str(error) if isinstance(error, WorkerError) else "UNEXPECTED_WORKER_EXCEPTION"
        self.emit("RUN_ERROR", error_type=type(error).__name__, message=message)


def inject_partial_then_block(output: Path, journal: BoundedJournal) -> None:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    with journal.path.open("ab", buffering=0) as stream:
        stream.write(b'{"kind":"SYNTHETIC_INTERRUPTED_FRAGMENT"')
        os.fsync(stream.fileno())
    marker = output / "FAULT_READY"
    with marker.open("xb", buffering=0) as stream:
        stream.write(b"partial event durable; waiting for supervisor\n")
        os.fsync(stream.fileno())
    descriptor = os.open(output, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    while True:
        signal.pause()


def load_sealed_basis_bytes(path: Path, basis_hashes: dict[str, str],
                           dimension: int) -> dict[str, bytes]:
    """Read the completed basis artifact once, then deserialize afresh per arm."""
    serialized = {}
    sealed = False
    with path.open("rb") as stream:
        for line in stream:
            require(line.endswith(b"\n"), "INCOMPLETE_BASIS_ARTIFACT")
            record = json.loads(line)
            if record["kind"] == "EIGEN_FINISHED":
                sid = record["specimen_id"]
                require(sid in basis_hashes and sid not in serialized,
                        "DURABLE_BASIS_MEMBERSHIP")
                check_basis(record["basis"], dimension)
                require(common.digest(record["basis"]) == basis_hashes[sid] ==
                        record["basis_sha256"], "DURABLE_BASIS_HASH_MISMATCH")
                serialized[sid] = common.canonical_bytes(record["basis"])
            elif record["kind"] == "BASIS_SEALED":
                require(record["basis_hashes"] == basis_hashes,
                        "DURABLE_BASIS_SEAL_MISMATCH")
                sealed = True
    require(sealed and set(serialized) == set(basis_hashes), "DURABLE_BASIS_INCOMPLETE")
    return serialized


def run(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    require(output.is_dir() and not any(output.iterdir()),
            "OUTPUT_MUST_BE_EXISTING_EMPTY_DIRECTORY")
    require(re.fullmatch(r"[0-9a-f]{40}", args.implementation_commit) is not None,
            "INVALID_IMPLEMENTATION_COMMIT")
    require(args.evaluator == "synthetic" or args.fault == "none",
            "FAULT_INJECTION_REQUIRES_SYNTHETIC_MODE")
    require(args.evaluator == "synthetic" or args.synthetic_profile == "default",
            "SYNTHETIC_PROFILE_REQUIRES_SYNTHETIC_MODE")
    require(args.evaluator != "physical" or args.wheel is not None,
            "PHYSICAL_EVALUATOR_REQUIRES_WHEEL")
    bindings = common.verify_implementation_files()
    spec, inputs = common.load_contract()
    limits = spec["limits"]
    resource.setrlimit(resource.RLIMIT_AS,
                       (limits["address_space_bytes"], limits["address_space_bytes"]))
    for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                     "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
        os.environ[variable] = "1"
    if args.evaluator == "synthetic":
        engine = SyntheticEngine(spec, args.synthetic_profile)
    else:
        from engine import PhysicalEngine
        engine = PhysicalEngine(args.wheel)
    journal = BoundedJournal(output / "EVENTS.ndjson", limits["raw_evidence_bytes_max"])
    try:
        journal.emit(
            "HEADER", approved_protocol_commit=common.APPROVED_PROTOCOL_COMMIT,
            implementation_commit=args.implementation_commit, source_bindings=bindings,
            runtime_provenance=engine.runtime_provenance,
            runtime_provenance_digest=common.digest(engine.runtime_provenance),
            test_mode=args.evaluator == "synthetic", evaluator=args.evaluator,
            fault=args.fault,
            synthetic_profile=args.synthetic_profile if args.evaluator == "synthetic" else None,
        )
        by_id = {specimen["id"]: specimen for specimen in inputs["specimens"]}
        specimens = [by_id[sid] for sid in spec["specimen_order"]]
        basis_hashes = {}
        eigen_starts = 0
        for specimen in specimens:
            require(eigen_starts < limits["eigensolver_calls_max"], "EIGENSOLVER_CALL_CAP")
            journal.emit("EIGEN_STARTED", specimen_id=specimen["id"])
            eigen_starts += 1
            basis = engine.make_basis(specimen)
            check_basis(basis, spec["dimension"])
            basis_sha = common.digest(basis)
            journal.emit("EIGEN_FINISHED", specimen_id=specimen["id"],
                         basis=basis, basis_sha256=basis_sha)
            basis_hashes[specimen["id"]] = basis_sha
        journal.emit("BASIS_SEALED", basis_hashes=basis_hashes)
        journal.basis_phase = False
        # Reload the retained artifact after the seal, not the engine's arrays.
        # Fresh JSON objects are constructed for both stages of every arm.
        serialized_bases = load_sealed_basis_bytes(
            journal.path, basis_hashes, spec["dimension"])
        del basis
        counts = {"primary": 0, "repeat": 0}
        configs = 0
        original_hashes = {}
        for arm in spec["arms_in_order"]:
            for specimen in specimens:
                sid = specimen["id"]
                has_room = (
                    configs < limits["configurations"] and
                    counts["primary"] + 4 <= limits["primary_endpoint_factorizations_max"] and
                    counts["repeat"] + 4 <= limits["verification_endpoint_factorizations_max"] and
                    sum(counts.values()) + 8 <= limits["all_endpoint_factorizations_max"] and
                    journal.size + 4 * MIB + 16 * MIB <= limits["raw_evidence_bytes_max"]
                )
                if not has_room:
                    journal.emit("RUN_FINISHED", reason="RESOURCE_CAP")
                    return 0
                journal.configuration_start_bytes = journal.size
                journal.emit("CONFIG_STARTED", arm_id=arm["id"], specimen_id=sid,
                             binding=common.config_binding(specimen, arm, basis_hashes[sid]))
                results = {}
                primary_evidence = None
                primary_gram_ok = None
                for stage in ("primary", "repeat"):
                    prepared = engine.prepare(specimen, arm, json.loads(serialized_bases[sid]))
                    evidence = check_prepared(prepared, arm, basis_hashes[sid], spec["dimension"])
                    journal.emit("GRAM_CHECK", arm_id=arm["id"], specimen_id=sid,
                                 stage=stage, evidence=evidence)
                    if stage == "primary":
                        primary_evidence = copy.deepcopy(evidence)
                        primary_gram_ok = prepared["gram_certified"]
                        if arm["id"] == "original_128":
                            original_hashes[sid] = {
                                "gram": evidence["unpermuted_gram_sha256"],
                                "K": evidence["unpermuted_K_sha256"],
                            }
                    else:
                        require(evidence == primary_evidence, "GRAM_OR_MATRIX_REPEAT_MISMATCH")
                    if arm["id"] == "original_reverse_128":
                        expected = original_hashes[sid]
                        require(evidence["unpermuted_gram_sha256"] == expected["gram"] and
                                evidence["unpermuted_K_sha256"] == expected["K"],
                                "REVERSE_UNPERMUTED_BASELINE_MISMATCH")
                    if not primary_gram_ok:
                        # Both Gram calculations must finish and compare before
                        # any skipped slots are claimed.  No LDL call is made.
                        continue
                    stage_results = []
                    for index, endpoint in enumerate(spec["endpoint_order"]):
                        stage_cap = (limits["primary_endpoint_factorizations_max"] if stage == "primary"
                                     else limits["verification_endpoint_factorizations_max"])
                        require(counts[stage] < stage_cap and
                                sum(counts.values()) < limits["all_endpoint_factorizations_max"],
                                "ENDPOINT_FACTORIZATION_CAP")
                        start = journal.emit("CALL_STARTED", arm_id=arm["id"], specimen_id=sid,
                                             stage=stage, endpoint=endpoint)
                        counts[stage] += 1
                        factor = engine.factor(prepared, index)
                        check_factor(factor, spec["dimension"])
                        journal.emit("CALL_FINISHED", arm_id=arm["id"], specimen_id=sid,
                                     stage=stage, endpoint=endpoint,
                                     start_sequence=start["sequence"], evidence=factor)
                        stage_results.append(copy.deepcopy(factor))
                        if stage == "repeat":
                            require(factor == results["primary"][index], "ENDPOINT_REPEAT_MISMATCH")
                    results[stage] = stage_results
                    del prepared
                if not primary_gram_ok:
                    for stage in ("primary", "repeat"):
                        for endpoint in spec["endpoint_order"]:
                            journal.emit("CALL_SKIPPED", arm_id=arm["id"], specimen_id=sid,
                                         stage=stage, endpoint=endpoint, reason="GRAM_UNCERTIFIED")
                journal.emit("CONFIG_FINISHED", arm_id=arm["id"], specimen_id=sid)
                configs += 1
                journal.configuration_start_bytes = None
                # The mixed fixture retains both a known baseline divergence
                # and an accepted-control mismatch before the real SIGKILL.
                fault_after = 7 if args.synthetic_profile == "mixed" else 1
                if args.fault == "partial_then_block" and configs == fault_after:
                    inject_partial_then_block(output, journal)
        journal.emit("RUN_FINISHED", reason="COMPLETE")
        return 0
    except Exception as error:
        try:
            journal.error(error)
        except Exception:
            # Do not replace, truncate, or repair complete durable records.
            # The supervisor receipt marks the failed process; offline replay
            # retains every valid prefix finding still supported by the log.
            pass
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--implementation-commit", required=True)
    parser.add_argument("--evaluator", required=True, choices=("physical", "synthetic"))
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--fault", choices=("none", "partial_then_block"), default="none")
    parser.add_argument("--synthetic-profile", choices=PROFILES, default="default")
    args = parser.parse_args()
    try:
        return run(args)
    except Exception as error:
        # Early binding/provenance errors may precede a trusted HEADER.
        print(str(error) if isinstance(error, WorkerError) else "WORKER_PREFLIGHT_ERROR",
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
