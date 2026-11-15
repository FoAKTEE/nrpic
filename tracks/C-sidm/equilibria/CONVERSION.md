# Knudsen number and cross-section per unit mass of the near-threshold equilibria

Every number below comes from run C-sidm-20261115-122915-cdc395c (`knudsen.py`,
`results/knudsen.json`) on the models of run C-sidm-20261115-120610-b4592be, unless a
literature locator is given. Units G = c = 1, ADM mass M = 1. Figures:
`figs/knudsen_conversion.png`, `figs/knudsen_profiles.png`.

## 1. The variable

    sigma~ = (sigma/m) / M

is the cross-section per unit (rest) mass in units of the ADM mass (sigma/m has the
dimension of a length when G = c = 1). sigma is the total cross-section, taken as constant
(isotropic elastic scattering in the centre-of-momentum frame, the operator of C-pre-1);
for a velocity-dependent cross-section, sigma/m below is its value at the core's
relative velocities. Physical units [BACKGROUND: CODATA 2018 G and c; IAU 2015 Resolution
B3 nominal GM_sun = 1.3271244e20 m^3 s^-2]:

    sigma~ = (sigma/m) c^4 / (G^2 M) = 9.119e22 (sigma/m / 1 cm^2 g^-1) (M_sun / M).

## 2. Definitions

| Quantity | Definition | Source and label |
|---|---|---|
| rest-mass density | rho0 = m n, n the number density of the static observers | the moments of `evstatic.py` |
| collision rate per particle | Gamma = rho0 (sigma/m) <v_Mol>, v_Mol = [(eps1 eps2 - q1.q2)^2 - 1]^{1/2} / (eps1 eps2), averaged over pairs of the local distribution (q orthonormal momentum per unit mass, eps = (1 + q^2)^{1/2}) | Moller relative velocity of relativistic kinetic theory [BACKGROUND] |
| mean free path | l = <|q|/eps> / Gamma (relativistic rate) | [BACKGROUND]; for a Newtonian Maxwellian l = lambda/sqrt 2 |
| literature mean-free-path scale | lambda = 1/(rho0 sigma/m) | astro-ph/0110561 eq. lambda_SIDM, `SIDMGT_Xiv2.tex` lines 388-390 [VERIFIED]; its lines 391-392 note l = lambda/sqrt 2 for hard spheres with a Maxwell-Boltzmann distribution |
| scale height | H = [v1^2 / (4 pi rho0)]^{1/2}, v1^2 = (p + 2 p_T)/(3 rho0) | astro-ph/0110561 eq. scaleheight, lines 403-405 (v the one-dimensional dispersion, line 351) [VERIFIED]; relativistic transcription rho -> rho0, v^2 -> (p + 2 p_T)/(3 rho0) [JUDGEMENT] |
| dynamical time | t_d = H/v1 = (4 pi rho0)^{-1/2}, proper time of the static observer; coordinate time t_d/alpha | astro-ph/0110561 lines 408-409 [VERIFIED] |
| Knudsen number | Kn = l_c / H_c | c: the centre; for the shells the radius of the peak of rho0 [JUDGEMENT] |
| collisions per particle per dynamical time | nu_c = Gamma_c t_d at the centre; nu_bar = <alpha Gamma>_particles t_d / alpha_c, the particle average per coordinate dynamical time | this package |

Because Gamma is proportional to sigma/m, Kn sigma~, nu_c Kn and nu_bar Kn are properties
of the model alone. <v_Mol> is computed by quadrature with the closed-form direction
average for the isotropic models and checked by Monte Carlo over pairs drawn with the
package's sampler (10 isotropic models: |MC - quadrature| <= 1.36 standard errors); for the
anisotropic shells the Monte Carlo value (2 x 10^5 pairs, standard error 0.1 percent) is
used. The closed-form direction average agrees with direct sampling and tends to the
Newtonian 4q/3 for two equal speeds q -> 0 (1.33333 at q = 1e-3).

