# Fable — v073p review and requested return

The native time-reversal wrapper and chiral control are useful additions. Five supplied tests pass, and the unchanged control runner completes. The source archive and original claims remain preserved. Keep this work labeled as an exploratory variant.

The broad claim that every downstream tool applies unchanged is not supported. At nine declared N=3,4,6 K′ points, the fast engine still builds K at the same momentum; its central six energies differ from native K′ by 43.25–100.19 meV. The K positive controls agree to below 5×10⁻¹³ meV. Correct or explicitly reject this mode before downstream use.

## Required variant corrections

1. **Define and enforce supported engines.** Make K′ matrix assembly, derivatives, frames and node solving agree with the declared native model, or reject K′ on unsupported paths. A wrapper on `BM.H` does not affect a fast implementation that bypasses that method. Include tests that fail with the current code, using the retained 18 comparison points and full ordered bases. Do not infer independent TBG or sparse support from these tests.
2. **Make the mirrored comparison executable.** Supply a producer for the manually added “fully mirrored” field, with explicit node order, periodic images, loop start offsets, circle parameterization, orientation convention and transport path. Retain both the unmirrored and corrected outcomes and their raw windings. The current runner reproduces OPPOSITE versus SAME at B=−0.30 and drops the added corrected field.
3. **Enforce measurement preconditions.** Check reality, finite values, requested band indices, pair/individual-band isolation as appropriate, overlaps and sewing loss. Record minimum overlap singular values before taking polar factors. Demonstrate rejection of the native mass=1 broken-reality case and the labeled rank-zero synthetic transport case. Fix or remove the ignored `lo` argument.
4. **Correct the signed explanation.** The saved winding sum is about +2, but the saved e₂ is −1. The cited Ahn–Park–Yang convention uses total winding −2e₂. Derive the relation for the actual code's frame and loop conventions; a text-only sign change does not establish a shared gauge. Preserve the honest statement that no signed inter-valley comparison has been verified.
5. **Provide the external-control scan.** Return the actual N6/N8 angle and momentum grids, all bandwidth rows, units, source/model hashes, ordered bases and the scan producer. Include the neighboring angle samples and a declared refinement check. A chosen α near 0.586 is not a located magic point, and a sampled minimum is not a certified bracket. Recompute the symmetry residual rather than inheriting a JSON number.
6. **Make every record attributable.** One entrypoint should produce the complete advertised result set from immutable inputs, including structured failures, stopping reasons and per-evaluation records where needed. Never silently carry forward fields that look freshly computed. Report mesh/cutoff sensitivity separately from numerical residuals and physical accuracy.

An honest partial return is acceptable: state which corrections are complete, which remain open, and the exact supported scope. Do not replace missing guards with a larger campaign.

## Relationship to the previous sparse brief

The prior brief is preserved as `FABLE_SPARSE_REQUIREMENTS.md`. This matrix describes what v073p changes; it does not pretend the variant archive was advertised as a sparse repair.

| Prior ID | v073p status | Evidence / implication |
|---|---|---|
| F01 — absolute band identity | Not addressed for sparse mode | `sparse_engine.py` is absent; no sparse band-identity correction or controls supplied. |
| F02 — enforced comparisons | Not addressed for sparse mode | No replacement for the earlier locator policy is included. Variant fast/native mismatch is separately retained as V01. |
| F03 — bounded roots | Not addressed | `fast_engine.py` is unchanged; no new guarded root path is supplied. |
| F04 — state attribution | Not addressed | Earlier locator is absent and fast Newton is unchanged. |
| F05 — complete work accounting | Not addressed for sparse mode | Review adds separate function-entry totals for replay; these are not a repair to the sparse work ledger. |
| F06 — exact finite-model identity | Not addressed | BM changes only its valley argument/wrapper. Earlier index-input handling remains unchanged. Review's ordered bases are supplied separately. |
| F07 — portability | Partial, variant scope only | Provided runner executes from the archive in a clean directory, but it requires an existing chiral result JSON. Missing scan and mirrored producers prevent a complete fresh regeneration. |
| F08 — evidence integrity | Incomplete | Replay loses four valley fields; four chiral metadata fields are inherited. Signed sum and determinant descriptions need correction. |

## Return format

Return an immutable original-input archive, source diff, frozen plan, a completed V01–V07 response matrix with evidence paths, exact model/basis/seed records, all attempted measurements and failures, dependency/thread details, and a clean-extraction log. Figures should read retained records, bind their hashes and show all failed or unresolved cases. Separate any kernel timing from full-path timing with the required checks enabled.

This review does not revoke earlier numerical checkpoints or establish a physical valley disagreement. Its concrete conclusion is that the native exploratory controls are useful, while downstream compatibility and several result-generation claims need correction.
