# S0t: signed endpoint defect and conservative continuum tubes

Parent f2b92feeea656e1e5429401c36e0900a4f4877bc. Responds to Claude source 5807427550 and Codex disposition 5299673108. Independent audit pending. Synthetic only.

## Full-step cancellation

On one step `[0,h]`, let `m=h/2`, let the exact frame solve `F'=K(s)F`, and let the frozen approximation solve `V'=AV`. Variation of constants gives

    D = integral_0^h U(h,s)(K(s)-A)V(s) ds.

Write

    K(s)-A = (K(m)-A) + K'(m)(s-m) + rho(s),
    ||rho(s)|| <= ||K''|| (s-m)^2 / 2.

The constant term costs `delta*h`, where `delta=||K_box(m)-A||`. For the centered linear term define `G(s)=U(h,s)K'(m)V(s)`. Its scalar first moment is zero, while

    ||G'(s)|| <= ||K'|| (||K|| + ||A||).

Consequently the full-step endpoint debit is

    ||C|| [delta*h + ||K''|| h^3/24
            + ||K'|| (||K||+||A||) h^3/12].

Every factor is retained per step. `||A||` is computed from the frozen skew matrix. The exact generator uses the declared uniform bound `||K||<=3` for the constant family and `||K||<=6` for the two-axis family. The packet retains the previously certified `||K'||<=24` and `<=120`. It uses conservative new bounds `||K''||<=438` and `<=4656` as described below. Incoming endpoint error is not amplified because exact and frozen propagators are orthogonal. Interval-exponential and product rounding remains a separate debit.

The rational verifier checks both this recurrence and the earlier uncancelled recurrence. A retained run must strictly improve the completed endpoint bound in each case. This is a proof-led ledger comparison, not an empirical convergence fit.

## Second generator derivative

For the constant family, `||n'||,||n''||,||n'''||<=1`. Product differentiation gives `||H'''||<=24`. With the unit-circle resolvent bounds already used in S0s,

    ||P'''|| <= 6||H'||^3 + 6||H'||||H''|| + ||H'''|| <= 294,
    ||K''|| <= ||P'''|| + 2||P''||||P'|| <= 438.

This deliberately does not exploit the analytic fact that the exact generator is constant.

For `Q(t)=Rz(t)Ry(t)`, repeated differentiation of the two unit generators gives `||n'''||<=8` and hence `||H'''||<=192`. With `||H'||<=6`, `||H''||<=48`, `||P'||<=6`, and `||P''||<=120`,

    ||P'''|| <= 6*6^3 + 6*6*48 + 192 = 3216,
    ||K''|| <= 3216 + 2*120*6 = 4656.

These constants are intentionally broad and apply uniformly on the padded parameter cells. Exact synthetic formulas remain regression oracles only.

## Endpoint versus tube rules

The centered cancellation is valid only after integrating the complete step. A partial-step tube has no symmetric interval around `m`, so every source and target tube retains the S0s charge

    ||C|| [delta*h + ||K'|| h^2/4]

plus incoming endpoint error and the existing padded-radius extension debit. The verifier checks the signed endpoint inequality and the uncancelled tube inequality separately. Seam coverage, determinant, singular-value lower bound, polar derivative amplification, noncommutation, order separation, and frozen-initial-generator refusal remain the S0s controls.

## Gap-to-derivative transfer contract

The results declare, but do not execute, the interface needed for a physical transfer. It requires a named self-adjoint spectral-projector derivative theorem with its hypotheses, cluster and complement intervals, a positive spectral-gap lower bound, Hamiltonian derivative bounds, and a specified contour or Sylvester construction. It must output projector and Kato-generator derivative bounds together with their valid parameter domain. Missing theorem, gap, derivative input, or domain agreement is a refusal. No physical derivative constant is inferred in this packet.

## Evidence and limitations

The retained Arb run remains fixed at 128 bits, one thread, 512 contour panels, 128 transport steps and 64 seam cells per family, with 40 seconds and 1 GiB. Exact projector, frame and seam formulas are controls, never inputs to the numerical contour or transport ledger. The rational verifier rechecks the two endpoint recurrences, tube rule, coverage, seam gates, quadrature charges, declared transfer contract and protocol mutations.

This packet does not certify a physical spectral window, physical derivatives, a full eta/rho/L/L2/L3 composition, higher seam derivatives, Q3/P3, physical S1-S4, v078 corrections or cutoff agreement.
