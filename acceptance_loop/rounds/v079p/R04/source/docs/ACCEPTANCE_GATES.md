# Fail-closed acceptance gates

The candidate archive cannot certify itself. Candidate-supplied verifiers and
logs are evidence inputs; the reviewer-controlled harness decides acceptance.

Only `PASS` advances. `FAIL`, `ERROR`, `SKIPPED`, `MISSING`, and `NOT_RUN` all
block publication.

Every G00-G17 result and every mandatory negative control must cite a retained
evidence path and SHA-256 from the candidate's exact evidence binding. The
complete ledgers are part of the canonical descriptor reviewed by both agents.

| Gate | Requirement |
|---|---|
| G00 | Candidate identity was approved before evidence generation. |
| G01 | ZIP has no traversal, absolute paths, collisions, links, encryption, or unsafe expansion. |
| G02 | Extracted regular-file inventory exactly matches the payload manifest plus the manifest itself. |
| G03 | Manifest hashes actual bytes, uses canonical paths, and excludes itself. |
| G04 | After two matching reviews, the staged finished ZIP matches a detached SHA-256 distributed outside the ZIP. It remains `NOT_RUN` before packaging. |
| G05 | The trusted source set is explicit and exact. Missing, extra, linked, or renamed inputs fail. |
| G06 | The harness hashes actual source bytes rather than comparing declarations. |
| G07 | Source-root digest is unchanged before and after all checks. |
| G08 | Expectations, plan, policy, basis, dependencies, and environment are bound to the approved source root. |
| G09 | Each execution receipt binds hashes, argv, cwd, runtime, timestamps, exit code, and outputs. |
| G10 | The evidence payload has exact non-self-referential manifest coverage. Detached gate ledgers and receipts are separately bound by the canonical descriptor. |
| G11 | Reviewer-owned record verification exits zero against extracted bytes. |
| G12 | The actual claim-bearing deliverable, including README, has zero lint violations. |
| G13 | Collected test IDs exactly match the approved inventory. |
| G14 | Test execution exits zero with no unapproved skips, xfails, or unknown results. |
| G15 | Structured receipts, raw logs, counts, and summaries agree. |
| G16 | A second clean extraction reproduces inventory and non-numerical checks. |
| G17 | A detached reviewer attestation records every gate and reports overall PASS only when all pass. |

Mandatory negative controls include: actual-source byte flip, missing source
identity, added source, changed expectations, source mutation during build,
missing/extra/tampered evidence, manifest self-reference, unsafe ZIP names or
links, altered finished ZIP, README claim drift, missing or failing test,
unapproved skip, log-count tampering, malformed checker arguments, and broken
harness configuration.

The immutable order is:

`approve source -> freeze inputs/environment -> generate evidence -> independent checks -> post-hash source -> package -> detached ZIP digest -> clean-extraction verification -> detached attestation`

Prepackage review requires G00-G03 and G05-G15 to pass. G04, G16, and G17
must remain `NOT_RUN` until the two-review `PREPACKAGE_ACCEPTED` transition;
they pass only inside the atomic staged-packaging transaction.

Any upstream byte change invalidates every downstream artifact and starts a
new round. These gates do not require or authorize a numerical or scientific
rerun.
