import hashlib
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import twistronics_acceptance_loop.orchestrator as orchestrator_module  # noqa: E402

from twistronics_acceptance_loop.orchestrator import (  # noqa: E402
    CONTROL_IDS,
    GateError,
    build_evidence_bindings,
    create_state,
    descriptor_digest,
    evaluate_state,
    ingest_review,
    package_evidence,
    verify_source_bindings,
)


class AcceptanceLoopTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.sources = self.root / "sources"
        self.sources.mkdir()
        (self.sources / "consumer.py").write_text("VALUE = 1\n", encoding="utf-8")
        consumer_sha = hashlib.sha256(b"VALUE = 1\n").hexdigest()
        (self.sources / "expectations.json").write_text(
            '{"expected": true}\n', encoding="utf-8"
        )
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        (self.evidence / "gate.log").write_text("retained evidence\n", encoding="utf-8")
        evidence_sha = hashlib.sha256(b"retained evidence\n").hexdigest()
        def write_receipt(kind, record_id, result="PASS"):
            receipt_path = self.evidence / "receipts" / kind / f"{record_id}.json"
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            reviewer_owned = kind == "gate" and int(record_id[1:]) >= 11
            receipt = {
                "schema_version": 1,
                "record_type": f"{kind}/{record_id}",
                "record_id": record_id,
                "checker": {
                    "id": f"{kind}/{record_id}",
                    "owner": "REVIEWER" if reviewer_owned else "HARNESS",
                    "path": "consumer.py",
                    "sha256": consumer_sha,
                },
                "inputs": [{"path": "consumer.py", "sha256": consumer_sha}],
                "argv": ["verify", record_id],
                "cwd": "/isolated",
                "runtime": "python-3.12",
                "started_at": "2026-09-24T00:00:00Z",
                "finished_at": "2026-09-24T00:00:01Z",
                "exit_code": 0,
                "result": result,
                "outputs": [{"path": "gate.log", "sha256": evidence_sha}],
            }
            payload = json.dumps(receipt, sort_keys=True) + "\n"
            receipt_path.write_text(payload, encoding="utf-8")
            return {
                "path": receipt_path.relative_to(self.evidence).as_posix(),
                "sha256": hashlib.sha256(payload.encode()).hexdigest(),
            }
        self.gate_results = {
            f"G{index:02d}": {
                "status": "NOT_RUN" if index >= 16 else "PASS",
                "evidence_refs": [{"path": "gate.log", "sha256": evidence_sha}],
                "detail": "retained synthetic gate evidence",
                "receipt": write_receipt(
                    "gate",
                    f"G{index:02d}",
                    "NOT_RUN" if index >= 16 else "PASS",
                ),
            }
            for index in range(18)
        }
        self.negative_controls = {
            control_id: {
                "status": "PASS",
                "evidence_refs": [{"path": "gate.log", "sha256": evidence_sha}],
                "detail": "retained negative-control evidence",
                "receipt": write_receipt("negative_control", control_id),
            }
            for control_id in CONTROL_IDS
        }
        self.artifact_sha256 = "a" * 64
        self.reviewed_commit = "b" * 40
        self.state = create_state(
            self.sources,
            ["consumer.py", "expectations.json"],
            source_label="candidate-1",
            evidence_root=self.evidence,
            round_id="TWI-ACC-v079p-R01-aaaaaaaaaaaa",
            baseline_sha="c" * 40,
            reviewed_commit=self.reviewed_commit,
            artifact_sha256=self.artifact_sha256,
            gate_results=self.gate_results,
            negative_controls=self.negative_controls,
        )

    def tearDown(self):
        self.temporary.cleanup()

    def review(self, reviewer, exchange, status="PASS", digest=None, source_id=None):
        source_id = source_id or f"issuecomment-{exchange}"
        message = {
            "schema_version": 2,
            "protocol": "TWISTRONICS-ACCEPTANCE/1",
            "round_id": self.state["round_id"],
            "source_id": source_id,
            "in_reply_to": None if exchange == 1 else "issuecomment-1",
            "reviewer": reviewer,
            "responder_marker": f"[{reviewer}]" + (
                "[HANDOFF]" if reviewer == "ASTRA" else "[REVIEW]"
            ),
            "exchange": exchange,
            "reviewed_commit": self.reviewed_commit,
            "artifact_sha256": self.artifact_sha256,
            "reviewed_descriptor_digest": digest or self.state["descriptor_digest"],
            "status": status,
            "claim_scope": "RETAINED_EVIDENCE_ONLY",
            "evidence_refs": ["gate.log"],
            "blockers": [] if status == "PASS" else [{"id": "B1", "finding": "probe"}],
            "limitations": ["No physical certification."],
            "next_action": "Continue only if this descriptor remains exact.",
            "reply_required": exchange == 1,
        }
        envelope = json.dumps(
            message, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
        message["transport_receipt"] = {
            "event_type": "issue_comment",
            "source_id": source_id,
            "url": f"https://github.com/alanfuller15/Twistronics/pull/6#issuecomment-{exchange}",
            "created_at": "2026-09-24T00:00:00Z",
            "body_sha256": "1" * 64,
            "fetched_commit": self.reviewed_commit,
            "envelope_sha256": hashlib.sha256(envelope).hexdigest(),
            "connector_verified": True,
        }
        return message

    def test_create_state_hashes_actual_bytes(self):
        self.assertEqual(self.state["status"], "IN_REVIEW")
        self.assertTrue(self.state["gate"]["actual_bytes_verified"])
        expected = hashlib.sha256(b"VALUE = 1\n").hexdigest()
        binding = next(
            item for item in self.state["source_bindings"] if item["path"] == "consumer.py"
        )
        self.assertEqual(binding["sha256"], expected)
        self.assertFalse(self.state["notification"]["alan_notification_required"])

    def test_tampered_actual_bytes_block(self):
        (self.sources / "consumer.py").write_text("VALUE = 2\n", encoding="utf-8")
        result = evaluate_state(self.state, self.sources, self.evidence)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(result["notification"]["alan_notification_required"])
        self.assertIn("hash mismatch", result["gate"]["issues"][0])

    def test_missing_source_blocks(self):
        (self.sources / "consumer.py").unlink()
        issues = verify_source_bindings(self.sources, self.state["source_bindings"])
        self.assertTrue(any("missing" in issue for issue in issues))

    def test_undeclared_source_blocks(self):
        (self.sources / "late_source.py").write_text("VALUE = 3\n", encoding="utf-8")
        result = evaluate_state(self.state, self.sources, self.evidence)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(
            any("undeclared source input" in issue for issue in result["gate"]["issues"])
        )

    def test_stale_review_digest_is_rejected(self):
        message = self.review("ASTRA", 1, digest="0" * 64)
        with self.assertRaisesRegex(GateError, "stale or foreign"):
            ingest_review(self.state, message, self.sources, self.evidence)

    def test_review_requires_evidence_and_limitations(self):
        message = self.review("ASTRA", 1)
        message["evidence_refs"] = []
        with self.assertRaisesRegex(GateError, "evidence_refs"):
            ingest_review(self.state, message, self.sources, self.evidence)
        message = self.review("ASTRA", 1)
        message["limitations"] = []
        with self.assertRaisesRegex(GateError, "limitations"):
            ingest_review(self.state, message, self.sources, self.evidence)

    def test_forged_reviews_in_loaded_state_are_rejected(self):
        forged = json.loads(json.dumps(self.state))
        forged["reviews"] = [self.review("ASTRA", 1, digest="0" * 64)]
        forged["exchange_count"] = 1
        with self.assertRaisesRegex(GateError, "stale or foreign"):
            evaluate_state(forged, self.sources, self.evidence)

    def test_each_reviewer_may_contribute_only_once(self):
        first = ingest_review(self.state, self.review("ASTRA", 1), self.sources, self.evidence)
        with self.assertRaisesRegex(GateError, "Astra first"):
            ingest_review(first, self.review("ASTRA", 2), self.sources, self.evidence)

    def test_two_accepts_produce_prepackage_state(self):
        first = ingest_review(self.state, self.review("ASTRA", 1), self.sources, self.evidence)
        self.assertEqual(first["status"], "IN_REVIEW")
        self.assertFalse(first["notification"]["alan_notification_required"])
        second = ingest_review(first, self.review("CLAUDE", 2), self.sources, self.evidence)
        self.assertEqual(second["status"], "PREPACKAGE_ACCEPTED")
        self.assertFalse(second["notification"]["alan_notification_required"])
        with self.assertRaisesRegex(GateError, "limit reached"):
            ingest_review(second, self.review("ASTRA", 1, source_id="issuecomment-3"), self.sources, self.evidence)

    def test_request_changes_blocks_and_material_finding_is_distinct(self):
        first = ingest_review(
            self.state, self.review("ASTRA", 1), self.sources, self.evidence
        )
        blocked = ingest_review(
            first, self.review("CLAUDE", 2, status="BLOCKED"), self.sources, self.evidence
        )
        self.assertEqual(blocked["status"], "BLOCKED")
        self.assertTrue(blocked["notification"]["alan_notification_required"])
        first_for_finding = ingest_review(
            self.state, self.review("ASTRA", 1), self.sources, self.evidence
        )
        finding = ingest_review(
            first_for_finding,
            self.review("CLAUDE", 2, status="MATERIAL_FINDING"),
            self.sources,
            self.evidence,
        )
        self.assertEqual(finding["status"], "MATERIAL_FINDING")
        self.assertTrue(finding["notification"]["alan_notification_required"])

    def test_reviewer_order_is_fixed(self):
        with self.assertRaisesRegex(GateError, "Astra first"):
            ingest_review(
                self.state,
                self.review("CLAUDE", 1),
                self.sources,
                self.evidence,
            )

    def test_review_identity_and_evidence_are_bound(self):
        message = self.review("ASTRA", 1)
        message["reviewed_commit"] = "d" * 40
        with self.assertRaisesRegex(GateError, "commit is stale"):
            ingest_review(self.state, message, self.sources, self.evidence)
        message = self.review("ASTRA", 1)
        message["evidence_refs"] = ["missing.log"]
        with self.assertRaisesRegex(GateError, "unbound evidence"):
            ingest_review(self.state, message, self.sources, self.evidence)
        message = self.review("ASTRA", 1)
        message["unexpected"] = True
        with self.assertRaisesRegex(GateError, "undeclared fields"):
            ingest_review(self.state, message, self.sources, self.evidence)
        message = self.review("ASTRA", 1)
        message["transport_receipt"]["connector_verified"] = False
        with self.assertRaisesRegex(GateError, "not verified"):
            ingest_review(self.state, message, self.sources, self.evidence)

    def test_descriptor_replay_is_rejected(self):
        replayed = json.loads(json.dumps(self.state))
        replayed["source_label"] = "different-candidate"
        with self.assertRaisesRegex(GateError, "descriptor digest"):
            evaluate_state(replayed, self.sources, self.evidence)

    def test_terminal_state_rejects_further_review(self):
        first = ingest_review(
            self.state, self.review("ASTRA", 1), self.sources, self.evidence
        )
        blocked = ingest_review(
            first,
            self.review("CLAUDE", 2, status="BLOCKED"),
            self.sources,
            self.evidence,
        )
        with self.assertRaisesRegex(GateError, "terminal state"):
            ingest_review(
                blocked,
                self.review("ASTRA", 1, source_id="issuecomment-3"),
                self.sources,
                self.evidence,
            )

    def test_conditional_pass_is_blocked(self):
        first = ingest_review(
            self.state,
            self.review("ASTRA", 1),
            self.sources,
            self.evidence,
        )
        result = ingest_review(
            first,
            self.review("CLAUDE", 2, status="CONDITIONAL_PASS"),
            self.sources,
            self.evidence,
        )
        self.assertEqual(result["status"], "BLOCKED")

    def test_nonpassing_gate_blocks(self):
        state = json.loads(json.dumps(self.state))
        state["gate_results"]["G09"]["status"] = "NOT_RUN"
        state["descriptor_digest"] = descriptor_digest(state)
        result = evaluate_state(state, self.sources, self.evidence)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("gate did not pass: G09", result["gate"]["issues"])

    def test_nonpassing_or_missing_negative_control_blocks(self):
        state = json.loads(json.dumps(self.state))
        state["negative_controls"]["unsafe_zip_path"]["status"] = "FAIL"
        state["descriptor_digest"] = descriptor_digest(state)
        result = evaluate_state(state, self.sources, self.evidence)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn(
            "negative control did not pass: unsafe_zip_path",
            result["gate"]["issues"],
        )
        missing = json.loads(json.dumps(self.state))
        del missing["negative_controls"]["unsafe_zip_link"]
        with self.assertRaisesRegex(GateError, "exact required set"):
            evaluate_state(missing, self.sources, self.evidence)

    def test_typed_receipts_are_distinct_and_verified(self):
        state = json.loads(json.dumps(self.state))
        state["negative_controls"]["added_source"]["receipt"] = state[
            "negative_controls"
        ]["missing_source_identity"]["receipt"]
        state["descriptor_digest"] = descriptor_digest(state)
        result = evaluate_state(state, self.sources, self.evidence)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("receipt reused" in issue for issue in result["gate"]["issues"]))

    def test_failed_postpackage_check_leaves_no_final_artifacts(self):
        first = ingest_review(
            self.state, self.review("ASTRA", 1), self.sources, self.evidence
        )
        accepted = ingest_review(
            first, self.review("CLAUDE", 2), self.sources, self.evidence
        )
        state_path = self.root / "prepackage.json"
        state_path.write_text(json.dumps(accepted), encoding="utf-8")
        output = self.root / "final" / "packet.zip"
        original = orchestrator_module.package_evidence

        def package_then_mutate(*args, **kwargs):
            result = original(*args, **kwargs)
            (self.sources / "consumer.py").write_text("VALUE = 99\n", encoding="utf-8")
            return result

        with patch.object(
            orchestrator_module, "package_evidence", side_effect=package_then_mutate
        ), contextlib.redirect_stderr(io.StringIO()):
            rc = orchestrator_module.main(
                [
                    "package", "--state", str(state_path),
                    "--source-root", str(self.sources),
                    "--evidence-root", str(self.evidence),
                    "--output", str(output),
                ]
            )
        self.assertEqual(rc, 2)
        self.assertFalse(output.exists())
        self.assertFalse(output.with_name(output.name + ".sha256").exists())
        self.assertFalse(output.with_name(output.name + ".attestation.json").exists())

    def test_attestation_write_failure_leaves_no_bundle(self):
        first = ingest_review(
            self.state, self.review("ASTRA", 1), self.sources, self.evidence
        )
        accepted = ingest_review(
            first, self.review("CLAUDE", 2), self.sources, self.evidence
        )
        state_path = self.root / "prepackage-attestation.json"
        state_path.write_text(json.dumps(accepted), encoding="utf-8")
        output_dir = self.root / "accepted-bundle"
        with patch.object(
            orchestrator_module, "_write_json", side_effect=OSError("simulated")
        ), contextlib.redirect_stderr(io.StringIO()):
            rc = orchestrator_module.main(
                [
                    "package", "--state", str(state_path),
                    "--source-root", str(self.sources),
                    "--evidence-root", str(self.evidence),
                    "--output", str(output_dir),
                ]
            )
        self.assertEqual(rc, 2)
        self.assertFalse(output_dir.exists())

    def test_unrelated_evidence_cannot_be_packaged(self):
        unrelated = self.root / "unrelated"
        unrelated.mkdir()
        (unrelated / "claim.txt").write_text("unrelated\n", encoding="utf-8")
        with self.assertRaisesRegex(GateError, "accepted binding"):
            package_evidence(
                unrelated,
                self.root / "unrelated.zip",
                expected_bindings=self.state["evidence_bindings"],
            )

    def test_unsafe_portable_archive_name_is_rejected(self):
        evidence = self.root / "unsafe"
        evidence.mkdir()
        (evidence / "..\\escape.txt").write_text("unsafe\n", encoding="utf-8")
        with self.assertRaisesRegex(GateError, "unsafe archive path"):
            build_evidence_bindings(evidence)

    def test_package_manifest_excludes_itself_and_digest_is_detached(self):
        evidence = self.root / "package-evidence"
        evidence.mkdir()
        (evidence / "record.json").write_text('{"ok": true}\n', encoding="utf-8")
        (evidence / "MANIFEST.json").write_text("stale\n", encoding="utf-8")
        (evidence / "PACKAGE.sha256").write_text("stale\n", encoding="utf-8")
        output = self.root / "out" / "packet.zip"
        result = package_evidence(
            evidence, output, expected_bindings=build_evidence_bindings(evidence)
        )
        detached = Path(result["detached_digest"])
        self.assertTrue(detached.exists())
        self.assertNotEqual(output.parent, evidence)
        self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(), result["sha256"])
        self.assertEqual(detached.read_text().split()[0], result["sha256"])
        with zipfile.ZipFile(output) as archive:
            self.assertEqual(sorted(archive.namelist()), ["MANIFEST.json", "record.json"])
            manifest = json.loads(archive.read("MANIFEST.json"))
        listed = [item["path"] for item in manifest["files"]]
        self.assertEqual(listed, ["record.json"])
        self.assertNotIn("MANIFEST.json", listed)
        self.assertNotIn("PACKAGE.sha256", listed)

    def test_package_is_deterministic(self):
        evidence = self.root / "deterministic-evidence"
        evidence.mkdir()
        (evidence / "a.txt").write_text("alpha\n", encoding="utf-8")
        first = self.root / "one.zip"
        second = self.root / "two.zip"
        bindings = build_evidence_bindings(evidence)
        package_evidence(evidence, first, expected_bindings=bindings)
        package_evidence(evidence, second, expected_bindings=bindings)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_package_rejects_symlinks(self):
        evidence = self.root / "symlink-evidence"
        evidence.mkdir()
        target = evidence / "record.txt"
        target.write_text("record\n", encoding="utf-8")
        os.symlink(target, evidence / "alias.txt")
        with self.assertRaisesRegex(GateError, "symlink"):
            package_evidence(
                evidence,
                self.root / "packet.zip",
                expected_bindings=[{"path": "record.txt", "sha256": "0" * 64, "size": 0}],
            )

    def test_package_output_must_be_outside_evidence(self):
        evidence = self.root / "inside-output-evidence"
        evidence.mkdir()
        (evidence / "record.txt").write_text("record\n", encoding="utf-8")
        with self.assertRaisesRegex(GateError, "outside"):
            package_evidence(
                evidence,
                evidence / "packet.zip",
                expected_bindings=build_evidence_bindings(evidence),
            )


if __name__ == "__main__":
    unittest.main()
