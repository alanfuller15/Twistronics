"""ledger.py (v047; status revised v050): a FORMATTER for the historical team summaries (v042, v043, v044, v046) and my
provisional anchor JSON. It does not validate acceptance status, schema completeness, model tags or source hashes.
The canonical ledger from v048 onward is the team generator (ledger_guard.py -> LEDGER.md, with COVERAGE.json and
LEDGER_SOURCES.json); this script is kept for reproducing the earlier tables only. No number is typed by hand. Usage: python ledger.py <v042 summary.json> <v043 SUMMARY.json> <v044 SUMMARY.json> [anchors_prep_N4.json]"""
import json, sys
import numpy as np
v042, v043, v044 = [json.load(open(p)) for p in sys.argv[1:4]]
anch = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else None
v046 = json.load(open(sys.argv[5])) if len(sys.argv) > 5 else None
final = json.load(open(sys.argv[6])) if len(sys.argv) > 6 else None
L = ["# Historical ledger tables (formatter output of ledger.py; superseded by the team LEDGER.md from v048)", "",
     "Numbers are read from the recorded JSON summaries named on the command line; acceptance status, schema and hashes are not validated by this script. Model tag as recorded in each summary.", ""]
L += ["## v044 (team): braid 1 → deepening → un-linking", "", "| engine | geometry | N | states | center crossing B* | shifted-path B* | final label | min param overlap | min spatial overlap |", "|---|---|---:|---:|---:|---:|---|---:|---:|"]
for c in v044['cases']:
    L.append(f"| {c['engine']} | {c['geometry']} | {c['N']} | {c['states']} | {c['center_crossing']:.10f} | {c['shifted_crossing']:.10f} | {c['final_label']} | {c['min_parameter_overlap']:.6f} | {c['min_spatial_overlap']:.6f} |")
L += ["", f"Cross-engine: " + "; ".join(f"N={x['N']}: max node diff {x['max_tracked_node_difference']:.2e}, labels agree {x['labels_agree']}, ref−bm center root {x['center_root_ref_minus_bm']:.2e}" for x in v044['comparisons']), ""]
L += ["## v043 (team): v028 → annihilation window; post-transfer → braid-2 window", "", "| case | engine | N | states | labels | min pair sep | min param overlap | max basis loss | min spatial overlap | min spatial ext. gap (meV) |", "|---|---|---:|---:|---|---:|---:|---:|---:|---:|"]
for c in v043['cases']:
    labs = c['labels'] if isinstance(c['labels'], str) else "/".join(sorted(set(map(str, c['labels'] if isinstance(c['labels'], list) else c['labels'].values()))))
    L.append(f"| {c['case']} | {c['engine']} | {c['N']} | {c['states']} | {labs} | {c['min_pair_separation']:.4f} | {c['min_parameter_overlap']:.6f} | {c['max_basis_norm_loss']:.2e} | {c['min_spatial_overlap']:.6f} | {c['min_spatial_external_gap']:.5f} |")
L += ["", "## v042: braid-2 window; first-annihilation window; gapped checkpoints", "", "| engine | N | braid-2 crossing ratio | first-annihilation B_tau |", "|---|---:|---:|---:|"]
for eng, byN in v042['engines'].items():
    for N, r in byN.items():
        b = r.get('braid_crossing', r.get('braid2_crossing', '')); a = r.get('annihilation', r.get('annihilation_T', ''))
        L.append(f"| {eng} | {N} | {b if isinstance(b,str) else f'{b:.9f}'} | {a if isinstance(a,str) else f'{a:.9f}'} |")
L += ["", "Cross-engine: " + "; ".join(f"N={N}: braid diff {x['braid_crossing_difference']:.2e}, annihilation diff {x['annihilation_difference']:.2e}, max gapped-checkpoint diff {x['max_gapped_checkpoint_difference']:.2e} meV, labels agree {x['labels_agree']}" for N, x in v042['cross_engine'].items()), ""]
if v046:
    L += ["## v046 (team): post-braid-2 cleanup and upper collision", "",
          f"cleanup states {v046['cleanup_states']}, root-continuation states {v046['root_continuation_states']}, fold windows {v046['upper_fold_windows']}; cleanup labels {v046['cleanup_labels']}; loop fallbacks cleanup/fold {v046['cleanup_loop_fallbacks']}/{v046['fold_loop_fallbacks']}; min param overlap {v046['min_parameter_overlap']:.6f}, min spatial overlap {v046['min_spatial_overlap']:.6f}, min sampled path gap {v046['min_sampled_path_gap']:.5f} meV, max node jump {v046['max_node_jump']:.2e}", "",
          "| engine | N | upper-annihilation ratio | node | cleanup join | just-open gap | far-open gap |", "|---|---:|---:|---|---:|---:|---:|"]
    for f in v046['folds']:
        L.append(f"| {f['engine']} | {f['N']} | {f['ratio']:.10f} | {f['node']} | {f['cleanup_join']:.2e} | {f['just_open_gap']:.5f} | {f['far_open_gap']:.5f} |")
    L += ["", "Endpoint local gaps (team three-start probe):", "", "| gap | N6 | N8 | difference | minimiser shift |", "|---|---:|---:|---:|---:|"]
    for g in v046['endpoint_local_gaps']:
        L.append(f"| {g['gap']} | {g['N6']:.6f} | {g['N8']:.6f} | {g['difference']:.2e} | {g['minimizer_shift']:.2e} |")
    L += ["", "Sampled tunnelling sensitivity (team gate): " + "; ".join(f"kappa {x['kappa']}: remote gap {x['remote_gap']:.4f} meV ({x['percent_change']:+.3f}%), {x['label']}" for x in v046['sensitivity']), ""]
if anch:
    L += ["## v047 anchors (mine): preparation leg A: 0 → 0.2 at B=T=0 (fixed-parameter, N=4)", "", "| A | flat pair label (bm / ref) | root diff | min remote gap (meV) | upper nodes (bm) |", "|---:|---|---:|---:|---|"]
    for r in anch:
        L.append(f"| {r['A']:.2f} | {r['bm_label']} / {r['ref_label']} | {r['max_root_diff']:.1e} | {r['bm_min_remote']:.4f} | {len(r['bm_upper_nodes'])} |")
if final:
    L += ["## v049 anchors (mine): flat-birth and final-annihilation windows (fixed-parameter, N=4, bm exact / ref)", "", "| window | ratio | A | bm roots | sep | label | ref root diff |", "|---|---:|---:|---|---:|---|---:|"]
    for r in final:
        rd = max(np.linalg.norm(np.array(x)-np.array(y)) for x, y in zip(r['bm_roots'], r['ref_roots']))
        L.append(f"| {r['window']} | {r['ratio']:.3f} | {r['A']:+.2f} | {tuple(round(v,5) for v in r['bm_roots'][0])} {tuple(round(v,5) for v in r['bm_roots'][1])} | {r['sep']:.4f} | {r['label']} | {rd:.1e} |")
    L.append("")
L += ["", "Coverage status is NOT computed here (v050): see the team COVERAGE.json. Preparation rows above are provisional candidates (brackets / extrapolations), not gate-accepted events."]
open('LEDGER.md', 'w').write("\n".join(L)); print("\n".join(L))
