# newton3: Newtonian three-body baseline of the Hills mechanism (F-pre-1)

Helper package of F-hills (brief S12, track sheet 9.9, F-pre-1). It holds the Newtonian
frame of reference that every later comparison of Track F uses: the restricted parabolic
three-body problem of Sari, Kobayashi & Rossi (SKR, arXiv:0911.1136) for the literature
scans, and a full Newtonian three-body scattering driver that takes the parameters of a
run of the code and returns the initial data of the three-black-hole runs.

Decision 0010: three point masses obeying ordinary differential equations are a
semi-analytic reference solution; nothing here is a simulation capability, nothing
outside the repository was adopted (no REBOUND), and nothing here belongs in
`athenak/src/`. Prediction-first record: `JOURNAL.md` (P0 to P8).

## Contents

| Path | What |
|---|---|
| `hills3/integrate.py` | vectorised adaptive Dormand-Prince 8(5,3) for many trajectories at once (per-trajectory time and step; tableau from the installed SciPy). Reproduces SciPy's DOP853 step for step (P0). |
| `hills3/orbits.py` | conventions (frame, orientation, phase), Kepler solver, conic states and times, Fibonacci sphere |
| `hills3/restricted.py` | restricted parabolic equations (SKR prp.tex:223-259), energy (prp.tex:350-357), outcome classification |
| `hills3/threebody.py` | **the driver**: `HillsSetup`, `initial_state`, `initial_state_json`, `scatter`, `trajectory`; wave 2: `member_energies`, `classify`, `evolve_states` (corrected member energies), `puncture_state`, `multi_puncture_block`, `parse_problem_block` (initial data in the multi-puncture form) |
| `hills3/reference.py` | every literature number used, with its locator (file:line of the paper source in `kb-data/raw/arxiv/`) |
| `tests/test_hills3.py` | 15 unit tests (Kepler, SKR free solutions, energy bracket, conservation, initial-data invariants, SciPy cross-checks, JSON round trip; wave 2: Jacobi identity, member energy after a capture, restricted limit, end-time independence, puncture input) |
| `scripts/` | scans (`scan_coplanar.py`, `scan_general.py`, `compare_full.py`, `convergence.py`), analysis and figures (`analyze.py`), curve readers (`digitize_skr.py`, `digitize_bkrs.py`), run registration (`runlib.py`), registered test run (`run_tests.py`); wave 2: `energy_definition.py` (Q1-Q3), `passages.py` (Q5), `puncture_input.py` (initial data from the shell) |
| `figures/` | every figure (PDF and PNG), style `python/nrpic/figstyle.py` |
| `results/` | the numbers behind the statements below, one JSON per analysis (copied from the analysis run directories) |

Run outputs live in `scratch/F-hills/<run_id>/`; manifests in `tracks/F-hills/runs/<run_id>/`.
Digitised third-party curves stay in the run directories (not committed).

## Conventions (checked by the tests)

- Units: G = 1; any consistent mass and length units. Bodies `[M, m1, m2]`, m = m1 + m2.
- Frame: barycentric. The binary's centre-of-mass orbit about M (Kepler conic of
  R = x_cm - x_M with mu = G (M + m), eccentricity `e_orb`, default 1 = parabolic) lies in
  the x-y plane, pericentre along +x, angular momentum along +z.
- r_t = a (M/m)^(1/3) (SKR prp.tex:88); penetration factor D = r_p / r_t (prp.tex:349).
- Binary orientation: unit angular momentum l = (cos th, sin th cos vphi, sin th sin vphi)
  (BKRS arXiv:1804.02911 mnras.tex:240-244, 286). Coplanar prograde th = vphi = pi/2;
  retrograde th = pi/2, vphi = -pi/2.
- Phase: the binary's mean anomaly extrapolated without tides to the pericentre time of the
  centre-of-mass conic ("effective phase", SKR prp.tex:601-610), measured in the binary's own
  sense of rotation from the projection of +x onto the binary plane; periapsis direction
  `varpi` from the same reference. For coplanar retrograde orbits SKR's phase is minus ours
  (`restricted.coplanar_phase` converts).
- Energies in units of (G m1 m2 / a)(M/m)^(1/3) (SKR prp.tex:793). Full problem (wave 2,
  section "Member energies at finite mass ratio"): E1, E2 are the Jacobi energies of the
  hierarchy left at the end (captured member against M, ejected member against the
  barycentre of M and the captured member), dE = (m1/m) E2 - (m2/m) E1 (KHSR
  arXiv:1201.4794 ms.tex:1103); NaN while m1-m2 are bound. Restricted: E2 = -E1. The
  wave-1 definition (each member against M alone) is kept as E1_M, E2_M, dE_M, outcome_M.
