# Journal of the szekeres package (helper of A-emd-pbh, wave 3a)

Predictions are written before the test runs; outcomes are appended below each, failed
predictions included. Labels: [VERIFIED] (symbolic check or registered run named),
[BACKGROUND] (textbook or cited paper, locator given), [JUDGEMENT], [TO VERIFY].

Reference: arXiv:1708.09143 (Bolejko, "Relativistic numerical cosmology with Silent
Universes"), source fetched with `nrpic-fetch-arxiv` to
`kb-data/raw/arxiv/1708.09143/v4/src/simsilun_rev.tex`; the quasi-spherical Szekeres
metric is its eq. (ds2) at lines 290-292, the function E(r,p,q) at line 296, the
evolution equation at line 301, the bang time at lines 307-310, the fluid scalars rho,
Theta, Sigma, W at lines 314-319, the shear and Weyl ansatz sigma_ab = Sigma e_ab,
E_ab = W e_ab at lines 212-215, the silent evolution equations at lines 218-223.

## Entry 1, 2026-11-19 14:35 UTC: conventions and predictions before any test

Conventions [JUDGEMENT]: signature (-,+,+,+), G = c = 1, Lambda kept in the symbolic
checks and set to 0 in the numerics (AthenaK runs of Track A have no Lambda). The paper
writes the metric with signature (+,-,-,-) but e_ab = h_ab - 3 z_a z_b, which is
traceless only when z_a z^a = +1: its conventions are mixed, so every sign is fixed here by
the symbolic computation, in mixed components (e^a_b = h^a_b - 3 z^a z_b with z_a z^a = +1,
eigenvalue -2 along z, +1 transverse). Radial label r = areal radius R on the initial
slice t = t_i (as `expball`); simultaneous bang time t_B = 0; the Szekeres dipole function
of the paper, E(r,p,q), is called `Ecal` here to avoid a clash with the LTB energy E.

Predictions (each refuted as stated):

- P1 (sym) The metric (ds2) with Rdot^2 = -k + 2M/R + Lambda R^2/3 satisfies
  G_ab + Lambda g_ab = 8 pi rho u_a u_b identically, u = d_t, with
  8 pi rho = 2 (M' - 3 M Ecal'/Ecal) / (R^2 (R' - R Ecal'/Ecal)) (paper eq. szrho, which is
  kappa rho). Refuted if the numerator of any component does not reduce to zero.
- P2 (sym) Theta = div u equals the paper's (sztht); sigma^a_b = Sigma e^a_b with the
  paper's Sigma (szshr); the electric Weyl tensor E^a_b = C^a_{cbd} u^c u^d = W e^a_b with
  the paper's W (szwey), same sign (Schwarzschild check: M' = 0, Ecal' = 0 gives
  E^r_r = -2M/R^3, the radial tidal stretching); the magnetic Weyl tensor vanishes
  (R_ijkt = 0 given the field equations). Refuted by any non-zero difference.
- P3 (sym) On the slice t = const (lapse 1, shift 0, K_ij = -(1/2) d_t gamma_ij, the
  sign of AthenaK, K = -Theta) the Hamiltonian and momentum constraints hold identically
  with S_i = 0; K^r_r = -(Rdot' - Rdot Ecal'/Ecal)/(R' - R Ecal'/Ecal),
  K^p_p = K^q_q = -Rdot/R.
- P4 (sym) The task text expects conformal flatness of the slice to fail in general. My
  prediction is the opposite [JUDGEMENT, from an argument written in DESIGN.md section 2]:
  the Cotton tensor of gamma_ij = (R' - R Ecal'/Ecal)^2/(1-k) dr^2 + R^2/Ecal^2 (dp^2+dq^2)
  vanishes identically for arbitrary R(r), k(r), S, P, Q(r); for k = 0 the slice is flat.
  Refuted if the Cotton tensor has a non-zero component.
- P5 (num) The evolution written with the universal function g(lambda),
  R = M^(1/3) t^(2/3) g(k t^(2/3)/M^(2/3)), reproduces `expball.exact.Shells.R` (written
  independently with the parametric cycloid and hypergeometric ages) to 1e-12 relative for
  every shell of data set 2 before its crunch; turnaround and crunch proper times to
  1e-12; k = -2E, Misner-Sharp m = M, K^r_r = KL, K^p_p = KT, rho at tau = 0 to 1e-12
  relative, in the limit of no dipole. Refuted by a larger difference anywhere.
- P6 (num) With no dipole the conformal map of this package gives the isotropic radius
  and psi of `expball.model.Ball.rbar_of_R` to 1e-10.
- P7 (num) With a dipole of amplitude eps = 0.1 (data set 2's LTB functions plus a
  rotating dipole supported in the transition shell), the Cartesian fields psi, K_ij, rho
  built through the conformal map satisfy the finite-difference Hamiltonian and momentum
  constraints with residuals that converge at the order of the stencil (2 and 4) in every
  norm, since the data are C-infinity (refuted: order below p - 0.3 at the finest pair).
- P8 (num) The difference between the Szekeres slice and the LTB slice with the same M, k
  (what a format-2 table can hold) is first order in eps: max|psi_Sz - psi_LTB|,
  max|rho_Sz - rho_LTB|/rho_b and max|K_Sz - K_LTB|/H have log-log slope 1.00 +- 0.05 in
  eps for eps <= 0.05. So a spherical table represents the Szekeres slice only at zeroth
  order in the dipole.
