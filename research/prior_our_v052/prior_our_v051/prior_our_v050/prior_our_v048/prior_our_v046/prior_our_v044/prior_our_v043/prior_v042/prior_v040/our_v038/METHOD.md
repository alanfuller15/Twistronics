# v038 protocol and limitations

## Scope

We continue the v037 first-braid work with fixed-direction event windows from
the supplied v029, v031, v032 and v033 logs. Their text is preserved in sources/.
The primary original and partner engine files are unchanged copies. models.py
adds the layer-antisymmetric sine harmonic separately in their respective
orderings. Matrix checks against the legacy original model cover N=4/N=6,
three later states and two momentum points, including an unwrapped point.
The partner wrapper is exactly unchanged when the added amplitude is zero.

This is not a continuous replay of every connecting leg. In particular, earlier
strain-direction sweeps and transfer legs, and all intervening node inventories,
remain outside this entry. The fixed-phi cleanup after braid 2 is included.
Keeping the direction fixed also avoids comparing
frames across a changing hard-cutoff basis. No unrecorded basis identification
is assumed.

## Second braid

At (A,B,T,phi,theta,eps)=(0,-0.4,-0.8,80 degrees,1.05 degrees,0.003), vary the
AA/AB ratio from 0.99 to 1.00. Track two upper-gap nodes and four upper-next-gap
nodes at 11 parameter states. U2 is explicitly lifted near f2=1.013; its
coordinates are not wrapped after refinement. Initial seeds came from a
documented discovery pilot, before measuring the path labels.

Carry each upper-node frame through parameter space. Separately compare them
by transport across the current center-to-center segment. Require loop charges
to agree at 64/128 points and radii 0.006/0.003. Spatial transport uses 128/256
intervals augmented near tracked adjacent nodes; parameter transport uses steps
0.001/0.002. Root the adjacent-node crossing and require the frame gate to
reject the singular connecting path. Individual temporal charges must remain
constant and spatial labels must change at the located event. These are
hypotheses under test; a mismatch is retained as a rejected replay.

The frozen second_acceptance_plan.json identifies the measured source hashes.

## Four collision windows

| Event | Fixed settings | Varying parameter |
| --- | --- | --- |
| First flat annihilation | A=0, B=-0.4, phi=65, ratio=0.8 | T: -0.70 to -0.74 |
| Upper annihilation | A=-0.35, B=-0.4, T=-1.8, phi=80 | ratio: 1.00 to 1.10 |
| Flat birth | Same as upper annihilation | ratio: 1.00 to 1.10 |
| Final flat annihilation | B=-0.4, T=-1.8, phi=80, ratio=1.10 | A: -0.35 to -0.30 |

For every engine and cutoff, locate two zero components of the selected real
2x2 Hamiltonian simultaneously with a zero determinant of its spatial Jacobian.
Require node gap below 10^-6 meV, the small Jacobian singular value below 10^-3,
the large one above 1, and external isolation above 10^-5 meV. Repeat with
finite-difference steps 2e-5 and 1e-5; event parameters must agree within 1e-6.

Continue the distinct pair through nine states on its existing side, ending
0.001 in parameter from the collision. Require no duplicate roots or jumps and
decreasing separation toward the event. Measure opposite relative charge at
the first and last state. A supplemental local check requires nonzero quadratic
curvature along the null direction and a transverse parameter derivative, both
stable under step halving, and the predicted side of pair existence must agree.

On the open side, use multistart gap minimization on an 18x18 grid at distance
0.001 from the event and 18x18/24x24 grids at the recorded window endpoint.
Analytic eigenvalue gradients use the affine Hamiltonian derivatives. Failed
L-BFGS-B attempts fall back to SLSQP from the original seed; success and a result
no worse than that seed are mandatory. Refined grids must agree within 0.01 meV.
All searches stay in the explicit [0,1]^2 chart. No periodic wrap changes a
computed value. Positive-gap acceptance requires a minimum above 10^-5 meV.

