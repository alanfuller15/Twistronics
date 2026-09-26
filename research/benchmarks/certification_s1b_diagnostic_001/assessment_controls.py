"""Synthetic truth controls for M1 assessment and validated-prefix retention.

Only standard-library JSON and in-memory synthetic outcomes are used.  No model
assembly, eigensolver, interval arithmetic or physical execution is performed.
"""

import io
import json
from pathlib import Path
import sys
import unittest

from assessments import EXPECTED, GRAM, NONPASS, OTHER, PASS, ZERO, assess


HERE = Path(__file__).resolve().parent
SPEC = json.loads((HERE / "SPEC.json").read_text())
INPUTS = json.loads((HERE / "INPUTS.json").read_text())
ENDPOINTS = SPEC["endpoint_order"]


def configuration(failures=None, completed=True, gram=True):
    failures = failures or {}
    result = {
        "outcomes": {
            stage: {endpoint: {"status": failures.get(endpoint, EXPECTED)} for endpoint in ENDPOINTS}
            for stage in ("primary", "repeat")
        },
        "completed": completed,
        "gram_positive": {"primary": gram, "repeat": gram},
    }
    return result


def faithful_configurations():
    result = {}
    for specimen in INPUTS["specimens"]:
        failed = [] if specimen["historical_signature"] == "accepted" else specimen["historical_signature"].split("+")
        for arm in SPEC["arms_in_order"]:
            result[(arm["id"], specimen["id"])] = configuration({e: ZERO for e in failed})
    return result


def baseline(result, specimen="upper_left"):
    return next(row for row in result["baseline_assessments"] if row["specimen_id"] == specimen)


def comparison(result, specimen="upper_left", arm="point_128"):
    return next(row for row in result["arm_comparisons"] if row["specimen_id"] == specimen and row["compared_arm_id"] == arm)