- P9 (num) For eps = 0.1 neither shell crossing (R'/R <= |b|) nor negative density
  (M'/(3M) <= |b|) occurs on any shell before the crunch of the core (tau = 44.45, data
  set 2) [to be computed; if it fails, eps is lowered and the failure stays on record].

## Entry 2, 2026-11-19 15:18 UTC: outcomes of P1-P9

- P1 HELD [VERIFIED, `sym/sym_szekeres.py --fast`, all ten components of
  G_ab + Lambda g_ab - 8 pi rho u_a u_b vanish at three exact rational points each, with
  Lambda kept; the registered repeat is run A-20261119-1528xx below]. The fully symbolic
  mode (`--only C` without `--fast`) did not finish within 50 minutes for the constraints
  and was not used; the random-point test is exact arithmetic (Schwartz-Zippel).
- P2 HELD: Theta, sigma^a_b = Sigma e^a_b, E^a_b = W e^a_b with the paper's formulas and
  signs, e = diag(-2, 1, 1); R_ijkt = 0 on shell (H_ab = 0); Schwarzschild limit W = M/R^3.
  The paper writes (+,-,-,-) and e_ab = h_ab - 3 z_a z_b; the mixed components used here
  are unambiguous.
- P3 HELD: Hamiltonian and momentum constraints, K^r_r, K^p_p, K = -Theta. A negative
  control (density doubled) is non-zero, as it must be.
- P4 HELD, against the expectation of the task text: the Cotton tensor of the comoving
  slice vanishes for arbitrary R(r), k(r), S, P, Q(r) (exact rational points), and also
  exactly for explicit polynomial functions (S = 1 + r/3 + r^2/5, P = r^2/7 + r/2,
  Q = r^3/11 - r/4, k = r^2/9, R = r + r^3/13, at (r, p, q) = (1/3, 2/5, -1/7): all nine
  independent components are 0 in rational arithmetic; probe script in
  scratch/A-emd-pbh/tmp/sym/, not registered). The k = 0 slice is flat (3-Ricci = 0); for
  k != 0 the slice is not flat. A first run reported four non-zero Cotton components: a
  random point had hit a zero of a denominator (exact evaluation gives zoo there); the
  check now skips singular points and the failure is on record here. The explicit
  conformal map (confmap.py) is a constructive proof: its identities hold symbolically
  (check E) and its pull-back equals the Szekeres metric to 1e-8 at 25 random points
  (finite differences, test_confmap_pullback_is_conformally_flat).
- P5 HELD with one bound exceeded: run A-20261119-151501-9cff966. Initial slice: M exact,
  k to 1.7e-16, rho 4.0e-16, KL 3.4e-15, KT 3.4e-15 (relative). R(tau) of 400 shells on
  400 times: 2.2e-14 up to 0.9 of the core crunch, 2.17e-12 at tau = 44.41, 0.1 per cent
  before the crunch of the core (R/r = 0.04) - the predicted 1e-12 is exceeded there, by
  the conditioning near the crunch; turnaround, crunch and R = 2M times 6.6e-15, 5.1e-15,
  5.1e-15. Figure `figures/fig_ltb_limit.png` (inspected).
- P6 HELD: isotropic radius of the map against `expball` 5.1e-12 (largest near r -> 0),
  psi 1.5e-12, rho 1.9e-12 rho_b, KL 1.2e-12 H at 20000 points (same run).
- P8 HELD: run A-20261119-151501-3e344a4. Fits over eps <= 0.05 give slopes 0.9996
  (psi), 1.004 (rho), 1.006 (K), 1.007 (KL - KT), 0.9995 (displacement of the centre of
  the r = 1 sphere); coefficients max|dpsi| = 0.0044 eps, max|drho|/rho_b = 1.84 eps,
  max|dK|/H = 1.43 eps, max|d(KL - KT)|/H = 1.11 eps, centre shift 1.93 eps (length units,
  ball radius 6). For eps = 0.1 the spherical table misses 0.19 rho_b of density and
  0.15 H of K, but only 4.4e-4 of psi. Figure `figures/fig_dipole_order.png` (inspected).
- P9 HELD: run A-20261119-151501-986153a. min over r and over tau up to 0.995 of the core
  crunch of (R'/R)/|b| = 10.0 (at tau = 0, where it is 1/eps by construction; it grows
  later), (M'/(3M))/|b| = 3.94. Figures `fig_slice_maps.png`, `fig_evolution.png`
  (inspected; the slice-map layout left an empty right margin and no z label: fixed in the
  script and rerun below).
- A defect found and fixed while testing (no registered run used the defective code):
  the safeguarded Newton loops (inverse map, cycloid angle, inverse of l) could leave a
  converged point at a bisection midpoint when the loop ended for all points at once; a
  slab of the mesh run then put one cell at the wrong shell (r = 0.0015 instead of 3.98).
  Converged points are now frozen, and a collapsed bracket counts as converged; serial
  and parallel mesh residuals agree to the last digit and batch and single-point
  evaluations agree exactly.

## Entry 3, 2026-11-19 15:19 UTC: predictions for the first AthenaK execution

Run: scripts/run_code_geodesic.py, processor executable of core-v0.3
(.work/build_cpu_v03/src/athena), periodic box [-8, 8]^3 at N = 32 and 64 cells per side,
nrpic_cosmo id = file with the field file of szekeres/codeid.py, one particle per cell at
rest with m = rho psi^6 h^3, CIC deposit, geodesic slicing (every lapse and shift driver
off), Z4c with nghost = 4, diss = 0.5, damp_kappa1 = 0.5, RK4 at CFL 0.25, to tau = 40
(the core crunches at 44.45). Predictions:

- P10 The field file is read and at tau = 0 the dumped energy density E equals the exact
  rho at every cell to the float32 precision of the dump (1e-6 relative): the CIC weight of
  a particle at a cell centre is 1 in that cell. chi = psi^-4 to 1e-6. Refuted by a
  larger difference anywhere.
- P11 alpha stays 1 to round-off (alpha_dev_max < 1e-12) and the run reaches tau = 40
  without failure at both resolutions.
- P12 The errors of K (= Khat + 2 Theta_Z4c), of E and of chi against the exact values at
  the same cells converge: the maximum relative error over the shell region falls by at
  least 4 from N = 32 to N = 64 at every dump time (second order or better; the stencils
  are sixth order, the cloud and the Kreiss-Oliger term are lower) [JUDGEMENT]. Absolute
  scale at N = 64: below 1e-2 relative for K at tau = 10 [JUDGEMENT, from the initial
  Hamiltonian residual of order 1e-3 of 16 pi rho_b at h = 0.25 (run
  A-20261119-151452-46f171e) and an amplification of order 10 to tau = 40].
- P13 The constraint monitor at tau = 0: rms H/(16 pi rho_b) over the shell region below
  1e-2 at N = 32 and smaller by at least 4 at N = 64.

## Entry 4, 2026-11-19 15:36 UTC: what the first AthenaK run shows while it runs; predictions for a second, short run

Run A-20261119-152010-94a9461, from its constraint statistics (`N32/szk.cstat.hst`) before
its own analysis finishes:

- N = 64 was stopped by me (kill of its process id) after start-up: on the loaded
  processors one cycle of 64^3 takes tens of seconds, so 640 cycles to tau = 40 would take
  hours. Its tau = 0 dump exists and is analysed by the run.
- N = 32 (h = 0.5): the whole-box maximum of |H| jumps from 9.6e-4 at tau = 0 (0.04 of
  16 pi rho_b, the size of the order-4 finite-difference residual of the data at this h,
  run A-20261119-152252-2ae031e: Linf 0.054) to 1.3e-2 at tau = 1 and 3.4e-2 at tau = 10;
  the mean |H| rises from 3.5e-5 to 1.4e-3; K leaves the exact range after tau = 20 and the
  run turns to NaN between tau = 24 and 28. P11 FAILED at N = 32 (and was not tested at
  N = 64). The data are under-resolved at h = 0.5: the initial momentum residual at this h
  is 34 per cent of 16 pi rho_b at its maximum (same mesh run), the smallest density scale
  is 0.55 (run A-20261119-152232-3d29cc1). Cause not established: resolution, the
  dissipation term (diss = 0.5 at h = 0.5), or geodesic slicing (no gauge damping) are
  candidates; none has been tested in a run where it could have failed.

Predictions for run 2 (scripts/run_code_geodesic.py --N 32 64 --tlim 2, dumps at
tau = 0.5, 1, 2, with a variant diss = 0):

- P14 If the early growth of |H| is a truncation effect of the under-resolved shell, the
  maximum and rms of H/(16 pi rho_b) over the shell at tau = 1 and 2 fall by at least 4
  from N = 32 to N = 64, with and without dissipation. If the dissipation drives it, the
  variant diss = 0 has a growth at least 3 times smaller at both N. Refuted (both
  hypotheses) if neither happens.
- P15 The relative error of K against the exact -Theta in the shell at tau = 2 falls by at
  least 4 from N = 32 to N = 64.

## Entry 5, 2026-11-19 15:39 UTC: outcomes of P10-P13 (run A-20261119-152010-94a9461)

Analysis of the run itself (`code_geodesic.json`, `figures/fig_code_geodesic.png`,
`fig_code_geodesic_profiles.png`, inspected):

- P10 HELD at N = 32 and 64: at tau = 0 the code's K equals the exact -Theta to 5e-16
  (the field file is read as written), E equals rho to 9e-9 (core) and 6e-8 (shell),
  chi = psi^-4 to 3e-8: the float32 precision of the dump. One particle per cell centre
  with the CIC deposit gives the exact density, as designed.
- P11 PARTLY: alpha stays 1 to 1.1e-13 (tau = 10) and 2.3e-13 (tau = 20); but the run at
  N = 32 does not reach tau = 40: K leaves the exact solution (relative error 0.15 in the
  shell and 0.17 in the core at tau = 10, 0.85 in the core at tau = 20) and the fields are
  NaN at tau = 30. N = 64 was stopped after start-up (entry 4). FAILED as stated.
- P12 NOT TESTED (no N = 64 evolution). At N = 32 the errors at tau = 10 are 15 per cent
  in K, 6.5 per cent in E and 4.4 per cent in chi (maximum over the shell): far above the
  "1e-2 at N = 64" scale predicted, which belongs to N = 64 and remains open.
- P13 HELD: the code's monitor at tau = 0, rms of H/(16 pi rho_b) over the shell, is
  9.8e-3 at N = 32 and 8.6e-4 at N = 64 (factor 11.4); over the core 9.7e-4 and 6.6e-5.
  The momentum monitor over the shell 1.5e-2 and 2.6e-3. These are the code's sixth-order
  operator on gamma_ij; the order-4 residual of this package at h = 0.47 and 0.23 was
  1.2e-2 and 1.4e-3 (shell, L2, run A-20261119-152252-2ae031e): the same size.
- The constraint grows fast after the start: rms H/(16 pi rho) over the shell 1.18 at
  tau = 10 and 6.3 at tau = 20 at N = 32 (normalised by the background density at that
  time). Cause: open (entry 4, run 2 below tests resolution and dissipation).

## Entry 6, 2026-11-19 16:05 UTC: outcomes of P7, P14, P15

- P7 PARTLY HELD: run A-20261119-152252-2ae031e (repeat A-20261119-153846-81db254, same
  numbers). Order-2 stencil at the finest pair (h = 0.117 -> 0.059): Hamiltonian 1.99,
  momentum 1.95 (all cells, L2). Order-4 stencil: Hamiltonian 3.84 (held, >= 3.7),
  momentum 3.61 (FAILED by 0.09: below p - 0.3); the maxima converge at 3.75 and 3.55.
  The LTB limit gives the same orders and norms to 2 per cent (3.84, 3.61), so the
  pre-asymptotic momentum order belongs to the smoothed top-hat profile and not to the
  dipole or the conformal map. In the homogeneous core the residuals stop at 6e-10 (L2)
  of 16 pi rho_b at h = 0.059: the round-off of psi from the map (about 1e-12) divided by
  h^2. Figures `fig_mesh_constraints.png`, `fig_residual_maps.png` (inspected).
- P14 FAILED as stated, with a clear reading: run A-20261119-153832-7097718. From N = 32 to
  N = 64 (one MeshBlock each, to tau = 2) the rms of H/(16 pi rho) over the shell falls
  from 0.304 to 0.095 at tau = 2 (factor 3.2; 3.3 at tau = 0.5, 4.0 at tau = 1), in the
  core from 0.099 to 0.028 (3.6): convergence, but by about 3 per halving, not the 4
  predicted. Without dissipation the growth is larger, not smaller (shell rms at tau = 2:
  0.688 at N = 32, 0.232 at N = 64): the Kreiss-Oliger term is not its cause, it damps it.
  The early growth of |H| is therefore a truncation effect of the under-resolved shell
  that converges at about order 1.7 at these cell sizes (h = 0.5, 0.25). Not tested: a
  third resolution (needs a card), the gauge (only geodesic slicing was run).
- P15 FAILED as stated: the maximum relative error of K in the shell at tau = 2 is 3.9e-2
  (N = 32) and 1.27e-2 (N = 64), factor 3.1 (order 1.6); in the core 2.2e-2 and 2.4e-3
  (factor 9.2); outside (Einstein-de Sitter, reached by the errors from the shell)
  1.4e-2 and 4.7e-3. E and chi errors fall by 3.2 and keep the ratio dE/E = 1.5 dchi/chi of
  a pure volume error (E = mass/sqrt(gamma), sqrt(gamma) = chi^(-3/2)), which says the
  particles stay at their cells: consistent with prediction 2 of DESIGN section 5, not a
  direct check of the particle positions.
- Reading [JUDGEMENT]: the code evolves the Szekeres hole towards the exact solution as the
  mesh is refined; at 64^3 the departure is 1.3 per cent in K by tau = 2. The test at the
  accuracy the brief asks for needs 128^3 and 256^3 to tau = 40 (DESIGN section 5) on a
  card; the processor build is too slow for that (64^3 to tau = 2 took 21 minutes).

## Entry 7, 2026-11-20 22:35 UTC (wave 3, round 1): choice of the dipole amplitude eps

Helper of A-emd-pbh, wave 3, package szekeres (card series). Rule fixed before the
registered run: take eps = 0.2 instead of 0.1 if (i) both regularity margins
(R'/R)/|b| and (M'/(3M))/|b| stay above 1.5 for all shells up to tau = 40, and (ii) the
finite-difference residuals of the initial slice (order-4 stencil, shell region, L2 and
maximum, N = 64 and 128 on [-8, 8]^3) grow by less than 25 per cent from eps = 0.1 to 0.2
while the non-spherical signal (direction dependence on a shell; Szekeres minus LTB at the
same cells) doubles. Otherwise keep 0.1. Reason: the test is of the code path without
symmetry, so what matters is the size of the non-spherical part of the solution against
the truncation error of the runs; the latter is set by the radial profile (P7: the LTB
limit has the same residuals to 2 per cent), so it should barely change with eps.

An unregistered trial of `scripts/run_eps_choice.py --n 32 --workers 4` (output in
scratch/A-emd-pbh/tmp/szekeres/eps_test, 2026-11-20 22:24 UTC) gave: margins 10.0 and
3.94 (eps = 0.1), 5.0 and 1.97 (eps = 0.2), minimum at tau = 0, as the exact 1/eps
scaling says (b is linear in eps; R, M do not depend on it); order-4 Hamiltonian residual
(shell, /16 pi rho_b) L2 1.74e-3 -> 1.82e-3 (N = 64), 1.53e-4 -> 1.59e-4 (N = 128), maximum
9.7e-3 -> 1.18e-2 and 9.8e-4 -> 1.13e-3; momentum L2 2.29e-2 -> 2.38e-2 and 2.79e-3 ->
2.86e-3, maximum 0.107 -> 0.127 and 1.57e-2 -> 1.75e-2 (growth 3 to 22 per cent);
direction dependence on a shell, |rho(+b) - rho(-b)|/mean 0.33 -> 0.71 and |K(+b) - K(-b)|/H
0.142 -> 0.292 at tau = 0, factor 2.0 to 2.2 at every tau up to 40. By the rule: eps = 0.2.
The residuals and margins do not depend on the --n of that trial (they are computed on
their own meshes); the gradient scales and the Szekeres-minus-LTB maxima do (h = 0.5 there).

P16 (registered repeat with --n 128, 6 workers): margins and residuals identical to the
trial to all printed digits; min rho/|grad rho| at tau = 40 below 0.17 (the value on the
axes, run A-20261119-152232-3d29cc1) for both eps, ratio eps 0.2 / eps 0.1 between 0.7 and
0.95 at every tau; Szekeres minus LTB at tau = 0: max |drho|/rho near 0.2 (eps = 0.1) and
0.6 (eps = 0.2), max |dK|/H 0.15 and 0.30. Refuted if a margin or residual differs, or if
the scale ratio falls below 0.6 (then the truncation error at eps = 0.2 would grow by more
than (1/0.6)^2 = 2.8 for a second-order error and the choice is reopened).

Decision: **eps = 0.2** for the card series and for the particle-number check (new
scripts default to it: `prep_code_files.py`, `analyse_code_runs.py`); `common.EPS` stays
0.1 so that the scripts of wave 3a reproduce their recorded runs.

## Entry 8, 2026-11-20 22:40 UTC: predictions for the card series and the particle-number check

Set-up (DESIGN sections 3-4, unchanged): eps = 0.2, periodic [-8, 8]^3, field file and one
particle per cell centre from `scripts/prep_code_files.py`, CIC, geodesic slicing,
nghost = 4, RK4, CFL 0.25, diss 0.5; deck `inputs/szekeres_geodesic_card.athinput`
(= szekeres_geodesic.athinput plus a restart output every tau = 10). Card executable of
release core-v0.3. Dumps at tau = 0, 10, 20, 30, 40. Members N = 64 (one 64^3 MeshBlock),
128 (one 128^3 block), 256 (eight 128^3 blocks: large blocks, because the cost of the
particle module grows with MeshBlocks times particles on the processors).

Cost and memory [JUDGEMENT from measured numbers]: Z4c on one A100 1.85e7 zone-cycles/s
at 128^3 (core run core-20261119-144437-6718c76, Slurm 4643, JOURNAL-omp entry on
core/build-openmp), 1.58e7 at 256^3 (A-20261119-144419-13d5601, bh_n256/athena.log);
particles: 2.1e6 particles with TSC at 64^3 cost about 0.1 s a step (same core run), so
with CIC about 2-3e-8 s per particle and step. Steps to tau = 40: 640, 1280, 2560. So
N = 64 about 0.5 min, N = 128 about 3.5 min, N = 256 1.3 to 1.6 s a step, 55 to 70 min:
it does not fit one job with the others; it runs under the wall-clock limit `-t` and, if
cut, continues from its restart file in a second job (restart checked on the processor:
a run restarted from its tau = 0 restart file gives the same final dump byte for byte,
smoke test at N = 16 in scratch/A-emd-pbh/tmp/szekeres/smoke, unregistered). Card
memory: Z4c 128^3 bench 4.4 GB peak and the 64^3 box with 2.1e6 particles 1.8 GB (same
core run) scale to about 35 GB (cells) + 10 GB (particles) for N = 256, below 80 GB.
Total for the package about 1.0-1.2 card-hours (cap 1.5).

Measured basis for the errors (eps = 0.1, processors, run A-20261119-153832-7097718):
N = 32 -> 64 at tau = 2 in the shell, rms |K - K_ex|/H 0.0416 -> 0.0088 (order 2.2), rms
|E - rho|/rho 4.0e-3 -> 8.2e-4 (2.3), max |chi - chi_ex|/chi 7.6e-3 -> 2.4e-3 (1.7), rms
H/(16 pi rho_b) 0.30 -> 0.095 (1.7); core rms K 0.016 -> 0.0015 (3.4). Growth at N = 32
(run A-20261119-152010-94a9461): shell rms K/H 0.042 (tau = 2), 0.084 (10), 0.18 (20),
non-finite by 30. The residuals of the data are the same at eps = 0.2 to 4 per cent
(entry 7), so these numbers carry over [JUDGEMENT].

- P17 (completion) N = 128 and N = 256 reach tau = 40 with finite fields; N = 64 reaches
  at least tau = 30 (N = 32 failed between 24 and 28 with errors three times larger).
  alpha = 1 to 1e-12 throughout; at tau = 0, K equals the exact value to 1e-15 and E
  equals rho to the float32 precision of the dump (1e-7). Refuted: N = 128 or 256
  non-finite before tau = 40, N = 64 before tau = 30, alpha off by more than 1e-12.
- P18 (sizes, shell, rms |K - K_ex|/H(tau)) N = 64: 0.02 at tau = 10, 0.3 at tau = 40;
  N = 128: 0.004 and 0.05; N = 256: 0.001 and 0.01 (the DESIGN estimate: per cent at
  tau = 40 needs h <= 0.06). rms |E - rho|/rho about a third of these, chi two thirds of
  E. The core errors grow faster than the shell's after tau = 20 (amplification about 75
  from tau = 10 to 40 in the core, run A-20261119-152232-3d29cc1) and are the largest at
  tau = 40. Refuted for a member if its shell value at tau = 10 or 40 lies outside a factor
  3 of the number given.
- P19 (orders) For the rms errors of K, E and chi in the shell and the core at tau = 10,
  20 and 30: the order of 64 -> 128 and of 128 -> 256 is at least 1.5, and the order of
  128 -> 256 is not lower than that of 64 -> 128 by more than 0.3 (approach to the
  asymptotic range, which is 4 for RK4 at fixed CFL with sixth-order stencils). At
  tau = 40 the core (density scale about 2 cells at N = 256) may be pre-asymptotic: order
  at least 1. Refuted by an order below these anywhere, or an error that grows with N.
- P20 (the test sees the non-spherical part) At N = 256 the maximum K error in the shell
  is at least 10 times smaller than the maximum of |K_Szekeres - K_LTB|/H at the same
  cells (0.30 at tau = 0, larger later), and the maximum E error at least 10 times smaller
  than the maximum |rho_Sz - rho_LTB|/rho, at every dump to tau = 30; at N = 128 at least
  5 times. Refuted otherwise.
- P21 (constraints) rms H/(16 pi rho_b(tau)) in the shell converges with the same order as
  the K error (within 0.5) between 128 and 256 at tau = 10 and 20.

Particle-number check (processors, release core-v0.3, one thread, N = 32, eps = 0.2, to
tau = 2, dumps 0.5, 1, 2): 1 particle per cell centre against 8 per cell on the lattice of
spacing h/2 with m = rho psi^6 (h/2)^3. In geodesic slicing the particles do not move, so
the particle number enters only through the deposit: with CIC each sub-particle gives 3/4
to its cell and 1/4 to the neighbour in each direction, so the 8-particle source is the
density smoothed by about (3/32) h^2 d^2/dx^2 per direction, an O(h^2) error of the source
(the 1-particle source is exact at the cell centres).

- P22 At tau = 0 the 8-particle run's E equals the deposit predicted by the preparation
  run (`E_dep` of slice_t0.npz, computed in numpy from the same weights) to 1e-6
  relative; its constraint monitor (rms H, shell) is larger than the 1-particle run's by
  roughly the rms of (E_dep - rho)/rho_b (the source error enters H as 16 pi dE).
- P23 At tau = 2 the 8-particle run is not closer to the exact solution: its shell errors
  of K, E, chi (rms) are between 0.7 and 3 times those of the 1-particle run (smoothing
  error of the source of the size of the mesh truncation at h = 0.5), and the difference
  between the two runs in E stays the initial deposit difference within 30 per cent (the
  mass per cell is fixed). So at this mesh the result does not depend on the particle
  number beyond the O(h^2) deposit term. Refuted if the 8-particle errors are below 0.7 or
  above 3 times the 1-particle ones, or if the 8-particle run diverges.

## Entry 9, 2026-11-20 22:36 UTC: PAUSED (flag locks/PAUSE, five-hour window at 97 per cent, written 14:33 PST)

Where I stopped. Done and committed (8cc42412): eps = 0.2 chosen by the rule of entry 7
(unregistered trial numbers; the registered repeat P16 is not run yet); predictions
P16-P23 (entry 8); scripts `run_eps_choice.py`, `prep_code_files.py`,
`run_cpu_members.py`, `analyse_code_runs.py` (smoke-tested at N = 16 on the processor,
unregistered, outputs in scratch/A-emd-pbh/tmp/szekeres/); deck
`inputs/szekeres_geodesic_card.athinput` (restart every tau = 10).

Running when the flag appeared (my flag check and the submission were one command; the
flag was written one minute before): run A-20261120-223422-8cc4241, the files of the
series (eps = 0.2, one particle per cell, N = 32, 64, 128, 256; about 15 min on 4 cores,
background). It is left to finish (no account usage). Nothing else was started; no card
job was submitted.

Next, in this order, after the pause is lifted:
1. `harness/bin/nrpic-run finish A-20261120-223422-8cc4241` (check run.log and
   prep_ppc1.json: four members, predicted_E0_rel_err about 1e-16).
2. Card batch (count first: `squeue -h -u $USER -o %j | grep -c '^A-'`, submit only if
   below 2): list file with PREP=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223422-8cc4241
   and DECK=tracks/A-emd-pbh/szekeres/inputs/szekeres_geodesic_card.athinput, three lines
   `N64 DECK mesh/nx1=64 mesh/nx2=64 mesh/nx3=64 meshblock/nx1=64 meshblock/nx2=64
   meshblock/nx3=64 problem/id_file=PREP/N64/fields.bin
   particles/particle_file=PREP/N64/particles.nrp -t 00:04:00`, the same for N128
   (blocks 128, -t 00:08:00) and N256 (blocks 128, -t 00:40:00); submit with
   `harness/bin/nrpic-run submit --kind scouting --gate G2 --package
   tracks/A-emd-pbh/szekeres --launcher batch --exe
   /data/haiyangw/nrpic/.work/build_gpu_v03/src/athena --list <file> --wall 00:58:00
   --purpose "..."`. If N256 stops at its -t limit before tau = 40, continue it from its
   newest restart file (`N256r <rundir>/N256/rst/szk.NNNNN.rst -t ...`), within the
   remaining card cap (1.5 card-hours in all for this package).
3. Processors meanwhile: prep of the 8-particle files (`prep_code_files.py --N 32 --ppc 8
   --eps 0.2 --workers 2`, registered), then the particle-number check with
   `run_cpu_members.py` (needs one change first: members from two preparation runs, e.g.
   NAME=DIR), then `analyse_code_runs.py --members N32 N32_ppc8 --label ppc`; the
   registered repeat of `run_eps_choice.py --n 128` (P16).
4. Analysis of the card members: `analyse_code_runs.py --run <card run dir> --prep PREP
   --members N64 N128 N256 [--cont N256:N256r] --label series`; outcomes of P17-P21 here;
   DESIGN sections 6-7 and README results.

## Entry 10, 2026-11-25 04:15 PST (lead of batch 17): the card series goes into the shared queue

Preparation run A-20261120-223422-8cc4241 is complete (manifest status completed; prep_ppc1.json:
four members, predicted E0 error 1e-16). Predictions P17-P21 of entry 8 stand as written (P22-P23,
the processor particle-number check, are not part of this submission). Two changes, neither in a
prediction: (1) executable: the card build of release core-v0.7 (`.work/build_gpu_v07/src/athena`)
instead of v0.3, by the rule that new runs use v0.7 (geodesic slicing, no Gamma-driver, so
dt_gauge does not apply; the non-finite guard of v0.5 is on by default and stops a blown-up member
with exit 3, which P17 counts as non-finite); (2) N = 256 runs as its own chain (restart output
every tau = 5 instead of 10 so that a segment cut by preemption loses less than 10 minutes),
N = 64 and 128 as one batch job (`lists/card_n64_n128.list`). Cost as entry 8: about 1.0-1.2
card-hours, cap 1.5. Queue entries: a-szk-n64-128 and a-szk-n256 (priority 2: G2 item C1 (iii)).
Read by `scripts/analyse_code_runs.py` (smoke-tested at N = 16, entry 9).

## Entry 11, 2026-11-25 18:50 PST (lead of batch 23): the card series ended; first reading against P17-P21

Runs (closed before reading): N64 and N128 in one batch job A-20261125-213939-0ad9f29 (q0040; closed failed: both
stopped by the non-finite guard, exit 3; 0.09 card-hours), N256 as a chain A-20261125-231808-0784bc9 (q0041; closed
stopped: the queue entry gave no segment count, so the chain ran one segment, MAX_SEGMENTS = 1, and ended at
tau = 21.2 of 40; ~0.98 card-hours). Field dumps every tau = 10: N64 at 0, 10, 20, 30; N128 at 0, 10, 20, 30; N256 at
0, 10, 20.
Reader: analyse_code_runs.py takes ~1 min per dump at N = 64, ~15 at N = 128 and an estimated hour at N = 256 on one
loaded core. A three-member run (A-20261126-022804-0bc68c2) and an in-session N64/N128 run (A-20261126-023242-f3f0578)
were stopped by hand and closed as stopped; both logs hold the N64 rows (identical). Detached for the next session:
A-20261126-024724-425ed7f (N64, N128: orders 64 -> 128 and figures) and A-20261126-023245-1dd80ad (N128, N256).
Outcomes so far (from athena.log of the members and the N64 rows of the stopped readers; no figure yet, so P18-P21
are not judged here):
- P17 (completion): N64 reaches tau = 30.25 (predicted >= 30: holds, barely); N128 is non-finite at tau = 37.47 (guard
  stop) before tau = 40: REFUTED for N128; N256 not decidable (finite at tau = 21.2 when the segment cap ended it).
  The breakdown time rises with N (N32 24-28, entry 9; N64 30.25; N128 37.47). alpha = 1 to 2.3e-13 (tau 10) and
  4.6e-13 (tau 20) on N64; at tau = 0 the shell's max |K - K_ex|/H is 1.8e-15 and max |E - rho|/rho 5.9e-8 (the
  clauses on alpha and tau = 0 hold on N64).
