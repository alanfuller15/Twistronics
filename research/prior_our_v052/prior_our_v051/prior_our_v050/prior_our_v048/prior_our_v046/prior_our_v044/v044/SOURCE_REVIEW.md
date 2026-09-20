# Partner v043 reconciliation

The incoming package and our previous delivery both use the label v043.
They are separate contributions: the partner's v043 adopts our v042 and
changes the toolkit; our v043 measures two connecting routes. This v044
keeps both records and does not treat the partner's “connecting legs open”
statement as a reversal of the newer measured connections.

The on-disk archive contains 100 files plus one directory entry, including
20 numbered logs. The claimed 21-log count is off by one; v040 remains
represented by reference rather than a numbered file. Both standalone
attachments match their archive copies byte for byte.

| Claim or change | Finding | Disposition |
|---|---|---|
| Guard patch applied verbatim | Uploaded tbg_ref.py is byte-for-byte identical to our final v042 patched file. | Verified. Ten failure-injection and endpoint regression cases pass against the adopted file. |
| New exact reciprocal geometry | BM's new option changes the layer K and q/G construction. Historical linear Hamiltonians are unchanged bit for bit at the checked states. | Verified by source diff and full-operator checks, including nonzero A, B and T. |
| Two engines agree with matched geometry | Twenty-four complete matrix comparisons cover six states, N=4/6 and two momenta, including an unwrapped point. Maximum difference is about 1.4e-12 meV. | Supported for the declared options and checked states; not an unrestricted parameter-domain proof. |
| They differ only in their topological estimators | The cutoff padding still differs: BM 1e-6 versus TBG 1e-9 inverse Angstroms. At N=4, eps=0.003 and phi=15.843560625 degrees, exact geometry yields dimensions 196 versus 188. | Qualification required. The padding is another finite-truncation choice; the optional patch names it explicitly while preserving defaults. |
| Shared geometry API | BM accepts geometry='linear' or 'exact'; TBG still has fixed exact geometry and no geometry keyword. | Correct the API wording. Both kinetic choices remain explicit in the replay harness. |
| 29 tests | All 29 supplied tests pass. | Verified. The new positive-gap test alone does not establish failure behavior; the ten adopted guard regressions test that separately. |
| Short team note: bm_lab N6 annihilation root rounds to -0.71331 | The detailed table correctly gives -0.713301013 for BM and -0.713314259 for TBG. | Minor transcription correction: BM rounds to -0.71330; -0.71331 is TBG. No numerical conclusion changes. |

Review cutoff: archive inventory and byte comparison across all files; deep
review of the changed BM initialization/geometry path, the complete guard
diff, the updated tests and cross_exact.py. Unchanged legacy drivers were not
all reread or re-executed. This is an incremental source/numerical review,
not a new exhaustive dependency or CVE audit. Prior API warnings about old
drivers retain their previous status.

The new code adds no network access or external command execution. The
geometry script constructs models, evaluates eigenvalues and prints results.
The guard patch adds input/refinement checks and search seeds; it does not
alter the Hamiltonian or eigensolver. The supplied tests were executed only
after source review. Sources and diffs are retained under provenance/.

The cutoff witness is recorded in provenance/cutoff_boundary_witness.json
and reproduced by boundary_probe.py. Two reciprocal indices lie about 5e-7
inverse Angstroms beyond the nominal cutoff, between the two hardcoded
paddings. The exact-geometry agreement at the campaign checks remains
valid; the witness limits the broader assertion of identical finite models
for every strain direction. The optional fixes/ patch adds a shared named
cutoff_tol, retains both defaults and has eight targeted tests.

The tbg_ref module introduction also retains the obsolete (I-E) kinetic
description. Its executed lab_nn_full branch uses R^T[I+(1-beta)E] and the
crystal-frame gauge rotated back; the old formula is now the explicitly
named geom_wrong option. The code, not that introductory description,
governs these measurements.

The primary new paths retain bm_lab=linear and ref_lab=exact so each joins
the existing record under the same model. A separately labeled bm_exact
control checks the first-braid crossing roots. Exact-Hamiltonian agreement
does not independently verify two topological estimators: our path replays
use one common measurement harness. The partner's alternative estimator
implementations remain available but are not silently counted as additional
measurements in this batch.
