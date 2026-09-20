# Strain convention: what is resolved and what is not

This entry fixes coordinates for an explicitly specified monolayer model. It
does not silently change either Hamiltonian used in the campaign replay.

Let E_l be the symmetric strain tensor in lab coordinates and R_l rotate the
unstrained layer's crystal axes into the lab. The real-space deformation is
F_l=(I+E_l)R_l. Reciprocal vectors transform by F_l^(-T). In crystal coordinates,
the strain is E_l^cr=R_l^T E_l R_l.

For nearest-neighbor hopping t_j=t exp[-beta(|F_l delta_j|/a_CC-1)], expand about
the actual strained Dirac point. To first order in strain, the kinetic matrix
acting on lab relative momentum, with Pauli axes tied to the crystal, is

M_l = R_l^T [I+(1-beta)E_l].

The geometric term is +E_l; the hopping term is -beta E_l. With beta=3.14 the
combined coefficient is -2.14. The gauge displacement, to the same order, is

A_l^lab = R_l { beta/(2 a_CC)
              (E_l,xx^cr-E_l,yy^cr, -2 E_l,xy^cr) }.

Using a lab tensor directly in the crystal-axis gauge formula omits a rotation
correction. These expressions assume a particular valley and zigzag crystal
axis. They are not an instruction to change signs while retaining incompatible
coordinates elsewhere. The coefficient -1 in the supplied team's velocity
tensor is not the coefficient implied by beta=3.14 under this hopping model.

The continuum tensor and gauge shift follow the uniformly strained
nearest-neighbor derivation in
[Oliva-Leyva and Naumis, Eqs. 13–15](https://arxiv.org/pdf/1404.2619).
The rotation mapping above is our explicit coordinate transformation.
The geometric deformation in
[Bi, Yuan and Fu, Eq. 9](https://arxiv.org/html/1902.10146v1)
must be read with that paper's conventions and approximations.

`strain_check.py` constructs the deformed bond vectors and exponential hopping
directly, solves the Dirac-point equation, and differentiates the Bloch sum.
It compares the gauge-invariant cone metric J^T J, avoiding a spinor-phase
ambiguity. It tests beta=0 and 3.14, three strain directions, two layer rotations,
and three strain magnitudes. The full first-order expression has second-order
residuals under strain halving. All 36 checks pass. This is evidence for these
monolayer formulas, not independent experimental validation of the bilayer.

The replay therefore retains two declared approximations:

| Engine | Reciprocal deformation | Kinetic tensor | Gauge |
| --- | --- | --- | --- |
| original | linearized | R_l^T | legacy lab-component formula |
| partner | exact inverse | (I-E_l)R_l^T | legacy lab-component formula |

Neither includes every term of the above consistent monolayer expansion. Both
also hold the chosen interlayer tunneling matrices fixed as strain changes.
Adopting a revised physical bilayer requires an explicit choice of tunneling,
relaxation and frame conventions, followed by a new labeled sensitivity run.
The present calculations establish model-specific robustness, not a uniquely
corrected TBG Hamiltonian.
