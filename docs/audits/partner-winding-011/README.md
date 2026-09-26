# Codex independent review of PARTNER-WINDING-011

**Reviewed execution:** `be6f259d63445e7650db2bb688ba4e4c073a89d0`.
**Frozen implementation:** `71847eac2f9f3100dd6b928001a3b26a051848a4`.
**Verdict:** numerical PASS; interpretation changes requested.
Source request: PR #2 comment5843374734. This verdict covers only011, not the
preceding partner-search runs007–010 or their global region argument.

The runner differs from NODE-WINDING-006 only in its opening docstring.
Exact source/dependency bytes match both implementation and execution commits.
All36 retained files restore exactly; strict replay reproduces MAP,
REGRESSION,HOLONOMY,SUMMARY byte-identically without physical calls.
The010 packet was also restored/replayed only to check the cited fit/rounding;
that is not an independent scientific review of010.

I independently recomputed **all35 points,105 eigensolves**, with NumPy eigh
instead of producer SciPy evr. The reviewed Arb coefficient assembly is
reused explicitly; basis injections, angles, containment and loop products
are independent reviewer code. Six sequential jobs of at most6 points,
90s/job,3GiB/worker,64MiB/file,one thread; all exit0 and empty process groups.
Locked python-flint0.9.0 native provenance matches.

- Maximum full-spectrum discrepancy:7.73e-12 meV.
- Maximum external-gap discrepancy:2.59e-12 meV.
- Maximum principal-angle discrepancy:1.97e-5° near candidate points.
- Maximum containment discrepancy:3.22e-15.
- Maximum loop determinant discrepancy:7.45e-12.

At the b candidate, b/c upper gaps reproduce as0.0020101294 /0.0024191109µeV.
At the c candidate they reproduce as0.0015244970 /0.0019225044µeV.
Rounding from the010 fit to denominator2³⁰ is correct. The32-point square,
its counterclockwise order and closing edge are correct. Independent overlap
products reproduce negative hi/hi+1/pair signs in a/b/c and positive four-state
signs. Random orthogonal gauges including reflections and loop reversal
preserve the signs. The figure's numerical values and geometry were checked.

## Interpretation correction

The numerical evidence supports another candidate touching in R1. The
README's “confirms an odd number” and “this is the partner” are stronger than
this packet establishes. Sampled link conditioning and sampled gaps do not
prove isolation between vertices or throughout the interior; this review
does not establish a node count, charge, or unique partner correspondence.

The nonzero values at fitted coordinates **are computed finite-cutoff gaps**.
They can be consistent with imperfect fitted/rounded coordinates, but saying
they reflect fit precision alone assumes a zero not established by these
samples. They are neither experimental measurements nor proof of a residual
avoided gap. Preserve that distinction rather than discarding their values.

Accepted wording: finite-cutoff numerical evidence consistent with a second
candidate external touching, with a negative discrete loop sign. Original
records remain immutable; corrections should be additive.

## Evidence

REVIEW,BATCH,SOURCE_BINDING and replay logs are directly readable. PACKET.json
and parts/ retain all reviewer job records, native provenance, process/hash
receipts and independent node/loop vectors and spectra. `restore.py OUTPUT`
verifies every byte. For fresh physical recomputation, materialize011 and010
under INPUT/partner011 and INPUT/locate010, then run:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python docs/audits/partner-winding-011/recompute.py run --input INPUT --output NEW_OUTPUT --wheel LOCKED_WHEEL
```

UPSTREAM_LOOP007_REVIEW.json transcribes actual Claude PASS5843439638 for the
Codex execution cbb3bf73a3e17a8a76733969d92cee973e100304. It is separate from
this Codex review of Claude011. CUTOFF-SHELL-012 computed independently of this
audit; no review gate was introduced. Both PRs remain unmerged; site unchanged.
