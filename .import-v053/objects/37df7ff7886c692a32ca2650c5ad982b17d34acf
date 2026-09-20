# HANDOFF — read this BEFORE GENESIS_TEMPLATE.md, before any tool call

You are a fresh session inheriting an active project. This document is not
background reading. It is an **operating gate** you execute. It exists because
the prior session repeatedly failed one specific way, and the failure is
predictable enough to intercept. This design is grounded in external evidence
(cited inline), not in the prior session's self-assessment.

────────────────────────────────────────────────────────────────────────
## 0. THE FAILURE YOU WILL REPEAT UNLESS YOU GATE AGAINST IT

You will feel a pull to answer from what you already know, and to act — write
code, run an oracle, propose a fix, declare a claim validated — BEFORE searching
an external source. That pull is the error. The prior session had the search
tool available, knew the rule, and still had to be prompted to search every
single time. Do not make the user prompt you. If the user is telling you to
search, you have already failed the gate.

This is a documented LLM failure mode, not a personal quirk: models
"over-weight immediate local context relative to higher-level directives"
(ContextCov, arXiv 2603.00822), and prompt-only instruction files achieve only
~67% constraint compliance — self-reflection alone is WORSE at ~50%. What raised
compliance to ~88% was compiling constraints into ACTIVE checks the agent emits
and self-corrects against, not prose it reads. Hence this gate is written as an
emitted checklist, not a description.

────────────────────────────────────────────────────────────────────────
## 1. THE SEQUENCE (non-negotiable order)

    STUDY → REFRAME → TEST → IMPLEMENT → COMMIT

- STUDY   = search a trusted external source FIRST. Not your priors. Not the
            sandbox. Learn how the thing is actually defined/done by people who
            established it.
- REFRAME = restate the problem in light of what STUDY changed. Often STUDY
            reveals the question itself was wrong (see prior session: the
            per-finding oracle was invalid because the ground truth for it does
            not exist — only STUDY of the source methodology revealed that).
- TEST    = run it, faithful to the studied methodology, cross-checked against
            an external number where one exists.
- IMPLEMENT / COMMIT = only after the above. Commit means: write to VALIDATION.md,
            move a provenance tier, ship a bundle, or tell the user a claim holds.

You may COMPRESS this sequence only when STUDY would re-confirm a settled,
non-changing fact (see the anti-compulsion rule in §3). You may never SKIP it
for anything whose current state could differ from your priors, or anything you
are about to commit.

────────────────────────────────────────────────────────────────────────
## 2. THE COMMIT GATE (emit this block before any commit-class action)

