# TWISTRONICS LOG — v023

**Scope of this entry.** Independent re-check of the v022 checkpoint (Dirac-node steering under \(\mathcal P\) breaking, Euler obstruction, remote-band escape route). The v022 numbers were produced by code that no longer exists, with an unstated perturbation. Everything below was recomputed from scratch in a new, fully specified strained Bistritzer–MacDonald model (`v023_code/`), so the *phenomena* are reproduced independently but the v022 *numbers* are not expected to match. Prior entries are unchanged; this is an append.

---

## 1. Corrections to v022

**C1 — The literature claim is verified (with a sign-convention footnote).**
Ahn, Park & Yang, *Phys. Rev. X* **9**, 021013 (2019): a real two-band system with Euler class \(e_2\) has band crossings whose winding numbers sum to \(2e_2\), so the Nielsen–Ninomiya pairing fails. The published PRX abstract writes \(+2e_2\); the arXiv v5 abstract (1808.05375) writes \(-2e_2\). Orientation convention only; it is the same statement v022 already noted as "(+1,+1) or (−1,−1) depending on convention".

**C2 — v022's remote-gap numbers were taken at \(N=4\) immediately after arguing that \(N=4\) can't be trusted at large perturbation.** Resolved here: for a *bounded* first-harmonic perturbation the \(N=4\) results agree with \(N=6\) to \(\lesssim1.5\%\) in the remote gap and to \(\sim10^{-4}\) in node position (Section 4). So the v022 methodological objection applies to the unbounded \(p^2\) knob, not to bounded perturbations. The qualitative v022 conclusion stands; its quoted values (0.146 meV, \(6\times10^{-8}\) meV, \(d_{\rm nodes}=0.139\)) remain unreproducible because the perturbation was never written down. **Rule going forward: every perturbation is logged as an explicit matrix in the plane-wave basis, or the result is not logged.**

**C3 — "Nodes move toward one another" is perturbation-specific, not general.** With the bounded scalar moiré harmonic used here, the two nodes drift *apart* slightly (separation \(0.213\to0.227\) in fractional BZ units over \(A\in[-0.15,+0.15]\)) while the remote gap closes. The robust statement is weaker and cleaner: **the nodes stay exact and barely move; the remote gap is what collapses.**

**C4 — Mechanism sharpened.** Once the remote gap closes, the flat–remote touching is an *exact* real Dirac crossing (\(\Delta_{\rm remote}\sim10^{-9}\) meV at both \(N\)), i.e. nodes appear in the adjacent gap. With nodes in the adjacent gap, the flat-gap node charges become non-Abelian (frame/quaternion charges: Wu, Soluyanov & Bzdušek, *Science* 2019; Bouhon et al., *Nat. Phys.* 2020) and braiding around adjacent-gap nodes can flip the relative sign of the flat-gap pair. "Remote-band incorporation" (v022) is the necessary door; braiding is the mechanism. What is actually observed past closure is pair *creation* in the flat gap (2 → 4 nodes), not annihilation.

**C5 — Direct numerical confirmation of same-handedness**, not just by citation: each Dirac node's real-frame winding was measured in a single orientation-consistent gauge and both are \(+1\) (or both \(-1\)), sum \(=\pm2=2e_2\). Section 5.

---

## 2. Model and conventions (all stated; see `bm_strain.py` docstring)

| item | value |
|---|---|
| \(a\), \(\hbar v\) | 2.46 Å, 5.944 eV·Å |
| \(w_1\) (AB), \(w_0/w_1\) | 110 meV, 0.8 |
| \(\theta\) | 1.05°, layers rotated \(\mp\theta/2\); valley \(K\) |
| heterostrain | \(E_l=\mp E/2\), \(E=\epsilon\,[\cos^2\phi-\nu\sin^2\phi,\ (1+\nu)\sin\phi\cos\phi;\ \cdot,\ \sin^2\phi-\nu\cos^2\phi]\), \(\epsilon=0.003,\ \phi=0,\ \nu=0.16\) |
| pseudo-gauge | \(A_l=\frac{\sqrt3\beta}{2a}(E_{l,xx}-E_{l,yy},\,-2E_{l,xy})\), \(\beta=3.14\) (Bi–Yuan–Fu form) |
| geometry | \(q_j=K^{(1)}_j-K^{(2)}_j\), \(K^{(l)}_j=(1-E_l)R(\theta_l)C_3^{\,j-1}K_D\); \(G_1=q_2-q_1,\ G_2=q_3-q_1\) |
| basis | \(|G|\le N|G_1|\); layer-2 momenta offset by \(q_1\) |
| \(\mathcal P\)-breaking knob | \(V(\mathbf r)=A\,w_1\sum_{j=1}^{3}\cos(\mathbf G_j\!\cdot\!\mathbf r)\ \mathbb 1_{\rm sub}\otimes\mathbb 1_{\rm layer}\) — bounded (nearest harmonics only), real, even, layer-symmetric ⇒ preserves \(C_{2z}T\), breaks BM \(\mathcal P\) |
| \(C_{2z}T\)-breaking knob | \(m\,\sigma_z\) (uniform) and \(m\,\tau_z\sigma_z\) (layer-antisymmetric; this one preserves \(\mathcal P\)) |

