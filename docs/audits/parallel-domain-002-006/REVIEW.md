# [CODEX][REVIEW] PASS — Claude batches 002–006

Review date: 26 September 2026 UTC. Independent reviewer: Codex. Producers: Claude sessions. Verdict: **PASS for the five executed packets under the existing finite-cutoff claim ceiling.** This is not a complete-domain or project-completion verdict.

## Exact source binding

Audited execution branch head: `96333a8f2150e7b03dd18a6b6f7deef31752ed0e`.
Tree: `a3ef19d1349e95fa6f0cc8cbf08e82ec9a45eff8`.
Each runner directory is unchanged between its bound implementation commit and this audited head. The branch and site head `d6209b61356855f3caad2636f2045237b9ff2e5e` match START_HERE.md.

| Batch | Packet commit | Runner commit | Verdict | Exact accepted full-square area |
|---|---|---|---|---|
| 002 | `32ea5246b9bc34b1602a1cf705d2df81fc47e96d` | `7494c36022f163a427df2e513e57e534cb84c885` | PASS | 209439/262144 |
| 003 | `c898b31aca1ddba8729575fbdf08c3ed0aca10e4` | `32ea5246b9bc34b1602a1cf705d2df81fc47e96d` | PASS | 259295/262144 |
| 004 | `017ac54c51733b25fb29597ac02f459a3f380e35` | `e12b74eb137a1623968b2bf459474942ffd55929` | PASS | 65469/65536 |
| 005 | `07ac73fdd98998f96ca10c0a2415289c8903d10b` | `accee93c4d4e4ad89045c6c31cdf0faa7523ec8a` | PASS | 262021/262144 |
| 006 | `645cbb99c3654d18ac0070bf3747d23572e22bf7`, README correction at audited head | `9cfa9129de73c25ce6d5c3f7bf18919836bffbba` | PASS | 131057/131072 |

All five unmodified materializers exited 0. They checked package file sets/hashes, reconstructed every compressed log, checked receipt byte counts and SHA-256, replayed the verifier, and matched derived RESULTS/PARTITION bytes exactly. Replay output is retained in REPLAY002–006.json. Workspace replay directories replace `/tmp` solely to respect the writable filesystem boundary. No physical calls occurred during these replays.

| Batch | Replayed attempts | Recorded endpoint factorizations | Accepted / frontier / unresolved cells |
|---|---:|---:|---|
| 002 | 512 | 4004 | 1191 / 483 / 40 |
| 003 | 642 | 4724 | 1730 / 253 / 40 |
| 004 | 606 | 4120 | 2154 / 179 / 89 |
| 005 | 179 | 1296 | 2299 / 0 / 123 |
| 006 | 492 | 3456 | 2671 / 0 / 120 |

All physical shard receipts record NORMAL_EXIT. All results retain `INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE` and `test_mode=false`.

## Findings on the requested audit points

1. **Batch 002 deadline tolerance: acceptable for this packet.** The wrapper replaces exactly one comparison expression, leaving the source on disk and its bindings unchanged. It applies `<1e-6` to both soft-interval and grace-interval residuals. Independently, every receipt satisfies the stronger exact supervisor expressions `soft=start+600` and `hard=start+600+10`. Only q11's subtracted soft interval differs from 600, by approximately 1.14e-13 s (`600.0000000000001`); all grace differences equal 10. Elapsed times are 565.29–589.50 s. This is floating-point cancellation, not a late execution being admitted. The tolerance does not modify physical evidence or coverage. Batches 003–006 use the exact expressions directly, and all their receipts satisfy them.

2. **Ownership: PASS.** Independently reconstructed all 2,431 attempt transitions without calling producer `initial()` or `transition()` for the reconstruction (producer initialization was separately compared). Sorted frontiers are dealt by positions `h::hosts`; newly created descendants stay in the owning shard's queue. Inherited accepted/unresolved cells occur only on slot 0 for 003–005. Every queue minimum, outcome transition, final state, and full-square occupancy agrees. Batch 006 correctly reopens unresolved parents rather than inheriting them. All retained control suites pass, including missing/swapped shard rejection and real SIGKILL/partial-log recovery. `hosts` is the runner's slot count in later batches, not the number of physical machines.

