# Our v052 — lower-pair preparation birth

[self-tested] The lower-pair birth passes in both engines at N4/N6. Each window combines two-root continuation, opposite-charge stations, refined fold/nondegeneracy checks and positive full-chart lower-gap searches on the other side. All four B=−0.25 lower-root pairs join the retained v044 start-state roots within 1e−6.

| engine / geometry | N | birth B | near-open lower gap (meV) | B=−0.10 lower gap (meV) | v044 root join |
|---|---:|---:|---:|---:|---:|
| bm_lab / linear | 4 | -0.2196650929 | 0.05134580 | 3.93729050 | 3.53e-15 |
| bm_lab / linear | 6 | -0.2196785111 | 0.05133879 | 3.93745156 | 1.91e-15 |
| ref_lab / exact | 4 | -0.2196698944 | 0.05134715 | 3.93751728 | 1.90e-15 |
| ref_lab / exact | 6 | -0.2196833132 | 0.05134014 | 3.93767834 | 3.47e-15 |

N6−N4 parameter shifts: bm_lab: -1.34e-05; ref_lab: -1.34e-05. These are discrete cutoff shifts, not error bounds against infinite cutoff. Charge-station mesh fallbacks: 0.

## Evidence and scope

Four windows contain 36 root-state records, eight charge measurements (all OPPOSITE) and eight open-side full-chart station searches, each on 18/24 meshes. Charges are measured at the first and last root state, not all 36 records. The joins establish same-state momenta; they do not establish a historical frame-orientation join.

The forward preparation route decreases B from 0 to −0.25 at A=0.2,T=0,phi=0,ratio=0.8. The discovery scan followed the known pair backward: two roots at −0.22, unresolved at −0.21. That failure was a bracket signal only. The accepted event locations come from a bounded fold solve with rank-one refinement, nonzero null curvature and transverse parameter slope, resolved roots on one side and searched positive lower gaps on the other.

The gap is index 2 in the eight-band harness, between the lower remote band and the first flat band. A positive lower gap does not mean the original flat-pair gap opens. This differs from v051's extra-flat-pair events: there the original pair persisted in the same gap and required a local-domain gate; here the full-chart lower-gap searches are positive on the open side. The older local records and their scope are unchanged.

All runs use explicit lab_nn_full and constant w0,w1, eps=0.003, theta=1.05 degrees. BM retains linear reciprocal geometry/cutoff_tol=1e−6; TBG retains exact geometry/cutoff_tol=1e−9. Hamiltonian source bytes are unchanged. Scientific sources and v044 anchors were frozen before the decisive runs; both N4 windows passed before N6 started. No shared conceptual error or physical-bilayer validation is ruled out by the two engines and shared measurement harness.

## Validation and limits

31 gate/join tests pass this batch: ten inherited bounded-domain tests, five ledger tests, seven anchor-join tests and nine lower-event publication tests. The original supplied regression suite was not rerun against unchanged Hamiltonians; its earlier 31-test result remains historical and is not counted here.

Full-chart searches are finite numerical evidence, not rigorous global lower bounds, exhaustive inventories or a proof of behavior between parameter stations. Existing seed failures remain triage signals, not topology verdicts. No established campaign label was changed. The remaining numerical coverage tasks are the original-flat-pair preparation replay with parameter-frame transport and a frame/root join into v044, followed by the separate lower unlink collision. These root-window results do not substitute for either task. Recipient consumption is [unconfirmed].