## 3. The conversion for every model

    Kn = (Kn sigma~) / sigma~

| model | rho0_c M^2 | v1_c | H_c/M | t_d/M (proper) | t_d/M (coord.) | <v>_c | <v_Mol>_c | l/lambda | Kn sigma~ | nu_c Kn | nu_bar Kn |
|---|---|---|---|---|---|---|---|---|---|---|---|
| king_y0p31400 | 0.00364 | 0.3158 | 1.4765 | 4.676 | 6.915 | 0.4829 | 0.6306 | 0.7658 | 142.5 | 1.5292 | 0.4028 |
| king_y0p32400 | 0.00388 | 0.3213 | 1.4555 | 4.530 | 6.773 | 0.4901 | 0.6388 | 0.7672 | 135.9 | 1.5251 | 0.4009 |
| king_y0p33403 | 0.00412 | 0.3269 | 1.4359 | 4.393 | 6.642 | 0.4971 | 0.6467 | 0.7687 | 129.8 | 1.5209 | 0.3991 |
| king_y0p34400 | 0.00437 | 0.3323 | 1.4176 | 4.266 | 6.521 | 0.5040 | 0.6545 | 0.7701 | 124.2 | 1.5168 | 0.3972 |
| king_y0p35400 | 0.00463 | 0.3377 | 1.4005 | 4.147 | 6.409 | 0.5108 | 0.6621 | 0.7715 | 119.1 | 1.5127 | 0.3953 |
| poly05_y0p27766 | 0.00298 | 0.3194 | 1.6506 | 5.168 | 7.549 | 0.4913 | 0.6380 | 0.7701 | 156.6 | 1.5382 | 0.4514 |
| poly05_y0p28766 | 0.00320 | 0.3257 | 1.6247 | 4.989 | 7.376 | 0.4995 | 0.6472 | 0.7718 | 148.5 | 1.5336 | 0.4493 |
| poly05_y0p29766 | 0.00342 | 0.3319 | 1.6009 | 4.823 | 7.217 | 0.5075 | 0.6561 | 0.7734 | 141.2 | 1.5289 | 0.4471 |
| poly05_y0p30766 | 0.00365 | 0.3380 | 1.5788 | 4.671 | 7.072 | 0.5153 | 0.6648 | 0.7751 | 134.6 | 1.5243 | 0.4449 |
| poly05_y0p31766 | 0.00388 | 0.3441 | 1.5584 | 4.529 | 6.938 | 0.5229 | 0.6732 | 0.7767 | 128.5 | 1.5196 | 0.4427 |
| arshell_y0p13320 | 0.00410 | 0.2682 | 1.1820 | 4.407 | 6.062 | 0.4396 | 0.5518 | 0.7967 | 164.5 | 1.6390 | 1.1982 |
| arshell_y0p13545 | 0.00422 | 0.2705 | 1.1754 | 4.345 | 6.002 | 0.4430 | 0.5570 | 0.7953 | 160.5 | 1.6375 | 1.1942 |
| arshell_y0p14768 | 0.00487 | 0.2830 | 1.1442 | 4.044 | 5.717 | 0.4610 | 0.5781 | 0.7975 | 143.2 | 1.6294 | 1.1884 |

Over the 13 models Kn sigma~ lies between 119 and 165, so the cross-sections for
Kn = 10, 3, 1, 0.3, 0.1, 0.03, 0.01 are sigma~ = 11.9-16.5, 39.7-54.8, 119-165, 397-548,
1190-1650, 3970-5480, 11900-16500. The central one-dimensional dispersion of the King and
polytrope models near threshold is v1_c = 0.32-0.34. The brief quotes about 0.3c for the
onset of the relativistic instability from 2506.17641 [TO VERIFY against that paper].

## 4. Kn = 10 to 0.01 for the three threshold models, N = 10^4

