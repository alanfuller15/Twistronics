# Audit evidence bundle

Read twistronics_v053_audit.md first. Recipient consumption is unconfirmed.

- full-inventory.md: every scanned source path, original rank and heuristic fields.
- layer1.json: original scanner output, including all markers and inferred subtrees.
- layer1.sarif: 527 heuristic missing-test findings; not externally schema-validated.
- deep-read-selection.json: exact top-14 source paths.
- evidence-verification.json: output of the included read-only verification helper.
- evidence-checks.json: initial artifact observations, including AST import references.
- input-preservation.json / input-sha256.json: input preservation checks and digests.
- archive-sha256.json: fingerprints of the two supplied ZIPs.
- audit-plugin/: unchanged plug-in sources and documentation.

The original project is not duplicated in this evidence bundle. Extract the supplied twistronics archive, then run `python -B verify_evidence.py /absolute/path/to/twistronics_v053_reconciled` to repeat the read-only data checks. This does not import project code or run project tests. Hash matching checks internal consistency, not scientific correctness or artifact authenticity.
