#!/usr/bin/env python3
"""
tool_quality_weighting.py — quality-weighted consensus for audit.py --ingest.

WHY: the flat consensus term (1.6 * n_distinct_tools) treats all tool agreements
as interchangeable. Real Lipp CVE data (ISSTA'22, Zenodo 10.5281/zenodo.6515687)
shows tools are NOT interchangeable: standalone recall ranges CommSCA 53.9% down
to Cppcheck 4.1%, and consensus weight should reflect that. This module replaces
the flat term with a quality-weighted one, via a THREE-CASE gate that is honest
about WHEN tool quality is actually known.

TIERING (charter III.7 — read VALIDATION.md):
  - The weighting PRINCIPLE (tools non-interchangeable; LOCO-family marginal
    weighting; the coarse tier transfers, fine weights do not) is
    [externally-grounded] on real Lipp data, cross-checked against the paper's
    published 53.9% CommSCA anchor and +15pp all-6 lift.
  - THIS CODE is [self-tested]: it runs and passes tests also written here.
    A sandbox PASS is Claude grading Claude. Closing to [externally-verified]
    is the same external-judge desktop step the rest of audit.py faces.

WHAT IS NOT HERE (resolved earlier, do not re-add):
  - R redundancy score: DROPPED. Coverage recall is monotone submodular, so
    L_zmin (min-over-subsets marginal) == full-set LOCO by identity for ANY
    detection dataset (verified by enumeration: 500 random + adversarial
    mutually-masking). R = standalone - L_zmin is therefore identically
    (standalone - full-set-LOCO) and carries no signal distinct from the weight.
    It is not "dormant"; it is structurally empty for detection. Standalone
    recall remains a DIAGNOSTIC, never a ranking axis.

THE THREE CASES:
  CASE 1  ground truth present for the tools in this ingest (a labeled benchmark
          with a CVE/answer key)  -> compute per-tool LOCO weights from THIS
          data's recall, per-ingest. Full-fidelity fine weights. Never reuse
          Lipp's numbers on non-Lipp input.
  CASE 2  no ground truth, tools recognized (production path, restricted-2b)
          -> apply ONLY the coarse transferable signal as discounted priors:
          a near-zero floor for measured-non-contributing tools (Cppcheck class)
          and a commercial/OSS tier gap. NOT the fine per-tool weights. Disclose
          per-scan that these are cross-dataset PRIORS, not measured on the
          user's code, with the transferability caveat.
  CASE 3  no ground truth, tools unrecognized -> flat count (1.6 * n_tools),
          exactly the current baseline. Disclose weighting is INACTIVE.

Every case DISCLOSES its mode. A user must always see whether weighting is
grounded on their data, carried as a prior, or off.
"""

# ---------------------------------------------------------------------------
# The flat consensus coefficient, preserved from audit.py (case-3 baseline).
FLAT_CONSENSUS_COEF = 1.6

