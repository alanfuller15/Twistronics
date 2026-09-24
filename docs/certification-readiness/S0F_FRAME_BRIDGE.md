# S0f: a conditional projector-to-frame-to-seam bridge

2026-09-24. Parent 9c7993b693023c0746d3e5b134678797de44d5da.
Claude source 5805000902; completed S0e review 5805023465. Independent S0f
review pending. This package is a bounded synthetic component, not the complete
composition certificate. Physical S1-S4 remain unimplemented and unexecuted.

## Frame lemma and assumptions

Let P be an exact orthogonal rank-two projector, Q an approximation with
||P-Q||_2 <= epsilon, and E an exact orthonormal two-column candidate. The
input balls must contain those objects. Set

`r >= ||(I-Q)E||_F + epsilon`, with r < 1.

Because ||E||_2=1, ||(I-P)E||_2 <= r. Thus G=E^T P E satisfies
`(1-r^2)I <= G <= I`. Define F=PE G^(-1/2). Then F^T F=I and F spans P.
The positive square root fixes the orientation relative to PE.

Writing PE=F G^(1/2) gives

`||F-PE||_2 = ||I-G^(1/2)||_2 <= 1-sqrt(1-r^2)`.

The triangle inequality therefore proves

`||F-E||_2 <= eta = r + 1-sqrt(1-r^2)`.

Every matrix entry differs by at most eta. Widening each supplied E ball by
the outward upper bound on eta encloses this exact F. The routine never
infers exact orthonormality from a small numerical Gram defect. Rank, spectral
split and exact candidate orthonormality are caller obligations, proved by
explicit algebra for this fixture. This is not yet a continuously transported
and consistently oriented rectangle frame for the physical case.

## Fixed bridge test

H=diag(0,0,2), P=diag(1,1,0), circle center zero/radius one, alpha=0,
beta=2, N=32. The Riesz routine supplies Q and its total error bound. The
candidate columns are e1 and (0,c,s), with t=1/1048576,
c=(1-t^2)/(1+t^2), s=2t/(1+t^2). Exact rational algebra gives c^2+s^2=1
and c>0. The exact projected polar frame is therefore (e1,e2).

The test checks that the computed frame balls contain that known exact frame
and feeds those balls into the explicit partial-shift seam S=diag(1,1,0).
The seam passes its 19/20 singular gate and 1/128 map-error gate. A candidate
containing e3 instead of the second target direction is refused, and a tighter
frame budget is separately refused. Six fixed checks pass.

## S0e integration findings

K1: additive modules use unique names primitives_s0f, pair_s0f and
certified_s0f. The copied pair module explicitly imports the dedicated
arithmetic. An import-time identity check binds the reused inertia function.
Both S0a-first and S0b-first subprocess controls pass.

K2: a fault-injection control traverses pair_from_enclosed_inputs ->
certify_pair -> certify_shift -> inertia_ldl and reaches the dedicated
NonfiniteEnclosure boundary. The injected LDL input is produced by a finite
exponential input exceeding the backend range. This establishes exception
propagation through the reused path, not naturally occurring overflow of the
well-conditioned pair fixture. Three integration checks pass in total.

K3: the seam docstring explicitly requires consistently oriented rectangle
frames before det(M)>0 has the CASE orientation meaning. The bridge only
establishes the stated local polar orientation.

K4: the full composer remains absent. Its required artifact/input hash binding
and exclusion of conditional budgets and SYNTHETIC_REASON_GATE_ONLY from final
q results remain open. A package manifest binds this packet's sources and
retained results; that is integrity evidence, not a substitute for the future
geometric dependency checks.

## Reproduction and limits

Use the existing locked python-flint 0.9.0 environment (wheel SHA256
376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76).
From repository root:

```sh
timeout 30 python -B research/benchmarks/certification_s0f_001/check.py /tmp/s0f-new
timeout 30 python -B research/benchmarks/certification_s0f_001/test_integration.py
python -B research/benchmarks/certification_s0f_001/verify.py
```

The retained runs used 128-bit arithmetic, one thread and a 1 GiB address-space
limit. The earlier exploratory six-check draft is not the retained release run.
No physical model, eigenproblem or numerical sweep was run.

Next: independently review this lemma and integration boundary, then bind
continuous frames, exact corner repair, both complete phase lifts and the joint
integer. Full-dimension Riesz wrapping and projector derivative bounds remain
open. No graphene class, cutoff agreement or physical certificate is established.
