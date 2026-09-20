# TWISTRONICS LOG — v025

**Scope.** Attempt at the v024 open item: realise a braiding-enabled annihilation of the original same-charge Dirac pair using a second bounded deformation. Second knob chosen: heterostrain direction \(\phi\) (bounded, physical, already known from v024 §1 to move the nodes strongly). Result: **null.** The two-parameter family \((A,\phi)\) at 0.3 % strain never carries a flat-gap node across the Dirac string of an adjacent-gap pair, so no braid occurs. Every intermediate measurement is consistent with that, and the null is itself useful: it shows what a braid would have to look like and rules out the cheapest route. Same model as v023/v024; new scripts `phi_at_A.py`, `charges.py`, `pairtest.py`, `local.py`, `A_track.py`, `f1f3.py`. All \(N=4\) (validated against \(N=6\) in v023/v024 for this regime).

Labels used throughout, by continuity from \(A=0\): **F1, F3** = the original pair; **F2, F4** = the pair created in the flat gap at \(A\approx0.2\); **U1, U2** = the pair created in the upper adjacent gap at \(A\approx0.15\).

---

## 1. \(\phi\) sweep at \(A=0.20\)

| \(\phi\) | flat-gap nodes | upper-gap nodes | \(\Delta^{\min}_{\rm remote}\) (meV) | note |
|---|---|---|---|---|
| 0 | 4 | 2 | \(10^{-9}\) | v024 starting point |
| 2–8 | 4 | 2 | \(10^{-9}\) | U1, U2 approach each other head-on |
| 9 | 4 | 0 | \(6.8\times10^{-3}\) | U pair annihilated near (0.66, 0.855) |
| 10 | 4 | 0 | 0.46 | **isolated again, 4 flat nodes** |
| 20–58 | 4 | 2 | \(10^{-9}\) | new U pair born near (0.92, 0.55) at \(\phi\approx15\) |
| 60 | 4 | 2 | \(10^{-9}\) | exact \(C_3\) image of \(\phi=0\) (checked) |

U1 and U2 track: (0.78,0.78)→(0.70,0.83) and (0.54,0.91)→(0.62,0.88); F3, the nearest flat node, stays ≥0.08 from the U1–U2 segment throughout. Geometrically no flat node is enclosed by the U pair's creation–annihilation loop.

## 2. Charge audit in the re-isolated regime \((A,\phi)=(0.20,10^\circ)\)

Straight-path windings from F1 (path-independent up to global sign in an isolated bundle):

$$ w_{F1}=-1,\quad w_{F3}=-1,\quad w_{F2}=-1,\quad w_{F4}=+1,\qquad \sum w=-2=2e_2 .$$

Originals still same-signed, created pair opposite, sum rule intact with four nodes. **No braid**, exactly as the geometry of §1 predicts. (Also a non-trivial check of the Ahn–Park–Yang sum rule in a 4-node isolated configuration.)

## 3. The near miss at \(\phi\approx50^\circ\)

F3 and F4 approach to a separation of 0.030 (frac) at \(\phi=50\) and separate again (0.041 at 52). Local dense search confirmed two distinct exact nodes at every \(\phi\) in 46–52 (the "3 nodes" on the coarse grid at 48 was an undercount). Relative charge measured along the direct 0.03-long segment between them, with no adjacent-gap node anywhere near:

| \(\phi\) | \(w_{F3}\) | \(w_{F4}\) | relative |
|---|---|---|---|
| 50 | −1 | +1 | opposite |
| 52 | +1 | −1 | opposite |

Opposite charges that pass with a finite impact parameter simply miss each other. A near miss is not evidence of anything, and this one wasn't.

## 4. The \(\phi:0\to60^\circ\) loop is a permutation, not a braid

Tracking all four flat nodes continuously and identifying the \(\phi=60\) configuration with the \(C_3^{-1}\) image of \(\phi=0\) (\((f_1,f_2)\to(f_2,-f_1-f_2)\), verified to \(10^{-3}\) on all six nodes):

$$ F1\to F3\to F2\to F1,\qquad F4\to F4 .$$

A 3-cycle among the three nodes that all carry \(w=-1\) in the isolated gauge, with the lone \(+1\) node fixed. Consistent with Abelian labels; a braid would have had to move a \(-1\) node onto \(F4\)'s slot or vice versa.

## 5. Pushing \(A\) instead

At \(\phi=0\), \(A=0.20\to0.28\): U1 moves to (0.92,0.70), U2 to (0.45,0.97), F3 creeps from (0.592,0.801) to (0.593,0.834). F3's normalised offset from the U1–U2 line shrinks from −0.073 to −0.047 but does not cross, and neither U node comes near the F1–F3 segment. Relative charge of the original pair along the straight F1–F3 segment:

| \(A\) | \(w_{F1}\) | \(w_{F3}\) | relative |
|---|---|---|---|
| 0.20 | −1 | −1 | same |
| 0.28 | +1 | +1 | same |

(Global sign is arbitrary per run.) Still same. Beyond \(A\approx0.3\) the bands are >50 meV wide (v024 §2), so this route is abandoned.

---

## 6. Conclusion of the attempt

Everything measured in v023–v025 fits one consistent picture:

- Isolated regime: \(e_2=\pm1\), two same-charge Dirac nodes, sum rule \(\sum w=2e_2\) holds with 2 and with 4 nodes.
- Adjacent-gap node pairs make the flat bundle non-orientable (holonomy −1, v024), so braiding is *possible*.
- Neither the scalar harmonic \(A\) nor the strain direction \(\phi\), nor their combination, ever drives a flat node across an adjacent pair's Dirac string. The adjacent pairs are born and die on their own, away from the flat nodes.

So "remote-band incorporation is the escape route" (v022) is correct as a statement about what *permits* annihilation of the same-charge pair, but in this model it is not what *happens* along any cheap deformation: the system escapes the Euler obstruction by creating a second flat-gap pair (F2, F4), not by braiding the first.

## 7. What a working braid experiment needs (carried forward)

A deformation that acts on the flat nodes and the adjacent nodes *differently*, so their relative motion can be steered. Candidates, all bounded and \(C_{2z}T\)-preserving:
- layer-antisymmetric scalar harmonic \(B\,w_1\sum_j\cos(\mathbf G_j\!\cdot\!\mathbf r)\,\tau_z\);
- sublattice-odd harmonics \(B\,w_1\sum_j\cos(\mathbf G_j\!\cdot\!\mathbf r)\,\sigma_x\) or \(\sum_j\sin(\mathbf G_j\!\cdot\!\mathbf r)\,\sigma_y\) (the \(\sin\cdot\sigma_y\) combination is real under \(\sigma_x\mathcal K\));
- a single-harmonic (one \(j\)) version of the scalar knob, which breaks the residual \(C_3\)-like structure and should move U1, U2 asymmetrically.

Success criterion, stated in advance: the straight-segment relative charge of the tracked original pair flips from "same" to "opposite" across a parameter interval in which an adjacent-gap node is seen to cross that segment; then reducing the knobs to re-isolate the bundle should allow (F1,F3) to annihilate, leaving (F2,F4) as the surviving same-charge pair with \(\sum w=2e_2\).

## 8. Self-corrections this entry
- Coarse-grid node count of 3 at \(\phi=48\) was an undercount (two nodes 0.05 apart); resolved with a local dense search before any conclusion was drawn.
- First instinct was to read the \(\phi\approx50\) near miss as "same-charge bounce". Measured instead of assumed; it was an opposite-charge miss.
