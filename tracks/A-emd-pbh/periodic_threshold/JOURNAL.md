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
