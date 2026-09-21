# Twistronics research

Current batch: **our v057 — historical consumers and controlled re-refinement replay**. Start with the [team share](research/v057/TEAM_SHARE_v057.md), [report](research/v057/REPORT.md), [attribution ledger](research/v057/ATTRIBUTION.md), [summary](research/v057/SUMMARY.json) and [reproduction instructions](research/v057/README.md).

The historical kinetic='none' baseline and endpoint lower-gap recipes now reproduce at N4/N6 with both the defective and repaired BM.refine helpers. All 28 recorded calls return supported values; six calls reach the wrapped second attempt, covering three seed/cutoff cases repeated under both helpers. No root, gap or bandwidth value changes. All observed first/final optimizer attempts succeed, so broader historical impact involving a failed second attempt remains unresolved.

The endpoint lower gaps are 22.537986131952 meV (N4) and 22.691984750071 meV (N6), reproducing the recorded v035 correction. Separate baseline Euler calculations pass the retained numerical gate at 24×40 and 32×56 meshes, returning e2=-1 at both cutoffs. These are finite sampled checks for a declared historical model, not a global isolation proof or physical-bilayer validation.

**62 tests passed in source/input/environment-bound run `20260921T023426Z_a4ce516a`**, including forced optimizer failures and corrupted-evidence rejection. Numerical workers also record matching before/after runtime identities. Publication rechecks the saved measurements, source-to-log attribution and test evidence. Prior tracked campaign, audit and partner evidence is preserved.

The attribution ledger records eight consumer relationships. Legacy transfer.py and flat_e2.py define their own Euler routines; repairs in euler.py alone do not gate them. The logs already withhold invalid Euler conclusions for nonisolated/nonorientable bundles and correct the earlier e2=0 prediction. Other historical sweeps and braid detours are not cleared by this batch.

Prior [v056](research/v056/REPORT.md) reconciles 80 selected campaign case records across eleven batches and identifies the success-field consumer. Prior [v055](research/v055/REPORT.md) contains the modern-model lower unlink fold and its [handoff correction](research/v055/ADDENDUM_v055.md). Prior [v054](research/v054/REPORT.md) contains audit repairs and the instrumented 76-state preparation replay. Their test runs remain separately labeled historical evidence.

## Layout

- `research/v057/`: current numerical probes, source-to-log ledger, tests and frozen publication records.
- `research/v056/`, `research/v055/`, `research/v054/`: previous checked batches.
- `research/incoming_partner_v054/`: preserved latest partner delivery.
- `research/v053/`, `research/prior_our_v052/`: earlier versioned campaign evidence.
- `audits/v053/`: original inspection audit and recorded responses.
- `research/MANIFEST.json` and `RELEASE.json`: original v053 import provenance, unchanged.

The [next bounded sequence](research/v057/NEXT_SEQUENCE.md) is an N8 endpoint-gap comparison under the modern lab_nn_full model in both engines, with explicit edge seeds and comparison to the supplied N8 record. A physical acceptance target, microscopic tunnelling strain law and independent validation remain necessary before physical magnitude claims. No complete security clearance, continuous-path proof, infinite-cutoff bound or new license is claimed.
