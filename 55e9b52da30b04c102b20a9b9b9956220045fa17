# Development checks

Before the numerical plan was written, an initial pytest collection attempt for the fold/search unit tests stopped because test_search.py reads NUMERICAL_PLAN.json. No numerical worker had started and no test-pass claim was made. The selected tests were rerun after the plan was created. The complete source/input/runtime-bound publication test run is separate.

A standalone recovery-unit-test collection attempt then exposed a missing parent import path in that test file. The test path was corrected before the recovery numerical plan or worker run. This was a test assembly error, not numerical evidence.

The first complete publication run (20260921T041740Z_556ccee2) had 119 passes and one failed mutation test. Its open_gradient fixture replaced the gradient at the lower-left corner with large positive components; those imply descent out of the feasible square and correctly project to zero, so they do not violate constrained stationarity. The fixture now uses a feasible descent direction at any boundary point. The numerical code and records were not changed. The failed run, prior publication plan and exact old test source are retained. A new publication plan and complete bound run follow the fixture correction.