nu_c, nu_bar: collisions per particle per dynamical time (independent of N at fixed
sigma/m, because a macroparticle of mass m_p carries the cross-section
sigma_macro = (sigma/m) m_p). Pair events per t_d: N nu_bar / 2. d_c = n_p,c^{-1/3} is the
mean distance between macroparticles at the centre (n_p,c = rho0_c N/M0, proper volume):
0.293 M (King), 0.312 M (polytrope), 0.291 M (shell) at N = 10^4. l_c/R and l_c/r_half use
the areal surface radius and the proper radius of the half-mass sphere instead of H_c.

King, y0 = y_max = 0.334032 (R = 13.630 M, r_half = 4.382 M proper, M0 = 1.0369):

| Kn | sigma~ | nu_c | nu_bar | pair events per t_d | sigma_macro/M^2 | l_c/M | l_c/d_c | particles in l_c sphere | l_c/R | l_c/r_half |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 12.98 | 0.152 | 0.0399 | 200 | 0.00135 | 14.36 | 49 | 4.9e5 | 1.05 | 3.28 |
| 3 | 43.27 | 0.507 | 0.133 | 665 | 0.00449 | 4.308 | 14.7 | 1.3e4 | 0.316 | 0.983 |
| 1 | 129.8 | 1.52 | 0.399 | 2.0e3 | 0.0135 | 1.436 | 4.9 | 493 | 0.105 | 0.328 |
| 0.3 | 432.7 | 5.07 | 1.33 | 6.7e3 | 0.0449 | 0.4308 | 1.47 | 13.3 | 0.0316 | 0.0983 |
| 0.1 | 1298 | 15.2 | 3.99 | 2.0e4 | 0.135 | 0.1436 | 0.49 | 0.49 | 0.0105 | 0.0328 |
| 0.03 | 4327 | 50.7 | 13.3 | 6.7e4 | 0.449 | 0.04308 | 0.147 | 0.013 | 0.00316 | 0.00983 |
| 0.01 | 12980 | 152 | 39.9 | 2.0e5 | 1.35 | 0.01436 | 0.049 | 4.9e-4 | 0.00105 | 0.00328 |

Polytrope k = 1/2, y0 = y_max = 0.297664 (R = 10.530 M, r_half = 4.445 M, M0 = 1.0370):

| Kn | sigma~ | nu_c | nu_bar | pair events per t_d | sigma_macro/M^2 | l_c/M | l_c/d_c | particles in l_c sphere | l_c/R | l_c/r_half |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 14.12 | 0.153 | 0.0447 | 224 | 0.00146 | 16.01 | 51.3 | 5.7e5 | 1.52 | 3.6 |
| 3 | 47.08 | 0.510 | 0.149 | 745 | 0.00488 | 4.803 | 15.4 | 1.5e4 | 0.456 | 1.08 |
| 1 | 141.2 | 1.53 | 0.447 | 2.2e3 | 0.0146 | 1.601 | 5.13 | 567 | 0.152 | 0.36 |
| 0.3 | 470.8 | 5.10 | 1.49 | 7.5e3 | 0.0488 | 0.4803 | 1.54 | 15.3 | 0.0456 | 0.108 |
| 0.1 | 1412 | 15.3 | 4.47 | 2.2e4 | 0.146 | 0.1601 | 0.513 | 0.57 | 0.0152 | 0.036 |
| 0.03 | 4708 | 51.0 | 14.9 | 7.5e4 | 0.488 | 0.04803 | 0.154 | 0.015 | 0.00456 | 0.0108 |
| 0.01 | 14120 | 153 | 44.7 | 2.2e5 | 1.46 | 0.01601 | 0.0513 | 5.7e-4 | 0.00152 | 0.0036 |

Shell L0 = 0.1, E_b maximum, y0 = 0.135452 (R = 5.038 M, r_half = 1.078 M proper from the
inner edge, M0 = 1.0431; "c" is the peak of rho0 at areal r = 3.95 M):

