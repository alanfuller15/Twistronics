# Fable — make the self-checks enforce their declared delivery contract

The reproduced basis-dependence diagnostic is useful. The supplied metamorphic rows also reproduce. Preserve those records and the input archive; fix the delivery machinery before calling it a release gate.

## 1. Fail the process when an asserted relation fails

`metamorphic.py` prints the count of false `holds` rows but does not exit nonzero. The review injects one failing MR1 and observes a normal status-0 exit. Write the complete result record first, then return failure when any asserted relation fails. Treat exceptions and incomplete runs as failures too.

MR6 is a diagnostic with unconditional `holds=True`. Give diagnostics a separate status rather than counting them as passed assertions. Distinguish the eight tested assertion rows from that one reported periodicity discrepancy. Bind each row to its model, ordered basis, momentum samples, tolerance, source hashes and execution status. Retain the suite's current limited coverage: e.g. MR3/MR4 test six central energies at one momentum, and MR7 has three comparisons, not every preceding transformed model.

## 2. Replace the placeholder README generator

The shipped `regenerate_readme.py` reads JSON, defines a helper, and prints “tables regenerated”; it never writes the README or emits a table. A sentinel README remains byte-identical after execution. Implement generation of clearly delimited result sections from validated fields. Test that changing one input metric changes the corresponding output cell and no unrelated claim. A success message must follow a successful write or a verified up-to-date check.

## 3. Bind claims to fields and models, not any nearby number

Keep the prose linter as a warning tool; use an explicit claim manifest for enforceable numerical statements. Each claimed value needs an evidence file, content hash, JSON pointer (or record selector), metric, units, model/basis identity, formatting/tolerance rule and allowed derivation. Scope claims need an expected case set compared against executed cases with unique identities and terminal outcomes.

The review's invalid fixtures expose these concrete gaps:

- A measured `5.3 meV` is skipped because it has only two digits after punctuation is removed, including when it disagrees with its cited record.
- A number from an unrelated field in the same JSON can validate the wrong metric.
- A nonexistent `missing.json` and a meaningless backticked identifier can satisfy the scope rule without any resolvable evidence.
- Prefixes `19`/`20`, intended for dates, also suppress measured values.
- The blanket “both below 1e-12” shortcut accepts changes by many orders of magnitude despite the stated relative tolerance.

Make these retained fixtures fail appropriately while retaining valid binding/notation controls. Avoid solving the false alarms by broadening exemptions. Handle dates, input parameters, method statements, historical statements and measured outputs as explicit claim types. A linter alone cannot establish that arbitrary natural-language claims are scientifically valid.

Run the actual delivery command on its own package. The shipped README currently produces six findings with exit status 1. Some are policy/input-number bookkeeping, but the MR2 failure paragraph cites the basis diagnostic while quoting the different-grid metamorphic value. Resolve that binding rather than hiding it.

## 4. Preserve the topology improvements, retain the unresolved boundaries

The changed start angle now reaches the actual winding path; the reviewed negative-start mismatch is fixed in the coordinate control. Wilson external-gap checks, the highest pair's lower gap, fractional Wilson indices, pair-link overlap and single-band adjacent-overlap refusal also improve.

Two transposed k2 sewing overlaps have the same singular values; they do not cover the k1 sewing direction. The review's zero-k1 sewing control returns a normal result with zero closure, and single-band final sewing can likewise return zero without refusal. Add actual k1/base/closure gates, positive finite policy validation, and the missing root/loop isolation checks. Support the highest single band with only its existing neighbors. Return or bind the actual sampled path arrays and distinguish point counts from interval counts.

The public `variant_guard_repairs` APIs are a separate, opt-in implementation addressing these contracts. Do not claim the bundled v076p routines inherited those gates automatically.

## 5. Qualify the sparse change

The old 2×2 LU counterexample now returns “inertia unavailable,” and six native review samples agree. Keep that improvement. The docstring also promises a reconstruction-residual check, but `_fact` does not compute one. Matching permutations and nonzero scaled pivots do not by themselves establish the claimed floating-point accuracy. The header's “Closes F01–F06” and the window's “proved” language remain inconsistent with the narrower caveat.

No native dense comparison is mandatory inside this bundled `window`; the review performed its own comparison afterwards. Use the already published dense-checked supported mode, or justify and test a different supported numerical criterion. General sparse root/event guards and accounting remain open; do not close them through prose.

## Scientific interpretation of the basis check

Changing the retained basis reduces the tested 17°/77° discrepancies, and increasing cutoff reduces them further. That is useful finite-model sensitivity evidence. A common set of integer labels alone is not a derivation of exact symmetry covariance: spell out the momentum transformation, basis permutation/sewing and finite-cutoff limitations before asserting a general C3 invariant.

The diagnostic tests 17°/77°; it does not directly retest the historical 0°/60° calculation. Leave that attribution qualified until the actual historical settings are recovered and tested. Do not present numerical agreement as a complete node inventory, physical validation, or a novelty result.
