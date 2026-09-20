# TWISTRONICS LOG — v024

**Scope.** Closes two of the three open items from v023: (a) strain-direction dependence of the baseline; (b) the braiding step, which v023 asserted from the literature (correction C4) and now measures. Same model and conventions as v023 (`bm_strain.py`); new scripts `orient.py`, `braid.py`, `phiscan.py`, `count.py`.

---

## 1. Strain-direction scan (open item 1)

0.3 % heterostrain, \(N=4\), \(A=0\):

| \(\phi\) (deg) | bandwidth (meV) | node sep (frac) | \(\Delta^{\min}_{\rm remote}\) (meV) | at |
|---|---|---|---|---|
| 0 | 24.26 | 0.214 | 5.46 | (0.680, 0.742) |
| 15 | 23.01 | 0.235 | 10.75 | (0.691, 0.717) |
| 30 | 22.00 | 0.197 | 7.66 | (0.778, 0.595) |
| 45 | 24.87 | 0.153 | 4.08 | (0.764, 0.581) |
| 60 | 24.26 | 0.133 | 5.50 | (0.742, 0.578) |
| 90 | 22.00 | 0.165 | 7.66 | (0.595, 0.627) |

- \(\phi=0\) and \(60^\circ\), and \(30^\circ\) and \(90^\circ\), are \(C_3\) images of each other and reproduce each other's bandwidth and remote gap (the 5.46 vs 5.50 at \(\phi=0/60\) is the \(N=4\) cutoff asymmetry already seen in v023 §3). Consistency check passed.
- Two exact nodes at every \(\phi\). Node separation ranges 0.13–0.24 and the remote gap 4–11 meV depending only on strain direction. v022's \(d_{\rm nodes}\simeq0.139\) is inside this range (near \(\phi\approx60^\circ\) in this convention), so the v022 geometry is plausibly a different \(\phi\), not a different physics.
- Consequence: a single "isolation at 0.3 % strain" number is meaningless without \(\phi\). Log \(\phi\) with every strained result.

---

## 2. The braiding step, measured (open item 2)

Setting: \(\phi=0\), \(A=+0.20\), past the remote-gap closing at \(A\approx0.15\). Nodes located on a \(30\times30\) (flat gap) and \(36\times36\) (adjacent gaps) grid with refinement, threshold \(\Delta<10^{-6}\) meV.

**Node inventory (identical at \(N=4\) and \(N=6\) to \(10^{-4}\)):**

| gap | nodes (frac) |
|---|---|
| flat–flat | (0.7695, 0.6517), (0.5959, 0.5723), (0.5915, 0.8011), (0.4573, 0.5621) |
| upper flat / remote above | (0.7796, 0.7782), (0.5443, 0.9117) |
| lower flat / remote below | none |

So the closing at \(A\approx0.15\) created **one pair of nodes in the upper adjacent gap**, and the flat gap went from 2 to 4 nodes.

**Measurement 1 — orientation holonomy of the flat two-band frame.** Transport the real 2-frame \((u_1,u_2)\) of the flat bands around a circle of radius 0.03 (frac) about each node, fixing the sign of \(u_2\) by continuity, and record \(\det\) of the start-vs-end frame:

| node type | holonomy \(\det\) | \(N=4\) | \(N=6\) |
|---|---|---|---|
| each of the 4 flat-gap nodes | \(+1.00\) | ✓ | ✓ |
| each of the 2 upper-gap nodes | \(-1.00\) | ✓ | ✓ |

Interpretation: around a flat-gap node both \(u_1,u_2\to-u_1,-u_2\) (det \(+1\)); around an adjacent-gap node only \(u_2\to-u_2\) (det \(-1\)). The flat two-band bundle is **no longer orientable** once adjacent-gap nodes exist. This is the first Stiefel–Whitney class \(w_1\) of the flat bundle becoming nontrivial on loops enclosing an adjacent-gap node, which is precisely the condition under which the flat-gap node charges become non-Abelian (frame charges) rather than \(\pm1\) integers.

