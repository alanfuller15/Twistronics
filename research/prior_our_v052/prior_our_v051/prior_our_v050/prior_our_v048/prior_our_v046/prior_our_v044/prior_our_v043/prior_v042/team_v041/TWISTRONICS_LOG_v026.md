# TWISTRONICS LOG — v026

**Scope.** Executes the v025 §7 plan: a third bounded, \(C_{2z}T\)-preserving knob on top of \((A,\phi)=(0.20,0)\), where the upper-gap pair U1, U2 exists and the original flat-gap pair F1, F3 is same-charge. **Result: the braid is observed.** An upper-gap node crosses the F1–F3 segment at \(B\approx-0.285\) and the straight-segment relative charge of the original pair flips from "same" to "opposite" exactly there, at \(N=4\) and \(N=6\). The follow-on annihilation was *not* achieved cleanly; the reasons and what it implies are recorded. New scripts: `knobs.py`, `f1f3_knob.py`, `combo.py`, `crossfine.py`.

---

## 1. Correction to v025 §7

v025 listed \(\sum_j\sin(\mathbf G_j\!\cdot\!\mathbf r)\,\sigma_y\) as \(C_{2z}T\)-preserving. **Wrong**, and it showed immediately: at \(B=0.05\) it gapped every node (mid gap 0.35 meV) and \(\max|{\rm Im}\,H|\) in the real basis was 2.7 meV instead of \(10^{-14}\). The rule, with \(C_{2z}T=\sigma_x\mathcal K\) acting component-wise: conjugation flips a \(\sin\) harmonic (imaginary Fourier coefficient) but not a \(\cos\); \(\sigma_x\)-conjugation flips \(\sigma_z\) but not \(\mathbb 1,\sigma_x,\sigma_y\). So the allowed bounded harmonics are

$$ \cos(\mathbf G_j\!\cdot\!\mathbf r)\times\{\mathbb 1,\ \sigma_x,\ \sigma_y\} \qquad\text{and}\qquad \sin(\mathbf G_j\!\cdot\!\mathbf r)\times\sigma_z , $$

each with either layer sign. Verified numerically (\(\max|{\rm Im}\,H_R|=5\times10^{-14}\) for \(\cos\sigma_y\) and \(\sin\sigma_z\)). The \(\sin\cdot\sigma_z\) term is a sublattice-staggered potential that is *odd* in \(\mathbf r\); it was not on the v025 list and turned out to be the one that works.

## 2. Knobs tried (all at \(A=0.20,\ \phi=0,\ N=4\), amplitude \(B\) in units of \(w_1\))

| knob | \(B\) range | effect on F3 vs U pair | crossing of F1–F3 segment? |
|---|---|---|---|
| \(\cos\cdot\mathbb 1\otimes\tau_z\) | ±0.15 | F3 slides along the segment toward F1; U's stay ≥0.09 off | no |
| \(\cos\cdot\sigma_x\) | ±0.10 | U pair nearly self-annihilates at +0.10; at −0.10 U2 approaches the *extension* beyond F3 | no |
| \(\sin\cdot\sigma_z\), \(B>0\) | +0.05, +0.10 | U1 approaches the extension beyond F1 | no |
| **\(\sin\cdot\sigma_z\), \(B<0\)** | −0.05 … −0.40 | see §3 | **yes, at \(B\approx-0.285\)** |

## 3. The \(\sin\cdot\sigma_z\) sequence, \(B<0\)

Offsets are perpendicular distances (frac) of adjacent-gap nodes from the F1→F3 line; \(t\) is the along-segment coordinate (crossing counts only for \(0<t<1\)).

| \(B\) | flat-gap nodes | upper / lower adjacent nodes | U1 \((t,\text{offset})\) | bandwidth (meV) |
|---|---|---|---|---|
| −0.05 | 2 (F2, F4 annihilated) | 2 / 0 | (0.30, −0.113) | 47 |
| −0.20 | 2 | 2 / 0 | (0.30, −0.084) | 60 |
| −0.25 | 2 | 2 / 2 (lower pair born, both at offset ≈ +0.05) | (0.38, −0.035) | 65 |
| −0.27 | 2 | 2 / 2 | (0.40, −0.014) | |
| −0.28 | 2 | 2 / 2 | (0.40, −0.005) | |
| −0.29 | 2 | 2 / 2 | (0.41, +0.003) | |
| −0.30 | 2 | 2 / 2 | (0.41, +0.010) | 70 |
| −0.35 | 2 | 2 / 2 | (0.39, +0.035) | 74 |

