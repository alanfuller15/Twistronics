# TWISTRONICS LOG — v044 — Connections adopted; braid-1 route anchors

**Scope.** Disposition of the team's v043 connections batch (their entry; my v043 is the v042 disposition, so this is v044 in the shared record, and their share is filed as `TEAM_SHARE_v043_team.md`). No corrections to prior entries arose. Contribution here: the anchor roots and labels for the one route still open before a connected campaign can be claimed — braid 1 with its deepening and unlinking legs into the v028 checkpoint — computed in both engines under the declared model at \(N=4\) and \(N=6\), so the team's next batch starts from verified endpoints. New file: `anchors_braid1.py`.

---

## 1. Adopted from the team's v043

Two connecting routes reproduce with `kinetic='lab_nn_full'` in both unchanged v041 engines at \(N=4\) and \(N=6\): 160 primary states, all gated.

| route | states | label along the route | joins |
|---|---|---|---|
| pre-annihilation flat pair: \((A,B_\tau,\phi)=(0.2,-0.4,0)\to\phi\,60\to A\,0\to\phi\,65\to B_\tau\,-0.70\) | 19 | OPPOSITE throughout | v028 checkpoint → v042 annihilation starting roots |
| post-annihilation upper pair: \((0,-0.74,65)\to\phi\,80\to B_\tau\,-0.8\to w_0/w_1\,0.99\) | 21 | SAME throughout | v042 post-transfer roots → v042 braid-2 starting roots |

Endpoint joins within \(4.4\times10^{-14}\); cross-engine node difference \(\le5.0\times10^{-6}\); \(N=4\to6\) node shift \(\le3.6\times10^{-4}\); carried charges constant within every run. Their changing-basis transport guard (match \((\text{layer},m,n,\text{spinor})\) coefficients after a declared cell pullback; record discarded frame weight; reject overlap < threshold or loss > 0.02) had minimum overlap 0.898 and maximum loss \(5.3\times10^{-4}\). Smallest resolved exterior gap on a comparison path 0.053 meV. Stop/resume reproduces frames bit for bit.

With this, the following legs of the v023→v033 story are reproduced under one declared model in two engines: braid 2 window, first-annihilation window (v042); v028 → annihilation, post-transfer → braid 2 (v043-team). The checkpoints v029 post-transfer, v031, v033 and the ratio-1.04 candidate are reproduced at fixed parameters (v039, v040, v042).

## 2. Braid-1 route anchors (this entry)

\(A=0.20,\ \phi=0,\ w_0/w_1=0.8,\ \epsilon=0.3\%\); `bm_strain` with `kinetic='lab_nn_full', geometry='exact'`; `tbg_ref` with `kinetic='lab_nn_full'`. Roots are unwrapped fractional coordinates; both engines agree to \(\le1.4\times10^{-12}\) at every state.

| state | \(N\) | root 1 | root 2 | label (both engines) | ref overlap min |
|---|---|---|---|---|---|
| \(B=-0.25\) | 4 | (0.745877, 0.612337) | (0.517235, 0.827766) | SAME | 0.995 |
| | 6 | (0.745901, 0.612328) | (0.517306, 0.827803) | SAME | 0.995 |
| \(B=-0.30\) | 4 | (0.740755, 0.611085) | (0.519801, 0.827664) | OPPOSITE | 0.996 |
| | 6 | (0.740777, 0.611076) | (0.519860, 0.827711) | OPPOSITE | 0.996 |
| \(B=-0.40\) (deepened) | 4 | (0.731911, 0.609186) | (0.527235, 0.830631) | OPPOSITE | 0.997 |
| | 6 | (0.731932, 0.609177) | (0.527276, 0.830687) | OPPOSITE | 0.997 |
| \(B=-0.40,\ B_\tau=-0.40\) (v028 checkpoint) | 4 | (0.770668, 0.646970) | (0.529556, 0.932538) | OPPOSITE | 0.998 |
| | 6 | (0.770788, 0.646851) | (0.529486, 0.932892) | OPPOSITE | 0.998 |

The last row is the start of the team's pre-annihilation route; the \(B=-0.30\) row is the end of the braid-1 window. These are fixed-parameter checkpoints with two-seed roots, not path replays: the crossing inside \((-0.25,-0.30)\), and whether any adjacent node crosses the pair's segment during \(B:-0.30\to-0.40\) or \(B_\tau:0\to-0.40\), is exactly what the next batch has to trace. v028 §2 recorded that the un-linking leg pulled U1 back across the segment when started from \(B=-0.30\) and not from \(-0.40\); that observation is under `kinetic='none'` and should be re-established, not assumed.

## 3. Campaign coverage under the declared model (both engines)

| leg | status |
|---|---|
| baseline \(e_2=\pm1\), same-charge pair | reproduced at fixed parameters (v041) |
| braid 1 window | anchors here; path replay open (v037 was `none`/team variant) |
| deepening \(B\to-0.40\), un-linking \(B_\tau\to-0.40\) | anchors here; path replay open |
| v028 → first annihilation | **path replayed** (team v043) |
| first annihilation | **path replayed** (v042) |
| post-transfer → braid 2 | **path replayed** (team v043) |
| braid 2 | **path replayed** (v042) |
| cleanup after braid 2 → endpoint | open |
| endpoint, per-band \(w_1\) | reproduced at fixed parameters (v042) |

Shared-author and shared-harness caveats as stated by the team apply to every row.

## 4. Next
Team batch: braid-1 path with deepening and un-linking from the anchors in §2, then the cleanup windows after braid 2 to the endpoint. After that the campaign is connected end to end under one declared model, and the remaining tasks are model-side (tunnelling strain law) and numerical (\(N>6\)).

## 5. Self-corrections this entry
- None to the physics. One bookkeeping item: the team and I both produced a "v043"; resolved by numbering as above rather than renaming either file's content.
