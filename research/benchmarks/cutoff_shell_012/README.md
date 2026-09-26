# CUTOFF-SHELL-012

Fourth nested cutoff d: apply the same seven-displacement b stencil once more
to cutoff c, deduplicate and sort lexicographically. 151 reciprocal indices,
604×604 matrix, central selected pair [301,302] (zero-based). Original a/b/c
are unchanged. Index-based band correspondence is diagnostic, not certified.

Two 3×3 exact-rational patches at step 2⁻²², centered on the rounded c candidate
from NODE-WINDING-006 (R3) and PARTNER-WINDING-011 (R1). 18 coordinates: 16 new,
two centers repeated for a/b/c regression. Four cutoffs: **72 eigensolves** in
three sequential jobs of six points. Bounds: 90 s/job, 600 s summed, 3 GiB
address space per worker, 64 MiB/file, one thread. No adaptive points/retries.

Engine upgrade: four-cutoff nested assembly/embedding checks and adjacent
a→b→c→d pair/four-state comparisons; two-patch summaries and descriptive
nine-point quadratic gap² fits. Fit extrema outside a patch are flagged.
Fits do not certify zeros or bound an unresolved gap. Two patches and four
finite cutoffs do not establish global behavior or infinite-cutoff convergence.

Computation is independently authorized; no audit gate. Original engine and
execution records remain immutable. Previous LOOP-ROBUSTNESS-007 now has
Claude PASS in PR #2 comment 5843439638, reviewed execution cbb3bf73a3e17a8a76733969d92cee973e100304.
