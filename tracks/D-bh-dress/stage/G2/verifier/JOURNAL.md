# JOURNAL of the fresh G2 verifier (Track D, checklist item C17)

Helper package `stage/G2/verifier/` (batch 26, 2026-11-25 night; decision 0044 item 1).
Newest at the bottom. Units M = initial puncture mass. Readers and reference are my own
(`tools/`); the package's scripts (`g2long/tools`, `g2runs/tools`, `flux_tools`) are not run
or imported. Inputs: the registered card outputs under `scratch/D-bh-dress/<run_id>/` and the
initial-data runs (particle files) only.

## Entry 0 (2026-11-25 22:15 PST, before any recomputation): sources, criteria, predictions

Read before writing this entry: CLAUDE.md; coord/CHARTER.md to "Owners" and the sheet of
Track D (9.7); decision 0044; scope/SCOPE.md sections 3-5; g2long/JOURNAL.md entries 1-4
(criteria N, G and predictions R1-R5), 6 (FV4, FE4, FK, FF4: P1-P14), 8, 10 (FN4, FNQ, FL16:
N1-N4, Q1-Q3, L1-L4); flux_tools/JOURNAL.md entries 4 and 7 (criterion (iii), D1-D4);
flux_tools/README.md section ES-F (construction); stage/G2/EVIDENCE.md and STAGE_REPORT.md
(claims; the report's Result column was seen while reading the claims). NOT read: the
outcome entries 5, 11-27 of g2long/JOURNAL.md, stage/REVIEW-wave3.md, CHECKLIST.md.
Predictions of the lead were committed before the runs: entry 1 at 53afc1a (12:29 PST
11-21, R1 registered 12:31), entry 6 at bd47394 (17:59 11-22, FK/FF4/FE4/FV4 registered
18:27), entry 10 at fdca920 (05:09 11-24, FN4 05:41), entry 15 at a2cbe28 (09:27 11-24,
FNQ/FL16 09:27) [VERIFIED from git log and run ids].

Criteria as written (g2long entry 1):
- N: max over 100 <= t <= 500 M of |D_ES1L - D_V1L| <= max(2 F_V(500), 1e-4), D_X(t) =
  M_X(t) - M_X(100 M), F_V(T) = max |D_V1L| on [100, T]; M_X from horizon_summary column 3,
  unique times. At M/16 and M/4 the same on 100-300 M (H3, P5).
- G: (iii) bins of 10 M of tau_rem (>= 20 removals), median of M_AH(first sample >= t_rem) /
  M_LTB(tau_rem) - 1 within +-0.01 for tau_rem <= 650 M (+-0.02 for N/4, Q1); D2 for t >= 20
  M: F_rem - 3e-3 <= M_AH - M_ctrl <= F_sph + 3e-3, F_rem = sum m E_K over removals (reasons
  2, 3), F_sph = net inward m E through sphere 1 (acc.hst) plus the content at t0.

My reference (V1). The ES-F slice is Schwarzschild of mass M in space (psi = 1 + M/2rbar),
dust with u_i = 0 and K^i_j chosen so that every shell has LTB energy E = -M/R0, i.e.
(dR/dtau)^2 = 2m/R - 2M/R0 with m = M + D(R0) (README ES-F; I re-derive: at t = 0 the shell
moves with dR/dtau = -R K_T = (2D/R)^(1/2), so 2E = 2D/R0 - 2m/R0 = -2M/R0). Cycloid
R = (m R0/2M)(1 - cos eta), tau = (m/(2M/R0)^(3/2))(eta - sin eta) + const; the shell starts
at eta0 (expanding branch, 1 - cos eta0 = 2M/m) and reaches R = 2m at etaH on the collapsing
branch (1 - cos etaH = 4M/R0). Rest mass and Misner-Sharp mass per particle: dm = m_rest
(1 - 2M/R0)^(1/2) (dust at rest in the slice, dR/dl = (1 - 2M/R)^(1/2)). I compute m(R0) as
M + the cumulative lattice sum over the particle file sorted by areal radius R0 = rbar psi^2.
- V1a (closed form): radial fall from rest at R_max in Schwarzschild: tau(R_max -> 0) =
  (pi/2) (R_max^3/2m)^(1/2); my cycloid gives it to 1e-12 relative, and a direct RK
  integration of d^2R/dtau^2 = -m/R^2 from (R0, (2D/R0)^(1/2)) gives tau_H to 1e-8.
  Refuted (reference not usable) above 1e-6.
- V1b: my lattice m(R0) at the outer edge equals M + 2.7386545 (the data maker's lattice
  Misner-Sharp sum, esf.json of D-20261121-203042-82deeec) to 1e-9, and my M_LTB(tau) at
  tau = 25, 50, 100, 200, 300, 400, 600 M lies within 2e-4 of the data maker's continuum
  numbers (1.0062, 1.0218, 1.0655, 1.1711, 1.2815, 1.3904, 1.5990) [the lattice differs
  from the continuum by one lattice spacing of R0 at most: dm/dR0 h ~ 4 pi R^2 rho h ~
  1e-4 at R0 ~ 30 M]. Refuted above 1e-3. tau_H(R0) monotonic.

V2 null test (own reader of horizon_summary, failure signature NaN or a bit-identical
repeat of the line before in columns 3-12):
- V2a I reproduce the lead's 2.28e-4 (M/8, 100-500 M), 1.99e-4 (M/16, 100-300 M), 4.57e-3
  (M/4, 100-300 M) to three digits, and 2 F_V(500) = 2.51e-4 at M/8. N holds at M/8 and
  M/16 and fails at M/4. Refuted (claim not reproduced) if any differs by more than 2 in the
  third digit or the verdict changes.
- V2b no failed search after t = 20 M in any of the six summaries; repeats at t < 20 M
  (as the 0.5 -> 1 M repeat of ES-FL seen when choosing the reader) are allowed and listed.

V3 growth criterion G on ES-FL (M/8), FK (N), FN4 (4N), FNQ (N/4), FL16 (M/16), FF4 (M/4),
controls V-1L, V-1L16, V-1L4 (each on its own mesh):
- V3a (iii) max |median| per member: ES-FL 0.62, FL16 0.485, FK 0.249, FN4 0.239, FNQ 0.290,
  FF4 0.685 per cent (lead); I reproduce each to +-0.02 per cent with my lattice M_LTB and
  my removal reader (duplicates of rewritten segments dropped by keeping, for each tag, its
  last record). Every bin within +-1 per cent (+-2 per cent N/4). Refuted if a member's max
  differs by more than 0.05 per cent or a bin leaves the band.
- V3b D2 holds at every finder sample after 20 M in every member with its own control.
- V3c D1 closure at the end (control-subtracted) within [0, +8e-3] for ES-FL (F3); F4:
  removed m E_K at 500 M in 0.60-0.70 for ES-FL. M_AH(end) of ES-FL in [1.56, 1.72] (F2).
- V3d (iii) medians of ES-FL step up after tau_rem ~ 285 M (+0.2 to +0.6 per cent) and those
  of FK do not (P9 as written: FK's medians for tau_rem 285-500 M at +0.25 +- 0.15 per cent).

V4 convergence (C2):
- V4a particle number at t = 100, 200, 300, 400 M: |M_4N - M_N| <= |M_N - M_N/4| at all four
  (lead: 4 of 4); the rms over a window of the two differences has ratio between 1.5 and 3.5
  (2 for N^(-1/2) noise). Removed m E_K of N/4 within 1 per cent of N at 100-400 M.
- V4b mesh: |DeltaM_16 - DeltaM_8| with DeltaM = M_AH(t) - M_AH(20 M) at 100, 200, 300 M
  below 5e-4 (lead 4.4e-4, 1.2e-4, 8.6e-5), and |DeltaM_8 - DeltaM_4| larger at all three.
- V4c exterior region norms (region.hst of FNQ and FN4): ratio FNQ/FN4 between 2.5 and 6
  on the shells outside the horizon (N^(-1/2) noise gives 2 for 16x particles? no: 4N/(N/4)
  = 16, sqrt 16 = 4; so 4 +- 1.5), falling toward 1 only where the deposit is deterministic.

V5 ES-FL against FK: identical M_AH (to 3e-4, P7) up to 219 M; ES-FL's dust removals switch
from reason 3 to reason 2 near t = 219 M when the horizon's minimum radius passes
4 x 0.8 = 3.2 M (horizon_summary column 12); FK keeps reason 3 (4 x 1.6 = 6.4 M, P8).
Refuted if the reason switch in ES-FL is more than 5 M away from the time minradius crosses
3.2 M, or if FK removes dust by reason 2.

V6 early removals in FK and FN4 (the lead's TO VERIFY). My expectation before looking
[JUDGEMENT, p ~ 0.5 each way]: the particles' proper time is correct (tracers will follow
the exact cycloid R(tau) to 1e-3 in R), and the early removals are real early removals:
after ~235 M, with excision kept on, the reason-3 removal surface (0.8 times the horizon's
coordinate radius, or a sphere of initial_radius) lies outside the exact horizon of the
shell being removed. Discriminating test: for tracers of group R0 = 28 M (exact tau_H =
354.2 M, crossing after 235 M) compare the areal radius from trajmet (R = r sqrt(gamma_tt),
gamma_tt the tangential component) with my cycloid at the same proper time; if R(tau)
follows the cycloid and the removal happens at R > 2 m(R0), removal is early; if R(tau)
lags by ~0.5 M of tau, the clock is off. Effect on G: (iii) shifts by at most dM/dtau x
0.7 M ~ 8e-4 relative, inside +-1 per cent; D2 by about 1e-3, inside 3e-3. So G does not
depend on it; D3 (diagnostic, bound 3e-4) can.

## Entry 1 (2026-11-25 22:18 PST): outcome of V1 (run D-20261126-061541-31e3b4e); prediction V1c

V1a HELD: the cycloid reproduces the closed-form fall time (pi/2)(R_max^3/2m)^(1/2) to
2e-16, a quadrature of dtau = dR (2m/R - 2m/R0)^(-1/2) to 4e-13, and a DOP853 integration
of d^2R/dtau^2 = -m/R^2 from the expanding start to 3.6e-12 (tau_H and R(tau)); max 3.6e-12.
V1b mixed: the lattice Misner-Sharp sum at the outer edge equals the data maker's
2.7386545133 to 2e-12 (N), 1e-11 (4N), 3e-13 (N/4): HELD. Particle counts 850724 (N),
3402772 (4N), 213012 (N/4), 140 tracers in each (14 per radius, ten radii); u_i = 0 for
all. tau_H(R0) of the lattice monotonic in R0 in all three. But my lattice M_LTB(tau)
(inclusive cumulative sum: m(R0) counts every particle with R0' <= R0) lies 2.7e-4 to
5.3e-4 above the continuum numbers for N (4N 2.4e-4, N/4 up to 1.05e-3): the 2e-4 bound
FAILED for N, not refuted (below 1e-3); N/4 above 1e-3. Reason [JUDGEMENT]: the inclusive
sum counts the particle's own lattice shell (up to 48 equal-radius points of a cubic
lattice) into the mass inside it, which a continuum shell does not feel; the tracers'
tau_H at R0 = 28 M move with it (353.88 N, 354.28 4N, 354.75 N/4 against the continuum's
354.24). The lattice reference is therefore noisy at the level of the early removals
(0.4-0.7 M), and cannot by itself decide V6.

V1c (prediction before the rerun): an independent continuum from the slice the code
actually evolves: the table esf.tab gives K_T(rbar), and the construction says K_T^2 =
2 D(R)/R^3, so m_tab(R) = M + R^3 K_T^2 / 2 with R = rbar psi^2. Expected: m_tab at the
outer edge = M + 2.7386556 (D_tot of esf.json) to 1e-6; M_LTB from m_tab equals the data
maker's continuum numbers to 1e-5 at the nine tau; tau_H(R0 = 28 M) = 354.24 +- 0.01;
the lattice with half-weight for its own shell (midpoint sum) within 2e-4 of m_tab
everywhere in 5 < R0 < 55 M. Refuted (the table and the data maker's continuum are not the
same slice) above 1e-4 in M_LTB.

V1c first reading (run D-20261126-061754-1089797): m_tab at the outer edge = M + 2.7386556250
= D_tot exactly; M_LTB from the table equals the data maker's continuum to 1e-6 at tau =
100-600 M; but at tau = 25, 50 M and for the tracers at R0 = 6, 10 M my table reading was
wrong (14.8, 33.7 against 15.9, 39.6): a defect of my reader, found by printing m_tab
against the lattice: the areal radius rbar psi^2 is not monotonic inside the throat
(rbar < M/2), so the interpolation in R mixed the two branches. Fixed (table restricted to
rbar >= M/2); rerun with the same prediction.

### Outcome of V1c (run D-20261126-061848-ed8f297; v1_reference.png looked at)

HELD in its main part: the continuum of the evolved table (m = M + R^3 K_T^2/2) gives
m(edge) = M + 2.7386556250 = D_tot exactly, M_LTB(tau) equal to the data maker's continuum
to 1.9e-8 at all nine tau (25-600 M: 1.0062, 1.0218, 1.0655, 1.1168, 1.1711, 1.2263,
1.2815, 1.3904, 1.5990), tau_H monotonic, and the tracer crossings 15.869, 39.613,
156.333, 354.241, 727.735 M (R0 = 6, 10, 20, 28, 36 M) as esf.json. So the reference of
criterion (iii) (esf_growth.csv) is reproduced independently from the slice the code
evolved [VERIFIED]. FAILED: "half-weight lattice within 2e-4 of m_tab": the largest
difference over 5 < R0 < 55 M is 2.2e-3 (N), 1.7e-3 (4N), 7.6e-3 (N/4); the lattice
point-counting noise in the mass inside a particle's own radius is larger than I guessed.
In crossing time it is an rms of 0.44 M (N), 0.24 M (4N), 1.34 M (N/4) between the
half-weight lattice tau_H and the continuum tau_H of the same particle. Consequence for
V6: a single particle's 'exact' crossing time is defined only to ~0.4 M (N) if the
dynamics feel the lattice mass inside it; I use the continuum (table) tau_H as the
reference of record and the lattice one as the second reading.

## Entry 2 (2026-11-25 22:24 PST): outcome of V2 (run D-20261126-062005-99c2399; v2_null.png looked at)

V2a HELD, reproduced to the digits quoted: M/8 max |D_ES1L - D_V1L| on 100-500 M = 2.283e-4
(at t = 256.5 M) against max(2 F_V(500), 1e-4) = 2.506e-4 (F_V = 1.253e-4): N holds, margin
9 per cent. M/16 on 100-300 M: 1.986e-4 (t = 243 M) against 2.685e-4 (F_V16 = 1.342e-4):
holds. M/4 on 100-300 M: 4.572e-3 (t = 299 M) against 3.952e-3 (F_V4 = 1.976e-3): the
criterion's pass condition FAILS at M/4. Nuance not in the lead's wording: N's own
refutation clause (|D_ES - D_V| > 3 max(F_V, 5e-5) = 5.93e-3 over more than 50 M) is not
met at M/4, because the M/4 vacuum control drifts by -2.0e-3 itself; the M/4 null test is
a failure of the pass condition by 16 per cent against its own floor, and a factor 20
against the M/8 result (P5 as written is refuted: it predicted 1e-4 to 4e-4).
The picture: at M/8 and M/16 the bubble-minus-vacuum difference rises to +1-2e-4 between
100 and 160 M and then stays flat (M/8 at +7e-5 from 300 to 500 M), the same curve at both
meshes, no trend; at M/4 vacuum and bubble separate linearly (vacuum -2e-3, bubble +1.5e-3
by 175 M).
V2b HELD: failure signature (NaN or bit-identical repeat of columns 3-12) in the 13
summaries only at t <= 5 M (V-1L, ES-1L 0.5 M; ES-FL, FK, FN4, FNQ, ES-F 1 M; V-1L4,
ES-1L4 1, 2, 4 M; FF4 0-5 M with 4 non-finite masses); none after 20 M in any; dropping
failed lines leaves N unchanged. All horizon numbers here are made without the finder's
diagnostics (no status files).

## Entry 3 (2026-11-25 22:23 PST): outcomes of V3, V4 (in part), V5, first look at V6 (run D-20261126-062152-b7144de; v3_growth.png looked at)

Reader checks: the rest mass in every dust removal record equals the particle file's at its
tag (max relative difference 0: tag = index in the file, all six members). Duplicates of
cut segments dropped by keeping each tag's last record: FK 34286 of 154190 (time ran
backwards 6 times), FN4 75972 of 555012 (4), FL16 3208 (3), FF4 22166 (2), ES-FL and FNQ 0.

V3a HELD, every number reproduced to the three digits quoted, with my table continuum as
M_LTB (lattice reference in brackets): max |bin median| of (iii) ES-FL 0.620 per cent (0.596),
61 bins to tau_rem 605 M; FL16 0.485 (0.472), 38 bins to 375 M; FK 0.249 (0.216), 50 bins;
FN4 0.239 (0.235), 50; FNQ 0.290 (0.278), 50 (band 2 per cent); FF4 0.685 (0.703), 60 bins.
No bin outside its band in any member. Overall medians +0.52 (ES-FL), +0.21 (FK), +0.22 (FN4),
+0.21 (FNQ), +0.08 (FL16), -0.08 (FF4) per cent.
V3b HELD: D2 at every finder sample after 20 M: ES-FL 960 samples (smallest lower margin
3.3e-3 at 187.5 M), FK 760 (3.0e-3), FN4 760 (3.9e-3), FNQ 760 (2.1e-3 at 393 M), FL16 1120
with V-1L16 (2.9e-3), FF4 280 with V-1L4 to the control's end at 299 M (2.1e-3). Upper side
never close (F_sph runs far ahead; >= 1.2e-2).
V3c: D1 closure of ES-FL at 499.5 M: raw +1.80e-2, control-subtracted +9.4e-3: OUTSIDE the
predicted [0, +8e-3] (F3's D1 part failed as written, by 1.4e-3). FK +2.2e-3, FN4 +2.6e-3,
FNQ +2.7e-4 (control-subtracted, 399.5 M). F4 HELD: removed m E_K of ES-FL at 500 M 0.601
(in 0.60-0.70). F2 (M_AH(500) of ES-FL in [1.56, 1.72]): the summary ends at 499.5 M; M_AH
at 400 M = 1.4920 (FK at 300 M 1.3708); not re-judged further.
D3 as written: ES-FL, FK, FN4, FL16 no violation; FNQ 8352 violations, the first at t_rem =
221.6 M, none before 219 M (the lead's 8352 of 29984 reproduced exactly); FF4 1704, all
before 219 M, the first at 7.75 M (early removals at M/4).
V5 HELD: ES-FL's last reason-3 dust removal at 218.9 M, first reason-2 removal after 50 M at
224.0 M, horizon minradius >= 4 x 0.8 M first at 219.5 M (FL16 220.0 / 224.3, FF4 225 /
229.8); FK and FN4 remove dust only by reason 3 to 400 M (minradius 4.53 M at the end < 6.4
M). FK equals ES-FL: M_AH at 100 M identical to 15 digits, at 200 M 2.2e-7 apart, at 219 M
7e-11; removed m E_K identical at 100 and 200 M (0.105293, 0.239049). The (iii) step of
ES-FL (+0.2 -> +0.6 per cent at tau_rem ~285 M) is absent in FK, FN4, FNQ, which keep
excision: P9 holds; FL16 shows the same step at the same place (its excision also ends,
220 M), FF4 too (225 M).
V4a (part): removed m E_K at 100/200/300/399.5 M: N 0.10529/0.23905/0.36807/0.48921, 4N
0.10462/0.23950/0.36857/0.48936, N/4 0.10439/0.24023/0.36978/0.49060: N/4 within 0.86 per
cent of N (largest at 100 M), 4N within 0.64 per cent: as claimed.

V6 first look (D4 with my continuum tau_H): ES-FL 0.23 per cent of dust removals before the
exact crossing (none before 219 M, min -0.084 M); FK 29.5 per cent (none before 219 M; 68.5 per
cent of those after 235 M; min -0.36 M); FN4 34.5 per cent (3.45 per cent before 219 M; min
-0.66 M); FNQ 41 per cent (min -0.67 M). These reproduce the lead's numbers. The panel shows
that tau_rem - tau_H falls SECULARLY with time in every member, from about +0.3 M at t ~ 50 M
to about 0 at 200 M and -0.2 M at 400 M in FK and FN4 (excision kept); ES-FL jumps up after
219 M only because removal moves deeper (lapse rule). The tracers make the same point
without lattice noise: group R0 = 28 M (exact tau_H = 354.24 M) is removed in FK at t = 278.0
M at tau_H - 0.39 M (reason 3), in FN4 at -0.16, FNQ -0.63, while in ES-FL the same tracers
are removed 4.4 M of coordinate time later by the lapse rule (alpha < 0.05, deep inside)
at only tau_H + 0.06 M. A particle deep inside the horizon with 0.06 M of proper time since
its exact crossing is not on the exact trajectory: it is ahead of the LTB clock.
My JUDGEMENT before the next test: excision does not remove dust outside the horizon; the
particles reach the horizon earlier in proper time than the exact solution says, by a
drift that grows with time (~0.1-0.15 per cent of tau). Either the code's proper time runs
slow (clock) or the shells fall faster (dynamics: an initial velocity deficit of ~0.14 per
cent, or a smaller bound energy |E|, would do it; a mass excess would do the opposite:
d tau_H / d ln m = +530 M at R0 = 28 M).

### Prediction V6b (before the run): tracer trajectories (traj.bin, trajmet.bin) of FK and ES-FL
(1) Clock: integrating dtau = alpha / W dt (W = (1 + gamma^ij u_i u_j)^(1/2)) along each
    tracer's samples reproduces the code's proper time to 1e-4 relative at t = 250 M
    [p ~ 0.8]. If it does not, the clock is the cause.
(2) Dynamics: the areal radius of the R0 = 28 M tracers, R = r (e_t.gamma.e_t)^(1/2) from
    the tangential metric component, against my cycloid at the same proper time: R_sim < R_LTB
    by a growing amount, and the maximum areal radius R_max below the exact m R0/M = 37.55 M
    by 0.02-0.1 M [p ~ 0.6]. At R0 = 20 M (exact R_max 22.47 M) the same with a smaller
    deficit. Refuted (dynamics exact) if R_max agrees to 0.01 M and R(tau) to 0.02 M up to
    the horizon.
(3) Either way G is untouched: the shift in (iii) is dM/dtau x 0.5 M ~ 6e-4 = 0.05 per cent.

## Entry 4 (2026-11-25 22:27 PST): outcome of V6b (run D-20261126-062436-72c04d3; v6_tracers.png looked at)

(1) Clock HELD: the code's proper time of the tracers equals my integral of alpha/W dt along
    the trajectory samples to 6e-7 relative at t = 250 M for R0 = 28 M (5e-7 at 36 M, 5e-6 at
    20 M, 6e-5 at 10 M where the samples cross the horizon early); in absolute terms below
    2e-4 M everywhere except at the last samples inside the horizon. The clock is not off.
(2) Dynamics: HELD (deviation found). My areal radius from the tangential metric component
    reproduces R0 at t = 0 to 2e-6 M (the measure works). The tracers at R0 = 28 M turn around
    below the exact R_max = 37.55 M (median -0.013 M ES-FL/FK, -0.021 M FN4, -0.004 M FL16)
    and reach a given areal radius on the way in EARLIER in proper time than the cycloid:
    at R = 9.4 M by 0.78 M (ES-FL, FK), 0.55 M (FN4), 0.40 M (FL16); at R0 = 20 M by 0.17,
    0.10, 0.045 M; at R0 = 10 M by less than 0.01 M. The offset builds up before and around
    turnaround (it is nearly the same at 0.75 R_max and at R = 4 M on the way in) and shrinks
    with the cell size (M/16 about half of M/8) and with the particle number (4N about 0.7 of
    N). R_sim - R_LTB reaches -0.1 M at tau = 300 M for R0 = 28 M at M/8.
Verdict on the open point (6): the dust is not removed before it crosses the horizon of the
run; it reaches that horizon early because the numerical shells run ahead of the exact
LTB solution by ~0.2 per cent of their proper time (0.5-0.8 M at tau ~ 350 M), an error of
the evolution that converges with mesh and particle number. The comparison clock is
right; the comparison reference (the exact solution) is what the run departs from. In ES-FL
the same early arrival is hidden because after 219 M removal happens deeper (lapse rule).
(3) Effect on G (estimate, JUDGEMENT): an early arrival by 0.7 M shifts the (iii) ratio by
dM/dtau x 0.7 / M_AH ~ 1.1e-3 x 0.7 / 1.35 = 6e-4 (0.06 per cent of the +-1 per cent band);
D2 by dF/dt x ~0.5 M ~ 6e-4 against margins of 2.1e-3 or more. It moves D3 (bound 3e-4) and
D4, which are diagnostics, not G.

V4 prediction stands as in entry 0 (V4a-c).

## Entry 5 (2026-11-25 22:28 PST): outcome of V4 (runs D-20261126-062609-bb28de7 and, with envelopes, D-20261126-062637-6fbe1c9; v4_conv.png looked at)

V4a HELD: |M_4N - M_N| <= |M_N - M_N/4| at 100, 200, 300, 399.5 M (4 of 4): differences N - N/4
= +1.43e-3, -3.9e-4, +3.9e-4, +5.9e-4; 4N - N = -3.7e-4, +3.6e-4, -9e-6, +4.9e-4. Caveat: single
samples are noisy (sample standard deviation of N - N/4 1.1e-3, of 4N - N 4.4e-4 over 20-400 M),
so the four-time ordering is weak evidence by itself; the window rms is the robust form:
ratio rms(N - N/4)/rms(4N - N) = 2.51, 2.63, 2.32, 2.42 on 20-100, 100-200, 200-300,
300-399.5 M (2 for N^(-1/2) noise; lead 1.9-3.1 on its own windows). Removed m E_K: N/4
within 0.86 per cent of N, 4N within 0.64 per cent (entry 3).
V4b HELD as stated, with a caveat on the sampling: Delta M_16 - Delta M_8 (from 20 M) =
4.40e-4, 1.16e-4, 8.6e-5 at 100, 200, 299 M (lead's numbers to the digit); with own vacuum
controls 3.6e-4, 2.9e-5, 1.3e-5. But these are single samples: over 20-299 M the difference
reaches 1.0e-3 in absolute value and its mean over 250-299 M is +5.8e-4 (a slow upward
trend is visible). Delta M_8 - Delta M_4 = -1.24e-3, -9.4e-4, -1.22e-3 (larger at all three:
L3 holds as written), mean -1.07e-3 over 250-299 M, up to 2.1e-3; with own controls -1.9e-3,
-2.9e-3, -4.0e-3. Two members in the regime, no order: agreed.
V4c HELD: Hamiltonian norm on shells, FNQ over FN4 (16 times fewer particles; N^(-1/2) noise
gives 4): [1.2 r_AH, 6 M] 3.19-5.14 (median 4.05), [6, 12] 3.28-4.81 (4.07), [12, 30] median
2.49 before 150 M and 4.09 after, [30, 60] 0.96-4.2 (median 1.10 before 150 M, deterministic,
rising to 4 by 350 M as the dust reaches it). The lead's "3.2-5.2 on shells, [30, 60]
deterministic to 150 M" is reproduced for the two inner shells.

Card-hours against the cost predictions (manifests `runs/<id>/manifest.json`, resources.gpu_hours):
V-1L 2.24 (V4 2.0-2.6 held), ES-1L 2.49 (E4 held), ES-FL 2.60 (F6 held), V-1L16 3.00 and
ES-1L16 3.33 (H4 ~3.0, ~3.4 held), FV4 0.59 (P4 held), FE4 0.826 (P6 0.5-0.8 FAILED narrowly),
FK 2.70 (P11 1.8-2.4 FAILED), FF4 1.34 (P14 held), FN4 3.19 (N4 held), FNQ 1.90 (Q3 held),
FL16 3.66 (L4 held).

Predictions of the lead that my readings judge as FAILED as written (all on record already
or listed here): V3 (F_V(500) <= 1e-4; 1.25e-4, not refuted), E2 (<= 1e-4 on 100-300 M and
<= 2e-4 on 100-500 M; 2.28e-4 at 256.5 M), H1 (M_V1L16 - 1 in [3e-5, 4e-4]; -2.7e-4 at 100 M),
H2 (F_V16(300) <= 5e-5; 1.34e-4), P2 (M/4 late offset in [+4e-3, 2.5e-2]; -7.9e-3: refuted),
P5 (M/4 null difference 1e-4 to 4e-4; 4.57e-3: refuted), F2 at 400 M (1.497-1.530; 1.4920, not
refuted), F3 (overall (iii) median +0.1 to +0.4 per cent; ES-FL +0.52; D1 in [0, 8e-3];
+9.4e-3), F4 ("every removal by reason 3"; 84496 of 147840 by reason 2 after 219 M), P6, P11
(costs), D3 at N/4 (8352 violations after 221 M) and at M/4 (1704, before 219 M), and N at
M/4 (pass condition). Held: N at M/8 and M/16, G in all six members, H3, P7-P10, P12, N1-N3,
Q1-Q2, L1-L3, F4 (removed sum), F5 (no lost horizon).
