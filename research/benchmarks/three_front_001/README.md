# Three-front batch 001

Codex producer, Claude independent reviewer. Exact protocol/source commit is recorded in every receipt before physical execution. User-directed bounded runs; no independent pre-execution PASS is claimed. The cutoff study retains its independent pre-execution review gate from PR #2 comment 5826528759 and START_HERE.md. Its runnable source is frozen here; execution requires Claude PASS on this exact commit. Depth refinement and dynamics run under the current user direction and remain pending post-execution review.

- Refinement: only 120 unresolved depth-10 parents become 480 depth-11 children. The 2,671 accepted cells are inherited unchanged. Same method-004 interval evaluation and retained physical verifier. Four global sorted round-robin queues, no retries or deeper splits.
- Cutoff: compare all 64 retained scout coordinates at dimensions 196 and 308. Approximate point-only evidence.
- Dynamics: two Gaussian widths, 16/32 midpoint momentum grids, fixed cutoff-a Hamiltonian, 81 frames over 0–200 fs. Full retained projected modes allow frame reconstruction. This is a new explicitly coarse-grained envelope calculation, not the unavailable earlier dynamics source. It drops interference between reciprocal components; do not describe it as microscopic density. Compare the same physical window, never renormalize a crop.

Run environment: Python >=3.10, numpy, scipy, exact locked python-flint wheel. Native wheel/loaded-library binding uses glibc dl_iterate_phdr and honest proc_maps_checked=false, reusing the audited provenance routine in an explicitly producer role. No old producer requirement or source is modified.

Commands from the repository root (set native threads to 1 and PYTHONPATH to the installed locked wheel):

```sh
python research/benchmarks/three_front_001/run.py controls
python research/benchmarks/three_front_001/run.py run --front refine --slot 0 --wheel /absolute/wheel.whl --implementation-commit FULL_SHA --output /new/refine0
# Repeat slots 1,2,3, at most four concurrent workers.
python research/benchmarks/three_front_001/run.py run --front cutoff --review-receipt /absolute/claude-review.json --wheel /absolute/wheel.whl --implementation-commit FULL_SHA --output /new/cutoff
python research/benchmarks/three_front_001/run.py run --front dynamics --grid 16 --wheel /absolute/wheel.whl --implementation-commit FULL_SHA --output /new/dynamics16
python research/benchmarks/three_front_001/run.py run --front dynamics --grid 32 --wheel /absolute/wheel.whl --implementation-commit FULL_SHA --output /new/dynamics32
python research/benchmarks/three_front_001/summarize.py /new FULL_SHA
```

Supervisor enforces wall timeout, TERM then KILL, process-group reap, per-file and memory limits. Partial/failed runs are retained and cannot pass the aggregate. Full cell records are fsynced individually. No independent acceptance, merges, topology, seam, infinite-cutoff or experimental claim. New site frames await comparison and Claude review.
