---
from: D-bh-dress
to: orch
type: request
needs_reply_by: none
refs: [run:D-20261126-055249-505b079, run:D-20261126-055502-fbb1bec, run:D-20261124-172725-2f426b6, run:D-20261124-172745-72472ed]
---
Track D's G2 package is assembled and asks for its fresh-context verifier and then the gate review
(decision 0016 item 4).

State (batch 25, lead session; g2long/JOURNAL.md entries 25-27; stage/REVIEW-wave3.md sections 23-24):
- q0010 FNQ (N/4, D-20261124-172725-2f426b6, 1.90 card-hours) and q0011 FL16 (M/16,
  D-20261124-172745-72472ed, 3.66 card-hours) closed by nrpic-run finish; every prediction made for them
  holds (Q1-Q3, XQ; L1-L5). Only unpredicted failure: D3 at N/4 after ~220 M (no bound in criterion G).
- Item C2 read with conv3 D-20261126-055249-505b079: particle number N/4, N, 4N ordered at all four named
  times, window scatter ratio 1.9-3.1 (N^-1/2 noise gives 2); mesh of the growth M/8 and M/16 agree in
  Delta M to <= 4.4e-4 (3.6e-4 to 1.3e-5 with own-mesh controls), M/4 labelled outside the regime (ruling
  0039 item 4), no order claimed; null-test mesh leg two members, no order (ruling 0041 item 4).
- Horizon numbers: all from runs made without <fastflow> diagnostics, rechecked by the signature
  (D-20261125-160142-b1c51b5, D-20261126-055208-4e0fd0e: no failed search after 20 M).
- Note v3 (note/main.pdf, 24 pages; section V, ledger part 11; schematics on core-v0.7), build
  D-20261126-055502-fbb1bec; checker --compile clean.
- nrpic-stage verify D-bh-dress G2 --no-checksums: PASS; report: FAIL only for C17 (no VERIFIER.md yet).

Requests:
1. Send the fresh-context G2 verifier (artefacts: stage/G2/CHECKLIST.md, EVIDENCE.md, OPEN.md, LADDER.md,
   rerun_plan.json, rerun_g2.py, note/; not the conclusions), then the gate review.
2. The full-checksum verify pass (--full, hours over ~300 GB of card outputs) before the review: run by
   the next D session or by the orchestrator, as you prefer; no D card job is queued or running.
3. No card time is asked for G2. G3's first card item (core's excision guard test, ah_exc_max_growth = 8,
   with diagnostics = true) waits for core's judgement of q0049.
