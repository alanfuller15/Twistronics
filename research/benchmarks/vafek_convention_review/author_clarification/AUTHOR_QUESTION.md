# Clarification of the K-valley projected strain term

In arXiv:2502.08700v2, we read A1 and A10 (HTML 26 and 35) as K-valley matrices and use B25-B27 (HTML 70-72) for the flat-band columns. At `v'=epsilon_xy=0`, our first-order projection of the c-double-prime strain term gives

\[
-\frac{2\gamma c''v k_y\epsilon_-}{\gamma^2+v^2|\mathbf k|^2}I,
\]

whereas B28 (HTML 73) prints the positive sign.

For a self-contained calculation, put `N=gamma²+v²|k|²`, with `gamma` nonzero. In a K-valley column gauge equivalent to the printed columns, their c2 and f blocks are

\[
C=\frac{\gamma I}{\sqrt N},\qquad
F=-\frac{v(k_x I+i k_y\sigma_3)}{\sqrt N},\qquad
T=-ic''\epsilon_-\sigma_3.
\]

Then `C†TF+F†T†C` gives the negative scalar above. A within-valley column-phase change leaves it unchanged.

We take `mu1=mu2=0`, consistent with the simplification at the end of Sec. II, and omit `M' epsilon_plus` as explicitly stated after B28. The c-Gamma3 components of these flat-band columns vanish, so c, c-prime, gamma-prime and mu1 terms have zero first-order projection; that is distinct from assuming their coefficients vanish. Restoring constant mu2 adds a ky-even scalar and does not remove the ky-odd difference as an identity.

Are we missing a valley, coordinate or basis mapping between these passages? B28's right factor lacks the K subscript; B31's following prose (HTML 76) and B41 (HTML 86) retain K-first columns and the K boost `k+q/2`. Does the later journal version clarify this? A mapping or pointer to an accessible accepted manuscript would help resolve our benchmark choice.

Our reading is provisional; we have not selected a production sign or established an error in the paper. The journal equations remain unchecked.

Evidence: [source audit](https://github.com/alanfuller15/Twistronics/blob/310ff15c076253f8721af6b6042d8206838d7f95/research/benchmarks/vafek_convention_review/source_audit/README.md), [direct printed-equation check](https://github.com/alanfuller15/Twistronics/blob/613fecbf7a14d0d60cd7af1b2956c9ecedd187db/research/benchmarks/vafek_convention_review/source_audit_followup/README.md), and [completed context review](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5286979704).
