# JOURNAL of the F-hills package newton3 (F-pre-1, Newtonian three-body baseline)

Helper of F-hills, one work package. Entries are appended; nothing is rewritten.
Sources (fetched with nrpic-fetch-arxiv, read only, never committed):
SKR = arXiv:0911.1136 v1 `kb-data/raw/arxiv/0911.1136/v1/src/prp.tex`;
KHSR = arXiv:1201.4794 v1 `kb-data/raw/arxiv/1201.4794/v1/src/ms.tex`;
BKRS = arXiv:1804.02911 v1 `kb-data/raw/arxiv/1804.02911/v1/src/mnras.tex`.
Locators below are `<label>:<line>` in these files.

## 2026-11-15 start: predictions written before any code ran

Scope [JUDGEMENT]. Decision 0010: the three-point-mass ordinary differential equations are
a semi-analytic reference solution and live outside `athenak/src/`; nothing here is a
simulation capability of the program. Two models are written: (i) the restricted
parabolic equations of SKR (eqs. at SKR:223-259, energy SKR:350-357, BKRS:181-188), which
is what all three papers integrate for their scans; (ii) the full Newtonian three-body
problem (18 first-order equations), which is the driver the later comparisons call and
which must tend to (i) as M/m grows. Integrator: my own vectorised Dormand-Prince 8(5,3)
with a step size per trajectory, coefficients taken from the installed SciPy; a few
cases are cross-checked with SciPy's `solve_ivp` (independent code path).

Conventions (to be stated in the README and checked by tests): x axis = pericentre
direction of the binary's centre-of-mass orbit, orbit in the x-y plane with angular
momentum along +z; binary relative vector r = r2 - r1 (secondary minus primary);
binary rotation axis l = (cos th, sin th cos vphi, sin th sin vphi) (BKRS:240-244,
BKRS:286), coplanar prograde th = vphi = pi/2, retrograde th = pi/2, vphi = -pi/2;
effective phase phi at the pericentre time, phase at the start phi0 = phi + omega t0
measured in the binary's own sense of rotation from the projection of x onto the binary
plane (SKR:601-610 for the coplanar case, where for retrograde orbits SKR's phi equals
minus mine); D = r_p / r_t, r_t = a (M/m)^(1/3) (SKR:88, SKR:349); energies in units of
(G m1 m2 / a)(M/m)^(1/3) (SKR:793, BKRS:417).

P0 (unit tests, before the scans). (a) Two-body Kepler orbit over 20 periods returns to
the analytic state to better than 1e-8 relative at rtol 1e-11. (b) Full three-body
energy and angular momentum conserved to 1e-9 relative through a D = 0.1 passage.
(c) The analytic free solutions of SKR:274-307 solve the tidal-only restricted
equations: numerical integration from their initial data stays within 1e-8 of the closed
forms; the energy bracket of SKR:350-357 is 20 B for the eccentricity solution
(SKR:397-401) and 0 for the five others. (d) The vectorised integrator and SciPy
DOP853 agree on the final restricted energy to 1e-7 for ten random cases. (e) The
initial data have zero total momentum, centre of mass at the origin, binary separation a
and the centre-of-mass orbit's pericentre r_p. Refuted by any of these failing; a
failure means a bug, not physics.

P1 (coplanar restricted scan, 3000 equally spaced phases in [0, pi) per D, as SKR:763).
Reproduces SKR's printed numbers: largest D with disruption 2.1 prograde and 0.44
retrograde (SKR:846-847, SKR:777-779), to +-0.03; prograde disruption probability
maximal near D = 0.15 (SKR:854) and 98.0-98.8 percent for 0.06 < D < 0.3 (SKR:1087);
both directions saturate near 80 percent for D < 0.1 (SKR:735-736, KHSR:677-679) and the
survival fraction in the deep limit is 19 percent (SKR:748-749) to +-1.5 points;
survival windows in the deep limit -0.31 pi < phi < -0.12 pi and 0.69 pi < phi < 0.88 pi
(SKR:785) to +-0.02 pi (prograde, D = 1e-5 standing in for the radial problem);
maximal |E| 27.3 prograde near D = 0.1 and 1.8 retrograde (SKR:848-849) within 10
percent (the prograde peak is a narrow phase spike; 3000 phases may under-resolve it);
mean ejection speed in the deep limit 0.99 sqrt(2 G m2/a)(M/m)^(1/6) (SKR:994), i.e.
<sqrt|E|> = 0.99 +- 0.02. Refuted if any of these misses its tolerance; then I first
check the convention (phase origin, start radius 10 r_t of SKR:599) before suspecting
the paper.