# ---------------------------------------------------------------------------
# COARSE TRANSFERABLE PRIOR (the ONLY thing hard-coded from Lipp).
#
# PROVENANCE: derived from the real Lipp 9-project matrix (193 CVEs, join
# reproduces the paper's published CommSCA 53.9% / all-6 68.9% / +15pp lift).
# TRANSFERABILITY BOUND (measured, not assumed, across the 9 projects):
#   - The COARSE TIER TRANSFERS: Cppcheck is bottom-or-tied in 5/9 projects and
#     never strong (max 20%); the commercial(CommSCA)/OSS gap holds on average.
#   - The FINE WEIGHTS DO NOT TRANSFER: CodeQL swings 0%->82.4% across projects
#     (stdev 28.9%); CommSCA is top in only 4/9. So per-tool fine weights are
#     codebase-unstable and are DELIBERATELY NOT carried here.
# Therefore this table encodes only a 3-bucket tiering, heavily discounted.
# A recognized tool inherits its bucket's multiplier; unknown tools -> case 3.
#
# Buckets (multiplier applied to that tool's contribution to the consensus term,
# relative to a baseline OSS tool = 1.0):
#   floor       ~0.1  measured non-contributing (Cppcheck class): near-zero,
#                     but NOT exactly 0 — a prior, not a measurement on this code.
#   oss         1.0   open-source baseline tier.
#   commercial  1.6   commercial/strong tier (CommSCA class), discounted from the
#                     fine ratio (CommSCA fine weight was ~0.67 vs OSS ~0.08-0.19;
#                     the raw ratio is ~4-8x, DISCOUNTED to 1.6x because the
#                     cross-project data does not support the full fine gap).
COARSE_PRIOR_TIER = {
    "cppcheck":    "floor",
    "flawfinder":  "oss",
    "infer":       "oss",
    "codechecker": "oss",
    "codeql":      "commercial",   # strong on average, but high variance (0-82%)
    "commsca":     "commercial",
}
# Multipliers redistribute AROUND the flat baseline rather than inflating it.
# Design decision (made explicit, per review): the prior both boosts strong
# agreements and cuts weak ones. To avoid GLOBAL INFLATION — where a
# two-commercial-tool agreement silently outscales the severity/kind/location
# components the rest of the score assumes — the tiers are anchored so the OSS
# baseline == 1.0 and the boost is modest and DISCLOSED at magnitude, not just
# named. commercial=1.25 (a disclosed +25% for a strong tool, not +60%),
# floor=0.1 (near-zero for measured-non-contributing). A same-tier pair therefore
# stays near the flat baseline; the prior tilts, it does not inflate.
TIER_MULTIPLIER = {"floor": 0.1, "oss": 1.0, "commercial": 1.25}

# Default multiplier for a tool we have NEVER measured: flat (1.0). An unknown
# tool contributes at baseline and — critically — does NOT change any other
# tool's multiplier. This is what makes the consensus term for a given set of
# agreeing tools INVARIANT to what else is in the ingest.
UNKNOWN_TOOL_MULTIPLIER = 1.0

# tools we have EVER measured (so we can distinguish case 2 from case 3 for the
# DISCLOSURE mode — note this no longer affects per-tool multipliers).
RECOGNIZED_TOOLS = set(COARSE_PRIOR_TIER.keys())


def _norm(name):
    return (name or "").strip().lower()


# ---------------------------------------------------------------------------
# CASE 1 helper: compute per-tool LOCO weights from a real detection matrix.
# detection_matrix: list of sets, one per ground-truth item (e.g. CVE), each the
# set of tool-names that detected it. This is the ONLY correct input for fine
# weights and is available ONLY when the ingest carries a labeled answer key.
def compute_loco_weights(detection_matrix, tools):
    """Full-set normalized LOCO weight per tool, from real ground-truth recall.
    Returns {tool: weight in [0,1], renormalized to sum 1 over positive weights}.
    [externally-grounded] when detection_matrix is real external ground truth."""
    tools = list(tools)
    N = len(detection_matrix)
    if N == 0:
        return {t: 0.0 for t in tools}

    def recall(S):
        S = set(S)
        return sum(1 for d in detection_matrix if d & S) / N

    full_others = {t: [x for x in tools if x != t] for t in tools}
    # full-set LOCO = recall(all) - recall(all without t) = marginal of t given rest
    all_set = set(tools)
    loco = {}
    for t in tools:
        loco[t] = recall(all_set) - recall(full_others[t])
    tot = sum(w for w in loco.values() if w > 0) or 1.0
    return {t: (loco[t] / tot if loco[t] > 0 else 0.0) for t in tools}


