# Contributing to Twistronics

Contributions are welcome when they preserve the project's evidence boundaries
and make review easier.

## Before proposing a change

1. Read [Start here](docs/START_HERE.md) and [current status](docs/STATUS.md).
2. Identify whether the change concerns presentation, software acceptance,
   synthetic certification readiness, or a physical calculation.
3. Work from an exact commit and name every retained artifact used.
4. Keep historical evidence immutable. Add a new bounded packet or correction
   rather than silently replacing an earlier result.

## Evidence expectations

A research or review contribution should record:

- exact source commit and input artifact digests;
- declared parameters, domain, conventions, and finite work limits;
- commands, dependency/runtime identity, and exit outcomes;
- machine-readable results and relevant negative controls;
- failures and inconclusive outcomes, not only successful cases;
- a claim ceiling and a direct statement of what remains open.

Software tests, acceptance gates, independent reviews, and physical
certificates are different evidence types. Label them accordingly.

## Documentation expectations

- Define project-local terms or link to the [glossary](docs/GLOSSARY.md).
- Give newcomers an accessible summary before implementation detail.
- Link draft work using an exact commit when reproducibility matters.
- Update `README.md`, `docs/STATUS.md`, and `research/README.md` together when
  an accepted milestone changes the public learning path.
- Preserve the distinction between observed finite-model behavior and physical
  or experimental interpretation.

## Licensing note

This public repository currently has no top-level license declaration. Public
visibility alone does not grant reuse rights. A license should be chosen by the
repository owner as a separate explicit project decision.
