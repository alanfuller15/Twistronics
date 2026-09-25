# R05 source-binding repair

R05 closes the R04 canonical-descriptor provenance failure. The frozen source
snapshot excludes generated interpreter artifacts, and both recursive and
explicit source binding now refuse `__pycache__`, `.pyc`, and `.pyo` inputs.

Compilation and tests run with bytecode generation disabled or against a
disposable tree. The published source inventory, retained evidence, and final
canonical descriptor must therefore be reconstructable from the same exact Git
commit.

This round concerns controller mechanics only. G04, G16, and G17 remain
`NOT_RUN` until a matching Astra and Claude review reaches
`PREPACKAGE_ACCEPTED`. No private v079p bytes or scientific workloads execute.
