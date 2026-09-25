#!/usr/bin/env python3
"""Summarize retained exploratory point spectra; never assemble or solve a model."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ENDPOINTS = ("lower.left", "lower.right", "upper.left", "upper.right")
CLAIM = (
    "Approximate finite-cutoff-a point spectra only. Positive sampled gaps and "
    "window margins do not certify cell interiors, gap lower bounds, coverage, "
    "seams, topology, or physical gap closure. Historical certified coverage "
    "remains 29663/65536. Refinement was selected from coarse observations; "
    "the combined samples are not a uniform or independent validation set."
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def number(value):
    return format(float(Fraction(value)), ".12g")


def point_descriptor(row):
    point = row["point"]
    return {"cell": point["cell"], "fractional_center": point["center"]}


def extrema(rows, getter):
    key = lambda row: (Fraction(getter(row)), row["point"]["cell"]["depth"],
                       row["point"]["cell"]["ix"], row["point"]["cell"]["iy"])
    lower, upper = min(rows, key=key), max(rows, key=key)
    return {
        "minimum_meV": str(Fraction(getter(lower))),
        "minimum_at": point_descriptor(lower),
        "maximum_meV": str(Fraction(getter(upper))),
        "maximum_at": point_descriptor(upper),
    }


def statistics(rows):
    if not rows:
        return {"samples": 0, "gaps": {}, "local_window_widths": {},
                "fixed_parent_endpoints": {}, "fixed_parent_failure_signatures": {},
                "all_fixed_endpoints_expected": 0, "sampled_common_upper_gap": None}
    result = {"samples": len(rows), "gaps": {}, "local_window_widths": {},
              "fixed_parent_endpoints": {}}
    for side in ("lower", "upper"):
        result["gaps"][side] = extrema(rows, lambda r: r["diagnostic"]["local_gap_estimates_meV"][side])
        result["local_window_widths"][side] = extrema(
            rows, lambda r: r["diagnostic"]["local_window_proposals"][side]["width_meV"])
    signatures = Counter()
    for endpoint in ENDPOINTS:
        counts, equalities, mismatches = Counter(), 0, 0
        for row in rows:
            value = row["diagnostic"]["fixed_parent_endpoint_diagnostics"][endpoint]
            counts[value["numerical_negative_count"]] += 1
            equalities += value["numerical_equality_count"] != 0
            mismatches += (value["numerical_negative_count"] != value["expected_negative"]
                           or value["numerical_equality_count"] != 0)
        result["fixed_parent_endpoints"][endpoint] = {
            "numerical_negative_count_distribution": {str(k): v for k, v in sorted(counts.items())},
            "points_with_equality": equalities, "mismatching_points": mismatches,
            "signed_bracketing_margin": extrema(
                rows, lambda r: r["diagnostic"]["fixed_parent_endpoint_diagnostics"][endpoint]["minimum_margin_meV"]),
        }
    for row in rows:
        failed = []
        for endpoint in ENDPOINTS:
            value = row["diagnostic"]["fixed_parent_endpoint_diagnostics"][endpoint]
            if (value["numerical_negative_count"] != value["expected_negative"]
                    or value["numerical_equality_count"] != 0):
                failed.append(endpoint)
        signatures["+".join(failed) if failed else "all_expected"] += 1
    result["fixed_parent_failure_signatures"] = dict(sorted(signatures.items()))
    result["all_fixed_endpoints_expected"] = signatures["all_expected"]
    lower = max(rows, key=lambda r: Fraction(r["diagnostic"]["band_energies_meV"]["98"]))
    upper = min(rows, key=lambda r: Fraction(r["diagnostic"]["band_energies_meV"]["99"]))
    lower_value = Fraction(lower["diagnostic"]["band_energies_meV"]["98"])
    upper_value = Fraction(upper["diagnostic"]["band_energies_meV"]["99"])
    result["sampled_common_upper_gap"] = {
        "maximum_lower_edge_meV": str(lower_value), "maximum_lower_edge_at": point_descriptor(lower),
        "minimum_upper_edge_meV": str(upper_value), "minimum_upper_edge_at": point_descriptor(upper),
        "signed_intersection_width_meV": str(upper_value - lower_value),
        "interpretation": "Approximate intersection over sampled point gaps only; a negative width is not a certified impossibility result.",
    }
    minimum_row = min(rows, key=lambda r: Fraction(r["diagnostic"]["local_gap_estimates_meV"]["upper"]))
    minimum_cell = minimum_row["point"]["cell"]
    same_depth_cells = {(r["point"]["cell"]["ix"], r["point"]["cell"]["iy"])
                        for r in rows if r["point"]["cell"]["depth"] == minimum_cell["depth"]}
    absent_neighbors = [[minimum_cell["ix"] + dx, minimum_cell["iy"] + dy]
                        for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy)
                        and (minimum_cell["ix"] + dx, minimum_cell["iy"] + dy) not in same_depth_cells]
    result["minimum_upper_gap_sample_neighborhood"] = {
        "cell": minimum_cell, "all_eight_neighbor_cells_sampled": not absent_neighbors,
        "absent_same_depth_neighbor_cells": absent_neighbors,
        "interpretation": "An interior sampled-cell neighborhood does not locate or bound the continuum minimum; sampled centers are never the cell boundaries.",
    }
    return result


def load_run(path, expected_packet):
    """Check retained packet identity and integrity without numerical imports."""
    names = {"EVENTS.ndjson", "RESULTS.json", "SUPERVISOR_RECEIPT.json", "MANIFEST.json"}
    if {p.name for p in path.iterdir()} != names:
        raise ValueError("RUN_FILE_MEMBERSHIP")
    if any(not (path / name).is_file() or (path / name).is_symlink() for name in names):
        raise ValueError("RUN_FILE_TYPE")
    contents = {name: (path / name).read_bytes() for name in names}
    manifest = json.loads(contents["MANIFEST.json"])
    entries = manifest["entries"]
    if len(entries) != 3 or {e["path"] for e in entries} != names - {"MANIFEST.json"}:
        raise ValueError("MANIFEST_MEMBERSHIP")
    for entry in entries:
        data = contents[entry["path"]]
        if entry["bytes"] != len(data) or entry["sha256"] != sha256(data):
            raise ValueError("MANIFEST_HASH")
    result, receipt = (json.loads(contents[name]) for name in ("RESULTS.json", "SUPERVISOR_RECEIPT.json"))
    if (result["packet_id"] != expected_packet or result["interval_factorizations"] != 0
            or result["status"] not in ("EXPLORATORY_COMPLETE", "EXPLORATORY_TIMEOUT", "EXECUTION_ERROR")
            or result["receipt_sha256"] != sha256(contents["SUPERVISOR_RECEIPT.json"])
            or result["raw_sha256"] != sha256(contents["EVENTS.ndjson"])
            or result["raw_bytes"] != len(contents["EVENTS.ndjson"])
            or receipt["durable_log_sha256"] != result["raw_sha256"]
            or receipt["durable_log_bytes"] != result["raw_bytes"]):
        raise ValueError("RESULT_RECEIPT_LOG_BINDING")
    rows = result["points"]
    if (len(rows) != result["points_completed"] or len(rows) > result["eigensolver_starts"]
            or result["eigensolver_starts"] > 64
            or (result["status"] == "EXPLORATORY_COMPLETE" and len(rows) != 64)):
        raise ValueError("POINT_COUNT")
    identities = []
    for row in rows:
        point, diagnostic = row["point"], row["diagnostic"]
        cell = point["cell"]
        identities.append((cell["depth"], cell["ix"], cell["iy"]))
        expected_center = [Fraction(2 * cell[axis] + 1, 2 ** (cell["depth"] + 1)) for axis in ("ix", "iy")]
        if list(map(Fraction, point["center"])) != expected_center:
            raise ValueError("CENTER_CELL_BINDING")
        energies = {int(k): Fraction(v) for k, v in diagnostic["band_energies_meV"].items()}
        for side, left, right, expected_count in (("lower", 96, 97, 97), ("upper", 98, 99, 99)):
            gap = energies[right] - energies[left]
            proposal = diagnostic["local_window_proposals"][side]
            if (gap < 0 or gap != Fraction(diagnostic["local_gap_estimates_meV"][side])
                    or Fraction(proposal["width_meV"]) != gap / 4
                    or Fraction(proposal["left"]) != energies[left] + 3 * gap / 8
                    or Fraction(proposal["right"]) != energies[left] + 5 * gap / 8
                    or proposal["expected_negative"] != expected_count):
                raise ValueError("LOCAL_DIAGNOSTIC_ARITHMETIC")
            for endpoint in ("left", "right"):
                value = diagnostic["fixed_parent_endpoint_diagnostics"][side + "." + endpoint]
                shift = Fraction(value["shift"])
                if (value["expected_negative"] != expected_count
                        or Fraction(value["minimum_margin_meV"]) != min(shift - energies[left], energies[right] - shift)):
                    raise ValueError("FIXED_DIAGNOSTIC_ARITHMETIC")
    if len(identities) != len(set(identities)):
        raise ValueError("DUPLICATE_SAMPLE")
    return rows, {
        "packet_id": expected_packet, "status": result["status"],
        "eigensolver_starts": result["eigensolver_starts"], "points_completed": len(rows),
        "interval_factorizations": result["interval_factorizations"],
        "uncompleted_points": result["uncompleted_points"],
        "pending_eigensolver_point": result["pending_eigensolver_point"],
        "elapsed_seconds": receipt["reaped_at"] - receipt["monotonic_start"],
        "termination_reason": receipt["termination_reason"], "worker_exit_code": receipt["worker_exit_code"],
        "post_reap_group_empty": receipt["post_reap_group_empty"],
        "sigterm_sent": receipt["sigterm_sent_at"] is not None,
        "sigkill_sent": receipt["sigkill_sent_at"] is not None,
        "runtime_provenance_digest": result["runtime_provenance_digest"],
        "source_bindings_sha256": result["source_bindings_sha256"],
        "input_files": {name: {"bytes": len(data), "sha256": sha256(data)} for name, data in sorted(contents.items())},
        "statistics": statistics(rows),
    }


def coordinate_text(descriptor):
    cell = descriptor["cell"]
    x, y = descriptor["fractional_center"]
    return f"d{cell['depth']} ({cell['ix']},{cell['iy']}); x={x}, y={y}"


def report(summary):
    lines = ["# Retained momentum-space point mapping", "", CLAIM, "",
             "Both batches use the frozen finite-cutoff-a CASE (196 dimensions), with fractional momentum coordinates k=xG1+yG2. Values below are approximate binary64 point diagnostics in meV. Source/runtime and record replay are performed by each scout's check-only verifier; this summary checks the retained file bindings and derives statistics without model evaluation.", "",
             "## Completed work", "",
             "| Batch | Status | Completed / started | LDL calls | Elapsed (s) | Exit / receipt |",
             "|---|---|---:|---:|---:|---|"]
    for label, batch in summary["batches"].items():
        lines.append(f"| {label} | `{batch['status']}` | {batch['points_completed']} / {batch['eigensolver_starts']} | {batch['interval_factorizations']} | {batch['elapsed_seconds']:.3f} | {batch['worker_exit_code']} / {batch['termination_reason']}; group empty={batch['post_reap_group_empty']} |")
    lines += ["", "Each batch had a maximum of 64 eigensolver starts, one worker/native thread, 2 GiB address space, a 120/150-second watchdog, and no retry. A completed point is not a certified tile.", "",
              "## Sampled gap and window statistics", "",
              "| Batch | Lower gap range (meV) | Upper gap range (meV) | Local upper window width range (meV) | Fixed parent endpoints all expected |",
              "|---|---:|---:|---:|---:|"]
    for label, batch in summary["batches"].items():
        s = batch["statistics"]
        if not s["samples"]:
            lines.append(f"| {label} | unknown | unknown | unknown | 0 / 0 |")
            continue
        def span(value):
            return f"{number(value['minimum_meV'])}–{number(value['maximum_meV'])}"
        lines.append(f"| {label} | {span(s['gaps']['lower'])} | {span(s['gaps']['upper'])} | {span(s['local_window_widths']['upper'])} | {s['all_fixed_endpoints_expected']} / {s['samples']} |")
    for label, batch in summary["batches"].items():
        s = batch["statistics"]
        if s["samples"]:
            minimum = s["gaps"]["upper"]
            lines += ["", f"{label} minimum upper adjacent-gap estimate: **{number(minimum['minimum_meV'])} meV**, at {coordinate_text(minimum['minimum_at'])}."]
            neighborhood = s["minimum_upper_gap_sample_neighborhood"]
            if neighborhood["all_eight_neighbor_cells_sampled"]:
                lines += [f"Its cell has all eight same-depth neighboring cells sampled, so the sampled minimum is interior to the selected cell union rather than on its outer sample row or column. This does not establish a continuum minimum between samples."]
            else:
                lines += [f"At least one neighboring same-depth cell was not sampled; the minimum is adjacent to the boundary of the sampled cell union. The center itself is not a geometric boundary point."]
    lines += ["", "## Fixed parent windows", "",
              "Mismatches count a wrong approximate strict negative count or equality at an endpoint. They are not certified inertia failures.", "",
              "| Batch | Lower left | Lower right | Upper left | Upper right |",
              "|---|---:|---:|---:|---:|"]
    for label, batch in summary["batches"].items():
        endpoints = batch["statistics"]["fixed_parent_endpoints"]
        lines.append("| " + label + " | " + " | ".join(str(endpoints[e]["mismatching_points"]) if e in endpoints else "unknown" for e in ENDPOINTS) + " |")
    for label, stats in [(label, b["statistics"]) for label, b in summary["batches"].items()] + [("Combined samples", summary["combined_statistics"])]:
        gap = stats["sampled_common_upper_gap"]
        if gap:
            lines += ["", f"{label}: max sampled E98={number(gap['maximum_lower_edge_meV'])} meV; min sampled E99={number(gap['minimum_upper_edge_meV'])} meV; signed common upper-gap intersection width={number(gap['signed_intersection_width_meV'])} meV. This is an approximate sample comparison, not a certificate of existence or impossibility."]
    lines += ["", "## Interpretation", "",
              "The refined batch samples four cells selected by the smallest coarse upper-gap estimates; it is targeted follow-up, not a uniformly finer map of the entire parent. The fixed parent upper windows disagree with the expected approximate counts across this refined patch, while locally proposed windows remain positive at the sampled centers. This supports using frozen local-window proposals in a separately bounded interval batch instead of investing in the same fixed-parent-window comparison. The much narrower local windows may still be inconclusive on closed cells. No sampled minimum supplies a lower bound between samples, and a smaller refined minimum does not prove physical gap closure.", "",
              "The plot displays sample locations only; orange rings identify each batch's sampled minimum. The axes are dimensionless parent-relative fractional coordinates u=512(x−351/512), v=512(y−368/512). Neither marker area nor the empty background represents certified momentum-space coverage.", "",
              "![Approximate upper gap at retained sample locations](upper_gap_samples.png)", "",
              "Exact rational statistics, per-batch file hashes, source/runtime bindings, and receipt summaries are retained in `SUMMARY.json`. The SVG and PNG derive only from those retained point observations.", ""]
    return "\n".join(lines)


def plot(coarse, refined, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm, Normalize

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "svg.hashsalt": "momentum-mapping-summary-001"})
    rows = coarse + refined
    if not rows:
        raise ValueError("NO_SAMPLE_POINTS_FOR_PLOT")
    values = [float(Fraction(r["diagnostic"]["local_gap_estimates_meV"]["upper"])) for r in rows]
    low, high = min(values), max(values)
    norm = LogNorm(vmin=low, vmax=high) if 0 < low < high else Normalize(vmin=low, vmax=high if high > low else low + 1)
    fig, axes = plt.subplots(1, 2, figsize=(11.3, 6.1), sharex=True, sharey=True, layout="constrained")
    artist = None
    for ax, samples, title in zip(axes, (coarse, refined), ("Coarse: 8 × 8 centers", "Refined: four selected parent cells")):
        xs = [float(512 * (Fraction(r["point"]["center"][0]) - Fraction(351, 512))) for r in samples]
        ys = [float(512 * (Fraction(r["point"]["center"][1]) - Fraction(368, 512))) for r in samples]
        gaps = [float(Fraction(r["diagnostic"]["local_gap_estimates_meV"]["upper"])) for r in samples]
        artist = ax.scatter(xs, ys, c=gaps, norm=norm, cmap="viridis", s=42,
                            edgecolors="#202020", linewidths=0.45, zorder=3)
        ax.set(xlim=(0, 1), ylim=(0, 1), aspect="equal",
               xlabel="Parent-relative u = 512(x − 351/512)", title=f"{title}\n{len(samples)} retained sample points")
        ax.grid(alpha=0.2)
        if samples:
            idx = min(range(len(samples)), key=lambda i: gaps[i])
            ax.scatter([xs[idx]], [ys[idx]], s=145, marker="o", facecolors="none",
                       edgecolors="#d14900", linewidths=1.5, zorder=4)
            ax.text(0.02, 0.98, f"Min estimate: {gaps[idx]:.6g} meV", transform=ax.transAxes,
                    ha="left", va="top", fontsize=9, bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none"})
    axes[0].set_ylabel("Parent-relative v = 512(y − 368/512)")
    cbar = fig.colorbar(artist, ax=axes, shrink=0.79, pad=0.025)
    cbar.set_label("Approximate upper adjacent gap (meV)" + ("; log color scale" if low > 0 and low < high else ""))
    fig.suptitle("Finite-cutoff-a momentum samples: exploratory, not certified coverage", fontsize=12)
    fig.savefig(output / "upper_gap_samples.png", dpi=180, bbox_inches="tight", pad_inches=0.15,
                metadata={"Software": "momentum_mapping_summary_001"})
    fig.savefig(output / "upper_gap_samples.svg", bbox_inches="tight", pad_inches=0.15,
                metadata={"Date": None, "Creator": "momentum_mapping_summary_001"})
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coarse", type=Path, default=ROOT / "research/benchmarks/momentum_mapping_scout_001/RUN")
    parser.add_argument("--refined", type=Path, default=ROOT / "research/benchmarks/momentum_mapping_scout_002/RUN")
    parser.add_argument("--output", type=Path, default=HERE / "OUTPUT")
    args = parser.parse_args()
    coarse, coarse_summary = load_run(args.coarse, "MOMENTUM-MAPPING-SCOUT-001")
    refined, refined_summary = load_run(args.refined, "MOMENTUM-MAPPING-SCOUT-002")
    all_centers = [tuple(r["point"]["center"]) for r in coarse + refined]
    if len(all_centers) != len(set(all_centers)):
        raise ValueError("DUPLICATE_POINT_ACROSS_BATCHES")
    summary = {"schema_version": 1, "summary_id": "MOMENTUM-MAPPING-SUMMARY-001", "claim": CLAIM,
               "batches": {"Coarse 001": coarse_summary, "Refined 002": refined_summary},
               "combined_statistics": statistics(coarse + refined)}
    args.output.mkdir(parents=True, exist_ok=True)
    expected = {"SUMMARY.json", "REPORT.md", "upper_gap_samples.svg", "upper_gap_samples.png"}
    if not {p.name for p in args.output.iterdir()} <= expected:
        raise ValueError("UNEXPECTED_SUMMARY_OUTPUT_FILES")
    (args.output / "SUMMARY.json").write_bytes(json_bytes(summary))
    (args.output / "REPORT.md").write_text(report(summary))
    plot(coarse, refined, args.output)
    print(json.dumps({"status": "RETAINED_DATA_SUMMARIZED", "samples": len(coarse + refined),
                      "physical_calls": 0, "outputs": sorted(expected)}))


if __name__ == "__main__":
    main()
