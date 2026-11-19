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

## Entry 3 (2026-11-19 14:45): first T4 run failed in the 1PN quadrature (run F-20261119-143638-83ce321)

The script stopped (exit 1) at the first L where round-off next to the turning point made
v_r^2 negative in the quadrature check "1PN-Q" (TypeError on None). The EIH integrations and
GR quadratures of the 19 rows before (areal r_p = 4.2 ... 40 M) had finished; their numbers are
in the run log, but I take the outcome from the rerun only. Fix: v_r^2 <= 0 next to the turning
point uses the analytic limit of the substituted integrand. Rerun below.

## Entry 4 (2026-11-19 14:50): outcomes of T0 and T4; T2 and T3 failed as designed

Test run F-20261119-143636-aae25fb (exit 0, 4 of 6 checks passed):
- T0a-T0d PASS (Newtonian limit 1.5e-16; 2404 restricted form 4e-15; sum of canonical momenta
  = Will's P 2e-16; momentum inversion 1.5e-16 on weak-field states). [VERIFIED]
- T2 FAIL. The measured k came out near -1 because I unwrapped the polar angle only at the
  periastron events (consecutive periastra differ by 2 pi + delta, np.unwrap removes the 2 pi):
  a defect of the measurement in the test, not of the equations. The orbits were also not the
  intended ones: with the Newtonian periastron speed at p = 20 M and nu = 0.25 the 1PN orbit is
  barely bound (apocentre 656 M instead of 40 M), so only one periastron fell inside the
  integration time. The same happens to the Hills start states (entry 7).
- T3 FAIL. Slopes -2.8 (1PN energy), -1.5 (Newtonian energy) instead of -2 and -1. The
  premise of the scaling (the Newtonian trajectory the same, PN a perturbation) does not hold
  for lambda = 1 ... 4: the encounter is chaotic and its fate changes with lambda (outcome 1 at
  lambda = 1, 0 at lambda = 4), and at lambda = 1 the EIH member reaches 3.1 M where M/r = 0.32.
  The normalisation by the initial kinetic energy is also poor: the member's kinetic energy at
  pericentre is about four times the initial one.
  Not a run, a development check (unregistered, numbers not used): dE/dt along the EIH equations
  at a random two-body state scaled as c2inv^2 (1.2e-7, 1.2e-9, 1.3e-11 at c2inv = 0.1, 0.01,
  0.001), and over one orbit at p = 200 M the energy variation scaled as c2inv^2. A registered
  test of this local property is T1 below.

T4 run F-20261119-143753-d82e9e3 (exit 0; the first attempt F-20261119-143638-83ce321 failed,
entry 3; `figures/fig_t4_trust.png`, `results/trust.json`). [VERIFIED as outputs of this run]
- EIH relative to exact Schwarzschild, parabolic orbits of equal L, error of the relativistic
  excess of the swept angle: -87.6 % at areal r_p = 4.2 M, -60.7 % at 6, -39.3 % at 8, -26.8 %
  at 10, -19.6 % at 12, -12.3 % at 16, -8.8 % at 20, -5.0 % at 30, -1.2 % at 100 M. 1PN
  underestimates the excess everywhere. The error stays below 10 / 20 / 30 / 50 % beyond areal
  r_p = 20 / 12 / 10 / 7 M.
- The L derivative of the excess (how differently two members of the binary are deflected)
  is worse: -82.8 % at 8 M, -61.1 % at 10, -45.6 % at 12, -28.5 % at 16, -20.0 % at 20,
  -11.1 % at 30 M; below 10 / 20 / 30 / 50 % beyond 40 / 25 / 16 / 12 M. Below about 7 M the EIH
  excess even decreases with decreasing r_p (it peaks at 1.10 rad near 6 M) while GR's diverges
  at L -> 4 M.
- No capture in EIH: for L = 0.5, 1, 2, 3, 3.5, 3.9, 4.0 M the EIH test body turns around at
  harmonic r = 2.70, 2.74, 2.95, 3.50, 4.15, 5.06, 5.35 M (GR: captured for every L < 4 M).
- Pericentres: for the L of the GR parabola with areal r_p = 8 M the EIH pericentre is 7.68 M
  (harmonic; GR 7.0), at 10 M 9.45 (GR 9.0).
- A second 1PN dynamics (quadrature of the conserved 1PN E and L, which differs from EIH at 2PN)
  differs from EIH by 7-16 % of the excess at 10-40 M: the 1PN truncation ambiguity is as large
  as the error against GR. Will's E is conserved along the test-mass EIH runs to 4e-13 per
  unit mass.
- Predictions (entry 1, T4): (i) no capture in EIH: CONFIRMED; (ii) "within 10 percent only for
  r_p >~ 30 M": REFUTED in the number (10 % is reached at 20 M), CONFIRMED in kind (27 % at
  10 M, 1PN underestimates); (iii) the derivative worse than the angle: CONFIRMED.
