# Journal of the work package `newton` (A-pre-3 under decision 0010)

Owner A-emd-pbh, helper for this package. Predictions are written before the test runs;
outcomes are appended afterwards, also when a prediction fails. Code units throughout
are those of arXiv:2605.04487 (G = c = 1, length c/H_k, so H_k = 1, t_k = 2/3, the patch
mass M = M_k = 1/2 and its Schwarzschild radius r_g = 2GM/c^2 = 1; see `PAPER_SETUP.md`).

## 2026-11-15, entry 1: predictions for the reference solutions (before any run)

Models of the homogeneous ellipsoid (semi-axes A_i, mass M, density rho_e) used below:
- I "isolated": the patch alone, A_i'' = -2 pi G rho_e alpha_i A_i (Lin, Mestel and Shu
  form; also exact for the patch inside a spherical cavity of a homogeneous shell).
- II "embedded": the patch fills an ellipsoidal hole of a uniform background rho_b, no
  external tide, A_i'' = -(4 pi/3) G rho_b A_i - 2 pi G (rho_e - rho_b) alpha_i A_i.
- III "added": the patch sits on top of a uniform background everywhere,
  A_i'' = -(4 pi/3) G rho_b A_i - 2 pi G rho_e alpha_i A_i. This is what the equations
  of 2605.04487 give if its pair force (its Eq. force_pp) sums the full patch mass while
  its comoving equation (Eq. x_eom) keeps the background term.

P1 (top-hat). Integrating R'' = -GM/R^2 from Zel'dovich spherical data reproduces the
closed-form cycloid: turnaround and collapse times agree to better than 1e-8
(relative). Started early (a0 lambda -> 0) the linear contrast at turnaround and at
collapse tends to (3/20)(6 pi)^(2/3) = 1.0624 and (3/20)(12 pi)^(2/3) = 1.6865
[BACKGROUND, values computed from the closed form], with a deviation of first order in
a0 lambda. Refuted if the agreement is worse than 1e-6 or the deviation does not fall
linearly.

P2 (coefficients). alpha_i = (2/3) A_1 A_2 A_3 R_D(A_j^2, A_k^2, A_i^2) (Carlson R_D)
agrees with the closed forms for oblate and prolate spheroids to 1e-12 and sums to 2 to
1e-13. Refuted by any larger difference.

P3 (spherical limit of the ellipsoid). With alpha = beta = gamma, models I and II give the
cycloid collapse time to 1e-7; model III collapses earlier.

P4 (plane limit). Model II with transverse Lagrangian radii 10^k times the collapsing
one and lambda_2 = lambda_3 = 0 collapses at the Zel'dovich time a = 1/lambda_1 (exact in
plane symmetry), with an error that falls by about ten per unit of k. Refuted if the
error does not fall or settles at a finite value.

P5 (numbers printed in 2605.04487). (a) The start a0 = 1/(2 alpha), t0/t_k = a0^(3/2)
reproduces the start times in the figure file names: 9.50883300 (alpha = 0.1114),
301.41635408 (0.01112224), 6.74936559 (0.14), 5.52427173 (0.16), to the printed digits.
(b) For the representative case (alpha, beta, gamma) = (0.1114, 0.0667, 0.0219) the text
gives first-axis shell crossing at t/t_k = 22.536 and second-axis collapse at 29.097.
Ordering expected from the forces along the short axis: t_1(III) < t_1(I) < t_1(II)
(model II pushes the short axis outward by 2 pi G rho_b (alpha_1 - 2/3) A_1 relative to I;
III adds the background pull). The N-body run has softening (kernel radius 0.14 of the
patch radius) and special-relativistic kinematics, both of which slow the collapse, so
the Newtonian model that represents its set-up should come out EARLIER than 22.536, by a
few percent. My expectation [JUDGEMENT]: model III (the literal reading) is within 5
percent below 22.536; if instead only I or II is, the paper's code subtracts the
background inside the patch. Refuted if no model is within 10 percent.

