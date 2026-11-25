# JOURNAL of verifier-c18 (fresh verifier of item C18 of gate G2, Track A; batch 18)

Helper of A-emd-pbh, 2026-11-25. Decision 0016 item 4, decision 0039 item 2(b). Processors
only, no card run. Claims are taken from the result tables of `threshold_ball/README.md` and
`conv_ball/README.md`; criteria from `scope/SCOPE.md` sections 3 and 7; predictions of the
packages as written before their runs (`conv_ball/JOURNAL.md` entry 3, committed before job 1;
`threshold_ball/JOURNAL.md` entry 1, committed 12:41:43 PST 2026-11-21 as c48bd33b, and entry 11's
statement of T4 written before its analysis). Not read before VERIFIER-C18.md is written: the
outcome entries of both journals, `stage/REVIEW-wave3.md`, `stage/G2/CHECKLIST.md`.

Readers and reference are the verifier's own (`scripts/vread.py` from docs/FORMATS.md and
coord/INTERFACES/diagnostics.md; `scripts/vref.py`: LTB dust from the format-2 table, written
from coord/INTERFACES/spherical_id_format2.md and the dust equations; `scripts/vmeasure.py`).
Nothing of conv_ball, threshold_ball, runs_ball, expball or python/nrpic is imported.

## Entry 1, 2026-11-25 13:02Z: predictions for the tests of the readers and the reference (before running them)

V0a (reference on an analytic field). A synthetic format-2 table of closed FLRW dust in
stereographic coordinates (psi^2 = 1/(1 + rbar^2/(4a^2)), KL = KT = -H, alpha = 1) at
eta0 = 1.2, a_m = 10, 4001 rows to rbar = 2a: vref.LTB returns m = a_m sin^3(chi)/2, the
turnaround tau_ta = (a_m/2)(pi - eta0 + sin eta0) and tau_AH from (1 - cos eta_AH)/2 = sin^2 chi
with relative errors below 1e-6 for chi in [0.1, 1.4] (second-order differences on rows of
about 5e-3 a; truncation about 1e-6 at worst). Refuted by an error above 1e-5 anywhere there.
V0b (exact areal radius). vref.LTB.areal_radius at tau_AH returns 2m to 1e-9 relative, and at
tau_ta returns 2A = a_m sin chi to 1e-9. Refuted by more.
V0c (trajectory reader). Synthetic traj/trajmet files (5 particles, 11 times, linear in t),
with a "restart" that repeats the last three times with changed values: Tracks keeps the
repeated (later) values, interpolates linear data exactly (1e-14), and the areal radius of
gamma_ij = A n_i n_j + B (delta_ij - n_i n_j) equals r sqrt(B) to 1e-14. Refuted otherwise.
V0d (summary reader and the BH rule). Synthetic summaries with known outcomes: (i) found from
search 10 to the end (40 searches every 0.25, mass 0.3): BH, persistent from t(10); (ii) the
same with the last search failed: not BH; (iii) found only in the last 3 searches spaced 0.25
(span 0.5 < 5 x 0.3): not BH; (iv) duplicated times with the later copy failed: the later copy
wins. Refuted by any other answer.
V0e (line measures). A tab line of Schwarzschild in isotropic coordinates (psi = 1 + M/(2r),
K = 0, M = 1, points 0.05 apart on [-16, 16]): line Misner-Sharp mass 1 to 1e-3 for r > 1 (the
derivative is second order on 0.05), MOTS at |x| = 0.5 with m = 1 to 2e-3; the constraint ratio
of a line with H = 0.3 x 16 pi E is 0.3 to 1e-12 in every weighting. Refuted otherwise.
V0f (the real tables). For the table of conv_ball's data set 3 my reference gives the exact
events the packages quote (conv_ball/JOURNAL.md entry 3, DESIGN.md 1: core turnaround 3.3716,
tau_AH of the core edge 9.5511, m 0.686563) to 1e-3 relative or better, and for the eight
threshold tables the tau_AH column of threshold_ball/DESIGN.md section 1 (15.386 ... 114.574)
to 1e-3 relative. This is the first independent check of the exact column; refuted by a
difference above 1e-3 relative in any member.

### Entry 1 outcome (registered run A-20261125-130535-b79555d; fig_v0a.png, fig_v0e.png looked at)

