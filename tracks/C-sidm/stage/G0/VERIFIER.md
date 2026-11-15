# Independent verification of the G0 and G1 material of Track C

Verifier helper of owner C-sidm, wave 2, 2026-11-15. Fresh reader: I started from the scoping
text (`tracks/C-sidm/scope/SCOPE.md`), the package derivations and code
(`gravothermal/`, `equilibria/`, `collide/`, `scope/scripts/`), the raw outputs and the paper
sources under `kb-data/raw/arxiv/`; the summaries (STATUS, HANDOFF, REVIEW, stage report,
package journals) were read only after sections 1 and 2 below were written (section 3).
Predictions: `JOURNAL.md` of this directory (committed in 8e669ce before any of my code ran).

Runs (processors, 0 card-hours):

| Run id | What |
|---|---|
| C-20261115-170630-1037f6a | my own code, `verifier/run_all.sh`: V1 to V7 (outputs `scratch/C-sidm/<run>/{mono,king,puls,rate,costs}`) |
| C-20261115-170716-e81ba08 | rerun of the track's scripts and tests: `scope/scripts/{seq_monoenergetic,king_sequence,knudsen_costs}.py`, `gravothermal/test_tmb.py`, `collide/REFERENCES/tests` (pytest), `equilibria/knudsen.py`; all exit 0; the three scope JSONs are byte-identical to those of runs C-sidm-20261115-115344/115348/115400-eb8b752, `knudsen.json` equal to `equilibria/results/knudsen.json`; test_tmb ALL PASS; 62 pytest pass |

