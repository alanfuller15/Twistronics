# Ledger reader handoff

Our v048 SUMMARY.json is a separate schema from the partner v046 and our earlier v046. Do not infer version identity from the integer alone; preserve the source archive and file hash.

Required top-level acceptance: `status == "ACCEPT"`, `version == "v048"`, `kinetic == "lab_nn_full"`, and the recorded `protocol_sha256`. `verification_tier` remains `self-tested`; `delivery_status` refers only to recipient consumption.

- `folds`: eight rows, one for each (`case`, `engine`, `N`). Cases are `flat_birth` and `final_ann`; engines are `bm_lab`, `ref_lab`; N is 4 or 6. Each row supplies `parameter`, `pair_label`, `root_states`, `charge_stations`, `just_open_gap`, `min_chart_overlap`, `loop_fallbacks` and an optional `birth_join`. Parameter means ratio for flat_birth and A for final_ann. This differs from our v046 upper-fold rows, whose parameter key was `ratio`.
- `gapped_cases`: four rows, one for each (`engine`, `N`), with `geometry`, `cutoff_tol`, `states`, `min_gap`, `min_seam_overlap`, `w1`, `w1_constant`, `anchor_joins` and the raw-summary `source` path. Each anchor join contains its name, per-gap differences and cycle-label agreement.
- Aggregate counts: `fold_windows`, `root_states`, `charge_stations`, `gapped_states`. Root-continuation states do not each have a loop-charge measurement; do not merge these counts into one purported number of fully charge-gated states.
- Aggregate margins: `minimum_sampled_gap`, `min_cycle_seam_overlap`, `max_anchor_gap_difference`; `w1` contains the common measured per-band/group labels.
- `source_sha256`: exact relative source-record paths and their file hashes. LEDGER_SOURCES.json also exposes this mapping. The release MANIFEST.json covers all archive members.

Before publishing a table, require accepted records, finite values, no missing/duplicate case-engine-cutoff rows, consistent model tags and source hashes. Unknown schemas should stop or remain explicitly unverified, never inherit an ACCEPT label. The supplied v047 preparation JSON lacks this acceptance protocol and stays in the provisional section.

Historical summaries are not retroactively upgraded to this schema. The generator includes explicit adapters for their known fields and checks their recorded model tags; it does not fill absent numerical evidence with defaults. Coverage qualifications are separate reviewed annotations in COVERAGE.json, not discoveries made by a formatting script.