P2 (general orientation, restricted). Orientation on a Fibonacci lattice over the whole
sphere (N_ori points), phase N_pha equally spaced in [0, pi); BKRS used 2000 x 200
(BKRS:352-357) and report < 0.3 percent change for 4x fewer points (BKRS:605-606).
With N_ori = 512, N_pha = 64 the disruption probability follows the BKRS fit
(BKRS:372-376) within 1.5 points for D <= 1.8, plateau 87-88 percent at D << 1
(BKRS:368-370, BKRS:606); the mean |E| over disrupted cases follows the BKRS fit
(BKRS:433-439) within 3 percent for D <= 1.5. Deep limit by inclination: survivors only
for 0.15 pi < th < 0.85 pi, minimum disruption about 80 percent at th = pi/2
(BKRS:507-509); <|E|>(pi/2)/<|E|>(0) between 1.4 and 1.7 (BKRS:524-525). Collision
probability with r_min < a/5 about 5-7 percent for D < 0.1 and about 14 percent near
D = 1.6 (BKRS:762-764), to +-2 points (my r_min is sampled at step ends only, a slight
overestimate of the minimum separation). Refuted if the fit is missed by more than
the tolerance over a range of D, not at a single point.

P3 (full three-body against the restricted limit). SKR set-up M/m = 1e6, m1/m2 = 3,
start 10 r_t: the full-problem energy change Delta E = (m1/m)E2 - (m2/m)E1 (KHSR:1103)
agrees with the restricted one; SKR:631 and KHSR:604-605 report 0.1 percent. I predict
the median relative difference over phases is below 1 percent at M/m = 1e6 and scales
like (m/M)^(1/3) through M/m = 1e3, 1e4, 1e5 [JUDGEMENT: the first neglected term of
the tidal expansion is of relative order r/r_m ~ (m/M)^(1/3)]. At M/m = 10 the
disruption probability and the energies differ from the restricted limit at the level
of tens of percent; I do not predict the sign. Refuted if the M/m = 1e6 difference
exceeds 1 percent, or if the difference does not decrease with M/m.

P4 (driver). `initial_state` followed by `scatter` from the same parameters gives the
same outcome as the vectorised scan; the outcome is insensitive (energy change within
1 percent, same disruption flag for > 99 percent of phases) to moving the start from
10 r_t to 20 r_t when the effective phase is held fixed, for M/m = 1e6. At M/m = 10 the
start distance matters more because the tidal field at 10 r_t is not negligible
[JUDGEMENT]; this is measured, not predicted.

## 2026-11-15 P0 outcome (run F-hills-20261115-130253-6fc800e, commit 6fc800e)

- did: wrote `hills3/` (integrate.py, orbits.py, restricted.py, threebody.py,
  reference.py) and `tests/test_hills3.py`; ran the tests.
