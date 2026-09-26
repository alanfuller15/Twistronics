# Review note: the two projected assemblies agree after boost reversal

**Status: the paper's signed convention is UNRESOLVED.** This note is additive. It reviews the diagnostic in draft [PR #4](https://github.com/alanfuller15/Twistronics/pull/4), commit [`caa700b`](https://github.com/alanfuller15/Twistronics/commit/caa700bfa285b889502bc902779b114b868b1aad), `research/benchmarks/vafek_convention_review/`. That diagnostic stays unchanged as history, and so do the [`vafek_2025`](../../research/benchmarks/vafek_2025/README.md) benchmark and its `model.py`. This note repairs no model, chooses no sign, runs no sweep and contacts no one.

## Two statements that are both true

| Comparison | Result at K=(0.23, −0.17), Q=0.5 | Meaning |
|---|---|---|
| Same (K, Q): literal versus direct | Adjacent band spacings differ by up to **1.5320713556 meV**. | No unitary basis change plus a common energy shift can reconcile them **at the same boost**. This is PR #4's result, reproduced here. |
| Boost reversed: U·H_literal(K, Q)·U† versus H_direct(K, −Q), with U = τx⊗σx | Largest matrix residual **5.7×10⁻¹⁴ meV** over all retained points and parameter sets. Spectra agree to ≤ 7.1×10⁻¹⁴ meV. | Within this implemented model, the two assemblies are the **same Hamiltonian family with opposite boost orientation**. |

The two statements don't conflict, because the reconciliation changes Q. Boost reversal is **not** a symmetry of either assembly on its own: the literal spectra at Q and −Q differ by 1.2986822493 meV at this point. That value equals the sorted-spectrum difference recorded earlier in `vafek_2025` for the two assemblies at the same point.

## Derivation for the implemented matrices

This follows `model.py` at SHA-256 `28af2f9c…0ed3`. The notation is the same as PR #4: x, y and Q are dimensionless, c = c'', e = ε₋, and d± = 1 + (x ± Q/2)² + y².

The two assemblies differ only in the sign of the scalar c–f term, so

H_literal − H_direct = 4cey · diag(1/d₊, 1/d₊, −1/d₋, −1/d₋).

Let U = τx⊗σx, which swaps the valleys and swaps the two components within each valley. Then:

1. **The c and f vectors.** C_Q = diag(d₊^−½, d₊^−½, d₋^−½, d₋^−½). Reversing Q swaps d₊ and d₋, so U·C_Q·U† = C_−Q. Swapping the four diagonal entries of F_Q and reversing Q gives U·F_Q·U† = −F_−Q. The overall minus sign cancels in the quadratic f–f projection.
2. **The interaction blocks.** The parent vector z = (1, i, i, 1)/2 is invariant under U, so its projector is too. Conjugation by U reverses the signs of τz and σz, and hc and hf contain them only in pairs such as τz·a·τz. So U·hc·U† = hc and U·hf·U† = hf; both residuals are exactly 0 in `RESULTS.json`.
3. **The valley blocks.** Swapping the valleys, together with σx conjugation (σx·σy·σx = −σy), preserves the M σ1 and δ terms of the kinetic blocks. It reverses the valley-odd scalar c–f term, which is exactly the difference between the two assemblies.

Together these give **U·H_literal(K, Q)·U† = H_direct(K, −Q)** for the implemented parent state and model definition. Because Q = 0 is the fixed point of the map, **spectral agreement at Q = 0 follows**. That is why PR #4's unboosted off-axis case had different matrices but matching spectra.

An equivalent statement: c'' appears only in the scalar c–f term of each assembly, so H_literal(c'') = H_direct(−c'') entry by entry, with residual ≤ 1.4×10⁻¹⁴ meV.

## Retained reproduction

[`reproduce.py`](reproduce.py) checks the hash of `model.py` before importing it. It builds only 4×4 matrices and refuses to overwrite its output. [`RESULTS.json`](RESULTS.json) records the full residuals, and [`RUN.log`](RUN.log) records the command and exit code 0. It checks, with tolerance 10⁻¹⁰:

- U is unitary, and U leaves hc and hf unchanged (residuals 0).
- U·C_Q·U† = C_−Q and U·F_Q·U† = −F_−Q (residuals 0). The C and F restated in the script reproduce the c–c and f–f terms inside `model.h` to ≤ 4.4×10⁻¹⁶.
- The Q-reversal identity holds at 4 points × 3 parameter sets: the defaults; strain 0.004; and c'' = 1000 with M = −2. The same-Q matrices differ at every off-axis point.
- The c''-sign identity holds at the same 12 combinations.
- PR #4's same-Q adjacent-gap difference is reproduced to 10⁻⁹ meV.
- The spectra agree for the literal assembly at (K, Q) and the direct assembly at both (K, −Q) and (−K, −Q). Literal spectra at Q and −Q differ.
- A search over all 16 Pauli products τa⊗σb, with and without complex conjugation, finds **no** same-(K, Q) equivalence. Under Q reversal it finds τx⊗σx, and τx⊗I combined with complex conjugation.

The run used Python 3.12.3 and NumPy 2.3.5. Hashes for this directory are in [`MANIFEST.json`](MANIFEST.json). To reproduce from the repository root into a new output path:

```sh
OPENBLAS_NUM_THREADS=1 python docs/convention-review/reproduce.py --output /tmp/convention-review-new.json
```

## What stays unresolved

- **The paper's convention.** Which physical sign of the boost q, of the coordinate map K = vk/γ, or of c'' relative to the flat-band gauge and valley labels is implied by the published equations (arXiv:2502.08700v2, HTML Eqs. 35 and 71–74)? This has **not** been checked here. arxiv.org was not reachable from the reviewing environment, so no primary-source comparison was made.
- **The next scientific gate** is a complete signed-convention table checked against the primary source. The sign of γ alone is **not** a resolution: in the direct assembly the flat-band vector comes from a kernel condition that does not depend on sign(γ), so γ acts only through the coordinate map.
- **Scope.** Both assemblies were written within this project, so their agreement is not independent validation. Results at a fixed signed Q depend on the unresolved convention. This note makes no claim about the full `vafek_2025` boost sequence, root search, braiding, Euler class or any experiment.
