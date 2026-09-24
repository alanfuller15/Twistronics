# R04 controller-mechanics candidate

R04 replaces the unpublished R03 attempt. Its source root is the frozen
`source/` snapshot, while `evidence/` contains operation-specific reports and
receipts produced from that snapshot.

The snapshot approval precedes evidence generation and binds every consumed
source byte except the approval record itself. Receipts include the actual
consumed source inventory and operation-specific timing/dispatch metadata.

This round reviews acceptance mechanics only. G04, G16, and G17 remain
`NOT_RUN` until a two-review `PREPACKAGE_ACCEPTED` state enters atomic staged
packaging. No private v079p bytes or scientific workloads are executed.