- found: the first run failed two of the predictions as I had worded them. (a) Kepler
  e = 0.6, 20 periods, rtol 1e-11: return error 1.1e-7, not < 1e-8. SciPy's DOP853 on the
  same problem gives 1.4e-7 with the same number of accepted steps (1173 vs 1174), and
  both reach 1e-9 at rtol 1e-13: the integrator reproduces SciPy's DOP853 step for step,
  and my tolerance-to-global-error guess was a factor 10 too optimistic. (b) Total-energy
  error 3e-8 relative to E_total at rtol 1e-11 for M/m = 1e3, D = 0.1; E_total is only
  the binary binding energy, a tiny difference of large terms; measured against the
  energy unit (G m1 m2/a)(M/m)^(1/3) it is 1.8e-9, at rtol 1e-13 it is 4e-10 of E_total;
  SciPy's DOP853 gives 3.8e-8 on the same case. The tests now state these measured
  bounds (Kepler at rtol 1e-13 plus agreement with SciPy within a factor 2; energy
  against the energy unit). Not a bug: a run in which it could have been one (SciPy
  comparison) shows the same numbers.
- found: free solutions of SKR solve the tidal-only equations to < 1e-8; the energy
  bracket is 20 for the eccentricity solution and 0 for the others (confirms the energy
  formula and its normalisation, SKR prp.tex:397-401); E2(phi + pi) = -E2(phi) to 1e-8;
  restricted energies agree with an independent SciPy integration to 1e-7; driver final
  state agrees with SciPy to 1e-6 relative; initial data: zero momentum, CoM at origin,
  binary a and e_b, orientation, CoM conic pericentre and eccentricity to 1e-9 or better.
- found (smoke test, not a registered result): about 1 in 3000 coplanar trajectories
  stalls (step below 1e-14 t) in a near head-on approach of the two members
  (r_min ~ 1e-8 a); they are bound at the stall. They are excluded from the fractions and
  counted ("fail"); a point-mass collision is outside the model anyway.

## 2026-11-15 scans P1/P2 finished; a deep-limit anomaly, prediction P5 before the check

- did: runs F-hills-20261115-130237-cbfaf6b (coplanar, 3000 phases per D, 207 D values
  x 2 directions) and F-hills-20261115-130239-cbfaf6b (orientation: 512 x 64 isotropic
  per D for 27 D; 31 inclinations x 32 azimuths x 64 phases for 8 D). Not yet analysed.
- found in the logs: below D ~ 5e-5 the disruption probability rises again (coplanar
  0.82 at D = 5.6e-5, 0.84 at 3.2e-5, 0.91 at 1.8e-5, 0.977 at 1e-5) and at D = 1e-5 the
  inclination scan gives <|E|> = 10.9 against about 1 at D = 1e-2. Suspected cause
  (not yet tested): loss of precision. Near pericentre the zero-energy free solution
  'time of periapsis' (SKR prp.tex:279-282) has an amplitude ~1/D and the energy is a
  difference of terms of that size divided by D, so at rtol 1e-10 the energy error grows
  like 1/D.
