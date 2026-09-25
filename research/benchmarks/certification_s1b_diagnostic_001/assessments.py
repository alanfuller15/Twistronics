"""Derive the frozen M1 review flags from verifier-validated evidence only.

This module does not validate interval arithmetic, source identity, hashes or the
event chain.  Its caller MUST perform those checks and only populate a repeat
outcome after exact primary/repeat evidence equality has been established.  In
particular, a worker's own comparison or success flags are not inputs here.

An invalid suffix does not erase a finding proved by the validated prefix.
``invalid_reason`` describes that suffix (or another packet error): unresolved
assessments remain unknown and all mechanism comparisons are excluded.
"""

from copy import deepcopy


EXPECTED = "EXPECTED_INERTIA_VERIFIED"
OTHER = "OTHER_INERTIA_VERIFIED"
ZERO = "ZERO_CONTAINING_PIVOT"
GRAM = "GRAM_UNCERTIFIED"
PASS = "FOUR_ENDPOINT_TESTS_PASS"
NONPASS = "NO_FOUR_ENDPOINT_PASS"
OUTCOMES = frozenset((EXPECTED, OTHER, ZERO, GRAM))
STAGES = ("primary", "repeat")


def _status(outcome):
    return outcome.get("status") if isinstance(outcome, dict) else outcome


def _snapshot(config, endpoints):
    """Extract conservative facts without trusting ``completed`` on its own."""
    observed = {stage: {} for stage in STAGES}
    if config is None:
        return {
            "started": False, "complete": False, "issues": [],
            "observed": observed, "paired": {}, "gram": {},
            "positive_gram": False, "gram_failure": False,
            "known_failure": False, "outcome": None,
        }
    if not isinstance(config, dict):
        raise ValueError("configuration must be a mapping or absent")
    issues = []
    all_outcomes = config.get("outcomes", {})
    if not isinstance(all_outcomes, dict):
        all_outcomes = {}
        issues.append("OUTCOMES_NOT_MAPPING")
    for stage in STAGES:
        stage_outcomes = all_outcomes.get(stage, {})
        if not isinstance(stage_outcomes, dict):
            issues.append("OUTCOMES_NOT_MAPPING:" + stage)
            continue
        if set(stage_outcomes) - set(endpoints):
            issues.append("UNEXPECTED_ENDPOINT:" + stage)
        for endpoint in endpoints:
            if endpoint in stage_outcomes:
                observed[stage][endpoint] = deepcopy(stage_outcomes[endpoint])
                if _status(stage_outcomes[endpoint]) not in OUTCOMES:
                    issues.append("INVALID_ENDPOINT_OUTCOME:" + stage + ":" + endpoint)
    paired = {}
    for endpoint in endpoints:
        primary = _status(observed["primary"].get(endpoint))
        repeat = _status(observed["repeat"].get(endpoint))
        if primary in OUTCOMES and repeat in OUTCOMES:
            if primary == repeat:
                paired[endpoint] = primary
            else:
                issues.append("REPEAT_STATUS_MISMATCH:" + endpoint)
        elif endpoint in observed["repeat"] and endpoint not in observed["primary"]:
            issues.append("REPEAT_WITHOUT_PRIMARY:" + endpoint)
    raw_gram = config.get("gram_positive", {})
    if not isinstance(raw_gram, dict):
        raw_gram = {}
        issues.append("GRAM_NOT_MAPPING")
    gram = {stage: raw_gram.get(stage) for stage in STAGES}
    if any(value is not None and type(value) is not bool for value in gram.values()):
        issues.append("INVALID_GRAM_STATE")
        gram = {stage: value if type(value) is bool else None for stage, value in gram.items()}
    if all(type(value) is bool for value in gram.values()) and gram["primary"] != gram["repeat"]:
        issues.append("GRAM_REPEAT_MISMATCH")
    positive_gram = all(gram[stage] is True for stage in STAGES)
    gram_failure = all(gram[stage] is False for stage in STAGES)
    if positive_gram and GRAM in paired.values():
        issues.append("GRAM_SKIP_WITH_POSITIVE_GRAM")
    if gram_failure and any(status != GRAM for status in paired.values()):
        issues.append("LDL_OUTCOME_WITH_FAILED_GRAM")
    complete = (
        config.get("completed") is True
        and len(paired) == len(endpoints)
        and (positive_gram or gram_failure)
        and not issues
    )
    # A paired failure is decisive even if later endpoints were interrupted.
    # Invalid local records cannot establish a fact; a prior valid configuration
    # remains usable when the caller reports an invalid *suffix* separately.
    known_failure = not issues and (
        gram_failure or any(status != EXPECTED for status in paired.values())
    )
    outcome = (PASS if positive_gram and all(paired[e] == EXPECTED for e in endpoints) else NONPASS) if complete else None
    return {
        "started": True, "complete": complete, "issues": issues,
        "observed": observed, "paired": paired, "gram": gram,
        "positive_gram": positive_gram, "gram_failure": gram_failure,
        "known_failure": known_failure, "outcome": outcome,
    }


