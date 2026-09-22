# A local coupled event branch as strain varies

The unknown vector has ten entries:

`y = (fp1, fp2, Ep, fq1, fq2, Eq, fu1, fu2, Eu, D)`.

Strain `s` is an external scalar parameter. All 87 reciprocal indices are fixed.
For each named node, the three equations are the real symmetric components of
a 2-by-2 Schur complement. The tenth equation places the upper-gap node on the
supporting line of the flat-node segment. Separate uniform inequalities require
that it lies strictly inside the finite segment, keep the periodic image lifts
unchanged, and separate the three momentum neighborhoods.

The exact argument below assumes exact enclosures of its inputs. Computed
eigenvalues, norms, inverses and frames use ordinary floating point with the
allowances in `PLAN.json`. The implementation does not provide outward-rounded
enclosures of those operations. Its conclusion is explicitly conditional.

## Nonlinear strain dependence

Let the fixed strain tensor have eigenvalues 1 and -nu. In layer l,
`E_l(s)=s L_l`, with `||L_l||=1/2`. The exact inverse deformation is

`P_l(s)=(I+s L_l)^-1`,
`P_l'=-P_l L_l P_l`,
`P_l''=2 P_l L_l P_l L_l P_l`.

On a cell with maximum absolute strain e, let `d=1-e/2>0`. Then

`||P_l|| <= 1/d`, `||P_l'|| <= 1/(2d^2)`,
`||P_l''|| <= 1/(2d^3)`.

The three q vectors are differences of layer-deformed Dirac vectors of length
KD. Therefore `||q_j'|| <= KD/d^2` and `||q_j''|| <= KD/d^3`.
Each reciprocal vector is a difference of two q vectors, giving twice these
bounds. Tunnelling is constant; the layer potential is affine in D.

The kinetic block is `hbar_v M_l(s) p_l(s,f) · sigma`, transformed to the fixed
real basis. `M_l` is affine in s; the gauge shift is `s a_l`. For an affine
momentum predictor `fbar(s)=f0+vf(s-s0)`,

`p = sum_j (m_j+fbar_j) G_j(s) + delta_l q0(s) - s a_l`,
`p' = sum_j [(m_j+fbar_j) G_j' + vf_j G_j] + delta_l q0' - a_l`,
`p'' = sum_j [(m_j+fbar_j) G_j'' + 2 vf_j G_j'] + delta_l q0''`.

Triangle inequalities bound these uniformly using
`|m_j+fbar_j| <= |m_j+f0_j|+h|vf_j|` and
`||G_j(s)|| <= ||G_j(s0)||+h sup||G_j'||`.
The second derivative of a kinetic block is
`hbar_v (2 M_l' p_l' + M_l p_l'') · sigma`.
The operator norm of a real Pauli-vector block is its vector length, and the
kinetic derivative is block diagonal. Taking the maximum over retained indices
and layers gives a uniform `M2` bound on the full Hamiltonian's second derivative
along the predictor. The affine D predictor has zero second derivative.

Similarly, momentum coefficients `A_j(s)=H_fj(s)` satisfy
`||A_j(s)-A_j(s0)|| <= h L_j`, with
`L_j = hbar_v (||M_l'|| sup||G_j|| + sup||M_l|| sup||G_j'||)`
maximized over layers. Native-engine controls check these formulas against
actual matrices. Those checks support implementation consistency; sampling
is not the derivation of the uniform bounds.

## Fixed frames and the coupled projected Jacobian

At a located center, fix orthonormal pair frame F and complement Q separately
for each node. With that node's energy E, define

`P=F^T H F-E I`, `B=Q^T H F`, `K=Q^T H Q-E I`,
`S=P-B^T K^-1 B`.

Use components `g(S)=(tr(S)/2,(S00-S11)/2,S01)`. When K is invertible, `S=0`
is a double eigenvalue. The complementary inertia `(lo, dim-lo-2)` fixes its
ordered band indices `(lo,lo+1)`. A uniform complementary gap preserves that
inertia throughout each tube. The bound on K is not a direct bound on every
neighboring gap of the full Hamiltonian.

For fixed image shifts, write `e=fq-fp+lift_q` and `w=fu-fp+lift_u`. The geometric
residual is `gamma cross(e,w)`, with declared scale gamma=1000. This rescaling
changes numerical conditioning, not the zero set. Its gradient is

`grad_p = (e_y-w_y, w_x-e_x)`,
`grad_q = (w_y,-w_x)`, `grad_u=(-e_y,e_x)`.

