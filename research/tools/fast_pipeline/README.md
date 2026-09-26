# Fast pipeline: upgrades 1–3 (byte-preserving)

**Authorization:** Alan, 26 Sep 2026. He asked to adopt upgrades 1 and 2 now, then upgrade 3.
**Producer:** a Claude Code session. **Independent review:** Codex **PASS** ([5844535047](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5844535047); evidence `cc60ef8f`), approved for all new frozen runs.

## What changes

| Upgrade | Change | Precision or reproducibility cost |
|---|---|---|
| 1. `FastPointMatrix` | Drop-in for `three_front_001/run.py:point_matrix`. H(x,y) = C₀ + x·C₁ + y·C₂. C₁ and C₂ touch only the kinetic 2×2 blocks (0.25–1.0% of entries). Everywhere else they are exact Arb zeros, so the float midpoint equals mid(C₀) exactly and is computed once. Only the support is re-evaluated per point, with the same Arb expression and order. | **None.** The output is byte-identical to the reference. |
| 2. Job sizing | Jobs of up to 32 points instead of 6–8. Per-job wheel provenance, rlimits, receipts, the 90 s limit and subprocess isolation are unchanged. | None |
| 3. `pack_states` / `unpack_states` | A deterministic container: per-array byte-plane shuffle, then zlib-9, with a SHA-256 of the raw bytes in the header. Store it as binary; use base64 only if a transport requires text. | None. Arrays are bit-identical after unpacking. |

## Evidence

**`controls.py` → `CONTROLS_RESULT.json`** (zero eigensolves)
- Fast and reference matrices are **byte-identical at all 48 control points × cutoffs a/b/c/d/e** (240/240). The control points cover the 006–021 loop and grid coordinates, domain corners and non-dyadic rationals.
- Matrix-build time per point:

| Cutoff | Reference | Fast |
|---|---:|---:|
| c | 135 ms | 1.5 ms |
| d | 254 ms | 1.7 ms |
| e | 469 ms | 5.0 ms |

- `pack_states` is deterministic and round-trips all 24 retained 021 `STATES.npz` files bit for bit.

**`reproduce_021.py` → `REPRODUCE_021_RESULT.json`** (576 physical eigensolves)
- The full LOWER-CONTROLS-021 run (execution `38204bfc`) was re-run with upgrades 1+2, in 6 jobs of 32 points.
- **192/192 SAMPLES rows are identical** to the retained rows (gaps, angles, containment, residuals).
- **1152/1152 energy and four-state vector arrays are bit-identical.**
- Summed job time is **63.2 s, against 215.9 s** for the original: 3.4× faster.
  - What remains is mostly the eigensolve (47 s).
  - Setup is 12 s, and matrix builds take 1.1 s.
- Packed states from the 6 regrouped jobs total 11.1 MB. Packing the original 24 jobs gives 11,269,337 bytes against 13,407,142 bytes of npz (**15.9% smaller**, measured by Codex in its review).
- Against the 18.3 MB of base64 parts, binary packed storage is about 38% smaller.

## Adoption rule for new runs

1. Import `FastPointMatrix` and build one per cutoff per job.
2. Keep `controls.py` passing at the run's own frozen commit before any physical call.
3. Use jobs of up to 32 points. Check the 90 s limit against the timings above (e: about 0.25 s per point including the eigensolve).
4. Retain states with `pack_states`, storing binary where the transport allows.
5. Nothing about reviewed runs changes: their frozen runners and evidence stay as they are.

The eigensolve is now the floor. Computing only a subset of eigenpairs would be faster, but it would break the "retain the full spectrum" rule, so it is **not** adopted.
