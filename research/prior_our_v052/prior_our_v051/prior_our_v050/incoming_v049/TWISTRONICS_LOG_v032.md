# TWISTRONICS LOG — v032

**Scope.** Closing the upper-gap pair and reading the flat bands' invariant. The U pair was closed at two parameter points. In both, a flat-gap pair nucleates in the same step, and the flat two-band bundle comes out isolated on all sides with **two opposite-charge nodes** and **a non-orientable Euler frame along \(k_1\)** (\(w_1\neq0\), Wilson-loop orientation closure \(-1\)). The v026 prediction "\(e_2=0\)" is revised: the Euler obstruction is gone (opposite pair, no Euler class defined), but the topology that remains is the first Stiefel–Whitney class, which is Wannierizable and therefore *not fragile*. Pending: \(N=6\) and second-line confirmation of the \(-1\) closure. New scripts: `inspect_local.py`, `Uwind.py`, `flat_e2.py`; `check_iso.py` given an import guard.

Base: \(B_{\rm sym}=-0.40\), \(\phi=80^\circ\), \(\epsilon=0.3\%\), \(w_0/w_1=1.0\), \(N=4\).

---

## 1. The U pair would not close without a flat pair appearing

| path | U sep | flat gap (meV) | what happened |
|---|---|---|---|
| \(A=-0.20\), \(B_\tau:-1.2\to-1.8\) | 0.09 → 0.21 | 4.7 → 9.1 | every other gap opens, U pair spreads |
| \(B_\tau=-1.8\), \(A:-0.25\to-0.35\) | 0.16 → 0.088 | 8.0 → 4.0 | closing |
| \(A:-0.36\to-0.39\) (local bisection) | 0.078 → 0.06 | 3.1 → 0.8 → **closed** | flat pair nucleates at (0.684, 0.906), 0.04 from U1, with the U pair still 0.06 apart |
| \(A=-0.35\), \(\theta=1.00\) | — | 2 nodes | **U pair gone** (f2|up min 4.4 meV) and flat pair present |
| \(A=-0.35\), \(w_0/w_1=1.10\) | — | 2 nodes | **U pair gone** (f2|up min 3.6 meV) and flat pair present |

Three independent knobs, one outcome. I suspected a conservation law (\(w_2\) of the rank-3 bundle \(\{\text{flat}_1,\text{flat}_2,\text{upper}\}\)) and a non-orientable \((\text{flat}_2,\text{upper})\) bundle. Both were tested and **both are wrong**:
- U-pair relative charge along paths winding once around the BZ (\(-f_1\) and \(+f_2\) cycles): opposite, same as the short segment ⇒ the \((\text{flat}_2,\text{upper})\) bundle is orientable. (The \(+f_1\) winding could not be measured: at \(f_1\approx1.7\) the truncated basis no longer resolves the node; \(-f_1\) covers the same \(\mathbb Z_2\) class.)
- \(w_2\) of the rank-3 bundle is not conserved across this campaign because the outer gaps closed and reopened repeatedly (lower pairs in v027–v031, upper pairs in v030–v031).

The nucleation is therefore an energetic three-band feature of this model (bands 2, 3, 4 all within a few meV where the U pair meets; bandwidth ~80 meV), not a topological law.

## 2. The isolated flat pair, read directly

At \((A,B_\tau,w_0/w_1)=(-0.35,-1.8,1.10)\):

| quantity | value |
|---|---|
| gap minima | lo|f1 32.3, f2|up 3.62, up|nx 10.3 meV — **flat pair isolated** |
| flat nodes | (0.681, 0.967), (0.682, 0.875), separation 0.093 |
| relative charge, straight segment | \((-1,+1)\): **opposite** |
| Wilson loop along \(k_2\), every \(k_1\) line | \(\det=+1\) (orientable along \(k_2\)) |
| orientation closure along \(k_1\) | \(\mathbf{-1.00}\) (non-orientable along \(k_1\)) |

At \((A,B_\tau,\theta)=(-0.35,-1.8,1.00)\): same gap structure (lo|f1 38.9, f2|up 4.4, up|nx 9.3 meV), same closure \(-1\). (Node count there came back as 1 on the coarse grid; parity says 2, not yet resolved.)

Compare v023 §5, the starting point: closure \(+0.997\), \(e_2=-1\), two same-charge nodes.

## 3. What this means

- **Euler obstruction removed.** The flat gap holds an opposite pair; nothing forbids its annihilation. The three braids of v026–v031 did what the theory says they can.
- **\(e_2=0\) is the wrong statement**, because \(e_2\) is only defined for orientable bundles and the flat bundle is no longer orientable. The invariant that survived is \(w_1=(1,0)\): the two-band real frame reverses orientation once around the \(k_1\) cycle. This is a \(\pi\) Berry phase carried by the flat pair along \(k_1\).
- **Not fragile.** A real line bundle with \(w_1\neq0\) over \(T^2\) is still Wannierizable (Wannier centres displaced by half a lattice vector along that direction). Once the opposite pair is annihilated, the two flat bands separate into two such line bundles with \(w_1\)'s summing to \((1,0)\). So the flat manifold has been driven from a fragile (Euler) state to an obstructed-atomic-limit-type state: a polarization index, not a Wannier obstruction. This is a sharper endpoint than "\(e_2=0\)".
- **How \(w_1\) changed.** \(w_1\) of the flat pair along a cycle flips whenever a node of an adjacent gap winds around that cycle between its creation and annihilation. U2 crossed the \(f_2=1\) boundary several times during the \(\phi\) sweeps (v030–v031), and the (upper, next) pair crossed \(f_1\) edges; the net effect is the \(-1\) closure seen here. This is the Ahn–Park–Yang statement that Euler and Stiefel–Whitney classes trade against each other through Dirac-string crossings, seen in a continuum model.

## 4. Pending before this is logged as established
1. \(N=6\) repeat of §2 (closure, det, node charges).
2. Closure measured along a second \(k_1\) line (\(f_2=0.5\)) and along \(k_2\) lines explicitly, to confirm \(w_1=(1,0)\) and not a base-line artefact.
3. Resolve the node count at \(\theta=1.00\) (expect 2, opposite).
4. Annihilate the opposite flat pair (should be routine now), then read \(w_1\) of each separated flat band.

## 5. Self-corrections this entry
- Two hypotheses (non-orientable \((\text{flat}_2,\text{upper})\); conserved \(w_2\)) were written down, tested, and discarded within the entry. Recorded because the non-orientability idea was right about the *wrong* bundle.
- First winding test returned \(w=-0.01\) for a node: impossible. Cause: the target node in the shifted basis was not refined before the loop was drawn. Rule: refine every node in the basis it will be measured in.
- `check_iso.py` executed its scan on import and broke every script that imported it. Import guard added.
