# JOURNAL of the package eih (F-hills, wave 3a, helper)

First post-Newtonian (Einstein-Infeld-Hoffmann, EIH) three-body reference for the Hills
passages, with the large black hole free. Asked for by the second check of G0
(`stage/G0/SECOND_CHECK.md`, "Which tests would tell", item 3): neither the Newtonian
(newton3) nor the geodesic-plus-Newtonian (HRNA, geodesic_binary) baseline is a controlled
approximation at mass ratio ten. Labels: [VERIFIED] (a run of this package or a source read at
its locator), [BACKGROUND], [JUDGEMENT], [TO VERIFY]. Times are UTC.

## Entry 0 (2026-11-19 14:30): sources and set-up

Equations read at their locators (README section "Equations"):
- EIH accelerations: Will, arXiv:1312.1289v3, `PN-NbodyDraft.tex` l. 338-355 (fetched today
  with `nrpic-fetch-arxiv`, under `kb-data/raw/arxiv/1312.1289/v3/src`). The same equation is
  printed in 2404.16270 `appendix.tex` l. 117-124 (Eq. eab.1, all c-sums written with the
  c = a pieces absorbed into "-5 m_a/r_ab") and 2604.27429 `template.tex` l. 100-120. I
  compared the three term by term by hand: they agree. [VERIFIED: reading]
- Conserved energy and momentum: Will l. 357-380 (Eqs. energy2, momentum). Centre of mass:
  Will gives it only truncated (l. 545-547); the general form used here, and the canonical
  momenta and angular momentum, are derived (EIH Lagrangian whose energy function is Will's
  E) and are tested numerically, not taken from a source. [JUDGEMENT until T3]
- Test-mass limit: 2404.16270 `appendix.tex` l. 127-131 (restricted equation, M fixed) and
  l. 182-188 (Eqs. EIH1, EIH2: 1PN energy and angular momentum of a test body).
- Two-body periastron advance: Schaefer & Jaranowski, arXiv:1805.07240v5,
  `LRRSJarXiv_v5.tex` l. 3121-3126 (k = Delta Phi / 2 pi) and l. 3169-3180: k = 3/(c^2 j^2)
  [1 + O(c^-2)], j = J/(mu G M), M = m1 + m2; period P = 2 pi G M / (-2E)^(3/2)
  [1 - (1/4)(15 - nu) E / c^2 + O(c^-4)] (l. 3182-3184), E = (H - M c^2)/mu.
- Exact Schwarzschild orbits for the trust analysis: the geodesic equations of the test body
  (E = 1 parabolic), [BACKGROUND]; the capture condition L < 4 M at E = 1 is the root
  condition of the radial potential (computed, not quoted).

Code: `eih.py` (equations, integrals, vectorised DOP853 with per-trajectory stop, drivers with
newton3's interface: `scatter`, `evolve_states`, `run_encounter`).

## Entry 1 (2026-11-19 14:45): predictions for the tests (written before any run)

T0, Newtonian limit and source consistency.
- With c2inv = 0 the EIH accelerations equal newton3's `_rhs_factory` to round-off (relative
  1e-14). Refuted above 1e-12.
- Test-mass limit: for m1 = m2 = 1e-9 M the EIH acceleration of a member equals the restricted
  equation of 2404 (`appendix.tex` l. 127-131, M fixed, the m2 terms dropped) to relative
  1e-8 (the neglected terms are O(m/M)). Refuted above 1e-6.
- The restricted equation with m1 = m2 = 1e-3 M (pair terms kept) differs from EIH with M free
  by O(m/M) = 1e-3 relative in the PN part. Refuted if the difference does not fall linearly
  with m/M (slope 1 +- 0.2 over m/M = 1e-2 ... 1e-4).

