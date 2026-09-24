# R06 published-recipe candidate

R06 closes R05's descriptor-input provenance failure. The exact stable inputs
are retained in `RECONSTRUCTION.json`; the exact reviewed commit is supplied
by the GitHub handoff because a commit cannot contain its own SHA.

Before handoff, the coordinator must reconstruct the round from the exact
published Git bytes and run `reconstruct-handoff` with the resolved commit and
proposed descriptor. A mismatch closes the candidate.

This round covers controller and package acceptance mechanics only. G04, G16,
and G17 remain `NOT_RUN` until two matching reviews reach
`PREPACKAGE_ACCEPTED`. No private v079p bytes or scientific workloads are
executed.
