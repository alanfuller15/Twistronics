# TWISTRONICS LOG — v036 — Second implementation

**Scope.** Item 2 of the reconciliation's recommended order: validate one baseline and one braid flip with a separately implemented Hamiltonian using independently chosen basis, strain and symmetry conventions. **Both reproduce.** The only numerical discrepancy is fully attributed to a physical O(\(\epsilon\)) term the first model omitted, which shifts a gap by 0.23 meV and changes no label. New files: `tbg_ref.py`, `test_tbg_ref.py`, `ref_sanity.py`, `ref_v023.py`, `ref_attrib.py`, `ref_v026.py`, `ref_v026_N6.py`.

**Independence, stated honestly.** Same author, so this is protection against convention and implementation errors, not against a shared conceptual mistake. Every choice below was made to differ from `bm_strain.py` wherever a convention could hide an error.

---

## 1. What is different in `tbg_ref.py`

| aspect | `bm_strain.py` (v023) | `tbg_ref.py` (this entry) |
|---|---|---|
| plane-wave basis | layer-2 grid offset by \(q_1\) | both layers on one absolute grid \(k+G\); layer Dirac points \(K^{(l)}\) inside the intralayer blocks (Koshino-style); different truncation |
| strain geometry | \(K_l=(1-E_l)R\,K\), small-strain | exact \((1+E_l)^{-T}R\) on reciprocal vectors; moiré \(G^M=b^{(1)}-b^{(2)}\) exactly |
| Dirac velocity | isotropic \(\hbar v\) | \(\hbar v\,(1-E_l)R(-\theta_l)\): velocity renormalisation kept (switchable, `vrenorm`) |
| \(C_{2z}T\) real basis | hand-chosen \((1,1)/\sqrt2,\ (i,-i)/\sqrt2\) | built numerically from the antiunitary \(A=S_x\mathcal K\): columns \(v+Av\), \(i(v-Av)\), checked \(A\)-invariant and orthonormal |
| Euler class | \(k_1\)-family of \(k_2\) Wilson loops, winding of the SO(2) angle | plaquette sum of SO(2) rotation angles over the whole BZ (lattice Euler class), with periodic orientation closure on both edges and per-plaquette det |
| node charge | rotation of the eigenvector inside a parallel-transported frame | winding number of \(d=(d_x,d_z)\) of the effective real \(2\times2\) Hamiltonian in a *fixed* real frame |
| node search | grid + Nelder–Mead, threshold on the minimum | same, plus a cone check: the gap must exceed 0.05 meV at distance 0.01 in two directions |

Sanity (unstrained, \(N=4\)): energies at \(K_M\), \(K'_M\), \(\Gamma_M\) equal the v023 values to \(10^{-3}\) meV despite the different truncation; bandwidth 7.43 meV; real-basis residual \(5\times10^{-14}\); plaquette Euler class \(-1.009\) on an \(18\times18\) mesh, closure \((+1,+1)\), all plaquette dets \(+1\).

## 2. v023 baseline (0.3 % strain, \(\phi=0\), \(N=4\))

| quantity | `bm_strain` (v023 §3) | `tbg_ref`, velocity term on | `tbg_ref`, velocity term off |
|---|---|---|---|
| node 1 | (0.75641, 0.60857) | (0.75747, 0.60748) | (0.75641, 0.60857) |
| node 2 | (0.57869, 0.72848) | (0.57970, 0.72740) | (0.57869, 0.72848) |
| bandwidth (meV) | 24.259 | 24.192 | — |
| min remote gap (meV) | 5.458 (\(N=6\): 5.500) | 5.230 (\(N=6\): 5.272) | **5.4580** (\(N=6\): **5.5005**) |
| Euler class | \(-1.000\) (Wilson) | \(-1.012\) (plaquette, \(24\times24\)), closure (0.999, 0.999) | — |
| node charges | same | \((-1,-1)\): **same** | same |

With the velocity term off, the second implementation reproduces the first to every printed digit at both cutoffs. So the two basis conventions agree exactly at fixed \(N\), and the entire discrepancy (0.23 meV in the remote gap, \(1.5\times10^{-3}\) in node position) is the \((1-E_l)\) velocity renormalisation, a genuine O(\(\epsilon\)) correction that `bm_strain` omits. It does not affect any label. **Correction to v023 §2: the model there neglects the strain-induced velocity renormalisation; magnitudes carry an O(\(\epsilon\)) ≈ 4 % uncertainty in remote gaps from that omission alone.** Node positions and topological labels are insensitive to it at 0.3 %.

## 3. v026 braid flip (\(A=0.20\), \(\phi=0\), \(B_{\rm sym}=-0.25\to-0.30\))

Second implementation, effective-2×2 winding estimator:

| \(B_{\rm sym}\) | \(N\) | velocity term | nodes | charges | label | v026 |
|---|---|---|---|---|---|---|
| −0.25 | 4 | on | (0.5160, 0.8276), (0.7442, 0.6123) | \((-1,-1)\) | SAME | SAME |
| −0.30 | 4 | on | (0.5186, 0.8274), (0.7392, 0.6110) | \((+1,-1)\) | OPPOSITE | OPPOSITE |
| −0.25 | 4 | off | (0.5156, 0.8278), (0.7434, 0.6126) | \((+1,+1)\) | SAME | SAME |
| −0.30 | 4 | off | (0.5182, 0.8275), (0.7385, 0.6113) | \((+1,-1)\) | OPPOSITE | OPPOSITE |
| −0.25 | 6 | on | (0.5161, 0.8276), (0.7442, 0.6123) | \((+1,+1)\) | SAME | SAME |
| −0.30 | 6 | on | (0.5187, 0.8274), (0.7392, 0.6110) | \((-1,+1)\) | OPPOSITE | OPPOSITE |

(Global sign per run is a base-orientation convention.) Node positions with the velocity term off match v026's to \(10^{-4}\). The flip is reproduced by a different basis, a different real-structure construction, and a different charge estimator, at two cutoffs.

## 4. Cross-implementation tests

`test_tbg_ref.py` (4 tests, ~11 s): unstrained spectra agree at \(K_M,K'_M,\Gamma_M\) to \(2\times10^{-3}\) meV; strained nodes agree to \(2\times10^{-4}\) with the velocity term off; the velocity term is the only difference in the remote gap (equals 5.458 without it; 0.15–0.30 meV lower with it); plaquette Euler class is \(-1\) unstrained. These run alongside the 17 tests of v034.

## 5. Status of the reconciliation's list

1. Freeze the reconciled package as reference — done on Alan's side; this entry adds to it.
2. **Independent baseline and braid flip — done** (this entry), with the stated same-author limit.
3. Continuous braid-path replay — open. `tbg_ref` now provides a second engine to do it with.
4. Cutoff convergence beyond \(N=6\) for endpoint magnitudes — open.
5. Scoping of conclusions — the v033 statement stands as "selected checkpoint labels reproduced under the gate, now by two implementations for the baseline and the first braid."

## 6. Self-corrections this entry
- The first draft of `tbg_ref.real_basis` contained a leftover placeholder QR line; removed before any run. Recorded because a stray line in a "reference" implementation is exactly what an independent check must not carry.
- v023 §2's model omitted the velocity renormalisation; identified and quantified here (§2), not by the earlier audits.
