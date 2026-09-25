#!/usr/bin/env python3
"""Run a frozen finite synthetic list, with per-job/global hard stops.

Usage: PYTHONPATH=<locked python-flint installation> python run_calibration.py --output RUN
The output directory must not already exist. No automatic retries or sweeps.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True)+"\n")


def regressions():
    from flint import arb, arb_mat
    from primitives import enclosure, inertia_ldl
    checks = []
    def check(name, condition, evidence):
        if not condition:
            raise AssertionError(name)
        checks.append({"name": name, "pass": True, "evidence": evidence})
    # H=1, V=2, s=2: correct congruence is -4, the omitted-Gram formula +2.
    good = inertia_ldl(arb_mat([[-4]]))
    wrong = inertia_ldl(arb_mat([[2]]))
    check("omitting_shift_Gram_changes_inertia", good["negative"] == 1 and wrong["negative"] == 0,
          {"correct": good, "omitted_Gram": wrong})
    zero = inertia_ldl(arb_mat([[0, 1], [1, 0]]))
    check("nonsingular_zero_leading_pivot_is_inconclusive", zero["status"] == "INCONCLUSIVE", zero)
    # Exact symmetric permutation: diagonal inertia is invariant.
    permuted = inertia_ldl(arb_mat([[3, 0], [0, -2]]))
    check("symmetric_permutation_preserves_inertia", permuted["negative"] == 1, permuted)
    repeated_minus = inertia_ldl(arb_mat([[-3, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 5]]))
    repeated_plus = inertia_ldl(arb_mat([[-5, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 3]]))
    check("repeated_pair_needs_no_internal_gap", repeated_minus["negative"] == 1 and repeated_plus["negative"] == 3,
          {"minus_shift": repeated_minus, "plus_shift": repeated_plus})
    # Schur family [[-1,b],[b,2]], b in [-1/4,1/4]; exact complement
    # -1-b^2/2 is negative, while complement block D=2 stays positive.
    b = arb(0, arb("1/4"))
    schur = -1 - b*b/2
    whole = inertia_ldl(arb_mat([[-1, b], [b, 2]]))
    check("uniform_Schur_family", schur < 0 and whole["negative"] == 1,
          {"schur_enclosure": enclosure(schur), "inertia": whole})
    # Direct selected-block motion cannot be dropped even if B=0.
    moving = inertia_ldl(arb_mat([[arb(0, 1), 0], [0, 2]]))
    check("zero_coupling_does_not_remove_direct_motion", moving["status"] == "INCONCLUSIVE", moving)
    # Parameter uncertainty is real error even when propagation is isometric.
    check("parameter_debit_is_not_roundoff", arb(2).sqrt()/1000 > arb("1/100000000"),
          enclosure(arb(2).sqrt()/1000))
    return {"status": "PASS", "checks": checks, "checks_passed": len(checks)}


def run_job(job):
    from flint import arb, ctx
    from primitives import enclosure, frobenius, identity, inertia_ldl, synthetic_symmetric, transport_constant
    ctx.prec = job["precision"]
    ctx.threads = 1
    start = time.monotonic()
    if job["kind"] == "regressions":
        result = regressions()
    elif job["kind"] == "inertia":
        n, shift = job["dimension"], job["shift"]
        h, v, d = synthetic_symmetric(n)
        assembly_done = time.monotonic()
        gram = v.transpose()*v
        eta = frobenius(identity(n)-gram)
        if not eta < 1:
            raise ArithmeticError("basis invertibility bound failed")
        # The shift multiplies the full Gram matrix, not the identity.
        k = v.transpose()*h*v - shift*gram if job["precondition"] else h - shift*identity(n)
        matrix_done = time.monotonic()
        result = inertia_ldl(k)
        expected = sum(di < shift for di in d)
        if result["status"] == "PASS" and result["negative"] != expected:
            raise AssertionError("known spectrum inertia mismatch")
        result.update({"expected_negative": expected, "Gram_defect_F_bound": enclosure(eta),
                       "sigma_min_V_lower_bound": enclosure((1-eta).sqrt()),
                       "assembly_wall_seconds": assembly_done-start,
                       "congruence_wall_seconds": matrix_done-assembly_done,
                       "LDL_wall_seconds": time.monotonic()-matrix_done})
    elif job["kind"] == "transport":
        raw = transport_constant(job["dimension"], job["omega"], job["steps"], job["degree"])
        if not raw["bound"] < arb(job["acceptance_error"]):
            raise AssertionError("transport error exceeds fixed acceptance")
        if not raw["reference_discrepancy_bound"] < raw["bound"]:
            raise AssertionError("known solution not inside the derived error ball")
        result = {"status": "PASS", "bounds": {k: enclosure(v) for k, v in raw.items()}}
    else:
        raise ValueError("unknown frozen job")
    result.update({"job": job, "wall_seconds": time.monotonic()-start,
                   "peak_resident_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   "physical_evaluations": 0})
    return result


def environment(wheel):
    import flint
    # Retain hashes of all loaded-package/native artifacts. No environment
    # variables, credentials, host names or user paths are exported.
    dist = importlib.metadata.distribution("python-flint")
    artifacts = []
    for member in sorted(dist.files or [], key=str):
        if str(member).endswith(".so") or ".so." in str(member):
            p = Path(dist.locate_file(member))
            artifacts.append({"path": str(member), "sha256": digest(p), "bytes": p.stat().st_size})
    return {"python": platform.python_version(), "implementation": platform.python_implementation(),
            "machine": platform.machine(), "system": platform.system(),
            "python_flint": flint.__version__, "FLINT": flint.__FLINT_VERSION__,
            "threads": 1, "wheel": {"filename": wheel.name, "sha256": digest(wheel), "bytes": wheel.stat().st_size},
            "native_artifacts": artifacts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--worker")
    args = parser.parse_args()
    spec = json.loads((HERE/"SPEC.json").read_text())
    if args.worker:
        resource.setrlimit(resource.RLIMIT_AS, (spec["limits"]["worker_address_bytes"],)*2)
        job = next(j for j in spec["jobs"] if j["id"] == args.worker)
        try:
            result = run_job(job)
        except Exception as exc:
            result = {"status": "EXECUTION_ERROR", "job": job, "error_type": type(exc).__name__, "message": str(exc)}
        print(json.dumps(result, sort_keys=True))
        return
    if not args.output or not args.wheel:
        parser.error("--output and --wheel are required")
    args.output.mkdir(parents=True, exist_ok=False)
    env = environment(args.wheel)
    if (env["python_flint"], env["FLINT"]) != (spec["backend"]["python_flint"], spec["backend"]["flint"]):
        raise RuntimeError("backend version differs from frozen specification")
    save(args.output/"ENVIRONMENT.json", env)
    start = time.monotonic()
    results = []
    for job in spec["jobs"]:
        remaining = spec["limits"]["global_wall_seconds"] - (time.monotonic()-start)
        if remaining <= 0:
            result = {"status": "INCONCLUSIVE", "reason": "GLOBAL_BUDGET", "job": job}
        else:
            try:
                proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--worker", job["id"]],
                                      capture_output=True, text=True, timeout=min(remaining, spec["limits"]["job_wall_seconds"]))
                if proc.returncode:
                    result = {"status": "EXECUTION_ERROR", "job": job, "returncode": proc.returncode,
                              "stderr": proc.stderr[-4000:]}
                else:
                    result = json.loads(proc.stdout)
            except subprocess.TimeoutExpired:
                result = {"status": "INCONCLUSIVE", "reason": "WALL_BUDGET", "job": job}
        save(args.output/(job["id"]+".json"), result)
        results.append({"id": job["id"], "status": result["status"], "wall_seconds": result.get("wall_seconds")})
        print(job["id"], result["status"], result.get("wall_seconds"), flush=True)
        # A logic/backend defect stops immediately; don't treat later jobs as passed.
        if result["status"] == "EXECUTION_ERROR":
            break
    summary = {"spec_id": spec["id"], "jobs": results, "planned_jobs": len(spec["jobs"]),
               "completed_jobs": len(results), "passed_jobs": sum(x["status"] == "PASS" for x in results),
               "wall_seconds": time.monotonic()-start, "physical_evaluations": 0,
               "status": "PASS" if len(results) == len(spec["jobs"]) and all(x["status"] == "PASS" for x in results) else "NOT_PASSED"}
    save(args.output/"RESULTS.json", summary)
    sources = [HERE/"SPEC.json", HERE/"primitives.py", HERE/"run_calibration.py"]
    records = sources + sorted(args.output.glob("*.json"))
    save(args.output/"MANIFEST.json", {"schema": "sha256_manifest_v1", "files": [
        {"path": str(p.relative_to(HERE)), "sha256": digest(p), "bytes": p.stat().st_size} for p in records]})
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
