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