- prediction P5 (convergence run, written before it runs): (a) D >= 1e-4: P_dis and
  <|E|> change by less than 0.2 points and 0.2 percent between rtol 1e-10 and 1e-13;
  (b) D = 1e-5 and 3.2e-5: the rtol 1e-10 values change by more than that, and at rtol
  1e-12 and 1e-13 they agree with each other and with D = 1e-4 (coplanar P_dis 0.80-0.83,
  SKR's radial limit 0.81); (c) end radius 30 -> 100 r_t: P_dis within 0.2 points,
  <|E|> within 0.2 percent; start radius 10 -> 20 r_t at fixed effective phase: P_dis
  within 0.5 points, <|E|> within 1 percent (D = 1e-3, 0.1, 1, 2). Refuted if (b) does not
  converge (then the cause is not the tolerance) or (c) misses. If (b) holds, the deep
  limit is quoted from D = 1e-4 (and the rtol 1e-13 points), and the D < 1e-4 values of
  the two scans are discarded.

## 2026-11-15 P5 outcome (run F-hills-20261115-131754-907e5fe); prediction P6

- found (a): D = 1e-3, 0.1, 1 are converged at rtol 1e-10 (P_dis and <|E|> identical to
  four digits at 1e-12 and 1e-13). D = 1e-4 is NOT (P 0.8150 vs 0.8100, <|E|> 1.092 vs
  1.038 at rtol 1e-10 vs 1e-13): prediction (a) refuted at D = 1e-4; the safe limit of
  the rtol 1e-10 scans is D >= 1e-3.
- found (b): the suspected cause holds; the anomaly is the tolerance. At rtol 1e-12 and
  1e-13 the rise of P_dis at small D disappears: P_dis = 0.808, 0.808, 0.808, 0.810 at
  D = 1e-5, 1.8e-5, 3.2e-5, 1e-4 (rtol 1e-13, coplanar prograde, 600 phases), i.e. 19.0-
  19.2 percent survival against SKR's 19 percent for the radial problem (prp.tex:748-749).
  <|E|> at D = 1e-5 is 1.165 (1e-12) vs 1.046 (1e-13): still moving at D = 1e-5, so the
  deep-limit energy is taken from D = 1e-4 at rtol 1e-12 (1.038, converged).
- found (c): end radius 30 -> 100 r_t changes nothing (P identical, <|E|> < 0.1 percent):
  confirmed. Start radius 10 -> 20 r_t: P_dis +0.0 (D = 0.1), -0.5 points (D = 1),
  -0.17 (D = 1e-3), +1.7 points (D = 2); <|E|> +2.6 percent (D = 1e-3), +0.4 (0.1),
  +0.1 (1), +3.8 (2). Prediction (c) refuted at D = 1e-3 and D = 2: the start radius of
  10 r_t (SKR prp.tex:599) is not converged at the percent level everywhere.
- decision: results of the rtol 1e-10 scans are used for D >= 1e-3 only; the deep points
  are recomputed at rtol 1e-13 (coplanar, D = 1e-5 .. 5.6e-4) and 1e-12 (inclination scan
  at D = 1e-4); the literature comparisons keep the papers' start radius 10 r_t, and the
  start-radius dependence is measured separately (P6) and stated as a systematic.
- prediction P6 (written before the run): with k0 in {10, 20, 40, 80} r_t at D in
  {1e-3, 0.1, 0.5, 1, 1.5, 2} (coplanar prograde, 1200 phases, rtol 1e-12), P_dis and
  <|E|> converge in k0: k0 = 40 and 80 agree within 0.3 points and 0.5 percent, and the
  k0 = 10 values differ from k0 = 80 by at most 2 points and 4 percent. Refuted if 40 vs 80
  still differ by more, or the k0 = 10 offsets exceed these bounds.

## 2026-11-15 P1 analysed (run F-hills-20261115-132435-7d0c6dd); prediction P7

- found (P1, against SKR's printed numbers; coplanar scan F-hills-20261115-130237-cbfaf6b
  for D >= 1e-3 plus the rtol 1e-13 deep supplement F-hills-20261115-132156-efddfc0):
  prograde: last disrupting D = 2.085, none at 2.090 (SKR 2.1: agrees to its rounding);
  P_dis maximal 0.988 at D = 0.16 (SKR 0.15), range 0.984-0.988 for 0.06 < D < 0.3
  (SKR 0.980-0.988); max |E| = 27.15 at D = 0.1 (SKR 27.3); deep survival 19.3 percent at
  D = 1e-5 (SKR radial 19); survival windows at D = 1e-5: 0.693-0.886 pi and
  -0.307 to -0.114 pi (SKR 0.69-0.88 and -0.31 to -0.12); <sqrt|E|> = 0.999 (SKR 0.99).
  retrograde: max |E| 1.84 (SKR 1.8); deep survival 19.9 percent; BUT last disrupting
  D = 0.405, none at 0.410, against SKR's 0.44 (prp.tex:778-779, 847): prediction P1
  (0.44 +- 0.03) refuted for the retrograde edge. D-uniform energy averages: prograde
  1.47 (SKR 1.46) when D is uniform and the average is over disrupted cases; retrograde
  0.55 (that definition) or 0.47 (unweighted over the disrupting range) against SKR 0.50;
  both directions together 1.38 (SKR 1.36). SKR do not state the definition; I do not
  claim a match for the retrograde value. Survivors that are harder than initially:
  87 percent at D = 1e-5 (SKR 'about 90 percent', radial).
- prediction P7 (before the digitiser runs): SKR's fig. 4 curves (read from the MATLAB EPS
  in kb-data) and mine agree to within 0.02 in P_dis for D < 0.3 in both directions; the
  largest differences sit at the edges (retrograde near 0.4-0.44, prograde near 2.0-2.1).
  Fig. 7 (phase-averaged and maximal |E| for fixed a): median relative difference below
  3 percent for <|E|>, below 15 percent for max|E| (a narrow-spike statistic that depends
  on the phase grid). If SKR's retrograde curve reaches zero near 0.41 the 0.44 of the text
  is a statement about a different quantity or a typo; if it reaches zero at 0.44 the
  discrepancy is real and its cause is open.

