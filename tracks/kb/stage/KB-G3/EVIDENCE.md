# KB-G3 evidence (owner kb; lead, wave 3 batch 13, 2026-11-24)

Gate (brief 12.10, line 1458): every statement in the evidence queue that bears on G1 of the six
tracks has been processed. Reading of the gate: SCOPE.md. Database for every number: snapshot
`kb-data/db/kb-20261124-9872d21.sqlite` (db/current from 2026-11-24 23:42 UTC; run
kb-20261124-233515-0ed31c7), 762 papers, 864 claims.

## State of the queue (snapshot kb-20261124-9872d21; own SQL; figure lead_b13/figures/fig_qa_claims.png, read)

| Track | Claims | to_verify | to_verify with a processing event | Other labels |
|---|---|---|---|---|
| A-emd-pbh | 170 | 1 | 1 | fulltext 167, judgement 2 |
| B-emd-gw | 73 | 0 | - | fulltext 61, judgement 12 |
| C-sidm | 113 | 0 | - | fulltext 104, judgement 9 |
| D-bh-dress | 101 | 8 | 8 | fulltext 82, judgement 9, background 1, refuted 1 (682) |
| E-stoch-inf | 7 | 0 | - | judgement 7 |
| F-hills | 89 | 2 | 2 | fulltext 85, judgement 2 |
| core | 150 | 4 | 4 | fulltext 145, judgement 1 |
| brief | 113 | 17 | 10 | fulltext 45, abstract 14, judgement 20, background 6, refuted 11 |
| kb | 48 | 0 | - | fulltext 8, abstract 2, judgement 14, refuted 24 |

Of the 697 fulltext claims, 233 are checked (a person read the passage) and the rest located by
machine; the verifier sampled both strata (17/18 and 17/18 right). Judgement claims are never
upgraded (brief 12.8).

## Criterion C1 (gate): met for the tracks' queues; not met for two brief seeds

- Tracks' queues (claims_tracks, 159 queue claims: 98 read, 19 kept with reasons, 42
  annotated; AUDIT.md 37/40 right): every to_verify claim of A, D, F and core now carries a
  processing event (this batch: 409, 447, 449, 450 verified, 452 annotated with claim 864).
- Brief seeds (claims_brief, 112 seeds and 48 defect claims; this batch 781, 804 verified,
  714, 809, 716, 798, 799, 808 annotated, 863 added): 7 to_verify seeds carry no event: 803 and
  805 bear on G1 of A, B, D, F (OPEN.md O1, O2); 806, 807, 810, 811, 812 do not [JUDGEMENT].
- Corrections of the verifier: 682 superseded by 862 (refuted as worded), 85 and 737 annotated.

## Independent verifier (decision 0016 item 4)

`VERIFIER.md` (fresh helper session of batch 11, predictions committed in 2e05c967 before the
draws, seed 20261124): 54/60 sampled claims right (95 % CP 79.5-96.2 %); population estimate
93.8 % (s.e. 3.5 %); refutations 10/11 brief seeds and 19/24 printed defects confirmed, none
wrong; code index 10/10 and 10/10; parse rate 714/744 = 95.97 % by its own definition. Its runs:
kb-20261124-130442-e69c2e8, kb-20261124-130450-578a535, kb-20261124-132849-3ebad97,
kb-20261124-132859-5f1a7f3; figures in verifier/figures (fig_sample.png read by the lead). The
verifier saw the state before this batch's corrections; a second verifier after O1-O3 is O6.

## Runs of this batch (all scouting, processors, 0 card-hours)

| Run | What | Result |
|---|---|---|
| kb-20261124-233445-89478ae | claims batch (lead_b13/scripts/apply_g3.sh) | 862-864 added; 682 refuted; 781, 804, 409, 447, 449, 450 verified; 714, 809, 452 annotated; FAILED on three relocates (missing --by) |
| kb-20261124-233504-c6530a6 | relocate 862-864 | 1, 3, 3 rows, all resolved |
| kb-20261124-233637-3d710a8 | annotate 716, 798, 799, 808 | 4 events |
| kb-20261124-233726-3b6e5b9 | annotate 85, 737 | 2 events |
| kb-20261124-233515-0ed31c7 | verify-downloads, QA, snapshot | exit 1 only gr-qc/9412071; C1 counts agree; parse 737/762 = 96.7 %; golden hybrid 28/32; snapshot kb-20261124-9872d21 |
| kb-20261124-234330-7f49a10 | QA figures | lead_b13/figures/fig_qa_{retrieval,claims,eqcount}.png (retrieval and claims read) |

Lead's review of the packages and of each verifier finding: `REVIEW.md` ->
`tracks/kb/stage/REVIEW-wave3.md`, section "kb lead batch 13".