- Outcome: survived = m1-m2 bound with apocentre inside half its Hill radius at the end
  (default: the unperturbed conic at 30 r_t outbound; P5: 100 r_t changes nothing).
  Otherwise disrupted, split into m2 ejected / m1 ejected / both bound / both free; bound
  but wider = unsettled (rerun to 300 r_t in the scans; 83 of 851968 isotropic samples
  stay unsettled).

## The driver (for F-pre-2, F-pre-3 and core)

```python
import sys; sys.path.insert(0, "tracks/F-hills/newton3")
from hills3.threebody import HillsSetup, initial_state, initial_state_json, scatter, trajectory
s = HillsSetup(M=10.0, m1=0.5, m2=0.5, a=30.0, e_b=0.0, D=0.7,       # or rp=...
               theta=1.5708, varphi=1.5708, varpi=0.0, phase=0.94)   # coplanar prograde
ic = initial_state(s, k0=10.0)      # or r0=<distance>: positions, velocities, momenta, t_to_pericentre
js = initial_state_json(s, k0=10.0) # the same as plain lists, for a problem-generator input file
out = scatter([s], k0=10.0)         # outcome, dE, E1, E2, captured-orbit a and e, r12min, ...
t, X, V, sol = trajectory(s)        # SciPy solve_ivp path (independent integrator) for figures
```

### Member energies at finite mass ratio (wave 2; corrects the defect of lead check V5b)

The defect. Before wave 2 each member's energy was its two-body energy with M alone,
E_i^M = mu_iM |v_i - v_M|^2/2 - G M m_i/|x_i - x_M|, mu_iM = M m_i/(M + m_i) (the
restricted-limit definition of SKR prp.tex:331 carried over). The lead found
(`stage/G0/checks/lead_checks.py` v5b, run F-hills-20261115-145559-a314517) that after a
capture the ejected member's E^M oscillates without settling (q = 10: 1.474-1.845 units;
q = 4: 0.989-1.723), so the value depended on the end time of the integration.

Derivation. Label the bodies after the encounter M, c (the member with the lower specific
two-body energy with M: the captured one) and e (the other). Jacobi coordinates of this
hierarchy: r = x_c - x_M, R = x_e - X, X = (M x_M + m_c x_c)/(M + m_c). With zero total
momentum the kinetic energy splits exactly,

    K = mu_in |r'|^2/2 + mu_out |R'|^2/2,   mu_in = M m_c/(M + m_c),
                                            mu_out = m_e (M + m_c)/(M + m_c + m_e),

and since x_e - x_M = R + beta r, x_e - x_c = R - alpha r (beta = m_c/(M + m_c),
alpha = 1 - beta),

    E_tot = E_in + E_out + W,
    E_in  = mu_in |r'|^2/2 - G M m_c/r                       (captured member, against M)
    E_out = mu_out |R'|^2/2 - G (M + m_c) m_e/R               (ejected member, against X)
    W     = -G M m_e/|R + beta r| - G m_c m_e/|R - alpha r| + G (M + m_c) m_e/R
          = -G m_e mu_in (r^2/R^3) P2(rhat.Rhat) + O(r^3/R^4)

(the dipole cancels because R is measured from the barycentre X; M beta^2 + m_c alpha^2 =
mu_in). dE_out/dt = -R'.grad_R W and dE_in/dt = -r'.grad_r W are O(R^-3); on an escape
orbit R grows linearly in t, so E_in and E_out converge, and E_in + E_out -> E_tot.
These are the "conserved two-body energies relative to the appropriate centre": the
captured member's against M, the ejected member's against the barycentre of M and the
captured member. With x_e' - x_M' = R' + beta r' the old definition differs from E_out by

    E_e^M - E_out = (mu_eM - mu_out)|R'|^2/2 + mu_eM beta R'.r' + mu_eM beta^2 |r'|^2/2
                    - G m_c m_e/R + O(r/R^2),

