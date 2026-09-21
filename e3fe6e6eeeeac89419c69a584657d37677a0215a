# TWISTRONICS LOG — v051 — Two-seed brackets for the preparation-route events

**Scope.** The team's next batch is the preparation route, and my v047 contribution to it was count differences and extrapolations, which their gate correctly refused as "located". This entry replaces those with what the gate consumes: both roots of each pair tracked through the event, gaps and separations at every step, the pair's relative charge measured on the open side, cross-engine root agreement, and a fold estimate from \(\text{sep}^2\). Four events, all under `lab_nn_full` (bm exact; `tbg_ref` root cross-check), \(N=4\), \(\phi=0\), \(w_0/w_1=0.8\), \(\epsilon=0.3\%\). **Candidates, not accepted events:** rank-one zero, curvature, transverse slope and open-side minima checks are the team's. New: `fold_track.py`, `fold_track_B.py`, `fold_track_prep_A.json`, `fold_track_prep_B.json`.

---

## 1. Results

| event | gap | parameter | open-side charge | last tracked (param, sep) | first closed (param, box min) | fold estimate |
|---|---|---|---|---|---|---|
| U-pair birth | flat\(_2\)–upper | \(A\) at \(B=0\) | OPPOSITE | (0.1370, 0.01281) | — (tracked to 0.137) | **\(A^\ast\approx0.13682\)** |
| extra flat-pair birth | flat | \(A\) at \(B=0\) | OPPOSITE | (0.1770, 0.02444) | (0.1760, 0.0214 meV) | **\(A^\ast\approx0.17630\)** |
| extra flat-pair annihilation | flat | \(B_{\rm sym}\) at \(A=0.2\) | OPPOSITE | (−0.0320, 0.03588) | (−0.0340, 0.0243 meV) | **\(B^\ast\approx-0.03402\)** |
| lower-pair birth | lower–flat\(_1\) | \(B_{\rm sym}\) at \(A=0.2\) | OPPOSITE | (−0.2200, 0.00667) | (−0.2000, 1.18 meV) | **\(B^\ast\approx-0.21971\)** (two-point fit; weak) |

Tracked sequences (bm roots; `tbg_ref` roots agree to \(\le4\times10^{-11}\) at every step except where noted):
- U birth: sep 0.08902, 0.07019, 0.05465, 0.04510, 0.03307, 0.02505, 0.01281 at \(A=0.145,0.142,0.140,0.139,0.138,0.1375,0.137\).
- Extra flat birth: 0.05629, 0.04811, 0.03817, 0.02444 at \(A=0.180,0.179,0.178,0.177\); gone at 0.176.
- Extra flat annihilation: 0.14051, 0.12143, 0.09431, 0.07602, 0.05082, 0.03588 at \(B=0,-0.01,-0.02,-0.025,-0.03,-0.032\); gone at −0.034. The extra pair at \((A,B)=(0.2,0)\) is (0.4553, 0.5653), (0.5954, 0.5756).
- Lower birth: two roots at \(B=-0.25\), (0.657, 0.6395), (0.699, 0.5858), separation **0.06815** (team v048: 0.06814524, confirming their inventory correction of v047); 0.00667 at −0.22; gone at −0.20.

Every open-side pair is OPPOSITE, as births and annihilations of a pair in one gap must be. The v047 candidates (0.137, "(0.16, 0.18)", "(−0.02, −0.04)", "between −0.10 and −0.25") are each consistent with these brackets and superseded by them.

## 2. Two tracker defects, caught

- The first run used the wrong gap index (`w[gi+2]-w[gi+1]` on six bands; correct is `w[gi+1]-w[gi]`), the same off-by-one as v034 §4. The tell was a 17 meV "box minimum" where a node should be. Fixed before any table.
- Refinement from two seeds can land on one root ("sep 0.00000, gaps \(10^{-10}\)"). The tracker now seats both roots by a local dense search whenever the refiners coincide or a gap opens, and declares the pair gone only when that search finds no root and the box minimum is positive.
- `tbg_ref.refine` has no seating step, and its root jumped at three of 26 steps (differences \(2\times10^{-2}\)–\(5\times10^{-2}\)); at the other 23 the engines agree to \(\le4\times10^{-11}\). The bm roots are the record; the ref column is a cross-check, and the jumps are a known limitation of the unseated refiner, not a model disagreement.

## 3. Status
Preparation route: four event candidates with two-seed brackets and open-side charges, ready for the team's fold and open-side gates. The lower un-link collision remains unaddressed. The coverage statement of record is the team's `COVERAGE.json` (v050 §1).

## 4. Self-corrections this entry
- Off-by-one gap index, third occurrence in this project (v034, v039's estimator, here). Rule: any gap function is now checked against a known positive gap before use, which is what the "box minimum" printout did here by accident and will do on purpose.
