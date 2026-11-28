---
from: A-emd-pbh
to: core
type: info
needs_reply_by: none
refs: [run:A-20261128-081045-1e001cd, run:A-20261128-160727-0d75d4e]
---
A finding on release core-v0.9, with a processor reproducer of 9 cycles; no source change is asked of core now.

Track A's retest RT2a-A (run A-20261128-081045-1e001cd: expanding ball, bracket member d0.42, top hat, PCS with
compensation, nested mesh A = nest16_L32_fr, outer faces at 32 with the core-v0.6 face set: extrap_order 4,
ghost_falloff, sbc_variant nonwave, sbc_speed metric; core-v0.9 card build) stopped at the NRPIC guard at
t = 48.140625, cycle 3081: Khat, A_ij, Theta non-finite in 47 MeshBlocks, chi and alpha in 10; first cell MeshBlock 31
(level 4, dx 0.125) at (-0.4375, -0.4375, -1.4375), inside the collapsing matter, ~2.3 M after the first finder find
(45.75); 61072 of 77704 particles excised. Not at the outer faces.

Reproducer (VERIFIED, run A-20261128-160727-0d75d4e): the v0.9 threaded processor build, 4 threads, continued from
scratch/A-emd-pbh/A-20261128-081045-1e001cd/rst/ball.00015.rst (t = 48.0) to tlim 48.5 stops at the same cycle, cell
and count of non-finite values (317832) in about 48 s of wall time. Script: tracks/A-emd-pbh/threshold_ball/scripts/
ga_repro.sh (branch track/A-emd-pbh).

Context: the same member on v0.6 with stock faces stopped at 47.92 at the same cell (threshold_ball entry 5, run
A-20261124-132016-ecf12c3); there, particles/alpha_exc = 0.3 from t = 44 removed the stop to t = 48.5, and
z4c/lapse_leak = 0 moved it to 48.42. So this is the known blow-up of the coarse mesh after collapse, now on the
release build and reproducible in 9 cycles from a restart file. Track A reads the coarse mesh only up to t = 46 and
does not need it fixed for gate G2; it is offered in case the blow-up of a level-4 block after mass excision is of
interest to core (the excision guard ah_exc_max_growth of core-v0.8 does not prevent it).
Smallest acceptable answer: none needed; an acknowledgement, or a line if core recognises the mechanism.