- P18 for N64 at tau = 10: shell rms |K - K_ex|/H = 0.0268 (predicted 0.02, within the factor 3: holds); at tau = 40
  no member exists. N64 at tau = 30: 1.04 (shell), the run is blowing up (guard 0.25 later).
- P20 on N64 (not a clause; for orientation): shell max K error 0.102 against the non-spherical signal 0.68 at
  tau = 10 (ratio 6.7), 0.26 against 1.42 at tau = 20 (5.5).
Next: read the two detached analyses (P18 at N128/N256, P19 orders, P20 at N = 128 and 256, P21), look at their
figures, entry 12. Whether N256 is continued to tau 40 (about 0.8 card-hour) is asked of orch
(outbox g2-state-after-batch-23).

## Entry 12, 2026-11-25 19:27 PST (batch 24): N256 continued to tau 40 (decision 0043 item 1(c)), prediction before the job

What: chain A-20261125-231808-0784bc9 (N = 256) is continued in place from rst/szk.00005.rst (tau = 21.203, cycle
1357) by `threshold_ball/scripts/continue_chain.sh A-20261125-231808-0784bc9 3` (same run, deck, executable and
arguments; MAX_SEGMENTS 1 -> 3, so at most two more segments). The wrapper now also appends the `continuations` record
that nrpic-run reads (harness/RULES.md, decision 0039 item 5). Field dumps at tau 30 and 40 are numbered 00003 and
00004 (NrpicStartup skips the dump times already passed, nrpic_io.cpp 1357-1362), so the dumps 0-2 that the detached
reader A-20261126-023245-1dd80ad is reading are not touched. Cost [measured in segment 1: 2.16 s a cycle at
dt = 0.015625]: 1203 cycles to tau 40, ~44 min plus start-up, so one segment of 50 min is expected, two at most
(~0.8 card-hours expected, cap 2).
Basis for the numbers below: breakdown (guard stop) times N32 24-28, N64 30.25, N128 37.47 (entry 11); the core
crunches at tau = 44.454. Two readings of the trend: an increment of 6-7 per doubling gives N256 at 43-45; a distance
to the crunch that halves per doubling (14.2 at N64, 7.0 at N128) gives 3.5, i.e. N256 at ~41. Shell rms
|K - K_ex|/H: N64 0.0268 (tau 10), 0.0616 (20), 1.04 (30); N128 0.0043 (10), 0.0123 (20) (reader rows of
A-20261126-024724-425ed7f and A-20261126-023245-1dd80ad, in their run.log): orders 2.6 and 2.3.
- P17 for N256 (stands as written in entry 8): finite fields to tau = 40, alpha = 1 to 1e-12. Expected to hold, with a
  small margin (breakdown ~41 by the crunch-distance reading). Refuted by a guard stop (exit 3) or a non-finite dump
  before tau = 40.
