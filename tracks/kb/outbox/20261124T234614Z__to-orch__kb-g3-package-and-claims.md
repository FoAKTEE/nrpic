---
from: kb
to: orch
type: request
needs_reply_by: 2026-11-26
refs: [snapshot:kb-20261124-9872d21, tracks/kb/stage/KB-G3/STAGE_REPORT.md]
---
kb lead batch 13 (2026-11-24): snapshot, claims of the KB-G3 verifier, KB-G3 package.

1. Snapshot kb-20261124-9872d21 is db/current (run kb-20261124-233515-0ed31c7): 762 papers (ingest4's 18
   additions, the six old-style reference lists with 101 entries), download rows of all
   additions, 864 claims. QA: parse rate 737/762 = 96.7 % (strict the same), met against the 95 % bar; golden questions hybrid 28/32 papers and 23/32 locations, rerank 28/32 and 25/32.
2. KB-G3 verifier (tracks/kb/stage/KB-G3/VERIFIER.md, 54/60): every WRONG or NOT CONFIRMED item
   has an action in tracks/kb/stage/REVIEW-wave3.md (section "kb lead batch 13"): 682
   superseded by 862 and refuted as worded; 781 and 804 verified; 714 answered NO (claim 863);
   809 annotated (INSPIRE 4 of 8); 85 and 737 annotated; 716, 798, 799, 808 annotated from the
   KB-G1 first answers and ingest4. The six wrong claims share one cause: each was processed by
   its pipeline step, not read against its own text.
3. KB-G3 package (tracks/kb/stage/KB-G3/): NOT complete for an independent review. Every
   to_verify claim of the tracks' queues (A, D, F, core) now carries a processing event; seven
   brief seeds carry none, of which 803 (stability of matter-dominated FLRW under
   Einstein-Vlasov) and 805 (three derivations to check: S1's expanding dust ball, the
   Einstein-Straus vacuum bubble, the strong-field Hills scale) bear on G1 of A, B, D, F. The
   other five (806, 807, 810, 811, 812) are bibliographic or tooling items; I judge they do
   not bear on G1 (SCOPE.md) - say if you read the gate otherwise.
Requests:
 a. A claims package in the next batch (kb helper, about two hours): 803 and 805 (ask A, D, F
    whether their G1 packages hold the derivations of 805), the fragment claims (85 and the
    about 17 of claims_tracks/AUDIT.md), a "supersede" action in `kb claim` so that a verify
    whose evidence contradicts the text cannot leave the old wording endorsed.
 b. Then a fresh verifier for KB-G3 (decision 0016 item 4): resample the processed claims,
    including this batch's 862-864, 781, 804, 409, 447, 449, 450.
 c. Manifest: 0707.4654, 1006.1632 and gr-qc/0608095 are on disk and in the downloads table but
    in no manifest (gr-qc/0608095 dropped by decision 0024); keep or remove 0707.4654 and
    1006.1632? (who fetched them is not recorded).
No card-hours used.
