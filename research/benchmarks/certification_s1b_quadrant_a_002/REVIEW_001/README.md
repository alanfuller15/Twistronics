# Retained failure diagnostics and N4 clarification

Date: 2026-09-25. ID: **S1B-QUADRANT-A-002-REVIEW-001**.
Source packet: `fd98e033d479c69709d7e434d0b527115c6a9ecd`.
This follows Claude audit [5825167937](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5825167937)
and recorded review [5825194993](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5825194993).

This is an inspection of retained records with exact rational arithmetic.
There are **zero new physical evaluations, factorizations or coverage attempts**.
The packet remains `INCONCLUSIVE_WATCHDOG_TIMEOUT`: 590 accepted cells,
391 unprocessed frontier cells, and 40 unresolved depth-9 cells. Accepted
coverage remains exactly `29663/65536` of the hard quadrant.

## What the retained failures show

All 40 unresolved cells failed the primary interval-LDL stage at a pivot
whose interval contains zero. None reached recomputation. Their recorded
Gram-margin lower endpoints remain positive (approximately
0.9999999999999724 to 0.9999999999999777), and both proposed window widths
exceed the frozen `1/100000 meV` target. Thus neither Gram invertibility nor
the proposed width threshold is the recorded blocker in these cells.

| Failed window | Cells | Endpoint pattern | Proposed width range, approximately meV |
|---|---:|---|---:|
| Upper | 36 | 26 both; 9 left only; 1 right only | 0.0350117–0.245049 |
| Lower | 4 | 2 both; 2 left only | 0.248111–0.334417 |

No cell fails both windows. The upper group lies within grid indices
`ix=346…356`, `iy=366…370` at denominator 512. The lower group consists of
`(332,332)`, `(333,332)`, `(333,331)`, `(334,331)` at denominator 512.
These describe the attempted cells, not a symmetry result or a map of all
difficult regions.

The exact width ranges and all 40 source record IDs, sequence numbers,
cell coordinates, Gram bounds, failed shifts, zero-containing pivots and
minimum preceding signed-pivot distances appear in [DIAGNOSTICS.json](DIAGNOSTICS.json).
Pivot indices are zero-based elimination indices. On an inconclusive
factorization, a retained partial negative count is not a certified matrix
inertia and a pivot index is not a band-crossing identification.

The smallest proposed upper width among accepted depth-9 cells is
`409062536313913/2000000000000000 meV` (about 0.204531), overlapping the
failed upper group's range. Proposed width alone therefore cannot classify
success. These windows are proposals derived from approximate midpoint
spectra, not certified gaps on failed cells.

The [completed review](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5825353921)
adds an important empirical qualification: 27 of 36 upper-window failures
have widths below the smallest accepted depth-9 upper width, and all four
lower-window failures lie below the smallest accepted depth-9 lower width
(about 0.343600 meV). Four accepted upper widths lie inside the exact failed
range; a fifth at about 0.246491 meV lies just above it. Width is therefore
a strong but imperfect separator within this selected sample. The accepted
upper minima at depths 7, 8 and 9 are about 0.810225, 0.412836 and 0.204531
meV; multiplying by `2^d` gives about 103.71, 105.69 and 104.72 meV. This
empirical scale motivates a bounded diagnostic, not a depth requirement,
physical gap bound, or forecast of success. In particular, extrapolating it
to widths near 0.035–0.08 meV suggests testing box sizes comparable to depths
11–12, without asserting that those sizes are necessary or sufficient.

One striking recorded example is the upper-left endpoint at `(9,352,367)`:
a preceding signed pivot approaches zero (about 0.000223914), followed by
zero-containing pivot 99 with width `306963819/4096` (about 74942.34).
This is an interval-elimination diagnostic, not a physical spectral scale.
It is compatible with interval amplification but does not isolate its cause.

| Depth | Attempts | Accepted | Inconclusive |
|---|---:|---:|---:|
| 5 | 4 | 0 | 4 |
| 6 | 100 | 48 | 52 |
| 7 | 197 | 139 | 58 |
| 8 | 218 | 165 | 53 |
| 9 | 195 | 155 | 40 |

These are priority-selected conditional samples, not same-cell convergence
or forecasts for the frontier. Retained failures establish neither gap
closure nor the necessity or sufficiency of depth 10. Observed throughput
is not a bound on the remaining frontier and its unknown descendants.

## Reproduction and binding

First materialize and verify the packet as described in [RUN/README.md](../RUN/README.md).
Then, from the repository root:

```sh
python research/benchmarks/certification_s1b_quadrant_a_002/REVIEW_001/inspect_retained.py /tmp/s1b-quadrant-a-002-review --check research/benchmarks/certification_s1b_quadrant_a_002/REVIEW_001/DIAGNOSTICS.json
```

The extractor uses only the standard library, pins the exact byte counts
and SHA-256 of the raw log, partition and results, checks the record chain,
and checks exact unresolved-cell membership. It compares the regenerated
report byte-for-byte. Without `--check`, it writes the deterministic report
to stdout. It does not reconstruct interval-LDL enclosures and does not
replace the reviewed packet verifier.

`MANIFEST.json` binds the extractor, report, this note, and the updated
RUN documentation/manifest. `RUN/HOSTED_MANIFEST.json` still has 108 entries;
only its README entry changes to bind the N4 wording correction. Both
materialization and N4 scripts were already bound there. The original
manifest remains available at the source commit. All execution data, N4
records, implementation and protocol bytes are unchanged.

## Next design question and claim ceiling

A future frozen diagnostic protocol could distinguish the effect of smaller
fixed boxes, a different fixed congruence/pivot strategy, and higher precision
on a preselected set of failed endpoints. This follow-up selects none of
those changes for execution and does not predict which will succeed. Any
new numerical work requires a separately frozen and reviewed protocol.

N4's same-runtime byte repeat is now explicitly qualified in RUN/README.md.
The retained hash binds artifact identity; checked interval evidence supports
certification. Cross-platform basis generation can change the bytes while
the tests still certify. Claude reported that behavior on another runtime;
this follow-up does not rerun N4.

No whole-quadrant, full-domain, uniform-isolation, cutoff-b/agreement,
topology, transport, seam, cutoff-convergence, v078 or experimental claim
follows. Both PRs remain unmerged.