# ---------------------------------------------------------------------------
# The mode selector + per-tool consensus multiplier.
def resolve_weighting(tools_present, ground_truth=None):
    """
    Decide which case fires and return (mode_dict, tool_multiplier(fn)).

    tools_present : iterable of tool driver names seen in this ingest.
    ground_truth  : optional. If provided, must be a dict with:
                      {"detection_matrix": [set(tool,...), ...], "label": str}
                    signalling CASE 1 (a labeled benchmark ingest).

    Returns:
      mode : dict describing which case fired + disclosure text + any weights.
      mult : function(tool_name) -> float multiplier on that tool's consensus
             contribution. Case 3 returns 1.0 for all (flat behavior preserved).
    """
    present = [t for t in tools_present]
    present_norm = {_norm(t) for t in present}

    # =====================================================================
    # PER-TOOL multiplier construction (ingest-INVARIANT).
    #
    # THE INVARIANT (the bug fix): a tool's multiplier depends ONLY on that
    # tool's own known quality, never on what OTHER tools are in the ingest.
    # So the consensus term for a given SET OF AGREEING TOOLS is identical no
    # matter what else was run. Adding an unrelated scanner cannot rescore a
    # finding those two tools agreed on.
    #
    # Precedence, per tool:
    #   1. measured on THIS ingest's ground truth (if a benchmark key present)
    #   2. else coarse tier prior (if the tool is recognized)
    #   3. else flat default (unknown tool contributes at baseline 1.0)
    # =====================================================================
    measured = {}
    gt_label = None
    if ground_truth and ground_truth.get("detection_matrix"):
        dm = ground_truth["detection_matrix"]
        gt_label = ground_truth.get("label", "labeled-benchmark")
        raw = compute_loco_weights(dm, sorted({_norm(t) for d in dm for t in d} | present_norm))
        pos = [w for w in raw.values() if w > 0]
        avg = (sum(pos) / len(pos)) if pos else 1.0
        measured = {t: (raw.get(t, 0.0) / avg if avg else 0.0) for t in raw}

    def mult(tool):
        t = _norm(tool)
        if t in measured:                     # (1) measured on this data
            return measured[t]
        if t in COARSE_PRIOR_TIER:            # (2) coarse tier prior
            return TIER_MULTIPLIER[COARSE_PRIOR_TIER[t]]
        return UNKNOWN_TOOL_MULTIPLIER        # (3) flat default, ingest-independent

    # ---- per-tool provenance, for disclosure -----------------------------
    def source_of(t):
        tn = _norm(t)
        if tn in measured: return "measured"
        if tn in COARSE_PRIOR_TIER: return "prior"
        return "flat"
    src = {t: source_of(t) for t in present}
    n_measured = sum(1 for v in src.values() if v == "measured")
    n_prior    = sum(1 for v in src.values() if v == "prior")
    n_flat     = sum(1 for v in src.values() if v == "flat")

    # ---- DISCLOSURE MODE: describes the MIX; does NOT change any multiplier.
    # (case numbers retained for continuity, now purely descriptive labels.)
    if n_measured and not (n_prior or n_flat):
        case, modelabel = 1, "MEASURED"
        disclosure = (
            f"Quality-weighting MODE=MEASURED (all {n_measured} tools): consensus "
            f"weights computed from ground-truth recall in THIS ingest "
            f"({gt_label}). Grounded on your data, not carried priors.")
    elif n_flat == 0 and n_measured == 0:
        case, modelabel = 2, "PRIOR"
        disclosure = (
            "Quality-weighting MODE=PRIOR (restricted-2b): NO ground truth for "
            "your code, so a coarse cross-dataset TIER prior is applied per tool "
            "(floor=x0.1 / oss=x1.0 / commercial=x1.25), NOT fine per-tool "
            "weights. MAGNITUDE (disclosed): a commercial+commercial agreement "
            "scores x1.25 the flat baseline, floor tools x0.1; same-tier "
            "agreements stay at baseline. CAVEAT: tiers are from the Lipp C-CVE "
            "dataset and may not hold for your codebase — a tool can over/under-"
            "perform its prior (CodeQL ranged 0%-82% recall across Lipp's 9 "
            "projects). Indicative, not measured-on-your-code.")
    else:
        # MIXED: some tools measured/prior, some unknown. Each tool weighted by
        # its OWN source; unknown tools sit at flat. This is the case the old
        # code got wrong (it collapsed the whole ingest to flat).
        case, modelabel = 3, "MIXED"
        disclosure = (
            f"Quality-weighting MODE=MIXED: {n_measured} measured, {n_prior} "
            f"prior-tiered, {n_flat} unrecognized (flat x1.0). Each tool is "
            f"weighted by its OWN known quality; unrecognized tools contribute "
            f"at baseline and do NOT change other tools' weights. A finding's "
            f"score depends only on the tools that agree ON IT.")

    mode = {
        "case": case, "mode": modelabel,
        "per_tool_source": {t: src[t] for t in sorted(present, key=_norm)},
        "per_tool_multiplier": {t: round(mult(t), 3) for t in sorted(present, key=_norm)},
        "tier_multipliers": TIER_MULTIPLIER,
        "disclosure": disclosure,
    }
    if gt_label:
        mode["label"] = gt_label
        mode["weights_measured_on_this_data"] = {
            t: round(measured.get(_norm(t), 0.0), 3) for t in sorted(present, key=_norm)
            if src[t] == "measured"}
    return mode, mult