T2, two-body periastron advance and period (bound orbits, e = 0.5, semi-latus rectum
p = 20 ... 640 M, nu = 0.25, 0.0826 (q = 10), 1e-5): measured k = Delta Phi/(2 pi) from
successive periastra against 3/j^2 with j from the 1PN angular momentum. Prediction: the
relative deviation k j^2/3 - 1 falls like 1/j^2, i.e. like M/p, with a log-log slope between
-1.8 and -2.2 against j, and |k j^2/3 - 1| j^2 between 1 and 20 (the size of the GR 2PN
coefficient, (5/4)(7 - 2 nu) + (1/2)(5 - 2 nu) E j^2, is about 8; EIH alone generates a
different but same-sized coefficient). Period: relative deviation from the 1PN formula falls
like (M/p)^2 (slope -2 +- 0.3 against p). Refuted outside these ranges.

T3, conservation in a Hills encounter. The encounter q = 10 (M = 1, m1 = m2 = 0.05, a = 3,
r_p = 8, coplanar prograde, effective phase 130 deg, start 4 r_t, end 30 r_t), and the same
encounter scaled to lengths lambda x (lambda = 1, 2, 4, 8, 16; velocities lambda^-1/2, times
lambda^3/2, so the Newtonian problem is identical and every PN term scales as 1/lambda).
Changes over the run, divided by the initial kinetic energy (momentum: sum m|v|; angular
momentum: sum m |x x v|):
- Newtonian energy and momentum change at 1PN order: slope -1 +- 0.15 in lambda.
- 1PN energy, momentum, angular momentum and the centre-of-mass motion G - P t change at 2PN
  order: slope -2 +- 0.3, and at lambda = 1 below 1e-2 relative. Refuted otherwise (a wrong
  sign or coefficient in the equations or in the integrals gives slope -1).

T4, where 1PN stops being trustworthy (test-mass limit against exact Schwarzschild).
Parabolic orbits (E = 1 in GR, 1PN energy 0) labelled by their angular momentum L (gauge
invariant): swept angle Delta phi(L) between r = 1e4 M inbound and outbound, exact
(quadrature) against EIH (integration of the EIH equations with a 1e-10 test mass); also the
"tidal" derivative d(Delta phi)/dL, which sets how differently the two members are deflected.
Predictions [JUDGEMENT]: (i) EIH never captures (its test-body energy has a repulsive
M^2/(2 r^2) term; every L has a turning point), while GR captures for L < 4 M (r_p = 4 M);
(ii) the relativistic excess of the deflection over the Newtonian 2 pi is reproduced by 1PN
within 10 percent only for r_p >~ 30 M (areal), within 30 percent at r_p ~ 10 M, and 1PN
underestimates it (GR's excess diverges at L -> 4 M); (iii) the error of d(Delta phi)/dL is
larger than the error of Delta phi at the same r_p. Refuted if 1PN is within 10 percent at
r_p = 10 M, or if 1PN overestimates the excess at r_p = 8-12 M.

## Entry 2 (2026-11-19 14:40): first test run failed in T0d (run F-20261119-143503-3cd3592)

T0a (Newtonian limit, 1.5e-16), T0b (2404's restricted equation at states with M at rest at
the origin, PN part equal to 4e-15 for m/M = 1e-9 ... 0.1) and T0c (sum of canonical momenta =
Will's P, 2e-16) passed. My T0b-bullet-3 prediction (an O(m/M) difference) was wrong in its
premise: at a state with x_M = 0, v_M = 0 the EIH acceleration of a member IS 2404's
restricted expression (I checked the terms by hand afterwards: all c = M pieces of 2404's
equation are EIH's), so the agreement is to round-off at every m/M; the M-fixed versus M-free
difference only appears along an evolution. [VERIFIED] The run then stopped (exit 1) in T0d:
the fixed-point inversion of the canonical momenta diverged on the random strong-field states
of T0 (masses up to 2 at distances ~ 1, 3U > 1). Fix: iteration divided by the diagonal
m (1 + 3U + 3/2 v^2) of dp/dv, and T0d run on weak-field states (positions x 10, U <~ 0.1, the
regime of the puncture data). Rerun below.
