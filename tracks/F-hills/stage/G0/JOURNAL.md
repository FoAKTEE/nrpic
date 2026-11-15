# Journal of the second check of G0 (helper of F-hills, wave 2, 2026-11-15)

Package `second_check`: an independent check, from the artefacts, of (1) the novelty verdict
`tracks/F-hills/novelty/NOVELTY.md` and (2) the disagreement between the Newtonian and the
geodesic (HRNA) baselines at q = M/m_b = 10 for r_p = 7-13 M (`stage/G0/checks/`, lead runs
V6 F-hills-20261115-145251-090f5dc, V7 F-hills-20261115-145915-71abf93). Times are UTC.
Predictions are written before the runs; outcomes are appended below them, also when wrong.

## Entry 1 - predictions, written before any run (2026-11-15)

What I read before predicting (artefacts, not conclusions): `checks/lead_checks.py`,
`checks/v7_summary.json`, `checks/v5v6_summary.json`, the figures `fig_v7_rp_scan.png`,
`fig_v5v6_q10.png`; the HRNA equations and initial data of arXiv:2404.16270
(`kb-data/raw/arxiv/2404.16270/v1/src/article.tex` l. 245-267, `appendix.tex` l. 138-179);
`geodesic_binary/hrna.py` (to know the conventions the lead used, not to reuse code).

Reading of the artefacts [JUDGEMENT]. In V6a the member that Newton ejects (m1) is the one
that HRNA plunges, and the one that Newton binds (m2, pericentre 5.9 M) is ejected by HRNA:
the two models disagree about the binary phase at pericentre, not only about the fate of a
low-angular-momentum member. Two candidate causes, both of which my runs can refute:

- C-IC (initial data). 2404's initial binary is Newtonian-circular in coordinate time
  (appendix.tex l. 143-158), while under HRNA the pair force is divided by Gamma^2 (article.tex
  l. 248-257). At 2404's release radius (50 r_t = 5065 M) this is negligible; at the NR
  release radius of F (4 r_t = 25.85 M at q = 10) the CM has Gamma = 1/(1 - 2M/r0) = 1.084 for
  E = 1, so in the CM proper time the binary starts with speed Gamma v_circ: a_eff = a0 /
  (2 - Gamma^2) = 1.21 a0, e = Gamma^2 - 1 = 0.17 (estimate, ignoring the anisotropic spatial
  metric and the boost). A 21 percent wider binary has r_t larger by 21 percent, so D_eff =
  D/1.21: this alone would move the separation edge from r_p ~ 13 M to ~ 15.7 M.
- C-GR (physics). In Schwarzschild a member with E ~ 1 and specific angular momentum L < 4M
  is captured; for Newtonian members after separation at r_p = 8 M the CM has L = 4.0 M and
  the members differ by about +-(r_p v_b/2 + a0 v_p/2) ~ +-1.5 M, so in most separating phases
  one member has L < 4 M. A Newtonian bound member with pericentre 5.9 M (V6a) has
  L ~ sqrt(M a (1 - e^2)) ~ 2.7 M < sqrt(12) M: in GR it cannot stay on that orbit.
- C-DEF (driver defect): a wrong sign, index or factor in either driver.

Tests (my own integrators in `second_check/models.py`: exact Schwarzschild coordinate-time
acceleration derived from the radial and azimuthal geodesic equations, pair force
(1/Gamma^2) g^ij a_j of 2404 Eq. CoordtEqs; Newton with the hole fixed and Newton with the
hole free; scipy DOP853):

SC0 self-tests. (a) Pair force off: E = f Gamma and L = Gamma |x x v| of a member conserved to
  < 1e-9 relative over a parabolic passage with r_p = 8 M; the 2404 Schwarzschild parabola
  reaches r_p = 8 M to < 1e-6. (b) Newton, hole fixed, pair force off: Kepler energy and L to
  < 1e-10. (c) Full Newton: total energy and momentum to < 1e-9 relative. Refuted (my code
  wrong) if any is missed by 100 times.
SC1 driver check, phase-averaged. q = 10 (M = 1, m1 = m2 = 0.05, a0 = 3, r_t = 6.463 M),
  prograde, release 4 r_t, stop at 30 r_t, r_p = 7, 8, 10, 12, 13 M, 72 phases. My
  Newton-fixed and HRNA fractions (separated; a member below 2.5 M inwards) agree with the
  lead's V7 (180 phases) within 0.06; my full Newton within 0.08 of newton3's (different phase
  conventions, both uniform). Refuted if any differs by more than 0.1.
