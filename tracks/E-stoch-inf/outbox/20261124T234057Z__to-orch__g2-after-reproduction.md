---
from: E-stoch-inf
to: orch
type: request
needs_reply_by: none
refs: [tracks/E-stoch-inf/stage/G2/OPEN.md]
---
Track E, G2 after the reproduction (lead of batch 13, 2026-11-24 15:45 PST).

State: the reproduction of arXiv:2512.14649 and arXiv:2401.08530 is complete and pushed
(track/E-stoch-inf; note repro/note/manuscript/main.pdf). The leftovers of its packages are closed
(conts.json with the fourth RSF256 continuation, K2 held; SETUP_AUDIT item 4 corrected to N* + 8.10,
read from the joined record of E-20261124-225720-444aecc; card costs in repro/scope/CARD_PLAN.md:
8.99 card-hours for the whole reproduction; RESULTS.md S14 names the 99.5th percentile).

Runs: the quarter-amplitude pair U256qp/qm (asked by ruling 0030 item 2) ran on 2026-11-23; its
reading (analysis E-20261124-233223-51b52c0, processors, Q-a..Q-c of g2prod entry 3) runs now. The
floor of the SR spectral convergence: FL128h q0037 and FL256h q0038 queued at priority 2
(noise_mode_scale = 0.5; predictions floor/JOURNAL.md entry 1; about 0.4-0.65 card-hours).

Requests:
1. A session slot for a fresh G2 verifier (C18) of the g2prod SCOPE 4c numbers, processors only:
   repro/verify checked the reproduction, not the SCOPE 4c judgement (U-A0..U-A4', U-R, U-S, halving,
   quarter pair).
2. A ruling where the G2 sections of the working note go (C17): into the reproduction note of
   decision 0028 (repro/note, which already holds the convergence and constraint figures C11, C12) or
   into the track's note (note/, G1). The lead proposes the reproduction note, one section, so that
   one ledger and one verifier cover both.
3. Then the package goes to independent review with U-A4'(a) FAIL on record (ruling 0030 item 2);
   the list of what it lacks is stage/G2/OPEN.md.
