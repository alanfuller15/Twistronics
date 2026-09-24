import hashlib
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from twistronics_acceptance_loop.orchestrator import (  # noqa: E402
    GateError,
    create_state,
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
        (self.sources / "expectations.json").write_text(
            '{"expected": true}\n', encoding="utf-8"
        )
        self.state = create_state(
            self.sources,
            ["consumer.py", "expectations.json"],
            source_label="candidate-1",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def review(self, reviewer, exchange, verdict="ACCEPT", digest=None, source_id=None):
        return {
            "schema_version": 1,
            "source_id": source_id or f"{reviewer.lower()}-{exchange}",
            "reviewer": reviewer,
            "exchange": exchange,
            "reviewed_binding_digest": digest or self.state["binding_digest"],
            "verdict": verdict,
            "claim_scope": "RETAINED_EVIDENCE_ONLY",
            "evidence_refs": ["retained.log"],
            "limitations": ["No physical certification."],
            "next_actions": ["Continue only if this binding remains exact."],
        }

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
        result = evaluate_state(self.state, self.sources)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(result["notification"]["alan_notification_required"])
        self.assertIn("hash mismatch", result["gate"]["issues"][0])

    def test_missing_source_blocks(self):
        (self.sources / "consumer.py").unlink()
        issues = verify_source_bindings(self.sources, self.state["source_bindings"])
        self.assertTrue(any("missing" in issue for issue in issues))

    def test_undeclared_source_blocks(self):
        (self.sources / "late_source.py").write_text("VALUE = 3\n", encoding="utf-8")
        result = evaluate_state(self.state, self.sources)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(
            any("undeclared source input" in issue for issue in result["gate"]["issues"])
        )

    def test_stale_review_digest_is_rejected(self):
        message = self.review("ASTRA", 1, digest="0" * 64)
        with self.assertRaisesRegex(GateError, "stale or foreign"):
            ingest_review(self.state, message, self.sources)

    def test_review_requires_evidence_and_limitations(self):
        message = self.review("ASTRA", 1)
        message["evidence_refs"] = []
        with self.assertRaisesRegex(GateError, "evidence_refs"):
            ingest_review(self.state, message, self.sources)
        message = self.review("ASTRA", 1)
        message["limitations"] = []
        with self.assertRaisesRegex(GateError, "limitations"):
            ingest_review(self.state, message, self.sources)

    def test_forged_reviews_in_loaded_state_are_rejected(self):
        forged = json.loads(json.dumps(self.state))
        forged["reviews"] = [self.review("ASTRA", 1, digest="0" * 64)]
        forged["exchange_count"] = 1
        with self.assertRaisesRegex(GateError, "stale or foreign"):
            evaluate_state(forged, self.sources)

    def test_each_reviewer_may_contribute_only_once(self):
        first = ingest_review(self.state, self.review("ASTRA", 1), self.sources)
        with self.assertRaisesRegex(GateError, "only once"):
            ingest_review(first, self.review("ASTRA", 2), self.sources)

    def test_two_accepts_produce_accepted_terminal_notification(self):
        first = ingest_review(self.state, self.review("ASTRA", 1), self.sources)
        self.assertEqual(first["status"], "IN_REVIEW")
        self.assertFalse(first["notification"]["alan_notification_required"])
        second = ingest_review(first, self.review("CLAUDE", 2), self.sources)
        self.assertEqual(second["status"], "ACCEPTED")
        self.assertTrue(second["notification"]["alan_notification_required"])
        with self.assertRaisesRegex(GateError, "limit reached"):
            ingest_review(second, self.review("ASTRA", 1, source_id="third"), self.sources)

    def test_request_changes_blocks_and_material_finding_is_distinct(self):
        blocked = ingest_review(
            self.state, self.review("ASTRA", 1, verdict="REQUEST_CHANGES"), self.sources
        )
        self.assertEqual(blocked["status"], "BLOCKED")
        self.assertTrue(blocked["notification"]["alan_notification_required"])
        finding = ingest_review(
            self.state,
            self.review("ASTRA", 1, verdict="MATERIAL_FINDING"),
            self.sources,
        )
        self.assertEqual(finding["status"], "MATERIAL_FINDING")
        self.assertTrue(finding["notification"]["alan_notification_required"])

    def test_package_manifest_excludes_itself_and_digest_is_detached(self):
        evidence = self.root / "evidence"
        evidence.mkdir()
        (evidence / "record.json").write_text('{"ok": true}\n', encoding="utf-8")
        (evidence / "MANIFEST.json").write_text("stale\n", encoding="utf-8")
        (evidence / "PACKAGE.sha256").write_text("stale\n", encoding="utf-8")
        output = self.root / "out" / "packet.zip"
        result = package_evidence(evidence, output)
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
        evidence = self.root / "evidence"
        evidence.mkdir()
        (evidence / "a.txt").write_text("alpha\n", encoding="utf-8")
        first = self.root / "one.zip"
        second = self.root / "two.zip"
        package_evidence(evidence, first)
        package_evidence(evidence, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_package_rejects_symlinks(self):
        evidence = self.root / "evidence"
        evidence.mkdir()
        target = evidence / "record.txt"
        target.write_text("record\n", encoding="utf-8")
        os.symlink(target, evidence / "alias.txt")
        with self.assertRaisesRegex(GateError, "symlink"):
            package_evidence(evidence, self.root / "packet.zip")

    def test_package_output_must_be_outside_evidence(self):
        evidence = self.root / "evidence"
        evidence.mkdir()
        (evidence / "record.txt").write_text("record\n", encoding="utf-8")
        with self.assertRaisesRegex(GateError, "outside"):
            package_evidence(evidence, evidence / "packet.zip")


if __name__ == "__main__":
    unittest.main()