Figures (copies of the first run's PNGs, each looked at): `verifier/figs/fig_v{1..7}_*.png`.
My code shares nothing with the track's: own structure equations and closures
(`verifier/v_mono.py`, `verifier/kingsolve.py`, closures derived from f(E) by hand), a
global-basis Rayleigh-Ritz instead of the track's finite elements (`verifier/v_pulsation.py`),
my own Maxwell-Juttner sampler (`verifier/v_rate.py`), my own log parser (`verifier/v_costs.py`).

## 1. The claims and the verdicts

Eight claims on which the plan rests (SCOPE.md sections 1 to 8), plus one that fell out of V4.

| # | Claim (where) | Verdict |
|---|---|---|
| V1 | Monoenergetic family: first E_b/M0 maximum at y_c = 0.67961, z_c = 0.4553 (G1 criterion (a) rests on it); Wu-Most rows reproduced (SCOPE 2, 3.1) | CONFIRMED |
| V2 | F21 truncated Maxwell-Boltzmann family is an exact f(E) steady state; F21 Table 1 reproduced; b = 0.1 eps maximum at Z(0) = 0.5404, trial root at 0.7500 (SCOPE 3.2, gravothermal 1-2) | CONFIRMED |
| V3 | The King model of 2009.08163 is that family at b = 1, y0 = -ln(1 - b w0); threshold y_max = 0.33403 (SCOPE 3.2, equilibria) | CONFIRMED |
| V4 | Exact fluid onset (gamma = 1 + p/u) at Z(0) = 0.6348 for b = 0.1, 0.579 for b = 0.5 (gravothermal 3) | CONFIRMED (one unit label wrong, see V4) |
| V4b | SCOPE 1: for Kn -> 0 the adiabatic-index (trial) criterion at Z(0) = 0.750 is the relevant fluid threshold; prediction window 0.54 < Z(0) < 0.75 | WRONG for the upper end |
| V5 | Knudsen number and sigma/m conversion: 1/(rho0_c H_c) = 166, 103, 199, 270; unit 1.097e-23 cm^2/g per M_sun; physical Kn_c ~ 1e-19 (SCOPE 4; equilibria CONVERSION.md) | numbers CONFIRMED; "one Knudsen number" NOT CONFIRMED |
| V6 | <v_Mol>(theta) = 4 K3(2z)/(z K2(z)^2), the collision-rate reference (collide SPEC 2) | CONFIRMED |
| V7 | Stiffness and cost: N = 600-1600 at Kn_c = 1, N ~ Kn^-3, 2-7 sub-steps at Kn_c = 0.1; unit costs from the logs; G1-G3 card-hours (SCOPE 7.1, 8) | CONFIRMED (sub-steps conservative by 1.6-1.9) |
| V8 | Source locators of the threshold choice and of the field (SCOPE 1, 3.3, 3.4, 6, 7; ~35 read) | CONFIRMED except one (2105.05556:581 mis-described) |

### V1 Monoenergetic sequence: CONFIRMED

Re-derived the closures from f = K delta(E - E0) (W = y^{-1/2}, rho0 ~ q W^2, rho ~ q W^3,
P ~ q^3 W/3; P_c/rho_c = (1 - y_c)/3 and rho0_c/rho_c = y_c^{1/2}, as 2611.12831
main.tex:1057-1070 prints) and integrated in areal radius (`v_mono.py`). Run
C-20261115-170630-1037f6a: maximum at y_c = 0.6796102, z_c = 0.455290, E_b/M0 = 0.0360576,
R/M = 6.55243; first zero at y_c = 0.3904461; E_b/M0(0.756) = 0.0339834, E_b/M0(0.605) =
0.0339763. The five rows of main.tex:1024-1028: R/M within 1e-5, M0/M within 5e-7, z_c within
4.3e-4 (half a printed unit is 5e-4; `fig_v1_mono.png`). Attempt to break: Newtonian limit
y_c -> 1 must be the n = 1/2 polytrope (density ~ (E0 - Phi)^{1/2}); my own Lane-Emden gives
xi_1 = 2.752698, omega_1 = 3.788651, and x_s, v_s approach sqrt(3/2) xi_1 = 3.37135 and
(3/2)^{3/2} omega_1 = 6.96020 linearly in 1 - y_c (3.37131, 6.95923 at 1 - y_c = 1e-4).
The track's rerun (`seq_monoenergetic.py`, run C-20261115-170716-e81ba08) gives
y_c = 0.6796101 (4e-8 from mine). What I could not check: that this maximum is the dynamical
threshold. The monoenergetic f is not a decreasing function of E, so the stability results
that need phi'(E) < 0 (2009.08163 paper.tex:177-179) do not cover it; that it marks the onset
rests on ST85 quoted by Wu and Most (2611.12831 main.tex:1092) and on the bracket of this
repository's runs [JUDGEMENT].

### V2 F21 family, b = 0.1: CONFIRMED

`kingsolve.py` integrates f = exp((W_c - W)/(b W_c)) - 1 directly over the local momentum
(not F21's I-integrals) with W_c = E_c e^{-Phi}; with unit normalisation these are exactly
F21's hatted units (rho^ = 4 sqrt2 pi I_rho follows from W - 1 = b x/(1 - b w)). That this
f(E) solves the Vlasov equation is by construction (function of the Killing energy), and the
agreement below shows it is F21's model. F21 Table 1 rows w0 = 0.6, 1.9, 3.2, 4.0515, 4.5
(main.tex:492-503): M^, E^rest, eps, Z(0), rho^(0), p^(0), v(0), <gamma>, gamma_cr within
3e-6 for w0 <= 1.9, rising to 1.3e-4 (B^: 2.4e-4) at w0 = 4.5 (`fig_v2_f21.png`); my
prediction of 2e-4 is exceeded by B^ = E_rest - M at the most concentrated row, where both
terms carry F21's 1.1e-4 errors; F21's R^ is the radius truncated to 1e-3 (differences
0.08e-3 to 0.92e-3, all positive) and its C = M^/R^(printed) (agrees to 1e-4 with that
reading). Criteria (exact extrema and roots): b = 0.1 eps maximum w0 = 3.16524,
Z(0) = 0.54041, eps = 0.035179, v(0) = 0.5035, C = 0.04892, R/M = 20.440; trial root
w0 = 4.05115, Z(0) = 0.75001, R/M = 25.869; E^ maximum Z(0) = 0.0891, B^ maximum Z(0) = 0.2997,
B^ = 8.48864e-4; b = 0.2, 0.3, 0.5 eps maxima at Z(0) = 0.52248, 0.51758, 0.51418 and trial
roots at 0.64417, 0.63040, 0.62192. Every number of the gravothermal README table and of
SCOPE 3.2 is reproduced to its printed digits. F21's eps_c(0) column: w0 = 3.2 prints
0.470526 against b w0/(1 - b w0) = 0.470588 (1.3e-4), as the gravothermal package says.

### V3 King model = F21 at b = 1: CONFIRMED

By hand: f = exp((E_c - E)/T_inf) - 1 with T_inf = b E_c is (e^{1 - E/E0} - 1)_+ of
2009.08163 paper.tex:635 exactly when b = 1 (E0 = E_c); y = ln E0 - mu (paper.tex:661) at
the centre is ln W_c(0) = -ln(1 - b w0). Their structure equation (paper.tex:663-672) is then
my equation in the variable ln W_c, so a "second route" through it is the same ODE; the
check is against their printed numbers. Run C-20261115-170630-1037f6a: y_max = 0.334032,
y_zero = 0.784518 (paper 0.334, 0.784, paper.tex:953; `fig_v3_king_b1.png`); at y_max
Z_c (to infinity) = 0.51191, E_b = 0.035589, R/M = 13.630, as in the equilibria README.

### V4 Exact fluid onset: CONFIRMED (eigenvalue unit mislabelled)

`v_pulsation.py`: Chandrasekhar's operator as F21 prints it (main.tex:201-206), written in
Sturm-Liouville form for u = r^2 e^{-Phi} xi, Rayleigh-Ritz with u = r^3 L_k(x), x a
stretched even variable, K = 4-20 terms. Limit check first (it could fail): Gamma = 2,
K = 100 polytrope, omega_0^2 = 0 at rho_c = 3.1824222e-3, the mass maximum at
3.1824221e-3 (M = 1.637276). Second check: the Rayleigh quotient of the trial u = r^3 gives
gamma_cr = 1.62118615274048 against F21's closed form 1.62118615274038 (main.tex:216-218) at
w0 = 4.0515: F21's closed form is exact for its trial function. Results: b = 0.1 onset at
w0 = 3.58711, Z(0) = 0.63482 (K = 10: 0.63489); b = 0.5 at w0 = 0.62795, Z(0) = 0.57904;
fixed gamma = 5/3 on the b = 0.1 structures: Z(0) = 0.77927 (all as the gravothermal README;
`fig_v4_pulsation.png`). Convergence at w0 = 4.0515: omega_0^2 = -2.570, -3.252, -3.308,
-3.3145, -3.3153 for K = 4, 8, 12, 16, 20. The README's "-3.59 against -6.7e-4 for the
trial, hatted units" differs from my -3.315 and -6.18e-4 by the factor 1/(1 - 2C) = 1.0838:
`tmb.pulsation` passes e^Phi = 1 - b w (lapse 1 at the surface, `tmb.py` line 389), whereas
the profile function and F21 use e^Phi = (1 - b w)(1 - 2C)^{1/2}. The README's statement (line 83) that
the lapse is (1 - b w)(1 - 2M/R)^{1/2} is therefore not what the eigenvalue was computed with;
omega^2 there is in the time of an observer at the surface. The zero crossing, and so every
onset above, does not depend on this normalisation.

### V4b The fluid end of the hypothesis in SCOPE 1: WRONG (upper end)

SCOPE.md lines 61-74 order the criteria as eps maximum 0.540 < adiabatic-index criterion
0.750, call the latter "the relevant (sufficient) criterion" for Kn -> 0 and predict that a
King b = 0.1 model with 0.54 < Z(0) < 0.75 survives the dynamical time when Kn_c << 1. The
trial criterion is sufficient for instability (an upper bound on omega_0^2), not for
stability; the exact fluid onset with the same gamma = 1 + p/u is Z(0) = 0.635 (V4), so models
with 0.635 < Z(0) < 0.75 are already fluid-unstable. The window of the prediction is
0.540 < Z(0) < 0.635 for F21's gas law (and moves with the law: 0.779 for gamma = 5/3, and
to lower Z(0) for a Juttner Gamma_1, which neither the track nor I computed). The track's
own gravothermal package (README section 3) has the right number; SCOPE section 1 and its
use in sections 3.4 and 5 were not updated.

### V5 Knudsen number: numbers CONFIRMED, a single definition NOT CONFIRMED

Arithmetic (run C-20261115-170630-1037f6a, ADM units): 1/(rho0_c H_c) with H = (p/(4 pi
rho^2))^{1/2}, rho the energy density (SCOPE 4) = 165.66 (King b = 0.1 eps max), 102.76
(trial root), 198.64 (King b = 1 max), 270.45 (monoenergetic max); unit G^2 M_sun/c^4 =
1.09657e-23 cm^2/g (CODATA G, c; IAU nominal GM_sun); 5 cm^2/g gives Kn_c = 4.5e-20 to
1.2e-19 at 200 M_sun for these four models (SCOPE: 4.5e-20 to 1.8e-19 over six; the
1.8e-19 is the monoenergetic 0.756 model, 1/(rho0 H) = 415 in the rerun) and 4.3e-13 to
1.1e-12 at 1.9e9 M_sun. CONVERSION.md's own definition (Moller mean free path
l = <v>/(rho0 sigma/m <v_Mol>), H = (p/(4 pi rho0^2))^{1/2}) at the King threshold: my 3D
quadrature gives <v_Mol>_c = 0.64675, <v>_c = 0.49713, rho0_c = 0.0041235, H_c = 1.43589,
Kn sigma~ = 129.82 (CONVERSION.md 129.8; rerun of `knudsen.py` the same). As predicted, the
two definitions differ: "Kn_c = 1" means sigma/m = 198.6 M^-1 in SCOPE's convention and
129.8 M^-1 in CONVERSION's, a factor 1.530 (1.532 for King b = 0.1), and the gravothermal
package uses a third, Kn_R = lambda_c/R, smaller by R/H_c = 21 (b = 0.1) to 11 (b = 1)
(`fig_v5_knudsen.png`). SPEC.md (the operator's specification) defines no Knudsen number at
all. The physical conclusion (Kn_c ~ 1e-19, a perfect fluid on the dynamical time) does not
depend on these factors; the label of every G3 run and the curve M_BH/M(Kn_c) do.

### V6 Moller-rate reference: CONFIRMED

Own sampler: kinetic energy K by rejection from a Gamma(3/2, 5/2, 7/2) mixture bounding
(1 + K) sqrt(K(K + 2)) e^{-K/theta}; 2e6 independent pairs per temperature; g - 1 formed
without cancellation. Pulls (MC - closed form)/standard error at theta = 0.001, 0.01, 0.1,
0.3, 1, 3, 10: +1.75, -0.27, -0.18, +0.51, +0.56, -0.82, +0.39; sampler check <W> against
K1/K2 + 3 theta within 1.3 standard errors; limits: ratio to sqrt(16 theta/pi) = 0.999984 at
theta = 1e-5 (1 - 25 theta/16), 1 at theta = 1e4 (`fig_v6_rate.png`). Rerun of the
package's suite: 62 passed (run C-20261115-170716-e81ba08); `test_tmb.py`: 14 PASS, ALL PASS.
Not checked by me: core's implementation of the operator (core-v0.3) against these
references; that is the box-test work of another helper.

### V7 Stiffness and cost numbers: CONFIRMED

Koda and Shapiro state P_bar < 0.1 (1101.3097 sidm1.tex:667-673) and r_k <~ lambda with
k ~ 32 (lines 551-553, 613, 680-684) [VERIFIED at the source]. With 32 macroparticles inside a
sphere of radius lambda_c = Kn_c H_c (SCOPE's H): N = 597 (monoenergetic), 1056 (King b = 1),
1426 (King b = 0.1 eps max), 1586 (trial root) at Kn_c = 1, times Kn_c^-3. Sub-steps at
dt = M/16 from the proper-time rate alpha_c rho0 (sigma/m) <v_Mol>: 1.6-3.4 at Kn_c = 0.1,
16-34 at 0.01, against the scope's 2-7 and 18-65: `knudsen_costs.py` uses the
non-relativistic t_r = Kn t_dyn/a and takes the coordinate step as proper time, which
over-estimates the rate by a v_1/<v_Mol>/alpha_c = 1.6-1.9 (conservative; then ceil).
Unit costs parsed from the AthenaK logs of the first paper (main checkout `runs/st/...`,
cpu time used / simulated span): 1.671, 3.279, 3.710, 14.171, 17.480 s per M against
1.67, 3.28, 3.71, 14.2, 17.5 (all within 0.2 percent), peak memory as quoted
(`fig_v7_costs.png`). The card-hour arithmetic of SCOPE 8 follows from its stated inputs
(6.6, 6.7, 5.6, 13.2, 155.6). What is not checked, because nothing measured it: the collision
cost and the "20 s per M" of the G3 estimate.

### V8 Source locators: CONFIRMED except one

Read at the source and saying what is quoted: 2105.05556 paper.tex:88-89, 139-141, 152,
167, 559, 612 (i = 270: stable to z_c 0.492, again 0.712-0.964, unstable beyond 0.983);
2009.08163 paper.tex:177-179, 635, 685-687, 953, 1155-1170, 1190-1193; 2602.17487 (only the
symbol C[f], intro.tex:9; "in the absence of collisions", results.tex:18; validation on
collisionless instabilities, methods.tex:196: no collision operator); 2108.11967
main.tex:274, 280, 283, 286, 324, 327; 2601.17117 SIDM_MS.tex:156, 341-344, 384 (t0 = 0.26
Gyr), 425/440/474 (445 t0), 476/481 (580 t0, 3e-8, 200 M_sun), 672 (collisional Boltzmann,
Gurian:2025zpc); gr-qc/0601112 ssevnum7.tex:229-231, 591, 694, 811-812, 1063;
astro-ph/0110561 SIDMGT_Xiv2.tex:310-321, 332, 389, 392, 983-1004; astro-ph/0111176:289-291;
2010.15132 smbh.tex:151; 2506.17641 sidmacc.tex:74 ("approximately 0.3 c"), 133;
1101.3097 sidm1.tex:410-412, 667-697, 1481-1491.
Mis-described: SCOPE 3.4 says "for core-halo models built from piecewise linear ansatz
functions the onset sits near the second maximum (paper.tex:581)". Line 581 says this for
small i, i.e. close to the k = 1 polytrope; the core-halo configurations are the larger i
(paper.tex:488), and for them (100 <= i <= 250) "the change of stability cannot be deduced
from binding energy considerations": for i = 200 the first maximum is at z_c = 0.394 and the
states are stable up to z_c = 0.787 (paper.tex:599). The scope's consequence (the eps
maximum is only a lower bound for King b = 0.1; scan to Z(0) ~ 1) is right and, read
correctly, stronger: the onset of a core-halo family can lie at twice the redshift of the
maximum and need not sit near any extremum.

## 2. The three weakest points of the plan [JUDGEMENT]

1. **The Knudsen number is not one number.** Three conventions are in use (V5): lambda/H with
   H on the energy density (SCOPE, the scan Kn_c = 0.1-100 of G3), the Moller mean free path
   over H on the rest-mass density (CONVERSION.md, the equilibria tables handed to the runs),
   lambda/R (gravothermal). The same "Kn_c = 1" is a cross-section 1.53 times larger in the
   first than in the second; the operator's specification has none. The G3 curve
   M_BH/M(Kn_c) and the comparison with the SMFP/LMFP literature (Kn = lambda/H of
   astro-ph/0110561 and 2010.15132 on rho) need one definition written into SPEC.md and
   CONVERSION.md before the first collisional run is labelled.
2. **The fluid end is neither reachable nor pinned.** The code reaches Kn_c >~ 0.1 at about
   1e6 particles (N ~ Kn^-3, V7) while the physical cores sit at Kn_c ~ 1e-19; the answer to
   the S3 question is the Kn -> 0 limit, to be taken from a GR-hydrodynamics run whose use
   is still [TO VERIFY] by core. That limit itself moves with the gas law: exact onset
   Z(0) = 0.635 for F21's gamma = 1 + p/u, 0.779 for 5/3, lower for a Juttner Gamma_1 (not
   computed), and SCOPE 1 still uses the trial root 0.750 (V4b). The prediction that frames
   the first science result therefore has the wrong fluid boundary, and the extrapolation
   from Kn = 0.1 to 0 crosses the whole conduction-dominated regime.
