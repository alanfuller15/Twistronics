# Fixed-specimen S1b diagnostic protocol

**DESIGN REVIEW PENDING / NO PHYSICAL RUNNER / NOT EXECUTED.**

This proposal addresses D1 in Claude review
[5825338266](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5825338266),
recorded by Codex in [5825353921](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5825353921).
The source is `ad18d34ef0bf3b5d4ec7a4d2e27ba954f2fd0492`. The machine-readable
contract is [SPEC.json](SPEC.json); [INPUTS.json](INPUTS.json) binds the retained
records, specimen selection, exact centers and fixed spectral windows.

## Question and evidence

Most unresolved cells have narrower proposed windows than any accepted
depth-9 peer: 27 of 36 upper failures and all four lower failures. The small
overlap still prevents width alone from classifying success. Accepted upper
minima at depths 7–9 scale near `105 meV / 2^d` in the retained sample. This
is a sampling observation; it does not prove a gap bound, a required depth,
or the success of a future run. The exact comparison is reproduced in
INPUTS.json, and the reviewed note now includes this qualification.

The proposed diagnostic asks whether the same frozen endpoint tests respond
to smaller boxes, higher arithmetic precision, or a different fixed
elimination order. It changes one factor per comparison to the declared
baseline, with an additional point-precision comparison. It does not test
every interaction, optimize windows, or extend the coverage queue.

## Seven frozen specimens

All indices below are at depth 9, with denominator 512. Each selection uses
only retained exact values; ties use ascending `(depth, ix, iy)`.

| ID | `(ix,iy)` | Historical class and selection |
|---|---|---|
| upper_left | (352,367) | Left-only upper failure; largest ambiguity interval in that class |
| upper_right | (351,370) | Sole right-only upper failure |
| upper_both | (351,368) | Both upper endpoints failed; smallest proposed upper width |
| lower_left | (333,332) | Left-only lower failure; largest ambiguity interval in that class |
| lower_both | (333,331) | Both lower endpoints failed; smallest proposed lower width |
| accepted_upper | (348,369) | Accepted; smallest proposed upper width at depth 9 |
| accepted_lower | (332,331) | Accepted; smallest proposed lower width at depth 9 |

This is an intentionally selected diagnostic sample, not a representative
sample for estimating failure frequency. All four historical shifts are used
for every specimen, including endpoints that previously passed.

## Eight fixed arms

Radius multipliers apply to both axes about the original center. The original
half-width is `1/1024`. The same exact rational basis and recorded shifts are
held fixed across all eight arms for a specimen.

| Order / arm | Radius multiplier | Bits | Basis column order | Comparison |
|---|---:|---:|---|---|
| original_128 | 1 | 128 | identity | Reconstructed baseline |
| point_128 | 0 | 128 | identity | Remove spatial box variation |
| point_256 | 0 | 256 | identity | Point arithmetic sensitivity |
| original_256 | 1 | 256 | identity | Full-box arithmetic sensitivity |
| original_reverse_128 | 1 | 128 | reverse | Fixed elimination-order sensitivity |
| half_128 | 1/2 | 128 | identity | Smaller concentric box |
| quarter_128 | 1/4 | 128 | identity | Smaller concentric box |
| eighth_128 | 1/8 | 128 | identity | Smaller concentric box |

The last three have side lengths equal to depth-10/11/12 grid cells, but
are centered on the depth-9 cell center. They are **not** tiling descendants.
Point or nested-box success cannot discharge a parent cell or certify its
children. The extra quarter/eighth arms examine the proposed scale heuristic
at a fixed, modest cost; they do not assume it is valid.

There are 56 configurations and 224 primary endpoint calls. Every completed
configuration repeats its four endpoint tests from serialized inputs in
fresh objects, adding at most 224 verification calls: **448 total**. Repeats
run even after an inconclusive primary result. They check retention and
reconstruction consistency using the same interval backend, not algorithmic
independence. Report actual started/completed calls and Gram-skipped calls.
Zero-containing pivots stop only their own factorization. No retry, extra
arm, conditional refinement or basis replacement is permitted.

Execution order is arm-major, then the seven specimen IDs above; endpoints
are lower-left, lower-right, upper-left, upper-right, followed by the four
verification repeats. This gets full-box and point controls early if the
watchdog truncates the fixed sequence. Partial results remain explicitly
incomplete and cannot be presented as a completed comparison.

## Fixed inputs and arithmetic obligations

The historical packet did not retain its exact basis matrices. A future
implementation must generate one new midpoint eigenbasis per specimen at
128-bit assembly precision, serialize every finite entry as an exact rational
from its 17-significant-digit decimal representation, and durably retain all
seven matrices and hashes before testing any arm. This is a new baseline
reconstruction; cross-platform historical basis identity is not assumed.
No arm or verification repeat may regenerate or re-round the basis.

