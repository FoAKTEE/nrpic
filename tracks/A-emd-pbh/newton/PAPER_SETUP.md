# The set-up of arXiv:2605.04487, with locators

Escrivà, Harada, Kohri, Terada, Yoo, "Gravitational wave emission from nonspherical
collapse in an early matter-dominated era using N-body simulations". Source read:
`kb-data/raw/arxiv/2605.04487/v2/src/main_v3.tex` (fetched 2026-11-15 with
`harness/bin/nrpic-fetch-arxiv`; v2 of the arXiv record). "Line" below means a line of
that file. Everything in the first two sections is [VERIFIED] against the source unless
marked; the third section is ours.

## What is evolved

| Item | Statement | Line |
|---|---|---|
| Matter | N collisionless particles of an overdense patch in an Einstein-de Sitter background; Newtonian self-gravity; "semirelativistic" kinematics | 206-214 |
| Coordinates | r = a x, peculiar velocity v = a dx/dt; a = a_0 (t/t_0)^(2/3), H = 2/(3t) | 216-248 |
| Comoving equation | x'' + 2 H x' = -grad_x phi / a^2, with grad_x^2 phi = 4 pi G a^2 (rho - rho_b): the background term "cancels out" | 259-312 |
| Kinematics | L = -m sqrt(1 - a^2 x'^2) - m phi; q = a^2 gamma x', gamma = sqrt(1 + q^2/a^2), q' = -grad_x phi; "the force law remains Newtonian, whereas the kinematics of the particles are treated relativistically" | 325-458 |
| Force | direct particle-particle sum over all particles, F_n = -G sum_m m (x_n - x_m) K(r_nm; h), cubic-spline kernel, h = 2.8 eps_com (Plummer-equivalent eps_com) | 460-511 |
| Integrator | kick-drift-kick leapfrog with exact EdS kick and drift factors (elliptic integral for the relativistic drift); constant global time step | 554-686, 2170 |
| Environment | "the particles evolved in the simulation represent only the finite inhomogeneous overdense patch"; isolated-patch approximation; tides and back-reaction on the expansion neglected | 695 |
| Units | length c/H_k (the equivalent patch radius at horizon entry), time 1/H_k, G = c = 1; so t_k = 2/3 and the patch mass M_k = c^3/(2 G H_k) = 1/2, Schwarzschild radius 1 | 2149-2170, 996-1002 |

## Initial data

| Item | Statement | Line |
|---|---|---|
| Patch | homogeneous Lagrangian sphere, R_L = 1 (code unit), mass M_patch = M_k (horizon mass at entry), m = M_k/N | 996-1006, 2184 |
| Deformation | Zel'dovich map x_i = (1 - D_0 lambda_i) xi_i, eigenvalues (lambda_1, lambda_2, lambda_3) = (alpha, beta, gamma), alpha >= beta >= gamma, alpha > 0, alpha + beta + gamma > 0 | 965-1012 |
| Velocities | x_i' = -H_0 a_0 lambda_i xi_i (growing mode D = a); q_i = a_0^2 gamma_0 x_i' | 1014-1034 |
| Amplitude | delta_L(t_k) = alpha + beta + gamma with D(t_k) = a(t_k) = 1; nu = delta_L / sigma | 1105-1136 |
| Shape | e = (alpha - gamma) / (2 delta_L), p = (alpha - 2 beta + gamma) / (2 delta_L); inverse alpha = (delta_L/3)(1 + 3e + p), beta = (delta_L/3)(1 - 2p), gamma = (delta_L/3)(1 - 3e + p) | 1172-1196 |
| Start | at turnaround of the shortest axis: a_0 = 1/(2 alpha), t_0 = t_k a_0^(3/2), t_k = 2/(3 H_k); shell crossing must not have happened yet | 1036-1060 |
| Particle load | uniform random sphere, relaxed to a glass by short-range repulsion (c_cut = 1.25), radial profile remapped to N(<r)/N = r^3; then whitening xi -> (det C)^(1/6) C^(-1/2) xi so that the second-moment tensor is isotropic to machine precision; residual quadrupole 1e-14 against 1e-1 for a random load | 2174-2240 |
| Centring | x_CM(t_0) = 0 and q_CM(t_0) = 0 subtracted | 1067-1076 |
| Numerical parameters | N = 3000 and eps_com = 0.05 fiducial; N = 1000, 3000, 9000 and eps_com up to 0.25 tested | 2275, 2344-2365 |
| Ensemble | about 10^3 configurations on grids in (alpha, beta, gamma) (Doroshkevich) or (nu, e, p) (BBKS); sigma = 0.01 and 0.1 | 2436-2442 |

## Numbers the paper prints, used as checks

| Case | Number | Line |
|---|---|---|
| sigma = 0.1, (alpha, beta, gamma) ~ (0.111, 0.0668, 0.0219), nu ~ 2, e ~ 0.223, p ~ -0.00125, N = 3000, eps_com = 0.05 | shell crossing of the shortest axis at t/t_k ~ 22.536; collapse along y at 29.097; largest virial parameter at 34.271; 99 percent of the GW energy by 45.024; virialization from about 50-60; the Zel'dovich approximation fails for t/t_k >~ 20 | 2275-2283 |
| same | start time 9.50883300 (figure file name, alpha = 0.1114) | 2287 |
| sigma = 0.01, (0.01112224, 0.00668337, 0.00219440) | snapshot times 301.416, 746.005, 966.039, 1152.918, 1452.827, 3300.509 | 2654-2659 |
| sigma = 0.1, (0.14, 0.04, 0.02), nu = 2, e = 0.3, p = 0.2 | snapshot times 6.749, 17.177, 29.630, 29.967, 32.971, 147.912 | 2670-2677 |
| sigma = 0.1, (0.16, 0.10, 0.04), nu = 3, e = 0.2, p = 0 | snapshot times 5.524, 12.071, 16.020, 18.313, 20.827, 63.032 | 2690-2695 |
| sigma = 0.1 | mean and median peculiar speed 0.4-0.5 c near the peak of the emission | 2400-2404 |

The appendix snapshot times are file names, not stated event times; reading the second
and third of them as first and second collapse is our inference by analogy with the main
case, where the second and third snapshot names equal the two event times of the text
[JUDGEMENT].

## What our reference solutions say about this set-up

All of this is from runs of this package (JOURNAL.md, entry 3).

1. The start convention is reproduced exactly: t_0/t_k = (2 alpha)^(-3/2) gives all four
   printed start times (run A-emd-pbh-20261115-113103-9832afd) [VERIFIED by run].
2. The two event times printed in the text (22.536, 29.097) are reproduced to +0.9 and
   +0.1 percent by a homogeneous ellipsoid whose full mass acts on top of the background
   deceleration ("added": effective density rho_b + rho_patch), and missed by 6 to 10
   percent (late, both events of this case) by the two consistent placements, the patch alone ("isolated") and the
   patch filling a hole in the background ("embedded"). Special-relativistic kinematics
   and softening both delay the collapse, so the consistent placements cannot be brought
   into agreement by them. The reading that the paper's pair force sums the full patch
   mass while its comoving equation keeps the background term is [JUDGEMENT]; the
   appendix cases support it for two of three cases and leave one unexplained
   (JOURNAL.md, P5(c)). [TO VERIFY against the paper's code, reference
   "escriva_github" of the paper.]
3. Consequence for track A [JUDGEMENT]: the AthenaK expanding ball is, in its Newtonian
   limit, the "isolated" placement (in spherical symmetry identical to "embedded" by
   Birkhoff's theorem). A comparison of our runs with 2605.04487 must therefore either
   switch on the added background in the Newtonian mode (to reproduce their numbers) or
   compare with the isolated reference, which collapses 1 to 13 percent later than
   their four cases (first collapse; JOURNAL.md entry 3).
4. Their kinematics is relativistic in the peculiar velocity only; the force is
   Newtonian and unsoftened beyond 2.8 eps_com. Our end-point estimate of the
   kinematic correction to the first-collapse time is 0.3 percent at sigma = 0.01 and 3
   to 6 percent at sigma = 0.1 for their cases, and 13 to 17 percent at delta_L = 1
   (tables/sr_estimate.csv). Full relativity changes the gravitational field as well;
   the paper states this is beyond its scope (footnote, lines 339-355).
