# TWISTRONICS LOG — v045 — Tunnelling strain law; cutoff convergence of the endpoint

**Scope.** The two open items that belong to the toolkit side rather than the path-replay harness: (a) a named strain dependence for the interlayer amplitudes \(w_0,w_1\), with its first-order result derived and its worst-case sensitivity measured; (b) the endpoint gaps at \(N=8\). **Result: to first order, heterostrain does not modulate \(w_0,w_1\) at all; the worst-case bound moves magnitudes by ≤7 % and no label; the endpoint gaps are cutoff-converged at \(N=6\) to \(10^{-4}\) meV.** New: `bm_strain.py` (`w_kappa`, `w_mode`), `w_strain_sens.py`, `endpoint_locate.py`, one regression test (30 total).

---

## 1. The tunnelling strain law

In the Bistritzer–MacDonald construction the interlayer matrix element between a layer-1 state at momentum \(\mathbf k+\mathbf G_1\) and a layer-2 state at \(\mathbf k'+\mathbf G_2\) is \(t(|\mathbf k+\mathbf G_1|)\,\delta_{\mathbf k+\mathbf G_1,\,\mathbf k'+\mathbf G_2}\): the hopping function is evaluated at the *common* momentum of the two coupled states. Near the valley that common momentum lies, to first order, at the mean of the two layers' \(K_j\) magnitudes. Under heterostrain \(\mathbf E_l=\mp\mathbf E/2\) those magnitudes shift by \(\mp\tfrac12\hat e_j\!\cdot\!\mathbf E\hat e_j\) and the mean shift vanishes. So

$$ \frac{\delta w_j}{w_j}=\kappa\,\bar\epsilon_j,\qquad \bar\epsilon_j=\tfrac12\sum_l \hat e_j\!\cdot\!\mathbf E_l\hat e_j=0\quad\text{for pure heterostrain}, $$

with \(\kappa=-\,d\ln t/d\ln q\) at the valley momentum. First-order modulation of \(w_0,w_1\) is a homostrain effect; heterostrain enters the tunnelling only through the \(q_j\) geometry the model already carries, and through \(O(\epsilon^2)\approx10^{-5}\) terms. This is the declared law, implemented as `w_mode='average'`. `w_mode='layer1'` evaluates the layer-1 strain alone, switching the cancellation off, as a worst-case bound; \(\kappa\) is a declared coefficient. (The physical \(\kappa\) for a given \(t(q)\) parametrisation, e.g. Koshino's, is of order a few; it is not needed for the conclusions below and is not asserted here.)

## 2. Sensitivity (\(N=4\), `lab_nn_full`, exact geometry, 0.3 %, \(\phi=0\))

| mode | \(\kappa\) | \(T_j\) scale | nodes | remote gap (meV) | label |
|---|---|---|---|---|---|
| average | 0, ±5 | 1.00000 (all \(j\)) | (0.5816, 0.7266), (0.7594, 0.6066) | 4.9709 | same |
| layer1 | +5 | 0.9925, 0.9990, 0.9990 | shift \(4\times10^{-3}\) | 5.3378 | same |
| layer1 | −5 | 1.0075, 1.0010, 1.0010 | shift \(4\times10^{-3}\) | 4.6215 | same |

Braid-1 window, worst case \(\kappa=\pm5\): SAME at \(B_{\rm sym}=-0.25\), OPPOSITE at \(-0.30\), both signs. The tunnelling-law item is therefore closed as a bounded sensitivity: \(\lesssim7\,\%\) on remote-gap magnitudes under an implausibly large modulation, zero at first order for the physical case, no label anywhere.

## 3. Endpoint gaps at \(N=8\)

Minimisers located at \(N=6\) by bounded multistart, then refined locally at \(N=8\) (dim 1060) from those points; `tbg_ref`, `lab_nn_full`, \((A,B_{\rm sym},B_\tau,\phi,w_0/w_1)=(-0.30,-0.40,-1.8,80^\circ,1.10)\):

| gap | \(N=4\) (v042) | \(N=6\) | \(N=8\) | minimiser (\(N=8\)) |
|---|---|---|---|---|
| lower – flat\(_1\) | 23.0292 | 23.18135 | **23.18139** | (0.99073, 0.28845) |
| flat | 2.8699 | 2.77673 | **2.77665** | (0.67678, 0.91888) |
| flat\(_2\) – upper | 3.3354 | 3.39250 | **3.39253** | (0.61233, 0.92216) |
| upper – next | 10.8216 | 10.85609 | **10.85609** | (0.19900, 0.75171) |

\(N=4\to6\): up to 0.15 meV. \(N=6\to8\): \(\le1\times10^{-4}\) meV, minimisers unchanged to \(10^{-5}\). The endpoint is cutoff-converged at \(N=6\); \(N=4\) values carry a ~0.1 meV cutoff error and the \(N=6\) ones are the quotable magnitudes. This is local convergence at the located minima, not a global re-search at \(N=8\).

## 4. What remains open

Model-side: nothing named. Numerical: none of the path replays has been run above \(N=6\) (labels have been cutoff-stable at every checkpoint so far). Harness-side (team): braid-1 path with deepening/un-linking from the v044 anchors; post-braid-2 cleanup to the endpoint. Then the campaign is connected end to end under one declared model. Physical-bilayer validation (relaxation, experiment) is outside this project's scope and stays so.

## 5. Self-corrections this entry
- First \(N=8\) attempt used the seam-seeded global multistart and timed out at dim 1060; replaced by locate-at-\(N=6\), refine-at-\(N=8\), which is the right tool for convergence and is stated as such.
- v038 §5 said the tunnelling strain dependence "remains unmodelled"; it now is, and the first-order answer is that for heterostrain there was nothing to model.