whose second term oscillates with the inner orbit at the fixed amplitude
mu_eM beta v_inf v_in. In energy units it is of relative order m/M (it vanishes in the
restricted limit, where E^M is SKR's E_1): 0.37/1.61 peak to peak at q = 10 and 0.73/1.31
at q = 4 (run F-20261115-174139-3340bf3). For the captured member both definitions
coincide (E_c^M = E_in).

Implementation (`hills3/threebody.py`). `member_energies(x, v, masses)` returns E1, E2
(corrected), the inner member, E_in, E_out, W, E_tot, the wave-1 energies E1_M, E2_M, and
the pair (E12, E_orb) of the binary hierarchy. The same rule covers every outcome: single
ejection (inner bound to M, outer escaping), both bound (inner = the tighter orbit; W does
not decay, the split is secular only), both free (all three separate, both energies
converge). While m1 and m2 are bound to each other (survived, unsettled) the members have
no separate energies: E1 = E2 = dE = NaN; E12 and E_orb (E_tot = E12 + E_orb + W_bin) are
returned, and dE_orb, the change of the binary's orbital energy about M. The outcome uses
the corrected energies: inner E_in < 0 and outer E_out >= 0 is a single ejection of the
outer member; E_in >= 0 with E_out < 0 (outer bound to an unbound pair) is "unsettled".
dE keeps KHSR's combination; with E1 + E2 = E_tot - W it is
dE = E2 - (m2/m)(E_tot - W) = -E1 + (m1/m)(E_tot - W): the energy moved from m1 to m2
beyond the mass-weighted share of the total, which tends to the restricted E2 because
E_tot/unit ~ -(1/2)(m/M)^(1/3) -> 0. The ejected member's speed at infinity relative to
the barycentre of the bound pair is v_inf = sqrt(2 E_out/mu_out).

Tests (`tests/test_hills3.py`, run F-20261115-174058-ad4fb17, 15 of 15 pass):
`test_jacobi_identity_with_direct_coupling` (identity with W computed from its
definition to 1e-12; quadrupole limit), `test_member_energy_conserved_after_capture` (the
test in which the old definition fails and the new holds: passages q = 10 and 4 to
t = 1500; old varies by > 0.1 units, corrected by < 1e-3 of that after t = 300 and
< 1e-5 units after t = 1000, end values within 1e-3 of V5b), `test_restricted_limit_of_corrected_energies`
(M/m = 1e6: both definitions agree to 1e-5), `test_end_time_independence_at_finite_q`
(M/m = 10: corrected dE the same at 30 and 100 r_t to 1e-3, old not).

### Initial data of the code: multi-puncture form (wave 2)

```python
s  = HillsSetup(M=1.0, m1=0.05, m2=0.05, a=3.0, rp=8.0, phase=np.radians(130))
st = puncture_state(s, k0=4.0, k_from=10.0)  # or r0=<distance>; k_from=None: on the conic
print(multi_puncture_block(st))              # <problem> block of nrpic_cf
```

or from the shell (`--predict` adds the full-Newton outcome from that state):

```text
python3 scripts/puncture_input.py --M 1 --m1 0.05 --m2 0.05 --a 3 --rp 8 \
    --phase-deg 130 --k0 4 --k-from 10 --predict [--json state.json]
```

`puncture_state` returns barycentric positions and momenta P = m v (zero total momentum,
barycentre at the origin, both to round-off after an exact re-centring) when the binary's
centre of mass is at the requested distance r0 (or k0 r_t) from M on the way in. With
`k_from` the encounter starts at k_from r_t and the full problem is integrated to the
event |x_cm - x_M| = r0 (DOP853, rtol 1e-12), so the state carries the tidal distortion
and phase shift of the approach (P4: a run must be compared with the reference started
from the same state); without it the bodies are placed on the unperturbed conic.
`multi_puncture_block` writes, in the order `order` (default m1, m2, M: the members get
trackers co_0 and co_1, as in `three_punctures/inputs`), `ncomp`, `comp<c>_type = puncture`,
`_mass`, `_x1.._x3`, `_p1.._p3`, `_s1.._s3` (zero unless given, listed so that the
command line can change them, interface section 2), `_corr` (default approx), then the
options of the existing Hills inputs (`corr_background = true`, `lapse = precollapsed`,
`puncture_setup = true`, `puncture_radius = 1.8`); numbers with 13 significant digits,
round-off below 1e-14 of the largest component written as 0.0. `parse_problem_block`
reads a block or a whole input file back. With k0 = 4, k_from = 10 the function
reproduces the start states of `three_punctures/inputs/hills_q10_m8.athinput` and
`hills_q4_m8.athinput` (made by linear interpolation of a 20000-sample trajectory) to
3e-6 in position and 1e-8 in momentum (test `test_puncture_state_reproduces_the_inputs`).

What the block does not do [JUDGEMENT; TO VERIFY with core]: masses are written as the
Newtonian masses, i.e. as the bare masses of the punctures. A corrected Bowen-York
puncture has ADM mass m + (5/8) P^2/m to second order (interface section 3, from
arXiv:0711.1165v2 second.tex:285-287), about 5 percent above m for the members at 4 r_t
(P/m = 0.28), and the conformal factor of the other holes raises each member's horizon
mass further (the 0.0515-0.0525 expected in stage/G1/STATUS.md for m = 0.05). The momenta
are Newtonian (no Lorentz factor; interface section 9 item 4 lists post-Newtonian momenta
as open). Choosing bare masses that give prescribed horizon masses, and PN momenta, is
initial-data work for core (Requests).

Example (run F-hills-20261115-132240-42345c2, `results/example.json`,
`figures/fig_driver_example.png`): M/m = 10, a = 30 m, D = 0.7, start at 10 r_t = 646 m;
the binary survives, hardened; energy error 3e-8 of the total; `scatter` and SciPy agree
on the final positions to 1e-6 m.

## Results

Numbers carry run ids; [VERIFIED] here means reproduced by a registered run of this
package against the printed source (locator), [JUDGEMENT] is interpretation.

**P0 tests** (run F-hills-20261115-130253-6fc800e: 9 pass; rerun at the final code,
run F-hills-20261115-133436-8bfc259: all 10 pass, including the JSON round trip). Two
tolerances I predicted were a factor ~10 too tight; SciPy's DOP853 shows the same numbers
(JOURNAL).

**P1, coplanar restricted, against SKR's text** (scan F-hills-20261115-130237-cbfaf6b,
deep points at rtol 1e-13 F-hills-20261115-132156-efddfc0, analysis
F-hills-20261115-133222-9cb10db, `results/coplanar.json`, `figures/fig_coplanar_*.png`).
Sampling: 3000 equally spaced effective phases in [0, pi) per D (as SKR prp.tex:763),
start 10 r_t (prp.tex:599), 207 D values from 1e-5 to 2.3.

