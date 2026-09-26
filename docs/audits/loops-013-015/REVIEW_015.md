[CODEX][REVIEW] CUTOFF-E-015 — **numerical PASS; interpretation correction requested**

**Reviewed execution:** `4445bddae841373db5b049fe423b7d3f09c5e883`  
**Frozen producer implementation:** `8cba7ef0f07d099c57d03b3efdba8aae49bb0512`  
**Review evidence:** `docs/audits/loops-013-015/authorized-execution/` in the commit containing this review  
**Frozen reviewer runner:** `d0ac63cbb700c6025c4ffa536bf44518e6dace0c`

Claude produced this run; Codex independently reviewed it. All producer source bindings and packet hashes match. Producer zero-solve replay reproduces MAP, REGRESSION, HOLONOMY and SUMMARY byte-identically (40 files).

I independently recomputed **all 41 cutoff-e points** with NumPy eigh, using the explicitly shared reviewed coefficient assembly (producer used SciPy evr). This is a new-cutoff recomputation, not a claim to have independently recomputed the other cutoffs or the Hamiltonian implementation. All retained spectra, four-state vectors, receipts and source bindings are packaged.

| Comparison with producer | Maximum difference (meV) |
|---|---:|
| Full spectrum | 9.095e-12 |
| Lower/upper external gaps | 3.652e-12 |
| Independent eigenpair residual | 1.404e-12 |

Exact loop geometry and closure checked independently. Own overlap products match every tested sign, determinant and minimum link singular value; explicit sign flips, reflections and reversal preserve signs. The added zero-solve verifier rechecks all spectra against producer states, every receipt, native-wheel binding and exact geometry; it does not change the frozen physical runner.

Runtime independently reconstructs e = sorted(set(d + b-stencil)): 197 vectors, dimension 788, pair [393,394]. The nine-point patch and 32-point R3 loop match their exact source geometry.

All four e cutoff/group entries agree: hi/hi+1/pair −1, four +1. Independent hi determinant **-0.759231240**, minimum link σ **0.954244340**. The center upper gap is **5.68615022e-06 µeV** in my solve.

The independent e gap² fit is positive definite with its stationary point inside the patch, at offsets (-3.02142415e-05, -0.000110525574) in 2⁻²² steps.

**Required wording correction:** “zero at double precision” is not an accurate description of the retained fitted minima. The raw b/c/d/e fitted minima are approximately −1.33e−9, −5.65e−12, −1.66e−14 and −2.64e−12 µeV², with fit residuals about 1.9–2.0e−9 µeV². My independent e fit instead gives +1.074e-11 µeV². These small, sign-changing fit values carry no resolved physical minimum-gap information. Use **“consistent with zero within the descriptive fit residual”**, and do not infer exact closure or a gap floor. Preserve the raw signed fits.

The successive **upper-gap differences** decrease by factors about 834 and 1127 for b→c→d→e on this patch. That ratio applies to this gap metric; it is not a universal rate for subspace angles or proof of infinite-cutoff convergence. Accepted overall reading: **finite-cutoff sampled evidence consistent with an R3 candidate external touching, with the negative discrete loop sign persisting at e**.

Audit execution: one authorized corrected launch, unchanged schedule, **601 solves / 101 jobs total** across 013–015; all NORMAL_EXIT and empty process groups, ≤6 points/job, one thread, locked wheel. Wall time 253.03s; longest job 3.78s. The failed first preflight remains verbatim in the prior evidence; it made zero physical calls (its recorded six was a scheduled count). No physical job was retried.

Restore and verify: `python docs/audits/loops-013-015/materialize_authorized.py /new/output` in the evidence checkout. All **511 files** restore exactly; REVIEW and VERIFICATION re-derive byte-identically with zero physical eigensolves.

No certified touching, node count, charge, partner correspondence, continuous isolation or infinite-cutoff claim. Both PRs remain unmerged. No 013–015 site promotion is authorized by this review; the site stays at v28 pending a separate request.
