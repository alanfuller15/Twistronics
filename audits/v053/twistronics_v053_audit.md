# Twistronics v053 — inspection-only audit

## Summary

The most urgent code finding is stale optimizer metadata: the BM refinement helper can return a second optimization result while retaining the first attempt's success/status fields. The release workflow also depends on a prior ZIP absent from this archive, and its report generator repeats a fixed test-pass statement without checking test evidence. The stored v053 evidence is internally consistent: all 2,477 manifest entries match, the 19 frozen source hashes and eight anchor hashes match, and 76 saved primary frame checkpoints support the reported 76 states and 36 parameter-mesh checks. Layer 1 scanned 738 Python files and flagged 527 missing test relationships, with zero secret-pattern or TODO matches; these are heuristic observations, not correctness verdicts. Layer 2 reviewed the first 14 ranked files, plus a 23-line matching-method excerpt, while Layer 3 checked saved artifacts and fetched dependency/API sources without running project code or tests. This audit does not establish scientific correctness, actual test coverage, complete CVE clearance, or a fresh numerical replay.

## Ranked action list

Colors prioritize the next review or repair; they are not vulnerability severity or exploitability scores. No project fixes have been applied.

1. **RED — Correct the BM helper's final-result metadata before relying on its success flag.** Refresh success/status/message from the final optimizer, preserve both attempts, and make failed/nonfinite outcomes explicit. Original scanner ranks 1 and 5 exposed the defect; an identical method is present in current rank 528. **Tier: fetched + sandbox source inspection. Verdict: fails.** Whether this helper affected accepted v053 measurements is **unverified**.
2. **RED — Bind publication's test-pass claim to a particular test run.** `build_report.py` hard-codes the count and prose; read a test-result artifact tied to source/test/environment hashes, and distinguish historical evidence from a fresh run. Original scanner rank 11. **Tier: sandbox source/data inspection. Verdict: fails as an enforced publication guarantee.** A supplied log does report 18 passes; this is not evidence that those tests failed.
3. **YELLOW — Make release packaging reproducible from supplied inputs.** Parameterize and document the exact prior-archive dependency, or package the preserved prior tree under a revised, explicit provenance contract; create the output directory. Original scanner rank 8. **Tier: sandbox file-existence check + source inspection. Verdict: fails for standalone repackaging of this extraction.** Do not silently substitute a reconstructed archive for the required byte-identical ZIP.
4. **YELLOW — Mark legacy Euler/braid entry points as exploratory, or route them through acceptance gates.** The legacy real-frame guard uses `assert`, which vanishes under Python optimization; the Euler routine returns a winding without rejecting failed orientation/closure diagnostics. Original ranks 13–14. **Tier: fetched + sandbox source inspection. Verdict: fails as a fail-closed scientific acceptance interface.** Their effect on the accepted replay was not established.
5. **YELLOW — Scope coverage and dependency review to active code, then preserve archive results separately.** The scan combines 738 file paths but only 244 distinct contents, and test matching is global across subtrees. Pin transitive/build dependencies and conduct a resolved-environment vulnerability check before making a security-clearance claim. **Tier: sandbox + fetched. Verdict: actual coverage and complete dependency security remain unverified.** This does not justify changing frozen numerical dependencies without a separately labeled comparison.
6. **YELLOW — Keep scientific acceptance explicitly scoped.** Continuous-path proof, infinite-cutoff accuracy, the separate lower unlink collision, and physical-bilayer validation are not established here. Before expanding claims, obtain the appropriate reference calculation/measurement and the inventor's intended acceptance target. **Tier: inventor + execution evidence needed. Verdict: unverified.** The supplied report already discloses these limitations.
7. **GREEN — Preserve the existing evidence bundle and its qualifications.** Retain manifests, frozen source/anchor records, checkpoint data, failure history and sampled-evidence language. **Tier: sandbox artifact checks. Verdict: holds for the consistency checks performed.** Hash agreement does not prove authenticity, chronology, or physical truth.

## Findings table

