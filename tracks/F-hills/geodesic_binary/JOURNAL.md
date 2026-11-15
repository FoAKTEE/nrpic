# JOURNAL of geodesic_binary (F-pre-2)

Predictions are written before a test runs; outcomes are appended below them, also when a
prediction fails. Locators: `2404` = kb-data/raw/arxiv/2404.16270/v1/src, `2402` =
kb-data/raw/arxiv/2402.02178/v1/src.

## 2026-11-15 setup

- [VERIFIED] Model: 2404/article.tex:222-267 (HRNA, Eq. CoordtEqs at :246-256, Gamma at
  :258-261, pair potential at :236-241); initial data 2404/appendix.tex:138-179; protocol
  2404/article.tex:300-318 (mb = 1e-6 M, a0 = 1.013 r_g, r_t = 101.3 r_g, r0 = 50 r_t, stop at
  r_cm > 150 r_t, 400 phases in [0, pi], beta in [0.1, 10]); separation criterion E_b > 0 at the
  end (:377); s.f. definition (:456-459); v_inf = sqrt(2 max(E1, E2)) (:584-587).
- [VERIFIED] Sign: 2404/article.tex:229 writes f = +P grad Phi, which with Phi < 0 would be
  repulsive; Eq. CoordtEqs (:248-256) carries the attractive sign. The code follows CoordtEqs.
- [VERIFIED] 2404/appendix.tex:145 places member 1 at x_cm + (m1/mb) a; for m1 = m2 this equals
  the CM-correct (m2/mb) a used in the code.
- [JUDGEMENT] The coordinates of 2404 are Schwarzschild (areal radius) in Cartesian form: the
  initial CM velocity (2404/appendix.tex:175-179) is the Schwarzschild-coordinate dr/dt and
  r dphi/dt, and the pair distance is "Euclidean" (:241). The paper does not name the
  coordinates explicitly.
- [JUDGEMENT] Decision 0010: the HRNA model is an ODE reference solution (two point masses,
  analytic background metric), allowed outside athenak/src. No REBOUND (2404 used REBOUND with
  IAS15, article.tex:350); the integrator here is a DOP853 written for this package.
- [VERIFIED] 2402.02178 uses a different model: a Fermi-normal frame along the CM geodesic with
  gravito-electromagnetic tidal forces and PN terms (2402/main.tex:293-341), not the exact
  acceleration of each member. A Kerr HRNA is therefore our own extension (Tejeda et al. 2017,
  cited at 2404/article.tex:154, ran HRNA in Kerr), and 2402 can be compared only on
  shared observables.

## T1 metric checks and flat-space binary (before running)

Prediction: g g^-1 = identity to 1e-14; d_k g from the closed forms agrees with fourth-order
central differences to 1e-9 relative; the CKS metric agrees with python/nrpic/kerr.py g4_cks to
1e-14; with M = 0 the HRNA equations reduce to Newton and a circular binary keeps its separation
to 1e-10 over 100 periods. Refuted by any larger deviation.

## T2 single-body limit against python/nrpic/geodesic.py (before running)

Setup: pair force off (m1 = m2 = 0); two members on independent geodesics: (a) Schwarzschild
coordinates, parabolic orbit with r_p = 10 r_g from r = 200 r_g through pericentre to 200 r_g,
plus a bound eccentric orbit; (b) Cartesian Kerr-Schild, a = 0.9, same two orbit types.
Reference: python/nrpic/geodesic.py integrate ('bl' with a = 0 for (a), 'cks' for (b)) at
rtol = 1e-13, sampled at the same coordinate times.
Prediction: position differences below 1e-7 r_g over the run, relative drift of E and L_z
below 1e-11 at rtol = 1e-12. Refuted by a difference that grows above 1e-6 r_g or a drift of
the invariants above 1e-10.

## T3 time dilation of a free-falling oscillator, 2404 appendix B (before running)

Setup of 2404/appendix.tex:37-68: two equal masses joined by Phi = k/2 (|x2 - x1| - l0)^2,
k/m = 1/5, l0 = 3 r_g/40, elongated initially to 4 l0/3, aligned perpendicular to the radial
direction, the CM falling radially from rest at infinity (E = 1, L = 0), Schwarzschild
coordinates. Frequency from successive maxima of the separation.
Prediction: the measured coordinate-time frequency follows f0 (1 - 2M/r) (2404/appendix.tex:62-66)
corrected by the transverse tide, f = f0 (1 - 2M/r) sqrt(1 + (M/r^3)/(2k/m)) [JUDGEMENT: the
transverse tidal eigenvalue M/r^3 of a radial geodesic], with relative deviation below 1e-3
between r = 200 and 10 r_g once the prediction is averaged over each measured period. Refuted if
the deviation exceeds 1e-2, or if it follows (1 - 2M/r)^(1/2) or no dilation instead.

### T1 outcome (run F-hills-20261115-125915-9518508)

- Metric identities 4.4e-16, closed-form d_k g vs fourth-order differences 7e-11 to 1.0e-10
  relative, CKS metric vs python/nrpic g4_cks 2.2e-16: prediction holds.
- Flat-space binary (M = 0, HRNA, mb = 1e-6): the separation oscillates with relative amplitude
  5.0e-7 for 100 periods, without secular growth. The prediction (1e-10) FAILED.
  Candidate cause, not yet tested: HRNA divides the pair force by Gamma^2 = 1/(1 - v^2) of each
  member (2404/article.tex:250), so a binary started with the Newtonian circular speed
  (v^2 = 2.5e-7 per member) is not circular in HRNA; expected amplitude ~ 2 v^2 = 5e-7.
- T1b prediction (before running): Newton with the same data stays circular to < 1e-10; HRNA
  with mb = 1e-8 (v^2 = 2.5e-9) gives amplitude 5e-9. Refuted if Newton shows the same 5e-7 or
  if the HRNA amplitude does not scale with mb.

### T2 outcome (run F-hills-20261115-125918-9518508)

- Position differences from python/nrpic/geodesic.py at the same coordinate times: Schwarzschild
  3.5e-9 r_g (parabolic, r_p = 10) and 2.7e-8 r_g (bound 8-30 r_g); Kerr a = 0.9 (CKS) 2.8e-9 and
  3.4e-8 r_g (inclined bound orbit). Prediction (< 1e-7 r_g) holds.
- Invariant drifts: E 1.7e-13 to 1.4e-12, L_z 1.6e-12 to 1.02e-11. The bound Kerr orbit's L_z
  drift (1.02e-11) is marginally above the predicted 1e-11 and below the refutation level 1e-10.
- Figure t2_geodesic_limit.png inspected: the differences grow smoothly (no jumps at pericentre).