# ---------------------------------------------------------------------------
# The consensus term. Replaces `1.6 * rec["n_tools"]` in audit.py.
# Instead of counting distinct tools, sum their per-tool multipliers * flat coef.
# In CASE 3 every multiplier is 1.0, so this reduces EXACTLY to 1.6 * n_tools —
# the baseline is preserved bit-for-bit when weighting is off.
def weighted_consensus_term(agreeing_tools, mult):
    return FLAT_CONSENSUS_COEF * sum(mult(t) for t in agreeing_tools)


# ===========================================================================
# INTEGRATION POINT for audit.py ingest_sarif (documented, not auto-applied):
#
#   In ingest_sarif(), after tools_seen is known and before the per-rec score
#   loop, add:
#
#       from tool_quality_weighting import resolve_weighting, weighted_consensus_term
#       qmode, qmult = resolve_weighting(tools_seen, ground_truth=GT_or_None)
#
#   Then in the score loop, REPLACE:
#       1.6 * rec["n_tools"]
#   WITH:
#       weighted_consensus_term(rec["tools"], qmult)
#
#   And surface qmode["disclosure"] in main()'s ingest print block, and
#   qmode into the JSON under agg["quality_weighting"]. GT_or_None is a labeled
#   benchmark's detection matrix if the ingest carries one, else None (the
#   normal production case -> case 2 or 3).
# ===========================================================================


