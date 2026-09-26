# Research questions 003: controlling unsampled variation

This pass replaces a proposed reliance on additional passing meshes with
**analytical variation bounds for explicit models**. It also executes Claude's
nested-grid counterexample through the unchanged archived Euler routine.

The result is a usable local resolution/isolation screen and its limits,
not a certified Euler invariant or new graphene result.

## Results

The actual run exited 0 in 4.70 seconds. All **21 declared predicates** held;
these include expected false acceptance by the sampled routine and expected
inconclusive outcomes from a conservative bound. The count is not a count of
independent scientific validations.

### A false answer can survive both nested grids

| 97-fold synthetic texture | 48 × 48 | 96 × 96 |
|---|---:|---:|
| Analytic oriented Euler number | 194 | 194 |
| Archived routine's oriented estimate | 1.999999999999996 | 1.999999999999996 |
| Minimum sampled link overlap | 0.9914448614 | 0.9978589232 |
| Maximum matrix difference from the once-folded grid | 1.12e-13 | 1.48e-13 |
| New full-cell projector variation bound | 12.82817 | 6.41409 |
| New local-chart screen (`bound < 1`) | Not certified | Not certified |

The analytic Euler value follows from the known reference's degree and a
97-fold torus covering. Both arrays of sampled Hamiltonians alias to the
once-folded model. The routine really returned the wrong integer for this
constructed texture; it was not run at a high resolution that resolves 97
folds. Its old sampled guards are unchanged.

For the once-folded reference, the full-cell variation bounds are 0.261799
and 0.130900, respectively, which meet the local-chart condition. The
49-fold case is also refused by this screen on both grids. Failure of a
sufficient bound means **unresolved**, not necessarily an incorrect answer.

### A bound for the retained projected Hamiltonian

For `vafek_2025/model.py:Model.direct_projection` with its retained default
parameters, the complete projected expression can be written `H=V^dagger A V`.
The derivation includes the changing basis V, not only the kinetic terms.
It gives the global bound

```
||H(K',Q')-H(K,Q)||_op <= 94 ||K'-K||_2 + 47 |Q'-Q|  meV.
```

K and Q are dimensionless coordinates defined by that source. At fixed
Q=0.5, each declared disk of radius 0.001 therefore has a uniform Hamiltonian
variation bound of 0.094 meV. For the middle ordered pair:

| Disk centre K | Centre external gap (meV) | Gap lower bound throughout disk (meV) | Coefficient-projector variation bound |
|---|---:|---:|---:|
| (0, 0) | 5.519890 | 5.331890 | 0.024501 |
| (0.23, -0.17) | 2.079565 | 1.891565 | 0.066952 |
| (0.4, 0.2) | 6.995612 | 6.807612 | 0.019262 |

The same sufficient gap test is inconclusive at all three declared larger
radii of 0.1. It does not falsely turn those negative lower bounds into a
claim of gap closure. Eight fixed boundary witnesses per disk satisfy the
bounds; the uniform statements come from the derivation, not from those
samples.

The bound for the embedded eight-component projector includes an additional
`2*rho` from basis motion. Both coefficient and ambient bounds are recorded.
This distinction matters before interpreting transport geometrically.

## Evidence and reproduction

- [DERIVATION.md](DERIVATION.md): full-cell reference bound, exact projected
  representation, rational parameter bound, gap and projector inequalities.
- [PLAN.json](PLAN.json): fixed cases, thresholds, expectations and five source
  identities recorded before this run. This is workflow provenance, not
  independent timestamp attestation.
- [bounds.py](bounds.py): imports the previous adapter and source model without
  editing either; uses the original archived production module for both alias runs.
- [RESULTS.json](RESULTS.json), [RUN.log](RUN.log), [RUN_RECEIPT.json](RUN_RECEIPT.json):
  actual results and process status. Numerical boundary witnesses are retained.
- [MANIFEST.json](MANIFEST.json): SHA-256 hashes of this package, excluding itself.

From the repository root, using the pinned dependencies of questions 001:

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -B research/benchmarks/research_questions_003/bounds.py --output NEW_DIRECTORY
```

An existing output directory is refused. The archived routine uses the same
declared policy as questions 002: its default overlap floor 0.5 and the
stricter phase ceiling pi/2. Basis and sewings are identity for the synthetic
torus; finite-cutoff TBG sewing is not exercised. Raw winding is converted
using `oriented_euler=-fibre_orientation_at_origin*raw_winding`, with the
previously declared base orientation. The renamed field makes its fibre
meaning explicit; historical files are untouched.

Full frame/link diagnostic streams are hashed; selected extrema, refusals
and complete Wilson phases are retained, not the full streams. The tests
check assembly against the retained 12-component implementation. They are
not an independently authored physical model or independent validation.

## What remains open

The local inequalities are analytical, but centre eigenvalues use ordinary
floating point, not interval enclosures. The six disks do not cover a
physical research domain. The bound applies to the direct-projection family;
it does not decide between the paper's sign conventions or justify changing
the other retained family.

The next proof obligation is to connect a declared continuous interpolation
of sampled projectors to the true bundle, with orientation and boundary
sewing accounted for, and then to the actual Wilson estimator. Passing a
local chart or gap screen is not that certificate. No Fable repairs,
graphene parameter sweep, node search, braiding or experimental claim was
made.

This pass responds to [Claude's nested-grid and variation-bound review](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5789862439)
and [the recorded qualification](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5287430089).
Partner review of this new derivation and execution is requested separately;
the earlier 26-check reproduction does not constitute review of this pass.