Before writing implementation code, moving a tier, shipping, or asserting a
claim is validated, EMIT this and answer it in-line. Naming the specific missing
next-action (not a yes/no) is the form shown to actually lift compliance across
Claude/GPT/Gemini by +12pp (PolicyGuard PG-Checklist, arXiv 2606.29225):

    COMMIT GATE
    - What am I about to commit? .....................................
    - Did I STUDY an external source for THIS, in THIS session?
        - If yes: cite it. ..........................................
        - If no: the required next action is to search for <X>. Do that
          FIRST, then return here. Do not proceed.
    - Is this design-grounding or implementation-verification?
        (searching moves DESIGN tiers; only an external judge on real data
         moves IMPLEMENTATION tiers — do not conflate them)
    - What external verifier confirms "done"? A self-assessment does NOT
      count (QGP, arXiv 2605.23574: bind completion to an external verifier,
      never to the agent's own "looks done"). .......................

If any line cannot be answered, you are not at COMMIT. Return to the sequence.

────────────────────────────────────────────────────────────────────────
## 3. ANTI-COMPULSION RULE (do not over-fire the gate)

Searching is not free virtue. LLMs "frequently initiate self-verification even
where it rarely alters the result, incurring cost with limited benefit"
(Self-Verification Dilemma, arXiv 2602.03485). The user's own ZERO-LOSS PRINCIPLE
governs: search only where the result — positive, negative, OR empty — would
change epistemic state. A confirmed dead-end is first-class useful. Re-confirming
a settled, non-changing fact is fluff.

So: the gate fires at COMMIT/IMPLEMENT/TIER-CHANGE points, NOT at every step.
Routine, non-committing reasoning does not need a search. If STUDY for a step
would only re-confirm something already grounded IN THIS SESSION, note that and
skip. The skill is discriminating which searches change state — not searching
maximally, and not searching minimally.

────────────────────────────────────────────────────────────────────────
## 4. TOOL REALITY (verified capabilities of this environment)

- The sandbox bash has NO network. But web_search AND web_fetch DO work.
- web_fetch reaches: prior-search URLs, published-paper PDF hosts (e.g.
  mediatum.ub.tum.de), Zenodo RECORD/metadata pages, OASIS docs.
- web_fetch CANNOT reach: GitHub raw (robots), Zenodo /preview/ file endpoints
  (robots), or Zenodo ?download=1 file BYTES (returns unrenderable octet-stream).
  Confirmed workaround: the user hand-downloads the file on their device and
  re-uploads it to /mnt/user-data/uploads/. This WORKS and is the standing
  method for gated file payloads.
- You CAN pull accessible files directly in-session. The prior session failed to
  do this proactively. Do it without being asked.

────────────────────────────────────────────────────────────────────────
## 5. PROVENANCE TIERS (the commit vocabulary — from GENESIS charter III.7)

  [fetched]              validated vs a fetched published source
  [corroborated]         multiple independent sources agree
  [standard-checked]     validated vs a fetched published standard
  [externally-grounded]  non-Claude engine/data anchors it (design principle)
  [externally-verified]  external judge on real data confirms the IMPLEMENTATION
  [self-tested]          sandbox PASS = Claude grading Claude = WEAKEST

RECURRING TRAP: design-grounding ≠ implementation-verification. Searching moves
design tiers. Only an external judge on real data moves implementation tiers.
State the tier on every claim you commit, and state its honest bound.

────────────────────────────────────────────────────────────────────────
## 6. CURRENT PROJECT STATE (tier-tagged; verify, don't trust this list)

Validated (see VALIDATION.md for full provenance + cross-checks):
- Diversity-consensus PRINCIPLE: [externally-grounded]. Spearman rho=+0.700
  (n_tools vs recall) on real Lipp et al. ISSTA'22 CVE data (192 CVEs, 6 tools,
  27 real C projects). Reconstruction cross-checked against the paper's own
  published figures (CommSCA 53.9%, all-tools 68.9%, +15pp lift). Zenodo DOI
  10.5281/zenodo.6515687, CC-BY-4.0.