# ---------------------------------------------------------------------------
# SELF-TESTS ([self-tested] — proves routing/disclosure/baseline-preservation,
# NOT that the weighting is correct on real production data).
def _selftests():
    import io, contextlib
    out = []
    def check(name, cond):
        out.append((name, bool(cond)))

    # ---- THE BUG-CATCHING TEST: cross-ingest consistency invariant --------
    # The SAME set of agreeing tools must produce the SAME consensus term
    # regardless of what OTHER tools are present in the ingest. This is the
    # invariant the old per-ingest-global architecture violated.
    _, f_pure   = resolve_weighting(["CommSCA", "CodeQL"])                  # only these two ran
    _, f_plus1  = resolve_weighting(["CommSCA", "CodeQL", "semgrep"])       # + an unrelated unknown
    _, f_plus2  = resolve_weighting(["CommSCA", "CodeQL", "semgrep", "pmd"])# + two unknowns
    agree = ["CommSCA", "CodeQL"]
    term_pure  = weighted_consensus_term(agree, f_pure)
    term_plus1 = weighted_consensus_term(agree, f_plus1)
    term_plus2 = weighted_consensus_term(agree, f_plus2)
    check("INVARIANT: CommSCA+CodeQL term unchanged by other tools present",
          abs(term_pure - term_plus1) < 1e-9 and abs(term_pure - term_plus2) < 1e-9)
    # and the previously-buggy specific case: adding Semgrep must NOT rescore it
    check("INVARIANT: unknown tool does not collapse recognized-tool weights",
          f_plus1("CommSCA") == f_pure("CommSCA") and f_plus1("CodeQL") == f_pure("CodeQL"))
    # the unknown tool itself sits at flat, without disturbing others
    check("unknown tool contributes at flat 1.0", f_plus1("semgrep") == 1.0)

    # MIXED disclosure fires (not a global collapse to flat)
    m_mix, _ = resolve_weighting(["CommSCA", "CodeQL", "semgrep"])
    check("mixed ingest discloses MIXED (per-tool), not global-flat",
          m_mix["mode"] == "MIXED")
    check("mixed per_tool_source is correct",
          m_mix["per_tool_source"]["CommSCA"] == "prior"
          and m_mix["per_tool_source"]["semgrep"] == "flat")

    # ---- PRIOR mode: recognized tools, no GT, redistributes around baseline
    m2, f2 = resolve_weighting(["Cppcheck", "CommSCA"])
    check("PRIOR mode when all recognized", m2["mode"] == "PRIOR")
    check("Cppcheck floored (<oss)", f2("Cppcheck") < f2("Flawfinder"))
    check("CommSCA commercial (>oss)", f2("CommSCA") > f2("Flawfinder"))
    check("only 3 buckets used (no fine weights)",
          set(round(f2(t), 4) for t in ["Cppcheck","Flawfinder","Infer","CodeChecker","CodeQL","CommSCA"])
          <= set(TIER_MULTIPLIER.values()))
    check("PRIOR discloses caveat + magnitude", "caveat" in m2["disclosure"].lower()
          and "x1.25" in m2["disclosure"])
    # NO GLOBAL INFLATION: a same-tier (oss+oss) agreement stays at flat baseline
    _, f_oss = resolve_weighting(["Flawfinder", "Infer"])
    oss_pair = weighted_consensus_term(["Flawfinder", "Infer"], f_oss)
    check("no inflation: oss+oss agreement stays at flat baseline",
          abs(oss_pair - FLAT_CONSENSUS_COEF * 2) < 1e-9)
    # commercial boost is the DISCLOSED modest magnitude, not the old 1.6
    comm_pair = weighted_consensus_term(["CommSCA", "CodeQL"], f2)
    check("commercial+commercial boost is x1.25 (disclosed), not x1.6",
          abs(comm_pair - FLAT_CONSENSUS_COEF * 2 * 1.25) < 1e-9)

    # ---- FLAT baseline preserved for all-unknown ingest -------------------
    m3, f3 = resolve_weighting(["semgrep", "pmd"])
    check("all-unknown -> MIXED/flat multipliers 1.0",
          f3("semgrep") == 1.0 and f3("pmd") == 1.0)
    agree3 = ["semgrep", "pmd", "sonar"]
    check("all-unknown reduces to flat 1.6*n_tools",
          abs(weighted_consensus_term(agree3, f3) - FLAT_CONSENSUS_COEF * len(agree3)) < 1e-9)

    # ---- MEASURED mode: ground truth present -> fine weights from THIS data
    dm = [ {"commsca"}, {"commsca","codeql"}, {"commsca"}, {"codeql"}, set() ]
    m1, f1 = resolve_weighting(["CommSCA","CodeQL","Cppcheck"],
                               ground_truth={"detection_matrix": dm, "label":"synthetic-gt"})
    check("MEASURED mode with ground truth", m1["mode"] == "MEASURED")
    check("MEASURED CommSCA weight >= CodeQL", f1("commsca") >= f1("codeql"))
    check("MEASURED Cppcheck (absent from GT) ~ 0 weight", f1("cppcheck") == 0.0)
    check("MEASURED discloses grounded-on-your-data", "MEASURED" in m1["disclosure"])

    # ---- DETERMINISM ------------------------------------------------------
    a = [round(f2(t),6) for t in ["Cppcheck","CommSCA","Infer"]]
    _, f2b = resolve_weighting(["Cppcheck","CommSCA"])
    b = [round(f2b(t),6) for t in ["Cppcheck","CommSCA","Infer"]]
    check("deterministic multipliers", a == b)

    passed = sum(1 for _, ok in out if ok)
    for name, ok in out:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"\n[self-tested] {passed}/{len(out)} routing/disclosure/baseline checks passed "
          f"(proves the CODE routes + discloses + preserves the flat baseline; "
          f"does NOT prove weighting is correct on real production data).")
    return passed == len(out)


if __name__ == "__main__":
    ok = _selftests()
    raise SystemExit(0 if ok else 1)
