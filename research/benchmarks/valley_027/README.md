# VALLEY-027: 1/1024 map of the R2–R4 valley and loops around the 026 dip

**Producer:** a Claude Code session. **Independent review:** Codex, requested but not awaited.
**Authorization:** Alan said "Computation heavy workflows only now, no gates" and "You pick and continue".

## Batches

| Batch | Contents | Solves | Jobs |
|---|---|---:|---:|
| A, B | Cutoff-d gap map on the exact 1/1024 lattice, x 636–756 and y 553–697 (/1024): 17545 points | eigenvalues only | 276 each |
| C | Three exact CCW loops on the 1/4096 lattice around the SWEEP-D-026 1.577 meV lower-gap dip at (171/256, 159/256): half-width 32/4096, half-width 16/4096, and a control shifted +64/4096 in y. R2 lies outside all three. | full `evr` with four-state vectors, six-group holonomy | 16 |

**Prediction (frozen):** every group is +1 on all three loops, meaning no net discrete sign at the dip. This is what SIGNS-025 `B_R2` and `B_R2R4` imply.

**Execution:** the Codex-reviewed `concurrent_supervisor`, with 4 workers, at most 32 points per job, one launch per batch and no retries.

**Claim ceiling:** sampled values and discrete signs only. There is no certified isolation, touching, count, charge or infinite-cutoff claim.
