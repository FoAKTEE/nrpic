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

## Entry 4 (2026-11-21 12:30 PST, lead of batch 5): J2 and J3 submitted; predictions

Written before either job runs. J1 (B-20261120-222955-c8e16e3, Slurm 4746) and P1
(B-20261120-223006-24448ac) are completed and closed, not yet analysed; nothing of their
outputs was read for this entry except the end lines of three logs (exit 0, 4.7e6 and 5.4e6
zone-cycles/s at 32^3 with 1 per cell, 0.96e6 zone-cycles/s with 27 per cell).

Executable: J2 and J3 continue the series of J1, so they use the same release executable
`.work/build_gpu_v03/src/athena` (core-v0.3), not v0.6: a convergence series must come from
one code; the changes of v0.4-v0.6 without an option are listed in the changelogs and are not
tested against this series [JUDGEMENT].

- J2 = `inputs/batch_j2.list` unchanged (b_n64_p1, f_n64_p1_a0, f_n64_p1_a2), one batch job,
  estimate 0.57 card-h (entry 1, cost).
- J3 changed from entry 2: leg B at 128^3 now runs to a = 1001 (t = 61.277), not to a = 51,
  because card time is no longer the limit (decision 0025 item 4). Deck
  `inputs/mode_prod_rst.athinput` = `mode_prod.athinput` plus a restart output every 4 units
  of t; chained with `scripts/submit_chain.sh` (release core-v0.6 copy of the script), at
  most 6 segments. Estimate 23000 steps, 0.37-0.49 s per step: 2.4-3.1 card-h (entry 1).

Predictions: those of entry 1 (PF1-PF6 for J2's leg F at 64^3; PB1-PB5 for b_n64_p1 and
b_n128_p1), unchanged. Specific to the two jobs:
- J2: f_n64_p1_a0 scale-factor measures about 1/16 of f_n32_p1_a0's (PF1, step halved);
  f_n64_p1_a2 noise part of alpha/chi extrema half that of f_n32_p1_a2 at equal A (PF5).
- J3: |e_D| at 128^3 at most a quarter of that at 64^3 at every a where both have records
  (PB3, second order or better), down to the floor of about 1e-6 in f; the 128^3 run passes
  a = 1001 without the guard or the chain reporting a non-finite field.
- Step time: 0.37-0.49 s per step at 128^3 with 1 per cell (read from the first segment's
  log; if it is above 0.6 s the segment count may not suffice: resume with the same start
  command, `scripts/submit_chain.sh <rundir> <deck>`).
Refuted as in entry 1: any |f - reference| reaching 1e-2, or errors that do not fall from 32
to 64 to 128 cells without a floor whose cause a run has tested.

## Entry 5 (2026-11-21 12:58 PST, lead of batch 5): J2 ended; J3 running

J2 = B-20261121-202304-dc3020e ended 12:44 PST, all three cases exit 0 at t = 61.277
(a = 1001; 11963 steps for b_n64_p1, 11613 for each f_n64 case), 0.35 card-h by Slurm
accounting against the 0.57 estimated (entry 1). Closed by the sequencer. Not analysed.
J3 = B-20261121-202335-3e6a898 started 12:44 on a card (segment 1 of at most 6).

## Entry 6 (2026-11-21 13:16 PST, helper of batch 6): analysis of J1, P1, J2 before reading

Batch 6 takes no card (decision 0026 item 1); J3 (B-20261121-202335-3e6a898, chain, Slurm
4825, 128^3 to a = 1001) is still running and is not touched. This entry is written before
any output of J1, P1 or J2 is read beyond file names, record counts and the last time
(t = 61.20-61.26 in every case: all sixteen runs reached a = 999-1001).
`inputs/runs.json` maps the sixteen cases to their run directories (16^3 from P1, 32^3 from
J1, 64^3 from J2). The analysis is the registered run of `scripts/analyze_f.py` and
`scripts/analyze_b.py` on that map. The predictions under test are those of entry 1
(PF1-PF6, PB1-PB5) and entry 4 (J2), unchanged; the 128^3 leg of PB3 waits for J3.

## Entry 7 (2026-11-21 13:24 PST): outcomes of legs F and B at 16-64 cells; prediction of P2

