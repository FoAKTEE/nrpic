# JOURNAL of flrw_conv (helper of B-emd-gw, wave 3 round 1)

Package: G2 criterion (a) of Track B (`coord/CHARTER.md` section 9.5): "the scale-factor
error and the linear growth rate of the particle FLRW run reach the sub-percent level and
converge in particle number and mesh". What was missing: `verify_cosmo/VERIFY.md`
section 7 items 1-2 (no particle-number leg, no growth rate f, no clean mesh sequence of
test B in the production configuration). Labels [VERIFIED], [BACKGROUND], [JUDGEMENT],
[TO VERIFY] as in the brief.

## Entry 1 (2026-11-20 14:30 PST): design, cost, predictions (before any run)

### Design

Units and gauge (`cosmo/README.md`): G = c = 1, initial Hubble rate 1 at a = 1, lapse
d_t alpha = -(1/3) alpha^2 K, zero shift; t is conformal time, a(t) = (1 + t/2)^2,
alpha = a, chi = a^-2, K = -3 a^-3/2, E = rho_0 a^-3 with rho_0 = 3/(8 pi); a = 1001 at
t = 61.277. Production configuration (`cosmo/README.md` lines 42-47): cubic cloud (pcs),
compensation c = 1/6, c2 = 7/15, cubic-spline metric (bspline), dt_expansion = 0.01,
damping 0.5 per unit of conformal time. Courant number 0.25 (as test B of `cosmo/`). Box
for both legs: L = 1.35085 initial Hubble radii = 128 Mpc/h of test B of
arXiv:1904.07841 (`Main.tex:415`), so that leg F is the background of leg B and both have
the same step sequence. Decks: `inputs/flrw_prod.athinput` (F, id = flrw),
`inputs/mode_prod.athinput` (B, id = file, step limit 0.002).

Leg F (homogeneous dust, a = 1 to 1001), initial data `cosmo/ic/make_lattice.py`:

| name | mesh | ppc (per cell) | noise A (absolute) | where |
|---|---|---|---|---|
| f_n16_p1_a0, f_n16_p1_a2 | 16 | 1 | 0, A2 | processors |
| f_n32_p{1,2,3}_a0 | 32 | 1, 8, 27 | 0 | card job J1 |
| f_n32_p1_a1 | 32 | 1 | A1 | J1 |
| f_n32_p{1,2,3}_a2 | 32 | 1, 8, 27 | A2 | J1 |
| f_n64_p1_a0, f_n64_p1_a2 | 64 | 1 | 0, A2 | card job J2 |

A2 = 4.2214e-4 = 0.01 h(32), A1 = A2/10; uniform in (-A, A) per component, seed 1
(`make_lattice.py` lines 51-54). A is fixed in length across meshes and particle
numbers, so "fixed noise" means one displacement amplitude per particle.

Measures (columns of `flrw.nrpic.hst` and `flrw.cstat.hst`, headers read in
`runs/cosmo/dav_b_n32_pcs4b_f2`): relative scale-factor error against (1 + t/2)^2
  - e_alpha = max(|alpha_max - a|, |alpha_min - a|)/a (lapse, extrema over the mesh),
  - e_chi from chi_min, chi_max (a = chi^-1/2, extrema),
  - e_V = (V/L^3)^(1/3)/a - 1 with V the proper volume (box average of the volume element),
  - e_K from mean_K (a = (-K/3)^-2/3, box average);
constraints Hr_max, Hr_mean, Mr_max, M_max, Theta_max from `.cstat.hst`; density extrema
E_min, E_max. The noise-induced part of a measure is its difference to the lattice run
of the same mesh.

Leg B (test B: delta_* = A sin(2 pi x/L), A = 1e-7, `Main.tex:413-415`; a = 1 to 1001),
initial data `cosmo/ic/make_east.py --delta 1e-7 --ratios 1,0,0`, step limit 0.002:

