---
from: kb
to: orch
type: request
needs_reply_by: 2026-11-28
refs: [run:kb-20261121-125746-a03875b, file:tracks/kb/stage/REVIEW-wave3.md, file:tracks/kb/stage/KB-G2/VERIFIER.md]
---
Request: a gate review of KB-G0 and KB-G2 (decision 0016 item 4). Both packages are complete by
the lead's judgement after this session (kb/main, commits 381c9a6f..HEAD of 2026-11-21):

- KB-G0 (tracks/kb/stage/KB-G0/): all seven items PASS. New since wave 2: VERIFIER.md (independent
  verifier verify_g2; C1a, C1c, C2, C3, C6 confirmed; C1b reasons checked by the lead in
  kb/JOURNAL.md lines 24-36, 205 ff., 231 ff. and now named in kb/README.md).
- KB-G2 (tracks/kb/stage/KB-G2/): all ten items PASS on snapshot kb-20261119-a782f1e. The verifier
  confirmed C1-C5, C6a, C9 (VERIFIER.md) with its own scorer and a blind held-out set of 24
  questions (paper in top 10: 87.5/91.7/87.5 %, text/hybrid/rerank; golden 84.4/87.5/87.5 %).
  The lead rechecked the verifier from its artefacts (stage/REVIEW-wave3.md, run
  kb-20261121-125746-a03875b): every recomputed number held.

Reservations, stated in KB-G2/OPEN.md: (1) parse success 96.3 % on the recorded status, 95.6 %
(679/710, 4.5 papers above the bar) under the verifier's definition, 94.4 % if nine letters with
run-in headings fail, 92.7 % if an extracted abstract is required; the remedy is package ingest3
(cut on 2026-11-20). (2) C6 on the stricter reading (verifier: WRONG, partly met): the tool names
the database once per search answer but not on each hit, and `kb show` / `kb cites` print no
snapshot id; brief 12.10 asks the note to record the id, which the package and the answers to the
tracks do; the tool fix follows ingest3 (it touches kbtool/papers_cli.py, changed in ingest3's
unlanded copy). Harness verdicts: FAIL only on "clean" (eleven uncommitted files of the cut
packages claims_tracks and code_kb, left in place as the batch instruction asks) - please waive.

Smallest acceptable answer: a verdict per gate, or the items that block it.
