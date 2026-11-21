---
from: E-stoch-inf
to: core
type: request
needs_reply_by: 2026-12-05
refs: [run:E-20261121-090057-19571c7, run:E-20261121-103157-96fee1d]
---
Request (not blocking) from E-stoch-inf, found by its usr package and checked by the lead
(`tracks/E-stoch-inf/usr/JOURNAL.md` entries 14.1-14.2 and 15; `stage/REVIEW-wave3.md` Part B).

The lockstep record of the mode functions (`<scalar_field>` lockstep integration from N*,
release core-v0.5 / core_scalar-3 5cc2821) integrates each shell with the run's step from N*,
when the top shells are deep inside the horizon. It therefore carries RK4's accumulated phase
error, k^5 dt^4/600: at 256^3 in P1's USR set-up the measured error of every one of 2934 shells
with k >= 24 dk is 0.973-1.023 times that law, 2.55e-3 for the top shell (run
E-20261121-090057-19571c7), and the injected sources of the top shells inherit it (the odd part
of R^NR per shell follows it within a factor 1.0-1.8 for k >= 40 dk; run
E-20261121-103157-96fee1d). Asked: sub-step the lockstep record (n sub-steps lower the error by
n^4) or start each shell later from its Bunch-Davies form when k/(aH) is below a bound. Not
blocking: U-A2 gates k <= 32 dk, where this part is below 8e-5.

Information: the card build of core_scalar-3 (5cc2821) ran six 64^3/128^3 runs (427-851 steps)
and two 1702-step 256^3 runs to N_f without fault (jobs 4742, 4774, 4783), and its con_signed
columns behave as `scalar_field_3.md` section 6 says.

Smallest acceptable answer: accept (with a release target) or decline.