## 2026-11-15 P7 outcome (run F-hills-20261115-132703-0bfc352), P6 outcome (run F-hills-20261115-132433-7d0c6dd); prediction P8

- found (P7): SKR fig. 4 and fig. 7 curves read from the EPS. Prograde: P_dis within
  0.004 of SKR for D < 0.3 (median 0.0014; largest 0.037 at the steep edge D = 2.07);
  <|E|> median relative difference 0.17 percent, max|E| 0.08 percent (90th pct 1.1).
  Retrograde: <|E|> 0.2 percent, max|E| 0.3 percent, but P_dis is systematically BELOW
  SKR's curve: -0.008 at D = 0.01, -0.03 at 0.1, -0.066 at 0.3, -0.16 at 0.4, and SKR's
  curve reaches zero at D = 0.445 (their text: 0.44) where mine does at 0.41. Prediction
  P7 holds for prograde and for the energies, fails for the retrograde P_dis.
- observation (not yet a cause): the missing retrograde disruptions match the number of my
  retrograde survivors whose final semi-major axis exceeds about 3 a (D = 0.1: 0.030 vs
  0.032; 0.3: 0.066 vs 0.076; 0.36: 0.095 vs 0.113; 0.4: 0.16 vs 0.19), while prograde
  survivors are almost never that wide and prograde agrees. My survivors are bound (two-body
  energy < 0) with apocentre inside half the Hill radius at 30 r_t, and P5 showed that the
  classification does not change between 30 and 100 r_t, so I hold them as survivors.
  Hypothesis H1: SKR count widened survivors as disrupted (a separation or energy criterion
  at a finite time).
- found (P6): start radius 40 vs 80 r_t: P_dis within 0.25 points and <|E|> within 0.25
  percent at all six D (converged, prediction holds). k0 = 10 vs 80: P_dis -0.17, -0.09,
  0.0, +0.26, +1.41, -2.17 points and <|E|> -1.8, +0.2, +0.3, +0.4, +0.2, -2.7 percent at
  D = 1e-3, 0.1, 0.5, 1, 1.5, 2. The P_dis bound of 2 points is exceeded at D = 2
  (2.2 points): prediction P6 fails narrowly there. SKR's fig. 4 at D = 1.5 (0.797) sits
  with my k0 = 10 value (0.792), not with the converged one (0.777): consistent with SKR's
  stated start of 10 r_t.
- prediction P8 (before the run): (i) BKRS's fig. 2 (dis_with_D.eps, read as text) has a
  coplanar retrograde curve; if H1 is about SKR's criterion only, BKRS's retrograde curve
  lies on mine (within 0.02) and their isotropic curve within 0.015 of mine. If BKRS's
  retrograde curve lies on SKR's, both used the same criterion and I test H1 directly:
  (ii) counting my survivors with a_f > X a as disrupted, one X between 2 and 4 brings my
  retrograde P_dis within 0.01 of SKR's at every D < 0.44 while leaving prograde within
  0.005. H1 is refuted if no single X does this.

## 2026-11-15 outcomes of P2, P3, P4, P8 and the finite mass-ratio scan

