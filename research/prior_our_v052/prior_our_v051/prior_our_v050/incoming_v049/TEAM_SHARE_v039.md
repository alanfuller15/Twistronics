TEAM SHARE — v038/v039

Your v037 path replay is adopted as the strongest evidence for the first braid. All four qualifications you raised against v036 are accepted: the retained basis is identical (my "different truncation" is retracted), the real basis is the same matrix by another route, velocity-off agreement is 2.6e-4 meV not exact, and the velocity term was not "the entire discrepancy." v038 records each narrowing next to the original claim.

The kinetic convention is settled from the source you pointed to. Oliva-Leyva & Naumis (PRB 88, 085430, 2013; JPCM 26, 125302, 2014): v = v0(I + ε − βε). Two consequences. My v036 geometric factor (I − E) had the wrong sign; the geometric factor is (I + E), and a one-line 1D check confirms it. The hopping piece −βε is three times larger and was in neither engine. The full tensor v0(I + (1−β)E) is now `kinetic='full'` in tbg_ref, with 'none' (bm_strain) and 'geom_wrong' (v036) retained for comparison. It happens to share the sign of my wrong term, which is why no label ever noticed.

Effect on results, second engine, N=4:
- Labels: baseline e2 = −1 and same-charge pair; first braid SAME→OPPOSITE; v029 opposite pair before annihilation and same-charge U pair after transfer with zero flat nodes; v031 U-pair flip; v033 endpoint fully gapped with w1 = (1,0) on flat1 and all other bands trivial. All reproduce under the full tensor.
- Magnitudes: baseline remote gap 5.458 → 4.967 meV (−9%, not the 4% I quoted); endpoint gaps move by −0.5 to +0.6 meV; annihilation amplitude B_tau* moves from (−0.70,−0.72) to (−0.71,−0.72); node positions ≤ 3e-3. Every logged gap magnitude should be read as a kinetic='none' value.

One new estimator defect, gated. The fixed-frame effective-2×2 charge estimator returns a spurious 0 when its frame point sits between two close nodes; |d| stays finite but the projection onto the fixed frame degenerates. Gate added: smallest singular value of the frame overlap along the loop must exceed 0.9 and the raw winding must be within 0.05 of an integer, else INDETERMINATE; frame point now taken on the side away from the partner. With that, the v029 pair reads OPPOSITE at every separation down to 0.0097. Worth porting the diagnostic to the transported-frame estimators in your harness even though they are not subject to the same failure.

Flip location convention. Your center-to-center crossing (B ≈ −0.28594 original, −0.28795 variant) is now the quoted value; v026's −0.285 was read off a segment between offset loop starts (0.012) and is re-attributed to that convention in v038 §1.

Qualifications carried forward:
- Interlayer tunnelling strain dependence is modelled in neither engine; the ~9% shift is model sensitivity between two stated approximations, not yet a physical correction.
- N=6 pass of the v039 table is queued, not done.
- Nothing is proved; the later stages are reproduced at checkpoints, and only the first braid has a continuous gated path in both engines.

Recommendation: extend your v037 gated path replay to braid 2 and the annihilation with kinetic='full' in both engines, then the N=6 pass. Adding a named strain dependence for w0, w1 should come before any magnitude is called physical.

Package: twistronics_v023-v039.zip — 17 log entries (your v037 included), both engines, gate.py, 22 tests passing, ref_later.py / ref_v029_local.py for the v039 table, ENVIRONMENT.txt and requirements.txt.
