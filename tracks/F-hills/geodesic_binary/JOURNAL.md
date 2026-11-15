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

## S4 equatorial Kerr, 2404 binary (before running) [JUDGEMENT predictions]

HRNA in Cartesian Kerr-Schild coordinates, spin a = +0.9 (CM orbit prograde with respect to the
hole) and a = -0.9 (retrograde), mb = 1e-6, a0 = 1.013, beta = 3, 5, 8, 10, 12, 15 (r_p = 33.8
to 6.75 r_g; the parabolic CM plunges below r_mb = 1.73 and 5.66 r_g respectively), 400 phases,
both binary senses; a = 0 from S3 (same coordinates).
K1 Retrograde binaries: s.f.(a = -0.9) > s.f.(a = 0) > s.f.(a = +0.9) for beta >= 5, since the
   relativistic increase of the retrograde s.f. found in 2404 should grow when the CM orbit
   counter-rotates with the hole (larger r_mb, stronger precession at fixed r_p) and shrink
   when it co-rotates. Refuted if the ordering fails at beta >= 8 by more than 0.02.
K2 Prograde binaries: |s.f.(a = +-0.9) - s.f.(a = 0)| < 0.03 for beta <= 10.
K3 2402.02178 is not reproduced here: its claim (2402/main.tex:592-597) concerns the survival
   boundary of inclined binaries at beta > 0.9, which needs inclined initial data, and its model
   (Fermi frame, tidal plus PN forces) differs from HRNA. Open item.

## C1 tolerance and C2 release-radius convergence (before running)

C1: beta = 3, 5, 8, both laws and senses, 400 phases, rtol = 1e-10 and 1e-13 against S1
(rtol = 1e-12). Prediction: s.f. differences <= 0.005 (2 phases of 400); mean v_inf differs by
< 0.5 percent. Refuted if any s.f. difference exceeds 0.01.
C2: beta = 4.7 (the case of 2404 appendix C, appendix.tex:212), r0 = 20, 50, 70 r_t.
2404 reports a relative s.f. variation of ~1e-3 (Newton, 1PN) and a stall at ~1e-2 (HRNA) for
r0 >~ 20 r_t (appendix.tex:216-217), without an explanation (:222). Prediction: Newton varies
by <= 0.005 (our phase resolution), HRNA by ~1e-2 relative. Candidate cause [JUDGEMENT, to be
tested only if C2 shows the HRNA variation]: the Newtonian-circular initial binary is not
circular under HRNA at r0 (T1b: the pair force is divided by Gamma^2, Gamma^2 - 1 ~ 4M/r0 + v^2
at release), giving an r0-dependent initial eccentricity of order 1e-3.

### S4 first attempt failed (run F-hills-20261115-131944-360a12e)

ZeroDivisionError in the end-of-run energy of the "virtual particle at the CM" after member
captures (the flat-space midpoint of a captured and an escaping member can sit where the
Kerr-Schild metric is singular). Fixed: these energies are NaN when not computable; after a
capture the stop test follows the surviving member (r > 150 r_t outwards, or turning around
beyond 10 r_t). Runs without captures are unaffected (checked: beta = 5, phi = 1.41 gives the
same r_cm(t_s) = 31.11 r_g and eps1 to all digits).

## T4 HRNA force in the 3+1 (x, u_i) form of the NRPIC pushers (before running)

Derivation (tests/t4_force_31.py docstring): du_i/dt = geodesic part + (alpha/W)(A_i +
u_i U^j A_j), U^j = gamma^jk u_k - W beta^j/alpha, A_i the Newtonian pair acceleration. This is
the form an AthenaK implementation would use. Test: the beta = 5, phi = 1.41 prograde
encounter released at 5 r_t, Cartesian Kerr-Schild with a = 0 and 0.9, integrated with scipy
DOP853 on python/nrpic/kerr.py, compared with hrna.py at the same coordinate times.
Prediction: the relative orbit x1 - x2 agrees to < 1e-7 a0 and member positions to < 1e-6 r_g.
Refuted if the relative-orbit difference exceeds 1e-5 a0 (a wrong 1/Gamma^2, projection or
index placement changes the internal orbit at order v^2 ~ 1e-2 of the separation or more).

