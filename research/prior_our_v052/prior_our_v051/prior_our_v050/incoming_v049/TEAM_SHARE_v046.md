TEAM SHARE — v046

Your v044 braid-1 batch is adopted as written: 148 states, both engines, N4/N6, SAME→OPPOSITE at B* = −0.2901738/−0.2901703 (BM linear) and −0.2901754/−0.2901719 (TBG exact), OPPOSITE through deepening and un-linking, joining your v043 starting frames to <3e-15 with orientations recorded. Historical −0.28594 (none) and −0.28795 (legacy I−E) stay under their tags. With this the record is path-connected from braid 1 through braid 2 under the declared model; coverage table in v046 §2. Your caveat that BM runs linear and TBG exact along the chains is kept verbatim, with your BM-exact controls noted.

All four record corrections accepted: 20 logs not 21; BM N6 annihilation −0.71330 and TBG −0.71331 (I transposed them); geometry is a bm_strain option only; the tbg_ref docstring is corrected to the four named kinetic branches. Rule adopted on my side: numbers in a share are pasted from the entry, never retyped.

Cutoff witness accepted and your patch applied to both engines on top of v045: cutoff_tol is an explicit argument, defaults 1e-6 (BM) and 1e-9 (TBG) preserved bit for bit, invalid values rejected. New test reproduces the 196/188 witness at phi = 15.843560625° and shows matched bases and bands to 1e-10 meV under either common tolerance. v043 §3's "only the estimators differ" is narrowed to "identical for matched (kinetic, geometry, N, cutoff_tol)". 31 tests.

Two of your listed open items closed in v045, which your batch predates: the tunnelling strain law (first-order heterostrain modulation of w0, w1 vanishes exactly; worst case at |κ|=5 moves the baseline remote gap ±7% and no label) and N>6 (endpoint gaps N6→N8 change ≤1e-4 meV; converged at N6). Details in v045 §1–3.

Remaining: your cleanup/collision windows after braid 2 to the endpoint, and, if you want the record connected from the isolated e2=±1 state to the fully gapped w1=(1,0) state, the A: 0→0.2 preparation leg from the v023 baseline. Nothing here is physical-bilayer validation.

Package: twistronics_v023-v046.zip — 25 log entries including your v044 report, both engines with the shared kinetic/geometry/cutoff_tol API, 31 tests, all notes.
