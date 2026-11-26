# JOURNAL of the work package periodic_threshold (Track A, wave 2)

Helper of A-emd-pbh. Predictions are written before each test; outcomes are appended
below them, including failed predictions. Labels: [VERIFIED] read at a locator or
computed in a registered run, [BACKGROUND], [JUDGEMENT], [TO VERIFY]. Times UTC.

---

## 2026-11-15, P0: design numbers of the set-up (written before the run)

Script `scripts/design_numbers.py` (pure arithmetic, no simulation). Code units of
`cosmo/README.md`: G = c = 1, H_i = 1 at a_i = 1, matter era, conformal time tau with
a = (1 + tau/2)^2; peak profile and eigenvalues of arXiv:2609.14218 (MDPBH.tex:839,
907-908; horizon entry k^2/(a^2 H^2) = 6, MDPBH.tex:709-719).

Predictions (consistency checks of the formulas, each would expose an error in them):
- with the paper's start k/(a_i H_i) = 1/5: horizon entry at a_H/a_i = 150 and
  t_H/t_i = 750 sqrt(6) = 1837.1 (the paper's t_H = 100 sqrt(6)/k with t_i = 2/(3 H_i),
  H_i = 5k, MDPBH.tex:549, 718);
- the amplitude whose top-hat collapse time of the compaction shell is 250 t_H is
  mu = 0.048 (scope run A-emd-pbh-20261115-112625-e854f12, SCOPE.md section 2, H1);
- the box of side 2L = 20/k is 100 initial Hubble radii and 8.16 Hubble radii at horizon
  entry; it shrinks in Hubble units as t^(-1/3).
Refuted (formula error) if any of the three differs beyond rounding.

## 2026-11-15, T1: what the existing tool builds for the peak (written before the run)

Question: can `cosmo/ic/make_field.py` (linear Newtonian-gauge dictionary from a
growing-mode density delta_N, Zel'dovich lattice, nonlinear constraint solve on the torus
for the particles) build the single-peak data, and how large is its error?
Driver `scripts/make_peak_ic.py`: zeta = 2 ln Psi of MDPBH.tex:839 on the mesh, delta_N =
-(2/5) lap(zeta)/(a_i H_i)^2 (linear growing mode, psi_N = -(3/5) zeta in the matter era
[BACKGROUND]), then `make_field.build` unchanged; peak at the box centre.
Cases: e = 0.2, p = 0; mu = 0.03 and 0.5; start eps_i = k/(a_i H_i) = 0.2 (the paper's),
1, sqrt(6) (horizon entry); 64^3 cells, one particle per cell, box 20/k.

Diagnostic: the change the constraint solve makes to the conformal factor of the
dictionary, c = max|psi - psi_dict| / max|psi_dict - 1|. The linear dictionary is
consistent with the constraints at first order, so c measures the second-order
mismatch, which the solve absorbs into the spatial curvature.

Prediction [JUDGEMENT]: the mismatch in K^2 and 16 pi rho is O(H^2 psi_N^2); absorbed by
the curvature, it changes psi by O((a H/k)^2 psi_N^2), so c ~ (aH/k)^2 |psi_N| ~
0.6 mu / eps_i^2 up to a coefficient of order one: c ~ 0.5 for (0.03, 0.2), ~ 10 for
(0.5, 0.2), ~ 0.02 and 0.3 at eps_i = 1, ~ 0.003 and 0.05 at horizon entry. Refuted if c
does not scale with mu at fixed eps_i (then the mismatch is first order: a gauge or
normalisation error of the driver or the tool) or if c is below 1e-3 at (0.5, 0.2) (the
dictionary would then be consistent at second order and my estimate wrong).
Also recorded: the largest lattice displacement in cells, mass ratios, the residuals of
the solve, and, from the gradient-expansion data of MDPBH.tex:515-543 evaluated on the
same mesh, the size of the non-conformally-flat part (4/5) p_ij/(aH)^2 that the file
format NRCOSMO1 cannot carry.

### T1, smoke test of the driver before the registered sweep (unregistered, 32^3)

Two debugging runs of `make_peak_ic.py` at n = 32, eps_i = 1, e = 0.2 (output in
`scratch/A-emd-pbh/tmp/smoke_ic*`, not registered, no number from them enters a note):
c = 0.362 at mu = 0.03 and c = 0.363 at mu = 0.003. The solve lowers psi at the peak by a
third of the dictionary perturbation (psi - psi_dict = -3.0e-3 against psi_dict - 1 =
8.4e-3 at mu = 0.03), localised on the peak, not a uniform offset.
**The T1 prediction is refuted by its own criterion**: c does not scale with mu, so the
mismatch is first order, not the second-order dictionary error I predicted.
Hypothesis (H-smooth) [JUDGEMENT]: on the Newtonian-gauge slice the Hamiltonian
constraint at super-horizon scales rests on a cancellation: K^2/12 - 2 pi E =
(3/4)[(1 - 2 psi_N) - (1 + delta_N - 2 psi_N)] = -(3/4) delta_N, where -2 psi_N is
(3/2)(aH/k)^2 times larger than delta_N. K is set on the mesh exactly, E is deposited
from the lattice (cloud, binomial filter, compensation), so E carries -2 psi_N smoothed;
the residual (3/2)(1 - S) psi_N is a first-order error, larger by (aH/k)^2 than the
smoothing error of delta_N itself, and the solve absorbs it into psi.

## 2026-11-15, T1 (revised), registered sweep: written before the run

Cases (all e = 0.2, p = 0, one particle per cell, cloud-in-cell, nfilter = 2 with
compensation as in `problems/cosmo/east_bh.athinput`):
(a) mu = 0.03, 0.5 at eps_i = 0.2, 1, sqrt(6), n = 64;
(b) mu = 0.03, eps_i = 1 at n = 32, 128 (resolution);
(c) mu = 0.03, eps_i = 1, n = 64 without the filter (nfilter = 0).
Predictions of H-smooth: c independent of mu to 1e-2 in (a); c falls with the cell size
as h^2 (factor 3-4 per halving) in (b); c grows roughly as (aH/k)^2 = 1/eps_i^2 at fixed
n in (a) (more than tenfold from eps_i = 1 to 0.2; several times smaller at sqrt(6)),
up to the change of kh with eps_i (the box is 20/k, so kh = 20/n at every eps_i and the
smoothing factor S is the same: then c scales exactly as 1/eps_i^2); (c) smaller c than
with the filter. Refuted if c does not fall with h (then the error is not the smoothing
of the deposit) or does not grow towards small eps_i (then it is not the super-horizon
cancellation).

## 2026-11-15, T2 and T3 (processor tests of the mesh and of the horizon finder): before the runs

Observed in an unregistered smoke run (FLRW, `inputs/peak_smr.athinput`, 8 cycles): the
serial processor executable reaches 7.8e3 zone-cycles per second on 8^3 blocks with four
ghost cells, so processor tests are kept to a few cycles. In the same smoke run the
static mesh (176 blocks, levels 0-2) kept chi_min = chi_max to 13 digits.

**T2a, homogeneous universe on the static mesh** (box [-10, 10]^3, root 32^3, level 1 in
|x| < 5, level 2 in |x| < 2.5, lattice of one particle per root cell, 8 cycles to t = 0.3,
finder on every 4 cycles centred at the origin). Cases: uniform mesh; static mesh with
the adaptive cloud level (deposit_ppc = 2, so every cloud sits on the root level); static
mesh with clouds at the finest local level (deposit_adaptive = false).
Prediction: uniform and adaptive-cloud cases stay homogeneous, H_max = H_mean (no
structure at level boundaries) and chi_max/chi_min - 1 below 1e-12; with clouds at the
finest level the lattice (one particle per 4^3 level-2 cells) deposits a strongly
non-uniform E there: relative Hamiltonian constraint of order 1e-1 to 1 on refined blocks
from the first step. Refuted if the adaptive case shows level-boundary structure above
1e-10 relative (then the prolongation of clouds or of the metric is not exact for a
uniform state) or if the finest-level deposit stays uniform.
**T3d, finder in the homogeneous universe** (same runs): no horizon is reported (outgoing
expansion 2/(aR) + 2H > 0 on every sphere); the run does not stop. Refuted by a reported
horizon or a crash of the finder.

**T2b, the peak data on the static mesh at t = 0** (mu = 0.5 and 0.03, e = 0.2, eps_i = 1,
32^3 root, data built by make_peak_ic.py at 32^3; one cycle). Prediction (from cosmo E1,
`cosmo/TESTLOG.md` 744-752: relative H 4e-5 on refined blocks against 2e-11 uniform, at
amplitude 1e-4): on the uniform mesh the Hamiltonian constraint of the code is the
finite-difference truncation of the spectrally solved data, |H|max well below
16 pi |E - Ebar|max (ratio < 0.1); on the refined blocks, where the root-level data are
interpolated (cubic) and the clouds sit on the root level, the ratio is of order 0.1 to 1
and independent of mu (linear error). Refuted if the refined-block error is below the
uniform-mesh error, or if it does not scale linearly with mu (ratio changing by more
than a factor 2 between mu = 0.03 and 0.5).

**T2c, adaptive refinement (Lohner) at the start** (mu = 0.5, e = 0.2, eps_i = 1, 32^3 root,
`inputs/peak_amr.athinput` with 8^3 blocks, 8 cycles = two refinement checks).
Prediction [JUDGEMENT]: the Lohner indicator of alpha chi^(7/4)... is a ratio of second to
first differences; at the start the peak spans about 5 root cells per Gaussian width, so
the indicator stays near or below the threshold 0.2 and few or no blocks refine in the
first 8 cycles. Refuted (not a failure of the code) if the central blocks refine at the
first check: then the refined blocks start from prolonged evolved data rather than from
the file, which is what the design needs to know.

**T3a-c, finder in a periodic mesh with a known horizon** (vacuum Schwarzschild puncture of
unit mass, `inputs/punc_box16.athinput`: box [-16, 16]^3, root dx = M, dx = M/8 inside
|x| < 1.5, one cycle, finder at cycle 0/1; reference: docs/TESTLOG.md, the corrected
finder on the exact initial slice at dx = M/8 gives 0.991521 on GPU and CPU).
(a) outflow boundaries, finder at the origin; (b) periodic boundaries, finder at the
origin; (c) periodic boundaries, finder centred one period away at (32, 0, 0).
Predictions: (a) 0.9915 to four digits if the finest level covers the finder's stencils
as in the calibration mesh; (b) identical to (a) to all printed digits (the boundary
does not enter at t = 0); (c) unknown: if the finder maps surface points into the box
it equals (b); if it does not, every surface point lies outside the mesh and it reports
no horizon or fails. Outcome (c) decides whether a peak may sit near a box face.

## 2026-11-15, P0 outcome (run A-emd-pbh-20261115-153520-0576e01)

All three checks hold: a_H/a_i = 150.000, t_H/t_i = 1837.117 (750 sqrt 6 = 1837.117);
top-hat amplitude for 250 t_H: mu = 0.0481 (1000 t_H: 0.0191); box 100, 8.165 and 1.296
Hubble radii at the start, at entry and at 250 t_H. Figure `fig_design_numbers.png`
looked at: box and r_m against t/t_H, collapse epochs against mu.

## 2026-11-15, S1 and S2 (first scouting runs on cards): written before submission

Common set-up: `inputs/peak_amr.athinput`; e = 0.2, p = 0, eps_i = k/(a_i H_i) = 1, box
[-10, 10]^3 (20/k, 20 initial Hubble radii), root 64^3 (k dx = 0.3125, r_m = 7.8 cells),
adaptive refinement by the Lohner indicator, up to four levels (k dx = 0.0195); data of
the T1 sweep at n = 64 (make_field.py, one particle per root cell, 262,144 particles,
solve change c = 0.078 at mu = 0.03); conformal-time lapse plus the driver towards
constant mean curvature, zero shift (cosmo E1 gauge); particles removed where alpha <
0.3; finder at the origin, initial radius 2.0, every 32 cycles. Release card executable
`.work/build_gpu_v03/src/athena`. Slurm limit 40 min each (at most 1.33 card-hours).
Epochs (P0 formulas, eps_i = 1: tau = 2 (sqrt(a) - 1), a = 6 (t/t_H)^(2/3)).

**S1, mu = 0.5 ("clearly above")**: above the particle threshold of arXiv:2609.14218 at
e = 0.2 (horizons for mu >= 0.05, MDPBH.tex:1101-1103) by ten and above the
Zel'dovich-hoop line mu > 0.452 (SCOPE.md T1) by a tenth. Zel'dovich axes collapse at
t/t_H = 1.95, 3.95, 15.6 (tau = 4.1, 5.8, 10.3); top-hat collapse of the compaction shell
7.5 t_H (tau = 7.6). tlim = 14 (30 t_H).
Predictions [JUDGEMENT]: (a) the run reaches the first pancake (tau ~ 4) with the
relative Hamiltonian constraint below 1e-2; (b) the Lohner indicator refines the centre
before tau ~ 4; (c) the central lapse falls relative to the largest lapse from tau ~ 5;
(d) either the finder reports a horizon between tau ~ 6 and 10, or the run ends before
it with a non-positive metric determinant at the centre, the failure of cosmo E1
(`cosmo/TESTLOG.md` 744-763). I rate (d, failure first) as the more likely outcome.
Refuted as a usable configuration for the line by a crash before tau = 4, or by a
horizon whose area mass exceeds the mass inside r_m at the start (0.5 r_m^3 = 7.35 in
these units, P0).

**S2, mu = 0.03 ("clearly below")**: below the particle threshold of arXiv:2609.14218
(none for mu <= 0.045) and below the finite-duration cutoff for 250 t_H (0.048, P0);
every criterion predicts no horizon by 250 t_H. First Zel'dovich axis collapses at
133 t_H (tau = 23); top-hat 508 t_H. tlim = 28.9 (250 t_H).
Predictions: no horizon to tau = 28.9; the relative Hamiltonian constraint stays below
1e-2 until the pancake forms (tau ~ 23), then grows in the sheet; the lapse at the
centre stays within ten per cent of the largest lapse until tau ~ 20. Refuted by a
horizon (it would be an artefact) or by a failure before tau = 20 (then the cause is
the gauge, the mesh or the noise, not shell crossing).
Cost prediction: each below 0.3 card-hours (8.1e-8 card-seconds per cell and step,
`tracks/core` run core-20261115-040406-1311b8e, as quoted in SCOPE.md 10.7).

## 2026-11-15, T2/T3 outcome (run A-emd-pbh-20261115-154250-527a6d1) and a driver bug

- **Bug in my driver, found by T2b.** On the uniform mesh at t = 0 the code's Hamiltonian
  constraint was 2.3 to 2.6 times 16 pi max|E - Ebar| (relative H_r max 0.64 at mu = 0.5,
  0.05 at mu = 0.03), where a solved data set should give a small fraction. Cause, read
  in the code: `make_peak_ic.py` wrapped the particle positions into [-L/2, L/2) instead
  of shifting them by -L/2, so the particles' peak sat at the box corner and the metric's
  at the origin. Fixed (x - L/2). The T2b and T2c numbers of this run are therefore void
  and are repeated; the run that was building the S1 data with the bug
  (A-emd-pbh-20261115-154356-527a6d1) was stopped and marked superseded. T1 is not
  affected (its diagnostic is computed before the positions are written).
- T2a confirmed: uniform mesh and static mesh with the adaptive cloud level stay
  homogeneous (chi_max/chi_min - 1 = 2e-15 at t = 0.3; H_max = H_mean, a uniform 4e-6 from
  the time integration, no structure at level boundaries); with clouds on the finest
  level the relative Hamiltonian constraint is 1.02 at t = 0 and the conformal factor
  spreads by 12 per cent by t = 0.3. As predicted.
- T3d confirmed: no horizon reported in the homogeneous universe (three runs), no crash.
- T3a/b confirmed: the finder gives 0.9915211031 on the puncture slice with outflow and with
  periodic boundaries, the calibration value 0.991521 of docs/TESTLOG.md to all its digits.
- T3c: with the finder centred one period away, (32, 0, 0), it reports no horizon: **the
  finder does not map surface points into the periodic box**. A horizon that crosses a
  box face is not found; the peak must sit at the box centre and the finder centre
  inside the box.
- T2c (adaptive mesh): the run died with a segmentation fault (exit -11) after cycle 4,
  the first refinement check, with 64 blocks and no refinement before it. To be repeated
  with the corrected data to see whether the crash belongs to the data or to adaptive
  refinement with periodic particles and the cosmological generator.

## 2026-11-15, T2b/T2c repeated with the corrected data (run A-emd-pbh-20261115-154740-69e8f8b)

- **T2b confirmed.** At t = 0 the code's Hamiltonian constraint over 16 pi max|E - Ebar|
  is 1.8e-4 (mu = 0.5) and 3.5e-5 (mu = 0.03) on the uniform 32^3 mesh: the solved data
  are consistent with the code's deposit and finite differences. On the static mesh
  (levels 1-2 interpolated from the root file, clouds on the root level) it is 0.085 and
  0.077: an eight per cent violation relative to the perturbation, the same at both
  amplitudes (linear, as predicted; the low end of the predicted 0.1-1). Outside the
  refined region it stays at 1.3e-3 to 1.4e-3.
- **T2c: the crash is not the data.** Adaptive refinement (Lohner) dies with a
  segmentation fault after cycle 4, the first refinement check, both for the peak and
  for the homogeneous universe (where no block can be flagged for refinement). Isolation
  run A-emd-pbh-20261115-155737-8422a4a (gdb backtrace; trivial criterion), outcome below.
  Consequence for the scouting runs: the four-level static mesh
  `inputs/peak_smr4.athinput` replaces the adaptive one.

## 2026-11-15, the data of S1: make_field does not solve mu = 0.5

Run A-emd-pbh-20261115-154735-69e8f8b (S1/S2 data, corrected driver): mu = 0.03 as in T1
(c = 0.078, residual 1.6e-12). For mu = 0.5 every inner solve stops at its 60-iteration
limit with max|H| between 0.04 and 0.12 (the residual does not fall), and the outer
iteration ends with a change of psi of 2.3e-4: **the tool's solve stagnates at this
amplitude** (Newtonian-gauge potential psi_N = -0.3 at the peak, lapse 0.64 in the
dictionary). The mu = 0.5 files exist but are not solved data.
S2 (mu = 0.03) was submitted with the static mesh: A-emd-pbh-20261115-155754-8422a4a
(Slurm job 4448), predictions as written above.

### T1b, largest amplitude the tool solves (written right after launching
run T1b and before reading any of its output)

