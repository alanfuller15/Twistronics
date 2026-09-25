# S0aa: intrinsic path-content digest binding

Parent `a540997569ace3a10506433d2b1f640959a52c79`. Follows the completed S0z audit. Synthetic interface evidence only; physical S1–S4 and v078 remain outside this packet.

## Why this packet exists

S0z correctly pinned the retained files in `SPEC.json`, but its internal contract helper still accepted already-parsed objects together with caller-supplied digests. A caller could consistently change the in-memory path, its declared derivatives, and its pathwise matrix derivatives while supplying the old digest. The frozen run stayed sound because its files were pinned, but the object-to-digest boundary was not intrinsic.

S0aa moves digest computation inside the checked boundary. The accepted contract entry point takes three file paths, reads their exact bytes, parses those same bytes, computes the assembly and path SHA-256 values internally, and only then derives the contract. Callers no longer supply a digest alongside a separately mutable object.

## Retained control

The new mutation changes the affine path consistently from

    gamma(t) = (t,t/2)

to

    gamma(t) = (t/2,t/4),

and changes `gamma1` and the `H1` diagonal consistently. The window artifact deliberately retains the original path digest. The file-backed entry point recomputes the changed path digest and refuses with `PATH_ARTIFACT_HASH_MISMATCH`.

The independent verifier repeats this control against the frozen source copy. It does not trust only the retained result summary.

All prior S0z exact derivations remain unchanged: the retained path still gives `(H1,H2,H3)=(1,0,0)`, the common contour remains `(c,rho,g,r,d)=(0,1/3,3,5/3,4/3)`, and `(K,K1,K2)=(15/16,45/32,1485/256)`.

## Refusal coverage

Thirty-one executed mutations include all thirty S0z refusals plus the consistent path-content change under the old digest. The packet retains zero physical evaluations.

## Evidence limits

S0aa hardens a provenance boundary over one synthetic diagonal affine family and one affine path. It does not certify graphene assembly, physical spectral windows, an accepted S1 partition, inertia or pivot evidence, a physical or non-affine path, projector motion, transport, seam derivatives, the composed physical error budget, topology, cutoff agreement, or v078. The result remains `DECLARED_UNEXECUTED` and ineligible for physical transport.