### T4 outcome (run F-hills-20261115-133219-90eeecd, figure t4_force_31.png inspected)

Relative orbit: max difference 4.2e-8 a0 (a = 0) and 4.3e-8 a0 (a = 0.9); member 1 position
1.8e-8 and 1.9e-8 r_g, over the whole passage (the binary separates in both). Prediction holds:
the 3+1 form with the projected force is the same model as Eq. CoordtEqs, to integration error.

### P7 rerun with the paper's units (run F-hills-20261115-134350-d16b473, figures/ex_*.png)

Same trajectories (identical numbers). For beta = 5, retrograde, phi = 2.04: E_b goes from
-1 to -1.68 E_b0 and E_cm from 0 to +0.17 E_b0 across pericentre; the paper's panel
(Figures/SR-5-130.pdf, bottom right, looked at only) shows the same two levels (about -1.7 and
+0.15 to +0.2). The remaining difference to the text is only the remark on rotation reversal.

### S4 outcome (run F-hills-20261115-133124-c799a81; a = 0 from S3, run F-hills-20261115-130922-634fb86)

Separation fraction (200 phases for a = +-0.9, 400 for a = 0):

| beta (r_p/r_g) | pro a=+0.9 | pro a=0 | pro a=-0.9 | retro a=+0.9 | retro a=0 | retro a=-0.9 |
|---|---|---|---|---|---|---|
| 3 (33.8) | 0.975 | 0.985 | 0.975 | 0.475 | 0.512 | 0.550 |
| 5 (20.3) | 0.985 | 0.990 | 0.995 | 0.645 | 0.710 | 0.750 |
| 8 (12.7) | 1.000 | 0.998 | 0.995 | 0.805 | 0.860 | 0.905 |
| 10 (10.1) | 1.000 | 0.998 | 0.990 | 0.865 | 0.912 | 0.965 |
| 12 (8.4) | 0.990 | - | 0.995 | 0.890 | - | 0.985 |
| 15 (6.8) | 1.000 | - | 1.000 | 0.930 | - | 0.995 |

K1 holds at every beta (retrograde binaries: a = -0.9 > a = 0 > a = +0.9, by 0.04-0.05 on each
side at beta >= 5). K2 holds (prograde differences <= 0.01). A member is captured in 64.5
(prograde) and 34 percent (retrograde) of the a = -0.9, beta = 15 encounters (r_p = 6.75 r_g,
just outside r_mb = 5.66 r_g), and in at most 0.5 percent elsewhere.
Abnormal endings: 6 of 4800 runs stopped on step-size underflow, all near-head-on collisions of
the point masses (a_min = 4e-9 to 1e-7 a0) close to pericentre, where the Newtonian pair force
drives the members to near-light speed and the model is meaningless; 2 runs lost both members
(the same pathology); 6 runs (a = -0.9, retrograde, beta = 15, separated) reached t_max. These
14 runs are reported, not removed; they change no s.f. above by more than 0.005.

### S2 outcome (run F-hills-20261115-134255-a3c22f8; 48000 encounters, 859 s on 6 cores)

| beta | r_p/r_g | s.f. pro N / H | s.f. retro N / H | <v_inf> pro N / H [km/s] | <v_inf> retro N / H | captured H pro / retro |
|---|---|---|---|---|---|---|
| 10.5 | 9.65 | 0.988 / 0.998 | 0.585 / 0.923 | 3558 / 3643 | 2346 / 2512 | 0 / 0 |
| 15 | 6.75 | 0.980 / 0.998 | 0.618 / 0.983 | 3452 / 3571 | 2466 / 2483 | 0 / 0 |
| 18 | 5.63 | 0.973 / 0.995 | 0.635 / 0.993 | 3373 / 3406 | 2504 / 2478 | 0 / 0 |
| 20 | 5.06 | 0.965 / 0.998 | 0.640 / 0.998 | 3312 / 3393 | 2540 / 2464 | 0.158 / 0 |
| 22 | 4.60 | 0.958 / 1.000 | 0.645 / 0.998 | 3272 / 3380 | 2567 / 1384 | 0.775 / 0.688 |
| 24 | 4.22 | 0.950 / 1.000 | 0.653 / 1.000 | 3245 / 3367 | 2581 / 479 | 0.930 / 0.980 |
| 25 | 4.05 | 0.948 / 1.000 | 0.655 / 1.000 | 3233 / 3308 | 2590 / - | 0.975 / 1.000 |

