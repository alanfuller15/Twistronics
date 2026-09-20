# TWISTRONICS LOG — v028

**Scope.** Resolve the v027 obstruction (reciprocal link with a lower-gap pair) and get the braided original pair into a state from which it can close. **Achieved the state; not yet the closing.** The new state is the cleanest configuration of the whole project: exactly two flat-gap nodes (the originals), opposite charge along their straight segment at \(N=4\) and \(N=6\), one upper-gap node on the far side of that segment, no lower-gap nodes, lower gap open. A strain-direction sweep from this state shrinks the pair separation while *widening* the lower gap and *strengthening* the braid, which is the direction the next entry should follow. New scripts: `scan_knob.py`, `scan_phi2.py`, `charges_env.py`, `charge_env2.py`, `descend5.py`, `descend6.py`.

Knob names: \(B_{\rm sym}\) = layer-symmetric \(\sum_j\sin(\mathbf G_j\!\cdot\!\mathbf r)\sigma_z\); \(B_{\tau}\) = layer-antisymmetric version (\(\tau_z\sigma_z\)); amplitudes in units of \(w_1\). Base \(A=0.20\), \(\epsilon=0.3\%\), \(N=4\) unless stated.

---

## 1. Route 1 (braid without spawning the lower pair): failed, systematically

| knob | lower gap | U1 crosses F1–F3? | verdict |
|---|---|---|---|
| \(B_\tau<0\) | opens (5.9→15.6 meV) | no, U1 retreats | clean environment, no braid |
| \(B_\tau>0\) | closes at +0.10 | U pair self-annihilates | no |
| single harmonic \(j=0\), \(<0\) | closes by −0.15 | yes, at −0.45 | lower pair already present |
| single harmonic \(j=1\) | opens | no | no |
| single harmonic \(j=2\), \(<0\) | opens (6.7→9.9 meV) | no, U1 retreats | clean, no braid |
| \(j=2\) at −0.30 then \(j=0\) sweep | closes at −0.25 | yes, at −0.40 | lower pair first, again |

Every \(\sigma_z\)-type direction that moves U1 toward the flat pair also pushes the lower remote band up; the lower gap closes before the crossing in all six variants. Not a topological constraint (nothing requires it), but a robust feature of sublattice-staggered perturbations in this model.

A \(\phi\) sweep in the clean \(B_\tau=-0.20\) environment (only F1, F3, U1, U2; lower gap 13 meV) reached an isolated state at \(\phi=70^\circ\) (upper gap 2.3 meV, lower 13.1 meV) with four flat nodes and charges \((F1,F3,{\rm new},{\rm new})=(-1,-1,-1,+1)\), \(\sum w=-2\). The U pair was born, wandered and died without threading the originals: **no braid**, sum rule intact with four nodes (second such check after v025).

## 2. Route 2 (un-link after the braid): works, with one condition

From the v026 braided state, opening the lower gap with \(B_\tau<0\):

- Starting from \(B_{\rm sym}=-0.30\) (U1 only +0.01 past the segment): the lower pair annihilates cleanly by \(B_\tau=-0.15\), both nodes on the far side, **but U1 is pulled back across at \(B_\tau\approx-0.12\)**. Braid lost.
- Starting from \(B_{\rm sym}=-0.40\) (U1 +0.05 past): lower pair annihilates by \(B_\tau=-0.40\), both nodes leaving on the far side (offsets +0.04…+0.08 throughout, never crossing), lower gap reopens to 4.5 meV, and **U1 stays across at +0.02**.

Condition: push the braid deep enough before un-linking.

## 3. The state \((A,B_{\rm sym},B_\tau,\phi)=(0.20,-0.40,-0.40,0)\)

| gap | nodes |
|---|---|
| flat | F1 (0.7686, 0.6476), F3 (0.5277, 0.9319) — separation 0.373 |
| upper | U1 (0.651, 0.755) at \((t,{\rm off})=(0.43,+0.02)\); U2 (0.185, 0.175), far |
| lower | none; minimum gap 4.54 meV |

Straight-segment relative charge of (F1, F3): \(N=4\): \((+1,-1)\); \(N=6\): \((-1,+1)\). **Opposite** at both cutoffs (global sign per run arbitrary). Bandwidth 79 meV: pure real-bundle topology, no flat-band meaning.

## 4. Closing attempts from this state

- Gradient descent on separation over \((A,B_{\rm sym},B_\tau,B_{\sigma_x},B_{\tau_z\mathbb 1},\phi,\epsilon)\) with a smooth penalty on U1's offset: stalls at 0.365. The steepest separation-reducing direction is "more \(B_{\rm sym}\)", which closes the lower gap; with the lower-gap minimum added to the objective the descent creeps along the constraint valley at ~0.001 per accepted step. Finite-difference steps of \(1.5^\circ\) in \(\phi\) cannot see its large-scale effect.
- Coarse \(\phi\) sweep, all monitors on:

| \(\phi\) | sep | lower gap (meV) | U1 offset | flat / lower nodes |
|---|---|---|---|---|
| 0 | 0.373 | 4.5 | +0.020 | 2 / 0 |
| 20 | 0.335 | 16.3 | +0.051 | 2 / 0 |
| 40 | 0.301 | 17.7 | +0.073 | 2 / 0 |
| 60 | 0.271 | 12.9 | +0.119 | 2 / 0 |
| −10 | 0.399 | ~0 | +0.002 | 2 / 1 — wrong way: lower pair re-born, braid nearly lost |

Positive \(\phi\) does three good things at once: shrinks the pair, opens the lower gap, and drives U1 further across (the braid becomes robust). This is the first knob found that is aligned with all three constraints simultaneously.

## 5. Next entry

Continue the \(\phi\) sweep past \(60^\circ\) with the same monitors; re-measure the (F1,F3) relative charge every \(20^\circ\) (the \(\phi\)-un-braiding of v027 §1 must not be repeated silently). If separation keeps falling, finish with a 2-knob map in \((\phi, A)\) and apply the three-part annihilation rule of v027 §6. Then re-isolate (annihilate U1–U2 by reversing \(B_{\rm sym}\), \(B_\tau\)) and compute \(e_2\); prediction still 0.

## 6. Self-corrections this entry
- v027 §5 proposed route 1 as the cleaner option; six variants show it does not exist for \(\sigma_z\)-type knobs. Route 2 is the one that works and needed the "push deep first" condition that v027 did not anticipate.
- The first un-linking attempt (from \(B_{\rm sym}=-0.30\)) would have been reported as success if only the lower-gap count had been watched; U1's offset going \(+0.009\to-0.002\) was the only tell. Monitor offsets, not counts.
- `descend5`'s lower-gap guard rejected steps but did not steer; `descend6` fixed that and confirmed the valley is real, not a bug.
