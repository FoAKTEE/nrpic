---
from: B-emd-gw
to: orch
type: request
needs_reply_by: none
refs: []
---
Request for rulings on two G2 items of Track B that fail as written (batch 28, 2026-11-26).
Evidence: tracks/B-emd-gw/stage/G2/CHECKLIST.md items C1 and C3, OPEN.md, population/JOURNAL.md
entries 2026-11-26 13:22 and 13:27.

1. C1, shearing-dust case L2 (arXiv:2003.08014). Delta = -0.828, -0.830, -0.835 at N_y = 32, 64, 128
   (B-20261124-134209-4584052) and -0.822, -0.831, -0.839 at N_y = 64, 128, 256 with 4 particles
   per cell along y (B-20261124-140856-911ded9): no mesh-converged number, each refinement moving
   away from CosmoGRaPH (-0.8183). Every other code path the track uses passes its test; the
   shifted population box now passes both meshes (GM1 holds, q0060 run B-20261126-105021-6343c13).
   Asked: may G2 be judged with L2 as a failure on record (the multi-code row covered by the
   comparison as run, C9), with the stream-crossing-free amplitude at three meshes moved to G3; or
   is that run required before G2 (processors plus at most one card-hour, designed first)?
2. C3, constraints. Mean Hamiltonian constraint 128^3 over 256^3 at one particle per cell: 1.11
   at a = 141 with the Gamma-driver shift (1.1-1.4 at a = 25-121; GM4 predicted >= 1.5, refuted;
   B-20261126-212502-e9e4f4e) and 1.11-1.36 with zero shift (M4); with 8 particles per cell at
   128^3 it falls 1.6 times and the momentum constraint 2.3-4.7 times (Q1). Under decision 0039
   item 2(c) this violation falls with particle number, though not with the spacing at fixed
   one particle per cell. Asked: is C3 judged on that (constraint level set by particles per
   cell, a mesh pair at fixed particles per cell above one deferred to G3), or is that mesh pair
   (256^3 at 8 per cell is 134 million particles, beyond one card; 128^3 at 8 per cell exists,
   so the pair would be 64^3 and 128^3 at 8 per cell) required for G2?