(N Newton, H HRNA; <v_inf> over separated encounters whose escaping member is unbound, also
when the companion was captured; "captured": a member crossed r < 2.5 r_g inwards, point-mass
near-collisions excluded.)
- Q1 holds: HRNA retrograde s.f. >= 0.9925 for beta >= 18 (0.9975 at beta = 20); the Newtonian
  retrograde s.f. stays <= 0.655 up to beta = 25.
- Q2 FAILED: the mean ejection speed of HRNA is within +0.4 to +3 percent of Newton (prograde)
  for beta = 15-25 and equal or lower (retrograde, -3 percent at beta = 20); the predicted
  > 20 percent excess does not exist in the mean. At beta >= 22 the retrograde mean drops
  (1384, 479 km/s) because most encounters now lose a member to the hole and the escaping one
  is barely unbound.
- Q3 FAILED in magnitude: captures start where predicted (beta = 20 prograde, 21 retrograde)
  but reach 0.78 / 0.69 at beta = 22 and 0.975 / 1.0 at beta = 25 (predicted < 0.3). Below
  r_p ~ 5 r_g the Hills outcome "one member bound, one ejected" is replaced by "one member
  captured by the hole, the other ejected or bound".
- Q4 partly: alpha_all at beta = 15 reaches 0.47 (median 0.34) for prograde, only 0.15 (median
  0.13) for retrograde encounters. Prograde HRNA results at beta >~ 10 are outside the
  self-consistency regime a/R << 1 of 2404 Eq. (9).
- Abnormal endings: 97 HRNA retrograde runs at beta = 21-24 reached t_max; all 97 are separated
  pairs with one bound and one unbound member that left in very different directions after
  whirling near r_p, so the flat-space CM never passed 150 r_t (outcome and energies final).
  18 runs lost both members; 4 stopped on step underflow and 74 of 48000 have a_min < 1e-4 a0
  (point-mass near-collisions, excluded from captures and speeds, kept in the s.f.).

### S1 outcome (run F-hills-20261115-130405-ce17dcf, 160000 encounters, 4695 s on 8 cores;
### analysis F-hills-20261115-142554-c10b371, figures s1_sepfrac, s1_vinf, s1_bound inspected)

Against the curves read from the paper's vector figures (digitize_2404.py; locators
Figures/sep_fraction.pdf, v8-asymp.pdf, frac-surv-Rgr-2.pdf of 2404):
- separation fraction: max |difference| 0.005 (retro Newton), 0.0225 (retro HRNA), 0.016 (pro
  Newton), 0.022 (pro HRNA); mean |difference| 0.001-0.005. The curves lie on each other.
- mean v_inf of separated encounters: max relative difference 0.4-0.7 percent in all four
  cases. Maximum v_inf at beta = 10, retrograde: 3364 vs 3366 km/s (HRNA), 2876 vs 2877 km/s
  (Newton); prograde 17946 vs 17149 (HRNA) and 13906 vs 14861 km/s (Newton) (the prograde
  maximum is a narrow spike in phase).
- bound fraction of retrograde survivors: max |difference| 0.02 (Newton), 0.06 (HRNA) for
  beta >= 1.
