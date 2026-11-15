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
