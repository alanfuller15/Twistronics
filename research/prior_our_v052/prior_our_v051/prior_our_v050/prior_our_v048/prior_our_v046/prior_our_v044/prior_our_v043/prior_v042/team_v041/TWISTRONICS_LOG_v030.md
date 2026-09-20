# TWISTRONICS LOG — v030

**Scope.** After v029 (original pair annihilated, obstruction transferred to the upper-gap pair U1, U2), the remaining task is to open the \((\text{flat}_2,\text{upper})\) gap so the flat pair becomes isolated and \(e_2\) can be read. **Not achieved this entry.** What was achieved: the region of knob space in which the flat gap stays empty is mapped, the cheap route (reversing the knobs) is ruled out, and the geometry that a braid of the U pair would need is characterised. New scripts: `scan_state.py`, `scan_U.py`.

Base state: \((A,B_{\rm sym},B_\tau,\phi,\epsilon)=(0,-0.40,-0.74,65^\circ,0.3\%)\). Gap labels: lo|f1, f1|f2 (flat gap), f2|up, up|nx.

---

## 1. Reversing \(B_{\rm sym}\): ruled out

| \(B_{\rm sym}\) | f1|f2 nodes | f2|up nodes | up|nx nodes |
|---|---|---|---|
| −0.40 | 0 (min 0.159 meV) | 2 | 2 |
| −0.30 | ≥1 (pair re-created) | 2 | 2 |
| −0.20 … 0 | 2 | 2 | 2–4 |

A flat-gap pair is re-created before \(B_{\rm sym}=-0.30\). Undoing the knob that made the braid re-fills the flat gap, as it should: the empty flat gap is a property of the post-braid configuration, not of small \(B_{\rm sym}\).

## 2. The empty-flat-gap window

Scanning one knob at a time from the base, requiring zero f1|f2 nodes:

| knob | window | f1|f2 min (meV) | lo|f1 min (meV) | note |
|---|---|---|---|---|
| \(\phi\) | 65° – 85° | 0.16 (65°) → **3.14 (80°)** → 1.55 (85°) | 15 → 6.9 → 4.0 | nodes return at 60° and at 90°; lower gap closes past 90° |
| \(B_\tau\) (at \(\phi=80\)) | ≤ −0.65 | 0.94 (−0.65), 2.3 (−0.80), 1.6 (−1.0) | 2.7 → 9.6 → 17.9 | nodes return at −0.55 |
| \(A\) (at \(\phi=80\)) | ≤ 0 | 3.1 (0), 1.7 (−0.05), 0.47 (−0.10) | 6.9 → 4.6 → 2.4 | nodes return at +0.05 |

Best-conditioned point found: \((A,B_{\rm sym},B_\tau,\phi)=(0,-0.40,-0.80,80^\circ)\): flat gap 2.3 meV, lower gap 9.6 meV, U pair separation 0.276, bandwidth 60 meV.

## 3. What the U-pair braid would need, and why no single knob does it

The U pair is same-charge along its straight segment (v029 §3). It becomes annihilable only if a node of the up|nx gap crosses that segment. Throughout the window there are exactly two up|nx nodes. Their positions relative to the U1→U2 segment (\(t\) along, offset perpendicular):

- one sits beyond U1's end, \(t\approx-0.5\) to \(-1.0\), offset +0.05 … +0.15; under \(B_\tau\to-1.0\) it swings around U1's end to offset −0.09 without ever entering \(0<t<1\);
- the other sits beyond U2's end, \(t\approx1.2\) to \(1.7\), offset +0.28 … +0.37, and moves away under every knob.

Passing around an endpoint at a finite distance does not change the path class, so none of these motions is a braid. A braid needs a knob that acts on the up|nx pair differently from the f2|up pair; the \(\sigma_z\)-family and the scalar harmonic move them together.

## 4. Status of the invariant readout

Still as v029 §4: no two-band bundle containing \(\text{flat}_2\) is isolated (U pair below the upper band, up|nx pair above it), so \(e_2\) of the flat pair is not defined at any point in the window. The theorem-level statement stands: zero nodes in the flat gap ⇒ \(e_2=0\) as soon as the gap above is opened without creating flat nodes. The obstruction now sits two gaps up from where it started (f1|f2 → f2|up, and the up|nx gap already carries a pair); each transfer moves it one band further from the flat manifold, which is the operational content of "fragile".

## 5. Next entry (design, not numerics)

- A knob with different weight on the upper remote band: candidates are a \(\cos\)-harmonic on the *interlayer* tunnelling amplitude (\(\delta w_0\), \(\delta w_1\) modulated by \(\cos\mathbf G_j\!\cdot\!\mathbf r\), which preserve \(C_{2z}T\) as real coefficients) or a second-shell harmonic \(\cos(\mathbf G_i+\mathbf G_j)\!\cdot\!\mathbf r\); remote bands are more sensitive to the higher harmonic than the flat bands are.
- Alternatively reduce the problem: shrink the U pair separation (0.26 at best so far) so that a small local deformation of the up|nx node suffices.
- Success criterion, pre-registered: straight-segment relative charge of (U1, U2) in the \((\text{flat}_2,\text{upper})\) frame flips from same to opposite across an interval in which an up|nx node crosses the segment; then U1–U2 annihilate by the v027 §6 rule; then Wilson loop of the flat pair with min det \(=+1\) on every \(k_1\) line and \(e_2=0\).

## 6. Self-corrections this entry
- `scan_U.py` computes the U segment without periodic wrapping; when U2 crosses the BZ boundary (\(f_2:0.97\to1.004\)) it reports a spurious separation of 0.70 and wrong offsets. Affected rows (\(A>0\), \(\phi\ge110\)) are excluded from §3; those rows were out of the window anyway (flat nodes re-created).
- The "up|nx node crossed the line" reading under \(B_\tau\to-1.0\) is a crossing of the line's *extension* at \(t\approx-0.6\), not of the segment. Distinguishing the two was the point of tracking \(t\); recorded so the distinction is not lost later.
