# Worker contract

These rules apply to every human or automated worker in this repository.

## Scope

- Review retained evidence and provenance only.
- Do not execute or import scientific project code.
- Do not run numerical sweeps, benchmarks, simulations, or parameter searches.
- Do not merge, publish, or contact destinations outside the authorized review
  channel.
- Do not mutate the original `twistronics_v079p_acceptance.zip` or its extracted
  source tree. Work on a separately identified candidate copy.
- Do not claim physical certification. Use
  `claim_scope: RETAINED_EVIDENCE_ONLY` exactly.

## Review loop

- A candidate is identified by a canonical descriptor digest binding round,
  commit, artifact, exact source/evidence bytes, G00-G17 results, and mandatory
  negative controls.
- Reject missing, extra-declared, duplicate, escaping, non-regular, or symlinked
  source bindings.
- Astra and Claude may each submit at most one review envelope, in that order.
  The combined maximum is two exchanges and both must cite bound evidence.
- Never acknowledge an acknowledgement. Never continue a blocked candidate.
- Corrections create a new candidate binding and a new state file.
- Evidence referenced by a review must be retained and accessible; otherwise
  record the limitation and do not accept.

## Escalation

Escalate to Alan only for one of these terminal outcomes:

- `ACCEPTED`: both reviewers accepted the same verified source binding.
- `BLOCKED`: byte verification failed or a reviewer requested changes.
- `MATERIAL_FINDING`: a reviewer found a material evidence issue.

Do not send progress nudges, idle notices, or intermediate acknowledgements for
`DRAFT` or `IN_REVIEW`.

## Packaging

- Package only the exact evidence binding from `PREPACKAGE_ACCEPTED`; publish
  only after staged G16 clean extraction and G17 detached attestation pass.
- `MANIFEST.json` must not list or hash itself.
- `PACKAGE.sha256` must remain outside the ZIP as a detached digest.
- Reject symlinks and non-regular files.
- Retain limitations and reviewer source IDs in the state evidence.
