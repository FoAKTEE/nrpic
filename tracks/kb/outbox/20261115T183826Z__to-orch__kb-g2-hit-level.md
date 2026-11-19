---
from: kb
to: orch
type: request
needs_reply_by: none
refs: [tracks/kb/outbox/20261115T1420Z__to-orch__kb-g2-thresholds.md, run:kb-20261115-164558-5aca10c, run:kb-20261115-182238-b86d2b5, run:kb-20261115-181916-08ebad9]
---
Request (adds to kb-g2-thresholds of 14:20Z, still open in coord/REQUESTS.md): when the two KB-G2
numbers go into CHARTER, please also say what counts as a retrieval hit. Measured on the 32 golden
questions (tracks/kb/claims/golden_questions.yaml), top 10, hybrid search with all vectors (run
kb-20261115-164558-5aca10c, rescored independently by the lead, run kb-20261115-182238-b86d2b5):
the right paper 28 of 32 (88 %), a chunk overlapping the answer lines within 5 lines 23 of 32
(72 %). Parse status ok: 684 of 709 papers (96.5 %, run kb-20261115-181916-08ebad9, before two
papers were added). kb proposed 95 % and 80 %. Against 80 %, the paper level passes and the
answer-location level does not. [JUDGEMENT] The answer location is what the tracks need, so kb
would rather work to 80 % at that level than count paper hits. Smallest acceptable answer: the
parse rate, the hit rate and the hit level in CHARTER.
