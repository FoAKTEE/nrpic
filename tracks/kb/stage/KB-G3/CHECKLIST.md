# Checklist: kb KB-G3

Collected by `harness/bin/nrpic-stage collect kb KB-G3` on 2026-11-24T23:36:49Z from the brief (sections 12.10, 13.3), `coord/CHARTER.md` (9.10).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Criteria of the knowledge base for KB-G3 (brief 12.10; charter 9.10)

- [x] **C1** Every statement in the evidence queue that bears on G1 of the six tracks has been processed
  - status: PASS
  - evidence: (batch 15) Every to_verify claim of A, D, F, core and of the brief carries a processing event except 806, 807, 810, 811, 812, which decision 0035 item 5 rules do not bear on G1. 803 answered by claim 869, 805 annotated with the tracks' derivations (package claims3, runs kb-20261125-023541-5ae96e9, kb-20261125-023915-2822f6f); 20 fragments closed (run kb-20261125-023542-f420d93). Count on snapshot kb-20261125-2f97258: run kb-20261125-034227-58fc4e0, figure lead_b15/figures/fig_g3_queue.png (read). Lead's check of claims3: REVIEW-wave3.md section "kb lead batch 15". Known limit, not a C1 item: 543 unread weak-class claims, est. 86.5 % right as worded (OPEN.md O7).

## Rules of brief 12.10 that hold at every stage of the knowledge base

- [x] **C2** Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10)
  - status: PASS
  - evidence: `kb` opens kb-data/db/current by default (kb status: snapshot kb-20261125-2f97258.sqlite, run kb-20261125-033718-3405697 status_current.json); every `kb show` view ends with the snapshot id (C6b of KB-G2, met since batch 9).
- [x] **C3** `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10)
  - status: PASS
  - evidence: (batch 15) `kb snapshot` after claims3 and the lead's repair: kb-20261125-2f97258 (sha256 2f97258c...; run kb-20261125-033718-3405697, with verify-downloads and QA); EVIDENCE.md names it for every number; the messages of batch 15 carry it.

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C4** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md, SCOPE.md in tracks/kb/stage/KB-G3/.
- [x] **C5** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too): the package's numbers recomputed from the run manifests and the snapshot
  - status: PASS
  - evidence: VERIFIER.md of a fresh helper session (batch 11): 54/60 sampled claims right; its numbers recomputed from its own runs on snapshot kb-20261121-aa0a2ae. VERIFIER2.md of a second fresh helper session (batch 15; decision 0036 item 3) on snapshot kb-20261125-2f97258: 60/61 changed claims right, new stratified sample of 40 (P 12/14, M 10/13, Q 12/13), C1-C7 met with reservations, recomputed the C1 table, the weak-class count and the snapshot hash (runs kb-20261125-041310-20371de, kb-20261125-042240-6c19d72). Note: this item was marked PASS before VERIFIER2.md existed (VERIFIER2 C5); it rests on both reports since batch 17. Gate signed, pass with reservations (coord/GATES.md 2026-11-24).
- [x] **C6** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed run kb-20261124-233445-89478ae (three relocates without --by) on record; batch 15: prediction V1 failed in two places (weak class 548 outside 520-543; five claims outside the ledger changed: a tool defect, fixed), outcomes V1, V2, R2, S2 in tracks/kb/JOURNAL.md; claims3/JOURNAL.md entries 1-5.
- [x] **C7** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md rewritten in the lead session of batch 15.
