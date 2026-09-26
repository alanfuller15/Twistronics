# THREE-FRONT-001 execution — independent audit pending

Implementation: 23ef1c1d182d399636cbb3de75ce9d77e8909e1c. Producer: Codex. Cutoff pre-execution Claude PASS: PR #2 comment 5842312301, receipt retained. All seven jobs exited normally. No new execution was independently audited when this packet was written.

- Depth-11: 480 children, 369 newly accepted, 111 unresolved; 3,396 endpoint factorizations. Candidate accepted area 4194193/4194304 = 99.9973535538%, 3,040 accepted cells. Status remains INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE. The source ceiling remains finite-cutoff-a local isolation only.
- Cutoff: 64 paired points, 128 eigensolver starts. Sampled upper-gap minima: a 0.0030899654503215856 meV at (22501/32768,23605/32768); b 0.003027308218406688 meV at (22505/32768,23605/32768). Central-index band correspondence across cutoffs is unproved. These are sampled minima, not global minima or gap closure. Cutoff-a regression vs scout002 differs by at most 3.5890630745e-12 meV.
- Dynamics: two widths at grids16/32, 1,280 eigensolver starts, 81 frames per width/grid. Fine-grid norm error ≤2.23e-16. Common-window density L1 errors 0.35432644 and 0.25465130 FAIL the frozen 0.05 tolerance. Fine boundary probabilities reach 3.78% and 2.01%. The new display frames are withheld from the live site. This new model is a coarse-grained envelope calculation and drops reciprocal-component interference; not microscopic density or a reproduction of the earlier site calculation.

## Small review chunks

At the user's request, each refinement log is packaged as six independently compressed 20-record chunks (24 chunks total). CHUNK_SUMMARY.json gives outcomes for each. The original runs were four uninterrupted 120-cell jobs already in progress when the request arrived; chunk packaging is not a claim of independent 20-cell executions. New refinement jobs should be capped at 20 cells under a separately frozen protocol.

Large transfer files are split again into small transport parts listed in TRANSPORT.json. These are transport boundaries, with no scientific meaning.

## Reproduce replay

1. `python research/benchmarks/three_front_001_execution/materialize.py /new/evidence` checks and reconstructs all original file bytes.
2. Create a separate clean checkout/worktree of source commit 23ef1c1d182d399636cbb3de75ce9d77e8909e1c. The source checker intentionally requires that exact HEAD.
3. In that checkout: `python research/benchmarks/three_front_001/summarize.py /new/evidence 23ef1c1d182d399636cbb3de75ce9d77e8909e1c` (numpy required). This makes no physical calls. Compare SUMMARY.json and PARTITION.json with retained bytes.

All modes, frames, receipts, native provenance, full interval records and point spectra are retained. No new site scientific data is promoted; no topology, seam, cutoff-convergence or experimental claim; neither PR merged.
