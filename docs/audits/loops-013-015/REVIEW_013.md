[CODEX][REVIEW] LOOP-CUTOFF-D-013 — **PASS**

**Reviewed execution:** `76dadaf9478bbb8e99ee26ada6b5ff046fc1628a`  
**Frozen producer implementation:** `7635c8586e13865487b396ea21ec7d274c13976e`  
**Review evidence:** `docs/audits/loops-013-015/authorized-execution/` in the commit containing this review  
**Frozen reviewer runner:** `d0ac63cbb700c6025c4ffa536bf44518e6dace0c`

Claude produced this run; Codex independently reviewed it. All producer source bindings and packet hashes match. Producer zero-solve replay reproduces MAP, REGRESSION, HOLONOMY and SUMMARY byte-identically (165 files).

I independently recomputed **all 192 cutoff-d points** with NumPy eigh, using the explicitly shared reviewed coefficient assembly (producer used SciPy evr). This is a new-cutoff recomputation, not a claim to have independently recomputed the other cutoffs or the Hamiltonian implementation. All retained spectra, four-state vectors, receipts and source bindings are packaged.

| Comparison with producer | Maximum difference (meV) |
|---|---:|
| Full spectrum | 6.821e-12 |
| Lower/upper external gaps | 2.927e-12 |
| Independent eigenpair residual | 1.124e-12 |

Exact loop geometry and closure checked independently. Own overlap products match every tested sign, determinant and minimum link singular value; explicit sign flips, reflections and reversal preserve signs. The added zero-solve verifier rechecks all spectra against producer states, every receipt, native-wheel binding and exact geometry; it does not change the frozen physical runner.

At cutoff d, hi/hi+1/pair signs are negative on full- and half-radius loops at both candidates, positive on both translated controls; all four-state signs are positive.

| Loop | hi sign | hi determinant | Min link σ |
|---|---:|---:|---:|
|R1_offnode_xplus4r_32|+1|0.98959001|0.99844743|
|R1_r1_32|-1|-0.83198654|0.98509621|
|R1_rhalf_32|-1|-0.83198647|0.98507815|
|R3_offnode_xplus4r_32|+1|0.96083208|0.99377196|
|R3_r1_32|-1|-0.75923124|0.95424437|
|R3_rhalf_32|-1|-0.75923124|0.95424218|

All 24 d cutoff/group entries agree. The full/half-radius geometry and +4-radius translations reproduce exactly. Accepted wording: **finite-cutoff numerical evidence consistent with candidate external touchings at R3 and R1, with negative discrete real-overlap signs on these sampled loops, persisting at cutoff d while translated controls are positive**. The 0.5 link threshold is discrete conditioning only.

Audit execution: one authorized corrected launch, unchanged schedule, **601 solves / 101 jobs total** across 013–015; all NORMAL_EXIT and empty process groups, ≤6 points/job, one thread, locked wheel. Wall time 253.03s; longest job 3.78s. The failed first preflight remains verbatim in the prior evidence; it made zero physical calls (its recorded six was a scheduled count). No physical job was retried.

Restore and verify: `python docs/audits/loops-013-015/materialize_authorized.py /new/output` in the evidence checkout. All **511 files** restore exactly; REVIEW and VERIFICATION re-derive byte-identically with zero physical eigensolves.

No certified touching, node count, charge, partner correspondence, continuous isolation or infinite-cutoff claim. Both PRs remain unmerged. No 013–015 site promotion is authorized by this review; the site stays at v28 pending a separate request.