Checks against the printed statements:
- P1 holds: retrograde onset beta = 1.9 (HRNA), 2.5 (Newton) (paper ~2 and 2.5).
- P2 FAILED at one point only: max |s.f.(HRNA) - s.f.(Newton)| (prograde, beta <= 9) is
  0.0575 at beta = 0.5, on the steep prograde onset; 0.0175 for 1 <= beta <= 9.
- P3 FAILED as I stated it (relative excess 10-60 percent): the relative excess reaches
  73 percent at beta = 3 (s.f. 0.51 vs 0.295); the absolute excess for beta in [3, 10] reaches
  0.33 (beta = 10: 0.91 vs 0.58). Since our curves coincide with the paper's figure, the
  paper's "up to 30%" (article.tex:475, :795) is the absolute difference in s.f.
  (percentage points) [JUDGEMENT on the wording, the numbers are the figure's].
- P4 holds away from the onset: for beta >= 3.5 the retrograde mean v_inf of HRNA exceeds
  Newton by up to 34.8 percent and 556 km/s (paper: up to 30 percent, article.tex:593; up to
  500 km/s, :797); including the onset region (beta 2-3.5, Newton barely separating) 154
  percent and 1015 km/s.
- P5 FAILED marginally: prograde, beta > 9, max v_inf of HRNA minus Newton = 4040 km/s
  (refutation level 4000; paper "up to 2000 km/s", article.tex:591). The paper's own band edges
  at beta = 10 differ by 2290 km/s; our HRNA maximum is 4.6 percent above and our Newton
  maximum 6.4 percent below them. A maximum over 400 phases of a narrow phase spike is not a
  robust statistic.
- P6 holds: fraction of retrograde survivors left bound to the hole, mean over beta > 8: 0.537
  (HRNA) and 0.352 (Newton) (paper > 50 and ~30 percent, article.tex:760); for 0.5 <= beta <= 1.2
  no retrograde binary separates and at least 88 (HRNA) and 100 percent (Newton) of the
  survivors are bound (paper: essentially all, :762).
- Consistency parameter a/R (2404 Eq. 9): the maximum over the run (any time) reaches 0.20 at
  beta = 10 (prograde) as the paper says ("as large as 0.2", article.tex:279); retrograde 0.055
  at beta = 8.5, against "alpha ~ 0.1" in the paper's two examples at beta = 8.5
  (appendix.tex:8, Fig. alpha) [TO VERIFY: factor 2; the paper's per-phase values were not
  read from Fig. alpha_beta]. While the instantaneous Newtonian E_b < 0 (my alpha_max) a/R stays
  below 0.006, because E_b is positive near pericentre for every binary (tidal shear).
- Abnormal endings: 77 runs at t_max (not examined individually), 29 step underflows and 951
  runs with a_min < 1e-4 a0 (point-mass near-collisions; kept in the s.f., excluded from the
  speeds); 7 members captured (all at the deepest beta).

### S3 outcome (run F-hills-20261115-130922-634fb86; analysis F-hills-20261115-142554-c10b371)

HRNA in Kerr-Schild (a = 0) against Schwarzschild coordinates, beta = 3, 5, 8, 10: |delta s.f.|
<= 0.005 in all eight cases (2 to 19 of 400 phases change outcome); mean v_inf differs by
0.2-1.4 percent. Prediction holds: the coordinate dependence of HRNA is below the s.f.
resolution here.

### S2 addendum, Q4 (analysis F-hills-20261115-142554-c10b371)

a/R at any time, maximum over phases (near-collisions excluded): prograde 0.15 (beta = 8.5),
0.20 (10), 0.47 (15); retrograde 0.055, 0.073, 0.15. Q4 holds for prograde, fails for
retrograde (0.15 < 0.2). Beyond beta = 15 the maximum is dominated by captured members and is
not meaningful.

## Summary of the package (2026-11-15)

1. Model implemented (`hrna.py`) and validated: metrics (T1), single-body limit against
   python/nrpic to 3e-8 r_g in Schwarzschild and Kerr a = 0.9 (T2), flat-space limit with the
   order-v^2 HRNA eccentricity understood (T1b), the time dilation of 2404 appendix B to 1e-4
   (T3), the 3+1 form of the force that AthenaK's pushers would use to 4e-8 a0 (T4).
2. Reproduction of 2404: six single encounters (outcomes 6/6, r_cm at separation to 1 percent;
   printed t_s differ by sqrt(2), which the CM orbit alone shows to be an inconsistency of the
   paper's numbers or units); separation fraction, ejection speed and bound fraction against
   the paper's figures to 0.02 in s.f. and 0.7 percent in mean v_inf; printed onsets and excesses
   reproduced, with the paper's "30%" for the s.f. being percentage points.
3. Pericentres of a few r_g (beta 10-25, r_p 10-4 r_g): HRNA separates retrograde binaries
   almost always (0.92 at r_p = 9.6 to 1.0 at 4 r_g; Newton 0.59-0.66); the mean ejection
   speed stays within 3 percent of Newton (prograde) or below it (retrograde); below r_p ~ 5 r_g
   the hole captures a member in most encounters (0.78/0.69 at r_p = 4.6 r_g, ~1 at 4.05 r_g).
   HRNA is outside its own consistency regime there (a/R up to ~0.5).
4. Kerr (equatorial): a = -0.9 raises and a = +0.9 lowers the retrograde s.f. by 0.04-0.05
   relative to a = 0 at beta >= 5; prograde unchanged; Kerr-Schild and Schwarzschild coordinates
   agree to 0.005 in s.f. 2402.02178 is not reproduced (needs inclined binaries; different model).
5. Convergence: tolerance (C1) changes at most 2 of 400 outcomes; the release radius (C2)
   moves the HRNA retrograde s.f. by 1 percent between 50 and 70 r_t (as in 2404) and by 3.7
   percent from 20 r_t; its cause is open (the initial-eccentricity candidate was tested and
   rejected). Open: 1PN law, inclined encounters, 2402.02178, the cause of the r0 dependence,
   rotation reversal of the beta = 5, phi = 2.04 example, the factor 2 in a/R at beta = 8.5.

### C1 outcome (run F-hills-20261115-142810-aad3f24; analysis F-hills-20261115-143837-0fa01c7;
### first analysis attempt F-hills-20261115-143824-2c937bc failed on a syntax error)

rtol = 1e-10 against 1e-12 at beta = 3, 4.7, 8, both laws and senses: at most 2 of 400 phases
change outcome (s.f. difference <= 0.005), median relative change of v_inf 1e-6 to 2e-5.
Prediction holds. (rtol = 1e-13 was checked only on the single encounter of the smoke test:
eps1 to 1e-8 relative, t_s to 1e-5 T0.)

### C2 outcome (run F-hills-20261115-135732-cace755, 2675 s on 6 cores; analysis
### F-hills-20261115-144217-0fa01c7; figure c2_r0.png inspected)

beta = 4.7, s.f. at r0 = 20 / 50 / 70 r_t:
- Newton: prograde 0.9875 / 0.985 / 0.985, retrograde 0.46 / 0.4625 / 0.46 (spread at the phase
  resolution). Holds.
- HRNA, 2404 initial data: prograde 0.99 / 0.995 / 0.995, retrograde 0.6975 / 0.6725 / 0.68
  (relative spread 3.7 percent; 1.1 percent between 50 and 70 r_t). Like 2404 (stall at ~1e-2,
  appendix.tex:217) for r0 >= 50 r_t; larger at 20 r_t. The tolerance contributes <= 0.005 (C1),
  so the dependence belongs to the model.
- HRNA with the Gamma-corrected initial binary: retrograde 0.70 / 0.6775 / 0.6775 (spread 3.3
  percent). The candidate cause (initial non-circularity from the 1/Gamma^2 of the pair force)
  is NOT supported: correcting it leaves the r0 dependence in place. Cause open [TO VERIFY];
  next candidates, untested: the anisotropic coordinate distance (g^rr = 1 - 2M/r) that
  distorts the binary during the infall, and the Newtonian (coordinate-time) phase of the
  released binary.
