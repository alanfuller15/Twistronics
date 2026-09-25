# Research archive map

The repository preserves successive deliveries and their provenance. This is
valuable for auditability but can mislead a first-time reader into treating the
directory tree as one current software product.

## Default-branch map

| Location | Purpose | First-time guidance |
|---|---|---|
| `docs/visual-guide/` | Accessible v060/v062 scientific presentation | Recommended first stop |
| `research/v062/` | Latest numerical batch presented on `main` | Use for the retained v062 report, method, coverage, and data |
| `research/v065/` | Evidence-recorder/software iteration | Do not treat as a newer numerical batch |
| `research/v053/`–`research/v061/` | Earlier research deliveries and handoffs | Consult only when tracing a result's provenance |
| `research/prior_our_v052/` | Nested preserved predecessor archive | Avoid on first read; paths repeat by design |
| `research/incoming_partner_v054/` | Preserved incoming partner delivery | Evidence source, not the current landing page |
| `audits/v053/` | Inspection and audit material for the v053 delivery | Useful for provenance and known limitations |
| `research/MANIFEST.json` | Historical archive inventory | Integrity record, not current project status |
| root `RELEASE.json` | Historical v053 release descriptor | Not the current research-status index |

## Public draft tracks

Later work is currently distributed across draft pull requests rather than the
default-branch tree. Use [STATUS.md](STATUS.md) for exact snapshots and claim
ceilings. In particular, the acceptance-loop tree in PR #6 is engineering
governance for exact evidence packages, not a scientific-result directory.

## Provenance rule

Do not delete or rewrite a historical packet merely to make navigation cleaner.
Improve navigation in the root and `docs/`, label historical metadata clearly,
and retain exact evidence paths and hashes.
