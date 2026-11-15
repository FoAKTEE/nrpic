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
