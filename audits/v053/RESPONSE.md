# Response to the inspection-only v053 audit

The supplied audit is preserved in [twistronics_v053_audit.md](twistronics_v053_audit.md), together with its full inventory, scanner observations and evidence checks. Its source archive is retained as `supplied-evidence.zip`. The project archive SHA-256 in `archive-sha256.json` matches the published v053 source archive: `e3eb430269e849f13d9127b9ed1a4b55d3e7244d6ded97c02801eee19f663820`.

## Confirmed repair targets

Targeted source inspection during publication confirms the following in the current v053 files. No fixes or fresh project tests were performed as part of this publication.

1. **Optimizer metadata:** `research/v053/engines/bm_strain.py`, `BM.refine`, replaces `res` after a wrapped refinement but retains the first attempt's success/status/message. Refresh metadata from the final result, preserve both attempts, and make failed/nonfinite outcomes explicit. Whether this helper affected an accepted result remains unverified.
2. **Test-evidence binding:** `research/v053/build_report.py` embeds `tests_this_batch=18` and passing-test prose. A historical log reports 18 passes; publication must separately verify a machine-readable test record bound to source, tests, dependencies and runtime. A historical log is not a fresh run.
3. **Portable packaging:** `research/v053/package_release.py` requires the exact v052 ZIP under `sequence-outputs/` and does not create its output parent. The published extracted prior tree is not that byte-identical archive. Make required input/output paths explicit and preserve the provenance distinction.
4. **Legacy acceptance interfaces:** `research/v053/engines/euler.py` uses an optimizable assertion before dropping imaginary components and returns orientation/closure diagnostics with its winding. Replace the runtime guard and keep legacy Euler/braid outputs exploratory unless they pass the declared isolation, orientation and refinement gates.

## Scope of this publication

The research tree remains the original v053 snapshot. This audit and response are separate additions, not rewritten frozen evidence. No accepted label is changed by this publication, and no claim is made that the defects had no effect. Establishing effect requires call-path review and appropriately gated regression/replay work.

The supplied audit reports internally consistent manifest, source, anchor and saved-frame hashes, 76 primary records and 36 mesh checks. Those checks establish internal consistency, not scientific truth, a fresh numerical replay or physical-bilayer validation. The separate lower unlink collision remains open. Dependency review is sampled, not complete CVE clearance.

Repair these publication/guard defects in a separately versioned change before expanding the scientific claims. Preserve the existing v053 evidence and compare any subsequent replay results explicitly.