3. **The collisionless threshold of the chosen family has no anchor, and the first anchor
   (monoenergetic) has no theorem.** King b = 0.1 is a core-halo family (R/H_c = 21-36); for
   core-halo families 2105.05556 finds onsets unrelated to the binding-energy extrema, up to
   twice the redshift of the first maximum (V8). The G2 scan must therefore cover
   Z(0) = 0.54 to about 1 at 1000 M per model (2105.05556 paper.tex:559) with three-way
   convergence, on a budget of 45 card-hours to the next gate (decision 0014) against the
   scope's own 45 for two families and 156 for G3, with the collision cost unmeasured. G1
   criterion (a) uses the monoenergetic family, whose f is not decreasing in E (no
   stability theorem, V1), whose threshold claim rests on ST85 second-hand, and whose
   intrinsic core oscillation (period near the core radial period) overlaps the mode to be
   measured near y_c,max.

## 3. Comparison with the track's own review

Written after sections 1 and 2 were committed (aade80f), from `stage/G0/REVIEW.md`,
`stage/G0/REPORT.md`, `stage/G0/OPEN.md`, `stage/G1/STATUS.md` and `STATUS.md`. Sections 1
and 2 are left as they were written; where the track had already dealt with a point, it is
said here.

**Agreements.** Every number I recomputed agrees with the lead's cross-checks X1-X5 (runs
C-sidm-20261115-131130-3077a99, -131135-3077a99) and with the packages: monoenergetic
maximum, F21 rows and criteria, King y_max, fluid onset 0.6348 (the lead by a sign change at
two finite-element resolutions, I by a different basis and a polytrope limit), closed-form
Moller rate (the lead by 3D quadrature, I by Monte Carlo with my own sampler), log costs.
The lead's constant of REPORT decision 2, K = 1/(rho0_c H_c) with H on rho0, is 168.90 for the
King threshold model from my run's outputs as well, and its cell-based particle rule of
REPORT section 3 follows from my numbers: 20 M0/(rho0_c lambda^3) = 1699 Kn^-3 and
10 x 27 M0/(rho0_c lambda^3) = 22934 Kn^-3 (arithmetic on the outputs of run
C-20261115-170630-1037f6a). I also re-read astro-ph/0111176:289-291, which the review lists
as not re-read: it says 1e-8 to 1e-6 of the halo, as quoted.

