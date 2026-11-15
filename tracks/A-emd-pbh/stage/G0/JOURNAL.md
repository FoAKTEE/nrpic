# Journal of the independent verifier of the G0 and G1 material (wave 2)

Helper "verifier" of A-emd-pbh, 2026-11-15. Read before writing this: CLAUDE.md, the charter
to "Owners", brief lines 335-365, 708-725, 834-860, decisions 0010-0015, the orchestrator's
rulings, `scope/SCOPE.md` (the scoping text, which names the claims), `expball/DERIVATION.md`
and the code and scripts named below. Not read before VERIFIER.md was written: STATUS.md,
HANDOFF.md, REVIEW.md, the JOURNAL files of the track and of its helpers, stage/G0/EVIDENCE.md,
stage/G0/OPEN.md, stage/G1/STATUS.md.

## Claims chosen (the plan rests on these)

- C1 Ball geometry and its amplitude window: 2M/R = (HR)^2 for the flat ball, no
  (anti-)trapped round sphere iff max 2m/R < 1; start a_i/a_H = (q/(R_b H_i))^2; the ball
  holds mu <= 0.031 (q = 3) or 0.069 (q = 2) at R_b H_i = 0.9, so the threshold line goes into
  the periodic box (SCOPE.md section 4; decision 0013).
- C2 Amplitude conventions: deltabar_ent = 12 mu/(5 e_E) = 0.883 mu, delta_c = 12 mu/5,
  2M/R_ta = (5/3) deltabar_ent (SCOPE.md sections 3 and 10.1).
- C3 Hoop line: h-hat(0.2, 0) = 0.452, i.e. the Zel'dovich-hoop criterion of arXiv:2609.14218
  requires mu > 0.45 at e = 0.2; h-hat(e, 0) runs 0.22-0.48 over e = 0.05-0.3 (T1).
- C4 H1 timing: top-hat collapse time of the r_m shell, mu_fd(250 t_H) = 0.048; the
  paper's particle runs end at 250 t_H; horizon for mu >= 0.05, none for mu <= 0.045 at
  e = 0.2 (MDPBH.tex L1102-1103); prediction "mu = 0.045 forms a horizon near 239 t_H".
- C5 Ball initial data (A-pre-1, G1 criterion): the slice data satisfy both constraints
  exactly; the finite-difference residuals converge at the order of the differences (2 and
  4) where the data are smooth; the turnaround and horizon times of the core are those of
  the cycloid with simultaneous bang time.
- C6 Dispersion axis and particle number: s_c between 0.548 (virial, arXiv:2507.18312 L542)
  and 1.5 (arXiv:2211.13950 L358), independent of the amplitude; lattice loading needs
  N >= 1e5 at deltabar_ent >= 0.04 and >= 2e6 at 0.01; random sampling 75-200 times more.
- C7 G2 horizon-mass target: Delta M/M_ADM <~ 1e-3 (arXiv:2611.12831 main.tex:945) and RMS
  2.061e-3, 9.362e-4, 7.347e-4 (main.tex:1484).
- C8 (if time) compute model: SR-1 0.15 card-hours and the first scan ~155 card-hours.

## Predictions (written before any of my runs)

V1 (C1). My own derivation: R_b H_i = q r_m (aH)_i = q (a_H/a_i)^(1/2) because aH ~ a^(-1/2)
in Einstein-de Sitter and r_m (aH)_H = 1, so a_i/a_H = (q/(R_b H_i))^2; the mean contrast in
r_m at the start is 0.883 mu (a_i/a_H). Predicted ceilings with the cap 0.3: 0.0306 (q = 3),
0.0688 (q = 2) at R_b H_i = 0.9, and e_E = 2.718 times less with the central cap. Refuted if
my numbers differ from SCOPE's by more than 2 %. Further prediction (my own reading, to be
tested on the figure `scope/results/fig_design.png`): at q = 2 the mean-cap ceiling 0.069 lies
ABOVE the paper's particle bracket (0.045, 0.05], so the statement "the ball holds only
amplitudes below the comparison amplitudes" is true for the hoop and fluid amplitudes but
not for the particle bracket at q = 2. Refuted if the q = 2 solid curve of fig_design.png
stays below 0.045 at R_b H_i = 0.9. On the slices of data sets 1 and 2 of expball, max 2m/R
equals (H R_b)^2 = 0.25 (flat, H R_b = 0.5) and stays below 1 for the bound core; refuted if
Ball.summary() reports an anti-trapped sphere or a different maximum.

