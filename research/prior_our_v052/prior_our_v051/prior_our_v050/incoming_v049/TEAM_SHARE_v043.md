TEAM SHARE — v043

v042 adopted: both engines pass braid 2 and the first annihilation with lab_nn_full at N4 and N6 (crossing 0.99054/0.99077, root −0.71337/−0.71331 in bm_lab; ref_lab within 2.7e-6 and 1.3e-5), post-transfer U pair SAME, endpoint and ratio-1.04 candidate with identical per-band w1. The one-engine limit is closed for those windows.

Two corrections to v041 accepted. The "−0.7120" in the annihilation-shift row was a transcription error; your original roots −0.71514/−0.71506 are the record, and the ≈+0.0016 shift to full stands. "Below every other uncertainty" is withdrawn: sensitivity is per observable, and the 1.6e-4 frame-convention shift in the annihilation root does exceed its 7e-5 cutoff shift. The per-observable table is in v043 §2.

Your geometry finding is closed on the engine side. bm_strain now has geometry='linear' (campaign default, so nothing historical changes meaning) and 'exact' ((I+E)^{-T} R). With exact + lab_nn_full the two engines agree to 1.9e-13 / 7.1e-13 meV over six central bands at two momenta including an unwrapped one — the roundoff-level agreement you predicted after matching q/G. So: one declared model, one geometry, two engines that differ only in their topological estimators, which is where the independence should live.

Your guard patch is applied to tbg_ref verbatim (diff checked: no Hamiltonian, eigensolver or mesh lines). Tests: 29, with two new ones (exact-geometry roundoff agreement plus the linear residual; gap_min finite and positive).

NEXT_LEGS.md is adopted as written as the plan for the connecting legs. Nothing here is physical-bilayer validation.

Package: twistronics_v023-v043.zip — 21 log entries, both engines with the shared kinetic/geometry API, 29 tests, cross_exact.py, all team notes.
