# JOURNAL of the package window (E-stoch-inf, wave 3 round 1)

Sensitivity of the USR spectrum to the window function: test L9 of
`../codebase/DESIGN_REVIEW.md` 8.1, the second G2 criterion of the track sheet ("sensitivity
to window-function parameters", `coord/CHARTER.md` 9.8). Window
W = (1 + tanh[s ln(sigma a H/k)])/2 (`coord/INTERFACES/scalar_field.md` 7.3), options
`<scalar_field> noise_sharpness` (s) and `noise_sigma` (sigma); production s = 5, sigma = 1
(`../usr/inputs/usr_256.athinput`, lines 74-75). Scan: (s, sigma) = (5, 1) baseline, (2.5, 1),
(10, 1), (5, 0.5), (5, 2), USR at 128^3 with nmax2 = 1024 (k_max = N/4 = 32 dk).

## Entry 0, 2026-11-20 22:20 UTC: what was read, and what the papers and the code say

- P1 (arXiv:2512.14649 v2, `PRD_v2.tex`) on the window [VERIFIED at the source]:
  line 177, W_k with W_0 = 1, W -> 0 as k -> infinity, a steep drop at k = sigma a H, "the step
  function is a common choice but smoother functions can also be envisaged"; line 503-506, the
  tanh window with s = 5.0 "an arbitrary sharpness parameter", footnote: "This should not have
  an impact on the result in the late-time limit, as long as a window follows requirements such
  as those defined in [Winitzki00]. However, for a given discrete scheme, not all windows are
  suitable. In particular the sharpness should be appropriate for the time stepping and for
  keeping all terms within perturbation theory."; line 507, a smooth window with Fourier-space
  draws is non-Markovian noise; line 519, "The coarse-graining is fixed to sigma = 1 for all
  scenarios"; lines 724-730, at most one discrete mode per step needs theta < n sigma/(2 pi)
  in their box (L = 2 pi/(sigma H*)), "more constraining ... only on super-Hubble cutoffs
  (sigma < 1)". P1 has no window scan. SPEC 3 and 7.3 cite arXiv:2606.14853 (BZ) for the
  freezing criterion only; it has no statement on the window of the stochastic sources
  (SPEC 7.3 is what this package uses from it).
- Our box stays 2 pi for every window (the task fixes the lattice), so changing sigma moves
  the crossings k = sigma a H by ln sigma in N instead of rescaling the box. Mode spacing per
  step at the last crossing: Delta k_sigma/dk = k_max H dt = (N/4)(theta 2 pi/N) = pi theta/2
  = 0.39 for every sigma [JUDGEMENT: derived from k_sigma = sigma a H, dt = theta dx], so
  P1's condition holds for all five windows.
- Initial slice and window [VERIFIED by reading the source of the executable,
  `git show a58e95b6:athenak/src/scalar_field/scalar_field_slice.cpp` lines 128-143 and
  `scalar_field_noise.cpp` lines 126, 160, 546-555]: the slice places A = W(N*) R and
  B = W'(N*) R + W(N*) R' per shell with `nopt.sharpness` and `nopt.sigma`, the same members
  the sources use (read from `noise_sharpness`, `noise_sigma`), and a, H of the lockstep
  background at N*. So the slice at N* is the coarse-grained linear state of each window,
  including the modes that are already in at N* (for sigma = 2 the shell k = dk is in to
  W = 0.999 and k = 2 dk to 0.5). Consistent with SPEC 5.3 for every window.
- In linear theory the sources make R^NR_k(t) = W_k(t) R_k(t) alpha_k exactly (P1:173-218,
  SPEC 2.1). Once every shell is through its window the linear prediction does not depend on
  (s, sigma): at N_f the smallest argument is x = 2.5 ln(0.5 x 0.9518 x e^10/32) = 14.5
  (s = 2.5, sigma = 0.5, k = 32 dk, H(N_f) = 0.9518 from `../usr/results/landmarks.csv`), so
  1 - W < 3e-13 [JUDGEMENT: arithmetic]. Any window dependence of the spectrum at N_f is
  therefore numerical (dispersion of the stencils, time step) or nonlinear.
- Crossings (W = 1/2 at k = sigma a H) against the USR phase (onset cN = 2.5234, aH = 11.894;
  end cN = 6.5503, aH = 665.8; `../usr/results/landmarks.csv`): shells with k < 11.89 sigma
  cross before the USR onset (k <= 11 dk for sigma = 1, <= 5 for 0.5, <= 23 for 2); all
  shells up to 32 dk cross before the USR end for every sigma (the last at about
  cN = ln(32/sigma) + 0.05: 3.5, 4.2, 2.8). The reference of entry 2 computes these exactly.
- 128^3, nmax2 = 1024: rms of W R at N_f 0.494 (ensemble lattice sum, var_cg = 0.24402 at
  cN = 10, `../usr/results/usr_reference.json`, key lattice_variance.N128_n1024, run
  E-20261119-143905-f2bcde3).

## Entry 1, 2026-11-20 22:30 UTC: predictions for the card job (written before it was submitted)

Runs (`inputs/card_window.list`, executable `scratch/core/exe/core_scalar-2/athena_gpu`,
a58e95b): USR 128^3, nmax2 = 1024, Courant 0.25, tlim = N* + 10, dump_dt = 0.5, for the five
windows with noise_mode_scale = +1 and -1 (b = (5, 1), s25, s10, g05, g2); slow-roll contrast
at 64^3 (nmax2 = 256, tlim N* + 8) for the five windows at +1 and the baseline at -1.
Odd part O = (R(+1) - R(-1))/2 (first + third order), even part E = (R(+1) + R(-1))/2 (second
order). Reference: ref_w = L^-3/2 W_w R alpha with the continuum MS mode R of the run's mode
file (as in `../usr/scripts/analyse_runs.py`). Error of a mode at N_f: |O/ref - 1|; in time:
|O - ref|/max_t|ref| (U-A2's normalisation). Thresholds fixed here; numbers marked
[JUDGEMENT] are estimates, not measurements.

- W1 (U-A2 per window). For every window the odd part at N_f agrees with its own reference
  within 0.02 for every mode with k <= 16 dk (k_max/2). Expected size 1e-4 to 1e-3 (USR 32^3:
  2.3e-4 at 8 cells per wavelength, `../usr/README.md`; SR Q128: 9.9e-5, `../ladder/README.md`).
  Expected order of the error at 8 < k <= 16: sigma = 2 > 1 > 0.5, and s = 2.5 >= 5 >= 10
  [JUDGEMENT: a mode put in at k/aH = sigma oscillates on the grid for about sigma - 1 radians
  before it exits, so the phase error of the stencils, delta k/k = 1.9e-4 at k dx = pi/4,
  grows with sigma; a wide window (s = 2.5) puts the tail in earlier]. For all modes up to
  32 dk (4 cells per wavelength, delta k/k = 0.9 percent) the largest error is expected at
  0.3 to 3 percent, largest for sigma = 2. Refuted if any window exceeds 0.02 for k <= 16 dk,
  or if the sigma ordering at 8 < k <= 16 is reversed (sigma = 0.5 worst).
- W2 (second order). The even part at N_f relative to the odd part (rms over modes) lies
  between 1e-5 and 1e-3 for every window, although the rms of W R is 0.49; per mode
  |E|/|ref| at N_f below 1e-2 for every mode. Reason [JUDGEMENT]: the usr runs gave 2e-5
  at R_rms 0.02 and 0.07, and the nonlinear terms of the evolved system act on the field-space
  amplitude delta phi = (Pi_b/H) R and on delta K = 3 eps1 H R, which stay tiny because
  eps1 falls to 1e-12 in USR, not on R itself. So at 128^3 the second-order part is not
  visible in the per-mode comparison: it lies at or below the first-order discretisation
  error (W1) and is seen only in the mirrored pair. It would become visible at k <= 16 dk
  only if E/O exceeded about 1e-3. Refuted if E/O (rms) at N_f is above 1e-2 or below 1e-6
  for the baseline.
- W3 (shift between windows). (a) At N_f the shell power shift P_w/P_b - 1 of the realisation
  (shell mean of |R|^2, odd parts where both runs have mirrors, else the +1 runs) equals the
  linear shift (zero to 3e-13) within 2e-3 for every shell k <= 16 dk, for every window;
  above 16 dk within 5 percent. (b) During the passage (every dump with 0 < cN < 4.5) the NR
  shift per mode, R_w - R_b, equals the linear shift ref_w - ref_b within
  0.02 max_t|ref| for k <= 16 dk; the linear shift itself is of order max_t|ref| there
  (the windows put a mode in up to ln 2 e-folds apart), so this is resolved. Refuted if (a)
  or (b) is exceeded at any such shell or mode.
- W4 (super-horizon shells). Shells that crossed the window before the USR onset in both
  windows of a pair (k < 11.89 min(sigma_w, sigma_b) dk) show no dependence on s or sigma at
  N_f beyond 1e-3 per mode in |R_w/R_b - 1|, and no trend with s or sigma above the scatter.
  Refuted if any such mode exceeds 1e-3, or if the shifts of those shells follow sigma or s
  systematically above 3 times their scatter.
- W5 (one-point). The rms of W R of the realisation at N_f (sum over the modes of the box,
  NR odd part) is the same for all windows within 2 percent and within 2 percent of the
  reference rms of the same realisation (lattice sum with the run's alpha); at intermediate
  dumps it follows each window's reference within 2 percent of its value. Refuted otherwise.
- W6 (constraints). The records <|H|/[H]> and <|M|/[M]> after the last crossing (cN > 5)
  agree between the windows within a factor 2 (the same modes are present); during the
  entry they are shifted in N by about ln sigma. Refuted if the late records differ by more
  than a factor 2.
- W7 (background). Box means of phi, Pi, K of all windows equal those of the baseline within
  1e-6 relative at every recorded cycle (the window changes only the perturbations; the
  backreaction on the means is second order and below 1e-3 even for the baseline, U-A1).
  Refuted if any window differs by more.
- W8 (slow-roll contrast at 64^3). Every window: odd/own reference within 0.02 for
  k <= 8 dk at N_f (expected 1e-4); shell power shift against the baseline below 1e-3 for
  k <= 8 dk; even/odd of the baseline below 1e-4. Refuted otherwise.
- Cost. USR 128^3 runs 2 to 3 min each on the card, the job 20 to 30 min (0.33 to 0.5
  card-hours); the wall limit is 30 min so that the cap of 0.5 card-hours holds. Refuted
  (and recorded) if a run takes more than 3.5 min.

Submitted 2026-11-20 22:24 UTC as run E-20261120-222424-0eb754b (Slurm job 4740), 16 runs,
`--gpu-hours 0.5 --wall 00:30:00`. The wall limit is 30 min, not the 45 min of the package
brief, so that the cap of 0.5 card-hours holds even if the job runs to its limit; the list
puts the six runs the package needs first and the four extra mirrored runs last.

## Entry 2, 2026-11-20 22:32 UTC: outcome of the linear reference (step 1)

Run E-20261120-222802-bffb812 (`scripts/window_reference.py`, 2 cores, 25 s); outputs copied
to `results/reference/` (`reference_{usr,sr}.json`, `shells_{usr,sr}.csv`) and
`fig/fig_ref_{usr,sr}_{windows,crossing}.png` (both looked at). USR 128^3, nmax2 = 1024: 854
shells, 68532 modes of the hemisphere.

- Self-check: the ensemble rms of W R at N_f for the baseline is 0.49398, the square root of
  the usr package's lattice variance 0.24402 (run E-20261119-143905-f2bcde3): same sum,
  independent code. The realisation of the runs (seed 20261115) has 0.49460.
- Linear prediction at N_f does not depend on the window: max over shells of 1 - W(N_f) is
  8.2e-15 (s = 2.5), 0 to rounding for the others; the linear power shift against the
  baseline is at most 1.6e-14 (USR) and 8.9e-12 (SR at N* + 8, s = 2.5). So every window
  dependence of the NR spectrum at N_f is numerical or nonlinear (entry 0 confirmed).
- Initial slice at N* per window (W of the shells |n|^2 = 1, 2, 3, 4; shells with W > 1e-3;
  rms of W R in the slice): b 0.5, 0.030, 0.0041, 0.00098; 3; 5.18e-6. s25 0.5, 0.150, 0.060,
  0.030; 13; 5.41e-6. s10 0.5, 0.00098, 1.7e-5, 9.5e-7; 1; 5.17e-6. g05 0.00098, 3.1e-5,
  4.0e-6, 9.5e-7; 0; 1.01e-8. g2 0.999, 0.970, 0.808, 0.5; 13; 1.57e-5. Together with the
  source reading of entry 0 the slice of each run is its window's coarse-grained state.
- Crossings (W = 1/2; W = 0.95 of the last shell): b, s25, s10 last at cN = 3.515 (0.95 at
  3.810, 4.104, 3.662); g05 4.208 (4.503); g2 2.821 (3.116). Shells crossed before the USR
  onset (cN 2.5234): b, s25, s10 119 shells (k <= 11.87 dk), g05 30 (k <= 5.92), g2 473
  (k <= 23.77); all others during USR, none after.
- One-point variance of W R (ensemble) relative to the baseline: cN = 1: s25 0.919, s10
  1.055, g05 0.41, g2 1.81; cN = 3: 0.984, 1.037, 0.625, 2.92; cN = 4: 0.947, 1.003, 0.479,
  1.003; cN = 5: 1 within 1e-4 for all; N_f: 1. The window changes the one-point statistics
  by up to a factor 3 during the passage (cN < 4.5) and not at all afterwards.
- Predictions of entry 1 unchanged by this (W4 uses k < 11.87 sigma dk for "crossed before
  USR").
- SR 64^3, nmax2 = 256 (214 shells, 8538 modes): last crossing cN 2.805 (b), 3.506 (g05),
  2.103 (g2); the class columns of `shells_sr.csv` refer to the USR landmarks and mean
  nothing for SR.
