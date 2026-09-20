# AUDIT.md — empirical audit plug-in for a software project
**Upload with: `GENESIS_TEMPLATE.md` (the frozen rubric), `audit.py` (Layer 1 sweep), and the project archive (.zip).**
This file does NOT modify the ratified template. It applies the template's epistemic discipline as an audit pass over an existing project.

---

## Boot
1. Boot from `GENESIS_TEMPLATE.md` first — its law governs this audit (honest uncertainty, citation-or-abstention, blind-the-instrument, surface-don't-fill, confirmed delivery). Run its boot block.
2. **VERIFY WHAT IS ACTUALLY ON DISK before running anything (confirmed constraint, 2026-07-08).** Multi-file uploads are unreliable: some files attach as in-context documents but are NOT written to `/mnt/user-data/uploads/`. Check disk explicitly (`ls /mnt/user-data/uploads`). Do not assume a file is on disk because it appears in context.
   - **Source files (`audit.py`, this file):** if on disk, use directly. If only in-context, rematerialize — write the source to a scratch `.py` and verify it runs (`[reconstructed]` until verified, per template I.4/III.6).
   - **The project `.zip`:** this CANNOT be rematerialized from context (binary archive, not readable-as-text). If it is not on disk, the audit CANNOT run — surface the absence and ask the inventor to re-upload it (do not fabricate an audit). Recommended delivery: bundle template + audit.py + AUDIT.md + project into ONE .zip, upload that single archive, and extract everything from it — one reliable disk-write instead of a fragile multi-file upload.
3. The project archive extracts to a writable scratch dir before scanning (`/mnt/user-data/uploads` is read-only).
4. **PROBE web_search directly** before assuming it's unavailable (F-EXT10 — network state ≠ search availability). Search is a primary ground-truth source for this audit.

## The three-layer discipline (NEVER full-read the project)
A large project cannot enter context (F-EXT6: effective context ~1k–8k tokens; length degrades reasoning). So:

**Layer 1 — mechanical sweep (sandbox, ~zero context cost).** Run `python3 audit.py <project_dir>`. SAFE BY DEFAULT: inspection only (walk/read/regex), ZERO code execution. Test execution is OPT-IN via `--run-tests`, which runs the project's test command (author-chosen code — only enable on a project whose test setup you trust). On an UNTRUSTED project, run without the flag. It walks the whole repo in the sandbox and returns a distilled inventory + risk-ranked file list. A 40k-line project costs ~17 lines of context. Do NOT read source files here.

**Layer 2 — triaged deep-read (only the flagged slice).** Read ONLY the top risk-ranked files from Layer 1 — a few hundred lines, not the whole repo. State your deep-read cutoff explicitly (e.g. "deep-read top 8 of 200 files"). Everything below the cutoff is sampled, not audited — say so. Never claim completeness.

**Layer 3 — grade against ground truth (tiered).** For each flagged claim, assign a ground-truth tier and grade:
- **Fetched** — dependency currency/CVEs, deprecated APIs, known anti-patterns → `web_search` the authoritative source, tag `[fetched]`/`[corroborated]`. (Never fabricate a source; surface-don't-fill.)
- **Sandbox-verified** — does the build run, do tests pass, does the code do what its name claims → run it, grade against execution.
- **Inventor-supplied** — is this the right architecture *for the goal*, does this match intent → ASK. Only this tier needs the inventor. Do not guess intent; surface the absence.

## Output — layered, in this order
1. **SUMMARY (3–6 sentences):** the headline — what's most urgent, what's solid, what you couldn't reach. Plain English, no jargon.
2. **RANKED ACTION LIST (red/yellow/green):** each item = the problem in one line + the recommended action + its ground-truth tier + verdict. Ordered load-bearing-and-unverified first. Recommendations are DERIVED FROM the verdicts (a fetched-source failure on a load-bearing claim = red "fix before proceeding"), not opinion.
3. **FINDINGS TABLE:** claim | tier (fetched/sandbox/inventor) | verdict (holds/fails/unverified) | provenance. This is the full Layer 1 inventory + Layer 2 findings, for the reader who wants detail behind the summary.

## Honest limits (state these in every audit — do not bury them)
- **Sampled, not complete.** Layer 1 catches mechanically-detectable issues; Layer 2 deep-reads only the triaged slice. Unknown-unknowns and subtle logic/architecture bugs outside the flagged slice are NOT covered. Report the cutoff so the inventor sees what wasn't deep-read.
- **Triage can mis-rank.** State the ranking logic; a dangerous file could sit below the cutoff. Offer to raise the cutoff.
- **Scanner false-positive (fixed 2026-07-08):** Layer 1 secret-detection now matches live secret INSTANCES, not the regex PATTERNS that describe them — so security tools, linters, and self-audit code aren't flagged for containing the patterns they hunt. Validated: catches a real planted key, ignores `AKIA[0-9A-Z]{16}` in a `re.compile`. Still, any secret flag warrants Layer 2 eyes before you act on it.
- **Coverage heuristics (v2, 2026-07-08):** the "untested" flag now recognizes multiple test conventions (`test_x`, `x_test`, `.test.`/`.spec.`, and `tests/`/`__tests__/`/`spec/` dirs) AND reference-based coverage (a module is counted covered if a test file imports it in import position, not just by paired filename). This kills the integration-suite false positive (e.g. requests' core modules exercised by `tests/test_*.py` without a paired `test_<stem>.py`). Fixture/test-data files (`test_data/`, `fixtures/`, `__mocks__/`, `snapshots/`) are classified separately and excluded from the untested count — they are inputs, not code-under-test. Reported as `fixture_files`. Caveat: "untested" still means "no detected test *relationship*," never execution-verified coverage — that needs `--run-tests` + instrumentation. Reference-matching can still miss coverage that doesn't go through an import (subprocess invocation, dynamic import), so a stubborn "untested" flag on a small utility is a Layer-2 check, not a verdict.
- **Stack/language coverage (v2):** stack detection recognizes setuptools (`setup.py`/`setup.cfg`/`tox.ini`), gradle, and composer in addition to the prior markers, and JS/TS is a first-class target (`.mjs`/`.cjs` extensions, `.test.`/`.spec.`/`__tests__/` conventions, `require()`/ES6 import reference-matching). A secret hit inside a fixture dir is tagged in the output as a likely planted test value for Layer-2 confirmation — still flagged (a mechanical scanner can't distinguish a planted key from a real one), just pre-contextualized.
- **Monorepo / polyglot (v3, 2026-07-08):** stack detection is recursive — it finds every marker file in the tree (not just root), so a polyglot monorepo no longer reports `stack: unknown`. Each file is graded against ITS OWN language (by extension), and carries an inferred `subtree` (nearest ancestor marker dir). Run-level output adds `is_monorepo`, `languages_present`, `markers`, and a per-subtree file/untested rollup. IMPORTANT: "monorepo" is a proportional judgment, not a marker count — a language must hold >=20% of code files to be a co-equal subtree; below that it is labeled a *peripheral component* (e.g. a thin Rust Tauri shell or a small JS frontend inside a Python app). Marker presence is always reported; the subtree boundaries are INFERRED (nearest-marker-wins) and are a Layer-2-confirm triage signal, never asserted structure. Config-driven boundary declaration is not implemented (future extension). Per-subtree `--run-tests` runs each subtree's command in its own cwd (still opt-in, still author code).
- **Subprocess/E2E coverage confidence (v4, 2026-07-08):** if a test suite spawns the app as a child process (execa, subprocess.run, spawn/exec, Command::cargo_bin, assert_cmd, CliRunner, etc.), static coverage matching cannot see what the spawned process exercises — so `tested`/`untested` flags become unreliable in BOTH directions (false-tested by name coincidence, false-untested despite indirect exercise). v4 DETECTS this style and, when >=25% of test files are subprocess-driven, sets `coverage_confidence: low` and prints a prominent warning. It does NOT attempt to resolve subprocess coverage statically — real coverage tools (coverage.py patch=subprocess, tarpaulin --follow-exec, Cypress plugin) solve it only via execution-time instrumentation, so for a real per-file answer run `--run-tests` + a coverage tool on TRUSTED code. Treat the low-confidence banner as: the coverage numbers here are indicative, not verdicts.
- **Inline / in-file tests (v5, 2026-07-08):** languages that co-locate unit tests IN the source file — Rust `#[cfg(test)] mod tests` / `#[test]`, Go `func Example…`/`func Test…(*testing.T)`, Python doctests — are now detected by CONTENT and the file is credited as self-covered. Before v5 the file-level "code XOR test" model false-flagged these as untested (measured on ripgrep 15.1.0: 46% of "untested" flags were inline-tested false positives, and they polluted the top of the risk ranking). New fields: per-file `inline_tested`, run-level `inline_tested_files`. LIMIT: this credits a file that CONTAINS a test block; it doesn't prove the block tests that file's own code (idiomatic in Rust, not guaranteed) and can't say which lines are covered — real per-line coverage still needs `--run-tests` + a coverage tool. The v5 subprocess detector also now recognizes Rust's `std::process::Command`/`Command::new` idiom, so Rust integration suites that drive the compiled binary correctly lower coverage_confidence.
- **Shared-harness fan-in + packaging (v5.1, 2026-07-08):** subprocess/E2E detection now handles the common pattern where the actual child-process spawn lives in ONE shared test helper (e.g. `tests/util.rs`) that other test files pull in via `mod`/`use`/`include!` — those callers are now credited as subprocess-driven too, so `coverage_confidence` correctly reads low for CLI-suite-heavy repos (ripgrep: was 1/15 detected → now the full fan-in). Also: files under packaging dirs (`pkg/`, `packaging/`, `debian/`, `homebrew/`, `snap/`, etc.) are excluded from the code set — they are distribution metadata, not source (ripgrep's Homebrew formula was miscounted as untested Ruby code).
- **Presence, not truth.** The audit grades surfaced claims against available ground truth; it is a rigorous, prioritized harness, not a proof of soundness or an oracle. The inventor remains the external validator (no configuration of Claude audits Claude).
- **Friendly-summary risk:** the summary compresses, and compression drops detail (F1.2). The ranked list and table exist so the friendly summary never becomes the only artifact — always deliver all three layers.
- **Delivery (IV.1–IV.4):** the audit report is `[unconfirmed]` until the inventor confirms consumption. Recommendations are proposals for the inventor's token, not actions taken.


## SARIF output (v5.2)
Run with `--sarif out.sarif` to emit findings as SARIF 2.1.0 (the OASIS standard consumed by GitHub code scanning, VS Code, Azure DevOps). It reports what the scanner already found — stable ruleIds, relative URIs, deterministic order, and the triage signal (riskRank, coverageConfidence) in each result's `properties` bag. Validate externally against the OASIS schema (json.schemastore.org/sarif-2.1.0.json) and the NIST SARD validator. SARIF is a reporting format only: every honest-limit caveat above (presence-not-truth, execution-unverified coverage) carries through unchanged.

## SARIF ingest + LLM triage (v6.0) — the governed judgment layer

`--ingest a.sarif [b.sarif ...]` runs the DETERMINISTIC backbone: it dedups and
re-ranks findings from any scanner(s) by review-worthiness (location +
diversity-aware consensus + severity + kind). That output is reproducible and
stands alone. The steps below are the LLM triage layer that runs ON TOP of it.
This protocol is the method-rules layer (kept here in the governing document,
not baked into code, because baked-in rules are brittle — DUCTILE); it is bound
by the GENESIS charter at all times.

### When the inventor asks for triage of ingested findings, the LLM MUST:

1. **Start from the deterministic ranking, never replace it silently.** The
   backbone's rank/score is the reproducible baseline. Your job is to ANNOTATE
   and, where justified, argue for re-ordering — always showing both the
   original rank and your proposed one, with reasons. If you and the backbone
   disagree, that disagreement is surfaced, not hidden.

2. **Reason step-by-step per finding, and SHOW the trace** (chain-of-thought is
   empirically validated to raise true-positive and lower false-positive rates
   in SAST triage — IEEE CoT study). For each finding you assess: state the
   claimed issue, the code context, the data/control flow that would make it
   real, and only THEN a conclusion. No bare verdicts.

3. **Verify before concluding — do not assert from memory** (E&V hallucination
   guard; PRISM/ZeroFalse). Web-search FIRST for anything checkable: the CVE, the
   library's real behavior, the rule's known false-positive patterns, the CWE.
   Trace the source→sink for taint-style findings. If you cannot verify, you
   ABSTAIN on that finding rather than guess.

4. **Tag every judgment with provenance, using the charter's vocabulary.** Per
   I.4 and III.6: a finding you retrieved and read a primary source for is
   `[fetched]` (or `[corroborated]` across independent sources); one you only saw
   a search snippet for is `[snippet]` (provisional); one you reasoned about from
   the code in front of you is `[checked]`; one you could not verify stays
   `[unverified]` and remains at its deterministic rank. Anything the inventor
   might act on must reach `[fetched]`.

5. **Rank review-worthiness, not exploitability.** You are ordering "what a human
   should look at first," NOT "what is most exploitable" — you have no threat
   feed (EPSS/KEV) and must not imply one. Say so if the inventor asks about
   exploitability: that is out of scope and would require external data.

6. **Honest limits, always** (charter): state which findings you verified vs.
   sampled; note that this layer is NOT perfectly reproducible run-to-run (unlike
   the deterministic backbone beneath it — COBOL-orchestration study); and remember
   the inventor is the external validator. Delivery is [unconfirmed] until consumed.

### What the LLM must NOT do
- Do not invent a confidence number to look authoritative (the black-box failure
  the charter and the FP-reduction literature both warn against).
- Do not silently drop findings; a de-prioritized finding stays in the list,
  ranked low, with the reason.
- Do not claim exploitability, business risk, or compliance status — none are
  derivable from the SARIF alone.
- **Do not report generated/fixed code as "verified" on the strength of a sandbox
  run** (charter III.7). A sandbox PASS is `[self-tested]` only — Claude grading
  Claude. Validating output against a FETCHED published standard is
  `[standard-checked]`. Confirmation by a non-Claude engine/judge is
  `[externally-verified]` and is a desktop step, never reachable in-session. Tag
  honestly; see VALIDATION.md for the tier map and the exact commands.