### Outcomes (analysis v2: F = run B-20261121-211951-b735833, B = run B-20261121-211956-b30627b)

The first registered analyses (B-20261121-211524-e54164d, B-20261121-211626-e2a4df8) gave
the same numbers for every quantity they share; v2 adds the PF2 column check, the absolute
momentum constraint, the plateau and early parts of the f error, a decaying-mode fit that
separates a constant growth-rate error, and the period of the oscillation in the potential.
A development check of v2 wrote into scratch/B-emd-gw/tmp/flrw_conv/dev (not used for
numbers). All outcome numbers below are [VERIFIED] by the two v2 runs named above
(`flrw_f.json`, `flrw_b.json` and the printed log in their run directories).

Leg F (every run reached a = 998.5-1000.2):
- PF1 held. Largest scale-factor error of the lattices over the run, extrema of alpha:
  3.81e-7 (16 cells), 1.86e-7 (32), 1.23e-8 (64); volume 2.77e-7, 1.35e-7, 8.9e-9.
  32 -> 64: factor 15.1 (predicted about 16, fourth order in the step); 16 -> 32: 2.05
  (predicted 2-5).
- PF2 held: 8 and 27 per cell against 1 per cell, largest relative difference over the
  physical columns of both history files 2.1e-12 and 2.3e-12 (K_max, K_min).
- PF3 held: Hr_max of the lattices at most 1.8e-7 (16), 8.5e-8 (32), 1.9e-8 (64).
- PF4 held: with noise the largest scale-factor error of any measure is 5.3e-5 (16 cells,
  A2, extrema of alpha); volume and mean K at most 1.9e-6.
- PF5 held for the laws. Noise part of the alpha extrema at a = 3: 2.24e-5, 7.18e-6, 3.57e-6
  for 1, 8, 27 per cell (1 : 0.32 : 0.16; predicted 1 : 0.354 : 0.192); A1 -> A2 x10.0;
  16 -> 32 -> 64 cells 4.12e-5, 2.24e-5, 1.06e-5 (1 : 0.54 : 0.26; predicted proportional
  to h). It does not grow with a (2.2e-5 at a = 3, 1.8e-5 at a = 300 at 32 cells): the
  potential of the growing mode is constant. Noise part of the volume at a = 30:
  2.12e-7, 2.15e-8, 6.40e-9 (1 : 0.10 : 0.030; predicted 1 : 0.125 : 0.037), x100 from A1
  to A2, 1.75e-7, 2.12e-7, 2.41e-7 at 16, 32, 64 cells (mesh-independent within 40 percent),
  proportional to a while linear (5.4e-8 at a = 10, 5.7e-7 at a = 100).
- PF6 partly failed. Sizes of the box averages as predicted (volume noise part 2.6e-9 at
  a = 1.5 rising to 1.5e-6); the alpha extrema at A2, 1 per cell, 32 cells are 2.3e-5,
  above the predicted 1e-6 to 1e-5: the extrema of a field of 32768 cells sit about four
  standard deviations out (Phi_rms 5.79e-6 of the initial data) [JUDGEMENT]. The Hamiltonian
  constraint is not "damped" after the start: Hr_max falls from 2.9e-2 to 3e-3 by a = 1.5,
  then grows with the cell-scale contrast to 0.66 at a = 1000 (32 cells, A2), 1.3 (64, A2);
  box mean 0.05-0.06. The density contrast of the noise turns nonlinear at the cell scale
  (largest |E a^3/rho_0 - 1| 0.46 at a = 30, 6.2 at a = 300 for 32 cells, A2), and the
  compensated cubic cloud then deposits negative cell densities (signed minimum of
  E a^3/rho_0 - 1 below -1 first at a = 60 (64 cells, A2), 140 (32, A2), 346 (16, A2),
  622 (32, 8 per cell, A2); never at A1 or 27 per cell). These are properties of an
  unresolved cell-scale structure, not of the scale factor, whose errors stay below 6e-5.
- Momentum constraint: the relative norm Mr is rounding over rounding on a homogeneous
  slice (definition in athenak/src/particles/nrpic_io.cpp), so the absolute |M| is shown:
  at most 1.2e-11 for the lattices, 3.4e-3 to 5.1e-2 at the start with A2 noise, falling
  as the run expands.

