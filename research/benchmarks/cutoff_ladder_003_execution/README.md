# CUTOFF-LADDER-003 engine expansion and pilot

Frozen implementation: c38b85452a41e2a8a1a4122e4f655f67a2931248.
Producer: Codex. Independent execution review: PENDING.

## Capability added

Three nested cutoffs at the same momentum coordinates, with adjacent pair/four-state comparisons, full spectra and retained four-state eigenvectors. Cutoffs a/b keep their original definitions (49/77 vectors, dimensions 196/308). New c applies the same seven-displacement neighbor-shell construction once more to b: 111 vectors, dimension 444. Explicit lexicographic indices are frozen in SPEC.json. Its energy-ranked central pair is indices 221/222 (zero based). This is an explicit extension, not a redefinition of the original certification case or a claim of physical band correspondence.

Engine validates exact source bytes against the frozen Git commit, verifies the shell construction, checks nested matrix embeddings, residuals and subspace metrics, and retains runtime wheel provenance. User authorized bounded computation without waiting for independent review. Three sequential jobs of 6/6/5 points, 51 eigensolves; 3 GiB/worker, 64 MiB/file, 90 s/job. Elapsed 6.916757 seconds.

## What changed when compute expanded

At these 17 momentum points, a→b maximum pair angle is 63.605978 degrees, whereas b→c is 0.443801 degrees. Four-state angles decrease from 0.559380 to 0.020922 degrees. Maximum absolute upper-gap change decreases from 7.212637 to 0.025178 micro-eV.

Minimum sampled upper gaps: a 2.153759 micro-eV at offset -5; b 1.583929 at +5; c 1.569143 at +5. Offset unit is 1/131072 in x, at fixed y, with k=xG1+yG2. Agreement improves substantially on this slice; no extrapolation to other momenta or infinite cutoff is made.

Minimum b-pair weight in c-four is 0.9999998792124621. Maximum eigenpair residual 1.61838e-12 meV. Both nested-matrix residuals are zero. All a/b spectra recomputed in this pilot match the previous execution exactly (REGRESSION.json), within a declared comparison threshold 1e-9 meV.

## Evidence and reuse

materialize.py NEW_OUTPUT --repo PATH restores all saved bytes, verifies SHA-256 and invokes the frozen metric replay without physical solves. analyze.py NEW_OUTPUT derives SUMMARY.json and cutoff-ladder.png. The figure plots actual computed momentum samples, not a time trajectory. Raw vectors, spectra, logs, receipts and provenance are in the parts archive. Independent review is requested against the exact execution commit; neither PR is merged.

The next expansion can use this third-cutoff capability on a small two-dimensional neighborhood around the shared gap minimum, then add another shell if changes warrant it.