mu = 0.2 and 0.3 at e = 0.2, eps_i = 1, 64^3. Prediction [JUDGEMENT]: the stagnation
sets in where the constant-coefficient Helmholtz preconditioner of `cosmo_id.solve`
(sigma = mean of (5/12) K^2 psi^4 + 2 pi psi^4 E) misrepresents the local coefficient by
order one, i.e. where psi^4 varies by tens of per cent: mu = 0.2 converges (residual
< 1e-10), mu = 0.3 is marginal. If mu = 0.3 converges, S1 runs at mu = 0.3 (above the
particle threshold of arXiv:2609.14218 by six, below the hoop line 0.452); otherwise at
the largest converged amplitude, and the "clearly above both" run waits for core's
generator.

## 2026-11-15, T2c isolation outcome (run A-emd-pbh-20261115-155737-8422a4a)

Cause established. The backtrace (homogeneous universe, Lohner criterion) ends in a call
through a null pointer (rip = 0x0) from `MeshRefinement::CheckForRefinement`,
`athenak/src/mesh/mesh_refinement.cpp:243`, the `RefCritMethod::user` branch, which calls
`pmy_mesh->pgen->user_ref_func(pmbp)`. `nrpic_cf` sets that pointer to a function that
calls the Z4c refinement criteria (`nrpic_cf.cpp:175-177, 392`); `nrpic_cosmo` never sets
it (`pgen.hpp:54` initialises it to nullptr). The trivial criterion crashes the same way
(exit 139), so the crash is independent of the criterion and of the data: adaptive
refinement with `<amr_criterion0> method = user` cannot run with the cosmological
generator today. The fix is one line in `nrpic_cosmo.cpp` (core); until then only static
refinement is available in the periodic box. (Not tried: an AthenaK built-in criterion
other than "user"; they monitor hydro variables, which this run does not have.)

## 2026-11-15, T1b outcome (run A-emd-pbh-20261115-155802-9a6596f) and S1 revised before submission

mu = 0.2: solved (residual 3.7e-12, c = 0.031); mu = 0.3: solved (residual 7.2e-12, 33
inner iterations, c = 0.137, outer change of psi 7.2e-5 at the end). Prediction partly
refuted: mu = 0.3 is not marginal, it converges; the stagnation lies between 0.3 and 0.5.
(c is not monotone in mu: 0.078, 0.031, 0.137, 0.103 for mu = 0.03, 0.2, 0.3, 0.5 at
64^3 and eps_i = 1, so second-order terms enter at these amplitudes; not pursued.)

**S1 revised: mu = 0.3** (solved data of this run, `S_mu0.3`), everything else as written
for S1 above. It is above the particle threshold of arXiv:2609.14218 at e = 0.2 by a
factor of six and below the Zel'dovich-hoop line (0.452): the two references predict
opposite outcomes, so "clearly above" holds only for the particle reference. Epochs (P0):
Zel'dovich axes at 4.2, 8.5, 33.6 t_H (tau = 5.0, 7.3, 13.8); top-hat collapse of the
compaction shell 16.1 t_H (tau = 10.4). tlim = 16 (49.6 t_H); finder from tau = 6, every
64 cycles. Predictions [JUDGEMENT]: (a) the run passes the first pancake (tau ~ 5) with
Hr_max below 1e-1 outside the refined-block boundary error of T2b; (b) the central lapse
falls relative to a(tau) from tau ~ 7; (c) if arXiv:2609.14218 and hypothesis H1 hold,
a horizon near 0.8-1.0 of the top-hat time, 13-16 t_H (tau = 9.4-10.4); if the hoop line
holds, no horizon and a halted pancake; (d) more likely than either, the run ends before
tau ~ 10 with a non-positive metric determinant in the finest cells (the E1 failure).
Outcome (d) or a crash before tau = 5 = UNDECIDED in the sense of SCOPE.md section 3.

Note on T2b: the mu = 0.5 data at 32^3 (run A-emd-pbh-20261115-154740-69e8f8b, `ic_peak0.5`)
were nearly solved (residual 4e-10 at the 60-iteration limit), unlike 64^3 (0.06): the
stagnation of the solve worsens with resolution. T1 sweep: mu = 0.5 at eps_i = sqrt 6
diverges (NaN) like eps_i = 0.2.

## 2026-11-15, T4: feasibility of the constant-mean-curvature route with the existing
solver (written before the run)

