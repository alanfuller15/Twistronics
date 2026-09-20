# TWISTRONICS LOG — v027

**Scope.** Attempt to complete the v026 sequence: annihilate the braided original pair (F1, F3), re-isolate, and check \(e_2=0\). **Not achieved.** The pair was driven from 0.31 to 0.035 apart with its relative charge still opposite, and then stalled against a specific, identifiable obstruction: a lower-gap node pair born as a side effect of the \(\sin\sigma_z\) knob became braided *through* the flat pair, forming a four-node cluster in which neither pair can annihilate. This is the reciprocal braiding of Bouhon, Wu, Slager, Weng, Yazyev & Bzdušek (Nat. Phys. 16, 1137, 2020), met head-on. All \(N=4\), \(\phi\)-free parameters as stated per point. New scripts (in `v023_code/`): `sep.py`, `descend.py`, `descend2.py`, `descend3.py`, `descend4.py`, `map2d.py`, `inspect_pt.py`, `inspect_B.py`, `Bback.py`, `charge_close.py`, `event*.py`, `retrace.py`.

Knob vector used by the descent scripts: \(x=(A,\ B_{\sin\sigma_z},\ B_{\tau_z},\ B_{\sigma_x},\ B_{\sin\sigma_z}^{(1)},\ \phi,\ \epsilon)\); amplitudes in units of \(w_1\), \(\phi\) in degrees.

---

## 1. Wrong turn first: the \(\phi=80^\circ\) route un-braided the pair

From the braided state \(x=(0.20,-0.30,0,0,0,0,0.003)\), rotating strain to \(\phi=80^\circ\) brought the pair to 0.164 apart, and a steepest-descent on separation then produced an annihilation. Full node inventory showed it was **F3 annihilating with a freshly created node**, not with F1; and at the last two-node point before that (\(x_3=(0.1525,-0.3439,0.0285,-0.0164,0.0092,82.43,0.0029)\)) the straight-segment relative charge of (F1,F3) read **same**. Somewhere along the \(\phi\) sweep an adjacent-gap node had re-crossed the F1–F3 segment. Lesson: the braid is a statement about a path class, and any deformation that lets an adjacent node re-cross undoes it silently. The relative charge must be re-measured after every leg, not assumed.

## 2. Guarded descent from the braided state at \(\phi=0\)

Objective: pair separation plus a penalty keeping in-segment adjacent nodes ≥0.04 off the F1–F3 line; steps rejected if the flat-node count changes. Seven knobs, finite-difference gradient.

| stage | sep (frac) | flat nodes | notes |
|---|---|---|---|
| start | 0.309 | 2 | U1 at offset +0.010 from the segment, lower node L1 at +0.037 |
| after 17 accepted steps | 0.108 | 2 | \(x=(-0.0014,-0.3358,-0.0126,-0.3396,0.1222,6.85,0.0013)\) |
| straight continuation | **0.035** | 2 | \(x=(-0.0122,-0.3281,-0.0211,-0.3864,0.1516,6.95,0.0008)\) |

At the 0.035 point: F1 = (0.6538, 0.7426), F3 = (0.6211, 0.7298). Relative charge along the straight segment: \(w_{F1}=-1,\ w_{F3}=+1\) → **still opposite**. This is the closest the original pair has been in this whole project, and it is an opposite-charge pair with no crossing of the segment since v026.

Bandwidth here is ~53 meV and \(A\) has gone slightly negative, \(\epsilon\) down to 0.08 %: a topology experiment on the real two-band bundle, not a flat-band statement.

## 3. Why it does not close: the lower-gap pair is threaded through it

Two further pushes were tried from the 0.035 point:

- **2-D map over \((A, B_{\sigma_x})\)**: one cell reported both trackers gone and the mid gap open at the meeting point. Dense inspection (`inspect_pt.py`) showed this was false: both flat nodes persisted 0.03 apart at every \(A\) in \(0\ldots0.010\), while the lower-gap node **L1 walked straight across the F1–F3 segment** ((0.623,0.758) → (0.640,0.747) → through) between \(\Delta A=0.005\) and \(0.0078\), and a new flat pair was created by \(\Delta A=0.015\). Same failure as §1, now watched in slow motion.
- **Walk \(B_{\sin\sigma_z}\) back toward \(-0.20\)** (where the lower pair did not originally exist): the lower pair does *not* annihilate. Dense inventories at \(B=-0.24,-0.225,-0.21,-0.18\) all show the same four-node cluster within a 0.04 radius:

| gap | nodes at \(B=-0.21\) |
|---|---|
| flat | (0.660, 0.721), (0.624, 0.716) |
| lower | (0.635, 0.734), (0.657, 0.736) |
| upper | (0.573, 0.782), (0.666, 0.672) — well away |

The lower pair sits ~0.01 off the flat pair's segment, between its endpoints; the flat pair sits likewise between the lower pair's endpoints. **Each pair is braided through the other.** The flat pair reads opposite along a path that passes on one side of the lower nodes, but the lower nodes are on that path; deforming around them flips the reading. Equivalently, neither pair can annihilate without the other moving out of the way, and the knobs move them together. This is the reciprocal braiding obstruction: a linked configuration of nodes in adjacent gaps that is stable against all the deformations tried.

## 4. What is established, what is not

Established (v026 + this entry):
- \(C_{2z}T\)-preserving braiding converts the Euler-protected same-charge pair into an opposite-charge pair (v026).
- That pair can be driven arbitrarily close (0.035) while remaining opposite.
- The remaining obstruction is not the Euler class; it is a reciprocal braid with a lower-gap pair that the \(\sin\sigma_z\) knob created at \(B\approx-0.25\) on its way to producing the braid.

Not established:
- Annihilation of (F1, F3), re-isolation, \(e_2=0\).

## 5. Route for the next attempt

The reciprocal link means the lower pair must be un-braided or annihilated *before* the flat pair closes. Two designs, in order of cleanliness:

1. **Avoid creating the lower pair at all.** The braid itself (U1 crossing) happened at \(B\approx-0.285\); the lower pair was born at \(B\approx-0.25\). Find a \(\sin\sigma_z\) direction (single harmonic, or a different layer sign) that pushes U1 across the F1–F3 segment before any lower-gap closing. Check the lower-gap minimum at every step.
2. **Un-braid.** From the cluster, drive the lower pair apart along a path that takes one lower node *around* a flat node (this flips the lower pair to opposite along the direct path) and annihilate it; then close the flat pair.

Either way the descent objective must include the lower-gap minimum explicitly, continuous in all arguments (the piecewise penalty used here stalled twice), and the relative charge must be re-measured at every accepted leg.

## 6. Self-corrections this entry
- \(\phi=80^\circ\) "annihilation" was F3 with a new node; caught by full inventory before logging. The un-braiding along the \(\phi\) sweep was then confirmed by direct measurement.
- Two tracker collapses (both refiners landing on one node at sep 0.03–0.04) were initially reported by the scripts as `sep=0.000`; both were resolved by dense local inventories and neither was an event.
- The 2-D map's "gap opened" cell was L1 crossing, not annihilation. Rule adopted: an annihilation claim needs (i) both trackers losing their node, (ii) an open gap at the meeting point, and (iii) an unchanged inventory of every other gap in the box.
- The `descend3`/`descend4` penalty was discontinuous at the segment ends; it produced spurious rejections and one stall. Noted for the redesign in §5.
