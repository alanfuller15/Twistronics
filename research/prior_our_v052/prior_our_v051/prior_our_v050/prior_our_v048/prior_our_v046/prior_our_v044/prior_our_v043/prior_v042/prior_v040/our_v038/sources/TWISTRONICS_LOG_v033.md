# TWISTRONICS LOG — v033

**Scope.** Endpoint of the campaign begun in v023. The v032 pending items are done: \(w_1\) confirmed at \(N=6\) on eight independent lines, the last opposite flat-gap pair annihilated, and the final state read band by band. **Result: the strained-TBG flat manifold has been driven, by \(C_{2z}T\)-preserving deformations only, from an Euler-class-1 fragile state with two same-charge Dirac nodes to a fully gapped state with zero nodes in any of the four gaps, in which the lower flat band alone carries \(w_1=(1,0)\) and every other band is trivial.** New scripts: `w1.py`, `w1_bands.py`.

---

## 1. \(w_1\) of the flat pair, confirmed (v032 pending items 1–2)

State \((A,B_{\rm sym},B_\tau,\phi,w_0/w_1)=(-0.35,-0.40,-1.8,80^\circ,1.10)\), flat pair isolated with one opposite node pair. Orientation closure of the transported flat 2-frame around each cycle, at offsets \(c=0,0.25,0.5,0.75\):

| | \(N=4\) | \(N=6\) |
|---|---|---|
| around \(k_1\) | −1, −1, −1, −1 | −1, −1, −1, −1 |
| around \(k_2\) | +1, +1, +1, +1 | +1, +1, +1, +1 |

\(w_1=(1,0)\), offset-independent, cutoff-independent.

## 2. The last pair annihilates

From the same state, \(A:-0.35\to-0.30\). Full four-gap inventory at \(A=-0.30\):

| gap | nodes | minimum (meV) |
|---|---|---|
| lower | flat\(_1\) | 0 | 22.7 |
| flat\(_1\) | flat\(_2\) | **0** | **2.87** |
| flat\(_2\) | upper | 0 | 3.15 |
| upper | next | 0 | 10.7 |

Zero nodes anywhere; every band from the lower remote band to the band above the upper remote band is an isolated real line bundle. (Bandwidth 75 meV — a real-bundle statement, as throughout.) \(B_\tau=-2.0\) gives the same fully-gapped state with the flat gap at 0.22 meV.

## 3. The final reading, band by band

Sign holonomy of each single real eigenvector transported once around a cycle (two offsets each), and orientation holonomy of the flat 2-frame:

| band | \(k_1\) | \(k_2\) | \(N\) |
|---|---|---|---|
| lower remote (band 1) | +1, +1 | +1, +1 | 4 and 6 |
| **flat\(_1\) (band 2)** | **−1, −1** | +1, +1 | 4 and 6 |
| flat\(_2\) (band 3) | +1, +1 | +1, +1 | 4 and 6 |
| upper remote (band 4) | +1, +1 | +1, +1 | 4 and 6 |
| flat pair 2-frame | −1, −1 | +1, +1 | 4 and 6 |

The flat pair's \(w_1=(1,0)\) sits entirely on the lower flat band. Band 2 has a \(\pi\) Berry phase along \(k_1\): a real line bundle with Wannier centre displaced by half a moiré lattice vector along the \(G_1\) direction. Every other band is trivial.

## 4. Campaign summary (v023 → v033)

| entry | state of the flat pair | what changed it |
|---|---|---|
| v023 | isolated, \(e_2=-1\), two same-charge nodes (0.3 % strain) | — |
| v024–v025 | same; adjacent-gap pairs come and go without threading | \(A\), \(\phi\): null |
| v026 | two nodes **opposite** along their segment; not isolated | braid 1: \(\sin\sigma_z\) drives U1 across the pair's Dirac string |
| v027 | 0.035 apart, stuck in a reciprocal link with a lower-gap pair | descent |
| v028 | opposite, un-linked, U1 robustly across | push braid deeper, then \(\tau_z\sigma_z\) opens the lower gap |
| v029 | **zero nodes** in the flat gap; U pair same-charge | pair annihilated; obstruction transferred one gap up |
| v030 | zero flat nodes; U pair cannot close (same charge) | mapped |
| v031 | U pair **opposite**; (upper, next) gap emptied | braid 2: \(w_0/w_1\to1.0\) births an (upper, next) node that crosses the U string |
| v032 | U pair closed; flat pair isolated with an opposite pair; frame non-orientable along \(k_1\) | \(\theta\) or \(w_0/w_1\); \(w_1\) traded for \(e_2\) |
| v033 | **fully gapped, zero nodes, band 2 carries \(w_1=(1,0)\), all else trivial** | \(A\) |

Everything after v023 preserved \(C_{2z}T\) exactly (checked at each new knob by \(\max|{\rm Im}\,H|\) in the real basis).

## 5. What this establishes, stated carefully

1. In this model the Euler obstruction of the strained flat bands can be removed without breaking \(C_{2z}T\), through two braids with nodes of adjacent gaps. The claim "fragile topology is trivialised by coupling to trivial bands" has been executed as a sequence of measured node-charge flips, gap closings and reopenings, with every step reproducible from the stated knob vectors.
2. The topology does not vanish; it is converted. The endpoint carries \(w_1\) on one flat band. \(w_1\) is a stable index (a Berry phase) but not a Wannier obstruction: a line bundle with \(w_1\neq0\) is Wannierizable with shifted centres. So the flat manifold ends in an obstructed-atomic-limit-type state rather than a fragile one. The v026 prediction "\(e_2=0\)" was imprecise: \(e_2\) is undefined for the non-orientable pair, and the correct endpoint statement is "\(e_2\) removed, \(w_1=(1,0)\) acquired". Recorded as a corrected prediction, not a confirmed one.
3. The mechanism by which \(w_1\) appeared is the one Ahn–Park–Yang describe: nodes of an adjacent gap winding around a BZ cycle between creation and annihilation change the \(w_1\) of the bands they touch. Here it was the upper-gap pair crossing the \(f_2\) edge during the \(\phi\) sweeps of v030–v031.

## 6. Open items, none blocking
- v032 item 3 (node count at \(\theta=1.00\)) not resolved; superseded by the fully gapped state.
- A \(\phi\)-scan of the endpoint to see how far the fully gapped, \(w_1=(1,0)\) state persists; and a check of which single knob reversal re-creates a flat pair (the reverse process should nucleate an *opposite* pair, not a same-charge one).
- For the teaching tool: the sequence v023 → v033 is a complete, animatable story of fragile topology: Euler class → braid → transfer → braid → Stiefel–Whitney class, each step a picture of nodes on the Brillouin zone with a measured sign.

## 7. Self-corrections this entry
- \(N=6\) `w1.py` first produced no output inside the time limit because the four-gap inventory dominates the runtime at \(N=6\); the inventory is now skipped above \(N=4\) and the cycle sampling reduced to 80 points (results unchanged at 120 vs 80 for \(N=4\)).
- None of this entry's physics claims needed correction; the correction to the *prediction* is in §5.2.