Assemble the 10-by-10 projected Jacobian J from the three local `(f1,f2,E)`
blocks, the shared D column, and this geometry row. Retain the actual center
projected residual g0 and strain derivative gs. Set `C=inv(J)`, `v=-C gs`,
and `ybar(s)=y0+v(s-s0)`. The code retains `I-CJ` and `gs+Jv` instead of
treating their numerical residuals as zero.

## Uniform Schur bounds

For each node, define the total moving Hamiltonian derivative
`T=H_s+vf1 A1+vf2 A2+vD AD` at the center. Let

`G0=min|eig(K0)|`, `b0=||B0||`,
`nv=||T-vE I||`, `bv=||Q^T T F||`, `R=(h^2/2) M2`.

Along the predictor,

`Gline=G0-h nv-R`, `Bline=b0+h bv+R`.

The projected Taylor remainder is bounded by R per symmetric component, while
the Schur correction is bounded by `Bline^2/Gline`.
The geometric predictor is quadratic in strain, with remainder
`gamma h^2 |cross(vq-vp,vu-vp)|` after its constant and linear terms.
These bounds, with the declared allowances, form a ten-component vector z.
The predictor displacement of the fixed-point map is bounded by

`Y = |C g0| + h |C(gs+Jv)| + |C| z`.

Use `c_i=sum_j |C_ij|`,
`rho=max(1e-6,4 max_i(Y_i/c_i))`, `r_i=rho c_i`.
No acceptance-driven adjustment of this radius rule is made.

In the full box `|y-ybar(s)|<=r`, set `a_j=||A_j(s0)||+h L_j` and
`b_j=||Q^T A_j(s0) F||+h L_j` for momentum derivatives. D's coefficient is
constant and energy enters K as `-E I`. Thus

`Gfull=Gline-a1 rf1-a2 rf2-aD rD-rE`,
`Bfull=Bline+b1 rf1+b2 rf2+bD rD`.

For coordinate j in `(f1,f2,D)`, the Schur-correction derivative is bounded by
`2 b_j Bfull/Gfull + Bfull^2 a_j/Gfull^2`; its energy derivative is bounded
by `Bfull^2/Gfull^2`. Add `h L_j` to the projected momentum derivative error.
The geometry gradient is affine in node coordinates, so its deviations are
bounded directly by predictor travel and coordinate radii. Put these component
bounds into the full 10-by-10 error matrix Ebound.

The weighted contraction bound is

`q = max_i [((|I-CJ|+|C| Ebound) r)_i/r_i]`.

Require `q<=0.5`, `max(Y/r)+q<=0.8`, and every `Gfull>0.001 meV`.
Banach's theorem then gives one coupled zero in the box for each strain, with
inner radii `r max(Y/r)/(1-q)`. Continuity of the matrix family and uniform
contraction make that zero a continuous function of strain. This is a local
event branch D(s), not a claim about all events at that strain.

## Segment geometry and joins

Uniform ranges of e and w give interval bounds on `e·w` and `e·e` by exact
endpoint products and squares. Division by the strictly positive squared-length
interval bounds `t=(e·w)/(e·e)`. Require t strictly inside `(1e-5,1-1e-5)`.
The full coordinate tube must remain inside the unit square, and both lifted
differences inside the open `(-1/2,1/2)` image patch. Each pair of root boxes is
separated in at least one momentum coordinate for every neighboring periodic
image. These are uniform tube conditions, not endpoint-only checks.

Adaptive bisection retains every failed parent. At each final leaf endpoint,
an independently located center receives a zero-width 10D certificate. Its
inner enclosure must fit strictly inside every incident full tube cross section.
Outer-box overlap alone never establishes identity. This joins local branches
across the declared strain interval. The two starting meshes share this same
physical equation but receive their own interval and endpoint checks.

## Limits of the numerical conclusion

The exact implications depend on the stated inputs being valid enclosures.
This implementation uses floating-point allowances, not a verified-arithmetic
library. For the distinction between computed norms and verified norm bounds,
see S. M. Rump, *Verified bounds for singular values, in particular for the
spectral norm of a matrix and its inverse*, BIT 51 (2011), 367–384,
[author PDF](https://www.tuhh.de/ti3/paper/rump/Ru10a.pdf). Its verification
algorithms are not implemented here.

The report reconstructs native matrices, stored frames, primitive data,
certificates, coverage and joins using the published bound functions. It is a
fresh numerical reconciliation, not an independently coded proof. Both engines
share the geometry/basis adapter and diagnostic framework. No complete node
inventory, full parameter-space event surface, charge transport, braid,
Euler-class change, physical validation or infinite-cutoff conclusion follows.