**Measurement 2 — path dependence of the relative charge.** Windings of the four flat-gap nodes with the frame orientation transported along straight paths from node (0.7695, 0.6517):

$$ (w_1,w_2,w_3,w_4) = (-1,\,-1,\,-1,\,+1), \qquad \textstyle\sum w = -2 . $$

The original pair is still same-signed; the created pair is opposite-signed \((-1,+1)\), as pair creation requires. Transporting the orientation from node 1 to node 2 along a path that passes on the other side of the upper-gap node (0.5443, 0.9117) instead gives

$$ w_2 = +1 \quad (\text{orientation flip } \det=-1), $$

i.e. the *relative* sign of two flat-gap nodes is path-dependent, and flips exactly when the comparison path winds around an adjacent-gap node. Same result at \(N=4\) and \(N=6\).

**What this establishes.** The v022 "remote-band incorporation" and the v023 sharpening (C4) are now both measured in code:

$$ \text{isolated}\ (A<0.15):\ \ w_1=w_2,\ \sum w=2e_2\ \Rightarrow\ \text{no annihilation};$$
$$ A\gtrsim0.15:\ \ \text{adjacent-gap node pair created}\ \Rightarrow\ \text{flat bundle non-orientable}\ \Rightarrow\ \text{relative sign of flat nodes path-dependent}. $$

Once the relative sign is path-dependent, "same charge" is no longer an obstruction: a flat node carried around an adjacent-gap node (by continuing to deform the Hamiltonian) returns with reversed relative charge and can then annihilate its partner. This is the Wu–Soluyanov–Bzdušek / Bouhon et al. mechanism, seen here in a strained-TBG continuum model rather than a toy model.

**What this does not establish.** No annihilation of the original pair was observed in the range scanned. Counts at larger \(A\) (\(N=4\), \(\phi=0\)):

| \(A\) | flat-gap nodes | upper-gap | bandwidth (meV) |
|---|---|---|---|
| 0.30 | 4 | 2 | 54 |
| 0.40 | 4 | 2 | 66 |
| 0.50 | ≥5 (odd ⇒ undercount, true count ≥6) | 2 | 75 |

By \(A=0.3\) the "flat" bands are 54 meV wide; this is outside any regime where the flat-band story means anything, so the sweep stops here. Observing an actual braiding-enabled annihilation would need a second, independent deformation that moves a flat node around an adjacent-gap node without blowing up the bandwidth. That is a design problem for a later entry, not a numerics problem.

---

## 3. Self-corrections this entry

- First path-dependence test used a polyline detour built from a perpendicular offset; for the upper-gap node at (0.78, 0.78) the two "sides" both passed the same way (the node sits behind the segment's start point in the along-path coordinate), so the null result there was a geometry error, not physics. Replaced by the orientation-holonomy primitive (Measurement 1), which is loop-by-loop unambiguous; the path-dependence result quoted above is from the node at (0.544, 0.912), where the detour was valid.
- Odd node counts on coarse grids are undercounts (node number in a gap changes by 2 under \(C_{2z}T\)); flagged rather than fixed at \(A=0.5\) because that regime is out of scope.

## 4. Open items carried forward

- Design a second bounded deformation (e.g. a \(C_{2z}T\)-preserving harmonic with a different sublattice structure, \(\sigma_x\) or \(\sigma_y\) weighted) that moves flat-gap nodes without collapsing isolation, and attempt the braiding-enabled annihilation explicitly.
- v022's \(p^2\) knob remains unreproducible (normalisation never stated). Closed as unrecoverable unless the original definition turns up.
- Teaching-tool implication (for the primer): the three measurable objects here — node winding, Euler class, orientation holonomy — are all things a reader can *see* on a Brillouin-zone map. Worth prototyping as the fragile-topology page.