P6 (Zel'dovich hoop). The hoop of the Zel'dovich pancake computed from the axes of the
code reproduces the closed form h = (2/pi)(alpha - gamma)/alpha^2 E(e) of 1609.01588
(its Eq. s_3, lines 603-607) to 1e-12.

P7 (scaling). With the start a0 = 1/(2 alpha) every Newtonian model is scale free: at
fixed (e, p) the times scale as delta_L^(-3/2) and the hoop ratio as 1/delta_L, to the
integration tolerance (1e-8).

## 2026-11-15, entry 2: first look at P5(b) (interactive smoke test, not a registered run)

A smoke test of `ellipsoid.py` (uncommitted code, interactive, numbers to be reproduced
by the registered validation run) gave for (0.1114, 0.0667, 0.0219), start t0/t_k =
9.50883: first collapse (axis 1) / second collapse (axis 2) at t/t_k
- isolated 23.813 / 32.059, with end-point SR kinematics 24.466 / 33.742;
- embedded 24.215 / 31.414, SR 24.850 / 33.138;
- added    22.733 / 29.126, SR 23.442 / 30.877.
Paper: 22.536 / 29.097. The ordering III < I < II of P5(b) holds. The literal model III
is within +0.9 and +0.1 percent; I and II are 6 to 10 percent late, and the corrections
that slow the collapse (SR kinematics, softening) would make them later still. So P5(b)
holds in its expected form, pending the registered run.

P5(c), written before running the other cases. If model III is the set-up of the paper,
it also lands within 5 percent of the event times inferred for the three appendix cases.
The inference is [JUDGEMENT]: for the main case the second and third snapshot file names
(source lines 2288-2289: 22.53593422, 29.09702899) are the two event times of the text
(line 2277, 2279), so I read the second and third snapshot times of the appendix figures
the same way: (0.01112224, 0.00668337, 0.00219440): 746.005, 966.039 (lines 2655-2656);
(0.14, 0.04, 0.02): 17.177, 29.630 (lines 2672-2674); (0.16, 0.10, 0.04): 12.071, 16.020
(lines 2691-2692). For the sigma = 0.01 case the end points move at about 7 percent of c
at the start (v = a0^(-1/2)/2 in these units), so its SR and Newtonian times must agree to better than 1 percent; for the
sigma = 0.1 cases SR delays by 2 to 6 percent. Refuted (for III) if any first-collapse
time is off by more than 5 percent; then either the inference of the event times or the
model is wrong, and the snapshots cannot be used.

## 2026-11-15, entry 3: outcomes of P1 to P7 (runs A-emd-pbh-20261115-113103-9832afd, validation; A-emd-pbh-20261115-113152-cd9539e, tables)

Before the registered run, two defects were found in unregistered dry runs and fixed
before the first commit of the code (bece205): (i) the collapse event sat at A_i = 0, which a sphere never reaches in finite
steps (no event, IndexError); the event is now at |A_i| = 1e-8 of the axis' initial
value; (ii) with the threshold first taken relative to the LARGEST axis, the plane-limit
error of P4 fell as 10^-k to k = 4 and then rose again (7.5e-4 at k = 5, 7.5e-3 at
k = 6), because the threshold then grew with the transverse axes; per-axis threshold
fixes it. Also the cycloid evaluation by Newton iteration failed near th = 2 pi (figure
check showed R off by 0.9 R_max); replaced by a bracketed root. Figures were inspected
after each fix (`figs/`).

- P1 holds. Turnaround and inner-point times of the direct integration agree with the
  cycloid to 4.9e-12 and 4.9e-12 (start a0 lambda = 0.02) and 8.5e-14, 7.1e-14 (start
  0.2); the whole curve to 1.6e-9 of R_max. Early start: delta_L(t_c) - 1.686470 and
  delta_L(t_ta) - 1.062410 fall as (a0 lambda)^1.0005; at a0 lambda = 1e-4 they are
  1.686571 and 1.062473; t_c/t_ta -> 2 to 1e-14. Figure `figs/fig_tophat.png`.
- P2 holds. Largest |alpha_RD - alpha_closed| = 1.3e-13 for c/a from 1e-3 to 1e3; the
  sum differs from 2 by at most 8.9e-16 over 1000 random triaxial shapes (axis ratios up
  to 1e6). Figure `figs/fig_alphas.png`.
- P3 holds. Isolated and embedded spheres collapse at the cycloid time to 3.4e-14
  (start at turnaround) and 1.0e-11 (start a0 lambda = 0.05); added collapses earlier,
  by 1.3 percent from the turnaround start and by 76 percent from the early start (there
  the added background doubles the density). The comoving formulation with gamma = 1
  (used for the SR estimate) equals the physical one to 3.8e-9 and 8.0e-10 (first,
  second collapse of the main case).
- P4 holds. |t_1/t_ZA - 1| = 1.47e-2, 1.49e-3, 1.49e-4, 1.49e-5, 1.49e-6, 1.46e-7 for
  k = 1..6 (start at turnaround); from a0 lambda = 0.01: 1.3e-1 down to 1.3e-6. Figure
  `figs/fig_plane_limit.png`.
- P5(a) holds: t0/t_k from a0 = 1/(2 alpha) equals the printed start times to 3e-10,
  8e-11, 4e-10, and 4.6e-7 for the sigma = 0.01 case, whose file name rounds
  alpha = 0.011122237 to 0.01112224 (that rounding alone gives 4e-7).
- P5(b) holds as recorded in entry 2 (same numbers in the registered run).
- P5(c) partly refuted. Model "added": first collapse +0.87 (main, from the text),
  -3.47 (sigma = 0.01), +1.42 (0.14, 0.04, 0.02), +7.70 percent (0.16, 0.10, 0.04);
  second collapse +0.10, -4.66, +1.31, +1.12 percent. The criterion (all first-collapse
  times within 5 percent) fails for (0.16, 0.10, 0.04). "isolated": +5.7, +1.1, +7.9,
  +12.5 (first), +10.2, +4.9, +28.9, +10.0 (second); "embedded": +7.5, +2.8, +11.3, +14.2
  and +8.0, +2.8, +15.6, +8.3. The end-point SR estimate delays by 0.3 percent at
  sigma = 0.01 and 3 to 6 percent (first) at sigma = 0.1. "added" is the closest model in
  6 of the 8 comparisons; the exception is the sigma = 0.01 case, which after scaling
  out the amplitude lies 4.5 percent LATER relative to the main case than any scale-free
  Newtonian model allows, while SR kinematics would make the sigma = 0.1 case the later
  one. So for that case either the snapshot times are not the event times, or the
  paper's runs break the scaling in another way (time step, softening schedule). Not
  decided [TO VERIFY]. Figure `figs/fig_paper_cases.png`.
  Reading [JUDGEMENT, supported by these runs]: the two event times the text prints are
  reproduced to 0.9 and 0.1 percent only by the "added" placement; the two consistent
  placements are 6 to 10 percent late before the SR and softening corrections, which
  would delay them further. This suggests that the N-body code of 2605.04487 sums the
  full patch mass in its pair force while keeping the background deceleration, i.e.
  the patch evolves with an effective density rho_b + rho_patch. If so, its
  "delta_L = alpha + beta + gamma" is not the contrast its runs evolve. To be checked
  against the paper's code (request to kb, README).
- P6 holds: 2.9e-15 over 200 shapes.
- P7 holds, better than predicted: spread of t_1 delta_L^(3/2) at most 1.5e-13 and of
  h delta_L at most 1.0e-13 over three amplitudes (0.05, 0.2, 1) and three shapes in
  each model.

Tables (run A-emd-pbh-20261115-113152-cd9539e; identical numbers to the superseded
A-emd-pbh-20261115-113108-9832afd, which differed only in a figure label position):
hoop threshold amplitude delta_L,th = h delta_L at p = 0, isolated / Zel'dovich:
e = 0.01: 0.089 / 0.131; 0.02: 0.167 / 0.247; 0.05: 0.359 / 0.525; 0.1: 0.592 / 0.821;
0.2: 0.855 / 1.084; 0.3: 0.968 / 1.153. The ellipsoid pancake is 0.64 to 0.91 times
the Zel'dovich one (`figs/fig_scan_hoop_ratio.png`), so the Newtonian hoop line lies
below the Zel'dovich line of 1609.01588 by that factor. First collapse at 1.86 t0
(e -> 0) to 2.9 t0 (e = 0.5) for the paper's start (`figs/fig_scan_hoop_time.png`).
End-point SR delay of the first collapse: 0.7-0.9 percent at delta_L = 0.05, 1.4-1.8 at
0.1, 4-5 at 0.3, 13-17 at 1 (`tables/sr_estimate.csv`).

## 2026-11-15, entry 4: prediction for the snapshot analysis self-test (before the run)

`compare_snapshots.py` reads AthenaK particle snapshots and compares semi-axes and
collapse times with the ellipsoid reference. Its self-test writes snapshots of the exact
"added" ellipsoid of the main paper case, sampled with N = 20000 random particles, in the
NRPIC001 convention (lengths and times x 2, clock from 0), and analyses them like a run.
Prediction: the axis of first collapse is axis 1; the first-collapse time from the
parabola vertex of the second moment agrees with the reference to better than 1e-3
(the sample's second moment is a common factor of c_1(t), so sampling noise does not
move the vertex; only the finite snapshot spacing does); the semi-axes at the start agree
with the reference to the sampling error of the ball, about 1 percent. Refuted if the
time is off by more than 1e-3 or the wrong axis is found.

## 2026-11-15, entry 4 outcome (run A-emd-pbh-20261115-113822-87cba08)

Holds. Axis 1 found first; first-collapse time 1.2e-5 from the reference (snapshot
spacing near the collapse 0.076, i.e. 5e-3 of t_1); semi-axes of the sampled ball within
0.9 percent of the reference (sampling error). Figure `figs/fig_axes_selftest.png`. The
first registered self-test (A-emd-pbh-20261115-113807-e02c969) printed the spacing as 0
through a bug in the report line; same analysis numbers.
