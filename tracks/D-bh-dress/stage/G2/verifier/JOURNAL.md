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