| Quantity | this work | SKR (locator) |
|---|---|---|
| largest D with disruption, prograde | between 2.085 and 2.090 | 2.1 (prp.tex:846-847) [VERIFIED to its rounding] |
| largest D with disruption, retrograde | between 0.405 and 0.410 | 0.44 (prp.tex:778-779, 847) **differs; see P8** |
| D of maximal prograde P_dis | 0.16 (P = 0.988) | 0.15 (prp.tex:854) [VERIFIED] |
| prograde P_dis for 0.06 < D < 0.3 | 0.984-0.988 | 0.980-0.988 (prp.tex:1086-1087) [VERIFIED] |
| deep-limit survival (D = 1e-5) | 19.3 % pro, 19.9 % ret | 19 % radial (prp.tex:748-749) [VERIFIED] |
| survival windows, D = 1e-5 prograde | 0.693-0.886 pi, -0.307 to -0.114 pi | 0.69-0.88, -0.31 to -0.12 pi (prp.tex:785) [VERIFIED] |
| max abs E, prograde | 27.15 at D = 0.1 | 27.3 (prp.tex:848) [VERIFIED] |
| max abs E, retrograde | 1.84 (D -> 0) | 1.8 (prp.tex:849) [VERIFIED] |
| mean ejection speed, deep | 0.999 (D = 1e-5), 0.994 (1e-4) | 0.99 (prp.tex:993-994) [VERIFIED] |
| survivors harder than initially, deep | 87 % | about 90 % (prp.tex:752-753) |
| D-uniform mean abs E | pro 1.47; ret 0.55 or 0.47; both 1.38 | 1.46, 0.50, 1.36 (prp.tex:850-853); definition not stated: prograde matches, retrograde not claimed |

**P7, SKR's curves** (run F-hills-20261115-132703-0bfc352, `results/skr_curves.json`,
`figures/fig_skr_curves.png`; curves read from the MATLAB EPS of figs. 4 and 7 in
kb-data). Prograde P_dis within 0.004 of SKR for D < 0.3 (largest 0.037 on the steep
edge at D = 2.07); phase-averaged abs E median relative difference 0.17 % (pro) and 0.2 %
(ret); maximal abs E 0.08 % and 0.3 %. Retrograde P_dis lies below SKR's curve
(-0.03 at D = 0.1, -0.066 at 0.3, -0.16 at 0.4).

**P8, why the retrograde edge differs** (run F-hills-20261115-132942-2f7ad7f,
`results/bkrs_h1.json`, `figures/fig_bkrs_and_h1.png`). Counting my survivors whose
final semi-major axis exceeds 3.5 a as disrupted reproduces SKR's retrograde curve within
0.009 at every D up to 0.6, moves the edge to 0.445, and leaves prograde within 0.0024
for D < 0.3. BKRS's coplanar retrograde curve (fig. 2) has the same offset from mine.
[JUDGEMENT] SKR and BKRS count widened but bound binaries as disrupted (their criterion is
not stated); with the two-body-energy plus Hill-radius criterion used here, which P5 shows
is settled by 30 r_t, the retrograde edge is 0.41. Both versions are available from the
stored per-sample data.

