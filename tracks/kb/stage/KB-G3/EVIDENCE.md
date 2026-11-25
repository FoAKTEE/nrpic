# KB-G3 evidence (owner kb; lead, wave 3 batch 15, 2026-11-25; first version batch 13)

Gate (brief 12.10, line 1458): every statement in the evidence queue that bears on G1 of the six
tracks has been processed. Reading of the gate: SCOPE.md. Database for every number below:
snapshot `kb-data/db/kb-20261125-2f97258.sqlite` (sha256 2f97258c...; db/current from
2026-11-25 03:45 UTC; run kb-20261125-033718-3405697), 762 papers, 881 claims. The batch-13
state (snapshot kb-20261124-9872d21, 864 claims) is in git history of this file.

## State of the queue (run kb-20261125-034227-58fc4e0, own SQL; figure lead_b15/figures/fig_g3_queue.png, read)

"Processed" = the claim carries an event verify, refute, annotate, relocate, check, supersede,
supersedes or withdraw.

| Track | Claims | to_verify | to_verify processed | Other labels |
|---|---|---|---|---|
| A-emd-pbh | 174 | 1 | 1 | fulltext 166, judgement 2, refuted 5 |
| B-emd-gw | 81 | 0 | - | fulltext 53, abstract 5, judgement 12, refuted 11 |
| C-sidm | 114 | 0 | - | fulltext 102, judgement 9, refuted 3 |
| D-bh-dress | 101 | 8 | 8 | fulltext 82, judgement 9, background 1, refuted 1 |
| E-stoch-inf | 7 | 0 | - | judgement 7 |
| F-hills | 90 | 2 | 2 | fulltext 84, judgement 2, refuted 2 |
| core | 152 | 3 | 3 | fulltext 144, judgement 2, refuted 3 |
| brief | 114 | 17 | 12 | fulltext 47, abstract 13, judgement 20, background 6, refuted 11 |
| kb | 48 | 0 | - | fulltext 8, abstract 2, judgement 14, refuted 24 |

Statuses (all 881): located 471, checked 268, unlocated 70, refuted 35, superseded 22, partial 12,
withdrawn 3. "Refuted" labels include the 22 superseded and 3 withdrawn claims.

## Criterion C1 (gate): met

- Every to_verify claim of A, D, F and core carries a processing event (batch 13 and earlier).
- Brief seeds: the five without a processing event are 806, 807, 810, 811, 812, which decision
  0035 item 5 rules do not bear on G1 of any track. 803 is answered by claim 869 and 805 is
  annotated with the tracks' derivations (package claims3; OPEN.md O1, O2). Unprocessed claims
  bearing on G1: none.
- Fragments (O3): 20 named fragments closed (13 superseded by 870-881, 4 pointed to siblings, 3
  withdrawn). Text-correction tool (O5): `kb claim supersede`, `kb claim withdraw`.
- Package claims3 checked by the lead from the artefacts: REVIEW.md -> REVIEW-wave3.md, section
  "kb lead batch 15" (ledger matches the database; no claim outside the ledger changed after the
  repair; sample rate recomputed; five claims read at their sources; one tool defect fixed).

## Known limit that the gate does not close (OPEN.md O7)

Claims labelled as supported by a pipeline step, never read against their own wording: 573
before claims3, 543 unread after it. Sample of 30 (seed 20261125): 26 right as worded, 86.7 %
(CP 95 %: 69.3-96.2 %); stratum-weighted 86.5 % (s.e. 6.1 %). This is the rate of the mixed class.
The machine-located claims alone (label set by the automatic seeder; claims3's WA, the second
verifier's M) are right as worded 28 of 35 times, 80.0 % (CP 95 %: 63.1-91.6 %): claims3's 18/22
pooled with the second verifier's 10/13 (VERIFIER2.md section 2; the pool is not independent of
claims3). The rest of the weak class: 20/21, 95.2 % (76.2-99.9 %). The second verifier's
stratum-weighted estimate for its W (529 claims) is 80.6 % (s.e. 9.3 %), about 86 claims not right
as worded (34-179). Expected not right as worded among the 543 by this package's own sample:
about 70 (21-167) [JUDGEMENT: extrapolation]. The errors found were all cuts or
mislabels of the automatic seeder (WA). Runs kb-20261125-021654-6799dfd (draw),
kb-20261125-023841-d9343e6 (rates), recomputed in kb-20261125-033503-dfc398e. The package's
class query today counts 548 because it does not exclude its own five annotations (308, 467,
662, 673, 720): run kb-20261125-033530-5a1ac43.

