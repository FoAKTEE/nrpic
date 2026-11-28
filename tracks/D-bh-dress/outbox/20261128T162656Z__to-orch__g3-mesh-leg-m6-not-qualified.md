---
from: D-bh-dress
to: orch
type: request
needs_reply_by: none
refs: [tracks/D-bh-dress/scope/SCOPE_G3.md, tracks/D-bh-dress/g3/amend/JOURNAL.md, coord/DECISIONS/0051-track-b-g2-signed-rulings-after-batch-40.md]
---
Track D, lead of batch 41: decision 0051 item 3 carried out; one point for you to confirm.

1. G-8 (q0100, run D-20261128-062142-c5666c4, 2.20 card-hours, core-v0.8) is read for G3-G1 only (g3/amend
   JOURNAL entry 9; reader D-20261128-160553-b500509, figure g8_read.png): every 10 M bin of the swallowed dust's
   proper time from 50 to 492 M lies at +0.17 to +0.25 per cent above the exact LTB growth (bound 0.5), +0.10 to
   +0.24 per cent with the shells' lead carried; the slope d ln M / d ln a within 3e-3 of the exact one.
2. The qualifying test of the M/6 member failed on processors. The same deck as the card timing run, two cycles
   on the release processor build (run D-20261128-160418-b618bff): the finder's search at t = 0 is not found
   (reason 6, 400 flow iterations, area mass 1.0053 at mean radius 0.61 M; the horizon of the data is at 0.5 M,
   three cells of M/6); the null-pair decks at M/6 fail the same way. At M/8 the same search is found after 136
   iterations. By SCOPE_G3 amendment A6 (written before the test) G-6u is not run and the null pair at M/6 is not
   queued: the mesh error of G3 is the envelope of |e-bar_8 - e-bar_12| with no order, FL16 (refined M/16 of G2)
   beside it to 190 M. The card timing run T-6u is queued once (q0110, cap 0.2) as the ruling's literal test.
   Please confirm this reading of "qualifies when its timing run finds the horizon at t = 0", or say if you want a
   retest with other finder settings at M/6 (more flow iterations, another start radius): I did not run one,
   because settings chosen after seeing the failure would not be the test the ruling names.
3. Builds: core-v0.9 reproduces core-v0.8 byte for byte on the G-8 deck (every output after two cycles, restart
   files included; same run, check K3): no G3 deck sets deposit_comp_c or deposit_fine_shape. New members run on
   core-v0.9 and G-8 stays one build with them in effect (SCOPE_G3 A6, builds).
4. Queued (priority 2, core-v0.9): q0110 D-T6u, q0111 D-G3-G12u (chain, cap 11; 9.4 card-hours measured rate).
   G-8-4N (particle leg) follows its processor smoke test. Card-hours toward G3: 3.72 used of 60.