Before the registered run, an unregistered smoke run of the same script (scratch/A-emd-pbh/tmp/
vc18_smoke, a debugging run, stated here because its result changed the code) gave V0a FAILED:
relative errors 3.9e-6 in m and 1.5e-5 in tau_ta, tau_AH at chi = 0.1, above the 1e-5 bound. The
cause is the cancellation in 1 - (dR/dl)^2 at small radii (relative error amplified by 1/chi^2)
with a second-order derivative of the table; the core-edge "exact" values also came out 1e-3 off
because the last row inside the break is up to one row (1e-3) inside the edge. Changes (commit
before the registered run): fourth-order central differences of R inside each piece, quadratic
extrapolation of the last three rows of a piece up to its break. Registered outcome:
- V0a PASS: max relative error 4.8e-12 (m), 1.9e-11 (tau_ta), 1.8e-11 (tau_AH) for chi in [0.1, 1.4].
- V0b PASS: R(tau_AH) = 2m to 3e-13, R(tau_ta) = a_m sin chi to 2.4e-12.
- V0c PASS: trajectory reader keeps the later of repeated records, interpolation and areal radius
  exact to 4e-16.
- V0d PASS: the BH rule gives (i) BH from t(10), (ii)-(iv) not BH; the duplicated-time summary
  keeps the later (failed) copies.
- V0e PREDICTION FAILED in one part: the line Misner-Sharp mass of Schwarzschild is 1 to 2.0e-4 for
  r > 1 (pass) and the constraint ratio is 0.3 to 5e-15 in all three weightings (pass), but the
  line MOTS sits at |x| = 0.5031, not within 2e-3 of 0.5 (error 3.1e-3); its mass is 1.0006 (within
  the 2e-3 predicted). Cause: second-order differences on 0.05 spacing where psi is steep; the
  mass, which is what is used, is within bound. The line MOTS mass is used below only as a
  secondary check with an uncertainty of order 1e-3 at that resolution.
- V0f PASS for all eleven tables (relative differences to the quoted values at most 2.6e-6 after the
  fix): data set 3 (and its 1.25, 1.35 balls) core turnaround 3.371611, core-edge tau_AH 9.551093,
  m 0.686562 (quoted 3.3716, 9.5511, 0.686563); threshold tables tau_AH(edge) 15.386139, 23.404718,
  35.159637, 40.053600, 43.656126, 46.415299, 54.979747, 114.574469 for delta_c = 1.0 ... 0.2
  (DESIGN: 15.386, 23.405, 35.160, 40.054, 43.656, 46.415, 54.980, 114.574), m_edge 0.54925 ...
  0.32955 as quoted. Core homogeneity: tau_ta equal at rbar = 1, 2 and the edge to 1e-6; the first
  trapped row beyond rbar = 0.3 is the last row inside the core edge in every table (the core edge
  is the first trapped sphere, as threshold_ball/DESIGN.md section 1 states). [VERIFIED] The exact
  columns of both packages are reproduced by an independent reference.

## Entry 2, 2026-11-25 13:06Z (commit 5b607af1): predictions for the recomputation of conv_ball (before running vconv.py)

Claims (conv_ball/README.md table and findings; final analysis A-20261121-120257-a2eb839): first
detection t, ddet, dtrap, mass median per member; mesh orders ddet 1.5, 2.0, dtrap 2.1, 1.5; mass
7.4e-3 -> 2.1e-3 -> 2.1e-4; fixed N = 4969736 mass 2-5e-4 on all meshes; at B the time errors do
not depend on N, the mass does (-2.1e-3 vs -3.0e-4).
- P1 first detection times: identical to the printed digits of the table (same files, my reader).
  Refuted by any difference.
- P2 ddet: my two interpolations agree with each other within 0.005 M and with the table within
  0.01 M for A, B, C, A-N8, A-N64, B-N8, B-R1.25, B-R1.35, A-R1.25, A-R1.35 (the definition is the
  same; band means and record interpolation may differ). The mesh orders then reproduce within
  +-0.3 (1.5, 2.0). Refuted by a larger difference.
- P3 dtrap: within max(0.005 M, 20 per cent) of the table values for the mesh triple. Refuted
  otherwise.
- P4 mass median: within 1e-3 (absolute, relative mass error) of the table for every member, with
  |dm(A)| > |dm(B)| > |dm(C)| reproduced; the C value below 1e-3 in magnitude. My exact horizon mass
  interpolates the trapped label between tracked bands, which the package may not; where the bands
  are far apart (gap > 0.1 in rbar) I expect differences up to 1e-3. Refuted by a larger difference
  or a changed ordering.
