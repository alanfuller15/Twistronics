# TWISTRONICS LOG — v038 — v037 disposition and the kinetic convention

**Scope.** (a) Disposition of the team's v037 first-braid path replay. (b) The four qualifications v037 raised against v036, each accepted and narrowed in the text below. (c) The strain-dependent kinetic term settled from the literature rather than from either of us, implemented, and its effect measured. **Labels unchanged; one v036 sign was wrong; remote-gap magnitudes carry a ~9 % model sensitivity, not the 4 % v036 claimed.** New files: `tbg_ref.py` (kinetic option), `ref_kinetic.py`, updated `test_tbg_ref.py`.

---

## 1. v037: accepted as the strongest evidence for the first braid

The team replayed the continuous \(B_{\rm sym}\) path of v026 in both engines through one shared gated harness: 21 parameter states per run, six tracked nodes per state, four runs (\(N=4,6\) × two Hamiltonian variants), 504 tracked node roots, largest tracked node gap \(1.8\times10^{-12}\) meV, smallest transport overlap 0.966. Findings that this log adopts:

- The spatial relative-charge comparison changes SAME → OPPOSITE exactly where the upper-gap node crosses the connecting segment; each node's charge carried along its own trajectory does not change. That is the mechanism as stated in v026 §4 and it is now seen at every sampled step, not only at two endpoints.
- At the crossing the gate refuses the comparison because the pair loses isolation on the singular path. That refusal is correct behaviour and is what v034's `classify` was meant to deliver.
- The orientation reversal is the holonomy around the parameter–momentum rectangle (initial segment, node trajectories, final segment). This is the cleanest statement of the effect the campaign has produced.

**Crossing location is path-dependent.** Center-to-center: \(B\approx-0.28594\) (original kinetic) and \(-0.28795\) (team variant), \(N=4\) and \(N=6\) agreeing to \(2\times10^{-6}\). With the loop-start offsets used by the v026 estimator (0.012), the singularity sits at \(B\approx-0.276\). **Correction to v026 §3: "\(B^\ast\approx-0.285\)" is the center-path value; the v026 number was read off a segment between offset loop starts and belongs to that convention.** Any quoted flip location now names its path.

Not established by v037, and not claimed: the later braid, the annihilation sequence, the endpoint, \(N>6\), and node births between samples.

## 2. v036 qualifications, accepted

| v036 claim | status | corrected statement |
|---|---|---|
| "different truncation" between the shared-grid and offset-grid bases | **wrong** | the retained integer index sets are identical at the tested \(N\); origin − \(K^{(2)} = q_0\) recovers the offset-layer momenta algebraically. The basis is a different *description*, not a different finite basis |
| real basis "built numerically, not by hand" | overstated | same canonical matrix, different construction route; it checks the hand construction, it does not replace it |
| "reproduces `bm_strain` to every printed digit" with the velocity term off | too strong | agreement to \(2.6\times10^{-4}\) meV in band energies (\(4\times10^{-3}\) meV in matrix entries) from exact vs linearised strain geometry; "very close" is the supportable phrase |
| "the entire discrepancy is the velocity renormalisation" | too strong, and the term itself was wrong (§3) | the discrepancy is dominated by the kinetic tensor; the residual is geometry linearisation |

## 3. The kinetic tensor, from the source

For uniform strain \(\bar\epsilon\) the low-energy Hamiltonian is \(H=\hbar v_0\,\boldsymbol\sigma\cdot(\mathbf I+\bar\epsilon-\beta\bar\epsilon)\cdot\mathbf q\), with \(\mathbf q\) measured from the shifted Dirac point \(\mathbf K_D=(\mathbf I+\bar\epsilon)^{-1}\mathbf K_0\) plus the \(\beta\)-dependent shift (Oliva-Leyva & Naumis, PRB **88**, 085430 (2013); J. Phys.: Condens. Matter **26**, 125302 (2014)). The three pieces: the unstrained Dirac term; \(+\bar\epsilon\) from the stretched bond vectors with unchanged hopping (a one-dimensional check: \(E=-2t\cos[ka(1+\epsilon)]\) gives \(v\propto a(1+\epsilon)\)); \(-\beta\bar\epsilon\) from the hopping modulation, \(\beta\approx3\).

