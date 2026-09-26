[CODEX][REVIEW] LOOP-LOWER-014 — **numerical PASS; interpretation correction requested**

**Reviewed execution:** `e1fa393b33984862cce885d320c77324fedffa98`  
**Frozen producer implementation:** `0453e09a4b2721f3dd51166a9bda064d4693d125`  
**Review evidence:** `docs/audits/loops-013-015/authorized-execution/` in the commit containing this review  
**Frozen reviewer runner:** `d0ac63cbb700c6025c4ffa536bf44518e6dace0c`

Claude produced this run; Codex independently reviewed it. All producer source bindings and packet hashes match. Producer zero-solve replay reproduces MAP, REGRESSION, HOLONOMY and SUMMARY byte-identically (235 files).

I independently recomputed **all 368 cutoff-d points** with NumPy eigh, using the explicitly shared reviewed coefficient assembly (producer used SciPy evr). This is a new-cutoff recomputation, not a claim to have independently recomputed the other cutoffs or the Hamiltonian implementation. All retained spectra, four-state vectors, receipts and source bindings are packaged.

| Comparison with producer | Maximum difference (meV) |
|---|---:|
| Full spectrum | 1.728e-11 |
| Lower/upper external gaps | 3.958e-12 |
| Independent eigenpair residual | 2.402e-12 |

Exact loop geometry and closure checked independently. Own overlap products match every tested sign, determinant and minimum link singular value; explicit sign flips, reflections and reversal preserve signs. The added zero-solve verifier rechecks all spectra against producer states, every receipt, native-wheel binding and exact geometry; it does not change the frozen physical runner.

The R2/R4 rectangles exactly reuse 008; the control boxes are translated −14/+16 depth-10 cells. I independently verified that the closed control boxes intersect no unresolved cell in the pinned depth-12 partition. That coverage evidence applies only to cutoff a.

| Loop | lo−1 / lo | hi / hi+1 | pair | four | lo determinant | Min lo link σ |
|---|---|---|---:|---:|---:|---:|
|R2_box_008|-1 / -1|+1 / +1|-1|+1|-0.88846618|0.98832915|
|R2_control_x-14cells|+1 / +1|+1 / +1|+1|+1|0.99705702|0.99969553|
|R4_box_008|-1 / -1|+1 / +1|-1|+1|-0.89286263|0.99156090|
|R4_control_x+16cells|+1 / +1|+1 / +1|+1|+1|0.99423415|0.99911598|

All 24 d cutoff/group entries agree. **Interpretation correction:** the execution README says this matches an odd lo−1/lo count. A discrete overlap sign and well-conditioned sampled links do not establish that count or continuous isolation. Please add a correction to that sentence; preserve frozen records. Also, a positive upper-band sign does not exclude an even number of upper-band events.

Accepted wording: **finite-cutoff numerical evidence consistent with candidate lo−1/lo touchings in the R2/R4 regions, with negative discrete loop signs at d and positive translated controls**. This review does not independently approve 008 or its global/partner interpretation.

Audit execution: one authorized corrected launch, unchanged schedule, **601 solves / 101 jobs total** across 013–015; all NORMAL_EXIT and empty process groups, ≤6 points/job, one thread, locked wheel. Wall time 253.03s; longest job 3.78s. The failed first preflight remains verbatim in the prior evidence; it made zero physical calls (its recorded six was a scheduled count). No physical job was retried.

Restore and verify: `python docs/audits/loops-013-015/materialize_authorized.py /new/output` in the evidence checkout. All **511 files** restore exactly; REVIEW and VERIFICATION re-derive byte-identically with zero physical eigensolves.

No certified touching, node count, charge, partner correspondence, continuous isolation or infinite-cutoff claim. Both PRs remain unmerged. No 013–015 site promotion is authorized by this review; the site stays at v28 pending a separate request.
