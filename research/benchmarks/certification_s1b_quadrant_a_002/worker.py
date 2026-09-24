#!/usr/bin/env python3
"""Single-process packet-002 worker; never spawns children or creates a session."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import resource
import signal
import sys
import time
from pathlib import Path

import common


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class PhysicalEvaluator:
    def __init__(self, wheel: Path, spec: dict):
        method_path = common.ROOT / "research/benchmarks/certification_s1b_method_004/check.py"
        base_path = common.ROOT / "research/benchmarks/certification_s1b_001/check.py"
        case_path = common.ROOT / "docs/certification-readiness/CASE.json"
        lock_path = common.ROOT / "research/benchmarks/certification_s1a_hardening_001/WHEEL_LOCK.json"
        self.method = load_module(method_path, "packet002_method004")
        self.base = load_module(base_path, "packet002_base")
        self.assembly = self.base.load_parent()
        case = json.loads(case_path.read_text())
        lock = json.loads(lock_path.read_text())
        self.runtime_provenance = self.base.runtime_provenance(wheel.resolve(), lock)
        self.assembly.validate_case(case)
        self.cutoff = case["cutoffs"]["a"]
        self.coefficients, _ = self.assembly.assemble_coefficients(
            self.cutoff["ordered_indices"], case)
        from flint import ctx
        ctx.prec = spec["algorithm"]["precision_bits"]
        ctx.threads = 1

    def __call__(self, cell: tuple[int, int, int], spec: dict) -> dict:
        evidence = self.method.probe_cell(
            self.base, self.assembly, self.coefficients, self.cutoff,
            {
                "precision_bits": spec["algorithm"]["precision_bits"],
                "recomputation_decimal_digits": spec["algorithm"]["recomputation_decimal_digits"],
            },
            list(cell),
        )
        return {
            "outcome": evidence["status"],
            "primary_factorizations": 4,
            "recomputation_factorizations": 4 if evidence["recomputation"] is not None else 0,
            "full_interval_evidence": evidence,
        }


class SyntheticEvaluator:
    runtime_provenance = {"synthetic": True}

    def __call__(self, cell: tuple[int, int, int], spec: dict) -> dict:
        return {
            "outcome": "INCONCLUSIVE",
            "primary_factorizations": 4,
            "recomputation_factorizations": 0,
            "full_interval_evidence": {"synthetic": True, "cell": common.cell_ref(cell)},
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--implementation-commit", required=True)
    parser.add_argument("--runtime-provenance-digest", required=True)
    parser.add_argument("--evaluator", choices=("physical", "synthetic"), required=True)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--fault", choices=("none", "partial_then_block"), default="none")
    args = parser.parse_args()

    output = args.output.resolve()
    if not output.is_dir() or any(output.iterdir()):
        raise RuntimeError("OUTPUT_MUST_BE_EXISTING_EMPTY_DIRECTORY")
    common.verify_implementation_files()
    spec, _, _ = common.load_frozen_state()
    resource.setrlimit(resource.RLIMIT_AS,
                       (spec["limits"]["address_space_bytes"], spec["limits"]["address_space_bytes"]))
    if args.evaluator == "physical" and args.wheel is None:
        raise RuntimeError("PHYSICAL_EVALUATOR_REQUIRES_WHEEL")
    evaluator = SyntheticEvaluator() if args.evaluator == "synthetic" else PhysicalEvaluator(args.wheel, spec)
    if args.evaluator == "physical":
        observed = common.sha256_bytes(common.canonical_object_bytes(
            evaluator.runtime_provenance))
        if observed != args.runtime_provenance_digest:
            raise RuntimeError("RUNTIME_PROVENANCE_DIGEST_MISMATCH")

    header_unsigned = {
        "kind": "header",
        "sequence": -1,
        "previous_record_sha256": None,
        "approved_protocol_commit": common.APPROVED_PROTOCOL_COMMIT,
        "predecessor_partition_sha256": common.PREDECESSOR_PARTITION_SHA256,
        "predecessor_results_sha256": common.PREDECESSOR_RESULTS_SHA256,
        "implementation_commit": args.implementation_commit,
        "runtime_provenance_digest": args.runtime_provenance_digest,
        "evaluator": args.evaluator,
        "test_mode": args.evaluator == "synthetic",
        "hash_encoding": "record_sha256=sha256(canonical object without record_sha256); previous_record_sha256=sha256(exact prior canonical line bytes excluding newline)",
    }
    _, header_line, previous_line_sha = common.hashed_record(header_unsigned)
    log_path = output / "ATTEMPTS.ndjson"
    common.append_durable(log_path, header_line)

    state = common.initial_replay_state()
    max_depth = spec["algorithm"]["max_depth"]
    while state["frontier"]:
        # Empty queue is tested above, before admission, per implementation note I3.
        if not common.admission_has_room(state, spec):
            return 0
        cell = common.select_current_minimum(state["frontier"])
        evaluated = evaluator(cell, spec)
        unsigned = {
            "kind": "attempt",
            "sequence": state["attempts"],
            "previous_record_sha256": previous_line_sha,
            "cell": common.cell_ref(cell),
            "priority_key": common.priority_record(cell),
            **evaluated,
        }
        record, line, line_sha = common.hashed_record(unsigned)
        if args.fault == "partial_then_block" and state["attempts"] == 0:
            # Test-only fault injection: make a real non-newline fragment, fsync it,
            # announce readiness, then wait for the external supervisor's SIGKILL.
            fragment = line[:max(1, len(line) // 2)]
            with log_path.open("ab", buffering=0) as stream:
                stream.write(fragment)
                stream.flush()
                os.fsync(stream.fileno())
            common.fsync_directory(output)
            (output / "FAULT_READY").write_text("partial attempt fsynced\n")
            common.fsync_directory(output)
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            while True:
                time.sleep(60)
        common.append_durable(log_path, line)
        common.apply_attempt(state, record, max_depth)
        previous_line_sha = line_sha
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
