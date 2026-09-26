# STATE-COMPARISON-001 — blocked pending independent pre-execution review

Question: at the64 already sampled narrow-gap coordinates, how much do the selected electron-state subspaces change when cutoff a grows to cutoff b? This is a new observable map, not more coverage refinement.

## Frozen pilot

Eight actual jobs, each8 paired coordinates and16 Hamiltonian eigensolver starts;128 starts total. Maximum2 workers,90s/job,600s/batch,3GiB/process,64MiB/file, no retry or adaptive points. Same case,128-bit Arb assembly converted to midpoint real matrices, exact locked python-flint0.9.0 wheel and reviewed source dependencies. No physical calls have been made for this packet.

Coordinates are copied unchanged from THREE-FRONT-001. REFERENCE.json extracts four central eigenvalues and the upper gap from the audited SPECTRA.json at execution3f52be02cf0dd27ac1d6c1cece8d45045358f2b4; it records the complete source file SHA256. Worker recomputation must reproduce these selected energies to1e-9meV.

## Comparison and checks

Basis rows are `2*layer*nG + 2*index_position + real_component`, as in the reviewed real-basis assembly. Exact reciprocal index, layer and real component match between49 and77 retained reciprocal indices. Zero-padding is an isometry from196 to308 rows. Every paired point checks `H_b[embedding,embedding] == H_a` numerically to1e-10meV; this is not an exact assembly proof.

Selected pair: a[97,98] vs b[153,154], zero-based. Surrounding group: a[96:100] vs b[152:156]. Both groups are fixed before seeing results; no best-match search or reordering after execution. The full eigenvalue lists and four eigenvectors per cutoff are retained.

For each group report:

- Singular values of the cross-overlap matrix, including its minimum; larger values mean more similar subspaces.
- Principal angles (SciPy's stable subspace_angles routine), invariant under sign choices and rotations within each group.
- Frobenius distance between the embedded projectors.
- Mean and maximum weight of the larger-model group outside the smaller retained basis. This describes added components, not a physical escape probability.
- External gaps on both sides of each group, so weak boundary separation can be seen rather than hidden.
- Signed change in the selected upper energy gap, b−a inμeV.

Weak pair overlap with strong four-state overlap would be consistent with mixing within the larger group; it would not prove a unique band correspondence. Similar subspaces at64 points would not prove behavior between points, stability at larger cutoffs, or a topological class. Degeneracy at a group's boundary can make its selection ambiguous: interpret overlaps alongside external gaps. No arbitrary similarity threshold is called a scientific PASS.

## Execution gate

Both `run` and direct `worker` modes refuse missing, non-PASS, wrong-reviewer or wrong-commit receipts before assembly/physical solves. The receipt is a transcription of an actual Claude PR2 review; the runner validates its fields, not GitHub authorship. Codex must fetch and verify the real review before creating it. Do not fabricate a receipt. Required fields: reviewer CLAUDE, verdict PASS, reviewed_commit equal to the exact40-character implementation SHA, and the matching PR2 issue-comment URL. Store the complete review text alongside these fields when recording the real review.

```sh
python research/benchmarks/state_comparison_001/run.py controls
# Only after Claude's real pre-execution PASS on FULL_SHA:
python research/benchmarks/state_comparison_001/run.py run --commit FULL_SHA --review /verified/REVIEW_RECEIPT.json --wheel /locked/wheel.whl --output /new/state-map
python research/benchmarks/state_comparison_001/run.py replay --commit FULL_SHA --output /new/state-map
python research/benchmarks/state_comparison_001/plot.py /new/state-map/MAP.json /new/state-map/state-map.png
```

The supervisor copies the review receipt; workers bind its hash in results. Each job retains all spectra/four-state vectors, metrics, exact coordinates, numerical residuals, wheel-native inventory, source commit, output hashes and termination receipt. Replay verifies all bytes/receipts and recomputes metrics from retained vectors without physical solves. Floating derived metrics compare at absolute1e-10, angles at1e-7degrees, with zero relative tolerance; this is a numeric replay, not a promised byte-identical cross-platform SVD. Producer-only matrix residual checks are retained, not independently reassembled in replay. Fresh point recomputation remains an independent-review task.

`plot.py` makes four sampled views: pair similarity, four-state similarity, pair added-component weight, and signed gap change. Similarity/weight scales are fixed0–1; gap change uses a symmetric zero-centred scale. It displays discrete samples without interpolation. The horizontal coordinates are fractional reciprocal coordinates, not an assertion of orthogonal physical axes. numpy/scipy required; matplotlib only for plotting. Runtime python-flint setup uses the locked wheel exactly as the reviewed predecessor.

Claim ceiling: approximate finite-model sampled diagnostics. No certified correspondence, cell-wide bounds, cutoff convergence, topology, seam, experiment or accepted area. The website is unchanged. Neither PR may be merged by this workflow.