def _aggregate(rows, key, applicable_key):
    applicable = [row for row in rows if row[applicable_key]]
    flagged = [row["specimen_id"] for row in applicable if row[key] is True]
    unresolved = [row["specimen_id"] for row in applicable if row[key] is None]
    state = True if flagged else (None if unresolved else False)
    return state, flagged, unresolved


def assess(spec, inputs, configurations, invalid_reason=None):
    """Return deterministic baseline assessments and restricted comparisons.

    ``configurations[(arm_id, specimen_id)]`` contains ``outcomes`` by stage and
    endpoint, ``gram_positive`` by stage, and a verifier-derived ``completed``
    boolean. Outcomes are status strings or mappings with a ``status`` key.
    An absent configuration is unstarted. All source bindings and normalized
    arithmetic outcomes must already have been checked by the caller.
    """
    endpoints = list(spec["endpoint_order"])
    specimen_order = list(spec["specimen_order"])
    arms = [arm["id"] for arm in spec["arms_in_order"]]
    if not endpoints or len(set(endpoints)) != len(endpoints):
        raise ValueError("endpoint_order must be nonempty and unique")
    if len(set(specimen_order)) != len(specimen_order) or len(set(arms)) != len(arms) or "original_128" not in arms:
        raise ValueError("ambiguous specimen or arm identities")
    specimens = inputs["specimens"]
    by_id = {row["id"]: row for row in specimens}
    if len(by_id) != len(specimens) or set(by_id) != set(specimen_order):
        raise ValueError("INPUTS specimen membership does not match SPEC")
    unexpected_configs = set(configurations) - {(arm, specimen) for arm in arms for specimen in specimen_order}
    if unexpected_configs:
        raise ValueError("unexpected configuration identity")
    if invalid_reason is not None and (not isinstance(invalid_reason, str) or not invalid_reason):
        raise ValueError("invalid_reason must be a nonempty string or None")
    snapshots = {
        (arm, specimen): _snapshot(configurations.get((arm, specimen)), endpoints)
        for arm in arms for specimen in specimen_order
    }
    rows = []
    for specimen in specimen_order:
        source = by_id[specimen]
        signature = source["historical_signature"]
        accepted = signature == "accepted"
        failed = [] if accepted else signature.split("+")
        if len(set(failed)) != len(failed) or set(failed) - set(endpoints) or (not accepted and not failed):
            raise ValueError("invalid historical endpoint signature")
        failed = [endpoint for endpoint in endpoints if endpoint in failed]
        baseline = snapshots[("original_128", specimen)]
        complete = baseline["complete"]
        historical_outcome = PASS if accepted else NONPASS
        baseline_failed = [e for e in endpoints if baseline["paired"][e] != EXPECTED] if complete else None
        coarse_match = historical_outcome == baseline["outcome"] if complete else None
        endpoint_match = failed == baseline_failed if complete and not accepted else None
        if baseline["issues"]:
            state, reason = "INVALID_EVIDENCE", "; ".join(baseline["issues"])
        elif complete:
            state, reason = "COMPLETE", "Completed baseline with verified primary/repeat evidence"
        elif invalid_reason is not None:
            state, reason = "INVALID_EVIDENCE", "Unresolved baseline after packet error: " + invalid_reason
        elif not baseline["started"]:
            state, reason = "NOT_STARTED", "No validated original_128 configuration"
        else:
            state, reason = "INCOMPLETE", "Baseline lacks a complete verified primary/repeat configuration"
        divergence = None if accepted else (True if baseline["outcome"] == PASS else (False if baseline["known_failure"] else None))
        control_mismatch = None if not accepted else (True if baseline["known_failure"] else (False if baseline["outcome"] == PASS else None))
        exclusions = []
        if accepted:
            exclusions.append("ACCEPTED_CONTROL_NOT_HISTORICAL_FAILURE")
        if not complete:
            exclusions.append("BASELINE_" + state)
        if divergence is True:
            exclusions.append("BASELINE_DIVERGENCE")
        if complete and not accepted:
            if coarse_match is not True:
                exclusions.append("HISTORICAL_LABEL_MISMATCH")
            if endpoint_match is not True:
                exclusions.append("HISTORICAL_FAILED_ENDPOINT_SET_MISMATCH")
            if not baseline["positive_gram"]:
                exclusions.append("BASELINE_GRAM_UNCERTIFIED")
            if any(baseline["paired"].get(e) != ZERO for e in failed):
                exclusions.append("HISTORICAL_FAILED_ENDPOINT_TYPE_MISMATCH")
            if any(baseline["paired"].get(e) != EXPECTED for e in endpoints if e not in failed):
                exclusions.append("OTHER_BASELINE_ENDPOINT_NOT_EXPECTED_INERTIA")
        if invalid_reason is not None:
            exclusions.append("PACKET_INVALID_EVIDENCE")
        rows.append({
            "specimen_id": specimen,
            "source_sequence": source["source_sequence"],
            "source_record_sha256": source["source_record_sha256"],
            "historical_signature": signature,
            "historical_configuration_outcome": historical_outcome,
            "historical_failed_endpoints": failed,
            "assessment_state": state,
            "reason": reason,
            "baseline_configuration_outcome": baseline["outcome"],
            "baseline_matches_historical_label": coarse_match,
            "baseline_failed_endpoints": baseline_failed,
            "baseline_failed_endpoint_outcomes": ([{"endpoint": e, "status": baseline["paired"][e]} for e in baseline_failed] if complete else None),
            "baseline_matches_historical_failed_endpoints": endpoint_match,
            "observed_endpoint_outcomes": baseline["observed"],
            "repeat_consistent_endpoints": [e for e in endpoints if e in baseline["paired"]],
            "gram_positive": baseline["gram"],
            "baseline_divergence_applicable": not accepted,
            "BASELINE_DIVERGENCE": divergence,
            "control_mismatch_applicable": accepted,
            "control_mismatch": control_mismatch,
            "baseline_failure_mechanism_comparison_eligible": not exclusions,
            "exclusion_reasons": exclusions,
        })
    control, control_ids, control_unknown = _aggregate(rows, "control_mismatch", "control_mismatch_applicable")
    divergence, divergence_ids, divergence_unknown = _aggregate(rows, "BASELINE_DIVERGENCE", "baseline_divergence_applicable")
    by_assessment = {row["specimen_id"]: row for row in rows}
    comparisons = []
    for arm in arms:
        if arm == "original_128":
            continue
        for specimen in specimen_order:
            row = by_assessment[specimen]
            compared = snapshots[(arm, specimen)]
            reasons = list(row["exclusion_reasons"])
            if not compared["complete"]:
                reasons.append("COMPARED_ARM_INVALID_EVIDENCE" if compared["issues"] else "COMPARED_ARM_INCOMPLETE")
            if control is True:
                reasons.append("CONTROL_MISMATCH_REVIEW_REQUIRED")
            comparisons.append({
                "specimen_id": specimen,
                "baseline_arm_id": "original_128",
                "compared_arm_id": arm,
                "baseline_configuration_outcome": row["baseline_configuration_outcome"],
                "compared_configuration_outcome": compared["outcome"],
                "compared_arm_complete": compared["complete"],
                "compared_endpoint_outcomes": compared["observed"],
                "failure_mechanism_comparison_eligible": not reasons,
                "exclusion_reasons": reasons,
                "interpretation_scope": "Relative to the retained reconstructed baseline; no historical repair or coverage claim",
            })
    return {
        "baseline_assessments": rows,
        "arm_comparisons": comparisons,
        "control_mismatch_detected": control,
        "control_mismatch_flagged_ids": control_ids,
        "control_mismatch_unresolved_ids": control_unknown,
        "baseline_divergence_detected": divergence,
        "baseline_divergence_flagged_ids": divergence_ids,
        "baseline_divergence_unresolved_ids": divergence_unknown,
        "invalid_reason": invalid_reason,
    }
