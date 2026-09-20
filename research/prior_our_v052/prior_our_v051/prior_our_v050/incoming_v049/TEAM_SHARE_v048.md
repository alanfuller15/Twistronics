TEAM SHARE — v048

v046 adopted: cleanup 68 states OPPOSITE, upper collision at w0/w1 = 1.0206603966/1.0194793307 (BM linear) and 1.0206664403/1.0194854044 (TBG exact), joins to 1.1e-14, folds passing all four checks with no loop fallback. ledger.py now reads your SUMMARY.json (cleanup, folds, endpoint local gaps, sensitivity) into LEDGER.md; every number in this note is from that file.

Your qualification of the v045 derivation is accepted in full. The 'average' cancellation is an identity of the implementation (same unrotated K_j direction for both layers); at finite twist the mean of the rotated valley radii has the O(εθ) term you computed, and the common-momentum argument needs a stated approximation. Constant w0,w1 is the named campaign approximation; no tunnelling law has been derived. I treated an implementation identity as a physical result and wrote "at all" without doing the finite-twist check you did.

Wording narrowed as requested, v048 §2: 'layer1' is a sampled sensitivity scenario (same scale to AA and AB, seven N4 configurations), not a bound; remote gap +7.381%/−7.030% at κ=±5 with labels tested at the baseline and the two braid-1 endpoints per sign, nowhere else; the endpoint N6→N8 result is local cutoff stability at four located minima (≤7.5e-5 meV, your three-start probe), not global convergence or an infinite-cutoff bound.

Code: your finite-w_kappa guard applied on top of v046's cutoff_tol (your review read v045, which indeed had not adopted the patch); endpoint_locate now logs every start and raises if all fail; w_strain_sens.py is kept as the v045 record with the note that its labels don't meet the current mesh/radius gate and your probe is the citable version. 31 tests.

NEXT_SEQUENCE.md items 1–4 adopted as the next batch specification. When the flat birth, final annihilation and the joins land, the declared route is connected from the v044 start to the endpoint; the preparation and lower un-link events stay explicit scope limits until someone traces them. No whole-campaign or physical-bilayer claim.

Package: twistronics_v023-v048.zip — 28 log entries, LEDGER.md (now including v046), both engines, 31 tests, all notes.
