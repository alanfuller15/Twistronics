TEAM SHARE — v045

Two toolkit-side open items closed.

Tunnelling strain law. In BM the interlayer amplitude is the hopping function at the common momentum of the two coupled states, which sits at the mean of the two layers' K_j magnitudes. Under heterostrain (E_l = ∓E/2) that mean shift is zero, so δw_j/w_j = κ·ε̄_j vanishes at first order; only homostrain modulates w0,w1 at O(ε). Implemented in bm_strain as w_mode='average' (declared law; T_j unchanged to 1e-12 at κ=±5) and w_mode='layer1' (cancellation off, worst-case bound). Worst case at |κ|=5: T_j scaled ≤0.75%, baseline remote gap ±7% (4.97 → 5.34 / 4.62 meV), nodes ±4e-3, no label change; braid-1 window still SAME→OPPOSITE at both signs. The physical κ for a given t(q) is not asserted; it isn't needed for any conclusion.

Endpoint cutoff. Minimisers located at N=6, refined locally at N=8 (dim 1060), tbg_ref lab_nn_full: lower|flat1 23.18139, flat 2.77665, flat2|upper 3.39253, upper|next 10.85609 meV. N=6→8 changes ≤1e-4 meV, minimisers unchanged to 1e-5. So the endpoint is converged at N=6; quote N=6 magnitudes, treat N=4 as ~0.1 meV. Local convergence at located minima, not a global N=8 search.

30 tests (one new: exact first-order cancellation and the worst-case bound).

Remaining: your braid-1 path with deepening/un-linking from the v044 anchors, and the post-braid-2 cleanup. After those, one declared model, two engines, end to end. Nothing here is physical-bilayer validation.

Package: twistronics_v023-v045.zip.
