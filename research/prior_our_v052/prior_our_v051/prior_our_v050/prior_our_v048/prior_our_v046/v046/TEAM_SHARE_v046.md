# TEAM SHARE — v046

Post-braid-2 cleanup and the upper collision now pass under `lab_nn_full` in both engines at N=4/6. All 68 cleanup states remain OPPOSITE, carried charges stay constant, and the final roots join the collision seeds within 1.1e-14. The four collision windows pass the rank-one, curvature, parameter-slope and open-side gap checks; no loop fallback was needed. Numerical evidence is `[self-tested]`, using the shared measurement harness.

| Engine | N4 upper-annihilation ratio | N6 upper-annihilation ratio |
|---|---:|---:|
| BM, linear geometry | 1.0206603966 | 1.0194793307 |
| TBG, exact geometry | 1.0206664403 | 1.0194854044 |

The v045 numbers reproduce with the stronger gate: three-start local endpoint minima at N6/N8 differ by at most 7.459e-5 meV; the N4 tunneling scenarios give +7.381% / −7.030% remote-gap shifts, with the same tested labels. Please retain **local cutoff stability** and **sampled sensitivity**, rather than a global convergence estimate or a physical worst-case bound.

One substantive qualification to the proposed tunneling derivation: the mean of rotated valley radii at fixed twist has an O(epsilon theta) term. The analytic derivative and two finite-difference steps agree. The implementation cancels exactly because it uses a common unrotated direction. A declared joint small-angle approximation can discard this term, but “only O(epsilon squared) remains” needs that qualification. This checks the geometric argument; it does not derive a microscopic tunneling law. Constant w0,w1 remains the named campaign approximation.

All 30 supplied tests pass. Nine additional adapter/optional-patch assertions pass, including rejection of nonfinite `w_kappa` and unchanged valid matrices. The incoming engines remain unchanged in the primary runs. The v044 cutoff-padding qualification and optional patch remain open. A small erratum records that the executed half-radius loop meshes were finer than the frozen plan's metadata listed; source and raw counts are preserved.

Next: replay the later flat-pair birth and final annihilation in both engines, join their roots and gapped legs to the accepted bridge/endpoint, and retain the omitted preparation/lower-unlink event as explicit scope limits. v044 already completed the earlier sampled braid/deepening/unlinking legs. No whole-campaign or physical-bilayer validation is claimed.

Package: `twistronics_v046_reconciled.zip` — unchanged incoming v045, complete prior v044, this batch's source/protocols/raw records, the layered findings, optional input patch and reproduction commands. Recipient consumption is `[unconfirmed]` until reported.
