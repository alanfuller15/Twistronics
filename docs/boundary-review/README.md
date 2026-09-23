# Review note: boundary gluing by polar maps

**Status: the corner cocycle for polar-projected sewing maps is NOT established. The gluing-repair step is OPEN.** This note is additive. It records the outcome of the review exchange on draft [PR #5](https://github.com/alanfuller15/Twistronics/pull/5), commit [`9293295`](https://github.com/alanfuller15/Twistronics/commit/929329564c676bbfc6e483dbf145416aeb25270d), `research/benchmarks/research_questions_006/`:
- Claude review [5790873292](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5790873292).
- Codex review [5288150576](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5288150576).

It changes no production code or earlier evidence, runs no physical Hamiltonian or cutoff comparison, and selects no sign convention.

## Setting

A boundary edge i carries a contraction Sᵢ, such as the archived truncated shift, from a source fibre with orthonormal frame E_src to a target fibre E_tgt. The proposed selected-fibre map is the polar isometry

```
J_i = E_tgt · polar(E_tgtᵀ S_i E_src) · E_srcᵀ   on range(E_src),
λ_i = 1 − s_min(E_tgtᵀ S_i E_src),       ε_i = ‖(J_i − S_i)|E_src‖.
```

## 1. Commuting contractions do not give a corner cocycle

Here is an explicit counterexample in the **most favourable** case.
- The ambient maps commute exactly: S₁ = diag(1, c, 1) and S₂ = diag(1, 1, c).
- F₀ has columns (1,1,0)/√2 and (−1,1,2)/√6.
- Every corner fibre is the exact image: ran S₁F₀, ran S₂F₀ and ran S₁S₂F₀.
- The corner rotation is the angle of (path J₂ʳ·J₁ᵇ)ᵀ(path J₁ᵗ·J₂ˡ) on the far fibre.

| c | max link loss λ | passes 0.05 sewing gate | corner rotation (rad) | ‖path difference‖ | telescoping bound Σε |
|---:|---:|---|---:|---:|---:|
| 0.5 | 0.3876275643 | no | 0.0814555876 | 0.081433 | 1.361042 |
| 0.95 | 0.0336303394 | **yes** | 0.000505966775 | 0.000506 | 0.133353 |

Codex reproduced both corner values independently in review 5288150576.

**Why it happens.** Both path composites equal X·N with X = S₂S₁F₀ = S₁S₂F₀, so each is X(XᵀX)^(−½)·O for some O ∈ O(2). Polar projection is nonlinear, so the two O factors differ in general. Commuting ambient maps fix the image but not the rotation within it.

With constant, commuting, **orthogonal** transitions and exactly equivariant fibres, J equals T restricted to the fibre, and the corner closes. The retained control gives a defect of 4.5e-16 (`orthogonal_control_defect` = 4.518979695706721e-16 in `RESULTS.json`).

## 2. A conservative operator-norm bound (Codex, review 5288150576)

- **Per-edge bound.** The fitting identity (C − F₁O)ᵀ(C − F₁O) = 2(I − |M|) − L gives εᵢ ≤ √(2λᵢ). For exact-image fibres, where Rᵢ = 0, the sharper bound εᵢ ≤ λᵢ holds, because (S − J)F₀ = F₁·O·(|M| − I).
- **Corner bound.** Telescoping each two-edge isometric path against its ambient contraction product, then using S₁S₂ = S₂S₁, gives

```
‖J₂ʳ·J₁ᵇ − J₁ᵗ·J₂ˡ‖ ≤ Σᵢ εᵢ.
```

This is an **operator-norm** bound, not a lifted-phase certificate. As the table shows, it is loose: 0.133 against an actual 5.1e-4 at c = 0.95. A nonzero cocycle defect needs a **consistent reference or repair construction** before an ordinary glued bundle can be claimed. Adding its size to an error budget is not enough. That construction is open.

## 3. Detecting off-target mismatch needs the complementary residual

My earlier suggestion to use P₁(H₁S − SH₀)P₀ was **wrong**. It measures only the on-target block.

**Counterexample.** Let H₀ = H₁ = diag(0, 0, 1), P₀ = P₁ = diag(1, 1, 0), and S a rotation by θ in the (e₁, e₃) plane.
- The projected residual is exactly 0.
- The off-target mismatch is ‖(I−P₁)SP₀‖ = |sin θ|.
- At θ = 0.2, the mismatch is 0.1986693 while the sewing loss is only 0.0199334.

**Correct statement (Codex).** Let B⊥ = (I−P₁)(H₁S − SH₀)F₀. For spectral P₁ and H₀F₀ = F₀A₀, the off-target part R = (I−P₁)SF₀ satisfies

```
H₁⊥ R − R A₀ = B⊥.
```

A certified **cross-spectrum** separation δ > 0, between the spectrum of H₁ on range(I−P₁) and that of A₀, then gives ‖R‖_F ≤ ‖B⊥‖_F/δ.
- A gap within H₀ alone does not supply that separation.
- In the counterexample, ‖B⊥‖ = |sin θ| and δ = 1, so the bound is tight.
- 200 seeded random spectral cases show no violation.

## 4. Conditions that remain for any polar-glued boundary

1. **Uniform invertibility.** s_min(Mᵢ(x)) ≥ 1 − λ along every whole boundary edge, for all continuous x and not only at samples, so that Jᵢ is C² wherever P is.
2. **Corner compatibility.** This means either exactness on the selected fibres at the corners (Lᵢ = Rᵢ = 0, so J = S restricted, with commuting S), or an explicit consistent repair. Section 1 shows it isn't automatic.
3. **Connection compatibility**, stated covariantly as ∇₁J − J∇₀.
   - A constant ambient T intertwines Kato transport. A polar J(x) generally does not.
   - The strip change of the glued holonomy then includes this defect in addition to the curvature flux.
   - Writing it as an angle derivative is valid only in the specified horizontal frames.
4. **Orientation.** Each transition must preserve the chosen fibre orientation, with det > 0 in oriented frames.
5. **Finite versus infinite basis.** The glued finite bundle is a chosen construction.
   - Comparing it with the physical infinite-basis translation, where H(k+G) = S·H(k)·S† holds exactly, needs retained per-edge leakage L, off-target R via B⊥ and a certified δ, and the corner defects.
   - These are needed at two cutoffs, with control between samples.
   - None of that is run here, and none of it would establish cutoff convergence.

## Reproduce

[`check.py`](check.py) builds only fixed 3×3 and small seeded random matrices, refuses to overwrite its output, and exits 1 on failure. [`RESULTS.json`](RESULTS.json) and [`RUN.log`](RUN.log) retain the run: 17/17 checks, exit 0, Python 3.12.3 and NumPy 2.3.5. [`MANIFEST.json`](MANIFEST.json) binds the files.

```sh
OPENBLAS_NUM_THREADS=1 python docs/boundary-review/check.py --output /tmp/boundary-review-new.json
```

## Scope

These are synthetic algebra checks. They are not production or physical calculations, and not interval enclosures. They give no graphene Euler value, no conclusion about retained labels and no sign choice. The v078 corrections remain with the original Fable conversation.
