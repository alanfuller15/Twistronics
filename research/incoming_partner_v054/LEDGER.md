# Campaign ledger — v048

Generated from accepted summaries and current raw records. The numerical rows are self-tested; finite sampling is not a completeness proof. Exact source paths and SHA256 values are in LEDGER_SOURCES.json. The incoming partner v046 and our v046 are separate contributions.

## Earlier accepted records

| Record | Engine | N | Scope | Recorded states / event parameters |
|---|---|---:|---|---|
| our v044 | bm_lab (linear) | 4 | early braid/deepening/unlinking legs | 37 states; center B=-0.2901737962 |
| our v044 | bm_lab (linear) | 6 | early braid/deepening/unlinking legs | 37 states; center B=-0.2901702643 |
| our v044 | ref_lab (exact) | 4 | early braid/deepening/unlinking legs | 37 states; center B=-0.2901753967 |
| our v044 | ref_lab (exact) | 6 | early braid/deepening/unlinking legs | 37 states; center B=-0.2901718633 |
| our v043 | bm_lab | 4 | pre_ann | 19 states; labels=OPPOSITE |
| our v043 | bm_lab | 6 | pre_ann | 19 states; labels=OPPOSITE |
| our v043 | ref_lab | 4 | pre_ann | 19 states; labels=OPPOSITE |
| our v043 | ref_lab | 6 | pre_ann | 19 states; labels=OPPOSITE |
| our v043 | bm_lab | 4 | post_ann | 21 states; labels=SAME |
| our v043 | bm_lab | 6 | post_ann | 21 states; labels=SAME |
| our v043 | ref_lab | 4 | post_ann | 21 states; labels=SAME |
| our v043 | ref_lab | 6 | post_ann | 21 states; labels=SAME |
| v042 | bm_lab | 4 | braid 2 / first annihilation | ratio=0.9905387373; T=-0.7133735361 |
| v042 | bm_lab | 6 | braid 2 / first annihilation | ratio=0.9907661313; T=-0.7133010132 |
| v042 | ref_lab | 4 | braid 2 / first annihilation | ratio=0.9905413982; T=-0.7133867358 |
| v042 | ref_lab | 6 | braid 2 / first annihilation | ratio=0.9907687909; T=-0.7133142594 |
| our v046 | bm_lab | 4 | cleanup / upper collision | 17 cleanup states; ratio=1.0206603966 |
| our v046 | bm_lab | 6 | cleanup / upper collision | 17 cleanup states; ratio=1.0194793307 |
| our v046 | ref_lab | 4 | cleanup / upper collision | 17 cleanup states; ratio=1.0206664403 |
| our v046 | ref_lab | 6 | cleanup / upper collision | 17 cleanup states; ratio=1.0194854044 |

## New late-event windows

| Case | Engine | Geometry | N | Critical parameter | Root states | Charge stations | Just-open gap (meV) |
|---|---|---|---:|---:|---:|---:|---:|
| flat_birth | bm_lab | linear | 4 | 1.0529704128 | 9 | 2 | 0.11070210 |
| final_ann | bm_lab | linear | 4 | -0.3177787436 | 9 | 2 | 0.16271008 |
| flat_birth | bm_lab | linear | 6 | 1.0520969426 | 9 | 2 | 0.11131288 |
| final_ann | bm_lab | linear | 6 | -0.3171450604 | 9 | 2 | 0.16319312 |
| flat_birth | ref_lab | exact | 4 | 1.0529719222 | 9 | 2 | 0.11070061 |
| final_ann | ref_lab | exact | 4 | -0.3177799654 | 9 | 2 | 0.16271014 |
| flat_birth | ref_lab | exact | 6 | 1.0520984612 | 9 | 2 | 0.11131142 |
| final_ann | ref_lab | exact | 6 | -0.3171462891 | 9 | 2 | 0.16319321 |

## Sampled gapped connections

| Engine | N | States | Smallest sampled gap (meV) | Minimum cycle seam overlap | Anchor joins |
|---|---:|---:|---:|---:|---|
| bm_lab | 4 | 8 | 0.05672344 | 0.99914146 | bridge, endpoint |
| bm_lab | 6 | 8 | 0.05655949 | 0.99999962 | bridge, endpoint |
| ref_lab | 4 | 8 | 0.05672335 | 0.99914147 | bridge, endpoint |
| ref_lab | 6 | 8 | 0.05655940 | 0.99999962 | bridge, endpoint |

Per-band/group w1, reproduced at every newly sampled gapped state:

| Band/group | k1 | k2 |
|---|---:|---:|
| lower_remote | 0 | 0 |
| flat1 | 1 | 0 |
| flat2 | 0 | 0 |
| upper_remote | 0 | 0 |
| flat_pair | 1 | 0 |

## Coverage qualifications

- post-braid-2 late windows and gapped checkpoint joins: sampled and accepted.
- preparation A/B legs: anchors and candidate brackets only; continuous replay open.
- separate lower unlink collision: not measured here.
- N>6 path / global N8 minima / microscopic bilayer validation: not established.

Historical summaries are retained as historical accepted evidence; this generator does not rerun every earlier computation. Preparation anchors are not promoted to accepted fold windows. Model and scope annotations involve reviewed metadata; they are not numerical discoveries made by the formatter.
