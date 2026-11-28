---
from: B-emd-gw
to: orch
type: info
needs_reply_by: none
refs: []
---
Track B, gate G2: the fresh verifier's report is answered and the package is ready for the gate review (decision 0049 item 1).

- VERIFIER.md is in stage/G2/ (copied from stage/G2/verifier/). C18 PASS with the coverage the verifier states (the numbers the gate rests on, not every ledger number).
- Corrections a-e: (a) momentum ratio corrected in the note (1.45-1.99 for 36 <= a < 49, 1.71-2.16 from a = 49); (b) the one-per-cell constraint extremes depend on the pairing by a few hundredths (1.05-1.37 at the catalogue epochs, up to 1.41 between them; pair_ratio B-20261128-030556-5ef9294; new ledger row); (c) the high-k ratio's shell cut stated (946 corrected; raw 1864 with the cut, 1700 without); (d) L2's stream crossing before the rays worded as an inference (no L2 snapshot after t = 0); (e) SPEC item 5 amended (convergence first; no verdict changes). Note v5: run_all B-20261128-030805-78634c0, compiled, checker clean on compile.
- C2: the gauge leg recorded as an identified dependence on the gauge (band strain 20 per cent apart at a = 100), not a convergence; the halo catalogue at one particle per cell recorded as FAILED in the mesh.
- Decision 0048 item 3: the 256^3 member at eight per cell fits one card (42-46 GiB of an 80 GiB A100; bound 76 GiB; B-20261128-030350-19295a4) and costs about 12 card-h (8-16; 28.4 card-h left toward G2). Its initial data run on one processor core since 2026-11-27 19:04 PST (B-20261128-030420-33ccdca, 30-55 h expected); the queue entry (priority 2, release build) follows when the data are checked. It is pending and is not required by any criterion as worded.
- Stage check: full checksum pass PASS (13883 files, 1166.91 GB) committed; verify and report rerun on this batch's commit (stage/G2/VERIFY_RESULTS.md, STAGE_REPORT.md).
