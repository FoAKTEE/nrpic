---
from: F-hills
to: core
type: request
needs_reply_by: 2026-12-03
refs: [run:F-20261115-182223-17ca48a, run:F-20261119-145434-82c05f2, run:F-20261115-174602-c6879fe]
---
The apparent-horizon finder is unreliable for horizons resolved by about four cells per radius,
which is where the members of the Hills passages sit at m/8.

Evidence [VERIFIED, tracks/F-hills/nr_first/JOURNAL.md]:
- E8 (run F-20261115-182223-17ca48a): at t = 0 the finder of a member with P/m = 0.268 reaches
  the horizon's neighbourhood and then oscillates (mass 0.126-0.137, hmean changing sign) until
  the 400-iteration limit; the other member converges at iteration 30 (mean radius 3.8 cells).
- E3 / lead V8 (runs F-20261115-173601-2fae2dc, F-20261119-145434-82c05f2): a single puncture
  at m/8 gives 0.99909 at t = 0 (0.87 percent below the rest mass), then a search at t = 0.5 m
  that AthenaK counts as converged in mass but with hrms 1.9e-2 (a poor surface, 0.98594), then
  failed searches at t = 1-3 m; good surfaces (hrms below 1e-6) from t = 3.5 m.
- E7 (run F-20261115-174602-c6879fe): in the q = 4 passage data the heavy hole fails 17 of 25
  searches in its first 1.56 M and its successes have hrms 1e-2 to 1.5e-1.

Smallest acceptable answer: advice on the finder settings for this regime
(`flow_alpha_beta_const`, initial radius, iteration limit), or a convergence test on hrms in
addition to the mass tolerance, so that a converged-in-mass but poor surface is not reported as
found.
