---
from: E-stoch-inf
to: orch
type: proposal
needs_reply_by: none
refs: []
---
Proposal (not a rewording of SCOPE 4c, which stays as written with its failure on record): two
clauses for later gates of Track E, from the fresh G2 verifier's findings (stage/G2/VERIFIER.md
sections 3.3, 5) and the lead's recheck (stage/REVIEW-wave3.md Part F).

1. Scaling of the constraints with the noise amplitude: judge the even part against a noise level
   taken from three amplitudes, sigma = rms(D1)/sqrt(17) with D1 = E(1) - 4E(1/2) and
   D2 = E(1/2) - 4E(1/4), and require rms(D2)/rms(D1) within 1 +- 0.05 and corr(D1, D2) within
   -4/17 +- 0.05 as the test that the per-run part is what the estimator assumes. Reason: the floor
   fixed in 4c is the difference of two odd-part norms equal to 1e-4 where the odd part exceeds
   the even part by one to three decades, so it moves by tens of percent (verifier run
   E-20261125-023427-6fb6400; note Sec. IV C).
2. Resolution: judge the discretisation part of the odd-part error, separated from the third-order
   part by Richardson in s^2 over three amplitudes, and not the maximum over k <= 32 dk, which at
   320^3 sits on a third-order flat part that does not depend on the spacing (note Fig. 14: ratio
   0.992 below |n| ~ 25, 2.91 above 40; verifier: discretisation part order 4.7).

Both need a third amplitude in every judged pair (about 1.2 card-hours per pair at 256^3).
