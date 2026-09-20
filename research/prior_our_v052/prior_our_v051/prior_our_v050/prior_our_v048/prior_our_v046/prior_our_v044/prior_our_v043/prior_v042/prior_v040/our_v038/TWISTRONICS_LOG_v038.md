# TWISTRONICS LOG — v038 — Later braid, collision events, and an earlier gapped endpoint

**A resolved gapped intermediate state changes the sequence description.**
On the v032 ratio leg at A=-0.35, B=-0.4, T=-1.8 and phi=80 degrees,
the upper pair annihilates before the flat pair is born. Both declared engines,
at N=4 and N=6, have a numerically resolved gapped state at ratio=1.04 between
those events. It already carries the same measured band-by-band w1 as the
recorded v033 endpoint: (1,0) on the lower flat band and (0,0) on the other three
examined individual bands.

The second braid and all four collision windows pass the refined gates in both
engines and cutoffs. The original endpoint remains supported. What changes is
the implication that the upper-pair disappearance must be accompanied by a new
flat pair: the coarse ratio step hid an intervening gapped region. The later
birth and final annihilation are unnecessary to obtain a gapped state with this
measured w1, once this ratio leg has been reached.

The fixed-basis cleanup from the second braid to the upper-collision leg is
also traced in both engines and cutoffs. This supplies a connected sampled
route from the second braid to the earlier endpoint. It does not certify every
earlier trajectory in the campaign.

## Resolved event ordering on the v032 ratio leg

All rows use A=-0.35, B=-0.4, T=-1.8, phi=80, theta=1.05 and eps=0.003.
The listed bounds locate two known folds; they are not a proof that no other
event exists anywhere in the interval.

| Engine | N | Upper annihilation ratio | Flat birth ratio | Separation in ratio |
| --- | ---: | ---: | ---: | ---: |
| original | 4 | 1.023709780 | 1.052830523 | 0.029121 |
| original | 6 | 1.022522824 | 1.051964364 | 0.029442 |
| partner | 4 | 1.022283939 | 1.052869664 | 0.030586 |
| partner | 6 | 1.021099856 | 1.052000173 | 0.030900 |

v032's “in the same step” can stand as a description of its coarse sampling.
It should not be carried forward as a simultaneous event or an unavoidable
three-band sequence. This correction was found by locating the collisions and
then testing a point between them, not inferred from a failed node search.

## Gap checks at the earlier endpoint, ratio=1.04

Each number is a refined minimum in meV. The 18x18 and 24x24 multistart searches,
augmented with explicit edge and opposite-seam seeds, agree within tolerance.
They are numerical minima, not rigorous lower bounds over a continuum.

| Engine | N | Lower gap | Flat gap | Upper gap | Upper-next gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| original | 4 | 30.337471 | 1.383211 | 0.886562 | 7.762370 |
| original | 6 | 30.481637 | 1.301338 | 0.946235 | 7.794359 |
| partner | 4 | 30.557212 | 1.392171 | 0.969468 | 7.813039 |
| partner | 6 | 30.700512 | 1.309302 | 1.028947 | 7.844905 |

Both flat bands are individually isolated here. Cycle signs pass two offsets
and meshes 64/128 along both reciprocal directions, including sewing norm and
overlap gates. The additional lower-remote outer-gap search passes as well.

| Examined band/group | w1 along k1 | w1 along k2 |
| --- | ---: | ---: |
| Lower remote | 0 | 0 |
| Lower flat | 1 | 0 |
| Upper flat | 0 | 0 |
| Upper remote | 0 | 0 |
| Flat pair | 1 | 0 |

These signs agree at the earlier and recorded endpoints, for both engines and
cutoffs. No Euler class is assigned to the non-orientable flat pair. This table
does not characterize unexamined remote bands.

## Second braid: mechanism reproduced

At (A,B,T,phi)=(0,-0.4,-0.8,80), the center-to-center comparison of the upper
pair flips SAME to OPPOSITE as an upper-next node crosses the segment. Each
individually carried charge remains unchanged. The singular path is rejected.

| Engine | N=4 crossing ratio | N=6 crossing ratio |
| --- | ---: | ---: |
| original | 0.990298568 | 0.990526654 |
| partner | 0.990414949 | 0.990642705 |

The path definition is the node-center segment in the recorded unwrapped chart;
the second node lies near f2=1.013. As v037 established, a loop-starting-point
segment can cross at a different parameter. Cutoff agreement of the mechanism
does not make the displayed root digits cutoff-converged.

## Cleanup connects the second braid to upper annihilation

At ratio=1.0, B=-0.4 and phi=80, the replay follows four recorded legs:
T:-0.8 to -1.2; A:0 to -0.2; T:-1.2 to -1.8; A:-0.2 to -0.35.
Seventeen parameter states carry the same two upper nodes. Their individual
temporal charges remain unchanged and their spatial comparison stays OPPOSITE.
Parameter step halving and spatial/loop refinements agree in all four runs.

The endpoint nodes match the separately measured upper-annihilation starting
nodes within 10^-6 in fractional coordinates. Adjacent-node counts are not
assumed fixed: connecting-path sampling explicitly minimizes both exterior
gaps and resolves their narrow regions. This traces the known pair's identity
through the cleanup; it does not inventory every possible new node elsewhere.

