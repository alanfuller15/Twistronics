# New frozen-run workflow

This additive workflow separates scheduling, retained-state loading and scientific checks. Existing frozen runners do not import it and remain unchanged. Independent Claude review of this implementation is pending. It is infrastructure, not a numerical or publication PASS.

## Before any physical call

1. Fix points, cutoffs, exact geometry, jobs, reused source files and regression points in SPEC. Keep one complete loop or job per reused source in the regression subset. Use at most 32 points/job and up to four workers, with job count divisible by worker count.
2. Bind the run's code, CASE, dependencies, shared tools, source manifests and every reused file. Freeze and push. Run nonphysical controls at the frozen commit, including fast-matrix controls with retained fixtures if using FastPointMatrix. Keep all result files. Check all reused files with `retained_states.preflight`.
3. Post the frozen-plan comment on PR #2 before physical execution. Declare the one-shot command, exact source SHA, numerical and resource limits, and no-retry behavior. A failed physical launch means stop and report.

## Scheduling API

Import `Job`, `Limits` and `run_jobs` from `concurrent_supervisor`. Each `Job` carries a unique `jobNNN` name, an argv tuple (never a shell string), and its planned point indices. A literal `{output}` argv element is replaced by the job directory. Supply an absolute repository `cwd`, a fresh output directory and the frozen 40-character `source_commit`.

The caller must compare frozen source/dependency bytes before `run_jobs`; the supplied commit is a binding label, not proof of a clean source tree. Each physical worker must repeat the scientific source bindings and runtime provenance checks before matrix evaluation or eigensolves. `bounded_worker.py` applies RLIMIT_AS/RLIMIT_FSIZE and enforces the single-thread environment before exec.

Receipts retain argv/configuration, output hashes, planned points, exit code, deadlines, signals and group emptiness. They do not invent an actual eigensolver count from planned work. The scientific worker must retain actual numerical progress/counts. The batch receipt reports `numerical_acceptance=NOT_EVALUATED`; replay and independent review are separate.

The supervisor polls all active jobs before admitting replacements, stops on observed failure, and cleans up all active groups on failure or SIGTERM/SIGINT. Cleanup has a separate bounded grace. SIGKILL/host loss may prevent cleanup/receipts, and the packet must then remain incomplete. Output-directory reuse and resume are rejected.

## Reuse API and worker obligations

`retained_states.preflight(spec, roots)` checks every reused file. `roots` maps source names to materialized source directories; `spec` uses the 023 `reuse.sources` and `reuse.point_source` layout.

`retained_states.load_job(spec, owned_indices, roots)` returns read-only copies of full spectra and four-state frames only for that job, plus verified I/O counts. Each needed SAMPLES/state file is read once, hashed, and decoded from the **same bytes**. It checks the coordinate/label mapping, array dimensions, dtype, finite sorted spectrum and frame orthonormality. It does not cache across workers or trust a previous preflight in place of hashing.

The physical worker must still:

- rebuild H at every reused cutoff and calculate the eigenpair and nested residuals;
- re-solve the frozen source regression subset with full-spectrum `evr` and compare exact array bytes;
- retain regression equality and recomputed/reference array hashes;
- solve all new-cutoff points, retain full spectra and four-state vectors, then replay all metrics and loop products.

Do not use the loader for undeclared new cutoffs without extending and freezing its schema/controls. It currently reads the reused cutoff from `additional_cutoff_<key>` and supports the reviewed NPZ/pack formats. A loader PASS says nothing by itself about the eigenpair residual against H.

## Controls

`python -B research/tools/test_concurrent_supervisor.py OUTPUT.json` runs synthetic process fixtures: no physical Hamiltonian or eigensolve. The retained-state fixture in `docs/audits/controls022-cutoff023/test_reuse_loader.py` needs materialized 021 and checks all 384 reused points against a separate decoder, plus rejection controls. Run controls with ordinary Python, not `-O`, because upstream numerical/packing checks use assertions.

Do not adopt `evd`, subset eigensolves or multithreaded BLAS within a job. The current H is exactly affine in momentum in the implemented model; adding quadratic terms or a reduced effective Hamiltonian is a separate research-method change, not a throughput optimization.