Leg B (test B, 1e-7 plane wave, a = 1 to 999.3-999.7):
- PB1 held for the density estimators, failed for the potential estimator. Largest
  |f - f_ref| over 1.05 <= a: delta 8.4e-5, 6.5e-6, 4.9e-6 (16, 32, 64 cells); delta_* the
  same within 10 percent. Potential (a phi from chi): 3.1e-3 (16), 3.0e-4 (32), 1.7e-4
  (64), and above 1e-4 after a = 2 at every mesh: the potential carries an oscillation of
  period 2.342 in conformal time (2.340 at 64 cells), i.e. L/P = 0.577 = 1/sqrt(3), the
  coordinate speed of the slicing d_t alpha = -(1/3) alpha^2 K; its relative amplitude
  9.3e-5, 1.1e-5, 6.2e-6 (16, 32, 64) and 7.2e-6, 7.1e-6 (8, 27 per cell) falls with mesh
  and particle number. That it is a gauge wave of the lapse is [JUDGEMENT] from the speed.
  The derivative of an oscillation of rising frequency in ln a amplifies it, so f from the
  potential is the weakest estimator; it stays below 1e-2 everywhere.
- PB2 held at 32 and 64 cells, not at 16. The decaying-mode fit with a separate constant
  growth-rate error (ln(D_*/A a) = c0 + c1 ln a + eps a^-5/2 on a <= 30, rms residual
  1.5e-7 to 2.1e-6) gives eps = +3.3e-5 (16), +4.5e-6 (32), +1.4e-6, +1.3e-6 (8, 27 per
  cell), +2.5e-6 (64): f_* - 1 at a = 1 of -(5/2) eps, at most 8e-5 (16) and 1.1e-5 (32),
  decaying as a^-5/2. The two-term fit of entry 1 (no constant term) gave -1.4e-4 at 16:
  it absorbs the constant growth-rate error of 7.3e-5 at 16 cells into eps.
- PB3 held for the plateau, failed for the floor. Plateau of the f error (median over
  a >= 3): delta 6.71e-5, 4.91e-6, 3.03e-7; ratios 13.7 and 16.2, fourth order in the mesh.
  Largest amplitude error |D_delta/D_ref - 1|: 4.9e-4, 3.4e-5, 1.4e-6 (factors 14 and 25).
  No floor at 1e-6 in the plateau down to 3e-7. The early part (a <= 2) does not converge:
  6.2e-5, 3.6e-6, 4.8e-6 at 16, 32, 64; it is the decaying mode of eps 2.5e-6 at 64 cells
  (-(5/2) eps = -6e-6 at a = 1). Its cause is not named: candidates the initial-data solve
  (Hamiltonian residual up to 3.6e-12, entry 2) and the start of the lapse; [TO VERIFY] by a
  run that changes one of them.
- PB4 failed for the amplitude, held for f. f of 1, 8, 27 per cell at 32 cells agree to
  1.2e-6 in the plateau (4.91e-6, 1.20e-6, 1.53e-6 in size; constant-error terms +5.1e-6,
  -1.5e-6, -1.8e-6). The amplitude error at a = 1000 is +3.39e-5, -1.06e-5, -1.30e-5: one
  per cell differs from 8 and 27 by 4.5e-5, above the predicted 1e-5. 8 and 27 per cell
  agree to 2.4e-6 in amplitude and 3e-7 in f: from 8 per cell on the error at 32 cells is
  the mesh part; at one per cell a sampling part of opposite sign adds +6.5e-6 to f.
- PB5 held: f_delta at a = 1.1, 10, 1000 is 0.888051, 0.986328, 0.999851 at 32 cells
  against f_ref 0.888050, 0.986323, 0.999846; comparing f_delta with 1 would show -0.112
  at a = 1.1, while f_* - 1 stays below 6e-6 in size there.
- Constraints of leg B: Hr_max at most 3.4e-9 (32) and 1.3e-8 (64), the background part
  (leg F lattices); mean-density error at most 2.3e-9.