- P8 (run F-hills-20261115-132942-2f7ad7f): (i) BKRS fig. 2 read from the EPS: isotropic
  curve within 0.009 of mine (median 0.0025), coplanar prograde within 0.005 for D < 0.3;
  their coplanar retrograde curve lies ABOVE mine like SKR's (up to 0.06 for D < 0.3), so
  BKRS used SKR's criterion. (ii) H1 survives a test that could have failed: counting my
  survivors with a_f > 3.5 a as disrupted brings my retrograde P_dis within 0.009 of SKR's
  curve at every D <= 0.6 and puts the edge at 0.445 (SKR: 0.44); prograde stays within
  0.0024 for D < 0.3. X = 3 and X = 4 are worse (0.087, 0.075), so the match is specific.
  I still do not know SKR's actual criterion; H1 is a reproduction, not their stated rule.
- P2 (analysis F-hills-20261115-133200-05ee76a): holds. P_dis within 0.0094 of the BKRS
  fit for D <= 1 and 0.013 for D <= 1.8 (predicted 0.015); mean |E| within 1.7 percent for
  D <= 1.5 (predicted 3); deep plateau 0.876-0.878; min P_dis 0.804 near theta = pi/2;
  energy ratio pi/2 over 0 between 1.44 and 1.71 for D = 1e-4 .. 0.3 (BKRS 1.4-1.7);
  collision probability 5.4-7.3 percent for D < 0.1 and 14.2 percent near D = 1.6. One
  miss in wording: I predicted survivors only for theta > 0.15 pi; with my threshold
  (P_dis < 0.999) the first theta with survivors at D = 1e-4 is 0.117 pi. BKRS say the
  surviving probability becomes "significant" above 0.15 pi; at 0.117-0.15 pi my P_dis is
  0.99-0.999, so not significant. Three analysis attempts failed on my own indexing bugs
  (runs F-hills-20261115-133009/133013-2f7ad7f, F-hills-20261115-133034-bf31889, recorded
  as failed) before the fixed analysis ran.
- P3 (analysis F-hills-20261115-133203-05ee76a): first half holds: at M/m = 1e6 the
  median relative difference is 6.0e-4 (D = 1) and 7.3e-4 (D = 0.1), SKR's single example
  2.4e-4 (SKR quote 0.1 percent). Second half only partly: for D = 1 the difference falls
  by 2.1-2.6 per decade of M/m between 1e3 and 1e6, as (m/M)^(1/3) predicts, but for
  D = 0.1 it falls by 4.5-5.7 per decade, closer to (m/M)^(2/3). I have no tested cause.
  At M/m = 10: 26 and 59 percent, with 11 and 25 percent of the phases changing fate.
- P4 (analysis F-hills-20261115-133205-05ee76a): refuted as worded. Starting at 10 instead
  of 40 r_t keeps the outcome of 95 percent (M/m = 1e6) and 97 percent (M/m = 10) of the
  phases, not > 99 percent; energy change within 0.6 and 0.8 percent (prediction held).
  The figure shows the cause directly: the curves shift sideways, i.e. the tidal field
  before 10 r_t shifts the effective phase, so individual phases near window edges change
  fate while phase averages do not (P6). Consequence for F-pre-3: compare NR with the
  driver started from the same initial data, not from the same effective phase.
- finite mass ratio (scan F-hills-20261115-132019-bfe00a9, analysis
  F-hills-20261115-133207-05ee76a): measured, no prediction beyond P3's "tens of percent".
  Isotropic P_dis at M/m = 10 within 0.04 of the restricted limit for D >= 0.3, higher at
  D = 0.1 (0.93 vs 0.86, 8.6 percent both captured); phase-averaged |dE| 0.49-0.79 of the
  restricted value for 0.1 <= D <= 1; coplanar retrograde disruption extends to D = 0.5
  (37 percent) where the restricted limit has none.
- status of the package: deliverables exist and are tested (driver, restricted reference,
  reproductions with locators, figures looked at). Open: eccentric binaries and
  non-parabolic orbits not compared with the literature; no second-agent check yet.

