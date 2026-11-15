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