| name | mesh | ppc | end | where |
|---|---|---|---|---|
| b_n16_p1 | 16 | 1 | a = 1001 | processors |
| b_n32_p{1,2,3} | 32 | 1, 8, 27 | a = 1001 | J1 |
| b_n64_p1 | 64 | 1 | a = 1001 | J2 |
| b_n128_p1 | 128 | 1 | a = 51 (t = 12.283), by cost | card job J3 |

The mesh sequence is at one particle per cell (16, 32, 64, 128); the particle-number
sequence at 32^3.

Growth rate. The code's slicing is the longitudinal gauge for the growing mode at linear
order: in arXiv:1904.07841 the zero-shift gauge with d_t alpha tied to K and the
Zel'dovich condition keeps phi constant and gives the conformal Newtonian line element
(`Main.tex:659-670`), and `make_east.py` (lines 11-15) writes that dictionary. Then
(`Main.tex:673`) delta(a) = -2 [1 + k^2/(3 H_c^2)] phi_0 sin kx with H_c^2 = 1/a here,
k = 2 pi/L = 4.65128, k^2/3 = 7.2116:
  - D_delta(a) proportional to 1 + k^2 a/3, f_ref(a) = (k^2 a/3)/(1 + k^2 a/3) =
    0.8782 (a = 1), 0.9863 (10), 0.99862 (100), 0.999861 (1001) [VERIFIED: arithmetic of
    `Main.tex:673`]. The dictionary matters: f_ref differs from the Einstein-de Sitter
    value 1 by more than 1e-2 for a < 13.7.
  - The gauge-invariant contrast delta_* = delta - 3 H_c v (`Main.tex:629`) obeys
    k^2 Phi = -(3/2) H_c^2 delta_* (`Main.tex:633`), so for the growing mode
    delta_* is proportional to a and f_* = 1 exactly [BACKGROUND]. v is the potential of
    the coordinate velocity, S_x = E a d_x v at linear order [JUDGEMENT: from
    S_i = rho W u_i, u_i = a V^i; to be checked against the data, where it must give
    delta_* = delta_N of the initial data].
Three estimators from the line records (`east.line.bin`: chi, alpha, K, E, S_x along the
first x1 line every 16 steps), each by projection on sin kx or cos kx (mean removed):
  (i) D_delta from delta = E a^3/rho_0 - 1, against f_ref;
  (ii) D_* = D_delta - 3 H_c v_amp with v_amp from S_x/(E a k), against 1;
  (iii) D_Phi = a phi_amp with phi = (a^2 chi - 1)/2 (Poisson form), f_Phi = 1 +
        d ln phi_amp/d ln a, against 1.