| Kn | sigma~ | nu_c | nu_bar | pair events per t_d | sigma_macro/M^2 | l_c/M | l_c/d_c | particles in l_c sphere | l_c/R | l_c/r_half |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 16.05 | 0.164 | 0.119 | 597 | 0.00167 | 11.75 | 40.3 | 2.7e5 | 2.33 | 10.9 |
| 3 | 53.5 | 0.546 | 0.398 | 2.0e3 | 0.00558 | 3.526 | 12.1 | 7.4e3 | 0.7 | 3.27 |
| 1 | 160.5 | 1.64 | 1.19 | 6.0e3 | 0.0167 | 1.175 | 4.03 | 275 | 0.233 | 1.09 |
| 0.3 | 535 | 5.46 | 3.98 | 2.0e4 | 0.0558 | 0.3526 | 1.21 | 7.4 | 0.07 | 0.327 |
| 0.1 | 1605 | 16.4 | 11.9 | 6.0e4 | 0.167 | 0.1175 | 0.403 | 0.27 | 0.0233 | 0.109 |
| 0.03 | 5350 | 54.6 | 39.8 | 2.0e5 | 0.558 | 0.03526 | 0.121 | 0.0074 | 0.007 | 0.0327 |
| 0.01 | 16050 | 164 | 119 | 6.0e5 | 1.67 | 0.01175 | 0.0403 | 2.7e-4 | 0.00233 | 0.0109 |

In the King and polytrope models nu_bar is about a quarter of nu_c (outer particles see a
lower density and a larger lapse factor); in the thin shell all particles see nearly the
peak density (nu_bar/nu_c = 0.73).

## 5. What this implies [JUDGEMENT unless stated]

1. Resolution at N = 10^4. The mean free path falls below the mean macroparticle distance
   at the centre for Kn below about 0.2 (l_c/d_c = 1 at Kn = 0.20 for King, 0.19 for the
   polytrope, 0.25 for the shell; from the tables, since l_c/d_c is proportional to Kn).
   A particle Monte Carlo collision step with pairs chosen within cells gets the
   collision rate right at any Kn, but transport in the short-mean-free-path end is then
   set by the cell size, not by l. The usual direct-simulation Monte Carlo practice of
   cells smaller than l with some tens of particles per cell [BACKGROUND, Bird's DSMC
   practice, not checked here] needs (l/d)^3 of order 20 or more. At Kn = 0.01 that
   requires d smaller by a factor 55 than at N = 10^4, i.e. about 10^4 x 55^3 ~ 2 x 10^9
   particles. With 10^4 to 10^6 particles, the scan from Kn = 10 to 0.01 resolves the long
   end (Kn >~ 0.3) only, and the short end tests the collision operator in its
   unresolved, cell-limited regime.
2. Time step. Collisions per particle per unit coordinate time at the centre are
   alpha_c Gamma_c = nu_c/(t_d/alpha_c): 23 per M at Kn = 0.01 for the King threshold model
   (152 per t_d, t_d = 6.64 M in coordinate time). An explicit collision step with at most
   one collision per particle per step needs dt <~ 0.04 M there, comparable to the CFL step
   of a mesh with dx = M/4 (0.06 M at Courant number 0.25). Below Kn ~ 0.01 the collision
   step, not the mesh, sets the time step (the stiffness of brief risk S3).
3. Astrophysical scale. For a constant sigma/m = 1 cm^2/g the threshold models have
   Kn = 1.4e-21 (King), 1.5e-21 (polytrope), 1.8e-21 (shell) at M = 1 M_sun and 1.4e-12 to
   1.8e-12 at M = 1e9 M_sun. A relativistic SIDM core with a cross-section in the range
   usually discussed for SIDM is therefore deep in the short-mean-free-path (fluid) regime.
   Kn = 10 to 0.01 corresponds to sigma/m = 1.3e-22 to 1.8e-19 cm^2/g at 1 M_sun. The Kn
   scan of S3 is thus a study of the transition between the collisionless and the fluid
   limits, not of a realistic cross-section. The fluid end is the regime of 2601.17117's
   Misner-Sharp treatment. This should shape how S3 frames its result.