At both 128 and 256 bits, rebuild the affine coefficient enclosures from the
same exact CASE inputs. Promoting a previously computed 128-bit enclosure
does not satisfy the precision arm. Retain the full Gram certificate and
enclose `V^T H(center) V + dx V^T Hx V + dy V^T Hy V - s V^T V`.
The reverse arm uses the exact permutation `195,194,...,0`, applied to both
rows and columns of the formed interval matrix and Gram matrix. It must
not remultiply using reversed basis columns: changed accumulation order
would confound the intended comparison. Bind the unpermuted interval hashes
to the original_128 arm before permutation. This is fixed
ordering, not adaptive pivoting; adaptive or 2-by-2 pivot algorithms require
a different reviewed protocol.

Every result must bind the source record, exact box, basis hash, permutation,
precision and shift. An inconclusive factor's partial negative count is not
certified inertia. Complete signed pivots with a different negative count are
reported as `OTHER_INERTIA_VERIFIED`, not as the target count or a malformed
record. Uncertified Gram bounds remain a diagnostic failure, with no LDL
performed for that configuration in either primary or verification stage.

The two accepted controls are comparators. If either original_128 control
fails, finish only the already frozen comparisons within the caps, report
`CONTROL_MISMATCH_REVIEW_REQUIRED`, and withhold favorable interpretation
pending review. Do not tune inputs to reproduce the historical label.

## Bounds, retention and review gates

SPEC fixes one cutoff-a case, dimension 196, one worker/native thread,
seven eigensolver calls, 448 total endpoint factorization starts, 2 GiB address
space, a 1,200-second soft deadline and a 1,260-second hard deadline measured
from worker launch, and 256 MiB raw evidence. This is a maximum work envelope,
not a promise that all comparisons finish. Source preparation, basis creation
and repeat checks are inside the same wall budget.

Use the already reviewed supervisor/log design as a reference, adding a
durable `EIGEN_STARTED`/`EIGEN_FINISHED` events for the seven basis-generation
calls, then a `BASIS_SEALED` event after all seven complete basis records.
Endpoint work starts only after the seal. Append `CALL_STARTED` before each
LDL call so interrupted work consumes its factorization budget. Bind each
`CALL_FINISHED` to its start; an interrupted final
call is never retried. Completed evidence is retained regardless of outcome.
Only an incomplete final line can be trimmed. A separate supervisor must
reap the worker group, confirm ESRCH, and retain the receipt before packaging.
An offline verifier derives counts, order, outstanding calls and terminal
status from the validated log, not from worker summaries. It checks exact
file membership, manifest bindings and byte-repeatable check-only packaging.

The future implementation must retain the exact locked wheel/native build,
Python/NumPy/BLAS identity and binary digests, source hashes, thread/precision
settings and complete serialized bases. Redact personal paths and hostnames;
do not collect credentials or unrelated environment values. Runtime identity
and all mathematical inputs must be auditable from the retained packet.

The current files contain only design and retained-data extraction. Claude
must pass this exact protocol commit before physical-runner implementation.
An implementation-only commit must then pass independent audit, including
known-inertia, zero-pivot, wrong-full-inertia, basis/shift/cell/precision/
permutation substitution, control mismatch, call-cap, byte-cap, repeat
mismatch, signal recovery, and unexpected-file controls, before execution.
Any executed evidence then requires a separate audit. These are sequential
gates, with no automatic follow-on run or merge.

## Reproduce the source selection

Materialize the already reviewed packet as described in
[its RUN note](../certification_s1b_quadrant_a_002/RUN/README.md), then run:

```sh
python research/benchmarks/certification_s1b_diagnostic_001/freeze_inputs.py /tmp/s1b-quadrant-a-002-review/ATTEMPTS.ndjson --check research/benchmarks/certification_s1b_diagnostic_001/INPUTS.json
```

This standard-library script reads and hashes the retained raw log, selects
the seven specimens by fixed rules, and reproduces INPUTS.json byte-for-byte.
It makes no model imports, eigensolver calls or factorizations. MANIFEST.json
binds this packet and the reviewed-note correction. Source commit and raw-log
hashes pin the historical evidence; no historical execution bytes change.

## Interpretation and claim ceiling

Point success with full-box failure is compatible with spatial-enclosure or
variation difficulty; it does not prove a gap closes. A precision-only pass
shows sensitivity to arithmetic precision for those fixed inputs, not a
unique cause. A reverse-order pass shows order dependence. All-arm failure
stays inconclusive. The arms do not test changes to window choice or to the
basis generation strategy, and do not measure all factor interactions.

Even a full-box four-endpoint pass remains diagnostic in this packet. It
does not modify the historical partition or acceptance rule. Coverage stays
`29663/65536` with `INCONCLUSIVE_WATCHDOG_TIMEOUT`. No whole-quadrant,
full-domain uniform isolation, cutoff-b/agreement, topology, transport,
seams, cutoff convergence, v078 or experimental claim follows.
