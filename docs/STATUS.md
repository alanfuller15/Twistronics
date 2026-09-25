# Research status

Reader update: **2026-09-25 UTC**. The earlier multi-track inventory below
retains its **2026-09-24** snapshot date.

The interactive guide and its source-bound display data were published on
`main` by [PR #8](https://github.com/alanfuller15/Twistronics/pull/8), merged at
[`bd25a56ec6652a44fee9d9cac10c89747241286d`](https://github.com/alanfuller15/Twistronics/commit/bd25a56ec6652a44fee9d9cac10c89747241286d).
The research packets in PR #5 remain draft evidence at their own exact commits.

## Interactive learning and retained draft mapping

The [interactive field guide](interactive-guide/README.md) now displays exact
saved observations from PR #5 at commit
[`3f174f19b3ed5d57598accd1d7b1550fc7c9eeff`](https://github.com/alanfuller15/Twistronics/commit/3f174f19b3ed5d57598accd1d7b1550fc7c9eeff).
This is a presentation update; the scientific draft is not merged by it.

- [Point mapping](https://github.com/alanfuller15/Twistronics/blob/3f174f19b3ed5d57598accd1d7b1550fc7c9eeff/research/benchmarks/momentum_mapping_summary_001/OUTPUT/REPORT.md):
  64 coarse and 64 targeted refined finite-cutoff-a spectra, dimension 196.
  The smallest sampled upper gap changes from 0.008193629349 to
  0.003089965450713 meV. These are approximate point observations, not lower
  bounds between samples or evidence of gap closure.
- [Retained S1b execution](https://github.com/alanfuller15/Twistronics/blob/3f174f19b3ed5d57598accd1d7b1550fc7c9eeff/research/benchmarks/certification_s1b_quadrant_a_002/RUN/README.md):
  accepted area is 29663/65536 of the declared quadrant [1/2, 1]², about
  45.26%, across 590 accepted cells. Frontier and unresolved cells remain;
  the run is `INCONCLUSIVE_WATCHDOG_TIMEOUT`. This is not full-domain
  coverage, and point mapping adds no certified area.

The guide also retains the explicitly historical v062 node-path lesson and an
ideal, unstrained geometric moiré lesson. The angle slider does not alter the
fixed research cases or run a model. Full-domain certification, complete
projector/transport/seam composition, infinite-cutoff convergence and
experimental validation remain open.

<details>
<summary><strong>Historical multi-track inventory: 2026-09-24</strong></summary>

This retained earlier inventory distinguishes material on the default branch from public
draft work. Draft pull-request heads can move; the full commit hashes below are
the exact snapshots reviewed for this page.

## Repository snapshots

| Track | Exact snapshot | Status for a new reader |
|---|---|---|
| Default-branch baseline reviewed for this documentation | [`33888bedd167dcb6356d83777767a338cf15c06f`](https://github.com/alanfuller15/Twistronics/commit/33888bedd167dcb6356d83777767a338cf15c06f) | Published landing material at the snapshot date: v060/v062 presentation and v065 software evidence |
| Migration-contract review, PR #2 | [`fe5438438ea3bcac5e0a70011f660bf7001d0835`](https://github.com/alanfuller15/Twistronics/commit/fe5438438ea3bcac5e0a70011f660bf7001d0835) | Draft review/evidence track; not merged into `main` |
| Certification-readiness and S1a, PR #5 | [`654ef460af1dc9594457feff37cf04d628f7d558`](https://github.com/alanfuller15/Twistronics/commit/654ef460af1dc9594457feff37cf04d628f7d558) | Draft bounded certification and independently reviewed physical affine-assembly track; not merged into `main` |
| v079p acceptance mechanics, PR #6 | [`d834fd0e06a7b5170cae933aeb2f645f836425d3`](https://github.com/alanfuller15/Twistronics/commit/d834fd0e06a7b5170cae933aeb2f645f836425d3) | Draft provenance/review/package controller; not scientific execution and not merged into `main` |

These tracks have different bases and purposes. Their version numbers do not
form one linear ladder of increasingly strong scientific conclusions.

## Evidence ladder

| Evidence | Retained status | Claim ceiling |
|---|---|---|
| v060/v062 continuation | Published on `main` | Sampled finite-model node and charge-comparison evidence under the declared conventions |
| v065 | Published on `main` | Evidence-recorder/software work; not a newer numerical campaign |
| Migration-contract work | Public draft | Software acceptance and retained replay evidence for the bounded migrated consumer |
| S0-series certification work | Public draft | Mostly synthetic interface, arithmetic, transport, and control evidence; each packet has its own ceiling |
| S1a physical affine assembly | Public draft; hardening audit passed at the exact snapshot above | Fixed-case source-to-affine-assembly bridge and nested ambient identity only |
| v079p acceptance loop | Public draft | Exact-byte provenance, independent-review, gate-ledger, and deterministic packaging mechanics only |

## What remains open

The current public material does not establish all of the following:

- physical S1b uniform interval-inertia coverage over the declared domain;
- certified full-domain projector and transport enclosures;
- valid oriented seam maps and corner composition for the physical systems;
- a certified finite relative class or physical Euler-class result;
- convergence to an infinite momentum cutoff;
- correspondence to an experimentally realized sample or control path.

The S1a hardening audit **passed** for exact commit `654ef460…`: Claude's
[review](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5812018439)
and the corresponding Codex
[disposition](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5812049828)
close the four pre-S1b hardening findings. Bounded S1b work may proceed from
that exact commit, carrying the remaining native-module provenance gate. No
S1b interval-inertia result is public at this snapshot, so uniform physical
isolation remains open. The 2026-09-25 update above supersedes this earlier
statement about whether an S1b result has been published.

</details>

## How to interpret common success words

- **Test passed:** the named test produced its expected outcome.
- **Review passed:** a reviewer found no blocker within a stated scope and
  exact evidence binding.
- **Package accepted:** provenance, review, and packaging gates closed for
  exact bytes.
- **Physical assembly bridge passed:** the declared fixed model was connected
  to retained affine assembly evidence within that packet's bounds.
- **Certified physical result:** requires the separate mathematical and
  numerical gates named by the declaration. None of the earlier phrases alone
  means this.

## Maintenance rule

Update this page, the root `README.md`, and `research/README.md` together when a
new public learning milestone is accepted. Historical archive descriptors may
remain unchanged, but they must identify themselves as historical records.