`Sandbox—static` means inspected source or files, not executed project behavior. `Sandbox—artifact` means read-only hashing, counting, parsing or comparison ran. `[checked]` identifies local evidence; `[fetched]` identifies retrieved authoritative material. Findings are phrased as claims so “fails” has a definite meaning.

| ID | Claim | Tier | Verdict | Provenance and scope |
|---|---|---|---|---|
| S01 | The supplied plug-in contains only three files | Sandbox—artifact | Fails | 17 regular files, 24 ZIP entries including directories; scanner imports another bundled module. |
| S02 | Default scanner mode executes no project code/tests | Sandbox—static + observed run | Holds for inspected path | `audit.py` lines 51, 356–377, 759–760; no `--run-tests` used. Scanner/helper Python itself necessarily executes. |
| S03 | The scanner has no explicit deletion or network operations | Sandbox—static | Holds within reviewed source | All 877 scanner lines and 366 helper lines inspected; no deletion/network APIs. No OS-level syscall trace was collected. |
| S04 | Running the scanner can never write files | Sandbox—static | Fails as an absolute claim | `--json`/`--sarif` use `open(...,'w')`; imports may create bytecode unless disabled. This run used `-B` and fresh output paths outside inputs. |
| S05 | The subprocess call is opt-in and shell-free | Sandbox—static | Holds | One `subprocess.run(cmd.split(), cwd=..., capture_output=True, timeout=60, text=True)` call at line 367; default `shell=False`; gated by `RUN_TESTS`. |
| S06 | Zero reported secret matches proves no secrets exist | Sandbox—static | Unverified | Only selected source extensions and three secret families are scanned; line-wide regex-context suppression can hide concrete values. Non-code data/configs are not secret-scanned. |
| S07 | “Normal” coverage confidence means reliable coverage | Sandbox—static | Unverified | Merely means the subprocess-test heuristic did not cross its threshold. No instrumentation; matching uses global file stems/import lines. |
| L01 | The scan inventoried 738 code files, 43 tests, zero fixtures and 36,281 scanner LOC | Sandbox—artifact | Holds | `layer1.json`; 738 inventory rows, no difference between counted/read source-file totals. LOC uses newline count plus one. |
| L02 | The scan flagged 527 missing test relationships, zero secrets and zero TODOs | Sandbox—artifact | Holds as presence counts | `layer1.json`, 527 SARIF results. This is not 527 proven untested modules. |
| L03 | The project is one Python stack | Sandbox—artifact | Holds as scanner classification | 17 recursive `requirements.txt` markers, Python only; `is_monorepo=false`. This heuristic does not establish organizational boundaries. |
| L04 | The scan found 12 inline-tested files and no subprocess-driven tests | Sandbox—artifact | Holds as heuristic output | Pattern detection only; execution coverage remains unverified. |
| F01 | BM refinement metadata describes the returned optimizer result | Fetched + sandbox—static | Fails | Historical ranks 1/5; AST-identical current `v053/engines/bm_strain.py`, lines 212–234. Second result replaces `res`, but success/status/message remain from first. SciPy documents these fields as optimizer termination metadata. [SciPy 1.17.0](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.OptimizeResult.html) [fetched][checked] |
| F02 | Report publication checks that its “18 tests pass” statement is supported by a matching run | Sandbox—static | Fails | `v053/build_report.py`, lines 26, 49–51 and 75–77: fixed count/prose, no test-result read; PLAN source map excludes tests and this report builder. [checked] |
| F03 | `package_release.py` can repack this extracted delivery without additional inputs | Sandbox—static/artifact | Fails | Lines 9–10 require absent `sequence-outputs/twistronics_v052_reconciled.zip`; output parent also absent and not created. Source-level failure path; packager not executed. [checked] |
| F04 | The legacy real-frame safety guard survives Python `-O` | Fetched + sandbox—static | Fails | `v053/engines/euler.py:21` uses `assert` before discarding imaginary components. [Python assertion semantics](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement) [fetched][checked] |
| F05 | Legacy Euler/braid outputs alone certify the required isolation/orientation/refinement gates | Sandbox—static | Fails as a certification interface | Euler returns determinant/closure diagnostics without rejecting them; its frame function selects only two bands and does not check external isolation. Braid CLI uses fixed radius/mesh and raw winding. Accepted replay impact is unverified. [checked] |
| F06 | `pair_measure`, `frame_checks`, `spatial`, and `replay_prep` show explicit refinement/rejection logic | Sandbox—static | Holds for presence | Deep-read ranks 6–7, 10, 12: charge agreement, restricted phase-resolution retries, overlap/orientation checks and located-gap checks are present. Their numerical correctness is not thereby established. [checked] |
| F07 | Historical `numerical_gate.py` includes explicit finite, residual, overlap, isolation and sewing checks | Sandbox—static | Holds for presence | Rank 4; runtime exceptions are used. Historical code, not proof of current scientific results. [checked] |
| F08 | Historical report builders independently revalidate all numerical claims they print | Sandbox—static | Unverified | Ranks 2–3 reconcile saved records and checks, but contain fixed explanatory/test prose and trust upstream measurement records. No numerical replay performed. [checked] |
| E01 | All manifest entries match the supplied files | Sandbox—artifact | Holds | 2,477 hashes and sizes match; no unlisted project files apart from the manifest itself. [checked] |
| E02 | Current frozen source/anchor and summary-input hashes match | Sandbox—artifact | Holds | 19 source files, eight anchors, four per-case summaries, and the prior v052 summary hash match. Timing of “frozen before run” is not proven. [checked] |
| E03 | Saved primary records support the stated batch counts | Sandbox—artifact | Holds | Four cases × 19 sequential records = 76; 36 coarse checks; 228 loop trials; summaries equal records; 76 frame hashes match; all saved spatial labels SAME. Numerical values were not recomputed. [checked] |
| E04 | Six saved resume-check files retain their reported hashes | Sandbox—artifact | Holds | Six of six match. Actual process-stop history and uninterrupted trajectory equivalence remain unverified. [checked] |
| E05 | A supplied test log reports 18 passes | Sandbox—artifact | Holds for log contents | `v053/provenance/frame_tests.txt`: 18 passed in 0.77s. No tests executed in this audit; correspondence to a particular source/environment is not independently established. [checked] |
| E06 | Current Python files parse | Sandbox—artifact | Holds for syntax | 25/25 current Python files parsed with `ast.parse`; no import, build or runtime check. [checked] |
| D01 | Current dependency versions exist as published packages | Fetched | Holds | NumPy 2.3.5, SciPy 1.17.0, pytest 9.1.1 fetched from their exact PyPI release pages; Python minimums 3.11, 3.11 and 3.10 respectively. Installation was not attempted. [fetched] |
| D02 | Current pins fall inside the affected ranges of the four sampled advisories | Fetched | Fails for those advisories | NumPy CVE-2021-41496 fixed in 1.19; SciPy CVE-2023-25399 fixed in 1.10.0; disputed SciPy CVE-2023-29824 fixed in 1.8.0; pytest CVE-2025-71176 fixed in 9.0.3. Pins exceed those fixes. This is not comprehensive CVE clearance. [fetched] |
| D03 | The frozen environment is a complete reproducible dependency lock | Sandbox—artifact | Fails | Current requirements pin three direct packages, with no resolved transitive lock/wheel hashes/BLAS build identity. Six historical requirement files leave pytest unpinned. [checked] |
| U01 | Saved ACCEPT labels establish physical truth or complete campaign coverage | Inventor + fresh execution/reference evidence needed | Unverified | Shared-harness agreement, finite samples and self-authored historical tests cannot settle physical validity. Existing limitations and open lower unlink collision remain. |