Verdict on criterion (a) at 16-64 cells: met. The scale-factor error is at most 3.8e-7
for lattices and 5.3e-5 with noise, converging at fourth order in the step and falling with
particle number and mesh as predicted; the growth rate agrees with the linear reference
(f_ref = a/(a + 3/k^2) for delta, 1 for delta_*) to 6.5e-6 at 32 cells and 4.9e-6 at 64,
with a plateau that converges at fourth order and an early decaying-mode part of a few 1e-6
that does not converge between 32 and 64 cells (floor, cause [TO VERIFY]). The 128^3 row
(J3) is pending.

### Prediction of P2 (optional row: Poisson-like start), before the run

Run: f_n32_p1_a3 (32 cells, 1 per cell, uniform displacements of +-h/2 per component,
seed 1; initial data B-20261120-223448-7f7c034: compensated delta_rms 0.469, Phi_rms
2.73e-4, <delta Phi> -9.02e-5), deck `inputs/flrw_prod.athinput`, processors (threaded
executable of core/build-openmp, 6 threads, as P1), list `inputs/cpu_p2.list`.
- Cost: 0.55-0.8 s per step at 6 threads (8 times P1's 16^3 at 4 threads), 5800 steps,
  55-80 minutes.
- Phi_rms is 47 times that of A2, <delta Phi> 2020 times. Extrema of alpha (first order in
  Phi): noise part about 47 x 2.2e-5 = 1.0e-3 at a <= 3, then roughly constant (as A2 at
  64 cells after it turned nonlinear) [JUDGEMENT]. Box averages (second order): 2020 x the
  A2 values if the law held, 5e-6 at a = 1.5, 4e-4 at a = 30, 2e-3 at a = 300; the start is
  nonlinear (delta_rms 0.47), so this is an order of magnitude only.
- Refuted (sub-percent at Poisson-like noise) if any scale-factor measure reaches 1e-2
  before a = 1000. Also recorded: whether the run reaches a = 1000 with finite fields.

## Entry 8 (2026-11-21 13:31 PST): P2 running; prediction of P3 (step and the early floor)

P2 = run B-20261121-212128-67b349a started 13:21 (0.45 s per step at 6 threads, inside the
predicted 0.55-0.8 s: faster). A development check of the B analysis with the partial
output of J3 (128^3, still running, records to a = 161; not a result) suggested that the
early part of the f_* error and the decaying-mode amplitude eps do not change from 64 to
128 cells (about 5e-6 and 2.5e-6 to 2.8e-6), so the early floor is not a mesh error. Until
a = 3 the step is set by the limit 0.002 of the expansion time at every mesh (Courant step
0.0105, 0.0053, 0.0026 at 32, 64, 128 cells), so the step is the same in all runs there.

P3 (`inputs/cpu_p3.list`, processors after P2, 6 threads): b_n32_p1 to t = 4 (a = 9) with
the step limit 0.002 (s_n32_p1_dt2, as J1) and 0.001 (s_n32_p1_dt1); analysis
`scripts/analyze_step.py` (fit ln(D_*/A a) = c0 + c1 ln a + eps a^-5/2 on a <= 8.5 for the
two P3 runs and J1's b_n32_p1). About 1090 and 2180 steps at 0.45 s: 25 minutes.
Prediction [JUDGEMENT]: the step is not the cause. The fourth-order integrator at a step of
0.002 has a truncation error far below 1e-6 over a unit of time, so eps changes by less
than 20 percent between the limits 0.002 and 0.001; and the processor run at 0.002 gives
eps within 20 percent of J1's card run (same initial data, same deck). Refuted if eps of the
0.001 run differs from that of the 0.002 run by more than 20 percent (then the step sets the
floor), or if the card and processor runs at 0.002 differ by more than 20 percent (then the
executables differ at this level and the comparison needs one executable).

## Entry 9 (2026-11-21 14:08 PST): outcome of P2 (Poisson-like start); provisional 128^3 row

P2 = run B-20261121-212128-67b349a (f_n32_p1_a3, threaded processor build, 6 threads):
exit 0 at t = 61.277, 13:21-14:04 (0.45 s per step; predicted 0.55-0.8 s). Analysis: run
B-20261121-220428-7367d5e (`analyze_f.py` on `inputs/runs.json` with the P2 case), figure
`fig_f_noise` looked at. [VERIFIED by these two runs]
- Sub-percent held at Poisson-like noise (the refutation was 1e-2): largest error over
  a = 1-999 of the alpha extrema 4.69e-3, chi extrema 4.26e-3, proper volume 2.93e-3, mean K
  2.13e-3.
- Extrema of alpha: noise part 1.16e-3 (a = 1.5) and 1.04e-3 (a = 3), as predicted
  (1.0e-3 = 47 x A2); not constant afterwards as predicted: 1.39e-3 (a = 30), 2.2e-3 (100),
  3.2e-3 (300), up to 4.7e-3 near a = 1000. Failed in that part.
- Box averages: noise part of the volume 5.0e-6 (a = 1.5), 3.7e-4 (30), 1.86e-3 (300)
  against the A^2 extrapolation of the A2 run, 5e-6, 4e-4, 2e-3: the second-order law holds
  to 10 percent although the start is nonlinear (delta_rms 0.47). Mean K: 6.4e-5 (a = 10),
  6.6e-4 (100), 1.3e-3 (300).
- The fields stay finite to the end. The relative Hamiltonian constraint is of order one from
  the start (largest Hr 1.2 at t = 0, 1.7 at the end), the compensated cloud deposits
  negative densities from the first record (signed minimum of E a^3/rho_0 - 1 is -38), and
  the absolute momentum constraint reaches 0.88: the cell-scale structure is not resolved,
  while the scale factor stays within 5e-3.
This is the row of brief section 10 about particle noise at small amplitude: with one
particle per cell displaced by up to half a cell, the box-averaged expansion deviates from
FLRW by 3e-3 at a = 1000, growing with a while the structure grows; with A2 (one percent of
a cell) by 1.5e-6.

Provisional 128^3 row (J3 still running): run B-20261121-220441-06021c4, `analyze_b.py` on
`inputs/runs_j3_partial.json` (J3 records to a = 189.5), figures `fig_b_conv`, `fig_b_error`
looked at. Not a result of the finished run; numbers on the common range 3 <= a <= 180.5:
- f plateau (median |f_* - 1|): 6.80e-5, 4.77e-6, 2.36e-7, 2.60e-8 at 16, 32, 64, 128 cells
  (ratios 14.3, 20.2, 9.1): still converging at 128 cells.
- Early part (a <= 2) 4.85e-6 at 128 (4.78e-6 at 64), eps = +2.77e-6 (64: +2.54e-6): the
  floor does not move with the mesh.
- The entry 4 prediction "|e_D| at 128^3 at most a quarter of 64^3's" fails provisionally:
  the amplitude error at a = 100 is -1.76e-6 at 128 against -7.2e-7 at 64. At 64 and 128
  cells the amplitude error is set in the first e-fold of expansion by the decaying-mode
  part (it is flat at -1.76e-6 from a = 2 on at 128 cells) and no longer by the mesh; at 64
  cells a mesh part of the other sign takes it through zero near a = 900.

## Entry 10 (2026-11-21 14:30 PST): outcome of P3 (step test); prediction of P4

P3 = run B-20261121-220450-e011c57 (s_n32_p1_dt2, s_n32_p1_dt1; both exit 0 at t = 4,
a = 8.8-9.0; 7.5 and 14.5 minutes). Analysis: run B-20261121-222718-311b50f
(`analyze_step.py`, `inputs/runs_step.json`), figure `fig_step` looked at. [VERIFIED by these
runs]
- Card against processors at the same step limit 0.002 (J1's b_n32_p1 against s_n32_p1_dt2):
  D_*/A a differs by at most 7.0e-8; eps 5.49e-6 against 5.54e-6 (fit on a <= 8.5). The two
  executables agree; that part of the prediction held.
- Step limit 0.002 against 0.001: eps 5.54e-6 against 3.87e-6 (30 percent), and D_*/A a
  differs by up to 1.47e-6 in the first e-fold: at 0.002 it rises to 4.3e-6 at a = 1.15 and
  dips to 3.4e-6 at a = 1.7, at 0.001 it stays near 3.9e-6; after a = 2 the two curves run
  parallel, 1.3e-6 apart. The prediction "the step is not the cause" is refuted by its own
  criterion (eps changed by more than 20 percent): the step limit sets a start error of
  about 1.5e-6 in the amplitude, the size of the floor seen at 64 and 128 cells (amplitude
  error flat at -1.76e-6 at 128 cells, entry 9).
- Design weakness of P3, recorded: at 32 cells and one per cell the plateau of the f error
  (5.6e-6, c1 of the fit) is as large as the early part, so the early maximum of |f_* - 1|
  (3.4e-6 and 4.6e-6) does not isolate the start error; the difference of the runs does,
  because mesh and particles are the same in both.

P4 (`inputs/cpu_p4.list`): the same run with the step limit 0.0005 (about 4400 steps, 33
minutes at 6 threads), analysed with the P3 pair by `analyze_step.py` (third panel: the
differences 0.001 - 0.002 and 0.0005 - 0.001 of D_*/A a).
Prediction [JUDGEMENT]: the start error converges with the step at second order (the
particle pusher is the implicit midpoint rule), so the largest |difference| 0.0005 - 0.001
is 1.47e-6/4 = 3.7e-7, within a factor 2 (ratio of the two differences between 2 and 8).
Refuted if the ratio is below 1.5 (the start error does not converge with the step) or above
12 (fourth order). If it converges, the step-free start error at 32 cells is estimated by
Richardson extrapolation from the three runs.

## Entry 11 (2026-11-21 14:58 PST): outcome of P4; cause of the amplitude floor

P4 = run B-20261121-222813-560158b (s_n32_p1_dt05, step limit 0.0005, exit 0 at t = 4,
14:28-14:57). Analysis with P3 and J1: run B-20261121-225745-773ffab (`analyze_step.py`),
figure `fig_step` looked at (third panel: differences of D_*/A a between step limits).
[VERIFIED by these runs]
- Largest difference of D_*/A a: 0.001 - 0.002 = 1.47e-6, 0.0005 - 0.001 = 3.53e-7; ratio
  4.2. The prediction (second order, ratio between 2 and 8) held. Most of each difference
  builds up in the first e-fold (1.17e-6 and 0.27e-6 by a = 2), the rest slowly to a = 9.
- Richardson extrapolation at second order: the step limit 0.002 of the B runs puts
  -1.9e-6 into D_*/A a at a = 9 (-1.5e-6 by a = 2) relative to the step-free value at 32
  cells and one per cell. This matches in sign and size the amplitude floor seen at 128
  cells (-1.76e-6, flat from a = 2, entry 9) and at 64 cells (-7.2e-7 at a = 100 with a mesh
  part of the other sign). In the first e-fold every mesh runs at the same step (the limit
  0.002 of the expansion time, dt = 0.002 (1 + t/2), below the Courant step until a = 1.7
  at 128 cells, 7.0 at 64 and 28 at 32 cells), so the floor of the amplitude error at 64 and 128 cells is the
  step error of the start, second order in the step limit. That the start error at 128
  cells is the same as at 32 is [JUDGEMENT] from sign and size; it was not run at 128.
- The fitted decaying-mode amplitude moves with the step (eps 5.54e-6, 3.87e-6, 3.42e-6;
  extrapolated about 3.3e-6), so part of what the three-term fit calls a decaying mode at
  32 cells is the step and part is not; the rest is not identified [TO VERIFY]. The fit is a
  weak separator here (the start error is not of the form a^-5/2).
- The f plateau is not affected by the step (c1 = 5.58e-6, 5.75e-6, 5.78e-6). The early
  swing of f_* at the limit 0.002 (a dip to 1e-7 at a = 1.1 and 1.7 between values of
  3.4e-6) disappears at 0.001 and 0.0005; at 32 cells and one per cell the early f error
  then merges into the plateau (5.6e-6), so the early f floor of 5e-6 at 64 and 128 cells
  is not separated from the step by these runs.
- Consequence [JUDGEMENT]: with the production step limit 0.01 (instead of the 0.002 used
  for leg B) the start error of the amplitude would be about (0.01/0.002)^2 = 25 times
  larger, about 5e-5: still sub-percent, but larger than the mesh error at 32 cells and
  above. Test B at the production limit was not run here.

Verdict on criterion (a), final for this package (128^3 pending): met. Scale factor
sub-percent at every mesh and particle number with and without noise (largest 5.3e-5 at
noise of 1 percent of a cell, 4.7e-3 at Poisson-like noise), converging in step, mesh and
particle number as predicted. Growth rate sub-percent everywhere (largest |f - f_ref|
8.4e-5 at 16 cells, 6.5e-6 at 32, 4.9e-6 at 64 for the density estimators), the plateau
converging at fourth order in the mesh to 2.6e-8 at 128 cells (provisional), falling with
particle number at 32 cells until the mesh part remains; the stated floor is the start
error of the step (about 2e-6 in the amplitude at the step limit 0.002, second order in
the step), named after P3 and P4, runs in which it could have failed.

## Entry 12 (2026-11-22 17:57 PST, lead of batch 10a): the finished 128^3 member; final verdict

J3 = run B-20261121-202335-3e6a898 ended 2026-11-21 22:21 PST: three segments (Slurm 4825,
4849, 4861; 50:04 + 50:03 + 19:44 = 2.00 card-h by Slurm accounting, estimate 2.4-3.1), one
outside kill resubmitted by the chain, 23261 cycles, t = 61.277 (a = 1000.0), exit 0, closed by
the sequencer. `inputs/runs.json` gains `b_n128_p1`; analysis run B-20261123-015452-18d2956
(`analyze_b.py` on `inputs/runs.json`, 16 s); figures `fig_b_conv`, `fig_b_error`,
`fig_b_constraints` looked at; copies in `figs/` and `results/flrw_b.json` (the 16-64 rows are
the same digits as run B-20261121-211956-b30627b). [VERIFIED by these runs]

Outcomes at 128 cells (1 per cell, a = 1 to 1000; plateau over 3 <= a <= 951):
- Entry 4, "128^3 passes a = 1001 without the guard or the chain reporting a non-finite field":
  HOLDS.
- Entry 4 / PB3, "|e_D| at 128^3 at most a quarter of 64^3's": FAILS (final; the provisional
  verdict of entry 9 stands). Largest amplitude error 1.83e-6 at 128 against 1.37e-6 at 64;
  flat at -1.7e-6 from a = 2 to the end. The floor's cause was tested at 32 cells (P3, P4: the
  step error of the start, second order in the step limit, -1.9e-6 by Richardson); that the
  same holds at 128 cells is [JUDGEMENT] from sign and size, not run at 128.
- PB3 plateau: median |f_delta - f_ref| 2.78e-8 (f_* 2.52e-8) against 3.03e-7 at 64: factor
  10.9 (32 -> 64: 16.2); between second and fourth order, no floor down to 3e-8. HOLDS.
- PB1: largest |f_delta - f_ref| 5.01e-6, all of it in the first e-fold (early part 4.85e-6);
  after a = 2 below 1e-4. HOLDS for the density estimators; the potential estimator again
  above 1e-4 after a = 2 (largest 1.72e-4, the oscillation of period 2.343) as at 32 and 64:
  FAILS as before, sub-percent.
- PB2: eps = +2.81e-6 (64: +2.54e-6). HOLDS.
- PB5: f_delta at a = 1.1, 10, 1000 = 0.888051, 0.986323, 0.999846 against f_ref 0.888050,
  0.986323, 0.999846. HOLDS.
- Constraints: largest Hr 6.2e-8 at 128 (3.2e-9, 1.3e-8 at 32, 64): it grows with the mesh by
  3.3, 4.0, 4.8 per doubling, roughly as N^2, from the first records on; a growth like
  round-off in second differences would show [TO VERIFY; not tested]. Mean-density error at
  most 4.0e-9.
Figure defect noted: in `fig_b_error` the legend of the potential panel covers the 128-cell
curve's top.

Verdict on G2 criterion (a), final: MET at 16-128 cells. Scale factor sub-percent at every
mesh and particle number (largest 3.8e-7 for lattices, 5.3e-5 with one-percent noise, 4.7e-3
with Poisson-like noise; leg F has no 128 member). Growth rate sub-percent at every mesh,
largest |f - f_ref| 5.0e-6 at 128 cells, its plateau converging between second and fourth
order to 2.8e-8; in particle number at 32 cells as in entry 7. The stated floor is the start
error of the step (about 2e-6 in the amplitude at the step limit 0.002), whose cause a run
could have refuted (P3, P4).
