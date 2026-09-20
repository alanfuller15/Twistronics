# TEAM SHARE — v044

Both v043 contributions are retained separately: yours adopts v042 and
updates the toolkit; ours supplies the two later connecting routes. The
guard patch is verified byte for byte. All 29 supplied tests and ten guard
regressions pass against your adopted code.

The earlier connection is now measured too. Braid 1, deepening B=-0.30 to
-0.40, and T=0 to -0.40 pass in both engines at N=4 and N=6: 148 primary
sampled states. The spatial label changes SAME to OPPOSITE at the located
upper-node crossing, remains OPPOSITE through both connecting legs, and
joins our v043 starting roots and frames. Individual carried charges stay
constant. Endpoint root mismatches are below 3e-15, with the relative frame
orientations recorded rather than assumed.

| Engine / geometry | N4 center-path B | N6 center-path B |
|---|---:|---:|
| BM / linear | -0.2901737962 | -0.2901702643 |
| TBG / exact | -0.2901753967 | -0.2901718633 |

These are lab_nn_full values. Keep the older approximately -0.28594
(original/no velocity tensor) and -0.28795 (legacy I-E prescription) under
their historical model labels. Moving the comparison segment by 0.012 in
f1 shifts the new crossing to about -0.27998; the crossing parameter is
path dependent. Each singular comparison is rejected by the isolation
gate. These numerical digits do not specify physical precision.

The exact-geometry implementation is verified more broadly than the two
band comparisons: 24 full-matrix checks span six states, both cutoffs and
ordinary/unwrapped momenta, with maximum difference 1.4e-12 meV. Separate
BM-exact crossing controls agree with TBG-exact to below 4e-15 in B. The
primary BM-linear path remains labeled linear, preserving its historical
meaning. Our replay still uses a common measurement harness; this is not a
new two-estimator comparison.

One remaining qualification to “differ only in their estimators” is real:
cutoff padding is 1e-6 in BM versus 1e-9 in TBG. At N=4, eps=0.003,
phi=15.843560625 degrees and exact geometry, two reciprocal indices sit
between those margins, giving dimensions 196 versus 188. The campaign
checks still agree where their bases match. This counterexample establishes
a truncation difference, not a demonstrated topological mislabel.

An optional patch adds explicit cutoff_tol to both engines and preserves
both old defaults. Eight tests pass: the witness matches in basis and full
matrix with either common tolerance; default matrices stay bitwise intact;
invalid padding is rejected. It is not used in the primary measurements.
For strict matched-model comparisons, name kinetic, geometry, N and padding.

Next measured batch: the fixed-phi cleanup and later collision windows after
braid 2. The lower-pair unlinking collision itself and the preparation from
the original baseline are not newly resolved here. Tunneling strain law,
N>6 endpoint convergence and physical-bilayer validation remain open.
Finite sampling is not an interval proof or an exhaustive node inventory.

Minor record corrections: the incoming ZIP has 20 numbered log files, not
21; its detailed event table is correct, but the short note's BM N6
annihilation value rounds to -0.71330, while -0.71331 belongs to TBG. The
geometry keyword is available on BM; TBG has fixed exact geometry. Its
introductory I-E kinetic formula also needs updating to describe the
selected lab_nn_full branch.

Package: twistronics_v044_reconciled.zip — your unchanged v043, our complete
prior v043 delivery, new protocol/source/records/frames, exact controls,
tests, the cutoff witness and optional patch, and this note.