V2 (C2). Independent computation of deltabar(r) from ln Psi by a different route (closed
form by sympy: deltabar(r) = -(4/5)(aH)^-2 (3/r) d/dr ln Psi) gives 12 mu/(5 e_E) at
k^2 r^2 = 6 and 12 mu/5 at the centre; r_m from the compaction-function maximum equals
sqrt(6)/k. The turnaround compactness from an exact LTB shell (simultaneous bang, my own
cycloid code, not expball's) tends to (5/3) deltabar_ent as the start contrast -> 0, with an
error proportional to the start contrast. Refuted if the limit differs from 5/3 by more than
1e-3 or the convention factors differ.

V3 (C3). An independent hoop computation (Zel'dovich ellipsoid at the first caustic,
perimeter of the pancake ellipse by direct quadrature of the arc length, mass of the
Lagrangian sphere r_m, h = C/(4 pi M)) gives mu_c(0.2, 0) = 0.452; the other convention of the
elliptic integral (parameter instead of modulus) would give 0.42. The blue line of
`thre_p0.pdf` of arXiv:2609.14218 (rendered here, read by eye) sits at 0.45 +- 0.02 at
e = 0.2. Refuted if the quadrature differs from h-hat by more than 1e-4 or the paper's line
reads closer to 0.42.

V4 (C4). mu_fd(250) = 1.686 e_E/(2.4 * 250^(2/3)) = 0.0481; t_c(r_m) at mu = 0.045 = 276 t_H, so
"0.86 t_c = 239 t_H". In `alpha.pdf` of arXiv:2609.14218 I expect the mu = 0.045 curve to run
beyond 239 t_H (the particle figure is at 245 t_H, MDPBH.tex L1131) with alpha_0 not
collapsing. If so, the H1 prediction with the median ratio 0.86 is already contradicted by
the published curve, and H1 survives only with the ratio near 1 for that amplitude.
Refuted (in the track's favour) if the mu = 0.045 curve ends before 239 t_H.

V5 (C5). (a) The track's pytest suite passes; (b) the track's convergence script reproduces
orders near 2 and 4 in the smooth regions (as written in DERIVATION.md section 7); (c) my
own 3D Cartesian constraint check (Christoffel symbols of psi^4 delta_ij written by hand,
np.gradient second-order differences, independent of mesh.py) on data set 2 (smooth top-hat
core, delta_c = 1, R1 = 0.3 R_b, R2 = 0.75 R_b, H R_b = 0.5, C^4 edge taper) converges at
order 2 in both constraints away from the centre; (d) breaking it: with KL replaced by
-KL in the core, or with the momentum constraint evaluated on a top-hat in E, the residual
does not converge (stays O(1) of 6H^2); (e) my own cycloid times (turnaround, R = 2m) of
the core from (m, E) agree with expball.exact to 1e-10 relative. Refuted by any order off
by more than 0.2 in the smooth region or a time mismatch above 1e-8.

V6 (C6). s_c(virial) = sqrt(3/10) = 0.548, s_c(2211.13950) = 3/2, both independent of the
amplitude; N_lattice(0.1 b_BH) = 7.9e4 at deltabar = 0.04, 1.8e6 at 0.01; N_random/N_lattice
= 74 and 210. Refuted if the source lines give other coefficients.

V7 (C7). Locators main.tex:945 and :1484 contain the quoted numbers. Already read before
this entry (it is a locator check, no run): both found as quoted; main.tex:945 also says the
horizon-mass error does NOT fall monotonically with spatial resolution at fixed N.

## Outcomes

(appended below after each run)

### Development of the script (not registered; scratch/A-emd-pbh/tmp/verifier_smoke*)

Three errors of my own, caught by smoke tests before the registered run: (1) a math label
`\sqrt6` that matplotlib does not parse; (2) in V1 I inverted R_b H_i = q (a_H/a_i)^(1/2) with the
wrong sign of the exponent (q x^(-1/2)), which gave ceilings of 1.7 and 3.8 instead of 0.069 and
0.031; corrected to q x^(1/2) before any number was used; (3) a brentq tolerance below scipy's
floor. The first version of OwnBall also put rho = rho_b in the core (corrected to
rho_b (1 + Delta + R Delta'/3) before the registered run), and interpolated (m, E) linearly for
the shell times (2e-6 relative error; replaced by evaluation at the shell).

### Run A-20261115-160935-41f721d (local, 4 cores, 37 s; outputs scratch/A-emd-pbh/A-20261115-160935-41f721d/)

V1 outcome: as predicted. mu_max = 0.03058 (q = 3) and 0.06881 (q = 2) at R_b H_i = 0.9 with the
mean cap 0.3; central cap 0.02531 (q = 2), e_E times less. The q = 2 mean-cap ceiling is ABOVE
the particle bracket (0.045, 0.05] for R_b H_i > 0.75 (fig_V1_ball_window.png, looked at): to
hold mu = 0.05 at q = 2 the start mean contrast must be 0.218, at q = 3 0.49; to hold the hoop
value mu = 0.45 it must be 1.96 (q = 2). Prediction confirmed: the ball cannot hold the hoop and
fluid amplitudes, but at q = 2 it does hold the particle bracket of arXiv:2609.14218.
Anti-trapping: own max 2m/R = 0.23612 at R = 8.26 (data set 2t), equal to the track's
Ball.summary() 0.23612; below 1, so no anti-trapped round sphere. Confirmed.

V2 outcome: as predicted. sympy: deltabar(r) = (12/5) mu exp(-k^2 r^2/6) at aH = k/sqrt6; r_m =
sqrt6/k from both the compaction maximum and the paper's condition (MDPBH.tex L709-711);
deltabar(r_m)/mu = 12/(5 e_E) = 0.88291, delta_c/mu = 2.4, ratio e_E. Exact shells: (2m/R_ta) /
deltabar_ent = 1.66643 at Delta_i = 1e-4 (limit 5/3, error linear in Delta_i: 1.6438 at 0.1);
Delta_i (t_c/t_i)^(2/3) -> 1.68661 against 1.68647. fig_V2_conventions.png looked at.

V3 outcome: as predicted. Pancake perimeter by quadrature gives mu_c(e, 0) = 0.21861, 0.34215,
0.41254, 0.45175, 0.47203, 0.48053 at e = 0.05 ... 0.3, equal to h-hat with E of modulus
sqrt(1 - x^2) to 5e-15; the parameter convention would give 0.4221 at e = 0.2. The rendered
thre_p0.pdf (src_render/thre_p0.png, read by eye) has the "Analytic criterion" line at about
0.45 at e = 0.2 and 0.34 at e = 0.1, i.e. the modulus convention. Prolate/oblate:
mu_c(0.2, -0.1) = 0.4551, mu_c(0.2, 0.1) = 0.4565.

V4 outcome: arithmetic as predicted (mu_fd(250) = 0.04813, t_c(r_m; 0.045) = 276.6 t_H, 0.86 t_c =
237.8). The rendered alpha.pdf (src_render/alpha.png, read by eye) shows: the mu = 0.045 curve
runs to the right edge of the plot at 250 t_H; alpha_0 has a sharp dip at about 205-212 t_H
(from ~13.5 to ~9) and then stays at 9-9.5 to 250 t_H, with no collapse near 238 t_H. So the
sub-prediction "mu = 0.045 forms a horizon near 239 t_H" of SCOPE.md section 2 is contradicted
by the published curve (my prediction holds). The mu = 0.05 curve has the same two-stage
shape: a first drop at ~178-183 t_H, a plateau, the final collapse ending at ~218 t_H (ratio
final/first ~1.2). My read-offs of the steep drops: mu = 0.15: 46; 0.10: 74; 0.075: 106; 0.06:
~145 (ends 152); 0.05: 180 (first), 218 (final); 0.3, e = 0: 12; 0.3, e = 0.2: gradual,
ends at 25. These agree with the track's by-eye values (24, 46, 74, 106, 144, 199). New
observation [JUDGEMENT]: the first dip of the 0.045 curve sits at ~0.76 t_c(r_m), as the first
drop of the 0.05 curve (180/236 = 0.76); the 0.05 run collapsed ~1.2 times later; the same
factor puts a 0.045 collapse at ~250-255 t_H, just beyond the plotted end. H1 therefore
survives, but its timing must be predicted from the two-stage shape, not from 0.86 t_c.

V6 outcome: as predicted. s_c = 0.5477 (virial) and 1.5000 (2211.13950); N_lattice = 7.9e4,
3.7e5, 1.78e6 at deltabar = 0.04, 0.02, 0.01; N_random/N_lattice = 74, 125, 209.

V5 outcome: (a) not run yet (pytest, below). (b) The track's own test function
(expball.mesh.residuals) on data set 2t (taper 0.1875 R_b, octant L = 1.25 R_b, all cells):
order 2: H 1.94, 1.98; M 1.78, 1.93; order 4: H 3.39, 3.75; M 2.82, 3.43 (N = 32, 64, 128).
Order 2 within 0.2 of 2 at the finest pair; order 4 still approaching 4 from below at N = 128.
(c) My own construction (built from Delta(R) with my own hypergeometric inversion, spline
derivatives, conformal quadrature) equals the table that AthenaK reads (scratch run
A-emd-pbh-20261115-130609-947c898) to 3e-15 in psi, 5e-11 H in KL, 2e-14 H in KT, 8e-15 in betar;
alpha = 1 in every row; KL = KT = -0.0445 < 0 at the centre (expanding in the code's sign). My
own finite differences on the full box, r < 1.15 R_b, N = 32 ... 128: H L2/6H^2 = 2.5e-2 ...
1.85e-3, orders 1.87, 1.78, 1.93, 1.96; M 9.7e-2 ... 1.03e-2, orders 1.38, 1.55, 1.74, 1.85
(approaching 2). (d) Breaking: KL -> -KL plateaus at H 1.09, M 1.89 (order 0); the "static
metric" KL (= -v' + v E'/(1+2E)) plateaus at H 0.021, M 0.040 (orders -> 0): the checker sees
the error, and KL = -dv/dR is the right one. K -> -K (time reverse) gives residuals identical to
the true data to all digits: the constraint test cannot tell an expanding from a collapsing
ball; the sign is fixed only by the convention and the first evolution step. (e) Shell times:
own cycloid core tau_ta = 16.89376895004044, tau_c = 44.45420456674754, core-edge tau_AH =
44.38146574194694 (identical to the track's predictions to all printed digits); first trapped
shell by minimisation: tau_AH = 44.34927 at R_i = 2.742 (m = 0.0805), the track's 400-shell grid
gives 44.34942 at R_i = 2.731 (m = 0.0796): agreement to 1.5e-4 in time, the grid is coarse.
Figures fig_V5_constraints.png (the blue "own" curve is hidden under the identical green
time-reversed one; redrawn in the next run) and fig_V5_radial.png looked at.

### Prediction for the second run (before it)

Same script with the figure fixes, the track's test to N = 256 (octant) and my own check to
N = 192: order 4 of the track's test reaches 3.8-3.9 at 128 -> 256 (DERIVATION.md section 7 says
3.92 H and 3.79 M for the smoothed top-hat without taper); my own order-2 check reaches
1.9 or more in M. Refuted if the order-4 momentum order stays below 3.6 at the finest pair.
pytest of expball (run separately): all tests pass; refuted by any failure.

### Run A-20261115-161253-e506d90 (pytest of expball, local, 4 cores; output in its run.log)

Outcome: 32 passed in 19 s (run with -B and no cache provider, temporary files in
scratch/A-emd-pbh/tmp/pytest_verifier, nothing written into the package). As predicted. No
figure: a pass/fail suite; the constraint figures of the next run cover what it tests.

### Run A-20261115-161239-1c41333 (second pass, local, 4 cores, 122 s)

V1-V4, V6: same numbers as the first run (the code paths did not change). V4 adds my read-offs
as data: ratios t_drop/t_c(r_m) = 1.01, 0.89, 0.82, 0.81, 0.76 for mu = 0.15, 0.10, 0.075,
0.06, 0.05 (first drop of 0.05); the 0.045 dip at 0.75 t_c(r_m); the two-stage scaling puts a
0.045 collapse at 252 t_H. fig_V4_timing.png looked at: the read-offs lie between 0.76 and 1.01
of the top-hat curve of the r_m shell, the 0.86 line passes through the middle, and the 0.045
cross sits below the 0.86 line, where the curve shows no collapse.

V5 outcome: as predicted. Track's test on data set 2t to N = 256 (octant): order 2 H 1.94,
1.98, 2.00; M 1.78, 1.93, 1.98; order 4 H 3.39, 3.75, 3.92; M 2.82, 3.43, 3.79 (all cells,
L2). My own check to N = 192 (full box, r < 1.15 R_b): H orders 1.87, 1.78, 1.93, 1.96, 1.97,
1.98; M 1.38, 1.55, 1.74, 1.85, 1.90, 1.93; H L2/6H^2 = 8.3e-4 and M 4.7e-3 at h = R_b/77.
Broken variants: KL -> -KL flat at 1.09 / 1.89; static-metric KL flat at 0.0216 / 0.0399;
K -> -K identical to the true data. fig_V5_constraints.png and fig_V5_track_test_rerun.png
looked at (straight lines of slope 2 and 4 at the fine end; the broken variants flat).
Order 4 of the track's test is reached only at N = 256 (3.92 H, 3.79 M), within 0.2 of 4 for
H and 0.21 short for M; order 2 within 0.07 at the finest pair.

### After VERIFIER.md sections 1-3 were committed (0ac9951)

Read the lead's journal entry (L1-L8), STATUS.md, RISKS.md, stage/G0/EVIDENCE.md, OPEN.md,
stage/G1/STATUS.md and the proposal to orch; wrote VERIFIER.md section 4. One of my points had
to be qualified by what I read: weak point 3 (a 0.161 M horizon on M/2-M/8 meshes) does not
apply to SR-1, whose geodesic slicing keeps the coordinates comoving (horizon at coordinate
radius ~2.7 M); it stays for SR-2 and moving-puncture gauges. Recorded as an amendment, the
original text kept. No other conclusion changed.
