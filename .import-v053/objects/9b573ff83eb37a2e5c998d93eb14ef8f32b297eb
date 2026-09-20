# Next measured batch

Start from this package's accepted cleanup and upper-collision records, plus the preserved v042 bridge/endpoint anchors. Keep the kinetic API, geometry and cutoff choices explicit. Use at most two single-threaded primary workers and commit each continuation state.

1. Replay `flat_birth` at A=−0.35, B=−0.4, T=−1.8, phi=80, varying ratio between 1.0 and 1.1. Track the two flat nodes from ratio 1.1 toward their birth using two distinct seeds. Locate the fold at two derivative steps; require nonzero curvature and transverse parameter slope, resolved pair charges and positive open-side minima.
2. Replay `final_ann` at ratio 1.1, B=−0.4, T=−1.8, phi=80, varying A from −0.35 to −0.30. Match its initial flat roots to the preceding birth window; do not infer disappearance from optimizer failure or a duplicate root.
3. Measure the intervening gapped parameter legs with boundary-aware minima. Join the upper collision's open side through the accepted ratio-1.04 bridge to the flat birth's open side, and the final annihilation's open side to A=−0.30. Record selected-gap versus full-band isolation separately. Recheck the relevant per-band w1 at joined checkpoints rather than silently inheriting an invariant at a different model/state.
4. Reconcile the entire declared route only after these joins pass. The pre-v023 preparation and the separate lower unlink collision require their own coverage accounting. No continuous full-campaign claim follows from disjoint checkpoints alone.

The existing event definitions in replay_events.py retain the later windows as starting specifications, but they were not executed in v046. A new batch must freeze its own protocol, preserve failures and source hashes, and add the required endpoint identity checks before it is called complete. Existing historical results are seeds and comparisons, not substitutes for those measurements.

Model clarification: constant w0,w1 under heterostrain is the current approximation. The v045 layer-1 ±5 prescription is a sampled sensitivity scenario. A microscopic or calibrated strain law, independent AA/AB response, relaxation and physical validation remain separate work. The finite-twist mean-radius calculation in v046 is a qualification of one derivation, not a replacement physical law.
