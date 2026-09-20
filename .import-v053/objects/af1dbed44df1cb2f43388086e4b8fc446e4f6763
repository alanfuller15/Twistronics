# Named strain conventions

The uploaded `v039_full` variant is reproduced exactly: inverse reciprocal
deformation, kinetic matrix `[I+(1-beta)E_lab] R^T`, and the legacy gauge formula
applied directly to lab components. Its default constructor still selects the
older `I-E` option, so explicit selection is mandatory.

For the separately specified nearest-neighbor monolayer model, let lab strain
be E and crystal-to-lab rotation be R, so the bond deformation is F=(I+E)R.
The first-order crystal-Pauli kinetic matrix is `R^T[I+(1-beta)E]`. Compute the
gauge from `E_crystal=R^T E R` and rotate that vector back to the lab.

The unrotated velocity and gauge formulas follow
[Oliva-Leyva and Naumis, Eqs. 1 and 13–15](https://arxiv.org/pdf/1404.2619).
The rotation mapping is our explicit coordinate derivation. The independent
bond calculation uses deformed nearest-neighbor vectors and exponential
hopping, solves the actual Dirac point, and compares the cone metric J^T J.
It therefore checks more than the sign of a one-dimensional toy dispersion.

`strain_audit.py` reruns 36 monolayer checks and nine direct comparisons at the
campaign layer rotation of 0.525 degrees. The lab-frame prediction has
second-order residuals under strain halving. For the uploaded convention,
the remaining discrepancy is first order in strain at fixed rotation.
At layer strain 0.0015 and direction 0 degrees, the maximum cone-metric error
is 6.77e-5 versus 9.22e-6 for the lab-frame prediction; gauge-displacement error
is 5.27e-5 versus 2.80e-6 inverse Angstrom. These are monolayer diagnostics,
not bilayer gap corrections. The omitted rotation terms scale as strain
times twist angle; they can be deliberately excluded in a declared joint
small-angle expansion, but are present in the specified rotated-bond model.

`lab_nn_full` is included as a separately named sensitivity adapter and tested
at the Hamiltonian level. It is not silently substituted into the primary
campaign replay. Neither variant supplies a strain-dependent interlayer
tunneling law, relaxation, experimental validation, or a unique physical
strained-bilayer Hamiltonian. Those choices remain open.