- [JUDGEMENT] Where 1PN stops being trustworthy for the Hills problem: the tidal splitting of
  the binary is governed by the differential deflection, whose 1PN error is 20 % at 25 M and
  50 % at 12 M (areal). So the EIH reference is a controlled correction to Newton (error of the
  relativistic part below about 20 %) for pericentres beyond about 25 M; between 12 and 25 M it
  gives the sign and rough size of the relativistic correction; inside about 12 M (all of the
  plan's pericentres: 7-17 M at q = 10, 9.8-16 M at q = 4) it is not a controlled
  approximation either, and below about 7 M (and for any member with L < 4 M, which GR
  captures) it is qualitatively wrong.

## Entry 5 (2026-11-19 14:55): predictions for the redesigned tests T1-T3 (before the run)

T1 (new), local consistency of the equations with the integrals. At 30 random three-body
states (weak field, r ~ 10-50, v ~ 0.05-0.2) the time derivatives of Will's E and P, of
J = sum x_a x p_a and of G - P t along the EIH equations (centred differences of the integrals
in x and v, contracted with v and a) scale as c2inv^2: ratio between c2inv = 1e-2 and 1e-3 equal
to 100 within 10 percent (median over states), while the derivatives of the Newtonian E, P, J
scale as c2inv (ratio 10 within 10 percent). Refuted otherwise.
T2 (redesigned). Initial relative speed at periastron chosen so that the 1PN energy equals the
Newtonian target -(1 - e^2)/(2 p) mu (e = 0.5); six periastra counted by events; the angle
unwrapped on a dense grid. Prediction as entry 1: |k j^2/3 - 1| falls like 1/j^2 (slope -1.8 to
-2.2 against j over p = 80 ... 640 M), coefficient |k j^2/3 - 1| j^2 between 1 and 20; period
deviation slope -1.7 to -2.3 against p.
T3 (redesigned). The q = 10 encounter at lambda = 8, 16, 32, 64, 128 (M/r_p from 1/64 to
1/1024; perturbative), changes normalised by the largest kinetic energy (and largest sum m|v|,
sum m|x x v|) along the run: slopes -2 +- 0.3 for the 1PN integrals and the centre-of-mass
drift, -1 +- 0.15 for the Newtonian E and P; the outcome the same at every lambda. At lambda =
1 (reported, not tested) the change of E is an indicator of the 2PN error of the encounter.

## Entry 6 (2026-11-19 15:05): the start state in 1PN; predictions for the scans and for P1

The start states of the plan (newton3's Newtonian parabola about M + m at 4 r_t) carry
Newtonian velocities. Read in 1PN they are not parabolic, and how they are read decides
whether the centre of mass is bound. Development check (unregistered; the numbers are
recomputed and recorded by the P1 run): the binary as one point m_b, two-body 1PN invariants
per unit reduced mass at phase 130 deg:
- q = 10 (r_p = 8): velocities read as EIH coordinate velocities, E = +0.0086, J = 4.88 M
  (hyperbolic, v_inf ~ 0.13); newton3's m v read as canonical 1PN momenta (the reading of
  Bowen-York momenta), E = -0.0045, J = 4.195 M (bound; J = the Newtonian L, as it must be).
- q = 4 (r_p = 9.82): +0.0071, J = 5.67 M against -0.0040, J = 4.95 M.
The difference is 1PN in the velocities (v_canonical ~ (1 - v^2/2 - 3U) p/m) but decides the
sign of E at r0 ~ 26-32 M. [JUDGEMENT] For predicting the NR passages the canonical reading is
the consistent one (the puncture momenta are ADM momenta, which at 1PN are the canonical
momenta of the EIH Lagrangian [BACKGROUND, TO VERIFY with core]); the velocity reading is the
like-for-like comparison with the two older baselines, which take v = P/m. Both are run
(models eih and eihp).

Predictions for the scans (scripts/scan.py; q = 10: r_p = 7-17 M, q = 4: 9.82-16 M; prograde
and retrograde; 360 effective phases; all models from the same coordinate state at 4 r_t):
S1. eih (velocity reading): the separated fraction (outcome not 0 or 5) is within 0.15 of full
    Newton at every r_p >= 10 M, prograde (the 1PN CM orbit is hyperbolic with a larger J, its
    pericentre close to the Newtonian one). Refuted if off by more than 0.15 at two or more of
    these r_p.
S2. A member of eih comes inside 5.35 M of M (the EIH turning radius of the L = 4 M parabola,
    the GR-capture proxy, T4) in 0.5-1.0 of the phases at r_p = 7-8 M (q = 10, prograde) and in
    less than 0.4 at r_p >= 12 M. Refuted outside.
S3. eihp (canonical reading) is deeper: its GR-capture-proxy fraction exceeds that of eih at
    every r_p of q = 10 prograde, and its separated fraction differs from eih by more than 0.1
    at some r_p. Refuted otherwise.
S4. Phase by phase (outcome classes, captures counted as their own class): eih agrees with
    full Newton in more than half of the phases at r_p >= 10 M (q = 10 prograde) and with HRNA in
    fewer phases than with Newton at every r_p. Refuted otherwise.
S5. Every eih encounter of the plan's lines has a member inside the trust radius 12 M of T4
    in most phases (> 0.5 at every r_p <= 13 M): the EIH line is not a controlled reference
    there. Refuted if below 0.5 at r_p <= 10 M.

Predictions for P1 (scripts/p1.py; start states of nr_first/inputs/p1_q4.athinput (q = 4)
and three_punctures/inputs/hills_q10_m8.athinput (q = 10), bare masses):
P1a. q = 4, eih (velocity reading): m1 leaves and m2 stays bound, as in Newton (m1 ejected,
    +1.312 units; nr_first E6), with m2's closest approach to M below Newton's 5.78 M and
    inside 5.35 M (GR-capture proxy). Refuted if m2 leaves.
P1b. q = 4, eihp (canonical reading): the centre of mass is bound in 1PN, the encounter is
    deeper than eih's (closest approach of the binary's centre of mass smaller), and the
    outcome differs from eih in at least one of: identity of the ejected member, ejection
    energy by more than 30 percent, or a member inside 5.35 M. Refuted if the two readings give
    the same member, energies within 30 percent and the same capture-proxy verdict.
