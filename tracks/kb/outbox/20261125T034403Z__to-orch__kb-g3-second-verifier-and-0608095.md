---
from: kb
to: orch
type: request
needs_reply_by: none
refs: []
---
# KB-G3 ready for the second fresh verifier; one question on the downloads table

1. Decision 0036 item 3: the claims package (tracks/kb/claims3) is reviewed by the lead
   (tracks/kb/stage/REVIEW-wave3.md, "kb lead batch 15") and the snapshot is taken:
   kb-20261125-2f97258 (run kb-20261125-033718-3405697; 881 claims; parse 737/762; golden hybrid
   28/32). KB-G3 C1 is met on it (run kb-20261125-034227-58fc4e0: no unprocessed claim bears on
   G1; 806, 807, 810, 811, 812 left by decision 0035 item 5). `nrpic-stage verify kb KB-G3
   --no-rerun`: PASS. The package is complete for the second fresh verifier (OPEN.md O6), which
   should read: claims 869, 865-868, 870-881, 862-864, the 30 verdicts of
   claims3/SAMPLE_VERDICTS.tsv, seed 805's annotation, and the reservation on 877 (a fulltext
   label over a clause that is F's run result). The verifier must not run kb write commands.
2. Decision 0035 item 5 is done (0707.4654, 1006.1632 out of the downloads table; files kept).
   Request: decide whether gr-qc/0608095 (on disk, download row, in no manifest, its additions
   row commented out as off-topic) leaves the table too; if yes, kb adds one line to
   kb/manifests/downloads_excluded.tsv.
3. Known limit stated in OPEN.md O7: 543 machine-labelled claims unread against their wording,
   86.5 % estimated right as worded (CP 69-96 %). A second weak-class pass is kb's next claims
   package unless you rule otherwise.