These are finite global searches, not certified lower bounds over every point.
Rank-one collision, distinct approaching roots, opposite charges and an open
side support annihilation; failed optimizers or missing grid nodes do not.

## Resolution amendment

The original first-annihilation N4 run rejected a 64-point winding loop near
the collision: phase increments were unresolved. Its JSON and log are retained.
A diagnostic needed 256 points at one node. The frozen amendment raises only
loop sampling to 256/512, with 1024/2048 fallback for that specific rejection.
It keeps phase, isolation, overlap, integer, radius and mesh-agreement gates.
Refined runs have separate filenames, leaving the failed attempt intact.

## Gapped-state checks

N4 collision locations motivated a new hypothesis: upper annihilation and
flat birth may be separated by an open interval. This was registered before
checking the bridge point (A,T,ratio)=(-0.35,-1.8,1.04). Both engines and cutoffs
receive all-four-gap searches and cycle checks. The recorded final endpoint
(-0.30,-1.8,1.10) receives the same checks.

For four individual bands and the flat pair, compare cycle signs along both
reciprocal directions, offsets 0 and 0.5, meshes 64 and 128. Enforce external
isolation, consecutive-frame overlap >0.1, sewing singular value >=0.95 and
sewing norm loss <=0.02. Require agreement across meshes and offsets. A
non-orientable flat pair is reported with w1, never assigned an Euler class.

## Cleanup continuation

The accepted second-braid endpoint at ratio=1.0 supplies the upper-pair seeds.
At fixed phi=80 and B=-0.4, follow T:-0.8 to -1.2, A:0 to -0.2,
T:-1.2 to -1.8, and A:-0.2 to -0.35. Four intervals per leg give 17 states;
two intervals per leg check parameter-transport orientation. The cutoff basis
is fixed along all four legs. Require the final node positions to match the
accepted upper-annihilation initial nodes within 10^-6, allowing a pair swap.

Carry individual frames, compare spatial orientation, and test charge loops
at 128/256 points with radii 0.004/0.002. The adjacent-node count is not assumed
constant. Instead, locate sampled local minima of both exterior gaps along
each connecting segment with bounded scalar minimization, add graded samples
around them, and compare 128/256 transport meshes. An unresolved or singular
path rejects the replay. This establishes continuity of the known pair, not an
exhaustive inventory of every band crossing along the cleanup.

## Boundary-search amendment

The original N6 endpoint lower-gap search returned 22.7087735 meV at x=0,
although the earlier work had found 22.6919848 meV near x=0.99095. Comparing
those records exposed a weakness: periodic-neighbor grid minima selection plus
bounded refinement can suppress a basin near the other side of the seam.
Agreement at two grid sizes did not catch it.

boundary_audit.py keeps the initial records and repeats every bridge/endpoint
gap search with extra corners, edge centers, all prior refined minima, and an
opposite-boundary seed for each minimum within 0.1 of a seam. Every added seed
is reevaluated; no energy value is wrapped. Both grids and all existing floors
still apply. It also checks the gap below the lower remote band, which is
needed to interpret that band's cycle signs globally. Final tables use the
amended minima, and changed values are listed in superseded_minima.json.

## Common gates and limits

Eight central eigenpairs are checked for finite values, Hermiticity/reality
residuals below 10^-9 meV, relative eigen residual below 10^-10 and orthogonality
below 10^-8. Every selected frame checks both external gaps. Each transport and
local chart requires overlap singular values above 0.1. Optimized Python must
not remove any acceptance condition; runtime checks use exceptions, not assert.

Two Hamiltonian engines share one measurement harness and numerical libraries.
Their physical approximations differ; neither is a complete independent
physical validation. N=4/N=6 agreement of labels does not imply all gap values
or event parameters have converged. No N>6 check, all-path proof, exhaustive
node-birth exclusion or complete quaternion charge algebra is claimed.

The partner topology estimators are not acceptance gates. This entry does not
repeat all historical tests or the static audit; it checks newly used source
and the numerical mechanisms needed for the specified windows.