The complete file-by-file Layer 1 table is `full-inventory.md`; machine-readable observations, recursive markers, inferred subtree counts and all original ranks are retained in `layer1.json`. No low-ranked finding has been silently discarded.

## Layer 1 — actual scanner behavior and run

Both supplied archives were listed on disk before extraction. ZIP entries were checked for path escape and symbolic links before extraction; none were accepted with either condition. The audit archive contains 17 regular files, rather than the three claimed in the prompt; the project has 2,478 regular files. `genesis.py` was absent, so its optional checks were skipped, with the boot checklist inspected manually. The user's explicit objective supplied authorization to proceed; no charter amendment or new ratification was made.

**Method deviation:** the initial charter read fetched 240 lines, crossing its boot-only STOP marker. The boot block was encountered first, but the instruction to stop there was not followed exactly. Project review remained bounded; the project was never fully read into context.

Before execution, both `src/audit.py` and its imported `src/tool_quality_weighting.py` were read. The helper defines constants/functions on import, with its self-tests guarded by `__main__`; those self-tests were not run. Default scan mode walks paths, identifies stack markers by filename, reads supported code files and test files as text, performs regular-expression matching, computes scores and prints results. It neither imports nor executes project modules. It excludes `.git`, dependency/build/cache directories, and certain packaging paths; it does not recursively inspect arbitrary nested ZIPs or binary files.

