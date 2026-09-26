# Exact Sites source for Claude review

Restores version 18 then applies the actual Git patches for versions 19–28. Every source file is checked against hashes read from the original Sites commits. This is a portable source/history transfer, not a claim that Sites commit objects exist in this GitHub repository.

Run `python materialize.py /new/absolute/output 28` (Python 3.12+, Git), then install from package-lock.json as needed. All sources, build scripts, compiled bundles, scientific display data, and binary density frames are included. No credentials or dependencies are packaged. Do not deploy the reconstructed site during review.

Current deployed v28 Sites commit: 9e6882ef94a8194c9f202d09846f9457c64b43f1.
Current index.html SHA-256: 45a21e1bfebf89a9c5d6a89552290c5dbc3c97c6625fbcfe6db8e1c05a712bd3.

Independent review requested on PR #2. For coverage exporter replay, use the audited scientific repository separately and supply the script's repo argument. Original v18–28 byte hashes and source IDs are in MANIFEST.json.

Version22 fixes the single grid-tolerance sentence in both index.html and graphene.html. Sites source 3c1f5d45331c4357093c60bb99dab719d48ca094. Restore with final argument22; v21 remains available. Numerical data and frames unchanged.

Version 23 promotes independently reviewed depth-11 coverage (Claude review 5842413474) and the qualified cutoff a/b comparison. All eight partition selectors, 3151 latest cells, 1554 point-to-partition links and source-bound export checks pass. This is data/text only; prior independent browser checks are not a new browser test. Dynamics002 remains separate and pending review.

Version 24 changes only the landing coverage render: a small full-square locator plus default 128× detail, yellow/dotted unresolved cells against dark blue accepted cells, visible legend and four area buttons. The four windows show36,30,26,19 unresolved cells, all111 in total. Data and scientific verdicts unchanged. DOM/geometry checks passed; a rasterized geometry preview was inspected. No new browser-rendering claim.

Version 25 makes the landing page a guided learning sequence: twist, electron probability, waves, energy, crossings, evidence. All six live models remain visible. One invitation and continuation per step; twist feedback compares physical repeat length against the starting angle. Default pattern view holds40nm field fixed so growth is visible. View controls are optional. The electron model is explicitly separate and does not respond to the twist slider. DOM checks cover navigation focus, angle feedback including preset events, fixed scale and existing coverage controls. No browser-rendering validation claimed.

Version26 addresses Claude finding5842735688: replace both queueMicrotask(discovery) callbacks with setTimeout(discovery), so preset/reset feedback runs after the angle-setting listeners. No design, data or model change. After-click DOM checks cover0.5°,3°,1.05°,reset and slider2°. Browser validation requested from Claude.

Version 27 promotes audited depth-12 coverage: 16777105/16777216 (99.999338%), 3,373 accepted cells and 111 unresolved depth-12 cells (Q11 96, Q00 15). Evidence is pinned to c389e345597e66eff81bf2f1219dd4272adf2bd6, Claude PASS 5842854287. Nine snapshots; prior eight are byte-equivalent as parsed run objects. The exporter checks exact area, complete non-overlapping occupancy, inherited cells, all 444 children, parent outcomes and manifest hashes, and reproduces both generated files byte-identically. Review metadata identifies each reviewer and scopes the latest audit link.

The gap paragraph now reports ~1.6 µeV on the b/c line (PASS 5843138081) and separately b/c/d agreement within 0.03 µeV on the two local patches (PASS 5843549264). Cutoff d was not sampled on the original line. No closure, global-minimum or infinite-cutoff-convergence claim. Optional touching panel, runs 013/014 and optional dynamics swap are omitted.

Only five source files change. The v26 timing fix, compiled 3-D bundles, styles and animation data are unchanged. Static links, latest selectors, prior snapshot equality, exporter reproducibility and actual landing preview script in a DOM stub passed; four windows count 36/30/30/15 cells at 256×. No new browser-rendering validation is claimed; desktop/mobile review is requested from Claude. Restore with `python materialize.py /new/absolute/output 28` and supply the scientific repository to `scripts/build-audited-coverage.py --repo ...`. Neither PR is merged.

Version28 adds only the approved candidate-touching panel in index.html, using accepted wording from006 review5843418742 and011 review5843536759. The first-candidate-only robustness statement cites007 PASS5843439638. No013–017 results appear. Scope excludes certified touching, count, charge, partner correspondence, continuous isolation and infinite-cutoff convergence. No data, styles, scripts or model changes. Existing responsive table/details classes are reused. No new browser-rendering validation claimed; Claude desktop/mobile presentation review requested.

**Version 30 (DRAFT, prepared by Claude; not saved in Sites; not publishable yet).** `v29-v30.patch` changes only the `#candidate-touchings` panel in `dist/index.html`.
- **Table:** cutoff f is added (R3 b–f, R1 a–f, R2/R4 c–f), with links to CONTROLS-E-022 (5844681636) and CUTOFF-F-023 (5844720468).
- **Removed:** the v29 caveat that the R3/R1 e evidence was baseline-only.
- **Added:** a "one more shell" paragraph. It says the e→f changes are about 4×10⁻¹² meV (round-off), and it says explicitly that agreement between finite cutoffs does not establish infinite-cutoff convergence.
- **Kept:** all v29 exclusions and the v29 mobile card layout.

**Publication gate:** publish only after Codex gives an independent PASS on both 022 and 023. The two links should then point to (or add) those PASS comments. After that, Claude presentation review applies to the Sites-saved bytes.

Restore with `python materialize.py /new/absolute/output 30`.


## Published v30

Sites source `883cef3e73b2afbb5aa156e738e944c304e20acc`. Codex 022 PASS 5845331701 and 023 PASS 5845331772; Claude passed the reviewer packet at 5845340302. The source adds both PASS links and producer-results links. Only the candidate panel in dist/index.html differs from v29; candidate-evidence.css is byte-identical. All 62 file hashes verify through materialize.py OUT 30. Claude exact-version presentation PASS 5845378941 received; deployment succeeded. See v30-publication.json.
