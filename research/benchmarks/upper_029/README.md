# UPPER-029: 1/1024 gap maps around R3 and R1

- **Resolution:** the same resolution and box size as VALLEY-027, around the upper-pair candidates.
  - R3: x 643–763, y 665–809 (/1024).
  - R1: x 308–428, y −54–90 (/1024). The cell is periodic, so y < 0 is valid.
- **Scale:** 35090 eigenvalue-only `evr` solves at cutoff d, in four predeclared batches under the reviewed supervisor. One launch each, no retries.
- **Outputs:** interior local minima of the lower, upper and pair gaps in each box.
- **Claim ceiling:** sampled values only.
- **Authorization:** "Computation heavy workflows only now, no gates".
