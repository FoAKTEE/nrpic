# JOURNAL of verifier_g1 (fresh-context verifier of Track D's G1 material, item C17)

Helper of owner D-bh-dress, wave 3, 2026-11-20. I produced none of the material. Before
the verdicts are committed I read only what the task allows: SCOPE.md, DERIVATION.md,
scripts, inputs, manifests, raw outputs, package README files (layout only), the AthenaK
source, the knowledge base, and the note at the pinned commit 78d470ca. Each entry: the
prediction and what would make the claim WRONG, written before the run; the outcome after.

## Entry 1 (2026-11-20 14:15 PST): V1, ES-1 and V-1, prediction

Script `v1_es.py` (my own readers of `traj.bin`, `trajmet.bin` with the 17-double record of
`athenak/src/particles/nrpic_io.cpp:811-814` and 926, `part.*.bin` of :941-978,
`horizon_summary_0.txt` by its header; the format-2 table of
`coord/INTERFACES/spherical_id_format2.md`). Exact curves from the data set
D-20261115-170213-d2c2131 only through its table `es.tab`/`v1.tab` and particle files
`es.nrp`/`v1.nrp` (not through `es.json`, `es_reference.csv` or the track's scripts):
R0 = psi^2 rbar at the tracer's start, Misner-Sharp mass m = (R/2)(1 - (dR/dl)^2 + R^2 KT^2),
energy per unit mass Etilde^2 = 1 - 2m/R0 + R0^2 KT^2 (a particle at rest in the slice moves
with dR/dtau = -R KT), then the closed-form radial geodesic (cycloid for Etilde < 1,
R = (R0^(3/2) + (3/2) sqrt(2m) tau)^(2/3) for Etilde = 1). Areal radius of a tracer from the
evolved 3-metric at the particle: R = r sqrt((tr gamma - n.gamma.n)/2), r the coordinate
distance from the puncture at the origin (tangential eigenvalue of a spherically symmetric
metric in Cartesian coordinates).

Predictions (what I expect if the track is right):
- P1a wall tracers (tags 56-69), max_i max_{tau<=200} |R/R_w - 1|: 2.2e-3 (ES-1), 1.6e-3
  (V-1). WRONG if my value differs from the claim by more than 15 per cent (definition of
  the areal radius could move it a little), or if it exceeds 3e-3.
- P1b exact crossing times of R = 2M from my closed form: 14.8269 M (R0 = 6 M) and
  34.4423 M (R0 = 10 M) to 1e-4 M; run crossings (proper time of the tracer interpolated to
  R = 2M) 14.826 and 34.437 M within 2e-3 M and 1e-2 M of the claims. WRONG if my exact value
  differs from the claimed exact by more than 1e-3 M, or the run value by more than 1e-2 M.
- P1c horizon mass, max |M_AH(t)/M_AH(100 M) - 1|: 100-200 M: 3.40e-4 (ES-1), 1.37e-4 (V-1);
  100-165 M: 9.3e-5 and 4.2e-5. WRONG if mine differ by more than 20 per cent (e.g. a
  different reference sample), or if ES-1 over 100-165 M exceeds 2e-4.
- P1d no dust particle inside the wall: in every snapshot (t = 0, 25, ..., 200 M), the
  smallest coordinate radius of a dust particle (tag >= 140) exceeds the largest coordinate
  radius of the wall tracers in the nearest direction; the particles removed during the run
  are tracers only (tags < 140). WRONG if any dust particle lies inside, or any dust tag
  disappears.

### Outcome of entry 1 (14:23 PST), run D-20261120-222209-871e07f

P1a-P1c held; P1d as I worded it (nearest of the 14 wall directions) FAILED at t >= 175 M,
while its refutation criterion (a dust particle inside the wall) was not met once the wall
is interpolated between the directions (below). Files: `v1_results.json`, figures
`v1_wall.png`, `v1_inner.png`, `v1_horizon.png`, `v1_dust_wall.png`, all looked at.
- P1a: wall, max over tau <= 200 M: ES-1 2.196e-3 (axis tracers; diagonal 1.734e-3),
  V-1 1.594e-3. The second areal-radius definition (det gamma / n.gamma.n)^(1/4) r gives the
  same digits. Attempt to break: over the whole run (tau up to 283 M in ES-1, 250 M in V-1)
  the error grows to 1.71e-2 (ES-1, diagonal, at the end) and 7.17e-3 (V-1); tau = 200 M is
  reached at t = 137.5 M. So the claim holds only on its stated window, and the window
  ends where the curves turn (figure `v1_wall.png`).
- P1b: exact crossing times from my closed form 14.82693 M and 34.44232 M (claims 14.8269,
  34.4423). Run, mean over 14 tracers: 14.82652 (cubic interpolation in R) or 14.82634
  (linear), 34.43683 or 34.43675; spread over the 14 tracers 1.6e-4 and 4e-4 M. The claimed
  14.8263 matches my linear value. R0 = 20 M group: 244.33 M against 244.74 (ES-1 only;
  V-1 ends first).
- P1c: horizon drift 3.400e-4 (ES-1) and 1.368e-4 (V-1) over 100-200 M; 9.35e-5 and
  4.21e-5 over 100-165 M; M_AH(100 M) - M = 9.55e-4 and 9.37e-4. Exact agreement with the
  claims. Attempt to break: with the mean over 95-105 M as reference the numbers become
  3.82e-4 and 1.32e-4 (100-200 M), 9.2e-5 and 3.7e-5 (100-165 M): the single-sample
  reference moves them by up to 12 per cent, not more.
- P1d: no dust tag disappears (696688 dust particles in all nine snapshots); the 42
  removed particles are tracers 0-41 (groups R0 = 6, 10, 20 M). A naive test (dust against
  the wall tracer of the nearest of 14 directions) fails at t >= 175 M (-0.061 M at 200 M)
  because the coordinate radius of the wall differs by 0.57 M between axis and diagonal at
  t = 200 M. With the wall interpolated between the 14 directions by the angular shape of
  the innermost dust layer itself (fit a + b(r0 - 36.4) + c q4 + d q6, residual <= 0.020 M,
  rms 0.007 M) the smallest margin is 0.1356 M at t = 200 M (lowest cubic harmonic alone:
  0.1359 M); within 6 degrees of the 14 wall tracers, model-free, 0.126 M. No dust inside.

## Entry 2 (2026-11-20 14:25 PST): V2, D-pre-3 in AthenaK's Newtonian mode, prediction

Script `v2_infall.py`. Inputs: the snapshots of N128c D-20261115-171503-4262f03, N64c
-171505-62940f4, N128Lc -171507-d1058a9 and their `setup.json` (eps, t_i, tag ranges of
clump and dust, dx); the measured kernel files `secondary_infall/kernel_nx{64,128}.txt` as
the only input taken from the track's analysis (for my matched shell reference).

My definitions (written before computing):
- Centre: mass-weighted centre of the clump particles in each snapshot. Initial radius r_i
  and direction n0 of every dust particle from snapshot 0. a/a_i = ((t + t_i)/t_i)^(2/3).
- Dress(t): dust mass on the shells that have passed through the centre at least once.
  A particle has passed once it lies on the far side, (x - c).n0 < 0; the passage front
  r_c(t) is the outermost initial radius at which half of the particles of a thin r_i bin
  have passed (shells that passed twice lie inside it). Dress = dust mass with r_i < r_c.
- Turnaround mass M_ta(t): clump mass plus the dust mass with r_i < r_ta,i(t), where
  r_ta,i is the outermost initial radius at which the median radial velocity of the
  not-yet-passed particles of a thin r_i bin crosses zero; r_ta(t) is the current radius
  of that shell.
- References: (i) point-mass Kepler closed form for M_ta with the actual enclosed mass
  (clump + lattice dust inside r_i, Hubble velocity eps r_i at t_i); (ii) my own spherical
  shell code (3000 shells built from the lattice of snapshot 0, leapfrog, sorting for the
  enclosed mass, reflection at the centre) with three force laws: measured kernel on the
  clump only, measured kernel on all enclosed mass, point mass with 0.25 M softening.
- Self-similar profile: Bertschinger-type collisionless solution, my own fixed-point
  iteration of Lambda'' = -(pi^2/8) tau^(2/3) m(Lambda tau^(-8/9))/Lambda^2 with
  m(lambda) = int_0^1 H(lambda - Lambda(tau) tau^(-8/9)) d(tau^(-2/3)), and
  rho/rho_b = (9 pi^2/16) m'(lambda)/(3 lambda^2), compared in bins (bin-averaged from m).

Predictions:
- P2a my M_ta of the runs equals the claimed run values (1.5063, 2.5966; 1.5064, 2.5966;
  1.5077, 2.5962, 4.8159 M) within 0.3 per cent. WRONG if more than 1 per cent off.
- P2b my dress equals the claimed run values (0.1744, 0.7975; 0.1736, 0.7966; 0.1751, 0.7977,
  2.1537 M) within 2 per cent (definitions may differ at the front). WRONG if more than
  5 per cent off without a definitional reason I can show.
- P2c run against my kernel-matched shell reference: M_ta within 0.5 per cent and dress
  within 1 per cent at a/a_i = 2 (dress: 3 per cent), 4 and 8; point-mass Kepler M_ta within
  1 per cent. WRONG if M_ta differs by more than 1 per cent or the dress by more than 2 per
  cent at a/a_i = 4 or 8 from my kernel reference.
- P2d my self-similar solution: outermost caustic near lambda = 0.36, m ~ lambda^(3/4) at
  small lambda; N128Lc at a/a_i = 8 within 25 per cent of it on lambda in [0.1, 0.3]
  (8 logarithmic bins). WRONG if a bin there deviates by more
  than 30 per cent.

Development before the registered V2 run (2026-11-20 19:00-19:15 PST, written before it):
- The first self-similar solver (solve_ivp with a Python right-hand side, reflection by an
  event at Lambda = 1e-6) did not finish one fixed-point sweep in 10 minutes; stopped. It is
  replaced by `v2_selfsim.py` (signed radial orbit through a centre softened by 1e-4 in
  Lambda, adaptive leapfrog, m as an exact quadrature along the steps). Smoke tests (not
  registered, scratch/D-bh-dress/tmp/vg1/ss_*.txt): outermost caustic lambda_1 = 0.3580,
  0.3618, 0.3610, 0.3630 for (tau_max, eta) = (30, 0.02), (200, 0.01), (200, 0.005),
  (500, 0.01); m(0.1) = 0.306-0.304; the eight bins on [0.1, 0.3] move by up to 4 per cent
  between tau_max = 200 and 500 (caustics cross bin edges). So the reference itself carries
  a few per cent per bin; the registered run uses (500, 0.01) and reports the other two.
- Smoke test of my snapshot reader on N64c (not registered): M_ta = 1.5060 and 2.5955 M,
  dress 0.1741 and 0.7957 M at a/a_i = 2 and 4, i.e. within 0.12 per cent of the claimed run
  values. The registered run repeats this and adds the shells and the self-similar profile.
- Attempts to break added before the run: half the number of r_i bins (150) for M_ta and
  dress; r_ta scaled by 0.97 and 1.03 in the profile; the profile against the two other
  self-similar solutions.

### Outcome of the first V2 run (19:15 PST), run D-20261121-031031-e23da04

- P2a held: my M_ta at a/a_i = 2, 4 (8): N128c 1.5058, 2.5955; N64c 1.5060, 2.5955; N128Lc
  1.5056, 2.5940, 4.8159 M; largest difference from the claimed run values 0.14 per cent
  (N128Lc at 2). Half the r_i bins: changes up to 0.10 per cent.
- P2b held: dress N128c 0.1749, 0.7990; N64c 0.1741, 0.7957; N128Lc 0.1749, 0.7955, 2.1527 M;
  largest difference 0.3 per cent.
- P2c: my "kernel on the clump, unsoftened dust" shells are WRONG as a reference: M_ta 5 per
  cent (a/a_i = 4) and 19 per cent (8) below every run and every other force law, growing
  with time (figure `v2_growth_ratio.png` of this run). Suspected cause (not yet tested): the
  unsoftened shell-shell force at the centre with a fixed step heats the passing shells.
  The other two laws agree with the runs: kernel on all enclosed mass and point (s = 0.25 M)
  give M_ta within 0.08 per cent at a/a_i = 2, 4, 8 and dress within 0.4 per cent at 4 and 8,
  but at a/a_i = 2 the dress of the runs lies 1.6 (N128c), 2.3 (N64c), 3.1 (N128Lc) per cent
  above my kernel shells and 0.0-0.6 per cent above my point shells. So the claim "0.1-0.5
  per cent" does not hold for the dress at a/a_i = 2 against a kernel reference; the
  difference is within the spread of my reference's force laws (1-2.6 per cent at a = 2).
- P2d held marginally: caustic lambda_1 = 0.3630 (500, 0.01), 0.3610-0.3618 (200);
  N128Lc at a/a_i = 8 on [0.1, 0.3]: ratios 0.741, 0.864, 1.048, 1.171, 1.138, 1.017, 0.798,
  0.927, largest deviation 25.9 per cent (25.2-25.4 against the two other self-similar
  solutions; 32.5 and 34.5 with r_ta scaled by 0.97 and 1.03). At a/a_i = 4 N128c and N64c lie
  at 0.41-1.05 of the solution. Figure `v2_profile.png` looked at: the runs follow the solution
  outside lambda = 0.1 and show the caustic at 0.36-0.40.

Second V2 run (prediction, 19:25 PST): the same script, the growth figures against the
kernel-on-all shells and the point shells, plus two step checks: kernel-on-clump at dt =
0.002 and kernel-on-all at dt = 0.005. If the kernel-on-clump deficit is the step at the
centre, it shrinks by at least a factor 2 at dt = 0.002; if it does not shrink, the cause is
something else (then I say "cause open"). Kernel-on-all must move by less than 0.1 per cent
(M_ta) with the halved step, else my kernel reference is not converged either. All run
numbers must reproduce exactly (processor analysis of the same snapshots).

### Outcome of the second V2 run (19:25 PST), run D-20261121-031711-0d79cb3

- Run numbers reproduced exactly (same M_ta, dress, profile ratios as the first run).
- Step checks: kernel-on-all is converged (dt 0.01 and 0.005 give identical numbers to four
  digits). The kernel-on-clump deficit GREW with the smaller step (N128c M_ta at a/a_i = 4:
  2.4575 at dt 0.01, 2.4020 at 0.002), so my guess "fixed step at the centre" is refuted;
  cause open. That variant (unsoftened dust self-gravity) is not the physics of the run, whose
  mesh softens the dust as well, and it is dropped as a reference.
- Against kernel-on-all (converged): largest M_ta deviation for a/a_i >= 1.5: 0.14 (N128c),
  0.27 (N64c), 0.43 (N128Lc) per cent; dress for a/a_i >= 3: 0.87, 1.05, 1.16 per cent, and at
  the round values a/a_i = 4 (8): +0.40, +0.11, +0.32 (+0.43) per cent; at a/a_i = 2 +1.6, +2.3,
  +3.1 per cent. Against point shells (s = 0.25 M) the dress at a/a_i = 2 is within 0.6 per
  cent. Figure `v2_growth_ratio.png` looked at: early dress (a/a_i < 2.2) scatters by several
  per cent against either law, later the curves stay within about 1 per cent.

## Entry 3 (2026-11-20 19:35 PST): V3, Kerr spike reference, prediction

Script `v3_kerr.py`: my own density in the equatorial plane from the invariants (E, C, Lz)
with the current and density of 1707.06302 (kerrdm.tex:396-416), capture by the root
structure of the radial quartic, Hernquist matching by equal radial actions and L = |Lz| +
I_theta/(2 pi) (kerrdm.tex:523-553), the Hernquist DF of :864-874 evaluated in delta = 1 -
eps~; halo M = 1e12 Msun, r_s = 20 kpc (kerrdm.tex:859, 885), hole 4e6 Msun (taken from the
track's kerr_lib.py:288; the paper's text gives only "M_BH >~ 4e6 Msun", :127, [TO VERIFY]);
f0 c^3 = 0.3 GeV/cm^3 / (2 pi (100 km/s)^2)^(3/2) (:763). My own pgf digitiser (tick labels
and grey gridlines).

Development before the registered run (not registered; scratch/D-bh-dress/tmp/vg1/):
- First version over-counted for a != 0: constant f at a = 0.8, r = 6.6 came out 1.194e8
  against 1.0585e8 in FdRW's figure. An independent quadrature over the local momentum of
  the zero-angular-momentum observer (zamo_test.py) disagreed by 14 per cent, the printed
  Jacobian (kerrdm.tex:347) passed a finite-difference check (jac_test.py, ratio 1.00000000
  at a = 0 and 0.8), and a scan of validity along C showed equatorial (Q = 0) plunging orbits
  marked valid: with Q = 0 the quartic has a root at r = 0 and r2, r3 can both lie inside r_+.
  Fix: require r3 >= r_+. After it, invariants and local-frame quadrature agree to 6e-4
  (a = 0.8, r = 6.6, 12, 300) and to 8e-4 at a = 0.
- Smoke values after the fix: Hernquist peak a = 0.8 3.899e18 at r = 5.06 (FdRW 4.083e18),
  a = 0.5 2.777e18 at 7.1 (FdRW 2.814e18), a = 0 2.425e18 at 7.73 (FdRW 2.439e18); constant f
  a = 0.8 at 6.6: 1.060e8 (FdRW 1.0585e8). The variant L = sqrt(C) moves the a = 0.8 peak by
  0.1 per cent only.

Predictions for the registered run (what would make each claim WRONG):
- P3a constant f, a = 0.5 and 0.8, equator: my curve within 1.5 per cent of FdRW's figure on
  r >= 5 M (the claim's 0.88 and 0.95 per cent are maxima over the track's nodes). WRONG if
  my max deviation on the digitised range exceeds 3 per cent away from the inner edge.
- P3b Hernquist a = 0: within 1.5 per cent of FdRW on r >= 5 M. WRONG above 3 per cent.
- P3c Hernquist a = 0.8, equator: my peak 4 to 5 per cent below FdRW and within 1 per cent of
  the track's 3.92e18; if mine were within 1 per cent of FdRW, the track's reference would be
  WRONG; if mine differed from both by more than 2 per cent, my own code is suspect.
- Axis (theta = 0) cases: not computed (no claim on the axis will be CONFIRMED by me).

## Entry 4 (2026-11-20 19:45 PST): V4, AthenaK stationarity in Kerr a = 0.8, prediction

Script `v4_kerr_stat.py`: my reader over all 12 x 201 snapshots of run
D-bh-dress-20261115-172611-1e40191; E, Lz, Q from the Kerr-Schild state with my formulas
(module docstring; geometry from nrpic_metrics.hpp:22-85); counts in r ranges 0-4, 4-6, 6-10,
10-16, 16-40 M; my reference counts from an off-equator generalisation of v3_kerr.py (C >=
Lz^2/sin^2 + a^2(1-E^2)cos^2, J_t, J_phi with 1/sin(theta), n = J^t Sigma^2 sin(theta)) for
the Hernquist DF cut at E < 0.99, normalised to all 48000 particles; block means of 1000 M
for the uncertainty of time averages.
Smoke tests (not registered): particles at t = 0 have 0.9085 <= E <= 0.98999816, so the cut
E < 0.99 of the sampler's arguments is what the particles carry; chunk 0, t = 0 -> 20000 M:
max |dE/E| 6.7e-6, |dLz| 6.4e-10, |dQ|/max(Q,1) 4.6e-6; my off-equator reference at mu = 0
equals my equatorial code to 2e-6.

Predictions:
- P4a late/early ratios per range in 0.998-1.004 (claim 0.998-1.003). WRONG if any range is
  outside 0.99-1.01 or differs from the claim by more than 0.003.
- P4b over all particles and 20000 M: max |dE/E| < 1e-5, max |dQ|/max(Q,1) < 1e-5,
  |dLz| < 1e-8. WRONG if any maximum exceeds 2e-5.
- P4c my reference counts within 2 per cent of the track's expected counts in every range;
  time averages 1-5 per cent below mine in 0-4, 4-6, 6-10, each at about one standard error
  (block estimate), and within 0.5 per cent in 10-16 and 16-40. WRONG if my reference
  differs from the track's by more than 3 per cent in an inner range (then the claimed
  deficit is a property of their reference), or if an inner time average lies above mine.