SC2 driver check, phase by phase. hrna.py (laws newton and hrna, same initial data) against
  my integrator at the same 72 phases for r_p = 8 and 13 M: outcome codes equal in >= 95
  percent of phases; separated / captured flags equal in >= 97 percent. Refuted (one of the
  two drivers has a defect) below 90 percent.
SC3 initial-data effect (C-IC). (a) Isolated-binary diagnostic: under HRNA with 2404's data at
  4 r_t, the binary separation oscillates between a0 and 1.3-1.5 a0 before pericentre; with
  the internal angular velocity divided by Gamma_cm (Gamma-corrected data) it stays within
  1.1 a0 until tides act; Newton stays within 1.05 a0. (b) Fractions: with the
  Gamma-corrected data, and with 2404's data released at 20 r_t (Gamma - 1 = 0.016), HRNA's
  separated fraction at r_p = 12 and 13 M drops from ~0.98 to 0.4-0.85; the two remedies
  agree with each other within 0.1. Refuted (C-IC is not the cause of the separation excess)
  if the fraction at r_p = 13 M stays above 0.9 with both remedies.
SC4 capture criterion (C-GR). (a) Consistency of HRNA: every member that HRNA plunges has,
  when its pair acceleration has fallen below 1 percent of the hole's (or at the plunge),
  test-particle (E, L) inside the Schwarzschild capture region (L below the barrier for its E);
  >= 95 percent of plunges. Refuted (defect in HRNA's plunge logic or force) below 90
  percent. (b) Newton with the GR criterion: applying the same criterion to the Newtonian
  members after separation (E = 1 + eps, same L), the fraction of phases with a would-be
  captured member is >= 0.5 at r_p = 7-9 M and decreases with r_p. Refuted (the HRNA plunges
  are not the relativistic counterpart of Newtonian low-L members) if < 0.2 at r_p = 8 M.
SC5 the input state of P1 (hills_q10_m8.athinput, V6a). Mine reproduces V6a: Newton-fixed
  ejects m1 (E1 ~ +1.9 units) and binds m2 (pericentre ~ 5.9 M); HRNA from the same
  coordinate state plunges m1 near t = 97 M. With the internal velocities relative to the CM
  divided by Gamma_cm the HRNA phase at pericentre moves; prediction: the outcome changes
  (m2 is the plunged or bound member) [low confidence, 50 percent].

Novelty (N1). Repeating the search with my own generic queries (web; INSPIRE through
`nrpic-fetch-arxiv --inspire-query`; forward citations of 2406.11985, 2505.03934, 2404.16270,
2402.02178, 2308.07365, 2605.20320, 2604.27429): prediction, the verdict holds (no full-NR
calculation of a binary tidally separated by a heavier black hole on a near-parabolic orbit;
no full-GR matter binary passing a black hole). Refuted by one paper that does either.

## Entry 2 - an observation of a smoke run, and the predictions it adds (before the registered runs)

Smoke runs (unregistered, `scratch/F-hills/tmp/sc_smoke`, code under development; numbers
below are not results): (i) SC0 (a), (b) pass (E and L of the 2404 parabola conserved to
7e-12 and 1.3e-10, r_p = 8 M to 7e-11); (c) full Newton conserves energy to 3.2e-9, above my
1e-9 but far from the 100-fold refutation level (close passages at rtol = 1e-11). (ii) At the
phase 2.488 of V6b my Newton-fixed gives E_u = (+1.798, -2.026) and my HRNA (+plunge of m1)
E_u = (-0.767, +0.689): the lead's V6b numbers are (+1.794, -2.026) and (-0.767, +0.688).
(iii) HRNA released at 20 r_t (2404 data) brought the CM to a pericentre of 31.6 M instead of
8 M.

Cause of (iii), derived before testing [JUDGEMENT until SC0d runs]. In Eq. CoordtEqs each
member's pair force carries its own 1/Gamma_i^2. In flat space 1/Gamma_i^2 = 1 - v_i^2, so the
total force on the pair is F (v2^2 - v1^2) = -2 F (dv . V) for equal members (F the force on
member 1, dv = v1 - v2, V the CM velocity): not zero for a moving binary. Averaged over a
circular orbit, the CM gets a constant acceleration (m1 m2 / m_b)(omega / a0) |V|,
perpendicular to V (to the right of V for a counter-clockwise binary). Relative to the hole's
pull on the CM at r = k r_t this is (sqrt(2)/4) k^(3/2) (m_b / a0) for equal members: 0.094 at
k = 4 and 1.05 at k = 20 for F's q = 10 binary (m_b/a0 = 1/30); 1.2e-4 for 2404's binary at
50 r_t. For a prograde binary falling in, its torque -c r rdot (c = (m1 m2/m_b)(omega/a0) =
5.1e-4) raises the CM's angular momentum by c r0^2 / 2: 0.17 from 4 r_t (r_p,CM 8 -> about
8.7 M), 4.2 from 20 r_t (r_p,CM about 30 M; smoke run 31.6 M). It is a property of the model
(Euclidean Newtonian force with member-wise 1/Gamma^2), so hrna.py must show it too.

