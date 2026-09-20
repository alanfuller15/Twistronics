# v047 reconciliation

The cutoff-tolerance API is adopted correctly, with historical defaults retained. All 31 supplied tests pass; 22 targeted checks cover the adopted cutoff behavior, the still-separate finite-tunneling patch and ledger rejection/compatibility rules. The preparation tables provide useful seeds, but do not establish complete event locations or a continuous preparation replay. The supplied ledger reproduces byte for byte; its fixed prose remains a source of stale scope claims. Numerical checks here are `[self-tested]`, not independent physical validation; recipient consumption is `[unconfirmed]`.

## Ranked actions

1. **Yellow — distinguish the two v046 contributions.** The incoming v046 adopts our v044; our separate v046 already measured post-braid cleanup and the upper collision. Preserve both records and source identities. **Tier/verdict:** checked artifacts; version collision holds.
2. **Yellow — complete the later connections.** Replay flat birth/final annihilation and sample their gapped joins, with explicit root identities and cycle labels. **Tier/verdict:** sandbox self-tested; results reported in REPORT.md, without promoting finite sampling to proof.
3. **Yellow — retain preparation events as candidates.** The supplied scripts bracket node-count changes or extrapolate positive gaps; add two-seed fold/charge/open-side checks before accepting births or deaths. **Tier/verdict:** source checked; “three events located” is unsupported at the current gate.
4. **Yellow — correct the preparation join explanation.** Match like geometry, refine the printed seeds, and compare with the actual 1e-6 join tolerance. **Tier/verdict:** source plus sandbox self-tested; the printed tolerance explanation fails, while a fresh matched-model root join passes.
5. **Yellow — generate status as well as numbers.** Validate accepted source status, schema, model tags and engine/cutoff completeness; bind source digests; keep provisional preparation rows distinct. **Tier/verdict:** source checked; current ledger's numerical tables reproduce, but the footer is hardcoded and stale.
6. **Green — preserve the adopted cutoff API.** Eight targeted cases test historical default matrices, both shared tolerances and invalid inputs. Keep the finite-w_kappa fix separate from primary measurements. **Tier/verdict:** sandbox self-tested; adopted cutoff tests pass.

## Findings table

| Claim | Tier | Verdict | Evidence |
|---|---|---|---|
| Both engines expose cutoff_tol with historical defaults | checked / sandbox self-tested | Holds at reviewed source and tested states | Constructor diffs; eight adopted-cutoff tests include full matrices and NaN/negative inputs. |
| “31 tests” | sandbox | Holds | Supplied suite: 31 pass. This is execution, not exhaustive coverage. |
| Prep flat roots agree across engines to about 9e-12 | inventor-supplied numerical record / checked source | Supported for the selected N4 roots; not all event diagnostics | anchors_prep_N4.json covers two original flat roots at six A values. Remote minima and adjacent-node inventories in that driver are BM-only. |
| U birth at A≈0.137 | checked | Candidate, not accepted fold | prep_detail.py samples five positive remote gaps. Its “bisection” banner does not describe its code: it performs no bisection or zero/Jacobian solve. |
| Extra pair birth and annihilation located | checked | Brackets only | Differences in finite global-search node counts bracket candidates. A search miss is not itself a disappearance proof. |
| One lower-gap node at B=−0.25 | sandbox self-tested | Confirmed undercount | Fresh two-seed refinement resolves two distinct roots, separated by about 0.068, in BM linear, BM exact and TBG exact. Both gaps are below 5e-13 meV. This corrects the inventory, not the unresolved birth location. |
| v044 anchors were exact in both engines; 2e-5 is below join tolerance | checked / sandbox self-tested | Fails as stated | The primary BM path was linear and TBG exact. 2e-5 exceeds 1e-6. Fresh refined roots join the matching anchors within 4.4e-15; rounding error in the printed seeds is about 4.9e-5. |
| Seed differences explain the residual | sandbox self-tested | Not supported for converged matched models | New BM-exact and TBG roots differ by about 4.1e-15; BM linear/exact differ by about 8.1e-7 at this state. The old unrounded B-sweep roots were not saved, so their specific residual cannot be attributed retrospectively. |
| Every ledger value comes from recorded summaries | checked / sandbox | Table reproduction holds; universal wording fails | Supplied ledger reproduces byte for byte from preserved summaries. Footer event values and coverage status are literal strings; kinetic header is not validated against input. |
| Ledger is an acceptance validator | checked | Not implemented | It reads arbitrary JSON without requiring ACCEPT, source hashes, complete engine/cutoff pairs or model consistency; fallback keys can print blanks. It is a formatter. |
| v045 closes microscopic tunneling / global cutoff convergence | prior v046 review | Still not established | Our distinct v046 gives the finite-twist qualification, sampled ±7.4% sensitivity and local N6→N8 agreement. This incoming package predates those corrections. |

## Layer 1 — on-disk scope

The upload contains 130 entries, 129 files. SHA256: `18217505087fe95e88c7bfaec8188c1e1364bc3876b1b70642851c1bd4077fa5`. Extraction rejects traversal and symlink entries. Compared with incoming v045, three Python files changed: bm_strain.py, tbg_ref.py and test_tbg_ref.py. Added files and the full diff are retained in provenance/input_inventory.json and source_changes.diff. This is an incremental byte/inventory review, not a rerun of the original scanner or a new dependency/CVE audit. Presence and risk signals are not verdicts.

## Layer 2 — deep-read cutoff and behavior

Deep-read scope: both constructor/cutoff diffs, the changed test, complete anchors_prep.py, prep_detail.py, prep_B.py and ledger.py, the new logs/ledger, and the measurement code used for this batch. Unchanged legacy drivers were not all reread or re-executed. Priority follows changed scientific behavior and generated claims, rather than implying every old script has been re-audited.

The new numerical drivers import local Python, execute eigensolvers/searches and print output. anchors_prep.py also writes its JSON output in the working directory. ledger.py reads the three supplied summary paths and optional anchor path, prints Markdown and overwrites LEDGER.md in its working directory. No explicit network, deletion or subprocess call appears in these four added drivers. The supplied ledger was executed only in an isolated provenance directory, preserving the incoming file. Python cache writes were disabled. This is an authorized numerical continuation; these drivers are not inspection-only scanners.

The anchor drivers do not implement current loop-mesh/radius agreement or complete optimizer-failure logging. prep_B.py also reuses its closest-pair variable if a later search returns fewer than two roots (or leaves it undefined on an initial such result). Recorded rows all have at least two roots, so that latent defect does not explain a demonstrated historical error.

## Layer 3 — concrete checks and limits

The lower-inventory probe uses both saved v044 lower-root seeds and resolves two distinct roots at the common N4 starting state. It establishes at least two, not an exhaustive inventory. The supplied one-node output is therefore incomplete; the internal cause of that search miss was not isolated.

The preparation join probe starts from the actual four-decimal printed seeds, refines with the shared gate, and compares root permutations to preserved v044 records. It confirms identity at one common state only. No preparation birth/death, Euler class or continuous preparation path is established by that probe. The archive's exact/exact preparation anchors do not replace the linear-BM path history.

All fresh numerical passes are self-tested. Two engines share this measurement harness and are not independent tests of the physical assumptions. Previously fetched primary-source discussion is preserved in our v046; no new microscopic law, dependency currency or CVE finding is asserted here. The charter and audit discipline continue without amendment. Triage can miss issues outside the named source slice.
