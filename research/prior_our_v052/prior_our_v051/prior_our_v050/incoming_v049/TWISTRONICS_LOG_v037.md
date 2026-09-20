# TWISTRONICS LOG — v037 — First-braid path replay

**The sampled first-braid replay supports the proposed adjacent-gap mechanism.**
In both Hamiltonian engines, at N=4 and N=6, the upper-gap node crosses the
center-to-center F1–F3 segment where its spatial relative-charge comparison
changes from SAME to OPPOSITE. Each node's charge carried continuously along its
own trajectory remains unchanged. At the crossing, the connecting segment loses
flat-pair isolation and the gate rejects its transport.

This is stronger evidence than matching two endpoints. It identifies the tracked
crossing, checks its location, measures the resulting orientation reversal and
refuses to assign a charge comparison on the singular path. It remains sampled
numerical evidence with a shared measurement harness, not a proof for the entire continuum or a full
independent derivation of non-Abelian quaternion charge algebra.

## Located center-path crossings

| Hamiltonian | N=4 | N=6 |
| --- | ---: | ---: |
| Original campaign approximation | -0.285942906 | -0.285941535 |
| Team exact-geometry / I-E velocity variant | -0.287952970 | -0.287950576 |

These two rows use different kinetic/geometry approximations. Their difference
is model sensitivity, not a numerical disagreement between equivalent bases.

## Path definition changes the reported flip location

Previous estimators connected loop-starting points displaced from the node
centers. The singularity of that shifted segment occurs at a different B:

| Common fractional x shift | Original N=6 | Team variant N=6 |
| --- | ---: | ---: |
| 0.000 | -0.285941535 | -0.287950576 |
| 0.006 | -0.280834822 | -0.282771467 |
| 0.012 | -0.276052481 | -0.277918218 |
| 0.020 | -0.270091913 | -0.271865319 |

Only the center path has the full 21-state charge replay here; shifted rows are
geometric singularity roots with explicit isolation rejection. Consequently,
"the flip occurs at B≈-0.285" must name its path convention. The measured center-path
endpoint labels are SAME at -0.25 and OPPOSITE at -0.30. The precise intermediate
crossing locations are not interchangeable between path definitions.

Temporally carried frames and newly spatially compared frames differ by a
negative orientation after the crossing. This is the measured holonomy around
the parameter–momentum rectangle bounded by the initial connecting segment,
the node trajectories, and the current segment. It explains why a spatial
comparison flips while the continuously carried local charges do not.

## What was verified

Four replays cover 21 parameter states each and six tracked nodes per state
(two flat-gap, two upper-adjacent, two lower-adjacent). Local charges pass two
meshes and a halved radius; parameter transport is checked at steps 0.0025 and
0.005. Spatial transport uses 128/256 intervals with extra samples near tracked
adjacent nodes. Node roots, reality, Hermiticity, eigen residuals, isolation,
phase resolution and overlap checks are enforced. No threshold was relaxed.

The largest tracked node gap is 1.83e-12 meV; the smallest transport overlap singular value is 0.966034. All 16 located singular paths are rejected for loss of isolation.

The four harness tests pass normally and under -O. All 21 tests supplied with
the team archive also pass. The runtime was Python 3.12.14, NumPy 2.3.5 and
SciPy 1.17.0; this differs from the uploaded dependency pins. Source inspection
preceded execution. The archive contains 14 logs, 83 files and one directory
entry (84 entries).

## Qualifications to the team v036 claims

The second implementation is useful, but several statements should be narrowed:

- **Basis/truncation:** at the tested N=4/N=6 baseline, the retained integer
  indices are identical. origin-K^(2)=q0 algebraically recovers the offset-layer
  relative momentum. A different momentum description does not establish a
  different retained finite basis in these cases.
- **Real basis:** the antiunitary construction produces exactly the same
  canonical real-basis matrix, although it constructs it by a different route.
- **Exact agreement with velocity off:** small residuals remain from exact
  versus linearized strain geometry. The checked band-energy differences reach
  0.00025943 meV; the largest checked matrix-entry difference is 0.00404124 meV.
  “Very close agreement” is supported; “exactly identical” and “the entire
  difference comes from velocity” are too strong.
- **Physical correction:** the team’s (I-E)R(-theta) tensor and my previous
  R(-theta)(I+E) sensitivity variant are different insertions. Neither alone
  establishes the uniquely correct strained-graphene kinetic term.

For the last point, a uniform-strain tight-binding derivation includes both
geometric and hopping contributions, v/vF=I+E-beta E, in its stated coordinates
([Oliva-Leyva–Naumis, Eqs. 14–15](https://arxiv.org/pdf/1404.2619)). The geometric
factor in [Bi–Yuan–Fu, Eq. 9](https://arxiv.org/html/1902.10146v1) should not be
confused with this complete hopping-sensitive tensor. The signs and layer/lab
frame mappings need an explicit agreed derivation before treating the ~4% shift
as a definitive correction rather than a sensitivity estimate. This does not
undo the observed robustness of the selected labels.

## Deliverable and remaining work

METHOD.md gives the exact protocol; acceptance_plan.json was frozen before
path labels were measured. The discovery pilot and raw checkpoints, tests,
source hashes and environment record are included. The static figure is
figures/first_braid_replay.png. The team upload and both prior archives are
unchanged; this package adds an auditable replay.

The primary Hamiltonians differ, but the gated measurement harness is shared.
The partner’s original charge/Euler methods were not used as acceptance gates.
Known-node continuation cannot exclude additional nodes born between samples.
This work does not replay the later braid, full annihilation sequence, final
endpoint, or N>6, and does not independently establish a global Euler invariant.
The next physical-model decision is to agree the full strain-dependent kinetic
and tunneling assumptions; the first-path mechanism now has explicit numerical
evidence in both currently defined variants.
