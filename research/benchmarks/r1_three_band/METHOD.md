# What is measured

The selected states are bands 297–299 (zero-based) of the 596-dimensional,
N8 R1 Hamiltonian: the two flat bands and their upper neighbor. At each
of D = 38 and 39 meV, two loops have a common basepoint. A surrounds the
previously tracked flat node q; B surrounds the selected upper-gap node.
Each loop follows a straight stem, a counterclockwise polygon, and the
reversed stem. D is fixed during every loop. This is not a temporal braid test.

[Wu, Soluyanov and Bzdušek (2019), Supplement IV.1 and V.1–V.2](https://arxiv.org/html/1808.07469v3)
describe the three-band frame space SO(3)/D2 and its quaternion fundamental
group. A lifted frame path distinguishes a full 2π rotation from the identity;
an ordinary subspace Wilson loop can miss that distinction. Their convention
associates adjacent gaps with different imaginary quaternion classes. We
use that framework, with an explicit reference chart for the embedded bands
and a declared inverse-lift convention for chronological path products.

## Reference chart and its domain

Let F(f) contain the three ordered, real eigenvectors and let B = F(base).
Define Q(f) = polar(BᵀF(f)). If BᵀF is nonsingular, this is equivalent to
expressing F in the continuous orthonormal reference frame

E(f) = P(f)B [BᵀP(f)B]^(-1/2), where P(f) = F(f)F(f)ᵀ.

Thus Q = EᵀF is a three-dimensional eigenframe, rather than a Wilson-loop
matrix. Eigenvector sign changes act on its columns. Rotating the reference
B by a constant SO(3) matrix changes the coordinates consistently.

We check the chart over a whole rectangle containing both disks and stems.
For each cell center c and any point in that cell, affine H gives
δ = Σ halfwidth_j ||∂H/∂f_j||₂ as a bound on ||H(f)−H(c)||₂.
Weyl's inequality gives an exterior-gap lower estimate L = g(c)−2δ−η.
Here g is the smaller of the gaps separating the selected block from its
two neighboring bands and η = 10⁻⁷ meV.

The following conservative projector estimate uses only exterior gaps.
Along a line from c to f, the off-block derivative in an instantaneous
eigenbasis has entries H'_{ab}/(E_b−E_a), with b in the three-band block.
Its Frobenius norm is at most √3 ||H'||₂/L. The spectral norm of P' equals
the spectral norm of this off-block matrix. Integrating gives
||P(f)−P(c)||₂ ≤ √3 δ/L. Consequently,

λ_min[BᵀP(f)B] ≥ s_min[BᵀF(c)]² − √3 δ/L.

The code subtracts a further numerical allowance of 10⁻⁷ from this squared
singular-value lower estimate. Both 8×8 and 16×16 covers must have
L > 0.001 meV and a chart singular-value lower estimate above 0.6.
Internal degeneracies are allowed inside these cells because the projector
contains all three states. This derivation concerns the exact affine model;
computed bounds are conditional on floating-point matrices, eigenvalues
and norms. They are not interval-arithmetic certificates.

## Contours and lift

On a contour, both internal gaps must also remain open. For an affine
subinterval with total Hamiltonian variation δ, every point is within δ/2
of one endpoint. The two-eigenvalue gap bound therefore reads
min(endpoint gaps) − δ − η. The adaptive rule checks all four gaps and
limits variation relative to this lower estimate. It also checks sampled
chart rank and small proper frame steps. Refinement doubles the polygon
and initial stem meshes, halves the allowed variation ratio, and halves
the frame-step angle cap. A separate radius test halves each local radius.

We choose the initial frame orientation once. Subsequent eigenvector signs
are chosen by positive column overlap. An improper resulting step is a
failure; its determinant is not silently corrected. Small SO(3) steps are
converted to quaternions with positive scalar component and multiplied.
We report the inverse cumulative lift, so traversing A then B gives
charge(AB) = charge(A) charge(B). Quaternions are ordered (w,x,y,z).
A second computation unwraps the signs of absolute rotation quaternions.

The measured paths include AB, BA and ABA⁻¹B⁻¹, constructed by concatenating
the stored projected eigenframe samples. Their results are compared with
products of the individually measured charges. Reversal, random local
eigenvector signs and a constant rotation of B provide additional checks.
They test the implementation; their agreement is not a separate physical
measurement. Individual signed imaginary labels depend on the initial
eigenframe convention. Cross-engine, mesh and radius comparisons use the
conjugacy classes {+1}, {−1}, {±i}, {±j}, {±k}.

## Limits

The local loop algebra is a prerequisite for a non-Abelian braid analysis.
Matching this algebra at two fixed D slices does not measure temporal charge
conjugation. No full braid, Euler-class change, global node inventory,
infinite-cutoff limit, novelty, or experimental realization is established
by this checkpoint. Strain is fixed; D supplies model layer potentials ±D,
not a calibrated experimental displacement field. The Hamiltonian engines
are separately coded but share this diagnostic implementation and its
assumptions. Earlier exploratory two-band charge helpers are not invoked.
