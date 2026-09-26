# STATE-SCAN-002: teaching from computed state mixing

Frozen implementation: 8dee23377371702df88d998ac29bd9c89304456e.
Input pilot execution: 25b6f71e8864e38f1b4f48a6cd391bbdda0f2790.
Producer: Codex. Independent execution review: PENDING.

17 new momentum-coordinate samples through pilot point 14; two sequential jobs of 9 and 8 points, 34 eigensolves total. Fixed y=23605/32768; x=22503/32768 plus offsets -8..8 divided by 131072. These are momentum coordinates k=xG1+yG2, not real-space positions or time frames.

The selected pair reaches a 63.605978-degree subspace angle between model sizes, while the four-state group stays below 0.559381 degrees. Even the least-contained normalized combination in the smaller-model pair has at least 99.99216179% weight in the larger-model four-state group at every sampled point.

At the center, the smaller model's upper selected state overlaps about 19.8% with the larger model's upper selected state and 80.2% with the state just above the pair. This gives a concrete teaching picture: the group stays similar while energy-ranked members mix. Individual squared overlaps depend on eigenbasis choices; the subspace measures are the more robust comparison.

Sampled upper pair gaps range 2.153759–10.239945 micro-eV (a), 1.583929–9.754485 micro-eV (b). The sampled minima lie at different momentum positions; no interpolation-based minimum is reported. No comparison here uses time evolution.

## Reproduce

Fetch the implementation commit and use its source/dependencies. Run materialize.py NEW_OUTPUT --repo PATH_TO_REPO. It checks every retained byte and replays metrics without physical eigensolves. plot.py NEW_OUTPUT recreates PNG/PDF and derives SUMMARY.json. Archive includes all vectors, spectra, metric rows, runtime provenance and receipts. plot.py is a postprocessing script, not part of the frozen physical runner.

Resource bounds: 3 GiB/worker, 64 MiB/file, 90 seconds/job, sequential jobs. No independent-review prerequisite: explicit user authorization is recorded in SPEC.json. Scientific source inputs are hash-bound and compared with exact Git content before execution and replay. Review is requested after computation. Neither PR merged; site unchanged.