f = d ln D/d ln a by centred differences on the record sequence; also the amplitude
error e_D(a) = D/D_ref - 1 with D_ref from the analytic phi_0 = -(3/2) A/k^2
(`cosmo/analysis/daverio_b.py` line 31).
Decaying mode. Dust has delta_* = A_+ a + A_- a^-3/2 [BACKGROUND]; a decaying part of
relative size eps = A_-/A_+ at a = 1 gives f_* - 1 = -(5/2) eps a^-5/2 / (1 + eps a^-5/2).
The initial data carry the growing-mode (Zel'dovich) velocities of the dictionary with a
constraint-solved conformal factor (`make_east.py` lines 120-172), so eps is set by the
discretisation only; it is fitted from D_*(a) on 1 <= a <= 5.

### Cost (step 2), from logs

- Cards: 32^3 with 8 per cell 0.019 s per step (`runs/cosmo/dav_b_n32_pcs4b_f2/athena.log`:
  6660 steps, 125 s); 64^3 with 1 per cell 0.057 s per step, 64^3 with 7.1e6 particles
  0.53 s per step, 128^3 with 1 per cell 0.49 s per step (run B-20261119-153655-2deca0a,
  `e1_p1_n64`, `e1_p3_n64`, `e1_p1_n128/athena.log`); 128^3 with 1 per cell 0.37 s per
  step (`runs/cosmo/dav_c704_n128_pcs4bt/athena.log`). Particles about 7e-8 s per
  particle-step.
- Steps: F (step limit 0.01, Courant 0.25 h) about 2950, 5810, 11600 at 16, 32, 64
  (5807 at 32 in `runs/cosmo/dav_b_n32_pcs4b`); B (limit 0.002) about 4350, 6660, 12000 at
  16, 32, 64 (6660 in `dav_b_n32_pcs4b_f2`); B at 128 to a = 51: about 4690.
- J1: F32 (7 runs) about 1230 s, B32 (3) about 700 s: 0.55 card-h. J2: B64 and two F64,
  about 2050 s: 0.57 card-h. J3: B128 to a = 51, 1700-2300 s: 0.65 card-h. Sum about
  1.8 card-hours of the 2.5 allowed. B128 to a = 1001 would be 23000 steps, 2.4-3.1
  card-hours: beyond the cap, not run.
- Processors (core's threaded build, `threaded_build.md` section 5 on core/build-openmp):
  Z4c 1.1e4 zone-cycles/s per thread, particles 3.3e-5 s per particle-step on one thread
  (64^3 box with 2.1e6 particles: 94.3 s per step). 16^3 at 6 threads about 0.1 s per
  step: the three 16^3 runs take about 20 minutes; 32^3 with 27 per cell would take about
  10 hours, so every 32^3 run goes to a card.
- Kind: scouting for all (nrpic-run refuses production for G2 before the tag
  stage/B-emd-gw/G1-pass-* and without a pre-registration); card executable the release
  `.work/build_gpu_v03/src/athena`, processor executable
  `scratch/core/exe/core_build-openmp/athena_cpu`.

### Predictions

F, lattices (no noise):
- PF1. Every scale-factor measure below 1e-6 at all times, every mesh and particle
  number. At 32^3 about 1e-7 (the integrator on the background: error of the mean density
  4.0e-7 at 32 cells with the limit 0.01, `cosmo/TESTLOG.md` line 1879, i.e. 1.3e-7 in a).
  At 64^3 the Courant step (0.0053) is below the limit throughout, so the step is half
  that of 32^3 and the error about 1/16 (fourth order) [JUDGEMENT]; at 16^3 the step grows
  to 0.021 after t = 2.2, so the error is larger than at 32^3 by a factor 2 to 5
  [JUDGEMENT]. This "mesh" sequence is a step sequence: the fields are uniform.
- PF2. A lattice of 8 or 27 per cell deposits exactly the same uniform density, so the
  8 and 27 per cell runs equal the 1 per cell run to rounding (relative 1e-12) in every
  field column.
- PF3. Hr_max below 1e-6 throughout.
F, position noise:
- PF4. Every scale-factor measure stays below 1e-3 at all a (sub-percent by ten at least),
  also after the cell-scale contrast turns nonlinear at A2 (expected near a = 100-300).
- PF5 (laws, [JUDGEMENT]). Independent displacements of rms A/sqrt(3) per component give
  a deposited contrast delta_rms proportional to (A/h) N_c^-1/2 (N_c = ppc^3 particles of
  mass 1/N_c per cell) and a potential Phi_rms proportional to A h N_c^-1/2 (the
  displacement noise has P_delta ~ k^2, Phi_k = -(3/2) delta_k/k^2 at k >> H_c). The
  extrema of alpha and chi are first order in Phi: their noise part scales as
  A h N_c^-1/2, i.e. 1 : 0.354 : 0.192 for 1, 8, 27 per cell, x10 from A1 to A2, and
  1 : 0.5 for 32 to 64 cells at fixed A. The box averages (proper volume, mean K) are second
  order: noise part of order <delta Phi>, proportional to A^2/N_c (1 : 0.125 : 0.037),
  independent of the mesh, growing with the contrast (proportional to a) while linear.
- PF6 (sizes). At A2, 1 per cell, 32^3: delta_rms of a few 1e-3 (measured from the
  initial data by `scripts/ic_stats.py` before the runs), Phi_rms about 1e-6 to 1e-5, so
  e_alpha, e_chi about 1e-6 to 1e-5; e_V, e_K about 1e-8 at a = 1, rising to at most 1e-5.
  The initial Hamiltonian constraint is violated at relative size delta (metric uniform,
  density not): Hr_max about delta_max at t = 0, then damped.
- Refuted if any run reaches 1e-2 in any scale-factor measure, or if the noise part of
  e_alpha (or e_chi) at fixed A does not fall from 1 to 8 to 27 per cell (by at least a
  factor 2 from 1 to 27).
B, growth rate:
- PB1. |f_delta - f_ref|, |f_* - 1|, |f_Phi - 1| below 1e-3 at every recorded a, mesh and
  particle number; after a = 2 below 1e-4. Basis: amplitude over linear theory 0.99999
  and density error with the mean removed 8e-5 at most over the thousandfold expansion
  at 32 cells (`TESTLOG.md` lines 1887-1896).
- PB2. Decaying mode |eps| < 1e-4, so f_* - 1 at a = 1 below 3e-4 in size.
- PB3. Mesh: the amplitude error |e_D| falls between 16, 32, 64, 128 at second order or
  better (cloud and reconstruction are fourth order; TESTLOG line 1901); the f error falls
  likewise until a floor at or below 1e-6 (precision of a 1e-7 wave in E, record spacing).
- PB4. Particle number (lattices, 32^3): f of 1, 8, 27 per cell agree to 1e-5; e_D
  differs between them at the 1e-5 level or below.
- PB5. f_ref at a = 1 is 0.878, so comparing f_delta with 1 instead of the dictionary
  would show 12 percent; f_* and f_Phi must show no such offset.
- Refuted if any |f - reference| reaches 1e-2, or if the errors do not fall from 32 to 64
  to 128 cells without a floor whose cause a run has tested.

## Entry 2 (2026-11-20 14:35 PST): initial data, submissions, estimator of f

Initial data: runs B-20261120-222902-6b0be3c (leg F, all meshes; leg B at 16 and 32 cells;
18 s) and B-20261120-222908-8aede2c (leg B at 64 and 128 cells; 40 s), both completed.
Deposited contrast of the leg-F data with the production cloud (`scripts/ic_stats.py`,
`<case>/ic_stats.json` in the first run) [VERIFIED, run B-20261120-222902-6b0be3c]:

| case | delta_rms (compensated) | delta max | Phi_rms | <delta Phi> |
|---|---|---|---|---|
| lattices, any mesh and ppc | below 6e-15 | below 3e-14 | below 2e-17 | 1e-32 |
| n32, 1/cell, A1 | 1.061e-3 | 4.11e-3 | 5.79e-7 | -4.46e-10 |
| n32, 1/cell, A2 | 1.061e-2 | 4.14e-2 | 5.79e-6 | -4.46e-8 |
| n32, 8/cell, A2 | 3.595e-3 | 1.55e-2 | 1.99e-6 | -5.05e-9 |
| n32, 27/cell, A2 | 1.963e-3 | 8.88e-3 | 1.07e-6 | -1.50e-9 |
| n16, 1/cell, A2 | 5.331e-3 | 1.99e-2 | 1.16e-5 | -4.50e-8 |
| n64, 1/cell, A2 | 2.122e-2 | 9.75e-2 | 2.93e-6 | -4.42e-8 |

The laws of PF5 hold for the initial data: Phi_rms 1 : 0.344 : 0.185 for 1, 8, 27 per cell
(predicted 1 : 0.354 : 0.192), 2 : 1 : 0.51 for 16, 32, 64 cells (predicted proportional
to h), x10 from A1 to A2; <delta Phi> 1 : 0.113 : 0.034 (predicted 1 : 0.125 : 0.037),
mesh-independent to 2 percent, x100 from A1 to A2. The compensation raises the raw
contrast by 2.5 (white noise sits near the Nyquist scale). This checks the initial data
only, not the evolution. At 64 cells and A2 the contrast starts at 2e-2 (rms), so with
growth proportional to a that run turns nonlinear near a = 30 to 50 [JUDGEMENT].
Leg B data: largest Hamiltonian residual of the solve 2.3e-13 to 3.6e-12, largest
|psi_N| 6.9e-9 (`b_*.log` of the two runs).

Submissions: card job J1 = run B-20261120-222955-c8e16e3 (Slurm 4746, pending behind
nine jobs at 14:30); processor runs P1 = run B-20261120-223006-24448ac (16^3, four
threads, 0.097 s per step). J2 and J3 wait: the owner has two card jobs queued (4745 of
another helper and 4746).

Estimator of f, fixed before any run of this package was analysed (decided on a
development check of the reader on the old run `runs/cosmo/dav_b_n32_pcs4b_f2`, whose
numbers are not results of this package): (1) the error f - f_ref is computed as
d ln(D/D_ref)/d ln a, not as the difference of two difference quotients, because the
centred difference of ln D itself carries a truncation error of order (Delta ln a)^2 f''/6
(1.6e-4 at a = 1.1 with records 0.116 apart in ln a); (2) the derivative is the slope of a
straight-line fit over a window of 0.1 in ln a, because late in the run the records come
closer in ln a (3e-4 per step) and the record-to-record jitter of an amplitude (1e-5 in
phi) would otherwise be amplified; the pointwise difference quotient is kept as `_fd`.

## Entry 3 (2026-11-20 14:35 PST): PAUSED (locks/PAUSE written 14:33)

Stopped here on the pause flag. One step started after the flag appeared (my check printed
the flag but did not stop the chained command): the initial data of the optional
Poisson-like start, run B-20261120-223448-7f7c034 (one second, completed, finished; case
f_n32_p1_a3, A3 = h/2 at 32 cells: delta_rms 0.469 compensated, Phi_rms 2.7e-4,
<delta Phi> -9.0e-5). Nothing else was started after 14:33.

State for the restart:
- Card job J1 = run B-20261120-222955-c8e16e3, Slurm 4746, PENDING (leg F at 32^3, leg B at
  32^3 with 1/8/27 per cell). It may run on its own. When it has ended: `nrpic-run finish
  B-20261120-222955-c8e16e3`; outputs in scratch/B-emd-gw/B-20261120-222955-c8e16e3/<case>/.
- Processor runs P1 = run B-20261120-223006-24448ac (16^3: f_n16_p1_a0, f_n16_p1_a2,
  b_n16_p1; started 14:30, about 17 minutes) still running in the background when the
  session stopped; close it with `nrpic-run finish B-20261120-223006-24448ac`.
- Not submitted: J2 (`inputs/batch_j2.list`: b_n64_p1, f_n64_p1_a0, f_n64_p1_a2; add
  f_n32_p1_a3 from run B-20261120-223448-7f7c034 if wanted; 0.6 card-h) and J3
  (`inputs/batch_j3.list`: b_n128_p1 to a = 51; 0.65 card-h). Submit each with
  `nrpic-run submit --kind scouting --gate G2 --package tracks/B-emd-gw/flrw_conv
  --launcher batch --list <list> --exe /data/haiyangw/nrpic/.work/build_gpu_v03/src/athena
  --gpu-hours 0.65 --wall 00:55:00` once the owner has fewer than two card jobs.
- Then: `inputs/runs.json` (case -> '<run id>/<case>'), registered analysis with
  `scripts/analyze_f.py` and `scripts/analyze_b.py`, figures into `figs/`, numbers into
  `results/`, outcomes against PF1-PF6 and PB1-PB5 here, verdict in README.
Card time used by this package so far: none (J1 has not started).