## Independent verifiers (decision 0016 item 4; 0036 item 3)

1. `VERIFIER.md` (fresh helper session of batch 11, predictions committed in 2e05c967, seed
   20261124): 54/60 sampled claims right (95 % CP 79.5-96.2 %); population estimate 93.8 % (s.e.
   3.5 %); refutations 10/11 brief seeds and 19/24 printed defects confirmed; parse rate 714/744 =
   95.97 % by its own definition. Runs kb-20261124-130442-e69c2e8, kb-20261124-130450-578a535,
   kb-20261124-132849-3ebad97, kb-20261124-132859-5f1a7f3.
2. `VERIFIER2.md` (fresh helper session of batch 15, predictions and seed 20261126 committed in
   d4741a70b, snapshot kb-20261125-2f97258): item 1, 60 of 61 claims written or changed since the
   first verifier right (781 not); item 2, a new stratified sample of 40: checked by a person 12/14
   (85.7 %), machine-located 10/13 (76.9 %), rest of the weak class 12/13 (92.3 %); item 3, C1-C7
   met, with reservations on C1 and C5; recommendation pass with reservations. Runs
   kb-20261125-041310-20371de, kb-20261125-042218-7b7af60, kb-20261125-042240-6c19d72,
   kb-20261125-042327-f947572 (failed before any draw: kb-20261125-041256-d4741a7).

## Gate signed; reservations closed in batch 17

KB-G3 is SIGNED, pass with reservations (coord/GATES.md, 2026-11-24, commit 8fdb954efa; decision
0037 item 1). In batch 17 the lead superseded the seven claims of VERIFIER2.md (781, 223, 574,
553, 145, 169, 462 -> 882-888, 553's successor labelled judgement) and processed the twelve
abstract-labelled claims without a locator (773 -> 889, 774 -> 890, 712 -> 891 located in the full
text; 709, 844 checked against metadata records; 710, 711, 715 withdrawn as headings; 706, 794,
795, 796 -> 892-895 to_verify as repository and tool statements): plan
tracks/kb/lead_b17/plans/P1_verifier2.json, dry run kb-20261125-124157-537e458, run
kb-20261125-124220-191593e (others' hash unchanged), check kb-20261125-124251-3855127 (none of the
twelve left; live to_verify +4; figure fig_a2_labels.png, read). OPEN.md O7-O9.

## Runs since batch 13 (all scouting, processors, 0 card-hours)

| Run | What | Result |
|---|---|---|
| kb-20261125-021654-6799dfd | claims3: weak-class draw | 30 of 573, seed 20261125 |
| kb-20261125-023523-40c916a | claims3: store search for seed 803 | 20 papers |
| kb-20261125-023539-1da3331 ... 023542-f420d93 | claims3: writes W1-W5 | 72 ledger rows; all write predictions held |
| kb-20261125-023614-440dff2 | claims3: downloads rows of 0707.4654, 1006.1632 | 765 -> 763 rows; files unchanged |
| kb-20261125-023841-d9343e6 | claims3: ledger, rates, figures | 26/30 |
| kb-20261125-023915-2822f6f | claims3: pointer 803/790 -> 869 | 2 events |
| kb-20261125-033503-dfc398e | lead: review of claims3 | ledger matches; 5 claims outside the ledger changed (defect) |
| kb-20261125-033530-5a1ac43 | lead: weak class today | 548 = 543 + 5 annotated |
| kb-20261125-033655-43ee7ce, 033703-3bd4386 | lead: restore checked_by/at of 289, 313, 430, 624, 862 | dry run, then 5 rows restored |
| kb-20261125-033703-a1be27a | lead: review repeated | 67 changed, all in the ledger |
| kb-20261125-033718-3405697 | verify-downloads, QA, snapshot | exit 1 only gr-qc/9412071; C1 762/762; parse 737/762 = 96.7 %; golden hybrid 28/32; snapshot kb-20261125-2f97258 |
| kb-20261125-034227-58fc4e0 | lead: C1 evidence | unprocessed bearing on G1: none |