**P2, general orientation, against BKRS** (scan F-hills-20261115-130239-cbfaf6b, part B
at D = 1e-4 and 1e-3 at rtol 1e-12 F-hills-20261115-132159-efddfc0, analysis
F-hills-20261115-133200-05ee76a, `results/general.json`, `figures/fig_general_*.png`).
Sampling: 512 orientations on a Fibonacci lattice over the whole sphere x 64 effective
phases in [0, pi) per D (BKRS used 2000 x 200, mnras.tex:352-357); inclination scan 31
theta x 32 azimuths x 64 phases.

| Quantity | this work | BKRS (locator) |
|---|---|---|
| P_dis(D) vs their fit (mnras.tex:372-376) | within 0.0094 for D <= 1, 0.013 for D <= 1.8 | fit accuracy 1 % for D <~ 1 (377-379) [VERIFIED] |
| mean abs E vs their fit (433-439) | within 1.7 % for D <= 1.5; 4.9 % at 1.85, 12 % at 1.95 | 1 %, 3 % at 1.8, 10 % at 2 (440-441) [VERIFIED] |
| deep plateau | 0.876-0.878 (D = 1e-3 .. 0.03) | 88 %, 87 % at 1e-3 and 0.1 (368-370, 606) [VERIFIED] |
| deep mean abs E, top-1 % energy | 0.978, 1.85 (D = 1e-3) | about 1 and 2 (462) [VERIFIED] |
| BKRS fig. 2 isotropic curve (read from EPS) | within 0.009 (median 0.0025) | P8 run |
| min P_dis over inclination, deep | 0.804 near theta = 0.45-0.5 pi (D = 1e-4) | about 80 % at pi/2 (507-509) [VERIFIED] |
| survivors only for theta > | 0.117 pi (P < 0.999) | 0.15 pi, "significant" (507-509) |
| mean abs E, theta = pi/2 over theta = 0 | 1.46, 1.44, 1.45, 1.71, 1.54 at D = 1e-4, 1e-3, 1e-2, 0.1, 0.3 | 1.4-1.7 (524-525) [VERIFIED] |
| collision probability, r_min < a/5 | 5.4-7.3 % for D < 0.1; peak 14.2 % near D = 1.6 | 5-7 %, about 14 % at 1.6 (757-764) [VERIFIED] |

**P5/P6, numerical systematics** (runs F-hills-20261115-131754-907e5fe,
F-hills-20261115-132433-7d0c6dd). At rtol 1e-10 the restricted energies lose precision
below D ~ 1e-3 (cancellation of a 1/D-sized zero-energy solution): D < 1e-3 is taken
from rtol 1e-12/1e-13 runs only. End radius 30 vs 100 r_t: no change. Start radius:
converged at 40 r_t (40 vs 80: P_dis within 0.25 points, mean abs E within 0.25 %); the
literature's 10 r_t is off by up to 2.2 points in P_dis (D = 2) and 2.7 % in mean abs E.
SKR's curves match my 10 r_t values, as they should.

**P3, full three-body against the restricted limit** (run F-hills-20261115-130630-c1d003c,
analysis F-hills-20261115-133203-05ee76a, `results/p3.json`,
`figures/fig_full_vs_restricted.png`; m1/m2 = 3, coplanar prograde, 200 phases).
SKR's example (D = 0.1, phi = 4 pi/5, M/m = 1e6): relative difference 2.4e-4 (SKR: 0.1 %,
prp.tex:631) [VERIFIED]. Median difference over phases relative to the mean abs E:
6.0e-4 (D = 1) and 7.3e-4 (D = 0.1) at M/m = 1e6, falling like (m/M)^(1/3) for D = 1 at
M/m >= 1e4 but faster (about (m/M)^(2/3)) for D = 0.1; at M/m = 10: 26 % (D = 1) and 59 %
(D = 0.1), with 11 % and 25 % of the phases changing fate.
Wave 2, with the corrected energies (rerun F-20261115-174142-0d549b5, analysis
F-20261115-175000-d2dc283, `results/p3.json`, figure redrawn; the old definition from the
same trajectories in the open squares): median 6.05e-4 and 7.29e-4 at M/m = 1e6 (before
6.03e-4, 7.29e-4), 0.265 and 0.591 at M/m = 10 (before 0.256 and 0.590), fate mismatch
unchanged (0.11, 0.25); outcomes change for 2 of 200 phases (D = 0.1, M/m = 10). SKR's
example 2.34e-4. The P3 statements stand.

