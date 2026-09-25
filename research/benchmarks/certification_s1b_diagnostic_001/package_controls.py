"""Synthetic byte-package controls; no numerical or model imports."""

import hashlib
import io
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

import package_io as package


def json_bytes(value):
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False).encode("ascii") + b"\n"


class PackageControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="diagnostic-package-controls-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def make_raw(self, raw=b'{"synthetic":true}\n'):
        directory = self.root / "raw"
        directory.mkdir()
        metadata, _ = package.package_plan(raw)
        (directory / "EVENTS.ndjson").write_bytes(raw)
        (directory / "RESULTS.json").write_bytes(json_bytes({"event_package": metadata, "synthetic_only": True}))
        (directory / "SUPERVISOR_RECEIPT.json").write_bytes(json_bytes({"synthetic_only": True}))
        package.write_manifest(directory)
        return directory

    def rebind_host_manifest(self, hosted):
        entries = []
        for path in sorted(hosted.iterdir()):
            if path.name == "MANIFEST.json":
                continue
            data = path.read_bytes()
            entries.append({"path": path.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        (hosted / "MANIFEST.json").write_bytes(json_bytes({"schema_version": 1, "entries": entries}))

    def test_round_trip_preserves_every_raw_byte(self):
        rawdir = self.make_raw()
        hosted = package.write_hosted(rawdir, self.root / "hosted")
        rebuilt = package.materialize(hosted, self.root / "rebuilt")
        self.assertEqual({p.name for p in rebuilt.iterdir()}, set(package.RAW_NAMES) | {"MANIFEST.json"})
        for path in rawdir.iterdir():
            self.assertEqual(path.read_bytes(), (rebuilt / path.name).read_bytes())

    def test_plan_is_deterministic_and_has_zero_mtime(self):
        first = package.package_plan(b"synthetic\n" * 100, part_bytes=10)
        second = package.package_plan(b"synthetic\n" * 100, part_bytes=10)
        self.assertEqual(first, second)
        compressed = b"".join(first[1].values())
        self.assertEqual(compressed[:10], b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff")
        self.assertEqual(list(first[1]), [package.PART_PREFIX + f"{i:03d}" for i in range(len(first[1]))])

    def test_multiple_production_parts_round_trip(self):
        raw = random.Random(7181).randbytes(1100000)
        rawdir = self.make_raw(raw)
        hosted = package.write_hosted(rawdir, self.root / "hosted")
        results = json.loads((hosted / "RESULTS.json").read_bytes())
        entries = results["event_package"]["parts"]
        self.assertEqual(len(entries), 3)
        self.assertEqual([entry["bytes"] for entry in entries[:-1]], [500000, 500000])
        rebuilt = package.materialize(hosted, self.root / "rebuilt")
        self.assertEqual((rebuilt / "EVENTS.ndjson").read_bytes(), raw)

    def test_raw_extra_file_is_rejected(self):
        rawdir = self.make_raw()
        (rawdir / "stale.txt").write_bytes(b"stale")
        with self.assertRaisesRegex(ValueError, "RAW_DIRECTORY_MEMBERSHIP"):
            package.write_hosted(rawdir, self.root / "hosted")

    def test_hosted_extra_file_is_rejected(self):
        hosted = package.write_hosted(self.make_raw(), self.root / "hosted")
        (hosted / "stale.txt").write_bytes(b"stale")
        with self.assertRaisesRegex(ValueError, "HOSTED_DIRECTORY_MEMBERSHIP"):
            package.materialize(hosted, self.root / "rebuilt")

    def test_part_mutation_is_rejected(self):
        hosted = package.write_hosted(self.make_raw(), self.root / "hosted")
        path = hosted / (package.PART_PREFIX + "000")
        data = path.read_bytes()
        path.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
        with self.assertRaisesRegex(ValueError, "COMPRESSED_PART_BINDING_MISMATCH"):
            package.materialize(hosted, self.root / "rebuilt")

    def test_noncontiguous_and_traversal_part_names_are_rejected(self):
        hosted = package.write_hosted(self.make_raw(), self.root / "hosted")
        path = hosted / "RESULTS.json"
        results = json.loads(path.read_bytes())
        for name in (package.PART_PREFIX + "001", "../outside"):
            with self.subTest(name=name):
                results["event_package"]["parts"][0]["path"] = name
                path.write_bytes(json_bytes(results))
                with self.assertRaisesRegex(ValueError, "EVENT_PACKAGE_PART_CONTIGUITY_OR_SIZE"):
                    package.materialize(hosted, self.root / "rebuilt")

    def test_stale_manifest_is_rejected(self):
        hosted = package.write_hosted(self.make_raw(), self.root / "hosted")
        (hosted / "SUPERVISOR_RECEIPT.json").write_bytes(b'{"changed":true}\n')
        with self.assertRaisesRegex(ValueError, "MANIFEST_BINDING_OR_FORMAT_MISMATCH"):
            package.materialize(hosted, self.root / "rebuilt")

    def test_symlink_member_and_directory_are_rejected(self):
        rawdir = self.make_raw()
        hosted = package.write_hosted(rawdir, self.root / "hosted")
        link = self.root / "linked_host"
        link.symlink_to(hosted, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "PACKAGE_DIRECTORY_REQUIRED"):
            package.materialize(link, self.root / "rebuilt")
        (hosted / "extra").symlink_to(rawdir / "EVENTS.ndjson")
        with self.assertRaisesRegex(ValueError, "PACKAGE_SYMLINK_OR_NONFILE"):
            package.materialize(hosted, self.root / "rebuilt")

    def test_existing_destination_is_not_overwritten(self):
        rawdir = self.make_raw()
        destination = self.root / "hosted"
        destination.mkdir()
        with self.assertRaises(FileExistsError):
            package.write_hosted(rawdir, destination)

    def test_raw_metadata_mismatch_is_rejected_after_valid_manifest(self):
        hosted = package.write_hosted(self.make_raw(), self.root / "hosted")
        path = hosted / "RESULTS.json"
        results = json.loads(path.read_bytes())
        results["event_package"]["raw_sha256"] = "0" * 64
        path.write_bytes(json_bytes(results))
        self.rebind_host_manifest(hosted)
        with self.assertRaisesRegex(ValueError, "RAW_LOG_BINDING_MISMATCH"):
            package.materialize(hosted, self.root / "rebuilt")

    def test_decompression_cap_is_enforced(self):
        hosted = package.write_hosted(self.make_raw(b"x" * 1024), self.root / "hosted")
        path = hosted / "RESULTS.json"
        results = json.loads(path.read_bytes())
        results["event_package"]["raw_bytes"] = 32
        results["event_package"]["raw_sha256"] = hashlib.sha256(b"x" * 32).hexdigest()
        path.write_bytes(json_bytes(results))
        self.rebind_host_manifest(hosted)
        with patch.object(package, "RAW_BYTES_MAX", 32):
            with self.assertRaisesRegex(ValueError, "RAW_LOG_TOO_LARGE"):
                package.materialize(hosted, self.root / "rebuilt")

    def test_duplicate_json_metadata_is_rejected(self):
        hosted = package.write_hosted(self.make_raw(), self.root / "hosted")
        (hosted / "RESULTS.json").write_bytes(b'{"event_package":{},"event_package":{}}\n')
        with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"):
            package.materialize(hosted, self.root / "rebuilt")

    def test_write_manifest_is_repeatable(self):
        rawdir = self.make_raw()
        before = (rawdir / "MANIFEST.json").read_bytes()
        package.write_manifest(rawdir)
        self.assertEqual((rawdir / "MANIFEST.json").read_bytes(), before)

    def test_check_only_compares_without_writing(self):
        rawdir = self.make_raw()
        before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in rawdir.iterdir()}
        package.write_manifest(rawdir, check_only=True)
        self.assertEqual({p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in rawdir.iterdir()}, before)
        (rawdir / "RESULTS.json").write_bytes(b'{"changed":true}\n')
        manifest_before = (rawdir / "MANIFEST.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "MANIFEST_BINDING_OR_FORMAT_MISMATCH"):
            package.write_manifest(rawdir, check_only=True)
        self.assertEqual((rawdir / "MANIFEST.json").read_bytes(), manifest_before)


def run_controls():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PackageControls)
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=2).run(suite)
    return {
        "control_family": "lossless_package_synthetic_only",
        "tests_run": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "status": "PASS" if result.wasSuccessful() else "FAIL",
        "failures": [{"test": test.id(), "traceback": detail} for test, detail in result.failures + result.errors],
        "numerical_calls": 0,
    }


if __name__ == "__main__":
    report = run_controls()
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