Purpose: evidence for request 1 (DESIGN.md 2.2), not production data. Script
`scripts/t4_cmc_route.py`: the gradient-expansion fields of MDPBH.tex:515-543 at
eps_i = 0.2 (the paper's start), e = 0.2, 64^3, box 20/k: psi_GE = Psi (1 - q/(6 (aH)^2)),
Ahat = psi^6 (2/5) p_ij H/(aH)^2, E from the conformally flat Hamiltonian constraint of
psi_GE with K = -3H, momenta u_i = Shat_i/Ehat from the momentum constraint; one
particle per cell at the cell centre (the paper's lattice, one cloud per cell), masses
Ehat h^3/W; then `cosmo_id.solve` (unchanged) with K = -3H, started from psi = 1.
Measure: c_CMC = max|psi - psi_GE| / max|psi_GE - 1|, the residual, the iterations.
Predictions [JUDGEMENT]: the solve converges for mu = 0.03 and 0.5 (the linearized
operator has sigma = (5/12) K^2 + 2 pi E > 0 and nothing large cancels on this slice);
without the filter c_CMC is at the level of the spectral-versus-deposit difference,
below 1e-6, since the cell-centred cloud deposits exactly; with two binomial passes and
compensation c_CMC is of the order (kh)^4 smoothing of delta, 1e-3 to 1e-2. Refuted if
the solve stagnates or diverges at mu = 0.5 (then the tool's iteration, not the slice,
limits the amplitude) or if c_CMC exceeds 0.05 with the filter.

### T4 outcome (run A-emd-pbh-20261115-160718-e04c0cc)

- mu = 0.03, eps_i = 0.2: **confirmed**. The solve converges in 9 (10) iterations to
  residual 6e-12 (3e-12); c_CMC = 7.5e-10 without the filter (the cell-centred cloud
  deposits exactly) and 3.4e-5 with two binomial passes and compensation, against
  c = 0.38 and no convergence for make_field at the same start (T1). The solved Ahat
  differs from the gradient-expansion Ahat by 1.3 per cent of its maximum (the solve's
  Ahat is longitudinal; the transverse-traceless part and the removed mean of S remain).
- mu = 0.5: **refuted** by my own criterion: the solve diverges (NaN) with and without
  the filter, started from psi = 1. Reading [JUDGEMENT]: the iteration of
  `cosmo_id.solve` preconditions with the constant mean of sigma = (5/12) K^2 psi^4 +
  2 pi psi^4 E; at mu = 0.5 psi^4 is 2.7 at the peak (Psi = 1.28), the local sigma
  exceeds the mean by more than the mean itself, and the low-wavenumber error grows. So
  the amplitude limit is the solver's iteration, not the slice.
Written before T4b: started from psi = psi_GE instead of 1, mu = 0.5 converges if the
divergence came from the start, and diverges again if it is the iteration (my reading
predicts divergence); mu = 0.3 from psi = 1: converges (psi^4 = 1.8 at the peak).

### T4b outcome (run A-emd-pbh-20261115-161134-f3949f8)

Both predictions confirmed: mu = 0.5 diverges again when started from psi_GE itself
(NaN after 200 iterations), so the divergence is the iteration, not the start; mu = 0.3
at eps_i = 0.2 converges from psi = 1 in 78 iterations to residual 7e-12 with c_CMC =
2.6e-8. On the constant-mean-curvature slice the existing solve reproduces the
gradient-expansion data at the paper's start for mu <= 0.3; above, a solver with a
variable-coefficient (Newton) step is needed.

## 2026-11-15, T1 outcome (run A-emd-pbh-20261115-153527-0576e01, `figures/fig_t1_solve_change.png` looked at)

c at e = 0.2, one particle per cell (n = 64 unless stated):

| mu | eps_i | n, filter | c | outer change at the end | residual |
|---|---|---|---|---|---|
| 0.03 | 0.2 | 64, 2 + comp | 0.377 | 1.3e-4 (not converged) | 9e-12 |
| 0.03 | 1 | 64, 2 + comp | 0.078 | 1.3e-6 | 1.6e-12 |
| 0.03 | sqrt 6 | 64, 2 + comp | 0.025 | 2.3e-8 | 1.2e-12 |
| 0.03 | 1 | 32, 2 + comp | 0.362 | 4.3e-6 | 3.8e-12 |
| 0.03 | 1 | 128, 2 + comp | 0.0040 | 1.1e-7 | 7.4e-12 |
| 0.03 | 1 | 64, none | 0.074 | 1.3e-6 | 2.4e-12 |
| 0.5 | 0.2 | 64 | NaN | diverged | |
| 0.5 | 1 | 64 | 0.103 | 2.3e-4 | 0.057 (stagnated) |
| 0.5 | sqrt 6 | 64 | NaN | diverged | |

Against the revised predictions (H-smooth):
- resolution: c falls by 4.6 from 32 to 64 and by 19.6 from 64 to 128: faster than the
  predicted h^2 (refuted as to the order, confirmed as to the direction; the deposit of
  the corner lattice by the linear cloud and the h^4 compensated filter mix);
- filter: 0.074 without against 0.078 with: the filter is a small part (confirmed in
  direction, marginal); the cloud of the corner lattice carries most of the smoothing;
- start epoch: c grows towards small eps_i but more slowly than 1/eps_i^2 (0.025, 0.078,
  >= 0.38 unconverged); the exact 1/eps_i^2 law is refuted;
- mu-independence at fixed eps_i could not be tested at mu = 0.5 (not solved).
Gradient-expansion diagnostics (same runs): non-conformally-flat part
max|gamma-tilde - delta| = 1.8e-4, 4.4e-3, 2.7e-2 at eps_i = 0.2, 1, sqrt 6 for
mu = 0.03 (Psi - 1 = 0.0149): the expansion is valid at the paper's start only;
transverse-traceless fraction of p_ij 0.26 per cent (mu = 0.03) and 3.9 per cent
(mu = 0.5).

## 2026-11-15, S0: processor dry run of the scouting configuration (written before the run)

The cards are queued behind about ten jobs. A processor run of the S2 input (four static
levels, mu = 0.03 data) for two cycles checks that the input, the data and the outputs
work before the card run, and gives the t = 0 constraint on the four-level mesh.
Prediction: it runs; 4 x 56 + 64 = 288 blocks of 16^3 (about 1.2e6 cells); at t = 0 the
relative Hamiltonian constraint H_r max is of order 1e-3 to 1e-2 (T2b: 8 per cent of the
perturbation at two levels; delta_N at the peak is 0.011 at mu = 0.03, eps_i = 1), all
on refined blocks; about 170 s per cycle (7.8e3 zone-cycles per second).

### S0 outcome (run A-emd-pbh-20261115-161829-dba94f6)

Confirmed: 288 blocks (56 per level 0-3, 64 on level 4), two cycles in 7.6e3 zone-cycles
per second, k dt = 0.0049. At t = 0: H_r max = 5.0e-3, H_r mean 6.4e-4, H max = 0.044
(about 0.18 of 16 pi max|E - Ebar|, against 0.077 with two levels in T2b: the deeper
levels add interpolation error). The finder ran (no horizon) but wrote its summary file
into the working directory, here the worktree root: the finder's output paths are not
taken relative to `-d` (moved by hand into the run directory; card runs run in their
run directory, so they are not affected). Recorded for core as a minor defect.
The dry run also showed two defects of my inputs, fixed before the queued card runs
started (inputs edited in place; manifests of S1 and S2 note it): the y and z lines of
E were written to the same file name as the x line (AthenaK names tab files by variable
unless `id` is set), and `adm_alpha` is not output when Z4c evolves the lapse (the
lapse is `z4c_alpha`). A smoke run of the corrected outputs (unregistered,
`scratch/A-emd-pbh/tmp/smoke_out`) produced all nine files and the analysis figures.
The T2 runs used the earlier version of `inputs/peak_smr.athinput` (outputs only differ).

Correction to the H-smooth entry above: for one Fourier mode lap psi_N = (3/2)(aH)^2
delta_N gives -2 psi_N / delta_N = 3 (aH/k)^2, not (3/2)(aH/k)^2 as written there (the
reading is unchanged; DESIGN.md uses the corrected factor).

## 2026-11-15, S2 outcome (run A-emd-pbh-20261115-155754-8422a4a; analysis A-emd-pbh-20261115-170751-a2287be; figures looked at)

Ran to tau = 28.9 (250.9 t_H), 5,919 steps, Slurm COMPLETED, 1,023 s = 0.284 card-hours
(prediction: below 0.3, confirmed; 0.17 s per step against the 0.13 of the unit-cost
model, a factor 1.3). All 262,144 particles kept (none excised, none escaped, rest mass
unchanged to 1e-16), no unconverged push.
- **No horizon** in 45 finder calls from tau = 15 (confirmed, as every criterion
  predicts).
- **Constraints: refuted.** I predicted H_r max below 1e-2 until the pancake (tau ~ 23).
  It passed 1e-2 at tau = 3.2 (t ~ 1.5 t_H) and 0.1 at tau = 14.1, and rose to 0.40, 0.84,
  1.66 at 130, 160, 200 t_H (maximum 1.73); the mean stayed at 5e-3 to 130 t_H and rose to
  0.07-0.22 after 160 t_H. M_r max 0.79 at 130 t_H, 1.6 at the end. Theta max 1e-5 to
  3e-4. By the bound of SCOPE.md section 3 (L2 of H outside any horizon below 0.1 of L2
  of 16 pi E), which the run cannot evaluate on its refined mesh (request 5), the late
  part is suspect; the maxima say the run is not converged in the sense of the threshold
  definition after ~100 t_H.
- Central density E_max/Ebar: 13 at 130 t_H (first Zel'dovich axis: 133 t_H), 26 at 160,
  106 at 200, 744 at 250 t_H. The profiles (`figures/fig_scouting_profiles_S2.png`) show
  the sheet normal to z (narrow in z, wide in x and y, as the eigenvalues say), density
  spikes at y = +-0.4/k with a dip at the centre by 207-251 t_H (caustics of the
  multi-stream sheet [JUDGEMENT]), and staircases on the refined levels from about
  30 t_H: the adaptive cloud level keeps the clouds on the root level (one particle per
  root cell, deposit_ppc = 2) and spreads them as constants over the fine cells, while
  the metric is smooth. Jumps of E_max at ~160 and ~220 t_H are the cloud level moving
  one level finer as the particles concentrate. Reading [JUDGEMENT]: the staircase of
  E against the smooth metric on refined levels, already 8-18 per cent of the
  perturbation at t = 0 (T2b, S0), drives most of the growth of H_r; the cure is more
  particles in the refined region (nested lattice, request 2), not the gauge.
- Lapse: alpha/a at least 0.94 everywhere to the end; at |x| = 4/k it stays within 3e-3
  of a(tau) (tab lines), so the far field follows the homogeneous solution and the
  background time of the collapse definition is usable (prediction "within ten per cent
  to tau ~ 20": confirmed, by a wide margin).
- Nothing broke: no crash, no non-positive metric determinant, no lapse collapse.

## 2026-11-15, S1 outcome (run A-emd-pbh-20261115-160349-9d232d2; analysis of both A-emd-pbh-20261115-171930-878a114; figures looked at)

Slurm COMPLETED, 653 s = 0.181 card-hours, 4,078 steps; but **the fields became
non-finite at tau = 11.70 (t = 21.9 t_H)** and the run carried them to tlim:
- before: central lapse alpha/a 0.81 (tau = 5, 2.9 t_H), 0.75 (6.2 t_H), 0.57 (11.3 t_H),
  0.43 (16.2 t_H), 0.14 at tau = 11.70 (21.9 t_H); smallest lapse alpha_min/a 0.032 there,
  off centre (the y line shows minima at y = +-0.5/k by 14.7 t_H); E_max/Ebar 4.8, 19,
  403, 6,500, 36,000 at tau = 5, 7, 9, 11, 11.6 (with jumps where the cloud level moves);
  Theta max 1e-3 to 0.27; H_r max 0.047 at t = 0 (ten times S0 at mu = 0.03: linear, as
  T2b), 0.16 at tau = 5, 1.4 from tau = 9; M_r max about 1.6;
- at tau = 11.70, in one record: chi_min -> -inf, K_max = 1e47, Theta = 7e46, every
  particle flagged as excised (np = 0), the step fell to 1e-244 and grew back by a factor
  of about two per cycle until it reached the Courant step again at tau = 11.71; the run
  then integrated non-finite fields to tau = 16 without stopping;
- no apparent horizon in 44 finder calls from tau = 6 to the end (every call before the
  blow-up returned NaN, i.e. not found).
Against the predictions: (a) refuted (H_r max 0.16 at the first pancake, above 0.1; it
was 0.047 at t = 0); (b) confirmed (the central lapse falls relative to a from tau ~ 7);
(c) undecided: no horizon by 21.9 t_H, where H1 and the particle runs of
arXiv:2609.14218 expect one near 13-16 t_H, and no halt either (the lapse kept falling,
the density kept rising); (d) confirmed in kind, not in time: the run ends with a
non-positive conformal factor (chi -> -inf; the cosmo E1 failure) at tau = 11.7, later
than the predicted "before tau ~ 10". Outcome class of SCOPE.md section 3: UNDECIDED.
Card-hours of both scouting runs: 0.465 of the 1.5 allowed.

## 2026-11-15, lead's review note (appended by the lead of A-emd-pbh; `stage/REVIEW-wave2.md`)

Reproduced: `analyse_scouting.py` rerun from the registered outputs (run A-20261115-182347-8ee3fcc)
gives the summary and the figures of A-emd-pbh-20261115-171930-878a114 byte for byte. The lead's
own reader (run A-20261115-182314-bebd0cf) confirms S1 non-finite at tau = 11.709 (21.9 t_H), H_r
max 0.047 at t = 0, alpha/a 0.136 at the last finite record, and S2 alpha_min/a >= 0.943. Two
conversions in the S2 outcome above are wrong: with t/t_H = ((1 + tau/2)^2/6)^(3/2) (P0),
tau = 3.24 is 1.2 t_H (not 1.5) and tau = 14.14 is 35.8 t_H (DESIGN.md said 45); DESIGN.md
corrected, the entry above is left as written.


---

# Wave 3, round 1 (2026-11-20): the relaxed 1+log lapse in the box

Package brief: `tracks/A-emd-pbh/PLAN-wave3.md` row 6. Executable of the card runs:
`/data/haiyangw/nrpic/scratch/core/exe/core_gauge/athena_gpu` (source b4430da, READY of
that directory: option `<z4c> lapse_leak`, tested on cards; no guard, no periodic finder,
no `dt_lightspeed`). Runs are registered with `harness/bin/nrpic-run` (`--package
tracks/A-emd-pbh/periodic_threshold`); run ids `A-<UTC>-<commit7>`.

## 2026-11-20 22:30Z, D3: data of P0L (written before the run)

`scripts/build_p0l.sh`: `make_peak_ic.py --mu 0.3 --e 0 --p 0 --eps-i 1 --n 64 --nfilter 2
--compensate` (the S1 settings with e = 0), then `track_select.py`, which reorders the
particle file so that 317 particles on the six half axes and the eight half diagonals
through the peak come first (tags 0..316, tracked by `traj_ntrack`). Checked before on
the S1 data (unregistered, scratch/A-emd-pbh/tmp/periodic_threshold/tsel_test): the
lattice of make_field sits on cell corners, (i + 1) h - L/2, so one particle sits on the
peak; largest displacement 0.18 spacings.
Prediction [JUDGEMENT]: the solve converges as at e = 0.2 (T1b: residual 7e-12, 33 inner
iterations per outer step, c = 0.137), because the spherical peak has the same central
amplitude and a profile no steeper than the elliptical one along its short axis: residual
below 1e-10, c between 0.05 and 0.2, delta_N max 0.12 (the Laplacian of the same Gaussian
at the centre does not depend on e), alpha_min about 0.80. Refuted if the inner solves
stagnate at the 60-iteration limit (then P0L moves to mu = 0.2).

### D3 outcome (run A-20261120-223123-f436c39; closed by the lead in batch 2b; recorded 2026-11-21 12:58Z by the helper of batch 3)

From `P0_mu0.3.log` and `P0_mu0.3/id.json` of the run: 17 outer steps, 29 to 33 inner
iterations each (no stagnation at the 60-iteration limit), Hamiltonian residual 6.0e-12,
momentum residual 1.0e-11 (prediction below 1e-10: holds), c = 0.088 (between 0.05 and
0.2: holds), delta_N max 0.118 (prediction 0.12: holds), alpha_min 0.805 (about 0.80:
holds). zeta_max 0.296, largest displacement 0.134 spacings, 317 tracked particles with
r0 from 0 to 9.375 (`track.json`). P0L stays at mu = 0.3.

The session of 2026-11-20 was cut after writing `scripts/ltbref.py`, `scripts/ltb_reference.py`
and `inputs/peak_leak.athinput` (uncommitted, never run). This session commits them,
runs the reference (R1 below) and finishes the decks.

## 2026-11-21 13:00Z, R1: exact reference of the spherical peak (written before the run)

`scripts/ltb_reference.py --data <P0 data> --mu 0.3 --rate 20` (processor, registered).
Two references: A, the paper's profile with simultaneous bang (ltb2609.Profile2609,
MDPBH.tex:573-743); B, the code's own initial slice (M, E and age of the shell of each
tracked particle, from fields.bin by Fourier interpolation; ltbref.reference_B).
Code units G = c = 1, H_i = 1 at a_i = 1, t_i = 2/3, k = eps_i = 1, t_H = t_i 6^(3/2) =
9.80; tau is the proper time from the initial slice.

Predictions, by hand from the closed forms (MDPBH.tex:680, 695, 743) [JUDGEMENT]:
- A1 every shell bound (ktilde = (2 mu/3) e^(-u) (1 - mu u e^(-u)) > 0, u = r^2/6), the
  crunch time t_s(r) increasing with r, and no shell crossing before the crunch of either
  shell (simultaneous bang with t_s' > 0 [BACKGROUND: Hellaby-Lake conditions]).
- A2 central crunch t_s(0) = (pi/3) m(0) ktilde(0)^(-3/2) with m(0) = 4 e^(3 mu)/(3 t_i^2) =
  7.38, ktilde(0) = 0.2: t_s(0) = 86.4, tau = 85.7, 8.82 t_H.
- A3 the first marginally trapped sphere (minimum over shells of the time of R = 2M) is
  the centre at the central crunch: near r = 0, t_ah = t_s(r) - 4M/3 with
  t_s(r) - t_s(0) = 15 r^2 and 4M/3 = 1.6 r^3, so t_ah grows outward. So the exact
  solution HAS trapped spheres at mu = 0.3 before any shell crossing, but they appear
  only with the central singularity and the apparent horizon grows outward from zero
  mass (consistent with "globally naked" at mu = 0.32, MDPBH.tex:766-768). Refuted if the
  minimum of t_ah sits at r > 0.1 r_m and earlier than t_s(0) by more than 1 per cent.
- B1 the ages of the code's shells equal t_i = 2/3 within 3 per cent for r0 < 5 (the
  data carry the growing mode only; nonlinear corrections ~ delta^2 ~ 1e-2), all shells
  of r0 < 5 bound; B shows a shell crossing only if its ages spread (decaying mode).
- B2 at equal Misner-Sharp mass the code's turnaround, R = 2M and crunch times differ from
  A by less than 20 per cent for 0.8 < r0 < 3 (the code's slice at eps_i = 1 is not the
  gradient-expansion slice of the paper: solve change c = 0.088, D3); sign not predicted.
- B3 axes and diagonals give the same M at equal r0 within 1e-3 for 0.5 < r0 < 5
  (64^3 lattice, spectral data, profile width 2.45 = 7.8 spacings).
- P periodic images: zeta at the face (r = 10) 5.8e-8 of mu, at the nearest image
  exp(-L^2/6) ~ 1e-29; the box mean of zeta removed by the periodic solve
  mu (6 pi)^(3/2)/L^3 = 3.1e-3, a shift of the background that B contains and A not.
- L background of the relaxed lapse with T = 0.05: alpha = exp(6 T H) within 1e-3 after
  t = 0.5; the coordinate time of 8.8 t_H (t = 86.4 - t_i) within 0.5 of the proper time.
Refuted as stated per item; a crash of the script is recorded and fixed, not hidden.

### R1 outcome (runs A-20261121-125808-7366ccd and, with the anisotropy measure corrected, A-20261121-130103-e007f42; `figures/fig_ltb_reference.png` looked at)

Numbers from `ltb_reference.json` of A-20261121-130103-e007f42 (every other number identical
to the first run):
- A1 holds: every shell bound, crunch time increasing with r, no shell crossing to tau = 3000.
- A2 holds: central crunch tau = 85.72 (t = 86.39, 8.817 t_H).
- A3 holds: the earliest R = 2M is at the innermost sampled shell (r = 0.005) at
  tau = 85.725, 3.8e-4 after the central crunch. The exact solution of the paper's profile
  at mu = 0.3 therefore HAS trapped spheres before any shell crossing, but its apparent
  horizon is born at the centre with the central singularity and grows outward from zero
  mass. P0L keeps mu = 0.3 and is compared shell by shell, with the horizon mass against
  time as the second test.
- B1 REFUTED: the code's own slice has shell ages from 0.577 (r0 = 0.30) to 0.670 (far
  field 0.668-0.670, t_i = 0.667): the centre is 13 per cent "young", a bang-time (decaying)
  perturbation in the make_field data at eps_i = 1. No shell crossing in any of the 14
  directions to tau = 600 all the same. All shells bound (the far shells weakly: the box
  mean of zeta, 3.07e-3, sits in the background of B).
- B2 REFUTED in its bound: at equal Misner-Sharp mass the code's slice turns around,
  traps and crunches 16-17 per cent EARLIER than A (median for 0.8 < r0 < 3; at most 30
  per cent there; 35 per cent at r0 = 0.3; agreement only near r0 = 3.5; beyond r0 = 5
  the comparison loses meaning, A's far shells crunching at tau ~ 1e4). Central crunch of
  the code's data: tau = 56.83 (5.87 t_H) against 85.72 (8.82 t_H) for the paper's profile.
  [VERIFIED for the spherical evolution of the code's t = 0 data] The data that make_field
  builds at mu = 0.3, eps_i = 1 are NOT the paper's mu = 0.3 spacetime: they collapse 1.5
  times earlier in proper time. Any comparison of the code's mu with the paper's threshold
  (0.32 < mu_c <= 0.33) has to go through reference B (or a generator that builds the
  paper's slice: request 1 of DESIGN section 8).
- B3 REFUTED at its stated bound, as a measurement: M of the diagonal shells against the
  axis shells interpolated in ln M against ln r0 differ by 4.7e-3 at most for 0.5 < r0 < 5
  (the first run's 0.14 was an artefact of interpolating M linearly in r0, M ~ r0^3);
  panel (a) shows axes and diagonals on one curve; +x, -x, +y, -z identical to the digits
  printed. Interpolation between axis shells 0.3 apart remains a candidate for the rest
  [JUDGEMENT].
- P as computed: zeta at the face 5.8e-8 of mu, at the nearest image 1e-29, box mean of
  zeta 3.07e-3. The images are negligible for the comparison; the zero mode is in B.
- L partly refuted: alpha = exp(6TH) holds after t ~ 0.3 (panel d; 1.052 at t = 3, 1.002 at
  t = 100), but the proper time of the background runs 0.54 (t = 10), 0.95 (t = 86) and 1.12
  (t = 200) ahead of the coordinate time (I said within 0.5); 8.8 t_H is coordinate time
  84.6, 21.9 t_H is 212.8.

Reference B for P0L, axis shells (r0, M; tau of turnaround, R = 2M, crunch):
0.30, 0.032; 28.1, 56.8, 56.8 | 0.60, 0.247; 30.4, 61.1, 61.5 | 0.91, 0.789; 34.6, 68.6,
69.7 | 1.21, 1.745; 41.0, 80.0, 82.6 | 1.52, 3.145; 50.5, 96.9, 101.7 | 1.83, 4.993; 64.6,
122.2, 129.8 | 2.15, 7.298; 85.7, 160.8, 172.1 (all shells: `ltb_reference.json`, key B.shells).

## 2026-11-21 13:10Z, K: processor smoke test of the relaxed-lapse deck (written before the run)

`inputs/peak_leak.athinput` (finished this session: release core-v0.5, cfl 1.0 with
dt_lightspeed 0.25, guard, hmean_tol_0 = 1e30, finder diagnostics, region norms, output
cadences for a run of ~140 time units) through `scripts/smoke_leak.sh`: P0L (data of
A-20261120-223123-f436c39, particles_track.nrp, traj_ntrack 317) and S1L (data of
A-emd-pbh-20261115-155802-9a6596f), 4 cycles each on the processor build of core-v0.5, the
finder from t = 0 every 2 cycles.
Prediction: both exit 0 after 4 cycles; the first step is 0.25 dx/c_max with c_max = the
largest lapse of the data (about 1.0) times sqrt(chi) (about 1): dt about 0.0049, falling
as the background lapse rises towards 1.27 (dt about 0.0039 by cycle 4, T = 0.05 being
~10 steps); no guard stop; the finder searches and finds nothing (status file written,
reason other than an immediate stop by hmean_tol); region.hst written; for S1L the t = 0
constraint statistics of S1 (H_r max 0.047, A-emd-pbh-20261115-160349-9d232d2) repeat
(same data, same mesh). Refuted by a non-zero exit, a guard stop, or a first step that is
not 0.25 dx/c_max.

### K outcome (run A-20261121-130655-0e84f0d)

Both runs exit 0 after 4 cycles (40 s set-up each on one core); no guard stop; the finder
searched at cycles 0 and 2 and stopped after 2 flow iterations with "mean radius
negative" (reason 4: not found, and not the immediate hmean_tol stop of the old decks);
`peak.region.hst` written (P0L at t = 0: inside r_m, H2 = 0.107 against 16 pi E2 = 7.51);
317 tracked particles in `peak.traj.bin`/`trajmet.bin` (5 records). S1L at t = 0 repeats
S1's constraint statistics (Hr_max 0.0471379 in both; S1 on the card,
A-emd-pbh-20261115-160349-9d232d2). One part refuted: the first step is 6.68e-3, not
0.0049: 0.25 dx/c with c = 0.73 on the finest level (central lapse 0.8 and chi there), so
the light-speed limit acts (dt < cfl dx = 0.0195) but my c_max = 1 was wrong; the mean step
of the first four cycles is 6.3e-3 (time 0.0253 at cycle 4) as the lapse rises. Warning:
`max_nmb_per_rank` is not used by a static mesh (harmless). No figure for four cycles; the
t = 0 lines of both runs enter the figures of the analysis (compare_ltb.py is first run on
this smoke output).

## 2026-11-21 13:20Z, P and S: card job 1, P0L and S1L (written before submission)

List `lists/job1.list`, release core-v0.5 card executable, wall 00:58:00; P0L to t = 140
(athena -t 00:25:00), then S1L to t = 220 (-t 00:30:00). Steps: dt rises from 6.7e-3 to
dx = 0.0195 once c_max < 0.25 (a > ~4, t > ~5): about 7,400 steps for P0L, 11,500 for S1L;
at S1's 0.16 s per step (A-emd-pbh-20261115-160349-9d232d2) 20 and 31 minutes, so either
may end on its wall limit with a restart file (then a second job continues it).

P0L, against reference B (R1, A-20261121-130103-e007f42) [JUDGEMENT throughout]:
- P1 background: alpha at |y| = 8 (alpha_y line) within 1e-2 of exp(6TH) of the R1
  background for t > 1, 1.02 +- 0.01 at t = 10.
- P2 shells: areal radius of the tracked shells (R = r sqrt(g_T) from trajmet) against
  their own proper time: within 3 per cent of B up to turnaround for r0 >= 1.2 (resolved
  by >= 4 root cells and the two binomial passes of the deposit); inner shells r0 <= 0.6
  turn around and crunch LATER than B (the deposit smooths the central density over ~2
  root cells). Turnaround (tau, B): 41.0 (r0 1.21), 50.5 (1.52), 64.6 (1.83), 85.7 (2.15)
  within 3 per cent for r0 >= 1.2. No particle reaches R = 0 in the code (the lapse
  collapses and the centre freezes); the 1+log lapse at the centre falls below 0.3 before
  coordinate time 70.
- P3 horizon: the finder finds an apparent horizon before t = 140 (coordinate), first at
  a coordinate time between 80 and 130 with mass between 1 and 5; at first detection the
  tracked shell whose B mass equals the horizon mass has proper time within 10 per cent of
  its B trapping time (B: R = 2M at tau = 80.0 for M = 1.75, 96.9 for 3.15, 122.2 for
  4.99), and the horizon mass at later searches follows M_B of the outermost shell whose
  proper time has passed its trapping time, within 10 per cent.
- P4 health: no guard stop before t = 140; region norm H2/E2 inside r_m below 0.05 to
  t = 50.
Refuted item by item; a guard stop or no horizon with a healthy run are the two outcomes
that would most change the plan (the first points at the gauge or the step, the second at
the finder or the central resolution).

S1L (mu = 0.3, e = 0.2, the S1 data; S1 in the E1 gauge went non-finite at tau = 11.70,
21.9 t_H = coordinate 212.8 here, and its finder never searched: hmean_tol 100):
- S1 the relaxed lapse carries the run past 21.9 t_H (coordinate 212.8) without a guard
  stop, or, if a horizon forms, to it and beyond for at least 10 time units;
- S2 an apparent horizon is found between 10 and 22 t_H (coordinate 97 to 213); the
  spherical peak of the same mu in the code traps from about 8 t_H (B), the elliptical one
  later [JUDGEMENT]; the paper's particle runs expect 13-16 t_H for their data (DESIGN
  section 7), which differ from ours (R1: the code's spherical data collapse 1.5 times
  earlier than the paper's profile).
- S3 central alpha falls below 0.3 before the horizon is found; E_max grows past 1e3 Ebar.
Refuted by a guard stop before 212.8 without a horizon, or by no horizon to t = 220 in a
healthy run (then S1 data are below the code's threshold in this gauge, or the finder
fails: the status file says which).

### Reader check of compare_ltb.py on the smoke run (A-20261121-131819-ed01cef; figure looked at)

No prediction was written for this check of the script (stated here so that it is not
mistaken for a test). Areal radius R = r sqrt(g_T) of the 316 tracked shells from the
code's metric at the particles against reference B: 2.4e-5 at most over the 5 records
(t <= 0.025), i.e. the code's t = 0 slice and the Fourier evaluation of R1 agree; the far
lapse (|y| > 7) at cycle 4 is 1.12462 against 1.12483 of the homogeneous solution of the
relaxed lapse; the central lapse rose from 0.81 to 0.96 in those four cycles. Panels of
turnaround, horizon and constraint history are empty for four cycles, as they must be.

## 2026-11-21 13:25Z, state at the end of the batch-3 session (card job pending)

Card job 1, run A-20261121-131600-02b5d41, Slurm 4799: PENDING behind six jobs of other
owners; Slurm's estimated start 2026-11-21 10:57 PST, after this session's window. Nothing
of it is judged. To close it (next session or the lead):
1. `harness/bin/nrpic-run finish A-20261121-131600-02b5d41` once `squeue -j 4799` is empty;
   look at `scratch/A-emd-pbh/A-20261121-131600-02b5d41/batch.list.status` (exit 3 of a
   member is the guard's designed stop) and the `Terminating` line of each `athena.log`
   (wall limit -t 25 / 30 min: then a restart file in `rst/` continues it in a job of its own).
2. `compare_ltb.py --run .../P0L --ref scratch/A-emd-pbh/A-20261121-130103-e007f42` and
   `analyse_scouting.py --gauge leak --run S1L=.../S1L --run S1=scratch/A-emd-pbh/A-emd-pbh-20261115-160349-9d232d2/run`
   (the S1 line in the E1 gauge needs a separate call without --gauge leak), both
   registered (README "How to rerun"); read every figure.
3. Judge P1-P4 and S1-S3 (entry 13:20Z) here, extend DESIGN 7.1 and the README table.
Not done in this package: the S1-8ppc run (optional; does not fit beside job 1 in the cap
of the session's queue position) and the adaptive-refinement job of step 6 (release
core-v0.5 has adaptive refinement in nrpic_cosmo and its card build passed core's short
card check, which includes the 32^3 ladder deck of peak_amr; the package keeps one job in
the queue, so it waits for job 1). Card-hours used by this package in wave 3: 0 (job 1
asks for 0.97).

## 2026-11-21 20:44Z, outcome of card job 1 (run A-20261121-131600-02b5d41, Slurm 4799), by the lead of batch 5

Closed with nrpic-run finish: failed (exit 3). Both members stopped on the core-v0.5 guard (chi
not positive): P0L at t = 4.815 (cycle 464; chi = -0.45, Khat = 1.0e7 at (0.459, 0.459, -0.518),
level 4), S1L at t = 15.076 (cycle 1398; chi = -2e6). The lead's reading (run
A-20261121-203120-eaba95f, `analysis/periodic_job4799.py`, figure fig_periodic_job4799.png looked
at): in BOTH members the L2 norm of H jumps by about four orders of magnitude at t = 2.506
(P0L 1.2 -> ~1e5; S1L 1.5 -> ~1e5), and |K|_max of P0L oscillates at 1-10 from then until the
blow-up at 4.8. A jump at the same time in two data sets points at the deck or the step (cfl 1.0
with dt_lightspeed 0.25), not at the matter [JUDGEMENT; no run has yet tested either].

Predictions: P1 and P2 not judgeable beyond t = 4.8 (no line output was compared; the run ends
long before turnaround); P3 REFUTED (no horizon: the run stops at 4.8, not 140); P4 REFUTED (guard
stop at 4.8). S1 REFUTED (stops at coordinate 15.1, not past 212.8); S2 REFUTED (no horizon); S3
not judged. Request to core: outbox periodic-relaxed-lapse-blowup. No periodic card job of this
owner until core answers; the long runs of batch 5 go to the expanding ball (threshold_ball).

## 2026-11-21 23:15Z, Q: card job 2, P0L and S1L at cfl_number 0.5 (written before queueing; lead of batch 7)

What changed against job 1 (run A-20261121-131600-02b5d41, Slurm 4799): `cfl_number` 1.0 -> 0.5 in
`inputs/peak_leak.athinput` (header CORRECTION; cause of job 1's failure: package periodic_diag,
decision 0027 item 2), executable release core-v0.6 (`.work/build_gpu_v06/src/athena`) instead of
v0.5, and each member a chain of its own (`scripts/submit_chain.sh`, restarts exact for periodic
set-ups, decision 0027 item 3) instead of one batch job. Data, particles, mesh (root 64^3, four
static levels, finest dx = 0.0195), gauge (relaxed 1+log, lapse_leak 20, Gamma-driver 0.75,
eta 2), deposit, finder and tlim (P0L 140, S1L 220) as job 1. Queued as lines 14 (P0L) and 15
(S1L) of `threshold_ball/queue.txt`, behind the threshold scan; the sequencer registers each with
nrpic-run when a slot frees. The remedy is tested on the uniform 64^3 mesh only (periodic_diag
G1 at cfl 0.5, G6 at 0.6, lapse frozen); this job is its first test on the refined mesh with the
relaxed lapse evolving [JUDGEMENT throughout].

Q1 remedy (the test this job exists for): in neither member does the L2 norm of H jump by more
than a factor 10 between consecutive history records anywhere in t in [1.5, 6] (job 1: four
orders at t = 2.506 in both); H_max stays below 0.1 to t = 5 (R2, the card deck with zero shift
on processors: 1.45e-2 at t = 2.37, 7.6e-3 at 3.0; job 1's P0L 0.84 at 2.40, 179 at 2.51); the
level-4 step never exceeds 0.5 dx (read from the history's dt column); no grid-scale
(odd-even) pattern in the beta^x or alpha line outputs at t = 2, 4, 6, 8, 10.
Q2 health: no guard stop before t = 20 in either member (job 1: P0L 4.8, S1L 15.1).
Q3 cost: about 0.17 s per step as job 1 (0.173); P0L about 14,300 steps (41 min), S1L about
22,000 (65 min); within a factor 2, so P0L ends inside its 2 segments and S1L inside its 3.
Then predictions P1-P4 (P0L against the exact reference B of run A-20261121-130103-e007f42) and
S1-S3 (S1L) of entry 13:20Z apply unchanged; they are judged from this job, not rewritten.

Refuted by: a jump or a guard stop of the kind of job 1 at a later time (for example t ~ 5, the
same accumulated amplification reached at half the rate: then 0.5 is not below the refined
mesh's threshold, and the gauge-speed limit core is asked for is needed before any periodic run);
grid-scale growth in beta^x on level 4 or at a level boundary (a threshold lower than Test B's
0.685 at the coarse-fine interface, which Test B does not model). A late failure (t > 20) with
grid-scale growth at the collapsing centre where gt^xx > 1.9 would refute the margin of the
periodic_diag README (shift speed above 1 where the conformal metric stretches), not the remedy
for the expansion phase; the line outputs of gt (z4c tab) say which. A cost above a factor 2 is
not a refutation of the physics: the chain then stops before tlim and is resumed
(`scripts/submit_chain.sh <rundir> <deck> <same args>`).

## 2026-11-24 13:00Z, state of card job 2 and continuation of S1L (lead of batch 11)

P0L = A-20261122-235305-4ea0aa5 (Slurm 4916) ended at tlim 140 in its first segment (14596
cycles, 46 min: chain status DONE). S1L = A-20261123-025907-97bab8d was cut, not failed: its
three segments went to preemptions of 2026-11-23 (segment 1 reached t = 10.1 and was killed
before its first restart after t = 0; segment 2 made no step; segment 3 restarted from t = 0 and
reached t = 66.25, cycle 7050, before SIGTERM; restart dt 50, so the newest restart is
`rst/peak.00001.rst` at t = 50), and the chain closed as FAILED (MAX_SEGMENTS = 3 reached). No
guard stop and no non-finite field in any segment log. Continued in place, not repeated: same run
directory, same executable (cmp-identical to the release v0.6 card build), same deck and
arguments, MAX_SEGMENTS raised to 9, restart cadence lowered to dt = 10 by `output7/dt=10.0` on
the command line (output cadence only; the physics and the step are unchanged). The predictions
Q1-Q3 (entry 23:15Z) and S1-S3 (entry 13:20Z) stand unchanged; Q1 and Q2 are judged now from the
history to t = 66 (later records of repeated times win), S1-S3 when the chain reaches 220.

## 2026-11-24 13:25Z, F: why P0L's finder found nothing (written before the runs; lead of batch 11)

Facts from job 2 (compare_ltb A-20261124-130142-9a2d6a2, job2_q A-20261124-130507-10510ac): P0L ran
to t = 140 without a guard stop; 160 searches, none found (60 "mean radius negative" for t <
78, then 100 "iteration limit reached without convergence of the mass", every one stuck at a
round sphere of coordinate radius 0.45 with area mass about 13 and mean expansion +350). Yet the
code's own shells fall through R = 2 M_B: r0 = 1.21 (M_B 1.74) at code proper time 84.8, r0 =
1.52 (M_B 3.14) at 99.6, from coordinate time ~87 and ~119 on. If the Misner-Sharp mass of a
shell equals M_B (no shell crossing), the slice holds trapped spheres from t ~ 87.

F1 (slice side, analysis only): the Misner-Sharp compactness 2m/R along the x line, from the
z4c line outputs (physical g = gt/chi, K_ij = (At_ij + gt_ij K/3)/chi, K = Khat + 2 Theta)
with conv_ball's misner_sharp_line, shows trapped points (2m/R > 1) on every line output after
coordinate time 90, and the outermost marginally trapped sphere's m is within 10 per cent of
M_B of the outermost shell past R = 2 M_B (1.74 at t ~ 100, 3.14 at t ~ 120-140). Refuted by
no trapped point on the line to t = 140 (then the slice avoids the trapped region and P3's
failure is the slicing, not the finder).
F2 (finder side, processors): the release finder restarted from P0L's restart files (t = 100,
peak.00002.rst; t = 140, peak.00003.rst) on the v0.6 threaded processor build, two cycles with a
search every cycle and initial radius 0.15, 0.3, 1.0 or 2.0 (deck value 0.6), converges to a
surface with irreducible mass within 10 per cent of the F1 line mass from at least one start
radius at t = 140. Refuted if no start radius converges while F1 shows a trapped sphere: then
the finder fails on this slice (strongly stretched centre, chi ~ 1e-5) and core is asked. A
restart of a card file that the processor build cannot read is recorded as such (no
judgement of F2).

## 2026-11-24 13:30Z, outcome of card job 2: Q1-Q3, P1-P4, F1 (lead of batch 11)

Runs: P0L = A-20261122-235305-4ea0aa5 (closed: completed, tlim 140, one segment, 14596
cycles); S1L = A-20261123-025907-97bab8d (to t = 66.33 so far, continued, see entry 13:00Z).
Analyses: job2_q A-20261124-130507-10510ac (fig_job2_q.png), compare_ltb
A-20261124-130142-9a2d6a2 (fig_compare_ltb_P0L.png), line_trapped A-20261124-131430-d1a2ee6
(fig_line_trapped.png); every figure looked at.

Q1 (the remedy on the refined mesh):
- (a) HOLDS: L2 norm of H changes by at most a factor 1.24 (P0L) and 1.29 (S1L) between
  consecutive records in t in [1.5, 6] (job 1: four orders at t = 2.506); cstat H_max by 1.30
  and 1.13.
- (b) REFUTED as worded, holds where it was aimed: H_max is above 0.1 only in the first
  ~0.3 time units (the data's own H_max is 0.487 at t = 0 for P0L, 0.496 for S1L, relaxing); in
  the window of job 1's jump it is 0.018 at t = 2, 0.016 at 2.4 (the zero-shift processor run R2
  had 0.0145 at 2.37), 0.011 at 3, 0.0078 at 5. My bound did not account for the t = 0 value of
  the refined-mesh data.
- (c) HOLDS: largest level-4 step 0.5000 dx (cfl_number 0.5 caps it from t ~ 3.5; before that
  the light-speed limit, 0.13-0.5).
- (d) HOLDS: odd-even amplitude of beta^x on level 4 at most 2.7e-5 of max|beta^x| at t = 2-10;
  the largest odd-even ratio on any level and line is 1e-2 (beta^x, level 0, t = 4: the second
  difference of a smooth profile at the root spacing, not an alternating mode); beta^x lines
  smooth (panel e). gt^xx on the x line at most 1.042.
Q2 HOLDS: no guard stop; P0L reached 140, S1L 66.3 before its preemptions.
Q3 HOLDS: 0.189 s per step (P0L, cpu time over cycles), 0.166-0.175 (S1L); 14596 steps for P0L
(predicted 14,300).
The remedy (cfl_number 0.5 with the Gamma-driver) is confirmed on the refined mesh with the
relaxed lapse evolving, through t = 140 [VERIFIED, two members]. Posted to core (outbox).

P0L against the exact reference B (entry 13:20Z):
- P1 HOLDS: far lapse at |y| > 7 within 2.2e-5 of the homogeneous relaxed lapse for t > 1.
- P2 PARTLY REFUTED: turnaround within 3 per cent of B for r0 >= 1.52 (2.9, 1.8, 1.7, 2.8 per cent)
  but 4.9 per cent at r0 = 1.21 (R within 3.5 per cent); inner shells later than B as predicted
  (r0 0.30-0.91: 9-27 per cent); all 14 directions identical to 1e-12 (spherical symmetry kept).
  The central lapse falls below 0.3 at t = 91, not before 70 (refuted).
- P3 REFUTED: no horizon found in 160 searches (60 "mean radius negative" before t = 78, then
  100 "iteration limit without convergence", each stalled at coordinate radius 0.45 with area
  mass ~13 and mean expansion +350). The code's tracked shells fall through R = 2 M_B from
  coordinate ~87 (r0 = 0.30-1.21) and ~119 (r0 = 1.52), proper times 6-33 per cent after B.
- P4 PARTLY REFUTED: no guard stop to t = 140 (holds); region norm ||H||/||16 pi E|| inside r_m
  0.168 by t = 50 (bound 0.05; a rise from ~0.05 to 0.17 between t = 46 and 50, at the same time
  as the jump of H_r max to ~1.5 in both members).

F1 (written 13:25Z) PARTLY REFUTED: the slice holds trapped spheres on the x line only from
t = 132 (not after 90): 2m/R reaches 0.75 at t = 100, 0.93 at 120, 1.02 at 132-140; the outermost
marginally trapped sphere sits at coordinate r = 0.072-0.076 (3.7-3.9 cells of level 4) with
R = 9.5-10.0 and m = 4.45-5.01, against M_B 3.14 of the outermost code shell past R = 2 M_B (not
within 10 per cent: 1.4-1.6 times larger, close to M_B 4.99 of r0 = 1.83). The areal radius at
r = 0.45 is 26.0 at t = 140, so the finder's stalled sphere (area mass ~13) is a round sphere far
outside the horizon: the gauge has drawn the collapsing region with R up to ~10 inside coordinate
r < 0.08. The Misner-Sharp mass of the slice near the centre is below M_B of the shells there
before t ~ 130 (at t = 100, m ~ 1.4 at R ~ 4), which is why particle shells read R < 2 M_B while
the slice is not yet trapped; whether that deficit is the slice's or the line's (innermost points,
1-4 cells) is [TO VERIFY].

## 2026-11-24 13:40Z, D: P0L on six static levels (peak_leak6), written before the processor smoke test and the card job

Why: P0L's horizon sits at coordinate r ~ 0.075 under 4 cells of level 4 (F1), and the finder
does not converge there (F2 so far). peak_leak6.athinput adds levels 5 (|x| < 0.3125, dx 0.00977)
and 6 (|x| < 0.15625, dx 0.00488), finder from t = 100 at initial radius 0.15, restart dt 10;
same data, particles, gauge, cfl_number 0.5 (every level at most 0.5 dx, decision 0027).
Queue: scratch/A-emd-pbh/sequencer_b11/ (queue file periodic_threshold/queue_b11.txt, line 1),
behind the two continued chains. Predictions [JUDGEMENT throughout]:
- D0 smoke (processors, 4 cycles, release v0.6 build): exit 0, 400 leaf MeshBlocks, first step
  0.25 dx6 / c (about 1.7e-3), no guard stop.
- D1 health: no guard stop to t = 140; the L2 norm of H changes by at most x10 between records
  in t 1.5-6 (Q1a repeated on six levels).
- D2 slice: trapped points on the x line (2m/R > 1 with K_T > 0) appear before t = 125 (on four
  levels: t = 132), and the outermost marginally trapped sphere's m at t = 140 lies within 10 per
  cent of the four-level value 5.0. Refuted by first trapping at t >= 130 again (then the late
  trapping is the slicing, not the central resolution).
- D3 finder: a horizon is found before t = 140, persistent from its first detection, with m_irr
  within 5 per cent of the line value at the same time. Refuted by no detection while D2 shows a
  trapped sphere resolved by >= 10 cells of level 6 (then the finder itself fails on this slice).
- D4 shells: turnaround of r0 = 1.21 within 3 per cent of B (four levels: 4.9) and of r0 = 0.91
  within 6 per cent (8.6). Refuted if neither improves (then the inner error is the particles').
- D5 cost: 0.22-0.35 card-seconds per step, about 57,000 steps to t = 140 (4-5.5 card-hours,
  5-7 segments).

### F2 outcome (run A-20261124-131232-e7b58f8, closed): REFUTED, the finder does not converge on P0L's slice

The processor build read the card restart files (setup complete in every member). Two or three
searches per member, 1000 flow iterations each, none converged ("iteration limit reached without
convergence of the mass"):
- t = 140, start radius 0.15: stalls at mean radius 0.083 with area mass 5.23 and mean expansion
  +3.06; start 0.3: r 0.099, m 5.63, +23; start 1.0: r 0.657, m 17.0, +534; start 2.0: r 1.69,
  m 34.9, +1569. The line's marginally trapped sphere is at r 0.0758, m 5.01 (F1): the search
  from 0.15 ends 9 per cent outside it in radius and 4.4 per cent above it in mass, still with
  positive expansion.
- t = 100, start 0.3: "mean radius negative" (the flow shrinks to the centre: no trapped sphere,
  as F1 found on the line at t = 100); start 1.0: stalls at r 0.417, m 9.79.
So on four levels the finder cannot settle on a horizon of ~4 cells, from any start radius. No
request to core yet: D3 (six levels, ~15 cells across the horizon) is the run in which a finder
failure could not be blamed on resolution.

### D0 outcome (run A-20261124-133457-9264c61, closed)

Exit 0 after 4 cycles on the release v0.6 processor build (one core, ~2 min per cycle with a
search every 2 cycles); 400 MeshBlocks (56 per level 0-5, 64 on level 6), no guard stop; the
finder searched (3 status rows). The first step is 8.93e-4, not 1.7e-3 as predicted (D0 refuted
in that number: the light-speed limit on level 6 binds with c ~ 1.4, a factor 1.9 smaller step
while c > 0.5; the late step is the cfl cap 0.5 dx6 = 2.44e-3 as assumed in D5). The deck goes to
the cards (queue_b11 line 1).

## 2026-11-25 07:15 PST (lead of batch 19): test A2 from S1L, prediction before any reading of its snapshots

Decision 0039 item 2(a): the lead decides whether the triaxial run S1L serves as A2 (oblate collapse against
the Zel'dovich time of first shell crossing) or one oblate member is queued. Decision: S1L serves as A2.
Its run A-20261123-025907-97bab8d (core-v0.6 card build, S1 data mu = 0.3, e = 0.2) has run to t = 198.7 and
wrote 20 full particle snapshots (262144 particles, every 10 coordinate units, peak.part.00000-00019.bin), so
the epoch of the first Zel'dovich axis lies inside the part already run; q0015 (continuation 198.7 -> 220) is
NOT needed for A2 (it serves S1-S3 and SCOPE section 7). Reference: DESIGN.md section 1, Zel'dovich eigenvalues
(2 mu/15)(k/aH)^2 (1+3e+p, 1-2p, 1-3e+p); first axis z at 4.2 t_H, second 8.5 t_H, third 33.6 t_H for mu = 0.3
(P0 run A-emd-pbh-20261115-153520-0576e01). Caveats on record: a periodic triaxial peak, not a deformed core
inside the ball; mu = 0.3 is not small, so the reference is first-order Lagrangian and the bound wide.
Prediction A2 [JUDGEMENT], written before any snapshot is read: the first shell crossing (sign change of the
Lagrangian Jacobian of x(q) on the particle lattice, or the z-separation of neighbouring lattice particles on
the z axis extrapolated to zero) happens first along z, at t_sc/t_H in [3.4, 5.0] (4.2 within 20 per cent: the
GR correction (aH/k)^2 ~ 6 per cent at that epoch plus an unquantified second-order Lagrangian term for e = 0.2),
before any horizon is found and before the central lapse falls below 0.3. Refuted by a first crossing outside
[3.4, 5.0] t_H, along another axis first, or no crossing before the lapse collapse. If the snapshots (spacing
of 10 coordinate units) cannot bracket t_sc to within that band, A2 is undecided and one oblate member is
queued (six card-hours at most, priority 2) with denser snapshots. Analysis not written yet (next session;
processors only; the conversion from coordinate time to t/t_H from the run's own background, DESIGN 1).

### Outcome of A2 (analysis A-20261125-151629-bb77171; second reading on three clocks A-20261125-151715-66f198f, added after the first reading; fig_a2_crossing.png looked at)

- Lattice: one-to-one from snapshot 0 (largest initial displacement 0.19 h); the minimum neighbour separation
  along z at t = 0 is 0.937 h, equal to the Zel'dovich value 1 - 0.064 at a = 1 (the data are the first-order
  growing mode, as designed).
- "z first" HOLDS: the first crossing is along z at the centre, then x, then y.
- The time PREDICTION IS REFUTED: the first z crossing lies at 6.35 t_H (snapshot bracket 6.19-7.21 t_H in
  coordinate time read as cosmic time), outside [3.4, 5.0]; on the other clocks 6.12 t_H (proper time of the
  lowest lapse), 6.13 (probe particle), 6.44 (background lapse): late by a factor 1.5 in time on every clock.
  Second axis x at 8.1-9.1 t_H (Zel'dovich 8.5), third y at 10.4-13.8 (Zel'dovich 33.6: after the first
  crossing the peak no longer follows the first-order solution). The lapse at the lowest point is 0.81 at the
  z crossing, so the slow central clock does not explain the lag. The separation falls more slowly than
  1 - 0.064 a from the first interval on (0.626 against 0.594 at t = 10, 0.200 against 0.008 at t = 40).
- Reading [JUDGEMENT, not tested]: Newtonian ellipsoidal collapse of the centre runs AHEAD of the Zel'dovich
  time, not behind it, so the lag is either relativistic (the scale is near the horizon early: (k/aH)^2 = a)
  or set by the initial velocities. The discriminating test, on processors: the same S1 particles under
  `<particles> pusher = newton`, `newton_poisson = fft` (core-v0.6), first crossing from the same reader.
  No oblate card member is queued: the snapshots bracket the crossing, so the fallback condition is not met.

## 2026-11-25 08:10 PST (lead of batch 20): A2 control in Newtonian mode and a second derivation of the reference, before any run

A2 stays FAILED as written (decision 0040 item 7). Second derivation of the Zel'dovich reference [this entry,
before the runs; inputs: id.json of A-emd-pbh-20261115-155802-9a6596f/S_mu0.3, a2.json of A-20261125-151629-bb77171]:
- Growth. For dust in an Einstein-de Sitter background the linear density contrast on the synchronous comoving
  slicing obeys delta'' + 2 H delta' = 4 pi G rho delta on every scale (no k dependence), growing mode
  D = a; the Newtonian Zel'dovich solution has the same D = a. The first-axis eigenvalue at a = 1 from S1L's
  snapshot 0 is 1 - 0.937 = 0.063 (DESIGN: (2 mu/15)(1 + 3e) = 0.064): first crossing at a_sc = 15.9 (15.6).
- Clock. H_i = 1 at a = 1: cosmic time t_c = (2/3) a^(3/2). r_m a H = 1 with aH = a^(-1/2) gives a_H = r_m^2 =
  6.000 (id.json r_m = 2.449490). So t_c/t_H = (a/6)^(3/2): a_sc = 15.6-15.9 gives 4.19-4.31 t_H. In the GR run
  (lapse ~ 1) a = (1 + 1.5 t)^(2/3) and t/t_H = (1 + 1.5 t)/6^1.5, the formula of a2_crossing.py. In the
  Newtonian mode (conformal time eta, a = (1 + eta/2)^2): t/t_H = (1 + eta/2)^3 / 6^1.5. The reference stands.
- What the particle file holds [VERIFIED, read this session]: total rest mass 956.02 against rho_m L^3 = 954.93;
  masses 0.966 to 2.19 times the mean (they carry psi^6 of the curvature perturbation, zeta_max 0.296); covariant
  u_i against the displacement x - q: ratio 1.03 (median), 1.00-1.38 (5-95 per cent), i.e. psi^4 times the
  f = 1 Zel'dovich velocity. A Newtonian pusher reads masses per coordinate volume and u_i as a dx/deta.
Members (core-v0.7 processor build, `pusher = newton`, `newton_poisson = fft`, spectral symbol, uniform periodic
64^3 mesh of side 20 = the particle lattice, CIC with the binomial filter and compensation of S1L, matter era
a = (1 + eta/2)^2, snapshots every 0.1 in eta to eta = 8.5; first crossing from a2_crossing.py --clock newton):
- N-z: S1L's positions, equal masses (rho_m L^3 / N), p = x - q: the pure Newtonian growing mode at a = 1;
- N-f: S1L's particle file as it is (the literal control of decision 0040 item 7);
- N-z128: N-z on a 128^3 mesh (force resolution).
Predictions [JUDGEMENT]:
- AZ1: N-z first crosses along z, at the centre, at t/t_H in [3.7, 4.5] (Zel'dovich 4.2-4.3; ellipsoidal second
  order earlier, CIC softening of a peak 8 cells in radius later, each under 10 per cent); N-z128 within 5 per
  cent of N-z. Refuted outside [3.7, 4.5] or another axis first; then the reference or the reader is wrong.
- AZ2: N-f crosses earlier than N-z (more mass at the peak, larger velocities), in [2.5, 4.3]. Refuted if later.
Consequence fixed now: if AZ1 and AZ2 hold, the same particles under Newtonian gravity cross about 1.5 times
earlier than under GR (6.1-6.4 t_H), so the lag is not in the initial velocities or masses as a Newtonian pusher
reads them; it lies in the relativistic evolution or in the coordinates of the GR run (the reader measures
coordinate separations; the Gamma-driver shift moves the coordinate lattice), and this control does not tell
which. If N-f crosses at >= 5.5 t_H the data are implicated instead.

### Outcome AZ1 (run A-20261125-160633-e38d321 member N-z; analyses A-20261125-162905-d0ef1d7 and A-20261125-162951-bb0fb26; fig_a2_crossing.png and fig_a2_compare.png looked at)

- N-z (Newtonian, 64^3 Fourier, equal masses, p = x - q) first crosses along z, at the centre, at 4.55 t_H (snapshot
  bracket 4.52-4.69), then x at 6.71; y not crossed by 9.9 t_H. Zel'dovich with the measured lambda_z = 0.063 (second
  derivation above): 4.35 t_H. AZ1 as written ([3.7, 4.5]) is REFUTED, narrowly: late by 5 per cent against Zel'dovich,
  the direction of the CIC softening caveat; N-z128 (same run, after N-f) tests that reading.
- Min Delta_z/h at S1L's snapshot times (t/t_H: Zel'dovich / GR S1L / Newton N-z): 1.09: 0.603 / 0.626 / 0.620;
  2.11: 0.382 / 0.467 / 0.398; 3.13: 0.196 / 0.326 / 0.209; 4.15: 0.030 / 0.200 / 0.052; 5.17: -0.123 / 0.093 / -0.069.
  The Newtonian member follows the Zel'dovich line to within 0.02 until it crosses; S1L leaves it from t/t_H ~ 1-2 on.
- What this establishes [VERIFIED by a run that could have failed]: the reference (D = a, a_H = r_m^2 = 6, the clock
  t/t_H = (a/6)^1.5) and the reader reproduce a Newtonian evolution of the same positions to 5 per cent; the factor
  1.46 of S1L (6.35 against 4.35) is not in the reference, the clock or the reader. Whether it is in the GR data
  (masses carrying psi^6, u_i carrying psi^4) is AZ2 (N-f, running).
Note on the IC script (defect of a diagnostic, not of the files): ic.json's median u/(x - q) is wrong (~1e-12): the
median lattice offset (1.4e-3 to 1.9e-3 instead of 0) puts tiny-|d| particles into the ratio. N-z's momenta carry a
uniform 1.4e-3 to 1.9e-3 (a bulk drift, harmless in a periodic box: neighbour separations do not see it). The
correct ratio (offset 0, read at the start of this session) is 1.03 median, 1.00-1.38 at 5-95 per cent.

### Outcome AZ2 and the consequence (analysis A-20261125-165125-1640161; fig_a2_compare.png with three curves looked at)

- N-f (S1L's particle file read by the Newtonian pusher: masses carrying psi^6 up to 2.19 times the mean, u_i read as
  a dx/deta) crosses along z at 0.43 t_H (x 0.50, y 0.65). AZ2's direction HOLDS (earlier than N-z), its band
  [2.5, 4.3] is REFUTED: read as a Newtonian coordinate density, the file is an overdensity of order one at the peak,
  not a Zel'dovich state. N-f is therefore not a fair copy of the GR physics; N-z is the control that matters.
- Consequence, as fixed before the runs: N-f does not lag (it crosses 15 times earlier than S1L), so the data as a
  Newtonian pusher reads them are not slow; N-z (the same positions with the Zel'dovich velocities) follows
  Zel'dovich to 5 per cent. The factor 1.46 of S1L lies in the relativistic evolution or in the coordinates of the
  GR run (the reader measures coordinate separations, which the Gamma-driver shift changes). Named only this far
  [VERIFIED: not the reference, the clock, the reader or the initial positions; a run that could have shown a
  lag in Newtonian dynamics did not]. Not named: relativistic physics against coordinate effect. Next test that can
  tell them apart: a gauge-invariant crossing measure in S1L (proper separation of lattice neighbours from the metric
  at the particles, or the sign of the proper-volume Jacobian), or a short GR member with zero shift; prediction
  first. N-z128 (same run, still going) checks the 5 per cent of N-z.
A2 stays FAILED as written (decision 0040 item 7).

## 2026-11-25 18:21 PST (lead of batch 23): a crossing measure that does not depend on the coordinates (A2X), before any reading

Why: S1L's first crossing (6.35 t_H, snapshot bracket 6.19-7.21) came from coordinate separations of lattice
neighbours along z and coordinate time read as cosmic time; the Gamma-driver shift moves the coordinates and the
1+log lapse slows the central clock, so the lag could be a coordinate effect (decision 0041 item 2).
Measure (new script `scripts/a2_invariant.py`, processors, existing snapshots of A-20261123-025907-97bab8d):
(i) the event: the Jacobian J = det(dx/dq) of the Lagrangian map on the particle lattice (centred differences,
periodic unwrap); a shell crossing is J <= 0 in some lattice cell. The sign of J is unchanged by any smooth spatial
coordinate change (J' = det(dy/dx) J, det(dy/dx) > 0), so the shift cannot move it; first snapshot with min J <= 0.
(ii) the clock: the dust's own proper time, bounded below on every worldline by tau_lb(t) = int_0^t alpha_min(t')
/ W_max dt' (alpha_min: column 16 of nrpic.hst, the lowest lapse anywhere; W_max from the largest |u_i| of the
snapshots with gamma^ij <= 1.5 delta^ij as a margin) and above by the coordinate time when alpha <= 1; the probe
particle's integrated proper time (column 15) as a cross-check. Converted as t_c = 2/3 + tau, t/t_H =
t_c / ((2/3) 6^1.5). The slicing offset of the initial slice against the synchronous one is ~ (2/5) zeta t_i,
below 0.01 t_H.
Prediction A2X [JUDGEMENT]: min J stays positive through the snapshot at 6.19 t_H and is negative at 7.21 t_H (the
same bracket as the z reader: the crossing at the centre is along a principal axis); the dust proper-time lower
bound at the last snapshot with J > 0 is above 5.0 t_H (the band's upper edge). If so, the lag is not a
coordinate effect of either the shift or the slicing: the dust worldlines live longer than the Zel'dovich time
without crossing, and the lag is in the relativistic evolution (physics or numerics; not named by this test).
Refuted if J first turns negative at a snapshot at or before 5.17 t_H (the z reader missed a crossing), or if
tau_lb at the last positive snapshot is below 5.0 t_H (the slicing could hide a timely crossing; then a short GR
member with geodesic slicing and zero shift is queued, prediction first, priority 2).
N-z128 (A-20261125-160633-e38d321, ended): AZ1's second clause, within 5 per cent of N-z (4.55 t_H), is read
with a2_compare.py in the same session.

### Outcome A2X (analyses A-20261126-022220-99b7be8, A-20261126-022338-0edc27c, A-20261126-022438-a08cc5f, A-20261126-022545-5af99fb; fig_a2x.png looked at)

- (i) HOLDS. det(dx/dq) on the lattice (forward and centred) stays positive through t = 60 (min 0.0011; 6.19 t_H on
  the coordinate clock) and is <= 0 in 134 cells at t = 70 (7.21 t_H): the same bracket as the z reader; no earlier
  crossing was missed by reading coordinate separations. The shift cannot move this event.
- (ii) AS WRITTEN NOT DECIDABLE (the bound is empty). The first run took W from the largest |u_i| of all snapshots
  (1.6e3, deep in the late collapse) and gave a bound of 0.07 t_H; the second, the running maximum (|u_i| 9.4 by
  t = 60); the third, only the 215 particles at the corners of the first-crossing cells: they carry covariant |u_i|
  up to 7.3 before crossing. Without gamma^ij at the particles (the snapshots hold x, u_i, m only) W is not bounded,
  and the "lower bounds" (0.58, 0.73 t_H) say nothing. Three runs of a defective bound are on record.
- Decided instead by the probe particle, the cross-check named before the reading: the code integrates the proper
  time of the particle nearest probe_x = (0.001, 0.001, 0.001), which is lattice point (32, 32, 32) at the origin and
  one of the 215 first-crossing particles (lattice distance 0; fourth run). Its proper time is 5.99 t_H on the last
  slice with J > 0 and 6.80 t_H on the first with J <= 0. On the dust's own clock the first crossing lies in
  (5.99, 6.80] t_H, above the band edge 5.0 and the Zel'dovich time 4.35. [VERIFIED as far as the code's proper-time
  integration of that worldline; that the probe is a crossing worldline was found after the run.]
- Consequence: S1L's lag is not a coordinate effect, neither of the shift (sign of J) nor of the slicing (proper time
  of a crossing worldline). It lies in the relativistic evolution or its data (physics or numerics; not named).
  No card member is queued for the coordinate question. A candidate to test, not a cause [JUDGEMENT]: at zeta_max
  0.3 the nonlinear relation between curvature and density (density contrast ~ e^(-2 zeta) times the linear one at
  the peak) lowers the physical first-axis eigenvalue below the coordinate 0.063 that the reference reads from
  snapshot 0; a member at half the amplitude would show a smaller lag if so (card, prediction first, next session).

### Outcome AZ1, second clause (N-z128; analysis A-20261126-022631-dafbb4f, fig_a2_compare.png with four curves looked at)

N-z128 (Newton, 128^3 Fourier mesh, same particles as N-z) first crosses along z at 3.62 t_H (bracket 3.59-3.73),
then x at 5.23, y at 8.54; N-z (64^3) crosses at 4.55. "N-z128 within 5 per cent of N-z" is REFUTED: the force
resolution of 64^3 (one cell per particle spacing) delayed the Newtonian crossing by 26 per cent. The converged
Newtonian time lies near or below 3.6 t_H, ahead of first-order Zel'dovich (4.35), as second-order ellipsoidal
collapse should (the batch-20 reading of N-z as "following Zel'dovich to 5 per cent" was a resolution accident).
So the GR lag is larger than stated in batch 20: S1L on the dust clock (5.99-6.80) against Newton at 128^3 (3.62) is
a factor 1.65-1.9. A2 stays FAILED as written (0040 item 7).

## 2026-11-25 18:35 PST (lead of batch 23): outcomes D1-D5 of P0L6 (chain A-20261125-044641-7d5bd16 closed: completed at t = 140, 4.87 card-hours over 8 jobs; analysis A-20261126-022753-f9e9c40; fig_job2_q.png, fig_line_trapped.png, fig_compare_ltb_P0L6.png looked at)

- D1 HOLDS: no guard stop to t = 140; the L2 norm of H changes by at most a factor 0.95 between records in t 1.5-6
  (Q1a repeated on six levels).
- D2 REFUTED: the x line first holds a trapped sphere at t = 136.0 (four levels: 132), not before 125; the outermost
  marginally trapped sphere at t = 140 has r = 0.103 (21 cells of level 6), R = 12.6, m = 6.28 against the four-level
  5.0 (26 per cent, outside 10). By the clause written before the run: the late trapping is the slicing (central
  lapse 3e-6 by t = 140), not the central resolution.
- D3 REFUTED, read from the status file only (decision 0040 item 3): 308 searches from t = 100.1 to 140.0, 307 not
  found (181 "iteration limit reached without convergence of the mass", 126 "mean radius negative") and ONE row
  "found" at t = 118.12. That row is not a horizon: area mass 562 (the line's trapped mass is ~6, and the line holds
  no trapped sphere before t = 136), mean coordinate radius 18.2 in a box of half-width 10, minimum radius -3.6
  (not a surface around the centre), mean expansion +2.1e5; the searches before and after it fail. It is a false
  acceptance of the mass-convergence test after a divergent flow. After t = 136, with a trapped sphere of 16-21
  level-6 cells on the line, every search stalls just outside it (mean radius 0.123-0.130, m 6.58-6.86, mean
  expansion +18 to +22): by the clause written before the run, the finder itself fails on this slice. Request to
  core (outbox): the false "found" and the stall on a resolved horizon, with the status file.
- D4 REFUTED: turnaround of r0 = 1.21 is 26 per cent late against B (four levels: 4.9) and of r0 = 0.91 82 per cent
  (8.6); shells r0 >= 1.5 stay within 1-4 per cent (0.95 per cent at 1.52). Neither improves; the inner shells are
  WORSE with two more levels, which no prediction anticipated. The clause written before ("then the inner error is
  the particles'") is the reading on record; not tested.
- D5 HOLDS: 58,500 steps (predicted about 57,000) and 4.87 card-hours (sacct over the 8 jobs; predicted 4-5.5).
C1 (ii) of G2 therefore stands as: the spherical LTB peak is followed to 1-4 per cent outside r0 = 1.5 on four and
six levels, trapped spheres appear on the line from t = 132-136 late in the slicing, and the horizon finder does
not find the periodic LTB horizon on a slice that resolves it (failure on record; request to core).

### A2X correction and check (18:40 PST, before running a2_probe_check.py)

Correction found by reading the source (athenak/src/particles/nrpic_io.cpp, NrpicProbe): the "probe" is a fixed
COORDINATE point and column 15 is the proper time of the normal observer there, int alpha dt, not of a particle. The
A2X outcome above called it "the probe particle"; that is wrong as stated. It is the dust's clock only if the particle
at the probe stays there with u_i = 0 (then W = 1 and dtau = alpha dt). For the peak centred at the origin the
reflection symmetry of the data should keep the central particle at rest at the origin.
Prediction PC [JUDGEMENT]: the particle nearest the probe at t = 0 (lattice point at the origin) stays within 1e-6 of
the probe point and has covariant |u_i| below 1e-6 at every snapshot to t = 70, while its lattice neighbours move
(|u_i| of order 0.01-1). Refuted if the offset or |u_i| exceeds 1e-3 before t = 70: then the probe clock is not a
dust clock and the A2X conclusion "(5.99, 6.80] t_H on the dust's own clock" is withdrawn (the shift-invariant
bracket of (i) stands, the slicing question reopens and a card member with geodesic slicing is the next test).

### Outcome PC (A-20261126-023551-f800cf5, fig_a2_probe.png looked at)

- The particle nearest the probe sits at the origin (lattice point (32, 32, 32)) and never moves: its offset from the
  probe point is 1.73e-3 = |(0.001, 0.001, 0.001)| at every snapshot to t = 70, and its covariant |u_i| stays below
  9e-13, while its neighbours reach |u_i| 3.9.
- PC's offset clause is REFUTED as written (1.73e-3 > 1e-3: I wrote it about the probe point, which lies 0.09 of a
  finest cell from the particle); its |u_i| clause holds. By the clause written before, the reading "(5.99, 6.80] t_H
  on the dust's own clock" taken from the probe column is WITHDRAWN.
- What stands without the probe column [VERIFIED, no judgement]: the central particle is at rest (W = 1 to 1e-24), so
  its proper time is int alpha(0, t) dt >= int alpha_min dt = 58.03 at t = 60 (column 16 of nrpic.hst; the A2X runs),
  i.e. >= 5.99 t_H, on the last slice on which no lattice cell has crossed; and it is a vertex of the cells that
  have crossed by t = 70 (the 215-particle corner set). So the first crossing occurs at a dust proper time above
  5.99 t_H on a crossing worldline: the lag against 4.35 (Zel'dovich) and 3.62 (Newton at 128^3) is not a
  coordinate effect. The upper end of the bracket (6.80) rests on the probe column and is not claimed.

## 2026-11-25 19:25 PST (batch 24): A2H, the relativistic member of S1L at half amplitude (decision 0043 item 1(d)), prediction before any run

Why: S1L (mu = 0.3, e = 0.2) first crosses at a dust proper time above 5.99 t_H (central particle at rest, int alpha_min
dt; outcome PC above) and in (6.19, 7.21] t_H on the coordinate clock (J sign, A2X (i)), against Newton at 128^3 3.62
(bracket 3.59-3.73, N-z128) and first-order Zel'dovich 4.35. The one candidate named (A2X outcome, decision 0043 1(d)):
the nonlinear relation between the curvature perturbation and the density contrast at zeta_max = 0.296. This member
halves the amplitude and changes nothing else. A2 stays FAILED as written whatever it shows.
Member S1L-h: data `make_peak_ic.py --mu 0.15 --e 0.2 --eps-i 1 --n 64 --nfilter 2 --compensate` (the S_mu0.3 command
of A-emd-pbh-20261115-155802-9a6596f with mu halved); deck `inputs/peak_leak.athinput` unchanged (gauge, mesh, deposit,
finder with diagnostics = true, cfl 0.5); overrides only id_file, particle_file, time/tlim = 220, particles/snap_dt =
5.0 (0.51 t_H between snapshots instead of 1.02) and output7/dt = 30 (a restart file every ~9 min of wall time instead
of ~15). Executable: card build of release core-v0.7 (S1L ran v0.6; v0.7 is byte-identical on the periodic set
without new options, tracks/core/RELEASE-v0.7.md; dt_gauge is absent, so the step is S1L's). Read by the same scripts
(a2_invariant.py for the sign of det(dx/dq), a2_crossing.py for the axis, a2_probe_check.py for the central particle).
Scalings used [VERIFIED as arithmetic on the quantities named; the self-similarity is BACKGROUND]: Zel'dovich first
axis lambda_z = 0.063 at a = 1 for mu = 0.3, first order in mu, so 0.0315 here: a_sc doubles and t/t_H = (a/6)^1.5
grows by 2^1.5 = 2.83. Newtonian ellipsoidal collapse of the same shape (e unchanged) in EdS is self-similar in
lambda a, so the Newtonian crossing scales by 2.83 too.
- Linear relation (no nonlinear term; GR = Newton at these scales): 2.83 x 3.62 = 10.2 t_H (bracket 10.15-10.55,
  N-z128 scaled); first-order Zel'dovich 2.83 x 4.35 = 12.3 t_H.
- Candidate (its effect on the growing amplitude is a factor g with ln g proportional to zeta_peak, so halving mu
  takes the square root of the lag in a): S1L's lag in a against Newton is (5.99/3.73)^(2/3) = 1.37 to (7.21/3.59)^(2/3)
  = 1.59; at half amplitude 1.17-1.26 in a, 1.27-1.42 in t: crossing at 12.9-14.9 t_H (central 13.6).
  Two versions of the factor, for orientation: the data's own conformal factor (psi_dict^4 = 1 + 1.2 zeta at the
  peak, id.json max_abs_psi_dict_minus_1 = 0.078; the solve changes psi by 0.011) gives a lag in a of 1.36 at full
  amplitude (crossing 5.7 t_H, just below S1L's lower bound 5.99) and 1.18 at half (13.1 t_H, inside the band); the
  literal gradient-expansion factor e^(-2 zeta_peak) = 0.553 (id.json ge: delta_cmc/((5/3) delta_N) = 0.551) would
  put S1L at 3.62 x 0.553^(-1.5) = 8.8 t_H and is already contradicted by S1L's coordinate bracket (<= 7.21).
- Null (a lag independent of the amplitude, e.g. a self-similar numerical delay such as the source smoothing of one
  particle per root cell with deposit_adaptive, ppc 2; one force cell per particle spacing delayed Newton by 26 per
  cent, N-z vs N-z128): lag unchanged, crossing at 2.83 x (1.61-2.01) x 3.62 = 16.3-21.2 t_H.
Prediction A2H [JUDGEMENT]: S1L-h first crosses along z at the centre, and the crossing bracket (last snapshot with
min J > 0 to first with J <= 0, on the coordinate clock t/t_H = (1 + 1.5 t)/6^1.5, with the central particle's
proper-time lower bound int alpha_min dt) lies inside [12.5, 15.2] t_H; no horizon is found and the lapse at the
centre stays above 0.8 up to the crossing (top-hat collapse of the compaction shell at 2.83 x 16.1 = 45 t_H).
Refuted toward an amplitude-independent lag if the bracket lies entirely above 15.6 t_H (then the candidate is out
and a numerical delay is the next candidate, to be tested at a finer deposit); refuted the other way if it lies
entirely below 11.8 t_H (the lag falls faster than first order in zeta); undecided if it straddles 15.2-15.6 or
11.8-12.5. What a hold does not separate: any effect first order in the amplitude, e.g. a relativistic (aH/k)^2
term (but (aH/k)^2 = 1/a is 0.04-0.06 at S1L's crossing, so it needs a coefficient near 8 to give S1L's lag).
Cost [JUDGEMENT from S1L's segments, chain/seg003 and seg005: 0.18-0.20 s a cycle at dt = 0.00977]: ~22,500 cycles to
t = 220, ~70 min of card time plus start-up: two segments, cap 2.0 card-hours, priority 2 (G2 waits for it, 0043).
Data build prediction D-h: the solve converges as at mu = 0.2 and 0.3 (residual ~1e-11), zeta_max 0.148,
delta_N_max 0.059 (half of 0.1176), jacobian_min ~0.94, change of the solve c between 0.03 and 0.14. Smoke test
prediction SM-h (processor build v0.7, 4 cycles): starts, reads 262144 particles, first dt 3.36e-3 within 5 per cent
(S1L's first step), finite fields, no guard stop. Refuted otherwise; then nothing is queued.

### Outcomes D-h and SM-h (runs A-20261126-032537-f1060e7 and A-20261126-032800-48a3825, closed completed), and the queue entry

- D-h: the solve converges (outer 17, Hamiltonian residual 5.0e-12, momentum 1.6e-11); zeta_max 0.1482, delta_N_max
  0.0588 (0.500 of mu = 0.3's 0.1176), jacobian_min 0.941, mass 0.979-1.488 of the mean, alpha_min 0.908. All as
  predicted except the change of the solve: c = 0.014, below the predicted [0.03, 0.14] (REFUTED as written; c falls
  faster than linearly in mu, 0.137 at 0.3, 0.031 at 0.2, 0.014 at 0.15). For A2H's orientation numbers:
  max_abs_psi_dict_minus_1 = 0.0414, ge delta_cmc_max_at_start = 0.0728 = 0.743 x (5/3) delta_N (e^(-2 x 0.148) = 0.744).
- SM-h: starts on the v0.7 processor build, reads 262144 particles, four cycles to t = 0.011 with finite fields and no
  guard stop; the finder ran at cycles 0 and 2 with diagnostics (status file: not found, "mean radius negative", no
  horizon, as it should be); alpha_min 0.907 -> 0.974 over the four steps (the relaxation of the excess lapse, as S1L).
  First step 2.83e-3 against the predicted 3.36e-3 within 5 per cent: REFUTED as written (16 per cent smaller). Reading
  [JUDGEMENT]: the first step is set by the light speed at the peak, alpha psi^-2, which is larger when the peak is
  shallower (0.908/1.041^2 = 0.84 against 0.805/1.079^2 = 0.69, ratio 1.21; measured step ratio 1.19); it only
  lengthens the start-up phase before the step reaches 0.5 dx and does not change the deck. Not a reason to hold the run.
- Queued: q0068 `a-s1l-half` (priority 2, chain, --gpu-hours 2.0 = two segments, card build v0.7, argv in the queue
  entry). Read with a2_invariant.py, a2_crossing.py and a2_probe_check.py on its run directory (`--reference 12.3
  --band 12.5 15.2` for a2_invariant's band; the clock as for S1L), then A2H is judged here.

### Outcome A2H (S1L-h closed completed: A-20261126-125306-0653547, 2 jobs, 1.18 card-hours; analyses A-20261126-213147-f274b2e, A-20261126-213150-1441107, A-20261126-213153-563fb0a, figure reruns with the member's own band and labels A-20261126-213414-261dd64, A-20261126-213459-0ce5ee6; fig_a2x.png, fig_a2_crossing.png, fig_a2_probe.png looked at) - 2026-11-26 13:36 PST, lead of batch 28

- Shift-invariant measure (sign of det(dx/dq) on the particle lattice, forward and centred differences agree): min J
  > 0 at t = 135.009 (t/t_H = 13.85; min J 0.0033) and <= 0 at t = 140.009 (14.36; 2 cells, the first-crossing cell
  at the origin). Axis reading: z crosses first, bracket (13.85, 14.36] t_H, interpolated 14.27; x crosses at
  (19.97, 20.48], y not by t = 220. The central particle stays at rest at the origin (|u_i| <= 5.6e-12, offset
  1.7e-3 from the probe point), so its proper time on the crossing slice is >= int alpha_min dt = 14.07 t_H.
  Horizon status file peak.horizon_status_0.txt: 288 searches, none found. alpha_min at the crossing 0.921 (> 0.8).
- A2H HOLDS: the crossing bracket (13.85, 14.36] t_H, and the dust-clock bound 14.07, lie inside [12.5, 15.2];
  the first crossing is along z at the centre; no horizon; lapse above 0.8. The lag against the scaled Newtonian
  crossing (2.83 x 3.62 = 10.2 t_H) is 1.38 in time, 1.24 in a: inside the predicted 1.17-1.26 (the square root of
  S1L's lag in a). Neither refutation (above 15.6: an amplitude-independent numerical delay; below 11.8) occurred.
- What the hold shows [JUDGEMENT]: the relativistic lag falls with the amplitude as an effect first order in the
  curvature perturbation does; an amplitude-independent numerical delay (one particle per root cell, deposit
  smoothing) is disfavoured as the main cause. It does not separate the nonlinear zeta-delta relation from other
  effects first order in the amplitude (written before the run). A2 stays FAILED as written (decision 0043 1(d)).
- Figure defects found and fixed in this session: a2_invariant.py and a2_crossing.py drew S1L's band, reference
  and title for every member (the numbers in the JSON used the arguments); both now take --band, --reference,
  --label (commit cfb6a17b2); a2_probe_check.py still titles its figure "S1L" (cosmetic, left).

## 2026-11-26 15:35 PST (lead of batch 31): FP, the core-v0.8 finder with polishing on the restart files of P0L6 and S1L (condition (b) of decision 0047), prediction before any run

Gate G2 of this track is NOT passed (coord/GATES.md, decision 0047, stage/G2/GATE_REVIEW.md). Condition (b): the finder
finds the trapped surface on the existing restart files of the periodic chain and of the triaxial run without a false
acceptance. Test FP: each restart file (P0L6 A-20261125-044641-7d5bd16 rst 16 at t = 130.0 and rst 17 at t = 140.0;
S1L A-20261123-025907-97bab8d rst 18 at t = 210.0 and rst 19 at t = 220.0; all written by build_gpu_v06) is continued
for ONE cycle on the processors with the threaded core-v0.8 build (scratch/core/exe/core_nrpic_v08/athena_cpu_omp,
3 threads) and searched at the end of that cycle by several horizons at the box centre (script
scripts/finder_probe_box.py, method of tracks/core/analysis/restart_finder/finder_probe.py):
- "v08 rule": mass_tol 1e-5, polish_iterations 100, flow_iterations 400, diagnostics, from the deck's start radius
  (P0L6 0.15, S1L 0.6): what a continued run with the recommended setting does;
- the same from the radius of the trapped region (P0L6: 0.103, the line's outermost marginally trapped sphere at
  t = 140, D2 outcome, and 0.012, the verifier's outermost tracked trapped shell at t = 140; S1L: 0.2 and 0.1);
- the same with flow_iterations 4000 (does the flow converge slowly, or not at all?);
- the tight rule, mass_tol 1e-9, 4000 iterations, no polishing, from the trapped radius;
- a sphere scan: flow_iterations 1 at a list of radii, which writes the surface integral of the expansion of the round
  coordinate sphere itself (column 10 of the status file, first flow iteration evaluates the start sphere; read in
  fastflow.cpp FastFlowLoop). Negative = the round sphere is trapped in the finder's own measure.

Predictions (written before the first probe):
- FP0 The restart files of build_gpu_v06 are read by the v08 processor build (v0.7/v0.8 pass, v0.6->v0.7 passed in F2).
  Refuted if the setup fails; then the v0.6 processor build without polishing is used.
- FP1 The v08 rule from the deck radius still ends with reason 6 at all four dumps. Reason: polishing acts only AFTER
  the mass rule is first met; reason 6 means the rule was never met in 400 iterations, so polishing cannot change it
  [JUDGEMENT from the interface text, section 2]. Refuted if any of them is found.
- FP2 No search is accepted with a positive mean expansion or a mean radius above 1 (no false acceptance). Refuted by
  any found = 1 row with hmean > 0 or meanradius > 1.
- FP3 P0L6, sphere scan at t = 140: the round sphere's expansion integral is negative between about 0.02 and 0.10 and
  positive at 0.12 and beyond (the line's trapped sphere, D2: outermost marginal sphere r = 0.103, m = 6.28); at
  t = 130 negative nowhere or only inside 0.03 (the line holds no trapped sphere before 136; tracked shells trapped
  from 122 at r ~ 0.01). Refuted if positive at every radius at t = 140 (then the finder's own expansion and the line
  reader disagree, a defect of one of them), or negative out to 0.12 or beyond.
- FP4 P0L6, searches started inside the trapped region (0.103, 0.012) with 4000 iterations: the flow moves outward to
  r ~ 0.10-0.13 and stalls with reason 6 again, the mass changing by more than 1e-5 per iteration to the cap. That
  would place the defect in the flow itself on this slice (core's item). Refuted if any of them is found with a mass
  between 3.47 (largest tracked trapped shell) and ~7 and a mean radius 0.08-0.13: then the finder works given a
  start radius and enough iterations, and condition (b) is met for P0L6 by a rule that the deck can carry.
- FP5 S1L at t = 210 and 220: whether any round sphere is trapped is open (nothing has read S1L's slice); prediction:
  the sphere scan is negative for some radius below 0.3 (S1L's searches stall with mean radius 0.53 and m ~ 20, the
  same pattern as P0L6 outside its trapped sphere), and the searches end with reason 6 as in P0L6. Refuted if the
  scan is positive at every radius (then S1L has no trapped round sphere and its "stall" is a different situation).
What happens next either way: if FP4 is refuted, the probe rule goes into the decks of the G3 box runs and S1L's
S1-S3 are judged with it; if it holds, the smallest reproducer (restart file, deck, expected radius) goes to core
(outbox), whose source session after 2026-11-27 takes it (decision 0047 item 4).

### Outcome FP (run A-20261126-233542-fd9f9f0, completed, 4 dumps, 82 searches; fig_finder_probe_box.png looked at) - 15:42 PST

- FP0 HOLDS: the v08 processor build reads the restart files of build_gpu_v06 (P0L6 and S1L), one cycle each, exit 0.
- FP1 HOLDS: the recommended v08 rule (mass_tol 1e-5, 100 polishing, 400 iterations) from the deck radius ends with
  reason 6 at all four dumps (P0L6 130: m 5.96, r 0.107; 140: m 6.86, r 0.130; S1L 210: m 19.5, r 0.53; 220: m 20.1,
  r 0.53). Polishing does not touch reason 6, as read from the interface text.
- FP2 HOLDS (no false acceptance): 2 of 82 searches are found, both at P0L6 t = 140 on the trapped surface (below). The
  script's automatic flag "hmean > 0" marks the one from 0.15 (surface integral of the expansion +0.18): too strict a
  flag, since a converged surface has an integral near zero of either sign (the other has -0.18; round spheres next to
  it have -2.8 at r = 0.10 and +4.3 at 0.11). At P0L6 t = 130, where no round sphere is trapped, the six searches end
  reason 6 or reason 4 (flow shrinks through the centre): nothing accepted.
- FP3 HOLDS: P0L6 t = 140, the round sphere's expansion integral is negative from r = 0.03 to 0.10 (-22, -26, -21,
  -9.6, -2.8) and positive at 0.02 (+10) and from 0.11 (+4.3) outward; at t = 130 positive at every radius (minimum
  +20 at r = 0.07). The finder's own expansion agrees with the line reader (trapped from 136, marginal sphere 0.103).
  [JUDGEMENT] The verifier's "tracked shells trapped in the code from t = 122.2" (R < 2 M with M of the exact shell)
  is not a trapped surface of the slice: at t = 130 no round sphere at r 0.005-0.5 is trapped.
- FP4 REFUTED for P0L6: with 4000 flow iterations the v08 rule FINDS the horizon at t = 140, from 0.15 after 3444
  iterations (area mass 6.309, mean radius 0.1042) and from 0.103 after 915 (6.298, 0.1037); the tight rule 1e-9 ends at
  its cap on the same surface (6.303, 0.104, integral -0.0017). Against the line's marginal sphere (6.28 at 0.103,
  outcome D2): +0.3 to +0.5 per cent in mass. Area mass 6.3 is above the largest tracked trapped shell's 3.47. So
  condition (b) is MET for P0L6 at t = 140 by a setting the deck can carry (flow_iterations_0 = 4000 with polishing):
  the card run's failure was the iteration cap of 400, not a stall of the flow. From 0.012 the flow runs through the
  centre (reason 4): a start inside the trapped band's inner edge (0.02-0.03) does not work.
- FP5 HOLDS: S1L has trapped round spheres: integral negative for r 0.05-0.12 at t = 210 (-17, -54, -14) and 0.03-0.16
  at t = 220 (-19, -30, -84, -43, -2.2), positive at 0.2 and beyond. But every S1L search fails (reason 6) also with
  4000 iterations: from 0.1 the flow ends at r 0.134 (t = 210, m 9.77, integral -3.1) and 0.159 (t = 220, m 10.66,
  -3.9), from 0.2 at 0.145 / 0.163 (+4.8 / +1.7), from 0.6 at 0.18 / 0.19; the tight rule 1e-9 ends at 0.153 / 0.167.
  The flows close in on a surface near mean radius 0.15-0.17 (m ~ 10-11) from both sides without meeting the mass
  rule in 4000 iterations. Condition (b) is NOT met for S1L.
- For S1L's prediction S2 of card job 2 ("an apparent horizon is found between 10 and 22 t_H"): t = 210 is 21.5 t_H
  (t_H = 9.78 on this deck's clock, 220 = 22.5 t_H): a trapped round sphere exists at 21.5 t_H, so a horizon has formed
  by then, but none is FOUND; S2 as written stays refuted (gate review G1).

### FPb, predictions before the second probe (15:45 PST)

Run FPb (same script, sets S1Lscan, S1Llong, P0L6scan; 2 jobs x 2 threads, beside C3-F on one core):
- FP6 S1L's first trapped round sphere appears in (190, 210]: no negative expansion integral at r 0.02-0.3 on the
  restart files at t = 150, 170, 180, 190; negative somewhere at 200 or only at 210. Basis: the trapped band widens
  from 0.38 dex at 210 to 0.73 dex at 220, so it opened some 5-10 time units before 210 [JUDGEMENT, linear
  extrapolation]. Refuted if negative at 190 or earlier.
- FP7 A search of 12000 iterations from 0.16 at t = 220 converges (found) at mean radius 0.15-0.19 with area mass
  10.5-11.5. Refuted if reason 6 again: then the flow on S1L's slice does not converge (core's item, with this file as
  reproducer).
- FP8 P0L6 at t = 120.0 (just before the tracked 'trapped in the code' time 122.2): no round sphere trapped at r
  0.01-0.13. Refuted if negative anywhere.

### Corrections and judgements left open (batch 31, from the gate review C19 and VERIFIER.md section 4)

- A2X (ii) correction (second verifier, finding 1): the particle snapshots of S1L and S1L-h carry each particle's proper
  time (72 bytes a particle; nrpic_io.cpp 1115-1117, read by the verifier), so the dust clock of the first-crossing cell
  is in the files: S1L 5.993-6.002 t_H on the last uncrossed snapshot, 6.835-6.943 on the first crossed, i.e. the first
  crossing lies in (5.99, 6.94] t_H on the dust's own clock; S1L-h (13.68, 14.17] (verifier run
  A-20261126-223151-8310871 [number of the verifier, read by it from the snapshots; not recomputed here]). "Not
  decidable" in outcome A2X (ii) and "the particle files hold x, u_i, m only" (HANDOFF trap) were wrong; withdrawn.
- S1-S3 of S1L's card job 2 (2026-11-21 23:15Z), judged from the history and the status file
  (A-20261126-234332-ec02d47; fig_s1l_s123.png looked at: the smallest lapse falls through 0.3 at t = 137.7 and levels
  off at 0.11 from t ~ 190; E_max over the mean deposit passes 1e3 at t = 127.3, peaks at 1140 near t = 135 and falls
  to ~140 by t = 190):
  - S1 HOLDS: the relaxed lapse carried the run to t = 220 (22.5 t_H) without a guard stop.
  - S2 REFUTED as written: no apparent horizon was FOUND in 314 searches to t = 219.9. A trapped round sphere exists on
    the restart files at t = 190 (FPb), 210 and 220 (FP), and the v0.8 finder finds the horizon at t = 220 from 0.16
    (m 10.73, r 0.161); so a horizon formed before 19.4 t_H, inside S2's window, but the run's finder did not find it.
  - S3 HOLDS: the central lapse fell below 0.3 (t = 137.7) and E_max past 1e3 of the mean (t = 127.3) before any
    horizon was found, and before the first trapped round sphere on the restart files (t <= 190; dated by FPb).

### Outcome FPb (run A-20261126-234232-84f3e98, completed, 8 dumps; figure redrawn with one colour per dump in A-20261126-234818-3c83420 after the first drew four dumps in black; replot attempt A-20261126-234811-9e42dae failed on a required --exe, kept; FPb/fig_finder_probe_box.png looked at) - 15:51 PST

- FP6 REFUTED (narrowly): S1L's first trapped round sphere appears in (180, 190], not (190, 210]. Smallest expansion
  integral of the round spheres r 0.02-0.3: t = 150 +81 (r 0.02), 170 +14.6 (0.08), 180 +0.62 (0.08, marginal), 190
  -16.3 (0.08; negative at 0.05 and 0.08), 198.7 -28.2, 200 -30.5. In units of t_H = 9.78: first trapped round sphere
  in (18.4, 19.4] t_H. A non-round trapped surface may exist earlier: the round-sphere test is sufficient, not necessary.
- FP7 HOLDS: from 0.16 at t = 220 the v0.8 rule with a cap of 12000 converges after 1927 iterations, area mass 10.73,
  mean radius 0.161, expansion integral -0.63 (inside the predicted 0.15-0.19 and 10.5-11.5). The S1L horizon is found
  given a start radius near it; from 0.1, 0.2, 0.6 with 4000 iterations it was not (FP5).
- FP8 HOLDS: P0L6 at t = 120.0 has no trapped round sphere (integral +33 to +134 at r 0.01-0.13): with FP3 (t = 130
  none, t = 140 trapped from 0.03 to 0.10) the first trapped sphere of P0L6 lies in (130, 140], as the line said (136).
Condition (b) of decision 0047 after FP and FPb: P0L6 found at t = 140 from the deck's start radius with 4000
iterations (3444 used); S1L found at t = 220 only from a start radius near the surface; no false acceptance in 82 +
57 searches; the false acceptance of the card run at t = 118.1 untested (no restart file). Request to core updated
(outbox, batch 31).
