# Research status and reading order

This page is for a researcher joining the Twistronics project who needs to know **where the current work is**. The repository's front page and illustrated guide present the historical **v062** landing material. That material is still valid as a record, but it is not the whole project. Current work is a software-acceptance review of one migrated measurement consumer.

## Where this page sits

| Item | Value |
|---|---|
| Current review branch | [`migration-contract-review`](https://github.com/alanfuller15/Twistronics/tree/migration-contract-review) at checkpoint [`44dc669`](https://github.com/alanfuller15/Twistronics/commit/44dc66951057a995ee0999c785aca3e0e6c67092), v078p contract review |
| This page | Added on `claude/twistronics-github-handoff-gvo3uf` in draft [PR #2](https://github.com/alanfuller15/Twistronics/pull/2), which targets that branch. The PR is not merged. |
| Historical landing material | [README](../README.md) and [illustrated guide](visual-guide/README.md), based on source commit [`7776ffd`](https://github.com/alanfuller15/Twistronics/commit/7776ffd3ca219ff976e578103b895e25db60dcc2) and covering v060/v062 |
| Who owns what | The original Claude/Fable conversation owns the v078 implementation corrections. The docs on PR #2 cover intake and review only. |

## Reading order

### 1. The scientific question and the declared model

- **Question.** How do band crossings (nodes) and their topological charge relationships behave along parameter paths in a continuum model of strained twisted bilayer graphene? The first two paragraphs of the [README](../README.md) and the [illustrated guide](visual-guide/README.md#the-question-in-one-minute) give the plain-language version and the terminology.
- **Historical model state (v062).** The illustrated guide varies the tunnelling ratio w₀/w₁ from 0.991 to 1.000 at A=0, B=−0.4, T=−0.8, φ=80° and N8 cutoff.
- **Current migration model (different from v062).** The current review measures a different state, frozen in the migration plan (`plan.model_defaults` in [`CONTRACT_EXPECTATIONS.json`](../research/benchmarks/migration_contract_review/CONTRACT_EXPECTATIONS.json)):
  - N=4, θ=1.05°, ε=0.003, φ=0°, A=0.2, w₁=110 meV, w₀/w₁=0.8.
  - `lab_nn_full` kinetic term and exact geometry.
  - The perturbation is B times a sine σz harmonic, at B ∈ {−0.25, −0.30}.
  - Both valleys.
  - Two coupled settings: radius 0.012 with 96/300 loop/transport intervals, and radius 0.008 with 192/600. Radius and mesh are not varied independently.
  - The consumer performs its own node discovery (`find_nodes`).
  - This parameter origin is documented in [guarded variant measurements](../research/benchmarks/variant_guard_repairs/README.md#mirrored-pairs).

### 2. Retained numerical evidence

- **v078p (current).** The eight labels reproduce in a fresh extraction ([v078p review](../research/benchmarks/migration_contract_review/README.md#numerical-replay)): B=−0.25 gives SAME and B=−0.30 gives OPPOSITE, in both valleys and both settings.
  - The labels agree exactly. Excluding timings, the largest difference in a numeric row field is 3.33067e-16, and the largest diagnostic difference is 8.88178e-16.
  - All 16,472 diagnostic rows are retained.
  - Full Hamiltonians and eigenvectors are not retained.
- **v077p (earlier).** The same eight classifications, with their sampled gate margins ([v077p review](../research/benchmarks/partner_migration_review/README.md)):

  ![Eight sampled classifications and gate margins from the v077p replay](../research/benchmarks/partner_migration_review/migration_review.png)

  *This is a retained v077p figure; its inputs are recorded in [`FIGURE.json`](../research/benchmarks/partner_migration_review/FIGURE.json). It shows N=4, both valleys and two coupled settings. It checks sampled consistency only. It makes no continuous-path or physical-validation claim, and it was not regenerated for this page.*

- **Historical v062.** Eleven measured ratios in two separately coded engines ([v062 report](../research/v062/REPORT.md), [coverage ledger](../research/v062/COVERAGE.md), [illustrated guide](visual-guide/README.md)). According to [`sources.json`](visual-guide/sources.json), the guide's figures come only from retained v060/v062 records. They do not show the migration model.

### 3. Software acceptance review

The eight retained classifications agree in the supplied and replayed v078p records. The open question is whether the delivery software **accepts only valid evidence**. Read the reviews in this order:

1. [v073p review](../research/benchmarks/variant_controls_review/README.md) and [v074p review](../research/benchmarks/variant_response_review/README.md): the valley implementation was corrected. Topology safeguards stayed open.
2. [Guarded variant measurements](../research/benchmarks/variant_guard_repairs/README.md): opt-in guarded APIs with enforced sampled gates and 38 regression tests.
3. [v076p self-check review](../research/benchmarks/partner_selfchecks_review/README.md): the numerical diagnostics hold up, but the delivery checks are not yet an enforcing gate.
4. [v077p migration review](../research/benchmarks/partner_migration_review/README.md): the migrated consumer reproduces all eight labels. However, it exited 0 when every measurement was rejected or no node pair was found, and it lost earlier rows after a discovery exception.
5. [v078p contract review](../research/benchmarks/migration_contract_review/README.md) and [`FABLE_NEXT_PASS.md`](../research/benchmarks/migration_contract_review/FABLE_NEXT_PASS.md) (current): the v077 failure paths are repaired, but the partner verifier still accepts invalid records. The reviewer checker [`check_records.py`](../research/benchmarks/migration_contract_review/check_records.py) is the bounded acceptance reference.

### 4. Correction intake and ownership

- [Team handoff](team-handoff.md): the baseline, outstanding items, evidence requirements and scope limits.
- [Correction intake](correction-intake.md): maps each correction to its existing probe and closing evidence, and lists what an incoming package must contain.
- [Checker readiness receipt](intake-evidence/README.md): shows this workspace can run the baseline checker.

### 5. Separate diagnostic: the projected-model convention

This is not part of the migration corrections. The [`vafek_2025`](../research/benchmarks/vafek_2025/README.md) paper benchmark has two in-project assemblies of the projected Hamiltonian.
- **Same boost:** at the same (K, Q) their spectra differ. PR #4, commit [`caa700b`](https://github.com/alanfuller15/Twistronics/commit/caa700bfa285b889502bc902779b114b868b1aad), draft and not merged, shows this.
- **Opposite boost:** they are unitarily equivalent once Q is reversed. [Convention review note](convention-review/README.md) gives the derivation and the hash-bound reproduction.
- **Open question:** which signed boost, coordinate or coupling convention the paper uses remains **UNRESOLVED**. The next gate is a signed-convention table checked against the primary source.

## Evidence and status

| Category | Item | Status | Where it is recorded |
|---|---|---|---|
| Observed baseline behavior | The eight SAME/OPPOSITE labels agree exactly between the supplied and replayed records. The largest numeric row-field difference, excluding timings, is 3.33067e-16. | Observed at `44dc669` | [v078p review](../research/benchmarks/migration_contract_review/README.md#numerical-replay) |
| Observed baseline behavior | The partner verifier accepts 10 invalid record variants; the reviewer checker refuses all 15 negative cases | Observed defect | [`CONTRACT_PROBES.json`](../research/benchmarks/migration_contract_review/CONTRACT_PROBES.json), [`CHECKER_REGRESSIONS.json`](../research/benchmarks/migration_contract_review/CHECKER_REGRESSIONS.json) |
| Observed baseline behavior | A returned `status='REJECTED'` is recorded as ACCEPTED, and a duplicate plan reports COMPLETE | Observed defect (synthetic controls) | [v078p review](../research/benchmarks/migration_contract_review/README.md#other-retained-controls) |
| Observed baseline behavior | A geometry-stage error leaves rows but no model or geometry context, summary or manifest | Observed defect (synthetic control) | Same section |
| Observed baseline behavior | The linter falsely accepts two claims, and the failure-control suite does not enforce its outcomes | Observed defect | [`LINT_PROBES.json`](../research/benchmarks/migration_contract_review/LINT_PROBES.json), [`FABLE_NEXT_PASS.md`](../research/benchmarks/migration_contract_review/FABLE_NEXT_PASS.md) |
| Separate diagnostic | For the `vafek_2025` projected model, U·H_literal(K,Q)·U† = H_direct(K,−Q) with U = τx⊗σx; the same-Q gap difference of 1.53207 meV is reproduced | Verified for the implemented model; the paper's convention is **UNRESOLVED** | [Convention review](convention-review/README.md) |
| Verified intake tooling | The baseline checker accepts the intact run (exit 0) and refuses `wrong_label` for exactly the intended error (exit 1). The runner enforces exact outcomes, with 12/12 synthetic regressions passing. | Verified at `8281f9e`; confirmed by Codex review 5286522495 | [Receipt](intake-evidence/README.md) |
| Implementation corrections | Content-consistency checking in the delivery gate | **UNREVIEWED** | [Correction intake](correction-intake.md#correction-map), item 1 |
| Implementation corrections | Returned status/schema and a unique case inventory | **UNREVIEWED** | Items 2a and 2b |
| Implementation corrections | Plan-to-constructor binding | **UNREVIEWED**. The baseline defect is reproduced by synthetic probes in draft PR #3, commit [`43fbc8f`](https://github.com/alanfuller15/Twistronics/commit/43fbc8fc484c4bb5639286409e811cdb8d66cbab), not merged. | Item 3; [probe receipt](https://github.com/alanfuller15/Twistronics/blob/43fbc8fc484c4bb5639286409e811cdb8d66cbab/research/benchmarks/consumer_boundary_review/evidence/20260923T0328Z/RECEIPT.json) |
| Implementation corrections | Finalization after errors, and behavior when the output directory already exists | **UNREVIEWED**. The existing-directory defect is reproduced by synthetic probes in draft PR #3, commit `43fbc8f`. | Items 4a and 4b; [PR #3 review README](https://github.com/alanfuller15/Twistronics/blob/43fbc8fc484c4bb5639286409e811cdb8d66cbab/research/benchmarks/consumer_boundary_review/README.md) |
| Implementation corrections | Metric-bound, precision-correct linting | **UNREVIEWED** | Item 5 |
| Implementation corrections | Enforcing failure controls, with forced and clean metamorphic evidence kept separately | **UNREVIEWED** | Items 6a and 6b |

## What is blocked, and on whom

The next deliverable is the **corrected v078 follow-up package**. The original Claude/Fable conversation is producing it in response to [`FABLE_NEXT_PASS.md`](../research/benchmarks/migration_contract_review/FABLE_NEXT_PASS.md). Every row marked UNREVIEWED above waits on it.

The Claude Code session that maintains PR #2 has repository context only. It **cannot retrieve unpublished files from that conversation**. The package has to be committed to this repository or attached to PR #2 before review can start. [Correction intake](correction-intake.md#incoming-delivery-requirements) lists what the package must contain.

Codex has published synthetic probes for the two previously untested gaps in draft [PR #3](https://github.com/alanfuller15/Twistronics/pull/3), commit [`43fbc8f`](https://github.com/alanfuller15/Twistronics/commit/43fbc8fc484c4bb5639286409e811cdb8d66cbab) ([review README](https://github.com/alanfuller15/Twistronics/blob/43fbc8fc484c4bb5639286409e811cdb8d66cbab/research/benchmarks/consumer_boundary_review/README.md)). They show that a changed N or strain in the plan is ignored even though the run reports COMPLETE, that an existing output directory is silently replaced, and that a constructor error truncates prior rows and diagnostics. That PR is unmerged, so these are commit links, not paths on this branch. The probes are baseline defect evidence, not a consumer repair, and the corrections stay UNREVIEWED.

## Scope limits

These limits apply to the current work:
- the same finite N=4 model family and two coupled radius/mesh settings, both valleys, and the shared guarded framework;
- sampled checks only;
- no continuous-path proof, complete node inventory, independent physical or experimental validation, Euler-class change or cutoff-convergence claim.

The historical v062 material keeps its own limits, stated in the [illustrated guide](visual-guide/README.md#what-remains-open).
