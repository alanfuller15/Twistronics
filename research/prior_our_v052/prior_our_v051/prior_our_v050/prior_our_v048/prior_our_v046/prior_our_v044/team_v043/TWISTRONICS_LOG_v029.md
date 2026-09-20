# TWISTRONICS LOG — v029

**Scope.** Completion of the sequence begun in v026: the original Euler-protected Dirac pair of the strained TBG flat bands, made opposite-charge by a \(C_{2z}T\)-preserving braid, has been **annihilated**. The flat gap is open everywhere with zero nodes, confirmed at \(N=4\) and \(N=6\). The obstruction did not disappear: the upper-gap pair that performed the braid now reads same-charge in its own two-band frame. That is the reciprocal transfer predicted by the non-Abelian picture and the Ahn–Park–Yang Dirac-string mechanism, observed directly. The final step, isolating the flat bundle and reading \(e_2=0\) from the Wilson loop, is blocked by nodes further up and is carried forward. New scripts: `scan_A2.py`, `push.py`, `final_check.py`, `transfer.py`, `n6check.py`.

All at \(\epsilon=0.3\%\), \(N=4\) unless stated; knob amplitudes in units of \(w_1\).

---

## 1. Path from the v028 state to the event

Start: \((A,B_{\rm sym},B_\tau,\phi)=(0.20,-0.40,-0.40,0)\), separation 0.373, opposite.

| leg | what moved | sep | lower gap (meV) | U1 offset / remark |
|---|---|---|---|---|
| \(\phi: 0\to60\) | strain direction | 0.373 → 0.271 | 4.5 → 12.9 | +0.02 → +0.12; minimum of sep in \(\phi\) is at 60°; past 85° the lower gap closes |
| charge re-check at \(\phi=60\) | — | 0.271 | — | \((+1,-1)\): **opposite** |
| \(A: 0.20\to0\) at \(\phi=60\) | scalar harmonic | 0.271 → 0.155 | 12.9 → 2.0 | +0.12 throughout; below \(A=0\) the lower gap closes |
| \(\phi: 60\to65\) at \(A=0\) | | 0.155 → 0.145 | 2.0 → 0.2 | further \(\phi\) closes the lower gap |
| \(B_\tau: -0.40\to-0.70\) at \((A,\phi)=(0,65)\) | layer-antisymmetric \(\sin\sigma_z\) | 0.145 → **0.022** | 0.2 → **13.4** | U1 passes around F3's end at offset +0.14 (never through the segment) |

\(B_\tau\) was the knob that finally aligned with all constraints: it opened the lower gap and closed the pair simultaneously.

## 2. The event, by the v027 §6 three-part rule

State immediately before: \((A,B_{\rm sym},B_\tau,\phi)=(0,-0.40,-0.70,65)\).

| | \(N=4\) | \(N=6\) |
|---|---|---|
| F1 | (0.6495, 0.8384), \(\Delta=8\times10^{-11}\) | (0.6495, 0.8383) |
| F3 | (0.6283, 0.8343), \(\Delta=7\times10^{-11}\) | (0.6284, 0.8342) |
| separation | 0.0216 | 0.0215 |
| relative charge, straight segment (loop radius 0.004) | \((-1,+1)\) **opposite** | \((+1,-1)\) **opposite** |

State after, \(B_\tau=-0.74\):

| check | \(N=4\) | \(N=6\) |
|---|---|---|
| (i) exact flat-gap nodes anywhere in the BZ | **0** | **0** |
| (ii) mid gap at the meeting point | opens 0.129 meV (−0.72) → 0.317 (−0.74); global minimum 0.159 meV at (0.637, 0.839) | 0.159 meV at the same point |
| (iii) other gaps unchanged | lower: 0 nodes, min 15.2 meV; upper: still exactly 2 nodes (U1, U2); local minima in the box 22 and 10 meV | lower 15.4 meV |

Bandwidth 66 meV; this is a statement about the real two-band bundle, not about flat-band physics. Annihilation amplitude \(B_\tau^\ast\in(-0.70,-0.72)\).

The original same-charge pair, which the Euler class forbade from annihilating in the isolated flat bundle (v023 §5, v025 §2), has been removed by a \(C_{2z}T\)-preserving deformation: braid (v026), un-link (v028), close (here).

## 3. Where the obstruction went

Upper-gap pair at \(B_\tau=-0.74\): U1 (0.590, 0.691), U2 (0.519, 0.965), separation 0.283. Winding of each in the \((\text{flat}_2,\ \text{upper remote})\) real two-frame, orientation transported along their straight segment:

$$ w_{U1}=+1,\qquad w_{U2}=+1 \qquad\Rightarrow\ \textbf{same charge.} $$

Before the braid this pair was created from nothing (v024 §2) and was opposite by construction. Crossing the flat pair's Dirac string flipped the flat pair's relative charge (v026) **and, reciprocally, its own**. The flat gap now has zero nodes; the upper gap holds a same-charge pair that cannot annihilate without a braid of its own. The fragile obstruction has moved one gap up.

## 4. Why \(e_2\) cannot be read yet

The Wilson-loop Euler class needs an isolated two-band bundle. At this point:
- \((\text{flat}_1,\text{flat}_2)\): isolated from below (15 meV) but not above (U1, U2 sit in that gap). Wilson loop min det \(=-1\): non-orientable, as it must be with two nodes in the adjacent gap.
- \((\text{flat}_2,\text{upper})\): min det \(=-1\) too. Cause: the upper remote band has nodes with the band above it (that gap's minimum is 0.28 meV on a coarse grid). So no two-band bundle containing \(\text{flat}_2\) is isolated, and the transfer cannot be read as a Wilson-loop integer here.

What *is* established without a Wilson loop: zero nodes in the flat gap. By Ahn–Park–Yang, the moment that gap's neighbours are opened without creating flat-gap nodes, the flat pair has \(\sum w=0\Rightarrow e_2=0\). The prediction of v026 §6 stands and is now one gap-opening away from a numerical integer.

## 5. Next entry

Open the \((\text{flat}_2,\text{upper})\) gap. Direct annihilation of U1–U2 is forbidden (same charge), so either (a) braid U1 with a node of the \((\text{upper},\text{next})\) gap — nodes appear to be present there already — and then annihilate the U pair, pushing the obstruction one further gap up; or (b) reverse the \(B_{\rm sym}\), \(B_\tau\) knobs to see whether the U pair leaves through a different route. Then Wilson loop on the flat pair: prediction \(e_2=0\), with the flat bands Wannierizable in the \(C_{2z}T\)-symmetric sense.

## 6. Self-corrections this entry
- The first charge check at \(B_\tau=-0.70\) used stale seeds from the previous scan; both refiners landed on the same node and the script printed "SAME". Caught immediately (sep = 0.000 with two exact gaps), redone with the true positions. Recorded because it is exactly the kind of false reading that would have inverted the conclusion.
- `push.py`'s "nodes in box" counts are unreliable (the refiner escapes the box); the box *minimum gap* is the trustworthy quantity and is what the three-part rule uses.
- The 21-point gap grid in `transfer.py` misses the U nodes (reports 1.84 meV where exact nodes exist). Fine for the (4,5) gap estimate, not for node counting; counts come from the dedicated search.