## Other collision locations

| Event and parameter | Original N=4 | Original N=6 | Partner N=4 | Partner N=6 |
| --- | ---: | ---: | ---: | ---: |
| First flat annihilation, T | -0.715140898 | -0.715056121 | -0.714296417 | -0.714217425 |
| Final flat annihilation, A | -0.317762476 | -0.317132337 | -0.317751935 | -0.317120187 |

Each collision has a rank-one zero, stable under derivative-step halving, two
distinct approaching roots, opposite charges before collision, a positive gap
on the other side and a nondegenerate local fold check. The flat-birth run
applies the same tests with the pair on the increasing-ratio side.

The first N4 original annihilation run rejected its coarse winding mesh near
the collision. Its record is preserved. An explicit amendment raised the loop
resolution to 256/512 points, with a higher-resolution fallback, without changing
any acceptance tolerance. The accepted replacement retains the same collision
and opposite-charge conclusion.

## Boundary-search correction

A comparison to prior measurements exposed a missed seam-near minimum despite
agreement between two grids: the original N6 endpoint lower gap was initially
22.7087735 meV at x=0, while a lower minimum lies near x=0.99095. The periodic
grid-neighbor rule plus bounded refinement could suppress that second basin.
The amendment seeds edges, corners and the opposite boundary of seam-near
minima, and repeats all bridge/endpoint gap checks. Tables use those amended
results; original records and every changed minimum are retained. No gap or
cycle label is changed by this correction. Grid agreement alone is therefore
not treated as a certificate of a global minimum.

## Recorded endpoint remains supported

At A=-0.30, T=-1.8 and ratio=1.10 (other parameters as above):

| Engine | N | Flat gap, meV | Upper gap, meV |
| --- | ---: | ---: | ---: |
| original | 4 | 2.868925 | 3.151484 |
| original | 6 | 2.776540 | 3.208887 |
| partner | 4 | 2.866381 | 3.237122 |
| partner | 6 | 2.773610 | 3.294381 |

All four monitored gaps and the additional lower-remote outer gap are resolved
positive. The measured w1 labels match the table above. Gap magnitudes retain
cutoff dependence; positivity and the selected topological labels are the
conclusions supported here.

The earlier endpoint shortens the sequence. The recorded final endpoint has
larger flat/upper gap margins, so it remains a useful separate reference rather
than being discarded.

## Strain convention result

The coordinate algebra is resolved for a specified nearest-neighbor monolayer
hopping model. With lab strain E and layer rotation R, F=(I+E)R, the first-order
kinetic matrix in crystal Pauli axes is R^T[I+(1-beta)E]. The gauge shift is
computed from R^T E R and rotated back to the lab. An independent bond-level
calculation passes 36 checks, with second-order residuals under strain halving.
See STRAIN_CONVENTION.md and
[Oliva-Leyva–Naumis, Eqs. 13–15](https://arxiv.org/pdf/1404.2619).

That resolves what the chosen monolayer approximation predicts; it does not
uniquely validate a full strained bilayer, its relaxation, or tunneling. The
two replay engines retain their original declared approximations. The roughly
4% remote-gap shift therefore remains model sensitivity, not a uniquely derived
physical correction. Adopting a revised bilayer requires a separately labeled
implementation and sensitivity run.

## Findings and next actions

| Priority | Finding | Effect on recorded conclusion | Action |
| --- | --- | --- | --- |
| 1 | Gapped state lies between upper annihilation and flat birth | Revise the coarse v032 sequence description; v033 endpoint labels stand | Carry ratio=1.04 as an earlier endpoint candidate |
| 2 | Earlier strain-direction and transfer legs remain untraced | Second braid through cleanup is connected; the full campaign is not yet a continuous replay | Replay the earlier legs with basis-aware continuation |
| 3 | Strain models omit different terms | No unique physical correction established | Adopt an explicit kinetic/gauge/tunneling convention before changing the reference model |
| 4 | Near-collision loop was under-resolved | Gate rejected it; refined result preserves the charge label | Retain the resolution amendment and failed evidence |
| 4 | A seam-near gap minimum escaped two-grid agreement | Amended minima change; positive gaps and cycle labels stand | Keep explicit edge and opposite-seam seeds |
| 5 | Event parameters and gap magnitudes shift with cutoff | Label agreement is stronger than magnitude convergence | Quote model, path and cutoff beside numbers |

## Evidence and limits

The package contains four second-braid and four cleanup replays, sixteen collision
windows, eight gapped-state checks with boundary and outer-gap checks, seven focused tests passing normally
and under -O, model assembly comparisons and the 36 strain checks. The historical
21-test suite passed in v037 and is not claimed as newly rerun here. Protocol
hashes, source hashes, failed attempts, environment and raw measurements are
included. All primary jobs ran in at most two concurrent processes with one
BLAS thread each.

This work uses two Hamiltonian engines but a shared measurement harness and
numerical libraries. It checks finite parameter and momentum samples. It does
not exclude every unseen node birth, cover N>6, prove complete quaternion charge
algebra, or replay the entire route from v023. No static-scanner flag is used
as evidence for a topological verdict. The earlier strain-direction and transfer
legs still need measurement before claiming an end-to-end campaign replay.
