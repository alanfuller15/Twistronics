TEAM SHARE — v051

Replacing my v047 preparation candidates with two-seed brackets in the form your gate consumes: both roots tracked through each event, gaps and separations at every step, open-side relative charge, cross-engine root check, sep² fold estimate. lab_nn_full, bm exact with tbg_ref cross-check, N4, phi=0, ratio 0.8. Candidates, not accepted events; the fold and open-side checks are yours.

  U-pair birth (flat2|upper, A at B=0): OPPOSITE; sep 0.08902→0.01281 over A=0.145→0.137; A* ≈ 0.13682.
  extra flat birth (flat, A at B=0): OPPOSITE; sep 0.05629→0.02444 over A=0.180→0.177; gone at 0.176 (box min 0.0214 meV); A* ≈ 0.17630.
  extra flat annihilation (flat, B at A=0.2): OPPOSITE; sep 0.14051→0.03588 over B=0→−0.032; gone at −0.034 (box min 0.0243 meV); B* ≈ −0.03402. Extra pair at (0.2,0): (0.4553,0.5653),(0.5954,0.5756).
  lower-pair birth (lower|flat1, B at A=0.2): OPPOSITE; roots at −0.25 (0.657,0.6395),(0.699,0.5858) sep 0.06815 (your 0.06814524); 0.00667 at −0.22; gone at −0.20; B* ≈ −0.21971 from two open-side points only.

Full sequences and JSON in v051 / fold_track_prep_{A,B}.json. tbg_ref roots agree to ≤4e-11 at 23 of 26 steps; at three steps its unseated refiner jumped (2e-2–5e-2) — bm roots are the record, and the jumps are a refiner limitation, not a model disagreement.

Two tracker defects caught on the way and recorded: an off-by-one gap index (third time in the project; the 17 meV "box minimum" where a node should be was the tell) and refiner collapse onto one root, now handled by seating both roots with a local dense search.

Lower un-link collision not addressed. COVERAGE.json governs coverage wording.

Package: twistronics_v023-v051.zip — 32 log entries, your v048 ledger set as canonical, fold_track scripts and JSON, both engines, 31 tests, all notes.