Added predictions:

SC0d flat-space moving binary (M = 0; circular counter-clockwise binary a0 = 3, m = 0.05
  each; CM velocity V = 0.28 along x, the CM speed at 4 r_t): HRNA (mine and hrna.py alike)
  accelerates the CM along -y at 1.42e-4 within 10 percent (displacement 6.4 after t = 300);
  hrna_sym (the pair factor (1/Gamma^2) g^ij evaluated at the CM for both members, my
  diagnostic variant, not a model of the literature) and Newton keep the CM on its line to
  < 1e-6. Refuted if HRNA's CM deviates by less than 0.5 after t = 300.
SC6 consequence at q = 10 (scans of SC1/SC3 extended): median CM pericentre over phases is
  shifted upwards from the nominal r_p by +0.3 to +1.2 M for HRNA released at 4 r_t, by
  > +10 M at 20 r_t; for hrna_sym within +-0.5 M of nominal at 4 r_t [one smoke phase gave 6.74
  at 20 r_t, so for hrna_sym at 20 r_t I predict only that the shift is < 2 M in the median].
  Release-radius convergence: hrna_sym with the Gamma-corrected binary gives separated and
  captured fractions at 4 and 20 r_t that agree within 0.1 at every r_p; plain HRNA does not
  (differences > 0.3 at some r_p). Refuted if hrna_sym's 4/20 r_t fractions differ by more
  than 0.15 at any r_p.
SC3 is amended: the "release at 20 r_t" remedy is confounded by SC6 for plain HRNA, so the
  test of C-IC is the Gamma-corrected binary at 4 r_t (HG4, hrna) and hrna_sym with and
  without the correction (S4, S4raw).

## Entry 3 - second smoke observation and one more prediction (before the registered runs)

Smoke runs (unregistered, code under development): the flat-space test SC0d gives a CM
acceleration of -1.065e-4 (mine) and -1.065e-4 (hrna.py) against my estimate -1.42e-4: the
sign and the presence are as derived, the magnitude is 25 percent lower than my estimate (my
estimate ignored that the Newtonian-circular binary is itself not circular under HRNA's
coordinate-time pair force; the registered run SC0d decides). On the NR start state (SC5) the
binary separation in the first 50 M grows from 2.97 to 4.83 under HRNA (2404 data), to 3.62
with the Gamma-corrected velocities, to 3.20 under Newton: the Gamma correction removes about
half of the inflation, not all of it; one Gamma-corrected HRNA case ran away (member faster
than light after a close approach of the point masses), hence the guard `superluminal` and
the near-collision flag (minimum binary separation < 0.01 a0) added to models.py.

SC7 prediction (GR invariants of the NR start state, before computing them). The NR data give
coordinate momenta P = m v of a Newtonian state in the puncture's (nearly isotropic)
coordinates. Reading u_i = P_i/m as the covariant 4-velocity in isotropic Schwarzschild of the
heavy hole (psi = 1 + M/2r, alpha = (1 - M/2r)/(1 + M/2r)), E = alpha sqrt(1 + psi^-4 |u|^2) is
below 1 for the CM by about (1/2) v^2 (2M/r) ~ 0.003 (bound, not parabolic), L = (x x u)_z ~
4.2 M per unit mass; the GR turning point of that (E, L) is near r_S ~ 6 M (areal), deeper
than the intended 8 M; one member's L is below 4 M. [Estimates by hand; refuted if the CM's E
exceeds 1 or its GR turning point lies outside 7.5 M.]

## Entry 4 - outcomes (registered runs, 2026-11-15 17:55-18:12 UTC)

Runs: F-20261115-175542-b49d687 (self-test, FAILED: the script did not read NRPIC_RUN_DIR;
kept on record), -175549-456bf4a (SC0 a-c), -175620-df20ffe (SC0d), -175614-5cc133d (scan,
9 models x 9 r_p x 180 phases, 6 cores, 12 min), -180835-66e13b2 (SC2, hrna.py),
-175636-5432651 (SC5), -175637-a592d7a (SC7), -181007-80649f5 (figures, superseded by
relabelled) -181106-52c4613 (figures and compare.json). Fractions below are over all 180
phases; a run stopped as "superluminal" (point-mass near-collision of the members; all 38
such runs of H4 and all of the other models were bound binaries at the stop) counts as not
separated.

