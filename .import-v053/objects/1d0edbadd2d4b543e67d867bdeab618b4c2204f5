# Original-flat-pair preparation: frozen frame replay

The route is A:0→0.2 at B=0, followed by B:0→−0.25 at A=0.2. T=0, phi=0, ratio=0.8, eps=0.003 and theta=1.05 degrees are held fixed. Both engines explicitly use lab_nn_full and constant tunnelling amplitudes. BM retains linear reciprocal geometry/cutoff_tol=1e−6; TBG retains exact geometry/cutoff_tol=1e−9.

An eleven-state BM N4 pilot uses 4 A intervals and 6 B intervals. It is exploratory, saved separately and excluded from accepted counts. The decisive protocol uses 8 A intervals and 10 B intervals: 19 states including the baseline, with no duplicated leg junction. Four engine/cutoff cases give 76 states. Both N4 cases qualify before N6. Sources and JSON/NPZ anchors are hashed before primary runs; Hamiltonian engines are unchanged from v052.

At every primary state:

1. Continue both original flat roots (gap index 3), require residual <1e−6 meV, separation >0.001 and individual jumps <0.06, and retain fractional coordinates in [0,1]².
2. Obtain the isolated real two-plane at each node. Carry each frame from the previous state by polar alignment in the declared Fourier-coefficient basis. Basis labels must remain identical along these A/B legs; transport overlap must exceed 0.1 and measured norm loss must not exceed 0.02.
3. Independently carry a coarse frame sequence using every second fine state within each leg. Compare fine/coarse orientation determinants at all nine coarse endpoints per case; each must exceed 0.99. This checks the orientation used for charges, not a unique accumulated SO(2) rotation.
4. Compare the two nodes spatially using 128/256 transport meshes with located minima of both selected-group external gaps. Require isolation >1e−5 meV, overlap >0.1 and fine/coarse orientation determinant >0.99.
5. Measure both node charges in their carried frames using radius min(0.004,separation/8), same-radius meshes 64/128 and half-radius mesh 128. Charges must agree under mesh/radius changes. Only unresolved loop phase steps permit the recorded 256/512/512 or 1024/2048/2048 fallback. A separately measured charge in the spatially transported endpoint frame must transform consistently with the recorded orientation. Spatial labels are observations, not forced to an assumed value.

The full route requires each individual carried charge to remain constant. Final roots are matched, including possible node permutation, to v044 step_000 within 1e−6. The anchor frame archive must match its recorded digest; basis labels must match; both endpoint two-planes must overlap above 0.999999 and the overlap determinant magnitude must exceed 0.999999. A node's charge must transform by the sign of that determinant. The two frame signs must agree, allowing one common overall reflection but rejecting a change of relative orientation. The spatial endpoint label must also match v044.

The older per-state anchor does not explicitly record cutoff_tol. Its compatibility relies on the previously reviewed historical defaults, the identical basis labels and the directly measured root/plane join; the present tolerance is explicit in every new state. This does not claim entire Hamiltonian equality from a few matching points.

Each accepted state commits JSON plus fine/coarse NPZ frames through an atomic directory rename. Restore validates contiguous steps, protocol and array digest/finiteness. The BM N4 primary replay pauses after three committed states, records six file hashes, then resumes in a new process. It must finish without changing those files. This is a stop/resume exercise, not a separate bitwise comparison to an uninterrupted replay.

The flat pair ceases to be globally isolated after the remote contacts already measured in prior batches. Only the sampled node planes and comparison paths are asserted isolated here; no Euler class is continued through that region. All parameter/spatial checks are finite numerical evidence, not analytic interval guarantees or physical-bilayer validation.