U1 crosses the F1–F3 segment at \(B\approx-0.285\), \(t\approx0.40\). The lower-gap pair is born on the positive-offset side and stays there, so it contributes no crossing. (Bandwidths are far outside the flat regime; this is a topology experiment on the two-band real bundle, not a flat-band statement.)

## 4. The measurement (pre-registered in v025 §7)

Winding of F1 and F3 with the real 2-frame orientation transported along the straight F1–F3 segment (radius 0.012, 80 loop points, 250 transport steps):

| \(B\) | \(N\) | \(w_{F1}\) | \(w_{F3}\) | relative |
|---|---|---|---|---|
| −0.20 | 4 | −1 | −1 | same |
| −0.25 | 4 | +1 | +1 | same |
| −0.25 | 6 | +1 | +1 | same |
| **−0.30** | 4 | −1 | +1 | **opposite** |
| **−0.30** | 6 | +1 | −1 | **opposite** |
| −0.35 | 4 | −1 | +1 | opposite |

(Global sign per run is arbitrary; only the product matters.) The flip coincides with the crossing in §3. This is the non-Abelian braiding of Wu–Soluyanov–Bzdušek / Bouhon et al., realised in a strained-TBG continuum model: **a same-charge Euler-protected Dirac pair has been converted into an opposite-charge pair by passing an adjacent-gap node between them.** Nothing was done to \(C_{2z}T\).

## 5. Annihilation attempt — not achieved

With F1, F3 now opposite along their segment, the \(\tau_z\) knob (which shortens the segment) was stacked on \(B=-0.30\):

| \(\tau_z\) amp | F1–F3 sep | notes |
|---|---|---|
| 0 | 0.24 | |
| +0.30 | 0.21 | lower pair self-annihilated (no crossing) |
| +0.50 | 0.20 | |
| +0.75 | — | new flat pair born near F3; 4 upper nodes |
| +1.00 | 0.24 | back to 2 flat nodes at new positions |

Separation never dropped below ~0.17 before the spectrum started spawning new pairs in both gaps. So "F1 and F3 can now annihilate" rests on the charge measurement, not on an observed annihilation. Recorded as such.

## 6. What the braid implies (to be tested)

If F1 and F3 do annihilate, the flat gap has zero nodes. An isolated two-band bundle with zero nodes has \(e_2=0\). So completing the sequence

$$ (\text{braid}) \to (\text{annihilate F1,F3}) \to (\text{re-isolate: annihilate adjacent pairs}) $$

would deliver the flat bands with **\(e_2=0\)**: the fragile topology transferred out through the remote bands, which is the Ahn–Park–Yang "Dirac-string" picture of an Euler-class transition and the concrete meaning of "fragile" (trivialisable by coupling to trivial bands). Note the catch already visible: after the braid, U1 and U2 have also had a flat node's string pass between them, so *they* cannot annihilate directly either; the order of the remaining annihilations is constrained, which is exactly the non-Abelian bookkeeping.

## 7. Open items

- Find a knob that drives F1→F3 without spawning pairs (a single-harmonic \(\sin\sigma_z\) term, or tuning \(A\) down after the braid to shrink the bandwidth first, are the two obvious tries).
- After annihilation, re-isolate and compute \(e_2\) with `euler.py`; the prediction is 0.
- All of this is at \(\phi=0\); the braid amplitude \(B\approx-0.285\) will be \(\phi\)-dependent.

## 8. Self-corrections this entry
- The \(\sin\cdot\sigma_y\) knob (v025 §7) breaks \(C_{2z}T\); caught by the real-basis imaginary-part check on first use. Symmetry rule rewritten in §1.
- Early sweeps reported "flat=3" and "adj=2+1"; both are coarse-grid undercounts of pairs (parity argument), confirmed by the fine scan in §3.