- P24 [JUDGEMENT, new; P18 as written is still judged as written]: N256 shell rms |K - K_ex|/H at tau = 30 lies in
  [0.004, 0.04] (N128 at tau 30 times 2^-2.3, with N128 at tau 30 between 0.02 and 0.2: it broke 7.5 later); at
  tau = 40 it lies in [0.03, 1]: the member is within a few tau of its own breakdown, so P18's 0.01 at tau = 40
  (factor 3: up to 0.03) is expected to FAIL. Refuted if tau 30 lies outside [0.004, 0.04] or tau 40 below 0.03.
Read by `scripts/analyse_code_runs.py` on the dumps 00003-00004 (detached, ~1 h a dump on one core), P19 at tau 30
from N128's tau 30 row; close the run again with `harness/bin/nrpic-run finish A-20261125-231808-0784bc9` once no job
of it is in squeue.

## Entry 13, 2026-11-26 13:25 PST (lead of batch 28): P17 for N256, P18-P21 from the two readers (figures looked at)

Runs, closed before reading: readers A-20261126-024724-425ed7f (N64, N128; closed by batch 24) and
A-20261126-023245-1dd80ad (N128, N256 dumps tau 0, 10, 20; closed completed 13:21 PST); the N256 chain
A-20261125-231808-0784bc9 continued by q0067 (segment 2, job 5380, 0.76 h of card time, STATUS DONE at tau = 40.000,
cycle 2560, exit 0). Figures looked at: fig_code_n64n128_convergence.png, fig_code_n128n256_errors.png,
fig_code_n128n256_convergence.png (slopes between the h^2 and h^4 guides, steeper for the core).
- P17 (completion). N256 reaches tau = 40 with finite fields (szk.nrpic.hst and szk.cstat.hst: no non-finite row to
  t = 40; exit 0): the completion clause HOLDS for N256 (the crunch-distance reading of entry 12, breakdown ~41, is
  not contradicted). The clause "alpha = 1 to 1e-12 throughout" is REFUTED as written for N128 and N256: max |alpha - 1|
  over alpha_min and alpha_max of szk.nrpic.hst is 6.8e-13 (N64), 1.70e-12 (N128, above 1e-12 from tau = 22.25) and
  3.64e-12 (N256, above 1e-12 from tau = 11.1), rising linearly in the cycle count at 1.4e-15 per cycle on both N128
  (1200 cycles) and N256 (2560 cycles) [the rate is VERIFIED from the files; that it is round-off of the geodesic
  lapse update is JUDGEMENT, the rate being the same on two meshes]. Entry 11 checked the clause on N64 only. The
  breakdown series (N32 24-28, N64 30.25, N128 37.47, N256 > 40) stands.
