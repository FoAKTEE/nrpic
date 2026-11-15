# Lead's review of the wave-2 helper packages of A-emd-pbh

Lead of A-emd-pbh, wave 2, 2026-11-15. Checked from the artefacts (registered outputs,
figures, journals), not from the helpers' reports.

## 0. Predictions of the lead's checks (written before the checks ran)

Two kinds of check. (i) Reruns of each package's own analysis from its registered outputs
(reproducibility): predicted to reproduce every number of the registered analysis run
exactly (same inputs, processor arithmetic). (ii) Independent re-derivations by the lead's
own script `tracks/A-emd-pbh/analysis/review_wave2.py` (own readers, own estimators, own
cycloid; no helper analysis code). Predictions for (ii), with the helper's value and the
tolerance beyond which the helper's statement counts as NOT CONFIRMED:

Expanding ball (runs_ball; core = tracked particles with initial areal radius <= 2.35 M):
- B1 exact core: a cycloid with R_max/R_i = 1.339803 and turnaround 16.893769 after the
  slice implies a bang time 2/(3 H_i) = 10.667 M before the slice (to 5e-3 M), the
  start time of data set 2t; crunch 44.454 (to 2e-3).
- B2 SR-1 first non-finite record at t in [32.5, 33.5] (dx = M/2) and [29.8, 30.8]
  (dx = M); largest |H| at t = 2, 10, 20, 30 (dx = M/2) = 0.014, 0.042, 0.051, 0.48
  within 10 per cent.
- B3 SR-1 comoving: |r/r_0 - 1| < 1e-12 and |tau - t| < 1e-10 while finite (dx = M/2).
- B4 mean core turnaround error (own parabola through three records): SR-1 dx = M/2
  -0.022 +- 0.02 M; SR-2 dx = M/2 +0.043 +- 0.02 M; SR-1 dx = M -2.50 +- 0.3 M; SR-2
  dx = M -0.82 +- 0.15 M. Mean R_max error SR-1 dx = M/2 +7e-4 +- 5e-4.
- B5 largest core |R/R_exact - 1| at tau = 16.894: SR-1 dx = M/2 6.2e-3, SR-2 dx = M/2
  7.5e-3, each within a factor 1.5 (my core set stops at 2.35, theirs at 2.4).
- B6 SR-2 dx = M/2: |alpha_c/a - 1| > 0.1 first at t in [6.3, 6.9]; largest central
  lapse 1.85 +- 0.03 (t <= 20); the probe's proper time reaches the crunch 44.454 at
  t = 35 +- 2.
- B7 card cost per cell-step 6.3e-8 (SR-1) and 7.2e-8 (SR-2) at dx = M/2, to 5 per cent.
- B8 dx = M/4 (helper's prediction R, runs_ball/JOURNAL.md entry 4, which I test; my own
  expectation in brackets): R1 both finite to t = 20 [yes]; R2 |mean dtau_ta| <= 0.02 M
  in both gauges and largest core |eps| at tau = 16.9 below 2.5e-3 (SR-1) and 3e-3 (SR-2)
  [I expect R2 to hold for SR-1 and to fail for SR-2, whose core is disturbed by the lapse
  pulse before turnaround]; R3 SR-1 largest |H| at t = 20 below 0.051 [yes]; R4 SR-2
  pulse: |alpha_c/a - 1| > 0.1 first between t = 6.0 and 7.0, peak 1.8-1.9 [yes].

Periodic box (periodic_threshold), background time t/t_H = ((1 + tau/2)^2/6)^(3/2):
- P1 S1 first non-finite record at tau = 11.70 +- 0.02, i.e. 21.9 t_H.
- P2 S2 relative Hamiltonian constraint maximum first above 1e-2 at tau = 3.2, which I
  predict is 1.2 t_H, not the 1.5 t_H written in DESIGN.md and the journal; first above
  0.1 at tau = 14.1, which I predict is 35-36 t_H, not the "about 45 t_H" of DESIGN.md
  and the helper's report. Largest value 1.73 +- 0.01.
- P3 S1 relative constraint maximum at t = 0: 0.047 +- 0.003; central lapse alpha/a at
  the last finite record 0.14 +- 0.03.
- P4 S2: smallest lapse alpha_min/a >= 0.94; t_end = 250.9 t_H; 0.17 card-s per step.

Newtonian mode (newton):
- N1 the analytic cycloid of each sampled ball (G = 1, E = V0^2/2 - M/R0) equals the
  stored reference turnaround to 1e-9.
- N2 top-hat at 128^3 with particle spacing 0.025: t_ta error +7.2e-4 and R_max error
  +4.3e-4, each within 2e-4 with my quartic-vertex estimator; error ratio 64^3 to 128^3
  between 3 and 7 (second order).
- N3 energy error to the cycloid time of R = 0.25 R_max below 2e-4 at 128^3.
- N4 first collapse of the 128^3 scan cases from the minimum of the smallest eigenvalue
  of the second-moment tensor within 3e-3 of the stored reference (the helper's estimator
  gives 2.2e-4 to 1.5e-3; mine sees the softened minimum, hence the wider band).

Closed forms (criteria2, verifier C1c):
- C1 ball ceilings at R_b H_i = 0.9 with the mean contrast capped at 0.3: mu <= 0.0688
  (q = 2), 0.0306 (q = 3); start contrast 0.218 for mu = 0.05 and 1.96 for mu = 0.45
  (q = 2). So the verifier's C1c (WRONG) is confirmed if these hold.
- C2 exact LTB central crunch (108 pi/576) e^(3 mu) mu^(-3/2): 124 t_H at mu = 0.03 and
  7.47 t_H at mu = 0.5, the values the criteria2 tables use.

What refutes my review instead of the helpers: a disagreement in (i), which would mean
the registered analysis is not reproducible from its outputs.
