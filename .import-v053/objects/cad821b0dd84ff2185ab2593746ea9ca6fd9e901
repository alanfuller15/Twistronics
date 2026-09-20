# TWISTRONICS LOG — v031

**Scope.** The v030 §5 design, executed. The upper-gap pair U1, U2 (same-charge since v029) has been braided with a node of the (upper, next) gap and now reads **opposite**; the (upper, next) pair then annihilated on its own, so the \((\text{flat}_2,\text{upper})\) two-band bundle is isolated with an opposite pair, i.e. \(\sum w=0\Rightarrow e_2=0\) for that pair. The U pair has been driven to 0.09 apart with the flat gap still empty at 4.7 meV. The final annihilation and the Wilson-loop readout of the flat pair are one push away and are carried forward. New scripts: `Ucharge.py`, `check_iso.py`; `scan_U.py` extended (ratio, theta, second-shell harmonic, periodic wrap).

Knob vector now: \((A, B_{\rm sym}, B_\tau, \phi, \epsilon, w_0/w_1, \theta)\). Base \(B_{\rm sym}=-0.40\), \(\epsilon=0.3\%\), \(N=4\).

---

## 1. The knob that acts on the remote band: \(w_0/w_1\)

Rather than a new harmonic, the existing AA/AB tunnelling ratio does the job. From \((A,B_\tau,\phi)=(0,-0.80,80^\circ)\):

| \(w_0/w_1\) | flat gap (meV) | lower gap (meV) | (upper, next) nodes relative to the U1→U2 segment \((t,{\rm off})\) |
|---|---|---|---|
| 0.80 | 2.3 | 9.6 | (−0.76, +0.041), (1.43, +0.316) — both beyond the ends |
| 0.90 | 6.5 | 1.0 | (−0.66, +0.023), (1.27, +0.276) |
| 0.98 | 7.9 | 0 | (−0.61, +0.012), (1.06, +0.220) |
| **0.99** | | 0 | new pair born inside the segment: (0.34, +0.048), (0.20, **+0.002**); old ones (−0.61, +0.011), (1.00, +0.208) |
| **1.00** | 8.3 | 0 | (0.49, +0.099), (0.08, **−0.026**), (−0.61, +0.009) |

Between 0.99 and 1.00 the newborn node at \(t\approx0.2\) crosses the segment. (The lower gap closes at ratio ≈ 0.91; that gap is two removed from the U pair and is irrelevant to its braid. It is reopened in §3.)

## 2. Pre-registered criterion (v030 §5), met

Relative charge of U1, U2 in the \((\text{flat}_2,\text{upper})\) real two-frame, orientation transported along their straight segment (radius 0.012, 80 loop points, 200 transport steps):

| \(w_0/w_1\) | \(N\) | \(w_{U1}\) | \(w_{U2}\) | |
|---|---|---|---|---|
| 0.98 | 4 | +1 | +1 | same |
| 0.99 | 4 | +1 | +1 | same |
| 0.99 | 6 | −1 | −1 | same |
| **1.00** | 4 | +1 | −1 | **opposite** |
| 1.02 | 4 | +1 | −1 | opposite |

The flip coincides with the crossing in §1. (\(N=6\) at ratio 1.00 timed out and is to be rerun; \(N=6\) at 0.99 agrees with \(N=4\).) Second braid of the project, same mechanism, one gap up from the first.

## 3. Clean-up after the braid

At ratio 1.0, \(\phi=80^\circ\):

- \(B_\tau:-0.80\to-1.2\): lower gap reopens (0 → 9.6 meV), flat gap 11.8 meV, U separation 0.224, **U pair still opposite** at −1.0 and −1.2. Along the way the crossed (upper, next) node annihilated with the one beyond U1's end; charge unchanged, so they met on the negative-offset side, not across the segment.
- \(A:0\to-0.05\): the remaining (upper, next) pair annihilates on the far side (both at positive offset). **Zero (upper, next) nodes**, minimum 3.9 meV. U pair re-measured: \((-1,+1)\), opposite.

At this point \((A,B_{\rm sym},B_\tau,\phi,w_0/w_1)=(-0.05,-0.40,-1.2,80^\circ,1.0)\) the \((\text{flat}_2,\text{upper})\) bundle is isolated from above (3.9 meV) and below (flat gap 12.3 meV) and holds exactly two nodes of opposite charge:

$$ \sum_{\text{U}} w = 0 = 2e_2(\text{flat}_2,\text{upper}) . $$

That is the isolated-bundle sum rule again, now certifying a *trivial* Euler class for the pair that carried the obstruction in v029. Compare the same pair at its birth (v024): opposite; after crossing the flat pair's string (v029): same; after crossing an (upper, next) node's string (here): opposite again. Two braids, two flips.

## 4. Closing the U pair

\(A\) further negative at the same base:

| \(A\) | U1 | U2 | U sep | flat gap (meV) | (upper, next) | lower gap |
|---|---|---|---|---|---|---|
| −0.05 | (0.564, 0.788) | (0.585, 0.977) | 0.190 | 12.3 | open, 3.9 | 3.7 |
| −0.10 | (0.569, 0.805) | (0.605, 0.957) | 0.156 | 10.8 | open, 3.9 | closed (pair) |
| −0.15 | (0.573, 0.823) | (0.623, 0.934) | 0.122 | 8.2 | open, 7.3 | closed |
| −0.20 | (0.577, 0.841) | (0.638, 0.909) | 0.092 | 4.7 | open, 9.1 | closed |
| −0.25 | — | — | — | **flat pair re-created** at (0.698, 0.873) | open, 9.3 | closed |

The U pair closes steadily under \(A\) but the flat gap re-fills just before it gets there. The window is \(A\in(-0.25,-0.20)\), U separation 0.09. Next entry: combine \(A\approx-0.2\) with deeper \(B_\tau\) (which both widens the flat gap and shortened U separation in §3) and apply the three-part annihilation rule; then reopen the lower gap with \(B_\tau\) and run `euler.py` on the flat pair with the requirement min det \(=+1\) on every \(k_1\) line. Prediction unchanged: \(e_2=0\).

## 5. Self-corrections this entry
- `Ucharge.py` first listed the (upper, next) nodes using the \((\text{flat}_2,\text{upper})\) gap index and printed the U nodes themselves at \((t,{\rm off})=(0,0),(1,0)\). Caught because a node cannot sit at both endpoints of its own segment; fixed (bands \(w_5-w_4\) with six bands returned).
- \(\theta=1.10\) reported U separation 0.000: tracker jump across the BZ boundary (\(f_2:0.99\to0.96\) on the other side). Full inventory shows the pair intact at 0.21. `scan_U.py` now wraps the segment vector; earlier unwrapped rows were already excluded in v030.
- The (upper, next) count dropping 4 → 2 at \(B_\tau=-0.9\) could have meant the crossed node went back; only the charge measurement (still opposite) settles it. Counts never substitute for charges.
