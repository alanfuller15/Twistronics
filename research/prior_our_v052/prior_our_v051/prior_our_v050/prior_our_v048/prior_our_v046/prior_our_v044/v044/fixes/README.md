# Explicit cutoff padding — optional patch

This patch is not used in the primary v044 replays. It adds `cutoff_tol` to
both constructors while retaining their historical defaults: BM 1e-6,
TBG 1e-9, in inverse Angstroms. Set the same value explicitly when comparing
the same finite Hamiltonian. It does not change the nominal N or geometry.

The counterexample is N=4, eps=0.003, phi=15.843560625048124 degrees,
geometry='exact', kinetic='lab_nn_full'. Reciprocal indices (-4,3) and
(4,-3) exceed the nominal cutoff by about 5e-7 inverse Angstroms. The
uploaded BM includes them (dimension 196); uploaded TBG excludes them
(dimension 188). No spectral difference between these unequal spaces should
be attributed to differing topological estimators.

With either common tolerance, 1e-9 or 1e-6, the patched models use identical
indices and their full matrices agree at the tested ordinary and unwrapped
momenta. Eight tests verify this witness, preserve both default matrices
bit for bit, and reject negative/nonfinite padding. The nominal cutoff is
still a finite approximation; a common padding does not establish cutoff
convergence or make the hard boundary smooth as strain varies.

Use cutoff_tolerance.patch or the two complete patched files. Engines under
../engines/ remain the unchanged partner upload. When reporting numerical
results, record kinetic, geometry, N and cutoff_tol together.