\(C_{2z}T\) acts as \(\sigma_x\mathcal K\) on every plane-wave component. Basis \(e_1=(1,1)/\sqrt2,\ e_2=(i,-i)/\sqrt2\) per sublattice pair makes \(H\) real symmetric (checked: \(\max|{\rm Im}\,H_R|<10^{-9}\)). Flat bands = the two eigenvalues straddling index \(D/2\). Nodes found by Nelder–Mead refinement of local minima of \(\Delta_{\rm mid}\) on a \(15\times15\) fractional grid.

Sanity: unstrained \(\theta=1.05^\circ\) gives flat bandwidth 7.43 meV, exact nodes at \(K_M=(0,0)\) and \(K'_M=(\tfrac13,\tfrac13)\), \(\Gamma_M\) remote gap 20.4 meV.

---

## 3. Baseline at 0.3 % strain — cutoff convergence

| \(N\) | dim | bandwidth (meV) | node 1 (frac) | node 2 (frac) | \(\Delta_{\rm mid}\) | \(\Delta^{\min}_{\rm remote}\) (meV) |
|---|---|---|---|---|---|---|
| 3 | 116 | 24.267 | (0.75646, 0.60863) | (0.57859, 0.72784) | \(10^{-10}\) | 5.479 |
| 4 | 196 | 24.259 | (0.75641, 0.60857) | (0.57869, 0.72848) | \(10^{-10}\) | 5.458 |
| 5 | 308 | 24.260 | (0.75646, 0.60859) | (0.57874, 0.72848) | \(10^{-10}\) | 5.500 |
| 6 | 452 | 24.260 | (0.75646, 0.60859) | (0.57874, 0.72848) | \(10^{-10}\) | 5.500 |
| 7 | 604 | 24.260 | same | same | \(10^{-10}\) | 5.500 |

Converged at \(N\ge5\); \(N=4\) is within 0.8 % on the remote gap and \(10^{-4}\) on node position. Node separation \(0.215\) (frac), \(0.25\,k_\theta\). Local remote separations at the nodes: 24.3 and 26.1 meV; the global minimum (5.5 meV) sits near \(\Gamma_M\) at \((0.680,0.742)\). Strain alone has already eaten most of the isolation.

---

## 4. Bounded \(\mathcal P\)-breaking sweep (\(C_{2z}T\) intact)

| \(A\) | \(N\) | exact flat-gap nodes | node sep (frac) | \(\Delta^{\min}_{\rm remote}\) (meV) |
|---|---|---|---|---|
| −0.15 | 4 / 6 | 2 / 2 | 0.2158 / 0.2159 | 0.9698 / 0.9707 |
| −0.10 | 4 / 6 | 2 / 2 | 0.2136 / 0.2137 | 3.606 / 3.652 |
| −0.05 | 4 / 6 | 2 / 2 | 0.2132 / 0.2133 | 4.975 / 5.020 |
| 0 | 4 / 6 | 2 / 2 | 0.2148 / 0.2148 | 5.458 / 5.500 |
| +0.05 | 4 / 6 | 2 / 2 | 0.2169 / 0.2168 | 4.547 / 4.581 |
| +0.10 | 4 / 6 | 2 / 2 | 0.2204 / 0.2203 | 2.514 / 2.534 |
| +0.15 | 4 / 6 | 2 / 2 | 0.2254 / 0.2253 | \(10^{-9}\) / \(10^{-9}\) |
| −0.20 | 4 / 6 | ≥3 / ≥3 (4 on 30×30 grid) | — | \(10^{-9}\) |
| +0.20, ±0.25, −0.30 | 4 / 6 | 4 | — | \(10^{-9}\) |

Reading:
- Both nodes stay exact (\(\Delta_{\rm mid}\sim10^{-10}\) meV) throughout; \(N=4\) and \(N=6\) agree on everything to the digits shown. The bounded knob is cutoff-stable, unlike the \(p^2\) knob of v022.
- Remote gap closes at \(A\approx+0.15\) (≈16 meV harmonic) and \(A\approx-0.20\) (≈22 meV). Closing is an exact flat–remote crossing, i.e. Dirac nodes appear in the adjacent gap.
- Node separation changes by <6 % over the whole isolated window. **No approach, no annihilation.**
- Past closure the flat gap holds 4 exact nodes (node count in a gap changes only in pairs under \(C_{2z}T\); the "3" entries are undercounts of the coarse grid, confirmed 4 on a 30×30 grid).

---

## 5. Euler class and node handedness (real gauge)

SO(2) Wilson loop of the two flat bands along \(G_2\), tracked in \(k_1\), in the explicit real basis with base-frame orientation carried continuously (closure det \(=+0.997\)):

| case | \(N\) | \(e_2\) |
|---|---|---|
| unstrained | 4 | \(-1.000\) |
| 0.3 % strain | 4 | \(-1.000\) |
| 0.3 % strain, \(A=+0.10\) (still isolated) | 4 | \(-1.000\) |

Per-node winding, measured as the rotation of the lower-band real eigenvector inside the parallel-transported 2-frame around a circle of radius 0.02 (frac), with the frame orientation transported along a path from node 1 to node 2:

| case | \(N\) | \(w_1\) | \(w_2\) | \(w_1+w_2\) |
|---|---|---|---|---|
| strain | 4 | +1 (0.980π) | +1 (0.981π) | +2 |
| strain | 6 | +1 | +1 | +2 |
| strain, \(A=0.10\) | 4 | −1 | −1 | −2 |

(The overall sign flips between runs with the arbitrary base orientation; within a run the two nodes always share it.) \(|w_1+w_2|=2=2|e_2|\): Ahn–Park–Yang holds in our numerics, and the v022 "same handedness" claim is now measured, not inferred.

---

## 6. \(C_{2z}T\)-breaking closes the triangle

0.3 % strain, \(N=4\); minimum of \(\Delta_{\rm mid}\) over the BZ sits at the (former) node positions:

| mass term | \(m\) (meV) | \(\Delta^{\min}_{\rm mid}\) node 1 / node 2 (meV) | \(\Delta^{\min}_{\rm remote}\) |
|---|---|---|---|
| \(m\sigma_z\) (breaks \(C_{2z}T\) and \(\mathcal P\)) | 0.5 / 1 / 2 | 0.538 / 1.076 / 2.149, second node ≈1.3 % larger | 5.45 |
| \(m\tau_z\sigma_z\) (breaks \(C_{2z}T\) only, \(\mathcal P\) intact) | 0.5 / 1 / 2 | 0.120 / 0.240 / 0.480 | 5.46–5.56 |

Both nodes gap immediately and linearly in \(m\); the isolated pair and \(e_2\) are irrelevant once \(C_{2z}T\) is gone. The \(\tau_z\sigma_z\) row is the clean one: \(\mathcal P\) is untouched, so this isolates \(C_{2z}T\) as the protecting symmetry. (Smaller slope because the two layers' mass contributions partly cancel in the flat-band wavefunction.)

The logical triangle proposed at the end of v022 is now established in code:

$$\mathcal P\ \text{broken},\ C_{2z}T\ \text{kept}\ \Rightarrow\ \text{both nodes exact, same charge, no annihilation};$$
$$\text{push harder}\ \Rightarrow\ \Delta_{\rm remote}\to0\ \text{as an exact flat–remote crossing; flat gap gains a node pair};$$
$$C_{2z}T\ \text{broken}\ \Rightarrow\ \text{both nodes gap} \propto m,\ \text{remote gap unaffected}.$$

---

## 7. Self-corrections made during this check (recorded per the log standard)

- First build measured plane-wave momenta from the moiré origin instead of from each layer's Dirac point; flat bands came out at ±8 eV. Caught by the unstrained sanity check; fixed by carrying the geometric \(K_l\) shift entirely in \(q_j\).
- First Wilson loop closed the \(k_2\) loop with the periodic embedding applied in the wrong direction (\(G\to G+G_2\) instead of \(G\to G-G_2\)); \(|{\rm eig}\,W|\approx0.08\) instead of 1 flagged it.
- First per-node winding used the rank-2 holonomy, which is ≈0 around a node by construction (the singularity lives inside the subspace). Replaced by the eigenvector rotation inside a parallel-transported frame.
- First post-closure node counts (3) were coarse-grid undercounts; parity argument flagged it, 30×30 grid gave 4.

---

## 8. Open items

- Strain direction \(\phi\) and the sign/magnitude convention of the pseudo-gauge field change the node positions and the 5.5 meV baseline; v022's geometry is unknown. A \(\phi\)-scan is cheap with `run_baseline_convergence.py <phi_deg>`.
- The braiding step (C4) is asserted from the literature, not measured. Measuring it means tracking the frame charge of the flat-gap nodes relative to the new adjacent-gap nodes past \(A=0.15\).
- The \(p^2\) knob's cutoff instability (v022) was not re-tested here because its energy normalisation was never stated.

## References checked this entry
- J. Ahn, S. Park, B.-J. Yang, PRX 9, 021013 (2019); arXiv:1808.05375 — sum of windings \(=2e_2\) (sign convention differs between versions).
- Z. Song, Z. Wang, W. Shi, G. Li, C. Fang, B. A. Bernevig, PRL 123, 036401 (2019) — \(C_{2z}T\) fragile topology of the TBG flat bands.
- Q. Wu, A. A. Soluyanov, T. Bzdušek, Science 365, 1273 (2019); A. Bouhon et al., Nat. Phys. 16, 1137 (2020) — non-Abelian node charges and braiding via adjacent gaps.
- Z. Bi, N. F. Q. Yuan, L. Fu, PRB 100, 035448 (2019) — heterostrain form used.
