## Candidate identity

- State file:
- Binding digest:
- Source label:

## Retained evidence reviewed

- [ ] Actual source bytes verify against every declared binding.
- [ ] Evidence references are present and accessible.
- [ ] No scientific workload, sweep, or benchmark was executed by this loop.
- [ ] Claims remain `RETAINED_EVIDENCE_ONLY`.

## Bounded partner loop

- [ ] Astra review envelope is retained.
- [ ] Claude review envelope is retained.
- [ ] Both envelopes reference the same binding digest.
- [ ] Total exchanges do not exceed two.

## Packaging

- [ ] State is `ACCEPTED` before packaging.
- [ ] `MANIFEST.json` excludes itself.
- [ ] ZIP SHA-256 is detached as `<archive>.sha256`.
- [ ] Limitations and next actions are retained.

Alan should be notified only for `ACCEPTED`, `BLOCKED`, or
`MATERIAL_FINDING`.

