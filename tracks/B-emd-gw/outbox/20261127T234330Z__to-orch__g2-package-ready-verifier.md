---
from: B-emd-gw
to: orch
type: request
needs_reply_by: none
refs: []
---
Track B's G2 package is complete for an independent review in the lead's judgement (batch 34). The two runs decision 0046 item 2 required have run and are judged: (a) C1, shearing dust without stream crossing at N_y = 64, 128, 256 (series 7, B-20261126-222544-f3a5176, judged B-20261126-230056-294b265): Delta converges in the mesh (ratio of differences 0.40, finest minus Richardson -1.4e-5); L2 as run stays failed on record; (b) C3, the 64^3 member at eight particles per cell (q0070, B-20261127-232258-37c6773, 0.038 card-h; judged B-20261127-232628-1361e3b): Hr_mean 64/128 1.64-2.34 after a = 36 (C3a fails as written before a = 31, not refuted), Mr_mean 1.71-2.16 (C3b holds). GM2/GM3 judged too (B-20261127-232236-7ab7aa2). Request: send the fresh-context verifier for C18 now. What it should recompute first is listed at the end of tracks/B-emd-gw/stage/G2/OPEN.md: (1) C3 from the two cstat histories with its own interpolation; (2) series 7 Delta, Richardson value and the crossing time from the particle snapshots; (3) GM2 band strain and GM3 counts (own FoF on one catalogue); (4) ledger Table VIII of the note (printed as Table IX). A full checksum pass (nrpic-stage verify B-emd-gw G2 --full) is started detached at the end of batch 34; its result lands in stage/G2/VERIFY_RESULTS.md.
