# Scope and review record

The final endpoint is A=-0.30, B=-0.40, T=-1.8, phi=80 degrees, ratio=1.10. It is distinct from the lower-unlink state in v055/PLAN.json. v055 supplies repaired engines and reusable adapters, not this batch's endpoint definition.

Before execution, the partner endpoint locator was read completely. Its current version uses a bounded Nelder–Mead search, either the best three sampled local minima or one supplied seed per gap; it adds a lower-gap edge seed only in grid mode, records every attempt, excludes failed/nonfinite results, and writes four per-start JSON logs. None of those logs is supplied. The retained stdout lacks the later starts/failed fields. The v045/v048 log entries attribute local N8 refinement and later instrumentation separately. Thus the current source cannot be represented as proven original run source.

The active modern adapter, eight-band measurements and local-domain helpers were read; engine constructors, static matrices and momentum Hamiltonians were checked, with the harmonic construction and runtime guard helpers. The new search and worker source was inspected and synthetic failure paths were tested before the numerical workers. The entire historical project was not reviewed. No new dependency/CVE clearance is claimed in this numerical batch.

Both constructors produce affine Hamiltonians in the explicit fractional chart. The worker checks this at an interior point and checks each analytic gap gradient against centered finite differences. Its eight-band eigensolver checks finite eigenpairs, residuals and orthogonality after explicit Hamiltonian reality/Hermiticity checks. This outer guard does not rely on the reference constructor's assert.

Each chart grid includes both boundary faces. All sampled local minima enter the seed list, without a best-k truncation. Each of four edges has a sampled one-dimensional search and bounded scalar refinement of local minima. Edge candidates also generate inward seeds to avoid face trapping. Known minima and diagonal offsets supply additional local continuation probes. Neither periodic value identification nor coordinate wrapping is used because finite plane-wave truncation is not exactly periodic.

Attempt success/status/message/nfev/nit and checked values belong to that attempt. A failed/nonfinite/nonstationary/worsening attempt cannot be promoted by a previous success flag. The fallback order and thresholds are frozen. Selected interior minima must show positive curvature at two finite-difference steps. This is a local numerical check, not a mathematical certificate.

The sampled result is accepted only if both meshes and both edge searches give positive minima and agree within the declared tolerance. Stored records are reconciled independently of numerical execution before report generation, and report generation first requires a matching actual test run. A failed or mismatched case prevents an accepted batch report.

Historical sources and seed derivation are hashed in HISTORICAL_TARGETS.json and NUMERICAL_PLAN.json. The preserved-tree manifest and previous main commit identify the baseline. These are consistency checks from one workspace, not independent authenticity or execution-time attestations.
