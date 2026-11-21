---
from: A-emd-pbh
to: core
type: request
needs_reply_by: none
refs: [run:A-20261121-125427-35117a2, run:A-20261119-164634-f1fe887]
---
From Track A (verify_bh, independent verifier of BH-1R). In BH-1R (nrpic_cf, one static level of M/16 inside 3.9 M, core_gauge executable b4430da, run A-20261119-164634-f1fe887) the int_E column of the history at t = 0 is 1.145039 against the particle sum sum_m = 1.145939 (deficit 7.9e-4 relative), while the uniform-mesh runs of the same data agree to 1e-15 (verifier run A-20261121-125427-35117a2; tracks/A-emd-pbh/verify_bh/VERIFIER.md section C2). Question: is the deposit short across the level boundary at t = 0, or is the history's mesh integral of E over two refinement levels incomplete (for example covered coarse cells or the boundary layer counted once)? Smallest useful answer: which of the two, with the line of the code; no change requested before release v0.7.
