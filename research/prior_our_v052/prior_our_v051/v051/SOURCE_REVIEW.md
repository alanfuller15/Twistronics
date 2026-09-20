# Layered incremental review — local preparation gate

## Layer 1: mechanical comparison

This batch starts from our delivered v050. No new user archive was supplied. `provenance/engine_comparison.json` hashes all copied engine files and confirms byte identity with v050. `PLAN.json` binds the scientific sources and the seed-anchor file before the decisive measurements. The pilot records are separate and never included in accepted counts.

The new scientific path uses local files, NumPy and SciPy. It writes atomic JSON checkpoints and text logs; it contains no network calls, shell execution or deletion. The read-only inventory/hash checks do not execute project code. Numerical model execution is the explicitly authorized workflow. This is not a new run of the original inspection-only scanner and not a dependency/CVE audit.

## Layer 2: deep-read cutoff and reviewed behavior

Deep-read cutoff: the new local-domain search, bounded fold adaptation, event definitions/runner, nondegeneracy integration, publication guard, report builder and associated tests. The unchanged shared measurement/transport helpers were checked for how the new calls use them; unchanged Hamiltonian engines and unrelated historical drivers were not reread in full.

- `local_domain.py`: validates the rectangle, rejects external seeds instead of clipping them into a new problem, bounds root and gap refinements, checks optimizer success/finiteness/domain membership and seed improvement, and separately scans/refines all four edges. Minima remain finite numerical searches.
- `local_fold.py` and `fold_character.py`: retain derivative-step and nondegeneracy checks while constraining the fold search to the rectangle. No solver failure is treated as an event.
- `run_local.py`: records both extra roots and both original roots, checks their spatial separation from the boundary, measures two charge stations, saves each completed station, and joins the windows at the identical shared parameter state. No original-pair charge or global flat-gap claim is inferred.
- `local_acceptance.py`: rejects wrong scope, altered domains, missing control/mesh/charge records, nonfinite or rejected data, and incorrect protocol identity before results reach the ledger.
- `build_report.py`: requires the complete two-event × two-engine × two-cutoff grid. Counts include common-state repeats and distinguish root records from charge measurements.

## Layer 3: findings against numerical/source evidence

| Priority | Finding | Ground truth / grade | Action or disposition |
|---|---|---|---|
| 1 | A global positive-flat-gap gate is invalid for these extra-pair events | Confirmed: the original pair is resolved outside the local rectangle at every retained control station | Separate local-event gate implemented; global gates unchanged |
| 1 | An unbounded minimum can leave the intended local domain | Algorithmic risk addressed in code and an injected escaping-optimizer test | Bound all local refinements and reject escaped outputs; preserve diagnostics |
| 2 | A boundary zero can invalidate an isolated-domain interpretation | Synthetic zero between edge grid points is detected by bounded edge refinement and rejected | Require both edge grids, corners, refined minima and positive values at each retained station |
| 2 | Partial/local records can be promoted accidentally in a ledger | Wrong-scope, wrong-box, missing-boundary/charge/control and changed-protocol mutation tests reject publication | Keep local scope explicit and require all eight accepted windows |
| 2 | Original-pair preparation and lower events remain incomplete | Coverage gap, not a failed numerical result | Next sequence retains lower-pair birth, full original-pair preparation/frame join and separate lower unlink collision |
| Info | Root-state counts exceed independent charge/parameter coverage | Shared A=0.2,B=0 state is repeated in both windows; charges measured at only two stations/window | Report 72 root records and 16 charge measurements, with four common-state repeats, rather than 72 charge-gated independent stations |
| Info | Finite minima/parameter meshes do not prove continuous positivity or inventory completeness | Mathematical limit of the implemented search | No analytic interval, complete inventory, infinite-cutoff or physical-validation claim |

All numerical conclusions here are [self-tested]. No new external physical or CVE claim was made, and no new web/dependency lookup was performed. The Hamiltonian source bytes and dependencies are unchanged. A source flag remains a triage signal; no vulnerability verdict is inferred merely from an import, optimizer call or file write.

## Ranked next actions

1. Locate the preparation lower-pair birth by following both retained lower roots backward; do not infer a disappearance from a failed search.
2. Replay the original flat pair over A:0→0.2 and B:0→−0.25 with explicit frame transport and a root/frame join into v044. The root controls in this batch do not substitute for that replay.
3. Locate and gate the separately omitted lower unlink collision using the retained v044 inventory.
4. Only after these gaps close, reassess whole-route coverage. Keep any named microscopic tunnelling law and physical-bilayer validation as separate research claims.
