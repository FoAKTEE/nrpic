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

### T1b outcome (run F-hills-20261115-130007-80eb1b9)

- Newton, same data: 1.16e-10 after 100 periods, a slow secular integration drift (figure);
  marginally above the predicted 1e-10, far below 5e-7. HRNA with mb = 1e-8: 5.03e-9, i.e. the
  amplitude scales with v^2 = mb/(4 a0). The cause named above is confirmed: the 1/Gamma^2 of
  each member makes a Newtonian-circular binary eccentric at order v^2 in HRNA (a property of
  the model with the paper's initial data, not an integration error).

### T3 outcome (runs F-hills-20261115-130058-00c6bf4, F-hills-20261115-130124-76059c5)

- 153 periods between r = 219 and 9.2 r_g. Proper period between maxima (CM proper time)
  vs 2 pi/sqrt(2k/m + M/r^3): max deviation 1.1e-4 for r_mid >= 13.4 r_g (the last midpoint
  above 10 r_g; one period spans about 4 r_g there); 1.2e-3 at r_mid = 9.2 r_g, where the
  midpoint assignment of a period that spans r = 11 to 7 dominates. Without the tidal term the
  deviation is 6.3e-4 at 13.4 r_g. Coordinate-time frequency vs the paper's f0 (1 - 2M/r):
  7.7e-6 at 200 r_g, 7.9e-4 at 13.4 r_g. Prediction (< 1e-3 for 10 <= r <= 200 after
  averaging) holds over the measured range r_mid >= 13.4 r_g; the static law (1-2M/r)^(1/2) is
  excluded by 10 percent at 13 r_g (figure t3_time_dilation.png inspected).
- This reproduces 2404 appendix B (free-fall experiment; the paper shows it as a figure only,
  appendix.tex:68 "excellent agreement").

## S1 reproduction scan of 2404 section IV (before running)

Setup 2404/article.tex:317-318, :348: mb = 1e-6, a0 = 1.013, r_t = 101.3 r_g, r0 = 50 r_t,
stop at r_cm > 150 r_t (or, here, at the CM apocentre if the CM is left bound with apocentre
> 10 r_t, or a member captured); beta = 0.1 ... 10 (100 values, the paper used 200), 400
phases in [0, pi); Newton and HRNA (Schwarzschild coordinates); prograde and retrograde.
Separation fraction s.f. = fraction of the 400 phases with E_b > 0 at the end (the paper
refines the two phase boundaries by bisection; with 400 phases the s.f. resolution is 0.0025).

Predictions from printed statements of 2404 (refutation thresholds in brackets):
P1 retrograde onset of separation: HRNA beta ~ 2, Newton beta ~ 2.5 (article.tex:475,
   :795) [refuted if the first beta with s.f. > 0.01 differs by more than 0.3 from these].
P2 prograde s.f. "essentially the same" for the two laws (article.tex:473, :788)
   [refuted if |s.f.(HRNA) - s.f.(Newton)| > 0.05 for any beta <= 9].
P3 retrograde s.f.(HRNA) exceeds Newton by up to 30 percent at fixed beta (article.tex:475,
   :795) [refuted if the largest relative excess over beta in [3, 10] is below 10 or above
   60 percent].
P4 retrograde mean v_inf of HRNA up to 30 percent (article.tex:593) or 500 km/s
   (article.tex:797) above Newton [refuted if the largest excess is below 10 percent or
   above 60 percent].
P5 prograde, beta > 9: the maximum v_inf of HRNA exceeds Newton by up to 2000 km/s
   (article.tex:591, :790) [refuted if the excess is below 500 km/s or above 4000 km/s].
P6 retrograde survivors bound to the hole after the passage (eps_cm < 0): > 50 percent of
   HRNA survivors for beta > 8 against about 30 percent for Newton (article.tex:760); all
   retrograde encounters with 0.5 <~ beta <~ 1.2 survive and essentially all of them end
   bound (article.tex:762) [refuted if the HRNA fraction for beta > 8 is below 40 percent or
   the Newtonian above 45 percent].
P7 single encounters (HRNA, beta = 5): prograde phi = 1.41 separates with r_cm(t_s) = 31 r_g;
   retrograde phi = 1.57 separates with r_cm(t_s) = 107 r_g; retrograde phi = 2.04 survives
   (article.tex:379-433). Figure 1 (beta = 8, retrograde, r0 = 10 r_t): phi = 0.5 separates,
   0.3 survives wider, 0.2 survives tighter and eccentric (article.tex:189). [Single phases
   depend on the exact release conventions (footnote at article.tex:313); a mismatch in one of
   them refutes only the claim that our conventions equal the paper's.]
   Already seen in the smoke test before this entry (not a registered run): r_cm(t_s) = 31.1
   and 107.6 r_g, but t_s = -0.020 and +0.109 T0 against the printed -0.01 and 0.08 T0.
   [VERIFIED by Barker's equation, independent of any code] On the Newtonian parabola with
   r_p = 20.26 r_g the CM needs t = sqrt(2 r_p^3/M)(D + D^3/3), D = sqrt(r/r_p - 1), i.e.
   648 M = 0.101 T0 from pericentre to r = 107 r_g, so the printed pair (0.08 T0, 107 r_g)
   cannot hold with T0 = 6406 M; both printed t_s match ours if their time unit is
   sqrt(2) T0 = 9060 M [JUDGEMENT; to be stated as an inconsistency of 2404, not resolved].

### P7 outcome (run F-hills-20261115-130724-982aba0, figures ex_*.png inspected)

- beta = 5 prograde phi = 1.41: separates, r_cm(t_s) = 31.1 r_g (paper 31), t_s = -0.020 T0
  (paper -0.01). beta = 5 retrograde phi = 1.57: separates, r_cm(t_s) = 107.6 r_g (paper 107),
  t_s = +0.109 T0 (paper 0.08); the binary's rotation reverses (L_b,z from - to +) as the paper
  says (article.tex:412). In units of sqrt(2) T0 our t_s are -0.014 and +0.077, i.e. the
  printed values; see the Barker check above.
- beta = 5 retrograde phi = 2.04: survives (paper: survives), final a = 0.594 a0, so
  E_b = -1.68 E_b0; the paper's Fig. sur-R (Figures/SR-5-130.pdf, looked at, not copied) shows
  E_b settling near -1.7 E_b0 and the same pattern of E_1, E_2 spikes after pericentre (member
  labels swapped). NOT reproduced: the paper says the rotation has reversed by the end
  (article.tex:424-425); ours keeps L_b,z < 0. [TO VERIFY: the paper's statement for this case;
  the trajectory otherwise matches.]
- Fig. 1 cases (beta = 8, retrograde, r0 = 10 r_t): phi = 0.2 survives with a = 0.0099 a0 and
  e_b = 0.992 (paper: more compact, very eccentric); phi = 0.3 survives with a = 1.20 a0
  (paper: wider); phi = 0.5 separates (paper: separates). 3 of 3.
- Summary: 6 of 6 outcomes and both printed r_cm(t_s) reproduced; the printed t_s differ by
  the factor sqrt(2) discussed above; one qualitative remark (rotation reversal at
  phi = 2.04) not reproduced.

## S2 pericentres of a few r_g (before running) [JUDGEMENT predictions]

Same binary (mb = 1e-6, a0 = 1.013, r_t = 101.3 r_g), beta = 10 ... 25 (r_p = 10.1 ... 4.05 r_g;
the parabolic CM plunges for r_p < 4 r_g, article.tex:209-215), 400 phases, both laws, both
senses. 2404 stops at beta = 10 because a/R grows (article.tex:318).
Q1 HRNA s.f. rises towards 1 for both senses (retrograde > 0.95 for beta >= 18); the
   Newtonian retrograde s.f. stays below 0.8 up to beta = 25. Refuted if the HRNA retrograde
   s.f. at beta = 20 is below 0.9.
Q2 Mean v_inf of HRNA exceeds Newton by > 20 percent for beta >= 15 in both senses. Refuted if
   the prograde excess at beta = 20 is below 10 percent.
Q3 Capture of a member (r < 2.5 r_g moving inwards) appears only for beta >~ 20 and stays below
   30 percent of the encounters at beta = 25 (HRNA).
Q4 alpha_all exceeds 0.2 for beta >= 15 in the deepest encounters: HRNA is outside the
   self-consistency regime of 2404 Eq. (9) there.

## S3 coordinate dependence of HRNA (before running)

HRNA in Cartesian Kerr-Schild coordinates with a = 0 against the Schwarzschild-coordinate runs
of S1, beta = 3, 5, 8, 10, 400 phases, both senses. Same invariant CM orbit; the pair distance
and the time slicing differ (HRNA is not covariant, article.tex:243). Tejeda et al. 2017
compared KS and BL coordinates (article.tex:285) without a printed number here.
Prediction [JUDGEMENT]: |s.f.(KS) - s.f.(Sch)| <= 0.02 for beta <= 5 and <= 0.05 at
beta = 10; mean v_inf differs by < 3 percent. Refuted if any difference is larger.