The sole subprocess site is inside the opt-in test block. It selects a fixed runner command from marker filenames—`pytest` for this scan—splits it into an argument list, sets a working directory, captures output and imposes a 60-second timeout. Such a test command can still execute arbitrary project-author code. In a single-language archive like this, the scanner would run from the scan root; its per-subtree behavior is conditional on its polyglot monorepo heuristic. None of that path was enabled.

Explicit report flags write and can overwrite their given paths. This run used new output paths outside the scanned tree, and `-B -E -s` disabled bytecode writing and ignored Python environment/user-site customization. No network API or deletion call appears in the reviewed scanner/helper. This is a source-based assessment and observed successful default run, not an OS-level confinement or system-call audit. Symlink escape and unbounded file reads are general scanner limitations; symlinks were excluded during this extraction.

Command used, with `WORK` denoting the extracted working directory:

```bash
python -B -E -s "$WORK/audit-plugin/audit-main/src/audit.py" \
  "$WORK/project/twistronics_v053_reconciled" \
  --json "$WORK/results/layer1.json" \
  --sarif "$WORK/results/layer1.sarif"
```

No `--run-tests`, dependency installation, build command, project import, numerical sweep or project mutation was performed. All 2,495 extracted input files (17 plug-in + 2,478 project) remained byte-identical, with no new files added under either input tree.

### Ranking and scanner limitations

Score = 3 for no detected test relationship + 5 per secret match + 1 per TODO/FIXME/HACK/XXX + 1 if scanner LOC exceeds 200. Distribution: five files score 4, 522 score 3, 40 score 1, and 171 score 0. Ties retain filesystem traversal order, so tied ordinal position is not a calibrated risk distinction and can vary with extraction/filesystem order. The machine field named `riskRank` in emitted SARIF contains the score, not the ordinal review rank.

The 527 missing-test flags are the entire SARIF result set; the scanner does not detect F01–F05 directly. It does not parse dependency versions or query CVEs, notwithstanding broad language in its module description about dependency staleness signals. The dependency review below was performed separately.

Its “live secret” filter is narrower than the docs suggest: it scans only supported code extensions for Stripe-live-key-like strings, AWS access-key-like strings and private-key headers. A whole line is ignored if regex-context syntax such as a raw-string prefix is present, even if that line contains a concrete key-shaped value. No key-shaped hit in this run means no hit under those rules, not no credentials anywhere in the archive. This false-negative risk follows from code inspection; no secret detector benchmark was run.

Test relationships use global stems/import-line text, including substring name matching, across all historical/current subtrees. A historical test can therefore cause a current same-named module to receive credit without demonstrating execution of that version. Zero detected subprocess-driven tests only yields the scanner's `normal` confidence label; it does not establish coverage. The archive has 244 unique code hashes among 738 paths. Keep the original ranking for traceability and use current-version scope/duplicate information as review annotations.

## Layer 2 — exact cutoff and evidence