## 2026-11-15 wave 2, package newton3_fix: predictions written before any code ran

Defect (lead's V5b, `stage/G0/checks/lead_checks.py:436-480`, `v5b_summary.json`, run
F-hills-20261115-145559-a314517): `threebody._pair_energy` gives each member's two-body
energy with M alone. When one member is captured, M moves on a small orbit about the
barycentre of (M, captured member), and the ejected member's energy measured against M
oscillates with that inner orbit and never settles (q = 10: 1.474 to 1.845 units after
t = 300; q = 4: 0.989 to 1.723), while the energy against the barycentre of M and the
captured member is constant (1.6127, 1.3119).

Corrected definition [JUDGEMENT on the choice, the algebra is exact]: Jacobi split of the
hierarchy left at the end. Inner pair = M and the member with the lower specific two-body
energy with M; outer body = the other member, measured against the barycentre of the
inner pair. E_in = mu_in |r'|^2/2 - G M m_c/r, E_out = mu_out |R'|^2/2 - G (M+m_c) m_e/R,
mu_in = M m_c/(M+m_c), mu_out = m_e (M+m_c)/M_tot. Then E_tot = E_in + E_out + W exactly
(zero total momentum), with W the tidal coupling, O(G m_e mu_in r^2/R^3); the dipole term
cancels because R is measured from the inner barycentre. Old minus new for the ejected
member contains mu_eM beta R'.r' (beta = m_c/(M+m_c)), which oscillates with the inner
orbit at a fixed amplitude: a relative error of order m/M that never decays. For the
captured member the old and new definitions coincide. Survivors (m1-m2 bound) have no
separate member energies; E1, E2, dE become NaN for them and the conserved pair (E12,
E_orb) is reported instead. dE keeps KHSR's combination (m1/m) E2 - (m2/m) E1 (ms.tex:1103)
of the corrected energies; with E1 + E2 = E_tot - W it equals E2 - (m2/m)(E_tot - W) and
tends to the restricted E2 as M/m -> infinity.

Predictions (refuted by the stated outcome):

