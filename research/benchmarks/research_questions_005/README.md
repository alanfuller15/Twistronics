# Research questions 005: general projector transport

This pass derives a direct error bound between a sampled polar-overlap link
and continuous Kato transport for finite-dimensional C2 projectors. It also
proves the sharp affine-spinor acceleration bound suggested in
[Claude's questions-004 audit](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5790331404).
Both derivations are submitted for partner review. Earlier evidence is frozen.

## Result and meaning

For a projector path with uniform `||P'||<=p`, `||P''||<=q` on an entire
edge of length h, and `p^2*h^2/2<1`, the polar link differs from the true
backward transport by at most

```
epsilon = p*(q+p^2)*h^3 / [6*(1-p^2*h^2/2)].
```

The operator-norm comparison holds for any rank. For real oriented rank two,
the proof also bounds the continuously lifted angle by epsilon. It obtains
this from a polar homotopy's length, rather than treating a norm bound as an
angle bound. The derivation requires only two projector derivatives.

Uniformity between ALL transverse rows, orientation, exact periodicity,
identity sewings and the numerical arithmetic layer are spelled out in
[DERIVATION.md](DERIVATION.md). This incorporates Claude's request to make
the continuous-x hypothesis explicit. It does not assert those hypotheses
for a physical graphene domain.

Using the general bounds on the already retained once-folded sphere:

| Intervals per axis | Total loop-error bound (rad) | Combined phase-step bound (rad) | Unwrapping condition | pi/2 guard condition |
|---:|---:|---:|---|---|
| 24 | 0.817528 | 4.924924 | Inconclusive | Inconclusive |
| 48 | 0.199084 | 2.043101 | Sufficient | Inconclusive |
| 96 | 0.049450 | 0.921368 | Sufficient | Sufficient |

This deliberately uses the generic curvature bound as well. Questions 004's
sharper sphere-specific bound still establishes its stated 48-grid result.
The 49- and 97-fold aliases fail the general sufficient conditions on all
three grids. Inconclusive means the bound is insufficient, not that the
calculation is necessarily wrong. No new two-dimensional grid run was made.

## Sharp spinor result

For the retained normalized lift `v=(1,-z)/sqrt(1+|z|^2)` along an affine
line `z=z0+u*t`, the global bound is `||v''||<=|u|^2`, with equality at
z=0. The proof reduces the squared norm to a positive scalar polynomial
inequality. It does not rely on the partner's sampled supremum.

The Hamiltonian first-derivative constants remain 94 in unit K directions
and 47 in unit Q directions. The second-derivative bounds improve:

| Direction | Previous bound | New bound |
|---|---:|---:|
| Unit K, fixed Q | 470 | 188 |
| Unit Q, fixed K | 117.5 | 47 |

Units are meV per respective power of the source's dimensionless coordinate.
For embedded projector acceleration along K, the moving-basis contribution
becomes `4*p1+4` instead of `4*p1+10`. The coefficient-projector bound still
contains `12*L^2/g^2` for rank two. At the three previously retained gap
estimates its total reduction is only **1.94%, 0.70%, and 2.46%**, respectively.
Those gaps are ordinary floating-point inputs, so this table is conditional
arithmetic, not an interval certificate.

## Fixed checks

The single run exited 0 in 1.23 seconds; **66/66 declared predicates held**.
The plan, formulas and thresholds were frozen before execution; no retry or
threshold adjustment was needed. Checks include expected inconclusive outcomes.

- Sixteen affine-spinor witnesses check the exact norm identity and bound,
  including sharpness at z=0 and half-speed Q directions.
- Twelve fixed source-model derivative checks agree with central differences.
  Maximum discrepancies are `4.57e-7` for first derivatives and `1.284e-5`
  for second derivatives, below the declared `5e-5` diagnostic tolerance.
- Six rank-two links in real four-space and three rank-three links in complex
  six-space compare sampled polar factors with numerical continuous transport.
  Their error bounds are respected; the maximum observed operator discrepancy
  is `3.388e-4`, compared with a bound `1.329e-2` for that edge. Endpoint
  gauge controls include a real reflection. ODE invariant residuals are below
  `5.3e-14`; this is not a validated ODE error enclosure.
- Three exact geodesic controls have zero transport discrepancy to tolerance.
  A rank-losing endpoint at h=pi/(2*0.7) is refused by the theorem's hypotheses.
- Nine resolution-bound evaluations, two comparisons to retained loop-error
  observations and three conditional gap calculations complete the checks.

The noncommuting paths are explicit: `R(t)=exp(t*A)exp(t*B)`,
`P(t)=W R(t) P0 R(t)^T W^dagger`, with constant unitary W. A and B are sums of
disjoint plane rotations, giving exact norms 0.8 and 0.6. Their generator
`C=A+exp(t*A)B exp(-t*A)` has norm at most 1.4, and `||C'||<=0.96`.
For skew-adjoint C and an orthogonal projector, `||[C,P]||<=||C||`,
as seen from its off-diagonal blocks. Hence the global constants are
`p=1.4`, `q=0.96+2*1.4^2=4.88`. The generator entries are retained in
RESULTS.json. The complex case is a constant unitary embedding of a real
path; it tests adjoints and gauge covariance, not every possible complex
geometry or a complex Euler invariant.

## Evidence and reproduction

- [DERIVATION.md](DERIVATION.md): hypotheses, complete link/scan proof,
  sharp spinor proof, limits and primary-source context.
- [PLAN.json](PLAN.json): fixed cases, thresholds, expected outcomes and six
  SHA-256 bindings, including the derivation itself.
- [projector_transport.py](projector_transport.py), [RESULTS.json](RESULTS.json),
  [RUN.log](RUN.log), [RUN_RECEIPT.json](RUN_RECEIPT.json): actual implementation
  and retained execution. All generated result records are retained; ODE
  internal trajectories are not.
- [MANIFEST.json](MANIFEST.json): hashes of the seven package files, excluding
  the manifest itself. Pre-run records are not independent timestamp attestations.

From the repository root with questions 001's pinned dependencies:

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -B research/benchmarks/research_questions_005/projector_transport.py --output NEW_DIRECTORY
```

Existing output directories are refused. The accepted environment was Python
3.12.14, NumPy 2.3.5 and SciPy 1.17.0. Imported earlier code is unchanged.

## Remaining gates

The proposed general link theorem is a transfer of the transport argument,
not a completed physical-model application. Uniform interval-enclosed spectral
isolation, verified real structure and orientation, physical boundary sewings,
and certified arithmetic errors remain necessary. The Vafek sign question
and Fable's v078 consumer/verifier corrections remain separately tracked.
No graphene Euler number, braid, experimental result, production repair or
merge is claimed by this pass.