- SC0 (a) holds: E to 7e-12, L to 1.3e-10, r_p = 8 M to 7e-11. (b) holds (4.5e-12, 7.4e-11).
  (c) energy of the full three-body problem to 3.2e-9: above my 1e-9, far from refutation.
- SC0d: the self-acceleration exists and is the same in both codes: -1.0646e-4 (mine) and
  -1.0647e-4 (hrna.py), hrna_sym and Newton exactly 0. My estimate -1.42e-4 is 25 percent too
  large: the "within 10 percent" part FAILED; the refutation level (< 0.5 M after 300 M) is
  far away (4.8 M).
- SC1 holds. Separated fractions at r_p = 7..13 M: mine Newton-fixed = lead's to all three
  digits (0.911 ... 0.000); full Newton within 0.011 of newton3; HRNA 0.99, 0.99, 0.98, 0.96,
  0.96, 0.94, 0.94 against the lead's 0.99, 1.00, 1.00, 0.98, 0.97, 0.98, 0.98; captured 0.96,
  0.93, 0.88, 0.84, 0.79, 0.71, 0.33 against 0.96, 0.94, 0.89, 0.86, 0.78, 0.69, 0.30.
- SC2: law newton 360/360 phases with equal outcome codes; law hrna 178/178 at 8 M (2
  near-collision stops of mine excluded) and 162/174 at 13 M (93.1 percent: the >= 95
  percent prediction FAILED at 13 M, above the 90 percent refutation level). The 12
  differences: 3 are late plunges of a bound member after hrna.py stopped on its bound-CM
  rule (identical energies to 3 digits), the rest phases next to outcome boundaries. No
  defect in either driver.
- SC3 (a) holds for HRNA (NR state: separation 1.0 -> 1.8 a0 before pericentre, Newton 1.07
  a0); the Gamma-corrected binary still reaches 1.2 a0 (my "within 1.1 a0" FAILED). (b)
  holds: HG4 separated 0.76 (12 M) and 0.63 (13 M) against 0.94 for H4; with the CM factor as
  well (S4) 0.54 and 0.48, and at 15/17 M 0.23/0.06 against 0.89/0.82 (H4).
- SC4 (a) holds: 658 of 658 H4 plunges and 488 of 490 S4 plunges at r_p = 7-10 M have
  test-particle (E, L) inside the Schwarzschild capture region. (b) holds: Newtonian members
  (NF4) end inside the GR capture region in 0.91, 0.91, 0.91, 0.84, 0.76, 0.58, 0.19 of the
  phases at r_p = 7..13 M; they are the members left bound with L = 2.2-3.2 M < sqrt(12) M.
- SC5 holds for the reproduction (Newton-fixed E_u = +1.891 / -1.901, bound member pericentre
  5.87 M; HRNA plunges m1 at t = 96.9 M, E2_u = +1.159; V6a: +1.887 / -1.901, 5.86 M, 97.1,
  +1.159). With the Gamma-corrected velocities (HRNA and hrna_sym) the outcome changes in a way
  I did not predict: the two point masses collide at t = 84.5 M (separation < 0.01 a0) before
  pericentre.
- SC6: Delta L_cm (release -> 2 r_t) of HRNA at 4 r_t is 0.12 at r_p = 7 M (predicted 0.127),
  0.003-0.02 for Newton, 0.02-0.08 for hrna_sym; from 20 r_t HRNA's CM pericentre is 30.5-44 M
  for nominal 7-17 M (predicted > +10 M): holds. The release-radius convergence of hrna_sym is
  REFUTED: S4 and S20 differ by up to 0.35 in the separated and 0.38 in the captured fraction
  (r_p = 8 M: 0.91/0.56 and 0.82/0.44); S20 has 25-60 percent near-collision stops, 90 percent
  of them after the CM pericentre (surviving, eccentric binaries). My diagnostic variant is
  therefore not a converged reference either.
- SC7 holds: the CM of the NR start state, read as u_i = P_i/m in isotropic Schwarzschild
  coordinates of the heavy hole (hole frame), has E = 0.99925, L = 4.19 M and a GR turning
  point at r_S = 5.77 M (isotropic 4.72 M); with the hole at rest E = 0.9929, L = 3.81 M
  (captured); with the total mass M + m_b, L/(M + m_b) = 3.81 (captured).
- N1 holds (SECOND_CHECK.md part 1): no full-NR Hills-type calculation and no full-GR matter
  binary passing a black hole found in 31 INSPIRE queries, 10 complete forward-citation lists
  and 6 web searches between 17:57 and 18:06 UTC.