Q1 (definition test, unit test + figure). Full Newton from the start states of the two
passages (q = 10: M = 1, m = 0.1, a = 3, r_p = 8, phase 130 deg; q = 4: m = 0.25, a = 5,
phase 127 deg; integrated from 10 r_t and read at 4 r_t, as the input files) to t = 1500:
for t >= 300 the corrected E_ej varies by less than 1e-4 units peak to peak and
E_ej + E_cap - E_tot by less than 1e-4 units; the old E_ej varies by more than 0.1 units.
E_ej(new) = 1.6127 (q = 10) and 1.3119 (q = 4) within 1e-3 (V5b's barycentric values);
E_cap(new) = E_tot - E_ej, about -0.232 - 1.613 = -1.85 (q = 10) and -0.315 - 1.312 =
-1.63 (q = 4), using E_tot ~ -m1 m2/(2a) = -(1/2)(m/M)^(1/3) units. Refuted if the new
energy varies by more than 1e-4 or the sum identity misses by more than 1e-4.

Q2 (end-time independence). scatter() at k_end = 30 and 100 r_t, coplanar prograde,
M/m = 10 and 4, D = 0.5 and 1.2, 128 phases: for single ejections the corrected dE differs
between the two end times by less than 1e-3 units in every sample; the old dE differs by
more than 0.05 units in some samples (oscillation amplitude ~ (m/M) of |E|). Refuted if
the new definition misses 1e-3 anywhere, or the old never exceeds 0.05.

Q3 (restricted limit unchanged). At M/m = 1e6 corrected and old dE agree to 1e-5
relative; P3's median differences at M/m >= 1e3 (6.0e-4 and 7.3e-4 at 1e6) change by less
than 10 percent of themselves. Refuted otherwise.

Q4 (finite-q rerun). Outcome classes change for less than 1 percent of the samples at
M/m = 10 (only marginal ejections, whose old energy crossed zero in its oscillation);
P_dis therefore changes by less than 0.01 at every D. The phase-averaged |dE| at M/m = 10
changes by less than 5 percent of itself at every D (the oscillation is zero-mean apart
from an offset of a few percent), so the statement "0.49-0.79 of the restricted value for
0.1 <= D <= 1" survives within 0.05. The P3 differences at M/m = 10 (26 and 59 percent)
change by less than 5 points. Refuted if any of these bounds is exceeded; then the old
finite-q numbers were biased by more than an oscillation and every statement built on
them is re-examined.

Q5 (passages q = 4 and 10 from the input-file states). Outcome unchanged (m1 ejected, m2
captured), E_ej as Q1; the captured orbit (a = 7.55, e = 0.247, pericentre 5.68 M at
q = 10, lead V5) is unchanged because the captured member's energy has the same
definition. Phase scans over 360 phases at the input configurations: fractions of each
outcome change by less than 0.01; the ejection energies by up to ~(m/M) of themselves.

Q6 (multi-puncture form). A new driver function returns, for a requested start distance
r0 (and optionally the distance k_from r_t from which the Newtonian approach is
integrated), the `<problem>` block of `nrpic_cf` (coord/INTERFACES/multi_puncture.md
section 2): comp<c>_mass, _x1..3, _p1..3 (P = m v), _s1..3, _corr. With k_from = 10 and
r0 = 4 r_t it reproduces the positions and momenta of
`three_punctures/inputs/hills_q10_m8.athinput` and `hills_q4_m8.athinput` (made by linear
interpolation of a 20000-sample trajectory) within 1e-4 in position and 1e-6 in momentum;
the block parses back to the same numbers; total momentum zero and barycentre at the
origin to 1e-12; the binary centre of mass at r0 to 1e-9. Refuted by any miss.

## 2026-11-15 first (unregistered) pytest of the new tests: Q1 sum part refuted as worded

- found: 14 of 15 tests pass. Q1's peak-to-peak parts hold (corrected E_ej constant to
  < 1e-4 units for t >= 300 in both passages, old E_ej varies by > 0.1); the sum part does
  not: max |E1 + E2 - E_tot| over t >= 300 is 1.23e-4 units at q = 10 (bound 1e-4), at
  t = 300, falling to 3.4e-7 at t = 1500. The residual is the tidal coupling W of the
  identity E_tot = E_in + E_out + W, which I under-estimated at t = 300.
- change: the test now checks the identity with W (exact, 1e-10 units) and the decay of
  W: |W| < 2e-4 units for t >= 300 and < 1e-5 for t >= 1000 (prediction from W ~ R^-3 with
  R growing about 3 times from t = 300 to 1000: 1.2e-4 x 0.03 = 4e-6). The registered test
  run follows.
- found (second unregistered pytest): Q1's peak-to-peak part is refuted for q = 4 as well:
  the corrected E_ej varies by 1.54e-4 units over t >= 300 (bound 1e-4); it drifts
  monotonically from 1.31206 to 1.31191 (no oscillation), the same spread as V5b's own
  barycentric values (1.311866-1.312020, v5b_summary.json), which I should have used. The
  cause is the same coupling W: the remaining change of E_out after time t goes like
  W(t) ~ t^-3.
- change: peak-to-peak < 3e-4 units for t >= 300 and < 1e-5 for t >= 1000 (prediction:
  1.5e-4 x (300/1000)^3 = 4e-6); the old definition still has to exceed 0.1.
- found (third unregistered pytest): |E1 + E2 - E_tot| = |W| reaches 3.6e-4 units at
  t = 300 for q = 4 (bound 2e-4 set from q = 10). Absolute bounds at t = 300 only measure
  the size of the coupling there. Final form of the test (no further change after the
  registered run): identity with W exact (1e-10); for t >= 300 the corrected energy varies
  at least 1000 times less than the old one, which varies by > 0.1; for t >= 1000 both the
  corrected energy's variation and |W| are below 1e-5 units; E_ej at the end within 1e-3
  of V5b's value.
