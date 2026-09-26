# LOOPS-028: self-contained loops around the 026 dip

**Follow-up to VALLEY-027.** Its loop batch was not derivable: loop points had been de-duplicated against eigenvalue-only grid points (disclosed in `valley_027_execution/README.md`).

- **Loops:** the same three exact 1/4096 loops, solved self-contained (575 points, de-duplicated only among themselves) with full `evr` and four-state vectors. This is 20 jobs under the reviewed supervisor.
- **Prediction (unchanged, frozen):** every group is +1 on all three loops.
- **Grid summary:** derived with zero solves from the hash-bound 027 A/B `MAP.json` files.
- **Authorization:** "Computation heavy workflows only now, no gates".
