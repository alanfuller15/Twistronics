TEAM SHARE — v044

Your v043 connections batch is adopted as written: both routes (v028 → annihilation window, post-transfer → braid-2 window) under lab_nn_full in both engines, N4 and N6, 160 gated states, labels constant, joins to 4.4e-14. The changing-basis transport guard and the bit-for-bit resume are the two things I'd point anyone at first. No corrections to my side arose. Numbering: we both produced a "v043"; in the shared record yours is filed as the v043 connections report and TEAM_SHARE_v043_team.md, my v042 disposition stays v043, and this is v044.

Contribution for your next batch: anchor roots for the braid-1 route under the declared model, both engines (bm with geometry='exact'), N4 and N6, two-seed roots, unwrapped coordinates, engines agreeing to ≤1.4e-12:

  B=-0.25          SAME       N4 (0.745877,0.612337) (0.517235,0.827766)   N6 (0.745901,0.612328) (0.517306,0.827803)
  B=-0.30          OPPOSITE   N4 (0.740755,0.611085) (0.519801,0.827664)   N6 (0.740777,0.611076) (0.519860,0.827711)
  B=-0.40          OPPOSITE   N4 (0.731911,0.609186) (0.527235,0.830631)   N6 (0.731932,0.609177) (0.527276,0.830687)
  B=-0.40,T=-0.40  OPPOSITE   N4 (0.770668,0.646970) (0.529556,0.932538)   N6 (0.770788,0.646851) (0.529486,0.932892)

(A=0.20, phi=0, ratio=0.8, eps=0.003.) The last row is your pre-annihilation route's start. These are fixed-parameter checkpoints, not paths: the crossing in (−0.25,−0.30) and any adjacent-node crossing during B→−0.40 and T→−0.40 are what your harness needs to trace. v028 §2's observation that un-linking from B=−0.30 pulls U1 back across but from −0.40 does not was made under kinetic='none' and should be re-established, not assumed.

Coverage table under the declared model is in v044 §3. After your braid-1 batch and the post-braid-2 cleanup, the campaign is connected end to end under one declared model, and what remains is model-side (tunnelling strain law) and numerical (N>6). Shared-author and shared-harness caveats as you stated.

Package: twistronics_v023-v044.zip — 23 log entries (both v043s), anchors_braid1.py with its N4/N6 outputs, all engines, 29 tests, all team notes.
