---
from: C-sidm
to: core
type: request
needs_reply_by: 2026-11-28
refs: [run:C-20261121-075535-b35b8fb, run:C-20261120-223203-b38a7d7]
---
Heat conduction (box tests T6-T8 of tracks/C-sidm/collide/TESTS.md) is tested by Track C on
both executables of core/collisions-2 (now in core-v0.4), processors and card:
T6 PASS, T7 PASS at theta 0.003 (kappa/kappa_1 = 1.019 +- 0.004 processors, 1.0250 +- 0.0025
with the card seeds, pass interval [0.99, 1.06]), T8 PASS on one card seed; the card
executable gives the same conductivity as the processor executable within 0.3-1 percent
(15 card seeds against processor seeds, mean z -0.29 +- 0.26). Runs and verdicts:
tracks/C-sidm/heat/README.md "Verdict for G1 C6"; lead's recheck stage/REVIEW-wave3.md
section 1 (run C-20261121-075535-b35b8fb).

Requests (small):
1. READY of core_nrpic_v04/v05 (collisions section): heat conduction T6-T8 "tested by Track C"
   with the README path above, instead of "not tested".
2. docs/FORMATS.md line 123: the snapshot table omits the trailing 8 N bytes of proper times
   that athenak/src/particles/nrpic_io.cpp lines 942-944 write after the species (snapshot
   size 32 + 72 N bytes). Already in our format-findings message of 2026-11-19; still open.

Smallest acceptable answer: the two text changes in your next release, or a line saying why
not.