**Full deep-read cutoff: original ranks 1–14 of 738 files, totaling 1,765 scanner LOC.** Rank 5 was reviewed through the fully read rank-1 source and its complete diff. Additionally, a 23-line `BM.refine` excerpt in current rank 528 was inspected after AST equality established that it matches the reviewed historical method. That is one targeted follow-up, not a full read of the current 295-line engine. No other source file below rank 14 was deep-read; mechanical AST parsing of 25 current files and hashing across the archive are not deep review.

| Original rank | Risk score | File (shortened; full path in deep-read-selection.json) | Review result |
|---:|---:|---|---|
| 1 | 4 | `v044/provenance/baseline_v041_bm.py` | Stale metadata after periodic-wrap re-refinement; F01. |
| 2 | 4 | `v042/build_report.py` | Historical reconciliation and fixed narrative; upstream numerical truth unverified. |
| 3 | 4 | `our_v038/build_report.py` | Source hashes and accepted-record checks present; fixed narrative/test counts. |
| 4 | 4 | `our_v038/engines/numerical_gate.py` | Explicit numerical rejection checks present; not executed. |
| 5 | 4 | `v046/provenance/prior_bm_strain.py` | Same refinement-status issue as rank 1. |
| 6 | 3 | `v053/pair_measure.py` | Mesh/radius consistency and phase-only retry gates present. |
| 7 | 3 | `v053/replay_prep.py` | Resume identity, node jump/separation, orientation and endpoint-join calls present. |
| 8 | 3 | `v053/package_release.py` | Missing external prior ZIP/output directory; F03. |
| 9 | 3 | `v053/routes.py` | 1 + 8 + 10 primary states, consistent with declared plan. |
| 10 | 3 | `v053/frame_checks.py` | Refinement comparisons and restricted retry present. |
| 11 | 3 | `v053/build_report.py` | Hard-coded passing-test claim; F02. |
| 12 | 3 | `v053/spatial.py` | Sampled gap minima and transport checks present; not continuous certification. |
| 13 | 3 | `v053/engines/euler.py` | Optimizable-away guard and ungated returned diagnostics; F04–F05. |
| 14 | 3 | `v053/engines/braid.py` | Legacy raw winding/transport CLI; certification and replay impact unverified. |

**F01 evidence:** the helper records `success`, `status` and `message` from the first `minimize` call. If periodic wrapping triggers a second call, it updates `nfev` and replaces `res` with `res2`, but does not refresh the other metadata. Provided the later finite/value-consistency check passes, a failed second call can still carry the first call's successful status, and the converse can also misreport failure. This is a source-level control-flow defect, not a reproduced numerical failure. The same AST is in current `bm_strain.py`, lines 212–234. SciPy's exact-version reference defines the termination fields for each optimizer result. [SciPy 1.17.0](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.OptimizeResult.html) [fetched][checked]

**F02 evidence:** the report builder initializes `tests_this_batch=18` and emits fixed “18 tests pass” prose. It never reads `provenance/frame_tests.txt` or another test outcome. The existing log does contain 18 passes, but the publication code does not enforce a match to a source/test/environment identity, and its source-freeze map does not include tests or the builder. A stale pass claim can therefore survive report regeneration. No allegation is made that the historical test run failed or was fabricated. [checked]

**F03 evidence:** the packager first reads `BASE/sequence-outputs/twistronics_v052_reconciled.zip`, demands a specific SHA-256, then writes under that same missing directory. The current archive preserves the prior delivery as an extracted `prior_our_v052/` tree; that is not the required ZIP byte stream. Existence checks establish the missing input; the packager was not run. [checked]

**F04–F05 evidence:** `euler.real_frame` checks reality using `assert`, then passes `HR.real` to `eigh`. Python omits assertions under `-O`. The Euler routine computes/returns determinant and closure values without gating its printed winding on them, and the braid driver exposes fixed-grid raw windings. These are defects if these helpers are treated as certification entry points; active replay impact is not established. AST import inventory found `knobs -> braid -> euler`, which establishes an import relationship but not execution of these numerical functions. [Python reference](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement) [fetched][checked]