4. Choice of length scale. Kn_R = l_c/R is 0.105 Kn (King), 0.152 Kn (polytrope) and 0.233 Kn
   (shell). A "Kn = 1" defined with the cluster radius is therefore about ten times more
   collisional than one defined with H_c. The definition above follows the gravothermal
   literature (lambda/H of astro-ph/0110561, eq. Hvslambda, lines 438-440 [VERIFIED]);
   l/lambda = 0.766-0.798 converts to the lambda-based number Kn_BSI = lambda_c/H_c = Kn/(l/lambda).

## 6. Recompute

    python3 runreg.py --purpose "..." -- python3 knudsen.py --out {out} --N <N>
    python3 fig_knudsen.py --run <run dir> --out figs

Rows for another N scale as sigma_macro proportional to 1/N, d_c to N^{-1/3}, pair events
to N; nu_c, nu_bar, sigma~ and l do not depend on N.

## 5. Track definition of Kn and K for the wave-2 models (lead, wave 2)

Runs are labelled with the track's Knudsen number (`../stage/G0/REPORT.md` decision 2,
`../collide/SPEC.md` section 1): Kn_c = lambda_c/H_c with lambda = 1/(rho0 sigma_m) (not the
transport mean free path l of section 2, l/lambda = 0.77) and H on the rest-mass density.
Then sigma~ = K/Kn_c with K = 1/(rho0_c H_c) = (4 pi/p_c)^{1/2} for isotropic models
(M_ADM = 1). The table of section 3 converts by K = (Kn sigma~)/(l/lambda): King threshold
129.8/0.7687 = 168.9. Values for the 13 models of run C-20261115-170742-84990ed (N = 1e5;
computed in run C-20261115-193751-d3872ff from each model's JSON; King threshold 168.90 as
in run C-sidm-20261115-131130-3077a99, F21 eps maximum 142.60 as the verifier's run
C-20261115-170630-1037f6a):

| model | Z(0) | H_c/M | K = sigma~ at Kn_c = 1 | sigma~ at Kn_c = 10 |
|---|---|---|---|---|
| king_y0p31400 | 0.47880 | 1.4765 | 186.08 | 18.61 |
| king_y0p32400 | 0.49529 | 1.4555 | 177.14 | 17.71 |
| king_y0p33403 | 0.51191 | 1.4359 | 168.90 | 16.89 |
| king_y0p34400 | 0.52851 | 1.4176 | 161.34 | 16.13 |
| king_y0p35400 | 0.54524 | 1.4005 | 154.33 | 15.43 |
| tmb01_Z0p5000 | 0.50000 | 1.1753 | 161.20 | 16.12 |
| tmb01_Z0p5200 | 0.52000 | 1.1441 | 151.53 | 15.15 |
| tmb01_Z0p5331 (Juttner fluid onset) | 0.53306 | 1.1248 | 145.72 | 14.57 |
| tmb01_Z0p5404 (eps maximum) | 0.54041 | 1.1142 | 142.60 | 14.26 |
| tmb01_Z0p5600 | 0.56000 | 1.0869 | 134.80 | 13.48 |
| tmb01_Z0p5800 | 0.58000 | 1.0605 | 127.53 | 12.75 |
| tmb01_Z0p6000 | 0.60000 | 1.0354 | 120.85 | 12.09 |
| tmb01_Z0p6348 (F21 fluid onset) | 0.63482 | 0.9941 | 110.46 | 11.05 |

The card runs CC1 and CC2 of `../threshold_scan/` used sigma~ = K/Kn_c with K = 168.895
(CC1) and 186.081 (CC2), the values above.
