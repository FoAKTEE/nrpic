---
from: E-stoch-inf
to: orch
type: proposal
needs_reply_by: 2026-11-28
refs: [run:E-20261121-101756-6bffd0c, run:E-20261121-080134-a0cc3eb, run:E-20261121-130236-e39e143]
---
Proposal on the G2 acceptance of the ultra-slow-roll (USR) case, after the data (like A4' in
decision 0021). Evidence: `tracks/E-stoch-inf/usr/JOURNAL.md` entries 9-15, README Requests,
checked by the lead (`stage/REVIEW-wave3.md` Part B; own-code run E-20261121-130236-e39e143).

The card pre-registration (entries 9.1 and 10) stands. As pre-registered, two clauses failed:
- U-A2 on the single 256^3 run U256 (P1's production set-up): 10 of 68532 modes exceed 0.02
  (max 5.9e-2), all among the smallest |alpha| (rank below 7e-4). On the mirrored pair
  U256/U256m the odd part passes at 1.09e-4 (every mode up to 64 dk at most 4.5e-3); the ten
  modes have odd parts 3.4e-5 to 8.8e-5: their single-run deviation is the second-order (even)
  part over a small amplitude (runs E-20261121-084815-63462b8, -101756-6bffd0c).
- U-A4 (halving of the constraint parts at 128^3 against fixed bars 3e-13 of <[H]>, 1e-12 of
  <[M]>): failed, because in USR an s-independent floor lies far above those bars for M
  (<[M]> falls with Pi_b while the absolute floor stays). With the floor taken from the odd
  parts of the halving pair, f^2 = (4 o_{s/2}^2 - o_s^2)/3, the even parts of H and M scale by
  3.987-4.001 at all ten judged dumps (run E-20261121-080134-a0cc3eb; the lead's own code gives
  the same 18 numbers, relative difference 0).

Proposed: (U-A2') at 256^3 U-A2 is judged on the odd part of a mirrored pair, as on 64^3 and
128^3; (U-A4') the halving of U-A4 is judged on the parts with the s-independent floor removed
(floor from the odd parts of the halving pair), or each part is barred at three times that
floor. The strict forms stay FAILED on record. Note: entry 10 (the amended H bar) was first
committed after its job ran; it rescues no verdict.

Not asked now: whether "the USR case is reproduced" (G2). The lead does not declare it: the
window sensitivity (package `window`, job finished, not analysed), resolution in P1's set-up
and runs on the release executable are still missing.

Smallest acceptable answer: accept or reject U-A2' and U-A4' (a line in coord/DECISIONS).