**Finite mass ratio** (run F-hills-20261115-132019-bfe00a9, analysis
F-hills-20261115-133207-05ee76a, `results/finiteq.json`, `figures/fig_finite_q.png`;
m1 = m2; 2048 isotropic samples or 256 coplanar phases per D). Down to M/m = 10 the
isotropic disruption probability stays within a few points of the restricted limit for
D >= 0.3 (q = 10: 0.747 vs 0.754 at D = 0.4; 0.601 vs 0.641 at D = 0.7) and is higher at
D = 0.1 (0.93 vs 0.86, with 8.6 % of encounters capturing both members). The
phase-averaged energy change in units of (G m1 m2/a)(M/m)^(1/3) drops to 0.49-0.79 of the
restricted value for 0.1 <= D <= 1 at M/m = 10 (0.85 at D = 1.2). Coplanar retrograde
binaries are always disrupted for D <= 0.3 at M/m = 10 and still at 37 % for D = 0.5, where
the restricted limit has none (its edge is 0.41). Exchange outcomes m1/m2 ejected are equal to all
digits for m1 = m2, as the symmetry requires.

**P4, start distance of the driver** (run F-hills-20261115-131801-907e5fe, analysis
F-hills-20261115-133205-05ee76a, `results/p4.json`, `figures/fig_start_distance.png`;
D = 0.5, prograde, m1 = m2, 200 phases). Against a start at 40 r_t, a start at 10 r_t keeps
the outcome of 95 % (M/m = 1e6) and 97 % (M/m = 10) of the phases and the median energy
change within 0.6 % and 0.8 %; at 5 r_t only 92 % and 90 %. The effect is mostly a shift of
the effective phase (the curves move sideways). [JUDGEMENT] A comparison with an NR run must
start the Newtonian reference from the same initial data (same r0), not from the same
effective phase.

**Newtonian predictions for the two passages of stage/G1/STATUS.md (wave 2, corrected
energies)** (run F-20261115-174959-3188846, `scripts/passages.py`, `results/passages.json`,
`figures/fig_passages.png`; definition check F-20261115-174139-3340bf3). Start states of
`three_punctures/inputs/hills_q10_m8.athinput` and `hills_q4_m8.athinput` (rebuilt by
`puncture_state(k0=4, k_from=10)`, equal to the files to 3e-6 and 5e-6), full Newton,
t = 0 at the start state; units (G m1 m2/a)(M/m)^(1/3) = 1.7954e-3 M (q = 10) and
4.9606e-3 M (q = 4). [VERIFIED: model outputs of these runs]

| | q = 10 (P1: M = 1, m1 = m2 = 0.05, a = 3, r_p = 8, 130 deg) | q = 4 (M = 1, m1 = m2 = 0.125, a = 5, r_p = 9.82, 127 deg) |
|---|---|---|
| outcome | m1 ejected, m2 captured | m1 ejected, m2 captured |
| E of the ejected member (against the barycentre of M + m2), settled | +1.6127 units = +2.895e-3 M | +1.3119 units = +6.508e-3 M |
| the same at t = 100 / 150 / 200 / 250 / 270 | 1.607 / 1.614 / 1.6128 / 1.6128 / 1.6128 | 1.268 / 1.319 / 1.312 / 1.3121 / 1.3121 |
| (wave-1 definition, against M alone, at the same times) | 1.770 / 1.507 / 1.827 / 1.492 / 1.485 | 2.155 / 0.974 / 1.494 / 1.453 / 1.002 |
| Newtonian speed at infinity of the ejected member (relative to the barycentre of M + m2, G = c = 1) | 0.3483 | 0.3401 |
| E of the captured member (against M) | -1.8450 units | -1.6266 units |
| E_tot (= E_ej + E_cap + W) | -0.2323 units | -0.3147 units |
| dE = (m1/m) E2 - (m2/m) E1 | -1.729 units | -1.469 units |
| captured orbit (osculating, t = 1500) | a = 7.547 M, e = 0.2474, r_p = 5.680 M | a = 7.746 M, e = 0.2503, r_p = 5.807 M |
| pericentres of the captured member | t = 92.2 (5.641 M), 219.0, 346.2 | t = 122.1 (5.777 M), 250.9, 378.6 |
| closest approach to M: ejected / captured | 9.43 / 5.64 M (no member inside 4 M) | 12.07 / 5.78 M |
| ejected member's distance from M at t = 200 / 270 | 53.7 / 80.5 M | 45.1 / 72.6 M |

