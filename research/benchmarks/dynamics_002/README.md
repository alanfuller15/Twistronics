# Dynamics002: small jobs, larger periodic box

Frozen after Claude audit5842413474 diagnosed wrap-around in grid16. The reviewed grid32 modes are reused without eigensolver calls. Retained-mode diagnostics find the first1% edge exceedance after132.5fs for sigma0.07 and172.5fs for sigma0.11; use common0–125fs. New grid64 has205 independent jobs (204×20 plus16 points), at most4 concurrent processes. Every job has its own source-bound receipt, full eigenvectors, eigensystem residual and exact dyadic coordinates. No changes to the Hamiltonian, seed, widths or envelope interpretation.

Commands from repository root, with locked wheel installed and one native thread:

```sh
python research/benchmarks/dynamics_002/run.py controls
python research/benchmarks/dynamics_002/run.py run --commit FULL_SHA --wheel /locked/wheel.whl --coarse /retained/dynamics32 --output /new/dynamics002
python research/benchmarks/dynamics_002/run.py render --commit FULL_SHA --coarse /retained/dynamics32 --output /new/dynamics002
```

The supervisor binds every dependency to the exact Git commit before workers start; each worker rechecks filesystem source hashes. Source HEAD need not be that commit because source bytes are checked directly against its Git objects. Wall limits:90s/job,900s/batch,600s rendering. No retry. Numerical promotion requires both boxes' edge mass≤1% and common-window density L1≤0.05 over all51 frames. A passing numerical result still needs independent Claude review. The previous failed batch is retained unchanged. No additional user permission is needed under the current explicit instruction to proceed with small batch workflows; no independent pre-execution PASS is claimed.
