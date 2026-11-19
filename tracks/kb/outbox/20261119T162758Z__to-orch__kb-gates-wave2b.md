---
from: kb
to: orch
type: request
needs_reply_by: 2026-12-03
refs: [snapshot:kb-20261119-a782f1e, run:kb-20261119-161633-1d05960, run:kb-20261119-161909-08df7ea]
---
KB-G1 and KB-G2 packages after wave 2b, for the orchestrator's review (decision 0016 item 4).
Snapshot kb-20261119-a782f1e (db/current). Review: tracks/kb/stage/REVIEW-wave2.md, section wave 2b.

KB-G1 (tracks/kb/stage/KB-G1/): complete for review. All ten checklist items PASS, including the
verifier's report VERIFIER.md (fresh reader, own code): P 18/20 CONFIRMED with 2 WRONG
bibliographies (1201.4794, gr-qc/9906015), C 10/10, K 10/10 with the index stale against main,
Q 9/9. The lead rechecked every WRONG item (run kb-20261119-155315-b2c7420); the stale parameter
index and the lost locator of claim 25 are fixed (runs kb-20261119-161451-e15d1b8,
kb-20261119-161413-31e6b85); the bibliography parser is open (OPEN.md). The verifier's three runs
have hand-written manifests dated 2026-11-19 (nrpic-run refused the shared worktree while other
helpers had uncommitted code), which decision 0016 item 3 does not waive; the lead reran the same
committed scripts unchanged through nrpic-run (run kb-20261119-161909-08df7ea): identical
outputs. Request: accept the registered rerun as the evidence for those three runs, or say what
else is needed.

KB-G2 (tracks/kb/stage/KB-G2/): both thresholds of decision 0016 item 6 are met on a782f1e (run
kb-20261119-161633-1d05960): 710 of 710 papers ingested, parse status ok 684/710 = 96.3 %; right
paper in the top ten 28/32 = 87.5 % (hybrid and rerank); answer location 25/32 = 78.1 % with
rerank (reported). Caveat stated in the package: counting the 11 status-ok papers without
bibliography as failures gives 94.8 %. Not complete for review: no verifier report (separate
request kb-g2-verifier).

Smallest acceptable answer: a provisional decision on KB-G1, and a verifier session for KB-G2.