- P5 particle leg at B: |ddet(B) - ddet(B-N8)| < 0.01 M and the masses differ by more than 1e-3
  (-2.1e-3 vs -3.0e-4 claimed). Refuted otherwise.

### Entry 2 outcome (registered run A-20261125-130753-314837e; fig_vconv_orders.png, fig_vconv_mass.png looked at)

Before the registered run, an unregistered smoke run on member B alone (scratch/A-emd-pbh/tmp/
vc18_conv_smoke) showed the two interpolations differ by 0.011 M at B; a third (straight-line fit
over three bands on each side, v3) was added before the registered run. Outcomes:
- P1 PASS: first detection times equal the table to its digits in all ten members (10.875, 10.7812,
  10.750, 10.8125, 10.8125, 10.750, 10.9062, 10.9375, 10.750, 10.750).
- P2 PARTLY FAILED. With v2 (tau and label interpolated linearly in the coordinate radius, tau_AH
  exact at the interpolated label: the literal definition) ddet reproduces the table to 1e-3 M or
  better in nine members (A 0.1924, B 0.0675, C 0.0166, A-N8 0.1086, A-N64 0.1464, B-N8 0.0705, A-R1.25
  0.1004, B-R1.25 0.0652, B-R1.35 0.1074) and to 0.011 M in A-R1.35 (0.1746 against 0.164, just
  outside the 0.01 bound). The interpolations do NOT agree within 0.005 M: v1 - v2 = -0.036 (A),
  -0.011 (B), 0.000 (C); v3 - v2 = -0.005 (A), +0.025 (B), +0.022 (C). Cause, read from the band
  table of B at the first detection: the finder's radius lies at the core edge (interpolated label
  2.4957 against the break at 2.4937), between the last tracked particle inside the core (r 0.4185)
  and the first outside (r 0.4501); tau_AH(label) has a kink there, so the estimate depends on how
  one interpolates across 0.03 in r. Mesh orders of ddet: v2 1.51 and 2.03 (claimed 1.5, 2.0), v1
  1.48 and 1.76, v3 1.01 and 1.27; the fall A > B > C holds in all three.
- P3 PASS: dtrap -0.0925, -0.0224, -0.0077 (claimed -0.093, -0.022, -0.0077), orders 2.05 and 1.53
  (2.1, 1.5); every other member within 0.001 M of its table value.
- P4 PARTLY FAILED: the mass median is within 1e-3 of the table in nine members (B -2.09e-3,
  C -2.25e-4, A-N8 -1.47e-3, A-N64 2.7e-4, B-N8 -3.05e-4, A-R1.25 6.5e-3, A-R1.35 1.02e-2, B-R1.25
  -1.94e-3, B-R1.35 -1.31e-3), but A gives 6.3e-3 against 7.4e-3 (1.1e-3 off). The claimed value
  lies inside my bracket [5.3e-3, 7.4e-3] (exact mass taken at the next tracked band outward or at
  the last trapped one): the tracked particles sample the trapped label too coarsely to fix the
  exact mass better than that. The bracket is [-9.6e-4, +5.0e-4] for C, so C's error is below 1e-3
  whatever the interpolation, but its value (-2.2e-4) and any order B -> C are below the
  resolution of the exact mass on the tracked set. Ordering |dm(A)| > |dm(B)| > |dm(C)| holds.
- P5 PASS: ddet(B) - ddet(B-N8) = -0.003 M; masses -2.09e-3 against -3.05e-4. At fixed N = 4969736
  the masses are 2.7e-4, -3.05e-4, -2.25e-4 (A-N64, B-N8, C), as claimed (2-5e-4).
- Boundary leg: A-L32 equals A to 1.0e-7 in ddet and 1.2e-7 in the mass median (claimed 1e-7);
  B-L32 equals B to 1.2e-11 in ddet and dtrap (claimed 1e-11) and to 1.2e-8 in the mass median.

## Entry 3, 2026-11-25 13:11Z (commit f1624142): predictions for the recomputation of threshold_ball (before running vthresh.py)

Claims: threshold_ball/README.md results table (A-20261124-131120-5c974ce; C-d0.42 from
A-20261125-115027-17b419e, A-20261125-115550-fe60ff1) and its bullet list. Rule: entry 1 of
threshold_ball/JOURNAL.md (three consecutive finds spanning 5 M_AH and every later search).
- Q1 rule: the same outcome as the table for all twelve members (BH: B-d1.00 ... B-d0.35, C-d0.42,
  C-R1.25; not: B-d0.20 never found, A-d0.42 and A-d0.40 three finds then the guard stop);
  persistent-from times equal to the printed digits (17.000, 25.250, 37.188, 42.250, 45.875,
  48.625, 58.312, 45.906). Refuted by any other outcome or time.
