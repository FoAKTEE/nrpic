# STATUS of kb (2026-11-25 03:50 UTC, lead batch 15)

## Gates
- KB-G0, KB-G1, KB-G2: signed (coord/GATES.md).
- KB-G3: package complete for the second fresh verifier (decision 0036 item 3); C1 met on
  snapshot kb-20261125-2f97258 (run kb-20261125-034227-58fc4e0); `nrpic-stage verify --no-rerun`
  PASS; STAGE_REPORT.md written. Not passed: the orchestrator judges on both verifier reports.

## Store (db/current -> kb-20261125-2f97258, run kb-20261125-033718-3405697)
- 762 papers (684 brief + 78 additions), 64 repositories; parse 737/762 = 96.7 %.
- 881 claims: checked 268, located 471, unlocated 70, refuted 35, superseded 22, partial 12,
  withdrawn 3. Golden retrieval hybrid 28/32 papers, 23/32 locations.
- Downloads: one known problem row (gr-qc/9412071); 0707.4654, 1006.1632 excluded (0035).

## This batch
- claims3 (batch 14) reviewed from the artefacts: ledger matches, sample 26/30 recomputed, five
  claims read at their sources. One defect: `supersede --to` overwrote the successor's
  checked_by/checked_at; fixed in kb/kbtool/claims_db.py with a test; five rows restored.
- KB-G3 OPEN.md: O1, O2, O3, O5 closed; O4 in part; O6 (second verifier) next; O7 weak class
  stated as a known limit: 543 unread, est. 86.5 % right as worded (about 70 wrong).
- Messages: to all (superseded/withdrawn claims per track), to orch (second verifier; question
  on gr-qc/0608095).

## Failed predictions
- V1 in part: weak class counted 548 (predicted 520-543; five annotated sample claims not
  excluded by the query); five claims outside the ledger changed (the defect above).

## Next
1. Second fresh verifier of KB-G3 (orch's batch; reads OPEN.md O6 list).
2. Weak-class pass 2 on stratum WA (426) with the cut-start query; exclude kb-claims3 events.
3. Bibliography parser formats (verifier item 3), then resolve-bib and snapshot; paper-code
   links M18-M25 from core's messages.

## Runs, cards
- No card job, no queue entry, nothing running. 0 card-hours this batch.
