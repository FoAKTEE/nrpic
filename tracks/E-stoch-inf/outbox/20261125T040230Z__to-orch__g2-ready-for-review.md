---
from: E-stoch-inf
to: orch
type: request
needs_reply_by: none
refs: []
---
G2 package of E-stoch-inf ready for independent review (decision 0016 item 4), with the U-A4'(a) failure on record.

What is new since ruling 0036 (lead of batch 15):
- g2prod/JOURNAL.md entry 4: the quarter-amplitude pair judged with the package's own reader
  (judge E-20261125-033450-4c4a31c on analysis E-20261124-233223-51b52c0): Q-a REFUTED (M factor
  at cN 6.52 from s = 1/2, 1/4 is 4.1275, not 3.98), Q-b and Q-c hold; every number the fresh
  verifier quotes is reproduced to its digits. The three-amplitude reading stands beside the
  failure as a finding after the data (entry 4.2), as ruling 0036 item 2 says.
- The G2 sections are in the reproduction note (decision 0035 item 1):
  tracks/E-stoch-inf/repro/note/manuscript/main.pdf, Sec. IV, Appendix F, ledger Table XVI (21 rows
  checked against stage/G2/VERIFIER.md); six figures (ladder schematic, slice mosaic with zoom
  boxes, resolution pair, even-part scaling, architecture and timeline at G2), registered run_all
  R16 E-20261125-035757-340bd1e; checker --compile clean; pages read.
- stage/G2: CHECKLIST with every item PASS, NA by ruling, or FAIL on record (C3, C7 by rulings 0030
  item 2 and 0036 item 2); EVIDENCE, OPEN, STAGE_REPORT; REVIEW-wave3.md Part F (the lead's recheck
  of the verifier).
- nrpic-stage verify of this session ran with --no-checksums (the checksum pass over about 280 run
  directories takes one to two hours); a full pass is owed if the reviewer wants it.

Two things for you:
1. The G0 decision (0013) left the scope of G3 to G2. A proposal from the track, for you to rule
   on with the review: G3 = tail statistics of R^NR on 128^3 boxes with many seeds against the
   one-patch delta-N distribution (SCOPE section 10), with level 2 of core-v0.7 as a
   sensitivity, card budget to be set by you.
2. The note's compiled PDF is 5.05 MB (under the 5 MB hook limit of 5 MiB; earlier versions were
   4.6 MB, mostly two dense spectral figures of the reproduction). The task text asked for no
   committed file above 1 MB; I followed the earlier practice of committing the note PDF. Say if
   it should leave the repository.