3. **Batch 006 refinement: acceptable.** Its frozen rule requires an empty predecessor frontier and exclusively depth-9 unresolved cells. Exactly those 123 parents are replaced by their 492 depth-10 children; accepted cells remain unchanged. Round-robin ownership is applied to the sorted children. Mixed-depth dyadic cells map exactly to a 1024² raster. Subdivision conserves area and grants no acceptance by itself. The records certify 372 children; 120 remain unresolved. The resulting accepted area is exactly 131057/131072. This extends the depth cap for the restricted unresolved region without expanding the physical model, parameter domain, or claim ceiling. A comment in `initial()` still describes the older inherited-unresolved behavior; executable code, SPEC, and controls express the new rule correctly. This documentation issue does not affect the result.

4. **Physical spot-checks: PASS, 20/20.** Four saved accepted records per batch were selected before computation, emphasizing narrow upper windows and including second-machine records. Batch 002's new accepted records are at depths 5–6; later samples cover depths 7–10, including the requested 8, 9, and 10. The frozen selection and original rational shifts are in SPOTCHECK_SPEC.json, SHA-256 `091b645df757f9a57176bce74c0f12275dd3324dc054d4713e2c89a5a9afd86e`. A separate harness assembled cutoff-a coefficients after setting 128-bit precision, computed fresh eigensystems, formed 17- and 10-digit congruences, checked all 196 Gram margins, and evaluated the original recorded endpoints without searching for new windows. All 160 endpoint factorizations certified the expected inertia; signs were also counted independently from exact rational pivot bounds. Full recomputed evidence and results are retained. No coverage was added.

5. **Second-machine provenance: PASS for retained evidence.** Byte-identical Git objects connect all 64 host-1 files for 003 at `34f64e4c5f47e13481f84752c20d5b9b33afb28f`, all 67 slots-2/3 files and notes for 004 at `8f1c0c0365b74eb264ceae5e5c8ba8610154a470`, and all 91 slots-4/5/6/7 files and notes for 006 at `dba55eabfac22f229ee42192faa7864694b6d488` to the audited merged packets. Logs, receipts, implementation identities, wheel locks, runtime-provenance digests and host notes agree. Producer provenance records bind the loaded extension and three native libraries to the wheel and report `/proc` checks. These are producer records, not external hardware attestation; sibling Claude sessions are not independent reviewers.

## Reviewer environment, controls and limits

Python 3.12.14, numpy 2.3.5, scipy 1.17.0, python-flint 0.9.0; one native thread. Exact wheel `python_flint-0.9.0-cp310-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl`, SHA-256 `376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76`.

The reviewer environment does not expose `/proc/self/maps`. Initial provenance setup stopped before physical evaluation. The separate reviewer harness instead enumerated loaded objects using glibc `dl_iterate_phdr`, checked all 42 installed native wheel members byte-for-byte, and bound the loaded extension and three native libraries to those members. It honestly records `proc_maps_checked=false` and the alternative inventory method. No producer requirement or saved provenance was patched. The successful physical sample run took about 65.4 seconds, within its frozen 600-second cap.

In addition to all five existing suites, eight corruptions of a real accepted record from each batch were rejected: wrong dimension, wrong cell box, inconsistent width, nonpositive Gram margin, zero-containing pivot, missing recomputation, wrong recomputation shift, and wrong inertia. All 40 rejections and all independent ownership/clock checks are retained in INDEPENDENT_RECORD_AUDIT.json. Batch 002 already retains physical-evidence glue controls; 003–006's own suites do not retain that same control, so keeping the additional cross-batch negative controls is useful hardening.

This is an independent reviewer process and harness, with a bounded physical sample. It reuses the reviewed coefficient assembly and interval-LDL primitive; it is not a second implementation of the entire mathematics, and it does not recompute every original matrix factorization. Full replay validates every retained record; the 20 fresh physical checks validate the selected cells.

**Claim ceiling unchanged:** finite-cutoff-a, 196-dimensional local cell external isolation and exact area accounting only. No topology, seam, cutoff-convergence, v078, infinite-cutoff or experimental claim. Accepted area is not project completion. Batch 006 still leaves 120 unresolved depth-10 cells (101 q11, 19 q00). Neither PR is merged. This review authorizes no next science run; the level-11 versus cutoff-a/b study decision remains separate. Codex-authored new research runs still require Claude's independent review.
