# Frozen independent review: 022, 023 and 024

200 fixed full-spectrum solves, 26 jobs, two isolated single-thread workers; no retry/resume. 90 s/job, 600 s/batch, 3 GiB address space, 64 MiB/file. The replacement supervisor at e039de6ae4b6a9285fad0fa63155c1324ba45a55 has Claude infrastructure PASS 5845181342.

Use the original Arb affine matrix builder, not FastPointMatrix. Independently compare 24 e corner points spanning all six 022 loops and 48 f corner points spanning all twelve 023 loops with NumPy full eigh. Re-solve all 64 declared e regression points with full scipy evr and demand exact spectra/four-vector bytes. For 024, independently solve both a and d at 32 fixed points: all eight historical regression points, all reported local minima, map/change extrema, boundary corners and fixed spread points. SPEC lists the complete final set and binds every consumed retained-state file and reference dependency.

Energy tolerance 1e-8 meV, gap tolerance 1e-9 meV, four-state eigenpair residual <1e-8 meV, each-band/pair/four-frame residual norm <1e-6. Preserve all full spectra and four-state vectors, progress counts, native provenance and supervisor receipts. Independent NumPy comparison is not adoption of a different production driver. No adaptive expansion, retuning or retries on failure.

Command (replace SHA only with this pushed source commit):
`PYTHONPATH=/workspace/scratch/0a981e4da253/pydeps OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B docs/audits/gates022-024/recompute.py run --commit SHA --wheel /workspace/scratch/0a981e4da253/wheels/python_flint-0.9.0-cp310-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl --output /workspace/scratch/0a981e4da253/gates022-024-run`

Post the exact frozen-plan comment before launch. Any failed launch stops the physical review and is reported. Scientific scope and all exclusions remain unchanged. This review adds no accepted coverage area. Site v30 remains gated on 022/023 numerical PASS and then Claude's exact presentation PASS. PRs #2/#3 remain unmerged.
