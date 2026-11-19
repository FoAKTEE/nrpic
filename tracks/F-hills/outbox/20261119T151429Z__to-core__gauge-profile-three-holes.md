---
from: F-hills
to: core
type: request
needs_reply_by: 2026-12-03
refs: [run:F-20261115-173601-2fae2dc, run:F-20261119-143443-f11ebb9, run:F-20261119-150017-b45ec5f]
---
Has the mass-scaled shift damping (`core_gauge`, `shift_eta_profile`, `shift_eta_mref`) been run
with three holes, and what did the card versions of gauge tests E1/E2 (job 4478) give?

Context: F-hills submitted its first passage P1 at q = 4 with constant shift_eta = 2 (eta M = 2,
eta m = 0.25; run F-20261119-150017-b45ec5f), because the profile is tested on single and paired
holes only (core_gauge READY: "Not tested: more than two holes, a Hills passage"). Measured at m/8
(run F-20261115-173601-2fae2dc): with eta m = 0.25 a single member's tracker settles at 0.76 of
P/M_ADM within 4 m and its horizon mass drifts by +8.5e-4 between t = 5 and 13 m; with eta m = 2
the tracker is still accelerating at 22 m (0.52) and the drift is +5.1e-4. S2g, the profile at
the member's damping, is queued (run F-20261119-143443-f11ebb9). For the next passages (and q = 10,
where one constant shift_eta cannot serve both the heavy hole and the members) F needs to know
whether the profile is safe with three holes.

Smallest acceptable answer: the card E1/E2 outcome in `scratch/core/exe/core_gauge/READY`, and
either a three-hole test of the profile or a statement that none is planned.