Phase scans at the same configurations, 360 effective phases, coplanar prograde,
corrected classification (start 10 r_t / 4 r_t on the conic): q = 10: single ejection
0.844 / 0.877, survived 0.151 / 0.112, both bound 0 / 0.006, unsettled 0.006 / 0.006, 2
of 360 phases stalled (near head-on approach of the members, counted apart); a member
inside 4 M in 0.05 / 0.05 of the phases; mean ejection energy 1.114 / 1.044 units (median
1.059 / 0.976, range 0.15-1.72). q = 4: single ejection 0.794 / 0.844, survived 0.206 /
0.150; inside 4 M 0.19 / 0.30; mean ejection energy 0.874 / 0.805 (median 0.766 / 0.697).
Against the wave-1 definition the classes change for 2 of 360 phases (q = 10 from 4 r_t:
two single ejections become both bound) and none otherwise; the ejection energy of a
single phase changes by up to 0.21 (q = 10) and 0.41 units (q = 4), the phase means by
-0.4 % and -0.2 % (from 10 r_t).

What changes in stage/G1/STATUS.md [JUDGEMENT]: nothing in kind. P1 item 2 already quotes
the barycentric +1.613 units and the captured orbit of V5/V5b; add that the corrected
energy has settled by t = 200 (1.6128), so the end of P1 can be compared directly, while
the definition against M alone would read 1.83 there. The q = 4 fallback: +1.312 units
(settled by t = 200), captured a = 7.75 M, e = 0.250, pericentre 5.81 M at t = 122.
Readers of the code's trackers must use the barycentric definition (the NR analogue is
the subject of three_punctures PLAN section 6).

## Rerun

Wave 2: through the harness from the worktree root (`harness/bin/nrpic-run submit --kind
scouting --gate G1 --package tracks/F-hills/newton3 --cores N [--background] --purpose
"..." -- python3 tracks/F-hills/newton3/scripts/<script> ...`; runlib then uses the run
id of nrpic-run, close background runs with `nrpic-run finish <run_id>`):

```text
scripts/run_tests.py                         # 15 tests, 30 s
scripts/energy_definition.py                 # Q1-Q3, 7 min on 1 core
scripts/passages.py --workers 4              # Q5, 20 s
scripts/compare_full.py p3 --workers 4       # 2 min
scripts/compare_full.py finiteq --workers 6  # 12 min
scripts/analyze.py p3|finiteq <run_id>
scripts/puncture_input.py --M 1 --m1 0.05 --m2 0.05 --a 3 --rp 8 --phase-deg 130 --k0 4 --k-from 10 --predict
```

Wave 1, from `tracks/F-hills/newton3`, with `OMP_NUM_THREADS=1` (each script registers its run and
prints the run id; analyses take the run ids of the scans):

```text
python3 scripts/run_tests.py                                   # P0, 25 s
python3 scripts/scan_coplanar.py --workers 6                   # P1, 10 min on 6 cores
python3 scripts/scan_coplanar.py --workers 6 --rtol 1e-13 \
    --D-list 1e-05,1.8e-05,3.2e-05,5.6e-05,0.0001,0.000178,0.000316,0.000562
python3 scripts/scan_general.py --workers 6                    # P2, 9 min on 6 cores
python3 scripts/scan_general.py --workers 2 --rtol 1e-12 --only-B 0.0001,0.001
python3 scripts/convergence.py --workers 10                    # P5
python3 scripts/convergence.py --k0-scan --workers 8           # P6
python3 scripts/compare_full.py p3 --workers 4                 # P3, 2 min
python3 scripts/compare_full.py p4 --workers 4                 # P4, 1 min
python3 scripts/compare_full.py finiteq --workers 6            # 10 min
python3 scripts/analyze.py coplanar <P1 run> <deep supplement run>
python3 scripts/analyze.py general <P2 run> <P1 run> <part-B supplement run>
python3 scripts/analyze.py p3|p4|finiteq <run> ; python3 scripts/analyze.py example
python3 scripts/digitize_skr.py <P1 run> <deep supplement run>             # P7
python3 scripts/digitize_bkrs.py <P1 run> <deep run> <P2 run> <P7 run>     # P8
```

Total cost of everything above: about 4 core-hours, no card-hours.

## Not done, open