P1c. q = 10: as P1a/P1b, with the member that Newton binds (m2, pericentre 5.64 M) inside
    5.35 M in both readings.

## Entry 7 (2026-11-19 15:15): outcomes of T1-T3, the scans and P1

Tests, run F-20261119-144536-fc9bf86 (7 of 7 pass; `figures/fig_t2_periastron.png`,
`fig_t3_conservation.png`). [VERIFIED]
- T1: median ratio of d/dt between c2inv = 1e-2 and 1e-3 over 30 random three-body states:
  Will's E 99.98, P 99.995, J 99.997, G - P t 100.01 (second order); Newtonian E, P, J 10.000
  (first order). Prediction CONFIRMED: the equations and the integrals are consistent to 1PN.
- T2: two-body periastron advance k against 3/j^2 (1805.07240 l. 3169-3180): relative
  deviation falls with slope -1.89 / -1.91 / -1.91 against j (nu = 0.25 / q = 10 / test mass,
  p = 80-640 M) with coefficient |k j^2/3 - 1| j^2 = 4.4-5.5 at p >= 160 M; radial period
  against the 1PN formula (l. 3182-3184): slope -1.99 / -1.99 / -1.98 against p. Will's E
  conserved to 1e-12 (nu = 0.25) ... 3e-9 (q = 10, p = 640). CONFIRMED.