class AssessmentControls(unittest.TestCase):
    def test_unstarted_is_unknown_for_all_seven(self):
        result = assess(SPEC, INPUTS, {})
        self.assertEqual(len(result["baseline_assessments"]), 7)
        self.assertEqual(len(result["arm_comparisons"]), 49)
        self.assertIsNone(result["control_mismatch_detected"])
        self.assertIsNone(result["baseline_divergence_detected"])
        self.assertEqual(len(result["control_mismatch_unresolved_ids"]), 2)
        self.assertEqual(len(result["baseline_divergence_unresolved_ids"]), 5)
        self.assertTrue(all(row["assessment_state"] == "NOT_STARTED" for row in result["baseline_assessments"]))

    def test_all_faithful_baselines_and_complete_comparisons(self):
        result = assess(SPEC, INPUTS, faithful_configurations())
        self.assertIs(result["control_mismatch_detected"], False)
        self.assertIs(result["baseline_divergence_detected"], False)
        self.assertEqual(sum(row["failure_mechanism_comparison_eligible"] for row in result["arm_comparisons"]), 35)
        self.assertIs(baseline(result)["baseline_matches_historical_failed_endpoints"], True)

    def test_baseline_pass_is_divergence_not_arm_repair(self):
        configs = faithful_configurations()
        configs[("original_128", "upper_left")] = configuration()
        result = assess(SPEC, INPUTS, configs)
        row = baseline(result)
        self.assertIs(row["BASELINE_DIVERGENCE"], True)
        self.assertEqual(row["baseline_configuration_outcome"], PASS)
        self.assertIs(row["baseline_matches_historical_label"], False)
        self.assertEqual(row["baseline_failed_endpoints"], [])
        self.assertIs(result["baseline_divergence_detected"], True)
        self.assertIn("BASELINE_DIVERGENCE", comparison(result)["exclusion_reasons"])

    def test_changed_endpoint_set_is_excluded_even_with_matching_label(self):
        configs = faithful_configurations()
        configs[("original_128", "upper_left")] = configuration({"upper.right": ZERO})
        result = assess(SPEC, INPUTS, configs)
        row = baseline(result)
        self.assertIs(row["baseline_matches_historical_label"], True)
        self.assertIs(row["baseline_matches_historical_failed_endpoints"], False)
        self.assertIs(row["BASELINE_DIVERGENCE"], False)
        self.assertIn("HISTORICAL_FAILED_ENDPOINT_SET_MISMATCH", comparison(result)["exclusion_reasons"])

    def test_wrong_inertia_type_is_excluded_with_matching_endpoint_set(self):
        configs = faithful_configurations()
        configs[("original_128", "upper_left")] = configuration({"upper.left": OTHER})
        result = assess(SPEC, INPUTS, configs)
        row = baseline(result)
        self.assertIs(row["baseline_matches_historical_failed_endpoints"], True)
        self.assertEqual(row["baseline_failed_endpoint_outcomes"], [{"endpoint": "upper.left", "status": OTHER}])
        self.assertIn("HISTORICAL_FAILED_ENDPOINT_TYPE_MISMATCH", comparison(result)["exclusion_reasons"])

    def test_complete_gram_failure_records_all_skipped_types(self):
        configs = {("original_128", "upper_left"): configuration({e: GRAM for e in ENDPOINTS}, gram=False)}
        result = assess(SPEC, INPUTS, configs)
        row = baseline(result)
        self.assertEqual(row["baseline_configuration_outcome"], NONPASS)
        self.assertEqual(row["baseline_failed_endpoints"], ENDPOINTS)
        self.assertIs(row["BASELINE_DIVERGENCE"], False)
        self.assertIn("BASELINE_GRAM_UNCERTIFIED", row["exclusion_reasons"])

    def test_partial_paired_failure_decides_divergence_false(self):
        config = configuration({"upper.left": ZERO}, completed=False)
        config["outcomes"]["repeat"].pop("upper.right")
        result = assess(SPEC, INPUTS, {("original_128", "upper_left"): config})
        row = baseline(result)
        self.assertIs(row["BASELINE_DIVERGENCE"], False)
        self.assertIsNone(row["baseline_matches_historical_label"])
        self.assertIsNone(row["baseline_failed_endpoints"])
        self.assertEqual(row["assessment_state"], "INCOMPLETE")
        self.assertIn("upper.left", row["repeat_consistent_endpoints"])

    def test_primary_failure_alone_does_not_set_review_flag(self):
        config = configuration({"upper.left": ZERO}, completed=False)
        config["outcomes"]["repeat"] = {}
        row = baseline(assess(SPEC, INPUTS, {("original_128", "upper_left"): config}))
        self.assertIsNone(row["BASELINE_DIVERGENCE"])
        self.assertIsNone(row["baseline_matches_historical_failed_endpoints"])
        self.assertEqual(row["observed_endpoint_outcomes"]["primary"]["upper.left"]["status"], ZERO)

    def test_partial_paired_passes_remain_unknown(self):
        config = configuration(completed=False)
        config["outcomes"]["repeat"].pop("upper.right")
        row = baseline(assess(SPEC, INPUTS, {("original_128", "upper_left"): config}))
        self.assertIsNone(row["BASELINE_DIVERGENCE"])
        self.assertIsNone(row["baseline_configuration_outcome"])

    def test_control_partial_paired_failure_flags_immediately(self):
        config = configuration({"lower.left": ZERO}, completed=False)
        config["outcomes"]["repeat"] = {"lower.left": {"status": ZERO}}
        result = assess(SPEC, INPUTS, {("original_128", "accepted_upper"): config})
        self.assertIs(baseline(result, "accepted_upper")["control_mismatch"], True)
        self.assertIs(result["control_mismatch_detected"], True)
        self.assertEqual(result["control_mismatch_flagged_ids"], ["accepted_upper"])
        self.assertEqual(result["control_mismatch_unresolved_ids"], ["accepted_lower"])

    def test_gram_only_paired_failure_decides_control_mismatch(self):
        config = {"outcomes": {}, "completed": False, "gram_positive": {"primary": False, "repeat": False}}
        result = assess(SPEC, INPUTS, {("original_128", "accepted_upper"): config})
        row = baseline(result, "accepted_upper")
        self.assertIs(row["control_mismatch"], True)
        self.assertIsNone(row["baseline_failed_endpoints"])
        self.assertIsNone(row["baseline_matches_historical_label"])

    def test_gram_primary_only_does_not_decide_control(self):
        config = {"outcomes": {}, "completed": False, "gram_positive": {"primary": False}}
        row = baseline(assess(SPEC, INPUTS, {("original_128", "accepted_upper"): config}), "accepted_upper")
        self.assertIsNone(row["control_mismatch"])

    def test_accepted_control_false_only_after_completed_pass(self):
        configs = {("original_128", "accepted_upper"): configuration(completed=False)}
        self.assertIsNone(baseline(assess(SPEC, INPUTS, configs), "accepted_upper")["control_mismatch"])
        configs[("original_128", "accepted_upper")]["completed"] = True
        row = baseline(assess(SPEC, INPUTS, configs), "accepted_upper")
        self.assertIs(row["control_mismatch"], False)
        self.assertIsNone(row["baseline_matches_historical_failed_endpoints"])
        self.assertIsNone(row["BASELINE_DIVERGENCE"])

    def test_false_completion_marker_cannot_be_overridden_by_outcomes(self):
        config = configuration({"upper.left": ZERO}, completed=False)
        row = baseline(assess(SPEC, INPUTS, {("original_128", "upper_left"): config}))
        self.assertIsNone(row["baseline_configuration_outcome"])
        self.assertIs(row["BASELINE_DIVERGENCE"], False)

    def test_true_completion_marker_cannot_override_missing_endpoint(self):
        config = configuration()
        config["outcomes"]["repeat"].pop("upper.right")
        row = baseline(assess(SPEC, INPUTS, {("original_128", "upper_left"): config}))
        self.assertIsNone(row["baseline_configuration_outcome"])
        self.assertIsNone(row["BASELINE_DIVERGENCE"])

    def test_true_completion_marker_cannot_override_unknown_gram(self):
        config = configuration()
        config["gram_positive"].pop("repeat")
        row = baseline(assess(SPEC, INPUTS, {("original_128", "upper_left"): config}))
        self.assertIsNone(row["baseline_configuration_outcome"])
        self.assertIsNone(row["BASELINE_DIVERGENCE"])

    def test_mismatched_repeat_status_is_invalid(self):
        config = configuration({"upper.left": ZERO})
        config["outcomes"]["repeat"]["upper.left"] = {"status": EXPECTED}
        row = baseline(assess(SPEC, INPUTS, {("original_128", "upper_left"): config}))
        self.assertEqual(row["assessment_state"], "INVALID_EVIDENCE")
        self.assertIsNone(row["BASELINE_DIVERGENCE"])
        self.assertIsNone(row["baseline_matches_historical_label"])

    def test_inconsistent_gram_is_invalid(self):
        config = configuration()
        config["gram_positive"]["repeat"] = False
        row = baseline(assess(SPEC, INPUTS, {("original_128", "upper_left"): config}))
        self.assertEqual(row["assessment_state"], "INVALID_EVIDENCE")
        self.assertIsNone(row["baseline_configuration_outcome"])

    def test_invalid_suffix_preserves_complete_divergence_and_control(self):
        configs = faithful_configurations()
        configs[("original_128", "upper_left")] = configuration()
        configs[("original_128", "accepted_upper")] = configuration({"lower.left": ZERO})
        result = assess(SPEC, INPUTS, configs, invalid_reason="chain failure after validated records")
        self.assertIs(result["baseline_divergence_detected"], True)
        self.assertIs(result["control_mismatch_detected"], True)
        self.assertEqual(baseline(result)["assessment_state"], "COMPLETE")
        self.assertFalse(any(row["failure_mechanism_comparison_eligible"] for row in result["arm_comparisons"]))
        self.assertIn("PACKET_INVALID_EVIDENCE", comparison(result, "lower_left")["exclusion_reasons"])

    def test_invalid_suffix_preserves_partial_known_control_and_unknowns(self):
        config = configuration({"lower.left": ZERO}, completed=False)
        config["outcomes"]["repeat"] = {"lower.left": {"status": ZERO}}
        result = assess(SPEC, INPUTS, {("original_128", "accepted_upper"): config}, invalid_reason="corrupt next record")
        row = baseline(result, "accepted_upper")
        self.assertIs(row["control_mismatch"], True)
        self.assertIsNone(row["baseline_matches_historical_label"])
        self.assertIn("corrupt next record", row["reason"])
        self.assertEqual(baseline(result)["assessment_state"], "INVALID_EVIDENCE")
        self.assertIsNone(baseline(result)["BASELINE_DIVERGENCE"])

    def test_terminal_names_do_not_erase_validated_findings(self):
        configs = {("original_128", "upper_left"): configuration(), ("original_128", "accepted_upper"): configuration({"lower.left": ZERO})}
        before = assess(SPEC, INPUTS, configs)
        for terminal in SPEC["terminal_precedence"]:
            with self.subTest(terminal=terminal):
                result = assess(SPEC, INPUTS, configs, invalid_reason=terminal if terminal == "EXECUTION_ERROR" else None)
                for key in ("baseline_divergence_detected", "baseline_divergence_flagged_ids", "control_mismatch_detected", "control_mismatch_flagged_ids"):
                    self.assertEqual(result[key], before[key])

    def test_one_unresolved_failure_keeps_aggregate_unknown(self):
        configs = faithful_configurations()
        del configs[("original_128", "lower_both")]
        result = assess(SPEC, INPUTS, configs)
        self.assertIsNone(result["baseline_divergence_detected"])
        self.assertEqual(result["baseline_divergence_unresolved_ids"], ["lower_both"])
        self.assertIs(result["control_mismatch_detected"], False)

    def test_control_flag_excludes_otherwise_eligible_comparisons(self):
        configs = faithful_configurations()
        configs[("original_128", "accepted_lower")] = configuration({"upper.right": OTHER})
        result = assess(SPEC, INPUTS, configs)
        self.assertIn("CONTROL_MISMATCH_REVIEW_REQUIRED", comparison(result)["exclusion_reasons"])
        self.assertFalse(any(row["failure_mechanism_comparison_eligible"] for row in result["arm_comparisons"]))

    def test_incomplete_compared_arm_cannot_be_eligible(self):
        configs = faithful_configurations()
        configs[("point_128", "upper_left")]["completed"] = False
        row = comparison(assess(SPEC, INPUTS, configs))
        self.assertIs(row["failure_mechanism_comparison_eligible"], False)
        self.assertIn("COMPARED_ARM_INCOMPLETE", row["exclusion_reasons"])

    def test_compared_arm_failure_is_a_valid_descriptive_comparison(self):
        result = assess(SPEC, INPUTS, faithful_configurations())
        self.assertEqual(comparison(result)["compared_configuration_outcome"], NONPASS)
        self.assertIs(comparison(result)["failure_mechanism_comparison_eligible"], True)

    def test_accepted_control_is_not_historical_failure_mechanism_specimen(self):
        row = comparison(assess(SPEC, INPUTS, faithful_configurations()), "accepted_upper")
        self.assertIs(row["failure_mechanism_comparison_eligible"], False)
        self.assertIn("ACCEPTED_CONTROL_NOT_HISTORICAL_FAILURE", row["exclusion_reasons"])

    def test_input_and_output_mutations_do_not_alias(self):
        configs = faithful_configurations()
        before = json.dumps([[list(key), value] for key, value in configs.items()], sort_keys=True)
        result = assess(SPEC, INPUTS, configs)
        baseline(result)["observed_endpoint_outcomes"]["primary"]["upper.left"]["status"] = "tampered"
        self.assertEqual(json.dumps([[list(key), value] for key, value in configs.items()], sort_keys=True), before)

    def test_unrecognized_outcome_never_certifies(self):
        config = configuration()
        for stage in ("primary", "repeat"):
            config["outcomes"][stage]["upper.left"] = {"status": "WORKER_SAYS_PASS"}
        row = baseline(assess(SPEC, INPUTS, {("original_128", "upper_left"): config}))
        self.assertEqual(row["assessment_state"], "INVALID_EVIDENCE")
        self.assertIsNone(row["BASELINE_DIVERGENCE"])

    def test_membership_and_signature_mutations_are_rejected(self):
        bad_inputs = json.loads(json.dumps(INPUTS))
        bad_inputs["specimens"][0]["id"] = bad_inputs["specimens"][1]["id"]
        with self.assertRaises(ValueError):
            assess(SPEC, bad_inputs, {})
        bad_inputs = json.loads(json.dumps(INPUTS))
        bad_inputs["specimens"][0]["historical_signature"] = "upper.unknown"
        with self.assertRaises(ValueError):
            assess(SPEC, bad_inputs, {})
        with self.assertRaises(ValueError):
            assess(SPEC, INPUTS, {("unfrozen_arm", "upper_left"): configuration()})

    def test_repeated_derivation_is_canonical_identical(self):
        configs = faithful_configurations()
        first = json.dumps(assess(SPEC, INPUTS, configs), sort_keys=True, separators=(",", ":"))
        second = json.dumps(assess(SPEC, INPUTS, configs), sort_keys=True, separators=(",", ":"))
        self.assertEqual(first, second)


def run_controls():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AssessmentControls)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return {
        "control_family": "M1_assessments_synthetic_only",
        "tests_run": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "status": "PASS" if result.wasSuccessful() else "FAIL",
        "failures": [{"test": test.id(), "traceback": detail} for test, detail in result.failures + result.errors],
        "numerical_calls": 0,
    }


if __name__ == "__main__":
    report = run_controls()
    print(json.dumps(report, indent=2, sort_keys=True))
    sys.exit(0 if report["status"] == "PASS" else 1)