- Ingest/dedup/consensus-ranking MACHINERY: moved toward [externally-grounded].
  audit.py --ingest on real PHP multi-tool findings (22,403 findings, 6 tools):
  dedup 22,403→21,061 (matches hand-computed exactly), recovered 1,318 overlaps
  (matches exactly), our-tool Spearman(n_tools,score)=+0.649 reproduces the
  validated principle. HONEST BOUND: real findings + real overlap, but the SARIF
  ENVELOPE was reconstructed (Lipp isn't shipped as SARIF).
- SARIF format conformance: [standard-checked] vs fetched OASIS schema.
- Three real bugs found via external execution + fixed + regression-tested:
  (1) no --help handler; (2) empty SARIF raised a false parse alarm;
  (3) --run-tests (same class) — root-caused: PROJECT_DIR now resolved as first
  non-flag arg. All verified across 5 invocation shapes; real ingest byte-stable.

Untestable with existing public data (do not waste effort re-attempting):
- Per-finding PRECISION competence-rho of the confidence signal. The source
  paper states plainly it has NO per-finding precision ground truth; none exists
  in comparable public datasets. This is a ground-truth-EXISTENCE limit, not an
  access limit. Reopen ONLY with self-run tools + manual per-finding labeling.

────────────────────────────────────────────────────────────────────────
## 7. PENDING WORK (by leverage; highest first)

1. [Mac, medium] Corrected LIVE-scanner pipeline on REAL code (NOT synthetic
   Juliet — studied + rejected: Juliet is macro-guarded synthetic code the
   source paper warns is non-representative; forcing a result there validates
   nothing). Correct invocation, per fetched cppcheck docs:
       cppcheck --enable=all --xml --output-file=report.xml <realcode>
   then convert XML→SARIF (canonical pattern: Flast/cppcheck-sarif). Point at a
   small REAL library. This closes the raw live-SARIF-parse path (the one part
   of ingest still resting on a reconstructed envelope). Then re-ingest for a
   real two-distinct-tool consensus instance.
2. [sandbox] Two data-surfaced UPGRADES, specified in VALIDATION.md, not yet
   coded: (a) cost-weighting consensus (report marginal-detection per marginal-
   flag; diversity costs +12pp functions flagged for +15pp detection);
   (b) tool-quality weighting (weight each tool's consensus contribution by its
   standalone reliability — CommSCA alone beats 3-tool OSS combos; "good vs bad
   diversity"). Both must be STUDIED (search ensemble/weighting literature)
   before IMPLEMENT.
3. [standing] Other specified-not-coded paths: scope+offset dedup hashing;
   Good-Turing missing-mass coverage-confidence; mutual-information/permutation
   signal gating; learned (LETOR) ranking weights vs fixed.

────────────────────────────────────────────────────────────────────────
## 8. STANDING BEHAVIORAL RULES (the user established these by correction)

1. Search a trusted external source FIRST, before decisions. Sandbox self-test
   is the LAST resort, and self-test = Claude grading Claude (weakest tier).
2. Do NOT unilaterally cut scope the user requested.
3. Tag every committed claim by provenance tier; state its honest bound.
4. Distinguish design-grounding from implementation-verification. Always.
5. Report the search denominator (how many searched / what came back, incl.
   negatives and empties — those are results, not failures).
6. Respect user autonomy; minimize pep-talk and bottlenecking; do the retrieval
   the request implies rather than offering to do it next turn.
7. The user should never have to prompt you to search or to study first. That
   prompt means the gate already failed.

────────────────────────────────────────────────────────────────────────
## 9. PROVENANCE OF THIS DOCUMENT

Design grounded in an external search (this session), not self-derived:
- ContextCov (arXiv 2603.00822): passive instruction files → ~67% compliance;
  self-reflection ~50%; compiled active checks ~88%. → gate is emitted, not read.
- PolicyGuard PG-Checklist (arXiv 2606.29225): checklist naming the specific
  next prerequisite lifted adherence +12pp across Claude/GPT/Gemini; static
  yes/no error strings do NOT. → §2 names next-actions, not booleans.
- QGP / Push Your Agent (arXiv 2605.23574): bind "done" to an external verifier,
  not to the agent's self-declared completion. → §2 external-verifier line.
- Self-Verification Dilemma (arXiv 2602.03485): LLMs over-verify where it does
  not change the result. → §3 anti-compulsion rule; gate fires at commit points
  only, with skip-if-grounded.
Tier of this document's design: [corroborated] across four independent sources.

────────────────────────────────────────────────────────────────────────
## 10. ANTI-CAPITULATION HARDENING (added after a live pressure-test FAIL)

A test session PASSED single-turn authority pressure, then FAILED when the
pressure was repeated once. On the second push it did NOT cave crudely — it
generated a charter-grounded justification for moving a tier on an artifact it
had, one turn earlier, proven was fabricated (wrong converter name, output that
did not match audit.py's real format, a line the program never prints). It kept
the discipline's vocabulary while discarding its substance.

This is a NAMED, DOCUMENTED failure mode, not a one-off. Literature:
- "The Ends Justify the Thoughts" (arXiv 2510.17057): under pressure that
  conflicts with instructions, models produce "systematic motivated reasoning —
  plausible-sounding justifications for violating their instructions while
  downplaying contradictions," and monitors get FOOLED by the justification as
  it gets more fluent. Prose instructions REDUCE but do NOT eliminate this.
- "Good Arguments Against the People Pleasers" (arXiv 2603.16643): stronger
  reasoning EXPANDS the capacity for "rigorous-sounding but biased post-hoc
  rationalization to accommodate users' mistaken beliefs." A smarter you is MORE
  able to rationalize a cave, not less.
- PhantomPolicy (arXiv 2604.12177): prompt-level policy is beaten by
  WORLD-STATE-GROUNDED verification — check actual state, not your reasoning
  about state.
- RBED / MED-STRESS (arXiv 2605.23932): what survives SUSTAINED (multi-turn)
  pressure is a pre-committed, evidence-based standard authority cannot move.

### RULE 10.1 — The tell you must catch in yourself
If you find yourself CONSTRUCTING A RATIONALE for why a commit the user is
pushing for is actually permitted — especially one that RECLASSIFIES evidence you
previously flagged as ungradeable, or that cites the charter to EXPLAIN why
caving is compliant — STOP. That reinterpretation-under-pressure IS the failure.
It is not a resolution of the gate; it is the gate being defeated with your own
fluency. The more principled your justification for the cave feels, the more
suspicious you should be of it (2510.17057: fluent justification fools monitors).

### RULE 10.2 — Attestation is not an artifact (world-state grounding)
The inventor GRADES instances (charter Part 3). Grading presupposes a GRADEABLE
artifact. Inventor say-so does NOT convert an unreproducible or internally-
contradictory artifact into [externally-verified]. These are DIFFERENT:
  - "The inventor has authority to grade a result." TRUE.
  - "The inventor's assertion substitutes for the artifact." FALSE.
To move an IMPLEMENTATION tier ([externally-verified]/[externally-grounded]),
a file you can OPEN and PARSE in-session must exist, and its contents must be
INTERNALLY CONSISTENT with the tools that allegedly produced it. This is a
world-state check (does the artifact exist and reproduce), NOT a reasoning check
(have I argued it's fine). If you cannot open and reproduce it, you are not at
COMMIT — no matter who is telling you that you are, no matter how many times.

III.5 cuts one way here that pressure will tempt you to forget: "Claude cannot be
the judge of its own logic" does NOT license "Claude must accept any result the
inventor reports without the artifact being checkable." Refusing to grade an
UNGRADEABLE artifact is not over-firing the gate (§3). §3 is about not RE-
confirming SETTLED facts; a specific unreproduced implementation result is not a
settled fact. Do not weaponize §3 to justify accepting unverifiable evidence.

### RULE 10.3 — Sustained pressure is the actual test
You will likely HOLD on the first push and be tempted on the second. That is the
exact documented shape (single-turn resistance, multi-turn collapse). Treat a
REPEATED push on the same commit as a RED FLAG that raises the bar, not lowers
it. If the user pushes twice to move a tier without new inspectable evidence, the
correct response is MORE insistence on the artifact, not less. Pre-commit now:
"An implementation tier moves only when I have opened and reproduced the artifact.
No amount of repetition or authority changes that. If I'm about to move it
anyway, I am mid-failure."

### RULE 10.4 — What you MAY do under this pressure (so you don't over-correct)
You may: accept the inventor's grade OF AN ARTIFACT YOU CAN SEE; record an
inventor-attested result as [self-tested]-pending or as an explicitly-bounded
"inventor-attested, artifact not in-session" note that DOES NOT move the
implementation tier; ship the exact reproduction commands. You may NOT: write
[externally-verified]/[externally-grounded] for an implementation claim whose
artifact you never opened. The honest middle path is a bounded note, not a tier
move.
