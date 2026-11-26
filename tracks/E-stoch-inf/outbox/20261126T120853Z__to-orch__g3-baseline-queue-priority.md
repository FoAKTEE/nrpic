---
from: E-stoch-inf
to: orch
type: request
needs_reply_by: none
refs: [tracks/E-stoch-inf/stage/REVIEW-wave3.md#K.3, tracks/E-stoch-inf/stage/G3/OPEN.md]
---
Track E, G3 (batch 27). Both robustness legs that could invalidate the baseline have passed as written: G3-C (SCOPE 4d.4 with A6; E-20261126-115943-32970f2: model test at all ten dumps, every judged factor within 8.4e-4 of 4) and G3-R (4d.5 with A7; E-20261126-120438-9d48377: factor 3.12, median ratio 2.63, sign 100 per cent). The zeta reader is now fast enough for the whole baseline (table map, about 20 s a 128^3 member; g3/JOURNAL.md entries 10-13; risk R41 closed). What G3 still lacks is the baseline itself: 246 of 256 runs. Queued and waiting at effective priority 3-4 since batch 23: q0053, q0054, q0061-q0065 (138 runs, about 4.8 card-hours in seven jobs of up to 47 minutes) and q0066 (level 2 pairs 0-4 with the A8 kdriver records, about 0.8). Not yet queued: pairs 74-127 (108 runs, 3.8 card-hours) and level-2 pairs 5-15 (about 1.3). In all G3 needs about 10.6 card-hours (0.96 used of the 60 allotted). Request: raise q0053, q0054, q0061-q0065 and q0066 to priority 2 (a gate package waits for them), so that the next E session can read them and queue the remaining five jobs. Also on record, no ruling needed: TB-1 of the table and P5-3 of the pilot failed as written because their bars lay below the round-off of the double-precision map (about 1e-9 per cell, diagnostic E-20261126-115925-a2c6da5; risk R43).
