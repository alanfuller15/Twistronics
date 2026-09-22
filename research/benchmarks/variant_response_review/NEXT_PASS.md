# Fable — focused next pass after v074p

The valley correction is effective. Preserve it: the native/fast matrices, energies, projected derivatives and frame projectors pass all 18 review cases, and the six sparse valley samples also agree. The complete producers are a meaningful improvement: all advertised JSON fields now regenerate and the 16-row bandwidth scan is backed by 1,600 retained spectra.

Prioritize the remaining implementation contracts before another numerical expansion.

## 1. Make the measured path match the declared path

Pass an explicit loop start angle or complete loop coordinates through `pair_charges` into `node_winding`. For a negative start offset, the first loop point must coincide with the frame's base point and the second loop must start exactly at the transported endpoint. If a connecting path is intended, make it explicit and measure it; do not identify frames at different points with an unqualified determinant of their overlap.

Return the K and K′ node coordinates, ordered seeds, refined gaps, periodic images, both loop coordinate arrays and the transport coordinates. Refine/check both K′ nodes. Current second-center gaps are about 0.0362 and 0.0386 meV. Those values do not prove a contour misses a node, but the centers cannot be treated as verified roots.

Keep the successful reproduced labels as historical measurements. Do not call a new result fully mirrored until the actual coordinate arrays, frame transport and finite-basis sewing satisfy the declared comparison. Include root, overlap, isolation, loop/transport mesh and radius checks.

## 2. Turn topology diagnostics into acceptance rules

- Enforce a finite positive external-gap threshold; `gap_tol` currently has no effect.
- Check minimum singular values for every frame link and both sewing directions before forming a Wilson result. Reject singular/nonfinite links; use refinement to resolve uncertain links.
- Apply a nonzero overlap rule to single-band sign transport as well as a band-gap rule. The smooth four-band control in `probes.py` has a 2 meV gap and zero adjacent overlap, yet returns normally.
- Handle both available external neighbors independently, including the highest pair. Return explicit not-applicable status only when an external neighbor genuinely does not exist.
- Retain the negative controls and structured rejection reasons. Do not relabel diagnostic-only outputs as accepted topology.

The reality and sampled-degeneracy refusals now work; keep those tests. Valid integer pair selection and range checking also work. A broader input policy should reject fractional band indices rather than silently truncating them.

## 3. Correct the sparse inertia claim before using it as a gate

The bundled `_fact` returns inertia 0 for `[[0,1],[1,0]]` at zero shift, despite its exact negative eigenvalue. The row and column permutations differ. The diagonal of a general pivoted LU U factor is not a justified inertia certificate.

Correct the method and show rejection or a correct count for this counterexample. Use a supported symmetric-indefinite factorization/count with justified numerical checks, or explicitly enforce dense ordered-band comparison for the narrowed supported mode. Ordinary floating-point agreement is not verified arithmetic. Remove “PROVED” and “closes F01–F06” until their requirements are actually satisfied. The successful valley samples remain useful; they do not close general band identity or the earlier sparse root/accounting contracts.

## 4. Generate the narrative from its records

The chiral prose says overlap 0.73, sewing 0.014 and external gap 5.3 meV; its own JSON and replay give 0.995703421, 0.0022690735 and 101.8343329 meV. Bind each summary to a model and evidence path. The approximately 5.3 meV values belong to the strained valley baseline.

Keep the signed claim withdrawn. Clarify the reference: the PRX abstract says +2e₂, but its equations (19) and (31) give −2e₂, matching the arXiv equation. This is not a clean version-level convention change. Specify the exact equation and derive the code's convention before a signed numerical comparison.

## Return package

Return a short V01–V07 response matrix, unchanged original inputs, exact source diff, frozen acceptance rules, all model/basis identities and coordinate paths, per-evaluation records, rejection cases, a source-bound narrative and figures, and a clean-extraction log. Distinguish completed corrections from exploratory output and from claims requiring a later scientific campaign. The next pass can be narrow; close these contracts before expanding cutoffs or scans.
