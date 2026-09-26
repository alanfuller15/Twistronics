# S0ab: single-snapshot triple-artifact binding

Parent `92d45b8fe4d6493a3a8a467d700a92db08b5a7c1`. Follows the completed S0aa audit in Claude source comment `5811206714` and Codex disposition `5811232147`. Synthetic interface evidence only; physical S1–S4 and v078 remain outside this packet.

## Why this packet exists

S0aa closed the stale path-object/digest route for the accepted entry point. Its contract still omitted the window-evidence byte digest, and its worker separately reread the artifacts for contract derivation, mutation baselines, and summary hashes. The frozen single-process run was sound, but the complete three-artifact identity was not carried by the contract and a narrow time-of-check/time-of-use surface remained.

S0ab reads `SPEC.json`, the window evidence, the assembly, and the path exactly once into an immutable byte snapshot. Contract derivation, retained summary hashes, and refusal controls consume that snapshot. The contract records the binding-spec digest and the complete window/assembly/path digest triple. No accepted helper takes already-parsed objects paired with caller-supplied digests.

## Retained control

The S0aa mutation remains: it changes the affine path consistently from

    gamma(t) = (t,t/2)

to

    gamma(t) = (t/2,t/4),

and changes `gamma1` and the `H1` diagonal consistently. The window artifact deliberately retains the original path digest. The file-backed entry point recomputes the changed path digest and refuses with `PATH_ARTIFACT_HASH_MISMATCH`.

The new S0ab mutation reverses the order of the four exact window cells. This preserves the exact cover and all derived numerical outputs, but changes the window artifact bytes while the binding specification retains the original digest. The accepted entry refuses with `WINDOW_ARTIFACT_HASH_MISMATCH`.

The independent verifier repeats both stale-content controls against the frozen source copy. It does not trust only the retained result summary.

All prior S0z exact derivations remain unchanged: the retained path still gives `(H1,H2,H3)=(1,0,0)`, the common contour remains `(c,rho,g,r,d)=(0,1/3,3,5/3,4/3)`, and `(K,K1,K2)=(15/16,45/32,1485/256)`.

## Refusal coverage

Thirty-two executed mutations include all thirty S0z refusals, the consistent path-content change under the old digest, and the semantically equivalent window-content change under the old digest. The packet retains zero physical evaluations.

## Evidence limits

S0ab hardens a provenance boundary over one synthetic diagonal affine family and one affine path. It does not certify graphene assembly, physical spectral windows, an accepted S1 partition, inertia or pivot evidence, a physical or non-affine path, projector motion, transport, seam derivatives, the composed physical error budget, topology, cutoff agreement, or v078. The result remains `DECLARED_UNEXECUTED` and ineligible for physical transport.
