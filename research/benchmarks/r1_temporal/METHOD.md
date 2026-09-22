# Sampled temporal transport and charge conjugation

The question is whether a charge can be compared along D with one carried
base eigenframe and an explicitly moving contour. The earlier three-band
checkpoint used independently based local loops at two fixed D slices.
This checkpoint follows a deformed contour at 9 and 17 D stations, carries
its base frame, checks selected temporal connections, and compares it with
a straight-path convention at both endpoints.

[Wu, Soluyanov and Bzdušek, Supplement IV.3, Eq. (43)](https://arxiv.org/html/1808.07469v3)
describe how based loops encircling a node can differ by conjugation with
another node's charge. Their world-line discussion relates a change of the
straight-ray convention to an orientation reversal. We test the corresponding
based-path algebra numerically. Our convention multiplies paths in chronological
left-to-right order, as declared in the preceding checkpoint; that differs
from the ordering of composed paths stated in the paper's footnote.

## Contour geometry

Use the previously tracked flat nodes p(D), q(D), and selected upper-gap
node u(D). Let e = (q−p)/|q−p| and n = (−e₂,e₁). The common base is
b = p + 0.55(q−p). A counterclockwise radius-r polygon around q starts at
a = q−re. Its stem has a moving kink k = u−0.006n. Define

- T: b → k → a → polygon → a → k → b;
- S: b → a → polygon → a → b;
- C: b → k → a → b.

T is the transported convention. S is the nominal straight convention.
C traverses T's outgoing stem followed by the reverse of S's outgoing
stem. All segments within a station are affine in fractional momentum.
Time connections are affine in (f₁,f₂,D) between the explicitly recorded
matching vertices. They use the existing coarse/fine root samples, not
new continuously certified node trajectories.

The moving kink keeps a declared offset from the sampled upper node. This
geometric choice alone is not a gap proof; every measured path is checked
spectrally. S is measured only at D = 38 and 39. A separate root calculation
locates its intervening crossing, where the spectral gate must reject S.

## One three-band chart through D

The real Hamiltonian is affine in (f₁,f₂,D), using the unchanged checked
R1 family. The reference B consists of bands 297–299 at the center of a
box containing all planned fine-grid vertices at both radii. The reference
is fixed for the entire D interval. At each point, Q = polar(BᵀF) expresses
the three ordered eigenvectors in the canonical chart described in the
[parent method](../r1_three_band/METHOD.md).

The same projector argument extends to three coordinates. In a cell with
halfwidths hⱼ, use δ = Σ hⱼ||Aⱼ||₂. Its exterior-gap lower estimate is
L = g(center)−2δ−10⁻⁷ meV. Provided L > 0, the projector-displacement
bound gives a squared chart singular-value lower estimate

s(center)² − √3 δ/L − 10⁻⁷.

Both exterior gaps are included; the selected triple may have internal
nodes. Failed lower estimates cause bisection along the coordinate with
the largest hⱼ||Aⱼ||₂ contribution. A cell with an actual center violation
or maximum depth is retained as unresolved. Every leaf must pass L >
0.001 meV and the chart singular-value lower threshold 0.6. The two covers
start from 8×8×2 and 16×16×4 grids. This is a conditional floating-point
bound over the containing volume, not an interval-arithmetic certificate.

## Carried base frame and guarded grid

At D38 we select a proper orientation for the ordered base eigenframe.
Along each adaptive temporal base edge, individual column signs are carried
by positive overlap. An improper step is rejected. The resulting base
frame seeds every loop at that station, so signs are not independently
reset at successive D values. Shared station frames are compared between
the two time grids.

All spatial polygon edges and both stems are checked at every station.
Between neighboring stations, temporal edges are checked at the base,
kink, and 16 or 32 equally spaced polygon vertices. Both radii, 0.003 and
0.0015, are included. On each affine edge, all four gaps must pass the
nearest-endpoint lower estimate min(endpoint gaps)−δ−10⁻⁷ meV > 0.001 meV.
The unchanged parent edge routine also limits relative Hamiltonian
variation, sampled chart rank and the proper frame-step angle.

**The checked temporal edges form a grid, not a certificate for all of its
two-dimensional faces.** Those face interiors can contain points not covered
by the all-four-gap bounds. The volume bound concerns only exterior isolation
and chart rank; it does not close this internal-gap limitation. Likewise,
root convergence at the carried stations does not certify root identity
between them. Both limitations remain part of the result's scope.

## Conjugation and crossing control

At each endpoint we measure the lifted charges of T, S and C with the same
carried base frame. We also explicitly concatenate samples for C S C⁻¹
and lift that full path. Its result is compared with both q_T and the
product q_C q_S q_C⁻¹. The path reduction behind this relation cancels
the retraced nominal stems; the discrete implementation must reproduce it.
The predicted change is a constant transported charge, a sign change in
the nominal endpoint charge, and a change in C from +1 to the upper-gap
class {±i}. Predictions are kept separate from numerical validity.

To locate the forbidden nominal crossing, the fine-grid p and q positions
are linearly interpolated in the known D bracket [38.0625,38.125]. At each
Brent evaluation, the unchanged upper-gap root solver refines u. The scalar
residual is u's signed offset from the interpolated p–q line. The resulting
upper root is included as an exact vertex of a nominal stem, and the
all-four-gap edge routine must reject that stem. No accepted charge is
assigned at this crossing.

The eight new analytic cases test translating nodes, carried frames with
and without imposed coordinate-dependent eigenvector signs, explicit
conjugation of adjacent-gap loops, and rejection of a degenerate transport
edge, at both resolutions. Two supplementary cases explicitly sweep D through
a degeneracy with gapped endpoints and require rejection, bringing the new
analytic total to ten. Source bindings of the eighteen parent analytic
cases are verified; those eighteen results are reused, not rerun here.

This checkpoint tests refined sampled transport and the associated based-path
conjugation in the finite N8 model. It does not establish full braid acceptance,
an Euler-class change, novelty, an infinite-cutoff limit, or a laboratory
control protocol. The two engines share the diagnostic implementation.
Strain remains fixed and D supplies layer potentials ±D meV.
