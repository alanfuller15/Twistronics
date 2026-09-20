TEAM SHARE — v041

Your v040 is adopted: braid-2 crossing at ratio 0.99053 (N4) / 0.99076 (N6), first-annihilation root −0.71355 / −0.71348 with the fold diagnostics, post-transfer upper pair SAME, endpoint and ratio-1.04 candidate with identical per-band w1. All three of your corrections to v039 are accepted and recorded next to the original text: the close-pair miss is a seed-coverage failure (my merge-tolerance arithmetic was wrong), the endpoint lower gap is 23.037 meV at N4 (boundary seeds; second edge minimum of the project), and the annihilation shift is ~0.0016, not 0.01.

Your action 2 is done. The STRAIN_NOTE convention — R^T [I+(1−β)E] with the gauge computed from R^T E R and rotated back — is now kinetic='lab_nn_full' in BOTH engines. bm_strain has the option for the first time; tbg_ref has no default any more and raises unless kinetic is given. Cross-engine agreement at N4 for none / full / lab_nn_full: node positions to 8.5e-7, remote gap to 2e-4 meV (5.4578/5.4580, 4.9663/4.9665, 4.9707/4.9709). lab_nn_full vs full differs by 0.004 meV and 7e-4 in node position, the O(εθ) you predicted. Whether a declared joint small-angle expansion should drop those terms is a choice, not an error either way; the difference sits below every other uncertainty.

Source-review items closed in tbg_ref: node_charge returns None (no 0 sentinel); per-loop overlap logged and the minimum over both loops reported; radius bound enforced for any request and coincident seeds rejected; gap_min is bounded Nelder–Mead in [0,1]² with edge/seam seeds. Not added: a loop-mesh/radius agreement gate — your harness has it, and I'd rather point at that than duplicate it.

Tests: 27 passing (17 regression + 10 cross-implementation), including one per kinetic option for cross-engine agreement, one that tbg_ref refuses an unspecified kinetic, and one that an invalid loop yields None.

Next, in order: rerun your v040 path replays with lab_nn_full in both engines (now possible, closes the one-engine limit for those legs); connecting legs under the declared model with two-seed continuation; a named strain law for w0, w1; N>6 on the endpoint gaps. Nothing in this package is physical-bilayer validation; it is one declared model, now in two engines.

Package: twistronics_v023-v041.zip — 19 log entries (your v037 and both v038s referenced; my v038 in place), both engines with the shared kinetic API, gate.py, 27 tests, cross_kinetic.py, all prior team notes.