**Differences.**

1. Knudsen number (my V5, weak point 1). The lead found the same split and fixed a
   definition in REPORT decision 2 (lambda = 1/(rho0 sigma_m), H on rho0, K = 168.9), which
   I did not know when writing section 2. So there are four values of sigma~ for
   "Kn_c = 1" on the King threshold model in the package (SCOPE 198.6, decision 2 168.9,
   CONVERSION 129.8, gravothermal lambda/R 17.8), and for the primary F21 b = 0.1 model
   K = 142.6 (my run; not printed anywhere in the package). The decision has not reached
   `collide/SPEC.md` (no Knudsen number at all; core's option takes sigma/m), CONVERSION.md
   (tables still in the l-based Kn) or SCOPE.md section 4. Weak point 1 therefore stands as a
   propagation problem, smaller than I first rated it.
2. SCOPE.md section 1 (my V4b). REVIEW lists no error in the scope's hypothesis; REPORT
   decision 3 adopts 0.6348 as the fluid anchor, so the REPORT is consistent, but the
   scoping text the REPORT relies on still calls the trial root 0.750 "the relevant
   (sufficient) criterion" for Kn -> 0 and predicts survival up to Z(0) = 0.75. Under
   decision 0012 that text is part of the package and needs the correction.
3. 2105.05556:581 (my V8). REVIEW states that every locator of SCOPE.md was re-read and is
   correct. The locator is right but the reading is not: line 581 is about small i (close to
   the k = 1 polytrope), and for the core-halo cases (100 <= i <= 250) the onset is unrelated
   to the binding-energy extrema (paper.tex:599, i = 200: maximum at z_c = 0.394, stable to
   0.787). REPORT section 1 and risk 2 quote only lines 88-89 and 612 and are correct.
4. Lapse normalisation of the pulsation eigenvalue (my V4). REVIEW: gravothermal "Wrong or
   to fix: nothing found". The eigenvalue of `tmb.pulsation` is computed with
   e^Phi = 1 - b w (tmb.py:389), not with (1 - b w)(1 - 2C)^{1/2} as README line 83 says, so
   the quoted -3.59 and -6.7e-4 are in the time of an observer at the surface (mine: -3.315,
   -6.18e-4 at infinity; ratio 1/(1 - 2C) = 1.084). No onset changes.
5. Sub-step estimate (my V7). Not covered by the review (it leaves the G2/G3 estimates
   unconfirmed). The scope's 2-7 (0.1) and 18-65 (0.01) sub-steps are conservative by
   1.6-1.9 (non-relativistic t_r and coordinate step taken as proper time).
6. Monoenergetic family (my V1, weak point 3). Not in the review: no stability theorem covers
   a non-decreasing f(E). REPORT decision 4 already moved the monoenergetic scan from G1 to
   G2 and keeps the family for verification only, which lowers the weight of this point.
7. What the review checked and I did not: core's kernels against the T0 vectors (run
   C-sidm-20261115-132624-13a77db), the T6-0 collisionless AthenaK run and its bitwise
   rerun, the 243 offline checks of the equilibria package (samplers, constraint, file
   round trip), the AthenaK read test of the King files, the RNG requirements. G1 STATUS
   says "NOT MET" (box tests T0b-T12 wait for core); I have nothing to add or remove there.

**Brief 13.3 item.** OPEN.md item 3 asks for a fresh-context verifier report
(`VERIFIER_REPORT.md`); this file is that report under the name the work package gave it.

## 4. Not checked by me

- Core's collision operator (core-v0.3) against the references: no box run of mine.
- The dynamical thresholds themselves (no AthenaK evolution was run here); V1-V3 confirm the
  binding-energy extrema only, V4 the fluid onset of F21's operator.
- The fluid onset with a Juttner Gamma_1 (OPEN item 6): not computed.
- The equilibria particle files, samplers and their AthenaK read test; the T6-0 run.
- The cost of a collision and the G3 "20 s per M" (nothing has measured them).
