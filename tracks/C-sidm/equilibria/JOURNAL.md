# JOURNAL of the work package C-sidm/equilibria (C-pre-4)

Predictions are written before each test runs; the outcome is appended afterwards, also
when the prediction fails. Labels: [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY].

## 2026-11-15 Setup

Sources read (fetched with `harness/bin/nrpic-fetch-arxiv`, untrusted data, not committed):

- gr-qc/0601112 (Andreasson and Rein), `kb-data/raw/arxiv/gr-qc_0601112/v1/src/ssevnum7.tex`.
  Ansatz `f = (E0 - E)^k_+ (L - L0)^l_+` (line 633), only shells (`L0 = 0.1`, lines
  647-649, 760-761), four cases (k, l) = (0,0), (0,1/2), (1,1/2), (0,3/2) (lines 658-665).
  Tables 1-4 (lines 762-837) list (Z_c, E_b) with stability; Z_c defined on line 694 as
  `1/sqrt(alpha(0)) - 1`, E_b = (M0 - M)/M0. The matter moments rho, j, S (lines 271-288)
  carry the factor pi/r^2 and the measure dL dw. [VERIFIED]
- 2009.08163 (Guenther, Koerner, Lebeda, Poetzl, Rein, Straub, Weber),
  `kb-data/raw/arxiv/2009.08163/v1/src/paper.tex`. Polytropes
  `f = (1 - E/E0)^k_+ (L - L0)^l_+` (line 631) and King `f = (exp(1 - E/E0) - 1)_+`
  (line 635); y = ln E0 - mu, z_c = e^{y0} - 1 measured to the boundary of the steady state
  (lines 660-689); E_b = (N - M)/N (line 922); Table "First binding energy maximizer and
  zero" (lines 948-960): King y_max = 0.334, y_zero = 0.784; (k,l,L0) = (0.5,0,0): 0.298,
  0.693; (0.5,0,0.001): 0.267, 0.583; (0.5,0.1,0.001): 0.265, 0.588. Instability sets in at
  the first binding-energy maximum for all models studied (lines 1083-1092, 1156-1160);
  King runs at y0 = 0.314, 0.324 (stable) and 0.344, 0.354 (unstable) (line 1146); the
  y_max point lies before the first turning point of the mass-radius spiral
  (lines 1160-1167). [VERIFIED]
- astro-ph/0110561 (Balberg, Shapiro, Inagaki), `.../astro-ph_0110561/v2/src/SIDMGT_Xiv2.tex`:
  lambda = 1/(rho sigma) with sigma the cross-section per unit mass (lines 307-308,
  387-389), H = [v^2/(4 pi G rho)]^{1/2} with v the one-dimensional dispersion
  (lines 351, 402-404), t_d = H/v (line 408), t_r = 1/(a rho v sigma) (lines 309-310).
  [VERIFIED]

Observation: the task names "isotropic polytropic or truncated-Maxwellian" families. Only
2009.08163 has isotropic families (King, which is the truncated Maxwellian
exp(1 - E/E0) - 1, and L0 = 0, l = 0 polytropes). gr-qc/0601112 has only shells with
L0 = 0.1, which are anisotropic (f depends on L through the cut-off and (L - L0)^l).
I build both; the shells need an anisotropic sampler. [VERIFIED from the sources above]

Note: gr-qc/0601112 Case 3 (k = 1) uses (E0 - E)^k without dividing by E0, so its
amplitude depends on how E0 is normalised (line 672-674); I do not reproduce Case 3.
Cases 1, 2, 4 have k = 0, where (E0 - E)^0_+ = (1 - E/E0)^0_+ and the family is fixed by
L0 = 0.1 and the amplitude 1. [JUDGEMENT]

## Test 1: binding-energy extrema and published tables (prediction, before the run)

Solver: static Einstein-Vlasov in Schwarzschild coordinates, y' = -e^{2 lambda}(m/r^2 +
4 pi r p) (2009.08163 eq. ssdgl, line 671), moments from f by Gauss-Jacobi quadrature.