- Eccentric binaries: the driver and the restricted code accept e_b and varpi (tested for
  the initial data only); BKRS's eccentric results (D_max 2.8 for e = 0.3, 3.2 for 0.6 and
  0.9, mnras.tex:623-624) were not reproduced.
- Non-parabolic centre-of-mass orbits (KHSR's e != 1 and the ejection-preference curves,
  ms.tex:1140-1152) were not reproduced; `e_orb` is supported by the driver and tested for
  the initial data only.
- The definition behind SKR's D-uniform average energies (prp.tex:850-853) is not stated;
  the retrograde value is not matched by either definition I tried.
- The radial restricted problem (SKR section 3) was not implemented; the deep limit is
  taken from the parabolic equations at D = 1e-5 .. 1e-4 at tight tolerance.
- No second agent has yet checked these results (nor the wave-2 definition).
- Wave 2: the multi-puncture block writes the Newtonian masses as bare masses and P = m v;
  no choice of bare masses for prescribed horizon masses, no post-Newtonian momenta
  (section "Initial data of the code"). The block has not been run by the code here
  (no card or processor run of AthenaK in this package); the existing inputs that it
  reproduces were checked by three_punctures.
- Wave 2: other packages still call the wave-1 energies: `three_punctures/scripts/newton_start.py`
  (imports `_pair_energy` and reads `E1`, `E2` of `scatter`, which are now the corrected
  energies and NaN for survivors) and `stage/G0/checks/lead_checks.py` (its own energies
  against M; V5b already uses the barycentric one). Not edited here (outside this package).

## Requests

- **core**: the three-puncture initial data of F-pre-3 (the "several black holes" item of
  decision 0010) should accept per puncture a mass, a position and a momentum in the
  barycentric frame, i.e. the output of `initial_state_json` (G = 1, lengths in the chosen
  mass unit); and the puncture tracks should be written at a fixed cadence so that the
  Newtonian `trajectory` from the same initial data can be overlaid.
- **F-hills lead**: (i) choose the start distance of the NR runs knowing P4 (>= 10 r_t keeps
  95-97 % of phase outcomes; 5 r_t only 90 %) and compare NR with the driver started from
  the same initial data; (ii) say which disruption criterion the track adopts for the
  literature comparisons (bound-and-inside-Hill, as here, or SKR/BKRS's, reproduced by
  counting survivors with a_f > 3.5 a as disrupted); (iii) post the requests above.
- **F-pre-2 helper (geodesic plus Newtonian model)**: use `hills3/orbits.py` conventions
  (frame, D, effective phase, orientation) so that its curves at large r_p/r_g can be
  overlaid on `fig_finite_q.png` at the same M/m.
- **kb**: the locators in `hills3/reference.py` point into `kb-data/raw/arxiv/{0911.1136,
  1201.4794,1804.02911}/v1/src/`; a second agent checking them, and H1, is welcome.

Wave 2 (newton3_fix):

- **F-hills lead**: (i) take the corrected Newtonian predictions of the passages (section
  "Newtonian predictions for the two passages") into `stage/G1/STATUS.md` (P1 item 2 and
  the q = 4 fallback) and `stage/G0/OPEN.md` item 7 (the defect is fixed; V5b's numbers are
  reproduced by runs F-20261115-174139-3340bf3 and -174959-3188846); (ii) the NR readers
  of three_punctures PLAN section 6 should measure the ejected member against the
  barycentre of the heavy hole and the captured member (the wave-1 definition reads 1.83
  instead of 1.61 at the end of P1); (iii) `three_punctures/scripts/newton_start.py` reads
  `E1`/`E2` of `scatter`, which are now the corrected energies and NaN for survivors: its
  figures and phase choice are unaffected for single ejections, but a rerun should say
  so; (iv) new start states for the code: `scripts/puncture_input.py` (or
  `puncture_state` + `multi_puncture_block`) for any requested start distance; (v) a
  second agent to check the derivation in "Member energies at finite mass ratio" and the
  test that separates the two definitions.
- **core**: for `puncture_state` output, decide whether the multi-puncture data should
  take the Newtonian masses as bare masses (as now; member ADM masses then about 5
  percent above m at P/m = 0.28, interface section 3) or bare masses solved for
  prescribed horizon masses, and whether momenta should carry a Lorentz or PN factor
  (interface section 9 item 4). The block uses only parameters of interface section 2.
- **harness (orch)**: none; `nrpic-run submit --package` worked for every run of this
  package (local launcher, background, finish). One inconvenience: a local submit is
  refused when the owner's cores in use plus the request exceed 16, including other
  helpers' runs, so a helper cannot see its own share; the finite-q rerun had to wait.
