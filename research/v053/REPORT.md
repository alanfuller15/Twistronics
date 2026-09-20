# Our v053 — original-flat-pair preparation frame replay

[self-tested] The preparation route now joins the accepted v044 start state through both roots and relative frame orientation in both engines at N4/N6. Each engine/cutoff covers A:0→0.2 at B=0, then B:0→−0.25 at A=0.2. There are 19 states per case, 76 in total, all with mesh/radius charge checks. Carried individual charges remain constant; observed spatial labels: SAME.

| engine / geometry | N | states | labels | min fine/coarse parameter overlap | root join | endpoint plane overlap | relative orientation |
|---|---:|---:|---|---:|---:|---:|---:|
| bm_lab / linear | 4 | 19 | SAME | 0.995465 / 0.982078 | 9.99e-16 | 1.000000000000 | +1 |
| bm_lab / linear | 6 | 19 | SAME | 0.995469 / 0.982090 | 1.58e-15 | 1.000000000000 | +1 |
| ref_lab / exact | 4 | 19 | SAME | 0.995465 / 0.982078 | 1.78e-15 | 1.000000000000 | +1 |
| ref_lab / exact | 6 | 19 | SAME | 0.995469 / 0.982091 | 2.64e-15 | 1.000000000000 | +1 |

Minimum sampled comparison-path external gap: 3.73845073 meV. Minimum spatial-transport overlap: 0.99778252. Maximum measured basis-norm loss: 2.08e-15. Loop-fallback states: 0.

## Evidence and what the join means

The accepted grid has eight A intervals and ten B intervals; a coarser frame route uses every second fine state, giving nine parameter-orientation comparisons per case, 36 in total. The eleven-state BM N4 pilot is preserved separately and excluded from all accepted counts. Both N4 replays passed before N6 began. The primary protocol and sources were frozen after the pilot and before the accepted runs.

At each state, both original roots are continued, both frames are carried using the declared real Fourier-coefficient basis, the spatial comparison path is checked/refined, and loops at two meshes plus half radius must agree. The strain-defined basis is constant on these A/B legs and its labels are explicitly checked. Local frame isolation along these sampled nodes/paths does not restore global flat-pair isolation after the previously measured remote-band contacts.

At the endpoint, saved v044 frame bytes must match their recorded digest and basis labels. Root positions must agree within 1e−6; both two-planes must overlap above 0.999999. Charge transformation must match each frame's orientation, and the pair's relative orientation must agree. A common overall orientation flip is allowed and tested: an arbitrary absolute gauge sign is not a physical discrepancy. The join does not claim a gauge-independent SO(2) angle or laboratory-coordinate time evolution.

## Validation

18 tests pass: eight endpoint-frame tests, three checkpoint-integrity tests and seven publication-acceptance tests. A common orientation flip and consistent root permutation pass; a one-sided flip, wrong charge, wrong basis/state, corrupted anchor bytes, missing coarse/temporal frames and pilot/partial records reject publication. Hamiltonian sources are unchanged from v052; historical supplied regression results are retained but were not rerun or recounted.

The BM N4 production run stopped after three committed states and resumed in a new process. All six existing checkpoint files kept their original hashes, and the resumed run completed all 19 states and its endpoint join. This exercises checkpoint restoration; no separate uninterrupted numerical replay was run for a bitwise trajectory comparison.

## Coverage and limits

Preparation event windows (v050–v052) and this original-pair frame replay now connect the baseline to the accepted v044 start. The separate lower unlink collision remains the outstanding numerical coverage item. No established campaign label was revised.

This is sampled continuation and transport, not a proof of behavior between all parameter/momentum samples. Fine/coarse comparison checks the orientation relevant to charge; it does not certify a unique accumulated SO(2) rotation. No Euler class is continued through loss of global two-band isolation. Two engines with a shared measurement harness do not exclude a shared conceptual error. Infinite-cutoff error bounds and physical-bilayer validation remain outside measured coverage. Recipient consumption is [unconfirmed].