Prediction.
1. y_max and y_zero of the four 2009.08163 models agree with the Table (lines 953-956) to
   the printed digit (|ours - paper| <= 0.5e-3, allowing 1e-3 since the paper's steady
   states were computed with explicit Euler / leap frog and Simpson, line 717-719).
2. For gr-qc/0601112 Case 1 (k = 0, l = 0, L0 = 0.1) the E_b at the listed Z_c agrees
   with Table 1 to the printed digit if Z_c is the standard 1/alpha(0) - 1; I expect the
   definition with the square root on line 694 to be a typo (it would be the redshift
   only if alpha were the square of the lapse). The maximum E_b is 0.041 between
   Z_c = 0.39 and 0.43.
3. Newtonian limit: as y0 -> 0 the isotropic polytrope k = 0.5 has the structure of the
   Lane-Emden polytrope of index n = k + 3/2 = 2: rho_c / rho_mean -> the Lane-Emden value
   computed by an independent ODE integration, to better than 1 percent at y0 = 1e-3.

Refuted if: any 2009.08163 value is off by more than 1e-3 (then my normalisation of f or
the moments is wrong, or the paper's precision is lower than printed); Case 1 E_b off by
more than 1 in the last digit for both Z_c definitions; or the Newtonian limit off by more
than 1 percent.

### Test 1, first outcome (debugging scan, not registered; the registered run follows)

- 2009.08163 Table: King y_max 0.33403 / y_zero 0.78452 (paper 0.334 / 0.784); k = 0.5:
  0.29766 / 0.69303 (0.298 / 0.693); k = 0.5, L0 = 0.001: 0.26649 / 0.58318 (0.267 /
  0.583); k = 0.5, l = 0.1, L0 = 0.001: 0.26480 / 0.58808 (0.265 / 0.588). Seven of eight
  within half a unit of the printed digit; y_max of (0.5, 0, 0.001) is 5.1e-4 off, inside
  the 1e-3 allowance of the prediction. Prediction 1 holds.
- gr-qc/0601112 Case 1: with Z_c = 1/alpha(0) - 1 the computed E_b at the listed Z_c are
  0.0357, 0.0392, 0.0413, 0.0410, 0.0401, 0.0380, 0.0279, 0.0042, -0.0226, -0.0648 against
  0.036, 0.039, 0.041, 0.041, 0.040, 0.038, 0.027, 0.004, -0.024, -0.070. With the
  definition printed on line 694 (square root) E_b would be negative from Z_c = 0.39 on:
  that definition is excluded, the square root is a misprint. Rows 0.65, 0.95, 1.1 differ
  by 0.9e-3, 1.4e-3, 5e-3; whether that is covered by the two-digit rounding of Z_c is
  checked in Test 2. Prediction 2 holds for the definition, not yet decided for the digits.

## Test 2: offline checks of the near-threshold models (prediction, before the run)

Model set (models.py): King y0 = 0.314, 0.324, y_max, 0.344, 0.354; isotropic polytrope
k = 0.5, y_max + (-0.02, -0.01, 0, 0.01, 0.02); gr-qc/0601112 Case 1 shell at Z_c = 0.39,
at its E_b maximum, at Z_c = 0.43. N = 10^4, stratified, seed 1 (production files); the
sampler checks also use N = 2 x 10^4 with both samplers, as python/tests/test_initial_data.py.

Prediction (thresholds of python/tests/test_initial_data.py where it has one):
1. psi and alpha match isotropic Schwarzschild at rbar_s to 1e-12, the slope of psi to 1e-5
   relative; areal(rbar_s) = R to 1e-10; rest mass by the isotropic integral equals N to 1e-8.
2. Isotropic models: p_T = p to 1e-12 relative. All: the anisotropic TOV equation
   p' = -mu'(rho + p) - 2(p - p_T)/r holds to 1e-6 of its largest term (p_T enters only here).
3. Hamiltonian constraint of the written tables: |Lap psi + 2 pi psi^5 rho| < 1e-6 of the
   largest source away from the matter edges (5 percent bands); Gauss form to 1e-6.
4. Stratified samples: radial and cos(theta) ECDF deviation <= 1/N; equal-mass shell counts
   exact. Moments in eight equal-mass shells (n, rho, p_r, p_t) within 4.5 standard errors
   for both samplers; radial momentum density consistent with zero. Plain Monte Carlo:
   KS p-value of the radii and of the Killing energies E against the continuum > 1e-3.
5. Every particle has E <= E0 and L >= L0; sum m W/psi equals M = 1 to < 1e-3 for the
   stratified 10^4 samples.
6. Newtonian limit: rho_c/rho_mean of the k = 0.5 polytrope at y0 = 1e-3 within 1 percent of
   the Lane-Emden n = 2 value from an independent ODE integration; also k = 1 (n = 2.5).
7. King: the first maximum of E_b lies before the first maximum of M along the sequence
   (2009.08163 lines 1160-1167).
8. gr-qc/0601112 Cases 1, 2, 4: every row's E_b lies within the range obtained from the
   rounding interval of the printed Z_c, widened by half a unit of the printed E_b.
   I expect a few high-Z_c rows to fail by ~1e-3 (paper steady states from a particle code
   [JUDGEMENT]); the E_b maximum of Case 1 lies between Z_c = 0.39 and 0.43 (the stability
   change of Table 1).

Refuted if any of 1-7 fails; for 8, failures are recorded with their size.

### Test 2, first outcome: run C-sidm-20261115-120801-38ab057 (checks of run C-sidm-20261115-120610-b4592be)

- Paper values: all eight 2009.08163 entries within 1e-3 (seven within half a printed unit).
  gr-qc/0601112: Case 1 10/10 rows, Case 2 9/10 (row Z_c = 0.39: 0.0406 vs 0.040, outside
  the rounding range by 7e-5), Case 4 8/9 (row 0.69: 0.0262 vs 0.025, outside by 1.9e-4).
  E_b maxima at Z_c = 0.3963 (Case 1), 0.4056 (Case 2), 0.4088 (Case 4). Case 1 and 2
  maxima lie between the table's last stable and first unstable A > 1 rows (0.39 / 0.43,
  0.39 / 0.42). Case 4 does not: the table has A > 1 stable at Z_c = 0.41 and 0.44, unstable
  at 0.52, while the E_b maximum is at 0.409. [JUDGEMENT] The E_b curve is flat there (0.0405
  at 0.41, 0.0403 at 0.44) and the growth time of the unstable mode diverges at the threshold,
  so a finite-time evolution can call a slightly unstable state stable; this does not
  affect the equilibria, but a threshold measured by evolution should be bracketed with
  growth-rate fits, not with stable/unstable labels.
- Newtonian limit (prediction 6): rho_c/rho_mean = 11.4096, 23.4249, 54.2424 for k = 0.5, 1,
  1.5 at y0 = 1e-3, within 1 percent of Lane-Emden n = 2, 2.5, 3 (independent ODE). Holds.
- Prediction 7 FAILED as written: the first maximum of M along the King sequence (amplitude 1)
  is at y0 = 0.0982, before the E_b maximum at 0.3340. Re-reading 2009.08163 lines 1160-1167:
  the y_max point lies "to the left of the first turning point" and states "remain stable even
  after the turning point principle would predict their instability", i.e. the paper claims
  exactly the ordering computed here; my prediction had the inequality reversed (misreading,
  not a defect of the models). The check is corrected and the run repeated.
- All per-model checks (1-5) passed for the 13 models. The particle identity sum m W/psi - 1
  is +1e-5 to +2.5e-4 for the 13 files (same seed for all, hence correlated). Over 12 seeds
  of the King threshold model at N = 10^4 (debugging, not registered): stratified mean
  -4.4e-5, standard deviation 1.7e-4; plain Monte Carlo standard deviation 4.1e-4. Statistical.
