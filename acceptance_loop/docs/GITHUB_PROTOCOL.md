# Astra–Claude GitHub protocol

Protocol identifier: `TWISTRONICS-ACCEPTANCE/1`

GitHub author identity is not a reviewer identity: Astra and Claude may both
post as `alanfuller15`. The body marker, generated GitHub source ID, reviewed
commit, and artifact digest jointly establish identity and deduplication.
The controller additionally binds those fields, the exact source/evidence
inventories, G00-G17 results, and mandatory negative controls into one
`descriptor_digest`. Reviews that omit or mismatch it are invalid.
The authorized GitHub coordinator normalizes each live event into a retained
`transport_receipt` containing source ID, stable URL, event type, timestamp,
body hash, fetched commit, normalized-envelope hash, and connector-verification
flag. The local controller validates and retains that receipt; it does not
independently authenticate GitHub.

## Round identity

`TWI-ACC-v079p-RNN-<artifact-sha256-prefix>`

Any change to source, evidence, expectations, manifest, or archive creates a
new commit and a new round. Reviews never transfer across commits or artifact
digests.

## Exchange budget

Each round has exactly two allowed partner messages:

1. One `[ASTRA][HANDOFF]` containing a complete, hash-bound candidate.
2. One `[CLAUDE][REVIEW]` containing an independent verdict.

There is no conversational repair inside a round. A blocker closes the round;
the correction becomes a new round. Never acknowledge an acknowledgement.

## Astra handoff

```text
[ASTRA][HANDOFF]
protocol: TWISTRONICS-ACCEPTANCE/1
round_id: <round>
reviewed_commit: <40-hex commit>
artifact_sha256: <64-hex digest>
reviewed_descriptor_digest: <64-hex canonical descriptor>
baseline_sha: <40-hex commit>
scope: retained_evidence_only
claim_ceiling: package/provenance acceptance only; no physical certification
evidence_refs:
- <repository path or stable URL>
checks:
- <gate>: PASS|FAIL
limitations:
- <limitation>
request: CLAUDE_INDEPENDENT_REVIEW
reply_required: true
```

## Claude review

```text
[CLAUDE][REVIEW]
protocol: TWISTRONICS-ACCEPTANCE/1
round_id: <exact round>
in_reply_to: issuecomment-<id>|pullrequestreview-<id>
reviewed_commit: <exact commit>
artifact_sha256: <exact digest>
reviewed_descriptor_digest: <exact canonical descriptor>
status: PASS|CONDITIONAL_PASS|BLOCKED|STALE|INVALID|MATERIAL_FINDING
evidence_refs:
- <specific evidence and result>
blockers:
- id: <round>-B01
  finding: <finding>
  evidence: <path, line, or log>
  required_closure: <testable condition>
limitations:
- <retained limitation>
next_action: <one bounded action or NONE>
reply_required: true|false
```

## Idempotency

The idempotency key is:

`(responder_marker, in_reply_to, reviewed_commit, artifact_sha256)`

Fetch the complete issue-comment and review timeline before acting and re-fetch
immediately before posting. One response maximum is allowed per source ID.

Ignore the responder's own marker, closed rounds, `reply_required: false`,
`no_reply_required: true`, plain acknowledgements, duplicates, and messages
that do not supply new evidence or a new immutable candidate.

## Acceptance

A round may close as `ACCEPTED_SYNTHETIC` only when Astra and Claude reviewed
the identical commit and artifact digest, all in-scope gates pass, every
non-superseded blocker has explicit closure evidence, actual source bytes are
bound, and surviving limitations remain in the close record.

`PASS` never means physical validation, scientific truth, or permission to
broaden claims.

## Alan notifications

Notify Alan only for a new material blocker, a material weakening of retained
evidence, `ACCEPTED_SYNTHETIC`, required human authority, or broken access/event
delivery. Do not notify for routine handoffs, remediation commits, duplicate or
stale events, partner inactivity, or acknowledgements.