Consequences for this project:
- **v036 §1 had the geometric factor with the wrong sign** (\(\mathbf I-\mathbf E_l\)). The geometric factor is \(\mathbf I+\mathbf E_l\).
- Neither model included the hopping piece, which is three times larger. The full tensor is \(\mathbf v/v_0=\mathbf I+(1-\beta)\mathbf E_l\approx\mathbf I-2.14\,\mathbf E_l\). By accident it has the same sign as the v036 term, which is why v036's labels were unaffected; its magnitude is 2.1× larger.
- The pseudo-gauge shift \(\mathbf A_l=\frac{\sqrt3\beta}{2a}(E_{xx}-E_{yy},-2E_{xy})\) used throughout is the same object as the \(\beta\)-dependent Dirac-point shift above once \(a\) (lattice constant) is converted to the bond length; unchanged.
- The team's \(R(-\theta)(\mathbf I+\mathbf E)\) sensitivity variant is the geometric piece alone with the correct sign.

`tbg_ref.py` now takes `kinetic='none' | 'geom_wrong' | 'full'`; `'none'` is `bm_strain`, `'geom_wrong'` is v036, `'full'` is the tensor above. Bi–Yuan–Fu's geometric factor is not the full tensor and the two should not be conflated; in the mixed-frame TBG problem the strain is applied per layer in the lab frame with \(\mathbf E_l=\mp\mathbf E/2\), and the tensor multiplies the momentum measured from the layer's shifted Dirac point before the layer rotation, which is the order used in `tbg_ref.H`.

## 4. Sensitivity of the baseline and the first braid to the kinetic term (\(N=4\), 0.3 %, \(\phi=0\))

| kinetic | nodes | sep | remote gap (meV) | bandwidth | \(e_2\) (plaquette) | charges |
|---|---|---|---|---|---|---|
| none (`bm_strain`) | (0.5787, 0.7285), (0.7564, 0.6086) | 0.2144 | 5.458 | 24.26 | −1.008 | same |
| geom_wrong (v036) | (0.5797, 0.7274), (0.7575, 0.6075) | 0.2144 | 5.229 | 24.19 | −1.008 | same |
| **full** | (0.5808, 0.7262), (0.7587, 0.6062) | 0.2145 | **4.967** | 24.20 | −1.007 | same |

First braid with the full tensor: \(B=-0.25\) → \((+1,+1)\) SAME; \(B=-0.30\) → \((+1,-1)\) OPPOSITE. Reproduced.

**Correction to v036 §2 and to every remote-gap magnitude in v023–v033:** the model sensitivity to the kinetic term is ≈ 9 % on the baseline remote gap (5.46 → 4.97 meV), with node positions moving by \(2.4\times10^{-3}\). Topological labels, node separation and bandwidth are insensitive. All logged gap magnitudes are `kinetic='none'` values and should be read with that caveat until the campaign is re-run with `'full'`; the v035 cutoff caveat (±0.1–0.25 meV) is smaller than this model caveat.

## 5. Convention now fixed for the log

Kinetic term: \(\hbar v_0[(\mathbf I+(1-\beta)\mathbf E_l)\,R(-\theta_l)\,(\mathbf p-\mathbf K_l-\mathbf A_l)]\cdot\boldsymbol\sigma\), \(\beta=3.14\), \(\mathbf E_l=\mp\mathbf E/2\) in the lab frame, \(\mathbf A_l\) as above. Tunnelling: first-harmonic \(T_j\) with \(w_0/w_1\) as stated per entry; strain enters the tunnelling only through the \(q_j\) geometry (no strain dependence of \(w_0,w_1\) is modelled, which is a further approximation the team correctly flagged). Any future magnitude is quoted with the kinetic option named.

## 6. Next
- Re-run the v029/v031/v033 checkpoints with `kinetic='full'` in `tbg_ref` (labels expected to hold; magnitudes will move).
- Extend the v037 gated path replay to the second braid and the annihilation, as the team recommends.
- Add the strain dependence of the interlayer tunnelling as a named option before any magnitude is called physical.

## 7. Self-corrections this entry
- Sign of the geometric velocity factor in v036 (§3). Found by reading the source the team pointed to, not by either audit or by my own check; a one-line 1D calculation would have caught it.
- Four v036 statements narrowed (§2); the "different truncation" claim is simply retracted.
- v026's flip location re-attributed to its path convention (§1).