## Layer 3 — ground truth and remaining uncertainty

### Saved evidence checks

The independent read-only helper `verify_evidence.py` parses/hashes supplied artifacts without importing project code. Its output is `evidence-verification.json`. It reproduces the manifest/source/anchor/frame counts above, matches each case summary to its saved step records, and reads the supplied test log. The initial inspection additionally checked input preservation; `input-preservation.json` records byte-identical inputs. The helper is auditor-authored; its successful execution is **[self-tested]**, not external validation of the scientific model. SHA-256 agreement provides internal consistency only; the manifest and artifacts come from the same supplier.

The minimum recorded comparison-path external gap is 3.7384507309642245 meV. That is a value read from the supplied records and reconciled across them, not recomputed eigensolver output. NPZ contents were hashed as opaque bytes; frame overlaps were not recalculated. Saved statuses are evidence claims, not an independent judge.

### Dependencies and CVE sampling

Current requirements are exactly NumPy 2.3.5, SciPy 1.17.0 and pytest 9.1.1. All three release pages were fetched. NumPy/SciPy require Python >=3.11 and pytest >=3.10; the archive declares Python 3.12.14, but that runtime and a fresh installation were not reproduced. PyPI reports newer NumPy and SciPy releases; older frozen numerical pins are not themselves a defect. [NumPy release](https://pypi.org/project/numpy/2.3.5/), [SciPy release](https://pypi.org/project/scipy/1.17.0/), [pytest release](https://pypi.org/project/pytest/9.1.1/) [fetched]

| Package / pinned version | Sampled advisory | Ground-truth boundary | Applicability to current pin |
|---|---|---|---|
| NumPy 2.3.5 | CVE-2021-41496 | Affects <=1.18.5; patched 1.19 | Outside affected range. [GitHub-reviewed advisory](https://github.com/advisories/GHSA-f7c7-j99h-c22f) |
| SciPy 1.17.0 | CVE-2023-25399 / PYSEC-2023-102 | Fixed 1.10.0 | Outside affected range. [PyPA advisory](https://github.com/pypa/advisory-database/blob/main/vulns/scipy/PYSEC-2023-102.yaml) |
| SciPy 1.17.0 | CVE-2023-29824 / PYSEC-2023-114 | Fixed 1.8.0; vendor/discoverer dispute security impact | Outside affected range; preserve the dispute. [OSV record](https://osv.dev/vulnerability/PYSEC-2023-114), [upstream issue](https://github.com/scipy/scipy/issues/14713) |
| pytest 9.1.1 | CVE-2025-71176 | Fixed 9.0.3 | Outside affected range. [Upstream release notes](https://github.com/pytest-dev/pytest/releases/tag/9.0.3) |

These four advisories were sampled, not an exhaustive dependency scan. Search covered OSV package listings and then exact advisory/upstream references. Typosquatted packages such as `numpy-lib` were excluded because they are different distributions. No lockfile resolution, OSV version-query API sweep, transitive/native-library inventory, installed-wheel verification, matplotlib advisory review, or reachability analysis was completed. No “CVE-free” verdict is warranted. Six historical requirements use NumPy 2.4.4/SciPy 1.17.1 with unpinned pytest; one older requirement set includes matplotlib 3.10.8.

The principal sources were chosen for authority: Python and exact-version SciPy documentation define API behavior; package-owner PyPI pages establish published versions; upstream release notes and PyPA/GitHub advisory records establish specific fixes. Search snippets and irrelevant generic hits were not used as proof. The source ledger below records 13 retained sources: nine primary/reference pages and four OSV discovery or cross-check pages; this is a focused sample, not a quantified recall study of all search results.

### Limits and acceptance

- **Cutoff:** 14 full-file reviews, plus one 23-line matching-method excerpt. The remaining source received mechanical inspection only. No full-project semantic or threat-model audit.
- **Execution:** no project code, tests, numerical engines, build or packaging executed. Syntax parsing and artifact checks do not demonstrate runtime correctness. Historical passing logs are not fresh passes.
- **Physics:** no external measurement, independent reference implementation, continuous-interval proof or full scientific-literature reconciliation. Two engines can share conceptual or harness errors. The inventor's intended physical acceptance target was not independently supplied for this audit.
- **Security:** limited secret patterns, selected file extensions, sampled direct-dependency advisories, no transitive/native dependency clearance or exploitability assessment.
- **Scanner:** ties, duplicate snapshots, global import/name heuristics and exclusion rules can mis-rank files. Raising the deep-read cutoff—especially for the active measurement and acceptance pipeline—is the next useful review expansion.
- **SARIF:** 527 heuristic missing-test findings were generated and JSON-parsed. No OASIS schema validator or external SARIF consumer was run, so standards conformance/import success is unverified. SARIF contains scanner findings only, not the manually discovered F01–F05 findings.
- **Delivery:** under AUDIT.md's rubric, recipient consumption remains **[unconfirmed]**. To accept this audit artifact, open this report, locate F01 and its original/current file references, then open `full-inventory.md` and `layer1.json` from the evidence bundle and confirm the 738-file/527-flag totals are usable on your device. This checks the audit's usability, not scientific truth. No new charter ratification is implied.

For a read-only repeat of the artifact checks after extracting the original project archive:

```bash
python -B verify_evidence.py /absolute/path/to/twistronics_v053_reconciled
```

This prints evidence observations. An independent reviewer should inspect the helper and compare its output with the supplied manifest and records. Project test execution remains a separate future verification step on a trusted copy.

## Source ledger

Each source below was fetched/read, not accepted solely from a search snippet. These are short paraphrased uses; no long source quotations are reproduced.

1. [NumPy 2.3.5 on PyPI](https://pypi.org/project/numpy/2.3.5/) — release existence, Python minimum, newer-release notice.
2. [SciPy 1.17.0 on PyPI](https://pypi.org/project/scipy/1.17.0/) — release existence, Python minimum, newer-release notice.
3. [pytest 9.1.1 on PyPI](https://pypi.org/project/pytest/9.1.1/) — release existence and Python minimum.
4. [Python assert statement](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement) — optimized builds omit assertion code.
5. [SciPy 1.17.0 OptimizeResult](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.OptimizeResult.html) — meanings of final result/termination fields.
6. [pytest 9.0.3 release](https://github.com/pytest-dev/pytest/releases/tag/9.0.3) — CVE-2025-71176 fix.
7. [NumPy advisory GHSA-f7c7-j99h-c22f](https://github.com/advisories/GHSA-f7c7-j99h-c22f) — affected range and patched version.
8. [PyPA SciPy PYSEC-2023-102](https://github.com/pypa/advisory-database/blob/main/vulns/scipy/PYSEC-2023-102.yaml) — fixed-version record.
9. [SciPy upstream issue 14713](https://github.com/scipy/scipy/issues/14713) — issue context and 1.8.0 milestone.
10. [OSV NumPy listing](https://osv.dev/list?ecosystem=PyPI&q=numpy) — candidate-advisory discovery, excluding different package names.
11. [OSV SciPy listing](https://osv.dev/list?ecosystem=PyPI&q=scipy) — candidate-advisory discovery.
12. [OSV pytest advisory](https://osv.dev/vulnerability/GHSA-6w46-j5rx-g56g) — affected-version cross-check.
13. [OSV PYSEC-2023-114](https://osv.dev/vulnerability/PYSEC-2023-114) — explicit disputed-security qualifier and fixed range.

## Proposed session delta

Ratifications/amendments: none. Graded findings: F01–F05 and scoped evidence checks above. State: original archives and extracted inputs unchanged; read-only audit artifacts generated. Pending: correct final optimizer metadata, bind test publication to test evidence, resolve standalone packaging inputs, then broaden active-pipeline review if desired. UNCATEGORIZED: no project-specific state was written into GENESIS_TEMPLATE.md; report consumption remains unconfirmed.
