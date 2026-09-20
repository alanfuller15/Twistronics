# Next bounded batch after our v052

All four named preparation event types now have measured windows in both engines at N4/N6: upper-pair birth (v050), extra flat-pair birth and annihilation (v051), and lower-pair birth (v052). This does not by itself complete the preparation route.

1. **Original-flat-pair preparation/frame replay.** Start at A=B=T=0,phi=0,ratio=0.8,eps=0.003,theta=1.05 with explicit lab_nn_full. Continue the original flat pair to A=0.2 at B=0, then to B=−0.25. Use parameter-frame transport and refinement, distinct two-seed continuation, mesh/radius charge checks and an explicit root/relative-frame join into the retained v044 step_000. Pilot a sparse N4 grid before freezing the decisive spacing, then both N4 engines before N6. Existing local charge/root anchors are seeds, not substitutes for the frame replay. Basis geometry remains strain-defined, but preserve engine/geometry/cutoff tags and do not assume an absolute historical gauge sign.
2. **Separate lower unlink collision.** Use the last accepted lower-root inventory from the v044 B leg (T=0,B=−0.4) to establish its subsequent bracket. The already measured flat-pair T leg did not measure this lower-gap event. Choose and freeze the appropriate full-chart or local gate from its actual inventory.

The v052 lower roots at B=−0.25 join the historical v044 roots within about 4e−15 in all four engine/cutoff cases. This is useful momentum provenance only; it does not remove step 1's frame-transport obligation.

Keep at most two single-thread workers, sparse bounded batches and checkpointed records. Deliver one ZIP with explicit remaining scope. Do not rerun completed event location passes unless a new model choice or failed join requires it.