- Q2 detection times: tau_det (first detection, v2) within 0.02 M of the table for B and C
  members (conv_ball showed an interpolation spread of about 0.01-0.02 M at B), within 0.05 M for
  A-d0.42, A-d0.40; ddet within the same. Refuted by larger differences.
- Q3 masses: dmmed within 2e-3 of the table for the B members; for C-d0.42 the claim (+2.4e-2) is
  a median over a window inside the first-detection transient (README note): I expect my median
  over every detection with an exact mass to be smaller, below 1e-2 [JUDGEMENT]. A-d0.42, A-d0.40:
  within 1e-2 of -3.8e-2, -4.6e-2.
- Q4 bracket: tau_det(B-d0.42) < 45 < tau_det(B-d0.40), interpolated delta_c(45) = 0.4103 +- 0.001;
  exact 0.4103 (my reference gives tau_AH 43.656126 and 46.415299: 0.41026); C-d0.42 below 45.
- Q5 constraint ratio (L2 of H over L2 of 16 pi E on the x line, outside the finder's radius, at
  the tab output nearest the first detection): above 0.1 in every member and weighting (the README
  says 0.3-3); at t = 0 well below 0.1 (con_H contains the matter term and the data solve the
  constraints). Refuted by a member below 0.1 at detection, or a t = 0 ratio near 1 (then con_H
  would lack the matter term and the whole comparison would be meaningless).
- Q6 criteria that the README lists as failed: T4's mesh-C half (|ddet(C-d0.42)| <= 0.0075 and
  |dmmed| <= 1.4e-3) fails as written; T5 (|ddet(C-R1.25) - ddet(C)| <= 0.02 M) fails (0.024
  claimed). I expect to confirm both failures.