- T3: q = 10 encounter scaled by lambda = 8 ... 128: slopes -2.10 (1PN E), -1.74 (1PN P),
  -1.92 (1PN J), -1.81 (centre-of-mass drift), -1.05 / -1.06 (Newtonian E / P); the outcome
  is the same (m1 ejected) at every lambda >= 8. CONFIRMED (P at the edge of the band).
  At lambda = 1 (the plan's r_p = 8 M) the EIH member reaches 3.1 M and the 1PN energy
  changes by 1.8 times the largest kinetic energy along the run, as much as the Newtonian
  energy (2.2): the expansion has broken down there.

Scans, run F-20261119-144537-4db7530 (all 120 tasks, 158 s on 13 cores), analysis
F-20261119-144830-1aaea9d (`figures/fig_scan_lines.png`, `fig_scan_phase.png`,
`results/scan_summary.json`). [VERIFIED as outputs]
- The dominant effect is the start state, not the encounter. With the velocity reading the
  binary comes apart by itself: at q = 10, r_p = 17 M retrograde, where Newton keeps the
  binary in 360 of 360 phases, EIH ends with "both free" in 360 of 360 and the members' distance
  never falls below its initial 3.0 M; same at q = 4 for r_p >= 12 M retrograde. With the
  canonical reading the binary shrinks instead (smallest separation 2.07 M at q = 10, r_p =
  17 M) and survives in 360 of 360. [JUDGEMENT, mechanism] The EIH pair force between the
  members carries the factor 1 - (5M/r + V^2 + ...) of the heavy hole's potential and the
  binary's motion (about 0.2-0.3 at 4 r_t), so a binary that is circular for Newtonian
  velocities at 4 r_t is not bound the same way in 1PN - the EIH counterpart of the Gamma
  effect found for HRNA in SC3. Tested in entry 8.
- S1 (eih within 0.15 of Newton at r_p >= 10 M, q = 10 prograde): REFUTED. 0.86/0.84/0.81/
  0.80/0.82/0.82 against 0.76/0.69/0.59/0.23/0/0 at r_p = 10/11/12/13/15/17 M.
- S2 (eih member inside 5.35 M in 0.5-1 of phases at 7-8 M, < 0.4 at >= 12 M): CONFIRMED
  (0.77, 0.64; 0.19, 0, 0, 0).
- S3 (canonical reading deeper): CONFIRMED at r_p = 7-15 M (1.00/0.91/0.81/0.72/0.58/0.27/
  0.017/0.006 against 0.77/0.64/0.53/0.43/0.32/0.19/0/0), equal (0 and 0) at 17 M; separated
  fractions of the two readings differ by up to 0.48 (r_p = 8 M: 0.39 against 0.88).
- S4 (eih agrees with Newton in > half of the phases at r_p >= 10 M; less with HRNA):
  REFUTED. Phase-by-phase agreement eih-Newton 0.01-0.16 at q = 10 prograde; eih-HRNA 0.01-0.37;
  Newton-HRNA 0.01-0.39. No two models agree phase by phase.
- S5 (an eih member inside the trust radius 12 M in > 0.5 of the phases at r_p <= 13 M):
  CONFIRMED (q = 10 prograde 1.00 ... 0.81; q = 4 prograde 1.00 ... 0.84).
- Internal error of EIH along the encounters: the 1PN energy changes by a median 0.16-0.48
  energy units (unit (m1 m2/a) q^(1/3) = 1.80e-3 M at q = 10, 4.96e-3 M at q = 4), 90th
  percentile up to 1.4 units, against mean ejection energies of 0.4-0.8 units: the 2PN-level
  error of the reference is comparable to the quantity it is meant to predict, on every r_p
  of the plan's lines, including 17 M.
- Mean ejection energies (single ejections, q = 10 prograde, r_p = 8 M): Newton 1.04, HRNA
  (same state) 1.12, eih 0.67, eihp 0.52 units.

P1 run F-20261119-144642-1ca3da1 (`figures/fig_p1_q4.png`, `fig_p1_q10.png`, `results/p1.json`).
[VERIFIED as model outputs]
- Start states in 1PN (binary as one point): q = 4: E/mu = +0.0071 (velocity reading) or
  -0.0029 (canonical), J/mu = 5.67 or 5.03 M; q = 10: +0.0086 or -0.0037, J/mu = 4.88 or
  4.25 M (Newtonian 4.19). Canonical velocities are 0.860-0.872 of P/m.
- q = 4 (nr_first P1): Newton m1 ejected (+1.312 units), m2 bound (closest 5.78 M); HRNA m2
  ejected (+0.965), m1 bound (first pericentre 7.26 M at t = 121, later 5.08 M); eih_v: m1 dives
  to 3.66 M at t = 105 (inside the GR-capture proxy), m2 recedes slowly (+0.11 units at
  t = 1500, "unsettled"); eih_p: no ejection, the binary is re-bound at t = 1500 (members at
  6.75 and 9.17 M closest); eih_p with horizon masses: m2 ejected with +0.21 units, m1 bound
  (a = 58 M). The 1PN energy changes over the run by 0.06, 0.14, 0.55 units.
- q = 10: Newton m1 ejected (+1.61), m2 bound (5.64 M); HRNA m1 plunges at t = 97, m2 ejected
  (+1.16); eih_v: m2 ejected (+0.71), m1 to 3.10 M (GR-capture proxy); eih_p: binary not
  separated at t = 1500, m1 to 4.63 M; eih_p_m: m2 ejected (+1.51), m1 bound to 5.32 M. In all
  three EIH variants m1 comes inside 5.35 M (GR would capture it), as HRNA has it, and none
  has Newton's sense (m1 ejected).
- P1a (q = 4 eih_v follows Newton's sense, m2 inside 5.35 M): REFUTED - the opposite: m1
  dives to 3.66 M and m2 leaves, HRNA's sense.
- P1b (q = 4 canonical reading: CM bound, outcome differs from eih_v): CONFIRMED for the bound
  CM (E/mu = -0.0029) and the different outcome (re-bound binary against a slow m2 escape);
  "deeper" was not measured as stated (the CM's closest approach is not recorded) and the
  members' closest approaches are larger (6.75 against 3.66 M).
- P1c (q = 10: m2 inside 5.35 M in both readings): REFUTED - m1, not m2, comes inside
  (3.10 and 4.63 M); m2 stays at 13.3 and 7.6 M.
- [JUDGEMENT] For P1 at q = 4 the EIH reference does not give a robust outcome: the reading
  of the puncture momenta (a 13 percent change of the start velocities, a 1PN-sized ambiguity)
  and 2 percent in the masses change the fate. For q = 10 the robust part is "m1 enters the
  region where GR captures, m2 does not", shared by HRNA and all three EIH variants, against
  Newton.

## Entry 8 (2026-11-19 15:20): predictions for the far-release EIH line (before the run)

To remove the start-state effect, a third EIH set-up: release at 40 r_t (5M/r0 = 0.02 for
q = 10), the binary Newtonian-circular there (release phase uniform), its centre of mass on the
1PN parabola: two-body 1PN energy of (M, m_b) zero (Will's E) and J/mu equal to the angular
momentum of the GR parabola with areal pericentre r_p (2404 appendix.tex l. 175), so that the
CM encounter is the same invariant encounter as HRNA's with 2404's data. Baselines: Newton
(newton3) from 40 r_t on its own parabola with the same nominal r_p, and HRNA with 2404's data
at 4 r_t (SC1's H4 set-up), both 360 phases; end at 30 r_t outbound.
F1. The binary does not come apart by itself: q = 10, r_p = 17 M retrograde survives in >= 0.9
    of the phases (Newton 1.0). Refuted below 0.9 (then the dispersal of entry 7 is EIH
    dynamics, not the start state).
F2. At q = 10 prograde the far-release EIH separated fraction at r_p = 15 and 17 M is within
    0.15 of Newton's (from 40 r_t) and below 0.3, far below HRNA's 0.8-0.9 (H4 in SC1); i.e.
    HRNA's separation at large r_p is an artefact of its set-up (SC3, SC6). Refuted if EIH
    separates more than 0.3 there.
F3. At q = 10 prograde r_p = 7-9 M a member of the far-release EIH comes inside 5.35 M in >= 0.5
    of the phases. Refuted below.
F4. q = 4 prograde: far-release EIH separated fraction within 0.15 of Newton's at r_p >= 13 M.

## Entry 9 (2026-11-19 15:30): predictions for 1PN-consistent start states of the two passages

`scripts/p1_state.py` builds, for each NR input, a start state at the input's r0 by releasing
the binary at 40 r_t (CM on the 1PN parabola with J/mu = L of the GR parabola with the input's
nominal pericentre, areal 9.82 M (q = 4) and 8 M (q = 10): 4.966 and 4.619 M; the second
check's R1) and integrating EIH inward; the release phase is tuned so the binary's orientation
relative to the CM direction at r0 equals the input's. Output: positions and canonical
momenta as a <problem> block, and predictions from that state.
Q1. The constructed state has a CM 1PN energy within 1e-3 of zero (per unit reduced mass) and a
    binary separation within 15 percent of the input's; its momenta differ from the input's by
    5-20 percent. Refuted outside.
Q2. q = 10: EIH from the consistent state gives a single ejection with the other member inside
    5.35 M (GR-capture proxy). Refuted otherwise.
Q3. q = 4: EIH from the consistent state gives a single ejection (not survived, not
    unsettled). Refuted otherwise.

## Entry 10 (2026-11-19 15:45): outcome of the far-release line; the binary's own 1PN is the cause

Run F-20261119-145315-2d18c52 (90 tasks, 160 s on 13 cores; `figures/fig_scan_far.png`,
`results/scan_far_summary.json`). [VERIFIED as outputs]
- F1 (q = 10, r_p = 17 M retrograde survives in >= 0.9): CONFIRMED, 1.00 (also 1.00 at 15 M).
- F2 (q = 10 prograde, EIH separated within 0.15 of Newton and below 0.3 at 15 and 17 M):
  REFUTED. EIH 0.96 and 0.92, Newton (40 r_t) 0.00 and 0.00, HRNA (2404 data, 4 r_t) 0.92
  and 0.86. At r_p = 7-9 M EIH separates only 0.41-0.51 (Newton 0.78-0.89).
- F3 (a member inside 5.35 M in >= 0.5 at 7-9 M): REFUTED at 9 M (0.43); 1.00 at 7, 0.63 at 8.
- F4 (q = 4 prograde, EIH within 0.15 of Newton at r_p >= 13 M): REFUTED (0.88/0.82/0.95
  against 0.69/0.63/0.46).
- Diagnosis (development check, unregistered: one far-release trajectory at r_p = 17 M): the
  binary separation oscillates between 3.0 and 4.2 from the first orbit on, at 260 M from the
  hole, i.e. the binary is eccentric (e ~ 0.2, Newtonian a ~ 3.3) before any tide acts. Cause
  [VERIFIED by the code's own two-body test, run below; BACKGROUND for the formula]: the
  binary's OWN 1PN dynamics. For the isolated EIH binary the circular relative speed is below
  the Newtonian one: (u/u_N)^2 - 1 = -0.097 at m_b/a = 1/30 (q = 10 binary), -0.151 at 1/20
  (q = 4 binary), -0.028 at 1/100 (computed by `eih.circular_speed_1pn`; the textbook 1PN value
  -(3 - nu) m_b/a gives -0.092, -0.138, -0.0275, the differences being O((m_b/a)^2)). A binary
  given Newtonian-circular velocities at a = 30 m_b or 20 m_b is therefore eccentric at 1PN,
  with a ~10 percent larger semi-major axis - in the EIH reference, and, since 1PN is GR's
  first correction, also in the NR runs whose momenta were set Newtonian [JUDGEMENT].
  The F1-F4 numbers above are for that eccentric binary; they are kept, not used as the
  reference.
- Predictions for the rerun with a 1PN-circular binary (`far_states(binary='1pn')`, the
  default from now on), written before it:
  F2'. q = 10 prograde: EIH separated at r_p = 15 and 17 M below 0.3. Refuted above.
  F4'. q = 4 prograde: EIH separated within 0.2 of Newton (from 40 r_t) at r_p >= 13 M.
  F5'. q = 10 prograde, r_p = 7-9 M: a member inside 5.35 M in >= 0.5 of the phases.

## Entry 11 (2026-11-19 15:50): prediction for T5 (before the run)

T5 (added to `tests/test_eih.py`): for the isolated EIH binary, (u/u_N)^2 - 1 from
`circular_speed_1pn` equals -(3 - nu) m_b/a up to c (m_b/a)^2 with one coefficient c (spread
below 2) over m_b/a = 1/100 ... 1/20; the binary started with that speed stays circular to 1e-6
over five orbits; started with the Newtonian speed it has (r_max - r_min)/(r_max + r_min)
between 0.05 and 0.2 at m_b/a = 1/30 and 1/20. Refuted otherwise. (The development numbers of
entry 10 are replaced by this run's.)

## Entry 12 (2026-11-19 16:05): outcomes of T5 and of the far-release line with a 1PN-circular binary

T5, run F-20261119-145848-6be68b3 (8 of 8 checks pass). [VERIFIED]
- (u/u_N)^2 - 1 of the isolated EIH binary: -0.0973 / -0.1507 / -0.0280 / -0.00922 at
  m_b/a = 1/30, 1/20, 1/100, 1/300; the 1PN formula -(3 - nu) m_b/a gives -0.0917 / -0.1375 /
  -0.0275 / -0.00917; the difference is c (m_b/a)^2 with c = -5.1, -5.3, -4.9, -4.8 (spread
  0.4). A binary started with this speed keeps r_max = r_min to 1e-6 over five orbits.
- Started with the Newtonian speed: (r_max - r_min)/(r_max + r_min) = 0.122 (q = 10 binary,
  a = 3 = 30 m_b), 0.208 (q = 4 binary, a = 5 = 20 m_b), 0.030 (m_b/a = 1/100), 0.0094 (1/300).
  Prediction (0.05-0.2 at 1/30 and 1/20): CONFIRMED at 1/30, REFUTED by 0.008 at 1/20.
  [JUDGEMENT] The binaries of the NR inputs, built with Newtonian-circular momenta at a = 30
  and 20 m_b, are eccentric at 1PN (e ~ 0.1-0.2) before any tide - in addition to the 1PN
  effects of the hole's potential.

Far-release line with the 1PN-circular binary, run F-20261119-145826-d4da8e1 (90 tasks,
131 s; `figures/fig_scan_far.png` now this run, `results/scan_far_summary.json`). [VERIFIED as
outputs]
- q = 10 prograde, separated EIH / Newton (40 r_t) / HRNA (2404, 4 r_t): r_p = 7: 0.42/0.89/
  0.99; 8: 0.45/0.85/0.99; 9: 0.91/0.78/0.99; 10: 0.54/0.71/0.98; 11: 0.72/0.63/0.96; 12: 0.92/
  0.54/0.97; 13: 0.94/0.39/0.96; 15: 0.94/0.00/0.92; 17: 0.85/0.00/0.86. EIH member inside
  5.35 M: 1.00, 0.98, 0.94 at 7, 8, 9 M.
- q = 10 retrograde: EIH separates 0.56-0.08 at 7-12 M (Newton 0 everywhere, HRNA 0.83-0.00),
  survives 1.00 at 13-17 M.
- q = 4 prograde: EIH 0.57/0.49/0.37/0.19/0.53/0.91 at 9.82-16 M against Newton 0.81-0.46 and
  HRNA 0.98-0.94.
- The 1PN energy changes along the run by a median 0.01-0.44 units, against the binary's
  binding energy m1 m2/(2a) = 0.23 units (q = 10) and 0.40 units (q = 4).
- F2' (q = 10 prograde, EIH separated below 0.3 at 15 and 17 M): REFUTED (0.94, 0.85).
  F4' (q = 4 prograde, EIH within 0.2 of Newton at r_p >= 13 M): REFUTED at 13 M (0.19 against
  0.69) and 16 M (0.91 against 0.46); holds at 14 M (0.53 against 0.63).
  F5' (q = 10 prograde, a member inside 5.35 M in >= 0.5 at 7-9 M): CONFIRMED (1.00/0.98/0.94).
- The fraction is not a smooth function of r_p for EIH (q = 10 prograde 0.91 at 9 M, 0.54 at
  10 M; q = 4 0.19 at 13 M, 0.91 at 16 M), unlike Newton. [JUDGEMENT] With 360 phases the
  sampling error is below 0.03, so the jumps are a property of the EIH set-up at fixed release
  radius; whether they converge in the release radius is the next test.

Prediction for the release-radius test (written before it): if EIH's separation at q = 10
prograde, r_p = 15 and 17 M, is a tidal effect of the passage, the separated fraction changes
by less than 0.1 between release at 20, 40 and 80 r_t (Newton is converged there: newton3 P5/P6).
Refuted if it changes by more than 0.1.
(The first two release-radius runs, F-20261119-150157-424bab2 and F-20261119-150159-4a27aa2,
were stopped at once: the figure code of scan_far.py assumed all three models and would have
failed with `--models eihfar`; fixed, rerun below.)

## Entry 13 (2026-11-19 16:10): prediction for T6 (driver interface), before the run

T6: for three phases of the q = 10, r_p = 8 M encounter, `eih.run_encounter(law='newton')`
gives newton3's outcome and the ejected member's energy to 1e-6 units (two different DOP853
implementations at rtol 1e-11), and `run_encounter(law='eih')` equals `eih.scatter` exactly.
Refuted otherwise.
