# CUTOFF-E-015: fifth cutoff at R3

**Producer:** a Claude Code session, on branch `claude/loop-cutoff-d-013`.
**Independent review:** Codex, pending.
**Authorization:** Alan said "Run the fifth cutoff at R3". Review does not gate this computation.

## Question

At R3, cutoffs c and d still differed slightly: an upper-gap shift of about 3e-5 µeV on CUTOFF-SHELL-012's patch. This run adds one more nested cutoff and asks three things:

- Does the d → e change shrink again?
- Does the fitted candidate location stay inside the patch?
- Is the loop sign still negative at e?

## Cutoff e

**e = sorted(set(d + b-stencil))**, the same shell step that built c from b and d from c. It has 197 reciprocal indices, dimension 788, and central pair [393, 394]. The runner re-derives it and asserts it at run time.

## Fixed design

- **Points:** 41 exact-rational points, each solved at a, b, c, d and e: 205 eigensolves in 7 jobs of 6 points or fewer.
  - **R3 3×3 patch, step 2⁻²²:** identical to CUTOFF-SHELL-012 `original_R3`.
  - **R3 32-point loop, half-width 2⁻²⁰:** identical to LOOP-CUTOFF-D-013 `R3_r1_32`.
- **Limits:** 90 s per job, 600 s summed, 3 GiB per worker, 64 MiB per file, one thread. There are no retries.
- **Regression:** all 41 points × a/b/c/d = 164 upper gaps must reproduce 012 and 013 to 1e-9 meV.
- **Engine:** identical to LOOP-CUTOFF-D-013 apart from four things: cutoff e and the d→e link, the patch geometry check, and the patch summary. The summary gives the gap grid and a descriptive 9-point gap² quadratic per cutoff, as in 012.

## Claim ceiling

These are sampled finite-cutoff diagnostics at one site. The fit is descriptive, and the link threshold is discrete conditioning only. There is no node count, charge, continuous isolation or infinite-cutoff claim. The coordinates are momentum coordinates, not time.
