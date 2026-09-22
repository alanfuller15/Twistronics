# Attaching continued nodes to a transported contour

This checkpoint combines three already published pieces of evidence: the
`r1_temporal` based-contour geometry and frame transport, `r1_surface` isolation
of the complete swept contour, and `r1_continuation` local node branches.
It adds a continuous geometric test linking those particular contours and
those particular branches. It changes no Hamiltonian, node path, contour or
charge convention, and makes no new eigensolve or band-charge measurement.

All conclusions inherit the earlier floating-point assumptions. The new
geometric calculations also use ordinary floating point with declared
allowances, not outward-rounded interval arithmetic.

## What is interpolated

For each adjacent pair of original D stations, every contour vertex follows
its declared affine interpolation. The ring consists of 64 or 128 oriented
polygon edges. The outgoing stem has two segments: base to kink, and kink to
the ring anchor. The incoming stem retraces them exactly.

The source vertices are checked against **all** previously bounded bilinear
surface-face corners. Thus the moving contour is the one covered by the
inherited spectral-isolation result, not a newly fitted circle. The continuation
input supplies boxes in `(f1,f2,E)` around affine predictors. Their `(f1,f2)`
projections contain the actual locally unique node under the inherited
conditions. We retain the original outer boxes, without shrinking their radii.

Partition D at the union of all contour stations and all accepted node-tube
endpoints. Each test interval then lies inside one source contour interval and
one source tube for each node. Affine interpolation and fixed box radii are
valid over the entire test interval. Failed bounds can be bisected under the
frozen depth limit; all parents and unresolved leaves remain in the record.

## Quadratic side bounds

Let a moving oriented polygon edge run from `a(t)` to `b(t)`, and let a moving
point be `x(t)`, all affine in normalized `t ∈ [0,1]`. Write
`e(t)=b(t)-a(t)` and `z(t)=x(t)-a(t)`. The oriented area

```
s(t) = cross(e(t),z(t))
     = B0 (1-t)² + 2 B1 t(1-t) + B2 t²

B0 = cross(e0,z0)
B1 = [cross(e0,z1)+cross(e1,z0)]/2
B2 = cross(e1,z1).
```

The three weights are nonnegative and sum to one. Therefore `min(Bi)` and
`max(Bi)` bound `s(t)` over the whole interval. This is a polynomial bound,
not a collection of endpoint or midpoint sign tests.

For each edge, every nonincident polygon vertex must have a strictly positive
lower side bound. These inequalities make the polygon simple, strictly convex
and counterclockwise throughout the interval. Merely checking consecutive
turns would allow some self-intersecting star polygons and is not used.

For **q**, test the four corners of its moving momentum box against every
polygon edge. A positive side bound for all corners and edges puts the whole
box inside the polygon, since side expressions are affine in point position.

For **p** and **upper**, require one fixed edge per node and interval with a
strictly negative upper side bound for every box corner. That half-plane
separates the entire box from the convex polygon for the entire interval.
The algorithm does not interchange the quantifiers: it must find an edge that
works uniformly, rather than selecting a different edge at each sampled D.

To report a clearance, divide a positive area bound by
`L=max(||e0||,||e1||)+length_allowance`. Because the norm of an affine vector is
at most this value, the quotient bounds the perpendicular distance from below.
Subtract the declared length allowance and require more than `1e-7` in
fractional-coordinate Euclidean units. These are not Cartesian reciprocal-space
distances. A negative normalized test margin is a failed sufficient condition,
not a measured physical intersection distance.

## Stem avoidance

A side-of-line test alone can fail when a node lies beyond a segment endpoint.
For each stem segment, choose one fixed nonzero axis `n` directed from the
midpoint box center toward the closest point of the midpoint segment.
Choosing this axis is only a heuristic for finding a separator; the acceptance
inequality is uniform and independent of whether the heuristic was optimal.

If the node-box predictor is `c(D)`, its halfwidths are `r`, and the two segment
endpoints are `v0(D),v1(D)`, then for every point on the segment and every point
in the box,

```
n·(segment_point - box_point)
  >= min_{D endpoint, segment endpoint} n·(vi(D)-c(D)) - |n|·r.
```

Affine dependence on D and convex dependence along the segment justify the
endpoint minimum. Divide a positive projection bound by the axis norm, include
the declared allowance, and require the same strict clearance gate. This
excludes both complete moving stem segments from all three tracked node boxes.
The return stem needs no duplicate geometry calculation.

## Consequence and limits

A simple counterclockwise polygon containing q has **geometric winding +1**
about its continued local branch. The separating half-planes give winding zero
about p and upper. The out-and-back stem contributes zero geometric winding and
avoids all three node neighborhoods. The conditional continuation and endpoint
joins ensure these labels refer to the same branches throughout D38–39.

Together with the inherited gapped swept-contour result, this attaches that
specific transported loop to q while excluding the other two tracked branches.
Its previously measured `+k` real-frame loop charge is reused, not remeasured.
Geometric winding is a statement in momentum space; it is not the frame charge
or an Euler invariant.

**No inventory of unknown nodes inside the polygon is supplied.** Local
uniqueness holds inside the much smaller continuation boxes, not throughout
the polygon interior. Consequently this checkpoint does not establish that q
alone accounts for the inherited loop charge. It also does not establish a
complete braid, an Euler-class change, novelty or experimental realization.

For the distinct role of based contours and conjugation in non-Abelian band
topology, see Wu, Soluyanov and Bzdušek,
[Non-Abelian band topology in noninteracting metals](https://arxiv.org/html/1808.07469v3),
Supplement IV.3. The elementary geometric bounds above are derived here; they
do not replace the Hamiltonian-based topology calculation.

## Floating-point and audit details

The frozen area allowance is `1e-14` in squared fractional-coordinate units;
the length allowance is `1e-10`. They are declared numerical allowances, not
proved roundoff enclosures. Nonfinite arrays, unclosed rings and degenerate or
incorrectly oriented polygons do not pass. Source hashes bind every reused
summary, model/measurement source, numerical record and array archive.

The independent report reconstructs the same geometry from retained sources.
It expands each side polynomial in the power basis and checks its analytic
extrema, reconstructs Bernstein bounds independently, checks stored witnesses,
and directly enumerates box corners for stem projections. It also checks exact
coverage, parent-child partitions and all inherited acceptance/hash conditions.
No inherited controls, spectral evaluations or charge measurements are counted
as new work. The new analytic controls are listed in `CONTROLS.json`.

N remains 8, strain remains fixed, and tunnelling is constant. D sets opposite
layer potentials `±D meV`, with layer difference `2D`; it is not a calibrated
experimental displacement field. Both independently coded Hamiltonians share
this geometric and numerical diagnostic framework.