- P18 (shell rms |K - K_ex|/H). N64: 0.0268 at tau 10 (0.02 +- factor 3: holds); at tau 40 no value (broke at 30.25):
  not met. N128: 0.00430 at tau 10 (0.004: holds); at tau 40 no value (broke at 37.47): not met. N256: 2.77e-4 at
  tau 10 against 0.001: below a factor 3 (3.6): REFUTED as written (the member is better than predicted); tau 40 is
  read by A-20261126-212141-7eeb046 (entry 14).
- P19 (orders >= 1.5; 128->256 not lower than 64->128 by more than 0.3). 64->128 at tau 10, 20, 30: shell K 2.64,
  2.33, 4.53; E and chi 2.82, 2.48, 2.45; core K 3.76, 3.66, 4.30; core E 3.39, 3.62, 3.68. 128->256 at tau 10, 20:
  shell K 3.96, 3.62; E, chi 4.01, 3.69; core K 5.13, 4.22; core E 5.23, 4.57. HOLDS at tau 10 and 20 (every order >=
  2.3, and 128->256 is higher than 64->128); tau 30 for 128->256 waits for A-20261126-212138-49b9a2d (entry 14).
- P20 (the test sees the non-spherical part; ratio of the signal max to the error max). N256: K 0.686/0.00238 = 288
  (tau 10), 1.43/0.00781 = 183 (20); E 0.714/0.000519 = 1376, 0.773/0.00194 = 398 (>= 10: holds). N128: K
  0.685/0.0253 = 27, 1.42/0.0666 = 21, 3.45/0.582 = 5.9 (tau 30); E 110, 47, 41 (>= 5: holds, barely for K at tau 30).
  HOLDS at N128 to tau 30 and at N256 to tau 20; N256 at tau 30 in entry 14.
- P21 (constraint order equal to the K order within 0.5, 128->256, shell). tau 10: H 4.01 against K 3.96 (holds);
  tau 20: H 4.65 against K 3.62 (difference 1.03): REFUTED at tau 20 (the Hamiltonian residual converges faster than
  the K error; the K error is not a constraint violation alone).
