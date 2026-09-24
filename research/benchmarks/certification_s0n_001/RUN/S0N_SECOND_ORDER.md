# S0n: fixed-budget matrix Taylor screen

Synthetic calibration only. This additive packet answers S0m review 5806446234 (U1–U3), following 3619ea28d829d26b8656ced51eb507da6204148e. No physical calculation, v078 correction or cutoff claim.

## Matrix screen

At each cell centre m compute D = Ja − Qtᵀ Jb Qs from actual repaired sewing and polar frame-overlap matrices. Compute D′ by the four-term product rule, using R′ = RG θ′ with G = [[0,−1],[1,0]]. This does not replace the matrix screen with the known relative-angle formula.

For radius r = 1/(2N), the first-order bound is ||D(m)||F + L r. The second-order bound is max(||D(m)−rD′(m)||F, ||D(m)+rD′(m)||F) + L2 r²/2. Convexity bounds the norm of the affine interpolant by its endpoints; Taylor's integral remainder bounds the rest uniformly.

For edge 1 θ′ = −π/d. For edge 2 θ′ = 2πw−π/d+defect+4b(1−2t)+δχ′(t), where χ′ = 30t²(1−t)². The actual corner-derived δ is used. Speed bounds v are inherited from S0m. Acceleration bounds are a = 0 on edge 1 and a = 8|b|+6|δ| on edge 2; |χ″| ≤ 6 follows from its polynomial on [0,1]. Q target/source angles are linear along each edge, so their angular accelerations vanish.

Using ||R″||F ≤ √2(a+v²), and applying the product rule to QtᵀJbQs, take L2 = √2[aA+vA²+aB+(vB+vQt+vQs)²]. L = √2(vA+vB+vQt+vQs). These bounds rely on the exact synthetic rotation identities; they are not numerical projector-derived bounds.

Six frozen pair jobs compare bumps 0.720 and 0.722 at N=256 in both orders, plus second-order N=128 at 0.722 and N=256 at 0.750. There is no adaptive search. For equal winding/defect pairs the independently known exact maximum 2√2|sin((bB−bA)/2)| is retained as context only. An unresolved bound for a true distance below one is resolution-limited, not evidence of unequal classes.

## Undeclared-error controls

Four frozen jobs use w=±1 and declared endpoint η=0.1, repair ρ=0.1. Applied endpoint errors are either 0.100 or 0.101. The alternating sample perturbations produce a total q shift (4η_applied+ρ)/(2π); enclosure widening still uses (4η_declared+ρ)/(2π). The excessive applied cases must exclude the known integer and return INTEGER_OUTSIDE_ENCLOSURE. Their branch guard uses the known applied amplitude so this control isolates the ledger failure. This demonstrates refusal for these constructed violations, not detection of every false error declaration. The passing controls have no additional arithmetic reserve; the separate CASE allowance remains open.

## Scope and reproduction

Run driver.py with the pinned python-flint 0.9.0 wheel and a fresh output path, then verify.py against retained RUN. Sources, wheel/native environment, exact dyadic interval endpoints, outcomes and runtimes are retained. Budget: 128-bit Arb, one thread, ten jobs, 40 seconds/job, 180 seconds total, 1 GiB/worker, no retries. No physical evaluations.

Uniform numerical derivation of η, ρ, L and L2, general Kato transport, Q3/P3 and physical S1–S4 remain open. This calibration cannot freeze a physical cell budget.