### Outcome of entry 3 (19:41 PST), run D-20261121-033209-9c0bd44

Figures `v3_constf_a0.5.png`, `v3_constf_a0.8.png`, `v3_hern_a0.0.png`, `v3_hern_a0.5.png`,
`v3_hern_a0.8.png` looked at. Self-checks: V(r) = R/r^4, I_theta(a=0) = 2 pi (L - |Lz|) to
1e-9, Hernquist action against a direct quadrature to 2e-9, Newtonian limit of the constant-f
density 0.995 at r = 2000 (loss cone), local-frame quadrature against the invariant integral
at the constant-f peaks 1.0005 (a = 0.8) and 0.9990 (a = 0.5), at r = 12 to 5e-5.
- P3a held: constant f, largest deviation from FdRW's figure 0.85 per cent (a = 0.5) and
  0.88 per cent (a = 0.8) over the whole digitised range, 0.34 per cent for r >= 5 Gm; peaks
  +0.15 and +0.14 per cent.
- P3b held within my WRONG threshold but not within my 1.5 per cent prediction: Hernquist a = 0,
  1.67 per cent for r >= 5 Gm (2.6 per cent at the inner edge, 4.4 Gm), median -0.56 per cent,
  peak 2.4256e18 at 7.735 against 2.4391e18 at 7.730 (-0.55 per cent). The residual is flat
  at -0.5 per cent from 5 to 18 Gm and -1 to -1.7 per cent from 20 to 38 Gm at every spin
  (also a = 0.5, 0.8): a common offset at large r, digitisation or a halo parameter.
- P3c held: Hernquist a = 0.8, my peak 3.8999e18 at 5.04 Gm, FdRW 4.0826e18 at 5.07 (-4.5
  per cent), the track's 3.9217e18 (-0.56 per cent from mine); doubled quadrature at the
  peak node +5e-4; variant L = sqrt(C) -0.1 per cent. a = 0.5: 2.7768e18 against 2.8136e18
  (-1.3 per cent). FdRW's a = 0.8 curve has a narrow bump at its maximum (figure), which my
  curve and the track's do not have.
- Caveat: at a = 0 my Lz scan found up to 23 disjoint valid intervals at some radius (root
  classification at near-degenerate roots); the doubled quadrature moved the a = 0 peak by
  7e-5 only, so the effect on the numbers above is small, but it is a fragility of my code.