- Q7 line MOTS mass within 1.5 per cent of the finder mass at the first detection (B members).
- Q8 (not a claim; SCOPE section 3 measures time by the envelope's proper time): the envelope's
  proper time at the first detection exceeds the core edge's by about the coordinate lag (1-2 M),
  so B-d0.42 would be detected after 45 in the SCOPE measure [JUDGEMENT, to be measured].

### Entry 3a, 2026-11-25 13:14Z (commit 1b00953e): a defect of my own reader, found by the first threshold run (A-20261125-131148-99204e1); predictions for the reruns

The first registered threshold run classified A-d0.42 and A-d0.40 as BH (persistent from 45.625 and
48.375) and put B-d0.35's persistent start at 57.3125 (table 58.312). Reading the raw summary of
A-d0.42: after 45.875 every record repeats mass 0.3771556660192116 and radius 0.1565937887708861
bit for bit until the guard stop. coord/INTERFACES/cosmo_amr.md section 2.3 says so: "after a failed
search [the summary] repeats the values of the last success, or NaN: read the status file to know
whether a line is new". My reader took every finite summary line as a find; that is wrong. The
outcomes of run A-20261125-131148-99204e1 for the rule, the persistent start and the medians are
withdrawn (the run stays on record); its first-detection numbers are unaffected (the first finite
record is always a real find, the summary writes NaN before it).

Change: `vread.read_summary` takes 'found' from `<base>.horizon_status_0.txt` when it exists (all
threshold members), and otherwise (conv_ball members, no status file) counts a record bitwise equal
in mass, area and mean radius to the previous one as a repeat. A new case V0d(v) tests both paths.

Predictions for the reruns (before them):
- V0d passes with case (v); V0a-c, V0e, V0f unchanged.
- conv_ball (V1 rerun): first-detection quantities identical to run A-20261125-130753-314837e; the mass
  medians change by less than 5e-4 (if repeats exist after the first detection they are few:
  README says C-R1.25 is found in every search, and the conv_ball members ran with hmean_tol 100).
- threshold (V2 rerun): A-d0.42 and A-d0.40 not BH (three finds, then the guard stop); B-d0.35
  persistent from 58.312; the other persistent starts as in the table; Q1 then holds.

### Entry 3b, 2026-11-25 13:19Z: second defect of my reader (rerun A-20261125-131458-396f809); predictions for the next rerun

Outcome of the rerun with status files: A-d0.42 and A-d0.40 not BH, B-d0.35 persistent from
58.3125 (both as the table, so entry 3a's predictions hold for them), but C-d0.42 came out NOT BH,
first find 45.9375 (table: BH, persistent from 45.906). Cause: the summary prints time with %g
(six significant digits), so C's searches every 0.03125 M are written 45.9062 where the status file
writes 45.90625; my exact-key match missed every such line and counted it as failed. B members
(searches every 0.0625 M: 45.875, 45.9375, all exact in six digits) were not affected. Change:
match each summary line to the status line of the nearest time within 1e-4 and take the status
file's full-precision time; new test V0d(vi). The rule outcome of C-d0.42 in run
A-20261125-131458-396f809 is withdrawn; its other members stand.
Prediction for the rerun: C-d0.42 BH, persistent from 45.90625, tau_det within 0.02 M of 43.705;
nothing else changes.

### Entry 3 outcome (registered run A-20261125-131608-2269f36 with the readers of entries 3a, 3b; V0 rerun A-20261125-131605-f9e71ee all PASS except the known V0e MOTS location; fig_vthresh_searches.png, fig_vthresh_summary.png looked at)

- Q1 PASS (after the two reader fixes): BH by the entry-1 rule for B-d1.00, B-d0.70, B-d0.50, B-d0.45,
  B-d0.42, B-d0.40, B-d0.35, C-R1.25, C-d0.42, persistent from 17.000, 25.250, 37.1875, 42.250,
  45.875, 48.625, 58.3125, 10.71875 (every search from the first find), 45.90625; not BH: B-d0.20
  (no find to the last search at 69.94; core band areal radius 9.48 and falling, dR/dt = -0.035),
  A-d0.42 and A-d0.40 (3 finds each, then the guard stop at 47.875 and 50.625, tlim 51 and 54).
- Q2 PASS: tau_det (v2) 15.5129, 23.4721, 35.1309, 40.1166, 43.6863, 46.4022, 54.9293 (B),
  43.4377, 46.1027 (A), 9.6031 (C-R1.25), 43.6892 (C-d0.42) against 15.513 ... 54.929, 43.442,
  46.103, 9.603, 43.705: within 0.004 M except C-d0.42 (0.016 M). ddet v2 equal to the table to
  0.001 M in the B members and C-R1.25 (0.0403 against 0.040), A-d0.42 -0.238 (-0.232), A-d0.40
  -0.331 (-0.331), C-d0.42 -0.0095 (-0.014). Interpolation spread: v1 and v3 differ from v2 by up
  to 0.07 M (B-d1.00 v1 +0.052; C-d0.42 v1 -0.062, v3 +0.030).
- Q3 PARTLY FAILED. Within 2e-3 of the table: B-d1.00 (-9.3e-4 vs -3.8e-4), B-d0.70 (-2.6e-3 vs
  -1.9e-3), B-d0.50 (-9.5e-3 vs -9.4e-3), B-d0.45 (1.0e-3 vs 1.9e-3). Not: B-d0.42 -2.4e-3 vs
  +2.8e-3 (my bracket [-5.4e-3, -0.05e-3]), B-d0.40 -6.7e-3 vs +3.2e-4 ([-9.7e-3, -3.7e-3]), B-d0.35
  -1.0e-3 vs +2.4e-3 ([-8.0e-3, +0.4e-3], only 31 of 73 finds have an exact mass). C-d0.42 +1.0e-3
  ([-3.9e-3, +6.5e-3], 94 of 163 finds) against +2.4e-2: smaller, as predicted. A-d0.42 -8.8e-3
  (-3.8e-2 claimed), A-d0.40 -2.9e-2 (-4.6e-2): with three finds the "median" is a single value.
- Q4 PASS: tau_det(B-d0.42) = 43.686 < 45 < tau_det(B-d0.40) = 46.402; interpolated delta_c(45)
  0.41033 (B), 0.40828 (A, first detections), exact 0.41026 (my reference); C-d0.42 at 43.689 < 45.
- Q5 PARTLY FAILED: at the first detection the ratio exceeds 0.1 in every member and weighting
  (r^2 weight 0.70-2.1 for B, 0.87 C-d0.42, 3.0 C-R1.25, 0.93-1.6 A; line weight 0.16-3.6; matter
  only 0.4-1.5), confirming the claim (0.3-3). But at t = 0 the ratio is NOT well below 0.1: 0.11-0.20
  (B), 0.105 (C-d0.42), 0.12 (C-R1.25), 0.22 (A) with r^2 weight, 0.086-0.19 with line weight. con_H
  does carry the matter term (otherwise about 1). So the initial top-hat data already sit at or
  above the bound of SCOPE section 3 on every mesh, falling only slowly with h (A 0.22, B 0.12, C 0.105).
- Q6 confirmed: T4 mesh-C half fails as written (|ddet(C-d0.42)| = 0.0095 > 0.0075 with v2, 0.030
  and 0.062 with v3, v1); T5 fails (|0.0403 - 0.0166| = 0.024 > 0.02).
- Q7 NOT REPRODUCED / not checkable with my reader: at the tab output nearest the first detection
  my line reader finds no marginally trapped sphere on the x line in any B member or C-d0.42 (the
  outgoing expansion stays positive, minimum about +0.1 for B-d1.00); two M later it finds one with
  a mass 1-4 per cent BELOW the finder's (B-d0.42 0.3811 vs 0.3942 at 47.75). My line reader is
  second order on M/32 (V0e: 3e-3 off in location at 10 cells across the throat; here 5 cells), so
  I cannot confirm or refute the 0.3-1.5 per cent claim.
- Q8: the envelope's proper time at the first detection is 0.5-0.6 M larger than the coordinate
  time and 2.8 M larger than tau_det (B-d0.42: 46.50 against tau_det 43.69); see the report for
  what this means for the time measure of SCOPE section 3.

## Entry 4, 2026-11-25 13:24Z: prediction for the mass time series (rerun of vthresh.py with fig_vthresh_masses)

The claimed C-d0.42 median +2.4e-2 is over "t 46.1-47.2 and 50.9-51" (README). My dm(t) of C-d0.42
inside 46.1-47.2 stays within [-1e-2, +1e-2] (my whole-window median +1e-3, bracket half-width
5e-3) [JUDGEMENT]; refuted by values near +2.4e-2 there. The line MOTS masses after the first
detection lie 1-4 per cent below the finder in every shown member.

### Entry 4 outcome (registered run A-20261125-131745-5388fde; fig_vthresh_masses.png looked at)

PREDICTION PARTLY REFUTED. C-d0.42's dm(t) is not within +-1e-2 throughout 46.1-47.2: from the
first find to 46.35 my exact mass on the slice is low (the outermost exactly trapped tracked shell
lies inside the core edge, m about 0.36) and dm reaches +7.8 per cent (median +4.1e-2 over the 9
finds there); from 46.35 to 47.2 the median is -2.2e-3, from 47.2 to 50.9 +1.8e-3. Over the README's
window (46.1-47.2 and 50.9-51, 37 finds) my median is -1.5e-3, not +2.4e-2. The B members show no
such excess: the largest dm in the first M after detection is +0.6 per cent (B-d1.00), and -0.2 to
-1.2 per cent at delta_c <= 0.5; later medians -9e-3 to +2e-3.
Line MOTS against the finder (all tab outputs after the first detection with a MOTS on the line and
a find within 0.04 M): C-d0.42 median -0.63 per cent (range -0.06 to -0.84), C-R1.25 -0.02 per cent;
B members -0.9 (B-d1.00) to -4.8 per cent (B-d0.35), growing as the horizon's coordinate radius
shrinks (5 cells of M/32 at threshold). The second half of the prediction holds for B, not for C.

## Entry 5, 2026-11-25 13:23Z: after VERIFIER-C18.md sections 1-6 were committed (0e38a43f)

Read the lead's material (CHECKLIST C1-C3, C7, C8, C18; threshold_ball entries 4 and 11 outcomes;
REVIEW-wave3 rows). Entry 4 of threshold_ball measures the first-detection excess against "the exact
mass of the shell at their radius", not against the outermost exactly trapped shell that DESIGN 4
uses for dmmed. One measurement made after reading, no prediction (the reference was not mine
before): run A-20261125-132256-b73f108, finder mass against the shell at the finder's coordinate
radius (v2 label): +1.0, +1.6, +0.2, +2.9, +2.1, +5.4, +20.1 per cent for B-d1.00 ... B-d0.35 (the
last at an isolated find), +3.1 and +0.75 (A), +1.5 (C-R1.25), +7.3 (C-d0.42; entry 11 gives 11.6);
against the core edge's exact mass -1.7 to +0.9 per cent on B, -0.8 per cent on C-d0.42. Section 7 of
the report compares.
