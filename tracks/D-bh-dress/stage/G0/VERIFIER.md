# Independent verification of the G0 and G1 material of Track D (wave 2)

Verifier: a helper of D-bh-dress that produced none of the material checked, working as a
fresh reader. Read first: `scope/SCOPE.md` (the scoping text; it names the claims),
`einstein_straus/DERIVATION.md`, the test scripts and inputs, and the raw outputs under
`scratch/D-bh-dress/`. The track's summaries (STATUS, HANDOFF, JOURNALs, stage reports,
`analysis/lead_checks/`) were read only after the verdicts below were written (section 3).
Predictions and outcomes, including the failed ones: `JOURNAL.md` in this directory. Every
number below carries a run id; my runs are listed in `README.md`. Labels as in the brief.

Verdicts: **CONFIRMED** (recomputed independently, rerun, and an attempt to break it did
not), **NOT CONFIRMED** (what could not be checked and why), **WRONG** (with the evidence).

## 1. Claims

### C1. The vacuum-bubble (Einstein-Straus type) slice of D-pre-1 is a valid exact reference — CONFIRMED (for the data set that exists)

Claim (SCOPE 3.4, 4, 5; DERIVATION 1-6): the format-2 table plus a puncture of bare mass
m_p = M/a satisfies the constraints; the Misner-Sharp mass is M between throat and wall;
the dust is marginally bound Einstein-de Sitter with H^2 R_w^3 = 2M; no anti-trapped sphere;
the mass inside the comoving wall stays M; R_w = (2/eps^2)^(1/3) M, wall speed (2 eps)^(1/3).

- Own recomputation from the 6096 table rows alone (no use of `es_model`), run
  `D-20261115-170002-8cefc3e`, figure `figs/v1_es_slice.png`: Misner-Sharp mass
  1 +- 2.7e-10 in the vacuum transition 4 < R < 35.5 M and 1 +- 3e-14 in the time-symmetric
  part and on the inner sheet; in the plateau m - H^2 R^3/2 within +-9.5e-13, i.e. the
  "dust mass removed = M" matching is exact (effective sharp-wall radius 40.04 M); H from
  KT, from KL and from the Hamiltonian density agree to 3e-13; radial momentum residual of
  order 4.00 (transition) and 3.90-3.99 (smooth dust edges) over h = 0.16 ... 0.02 M; no
  row with both null expansions positive; throat at rbar = 0.52 (grid) against b/a =
  0.5243; u = a - 1 constant inside rbar = 3 M, so M = a m_p = 1 (m_p = M would give a hole
  of 0.9766 M). Exact reference curves of `es_reference.csv` equal my closed forms
  R_w(tau) = (R_in^(3/2) + (3/2) sqrt(2M) tau)^(2/3) and a(tau) = (1 + (3/2) H tau)^(2/3) to
  7e-16. Particle file: 140 tracers of mass 1e-30, dust from rbar = 36.23 M outward, all
  u_i = 0, total dust mass equal to M_total - M to 2.8e-8.
- Rerun of the test said to support it, on the release executable: the t = 0 code check of
  `code_t0_check.py` on `.work/build_cpu_v03` (core-v0.3) reproduces the wave-1 branch-build
  dumps bit for bit (max |difference| = 0 in E, chi, H, M_i, Khat, alpha at dx = 1 and
  1/2 M), run `D-20261115-170224-924d1d9`, figure `figs/v1b_code_t0.png`; mid-transition
  |H| 8.4e-9 -> 1.4e-10 and inner-dust-edge |M| 1.1e-5 -> 1.1e-6 (orders from two
  resolutions only).
- Breaking attempts: replacing KL by KT in the transition (a wrong curvature) gives a
  momentum residual of 8.7e-4 at every spacing (the check has teeth). Scales: R_w = 60.6,
  27.1, 13.0, 5.8 M and H R_w = 0.18, 0.27, 0.39, 0.58 at eps = 0.003, 0.01, 0.03, 0.1;
  H R = 0.88 at 1.5 R_w for eps = 0.1, below the anti-trapping limit H R = 1 (my numbers,
  same run). Constancy of the mass inside a comoving dust wall is Birkhoff plus p_r = 0
  [BACKGROUND]; I did not re-derive the symbolic identities of `sym/` (rerun already by the
  lead in wave 1).
- Not covered: the only data set has eps = H M = 5.58e-3 (R_w = 40 M); no data set exists
  at the G2 values eps = 0.03 or 0.01, where the transition region 4 M < R < R_in is much
  narrower (R_in about 9 M at eps = 0.03 with the same w_in = 4 M). Near the puncture the
  code's |H| is O(1) and does not converge at dx = 1/2 M (throat unresolved), as stated.

### C2. The noise floor of D-pre-4 is small and converges — CONFIRMED for the secular drift; the floor has a non-converging part

Own analysis of the raw finder output of the two card runs, run `D-20261115-171508-94e8cb1`,
figure `figs/v2_drift.png` (definitions fixed in the script before looking at the track's
analysis: 20 M running mean, t0 = 50 M):

| | M/8 (`...121313-284ec4f`) | M/16 (`...121314-284ec4f`) |
|---|---|---|
| Mbar(50 M) - 1 | +1.35e-3 | -2.6e-4 |
| max |Mbar(t) - Mbar(50 M)|, t <= 490 M | 2.95e-4 | 3.7e-5 |
| linear slope over 50-500 M (per M) | (4.0 +- 1.0)e-7 | (8.8 +- 1.3)e-8 |
| rms about the running mean | 1.5e-5 | 1.5e-5 |
| largest deviation from the linear fit | 1.0e-4 (t = 50, transient) | 7.4e-5 (t = 327.5) |
| same, windows 200-260 / 300-340 M | 7.3e-5 / 9.6e-5 | 5.5e-5 / 7.4e-5 |
| spin magnitude | < 4e-8 | < 3e-9 |

Drift ratio 7.9 (order 3.0); prediction (M/8 < 1e-3, M/16 < 2e-4, ratio >= 4) holds. But:
(i) the offset Mbar - 1 changes sign between M/8 and M/16, so it is not a convergent
sequence and its "order" is meaningless; at M/16 it is the finder setting (TESTLOG:381-383:
finder against slice 3e-4 at production settings) rather than the evolution (slice error
1.4e-5, TESTLOG:384-385); (ii) excursions at t = 200-260 and 300-340 M have the same times
and nearly the same size at both resolutions (third panel of the figure): a domain-scale
signal, not resolution error. The runs kept the +-128 M domain of the calibration input,
while the scoping cost model itself asks for L >= 0.71 T = 355 M for 500 M; a boundary
signal is the obvious candidate [TO VERIFY: the same run with L = 384 M]. (iii) The M/8
run is still in its gauge transient at t0 = 50 M (half of its 2.95e-4 is reached by
100 M). Consequence: the floor to quote for an instantaneous mass is about 7e-5 at M/16 and
it does not shrink with resolution in this set-up; the secular part is 3.7e-5 over 440 M.
k_floor over one doubling: 5.4e-5 (M/16) from the drift alone. Not checked: the M/32 run
(not made) and the finder re-search and Misner-Sharp analysis of the dumps (run
`...130954-49ed46f`), which I did not redo.

### C3. Turnaround of cold dust around a point mass in EdS (SCOPE section 4) — CONFIRMED

Own closed-form Kepler parametrisation, run `D-20261115-171532-ba23a99` (ODE check of one
orbit: turnaround time and radius agree to 7e-13): M_b,ta/(a/a_i) = 0.2627, 0.4070,
0.4997, 0.5593, 0.5641 at a/a_i = 2, 4, 10, 121.5, 1000, asymptote (4/(3 pi))^(2/3) =
0.56475 (within 1 percent from 121.5 on); turned around with the hole 1.5254 M and 2.628 M
at a/a_i = 2, 4; r_ta = 74.6 / 33.4 / 16.1 / 7.2 M (a/a_i = 2) and 187.3 / 83.9 / 40.3 /
18.1 M (a/a_i = 4) for eps = 0.003 / 0.01 / 0.03 / 0.1; d ln r_ta/d ln a = 1.33314 and
frozen-in slope -2.25033 at a/a_i = 1000; run lengths 121.9 / 466.7 M (eps = 0.01),
40.6 / 155.6 M (0.03), 12.2 / 46.7 M (0.1). Every printed number of SCOPE section 4
reproduced to its digits ("187" is 187.3).

### C4. Self-similar secondary infall gives rho ~ r^(-9/4) (D-pre-3, SCOPE 4 and 5) — CONFIRMED as the asymptote (lambda << 1e-2); the proposed G1 test of it is mis-specified

- The track's self-similar solver rerun (`selfsimilar.py --taumax 300`, run
  `D-20261115-171818-a5aefe8`) reproduces run `D-bh-dress-20261115-123813-97afeea` exactly
  (text output identical except wall times; `selfsimilar_profile.npz` byte-identical). Its
  m(lambda) has d ln m/d ln lambda = 0.741 over 1e-4 ... 1e-3 and 0.705 over 3e-3 ... 3e-2:
  the -9/4 slope is reached only for lambda = r/r_ta << 1e-2. Mean density slopes of that
  solution: -2.26 (1e-4 ... 1e-3), -2.30 (3e-3 ... 3e-2), -2.32 (0.01 ... 0.1), -2.37
  (0.03 ... 0.3), -2.35 (0.002 ... 0.5), -2.42 (0.05 ... 0.5) (my evaluation of the
  track's profile, comparison run below).
- My own radial-shell code (Newtonian, shell crossing, point seed in EdS, pure Hubble flow
  at t_i as in the scoping set-up; `verify/v4_shells.py`), a/a_i = 100, run
  `D-20261115-173149-7c6dd72`, figure `figs/v4b_compare.png`: the enclosed-mass profile
  m(lambda) = M(<lambda r_ta)/M_ta approaches the track's self-similar m(lambda) as the
  number of shells grows: median deviation over 0.02 < lambda < 0.5 of -32, -23, -14,
  -7 percent for N = 2000, 4000, 8000, 16000 (largest 13 percent at N = 16000; a 1/N
  extrapolation gives -1 to -4 percent [JUDGEMENT]); a four times smaller step changes it
  by 4 percent. The deficit is discreteness heating of the shells (7, 3, 1 percent of the
  turned-around dust outside r_ta at N = 2000, 4000, 8000). Enclosed-mass slopes over
  0.03-0.4 r_ta: -2.32 ... -2.44 in every variant, consistent with the self-similar
  solution's -2.37 over 0.03-0.3 and not with -9/4. My first prediction (-2.25 +- 0.1 over
  0.05-0.3 r_ta) failed because -9/4 is not the slope there; the first registered run
  (`D-20261115-171733-633d422`) was stopped after two variants when I changed the step rule
  (JOURNAL entries 8-10). Not reached by my code: lambda < 1e-2, where the seed (2.3 percent
  of M_ta) and the softening dominate, so the asymptote itself rests on the semi-analytic
  solution and on the frozen-in argument (C3: -2.2503 at a/a_i = 1000).
- Consequence for the plan: the G1 criterion proposed in SCOPE section 5, "the same in
  AthenaK's Newtonian mode ...: slope -9/4 +- 0.05 between 2 dx and r_ta/2", would fail for
  an exact code: the self-similar solution's own mean slope between 0.002 and 0.5 r_ta is
  -2.35. The criterion should compare m(lambda) with the self-similar solution, not a
  power law.

### C5. Capture cone: cold dust is swallowed; a bound spike needs sigma ~ 0.05-0.1 (SCOPE 4) — CONFIRMED with a 6-11 percent correction

Exact Schwarzschild effective potential, run `D-20261115-171532-ba23a99`: L_c(E = 1) = 4.000 M;
my root of V_max(L) = E^2 agrees with SFW eq. (Lcrit) (1305.2619 `SFWpaper.tex:380`) to
1.6e-15 (run `D-20261115-171534-ff5b0e9`). For a particle at turnaround radius r with
tangential speed v (static frame), the capture threshold is v_c = 0.221 at r = 16.1 M and
0.113 at 33.4 M, i.e. 0.89 and 0.94 of 4M/r (E = 0.960 and 0.976 < 1 there, so
L_c = 3.65 and 3.80 M); SCOPE's "0.12-0.25" should read 0.11-0.22. The circular speed
(1.5 M/r)^(1/2) = 0.31 and 0.21 is still above. The cold growth law: absorbed background
mass per unit a/a_i 0.095, 0.207, 0.292, 0.355 at a/a_i = 2, 4, 10, 1000, asymptote
0.35577 = 0.5648/2^(2/3) (collapse order monotonic in M_b, so no shell crossing before
capture); SCOPE's asymptote is right and its transient warning matters: at a x 4 the
hole grows by 0.83 M, not 1.42 M. Not checked: the dispersion needed for a bound spike
(sigma ~ 0.05-0.1 is a judgement; it needs the distribution of tangential speeds, which
the shell runs `...123516...` to `...130000...` address and I did not redo).

### C6. Probe-limit spike reference (D-pre-2): density vanishes at 4 M — CONFIRMED; the proposed G1 numbers "3" and "15 percent" are SFW's prose, not what the exact calculation gives

Own phase-space quadrature of a constant f in the static frame (run `D-20261115-171534-ff5b0e9`,
figure `figs/v6_spike_constf.png`): rho = 0 for r <= 4 M (1.5e-4 f0 at 4.02 M), peak
0.1695 f0 at r = 7.58 M; GS (8 Gm) peak 0.0654 f0 at 16.3 M; ratio 2.59; the 4 Gm variant
peaks 9.2 percent above the relativistic curve; quadrature converged to 5e-5; Newtonian
limit recovered (0.991 at r = 1000 M, capture cone). The track's `rho_constf_rel` agrees
with my independent quadrature to 1.4e-5 over the whole profile. SFW's text
(`SFWpaper.tex:443`: GS "a factor of three smaller at its peak", 4 Gm variant "about 15%
higher") is prose; the track's own run `D-bh-dress-20261115-123029-4df1e76` also finds 2.59
and 9.2 percent and matches the digitised SFW figure 1 peak to 0.03 percent. So the G1
numbers proposed in SCOPE section 5 ("peak ratio to Gondolo-Silk 3 and the 8Gm -> 4Gm
curve 15 percent above") would fail an exact code; they should be 2.59 and 9.2 percent (or
the digitised curve). Not checked: the Hernquist adiabatic-growth spike and the Kerr
curves, and the AthenaK stationarity runs of P2.

### C7. Definitional drift of the area mass in McVittie, d ln M_AH/d ln a = -12 (mH)^2 — CONFIRMED (leading order; 25 percent short at eps = 0.1)

sympy from the McVittie metric itself (run `D-20261115-171543-d966aba`): Misner-Sharp mass
m + H^2 R^3/2 exactly; black-hole apparent horizon R_h/(2m) = 1 + 4 h^2 + 48 h^4 (h = mH);
with H^2 ~ a^-3: d ln M_AH/d ln a = -12 h^2 - 240 h^4. Exact roots: -1.20e-3, -1.10e-2,
-0.151 at h = 0.01, 0.03, 0.1 (SCOPE: -1.2e-3, -1.1e-2; at 0.1 the leading term -0.12 is
25 percent short). The precision statement holds: a 1 percent floor gives |k| < 0.0144
over one doubling; k = 1 against k = 0 is Delta ln M = 0.693.

### C8. Compute estimate (SCOPE section 7) — the throughput model CONFIRMED where it was anchored; WRONG for the finer meshes the plan needs (M/32, M/64)

- Anchors re-read from the logs by my own parser (run `D-20261115-171545-d7e01a7`): 288,
  344, 400 blocks and 2.08, 4.71 (dx8_tight), 11.46 s per M at M/4, M/8, M/16: as stated.
  With the domain the D-pre-4 runs actually used (+-128 M) the model predicts their cost to
  3 percent (measured/model 0.968 and 0.969: 0.654 and 1.523 card-hours); SCOPE's 0.90 and
  2.01 h assumed a domain grown to 0.71 T that the runs did not use.
- Source facts: one global step from the smallest cell (`z4c/z4c_newdt.cpp:26-39`; the only
  "subcycle" in the source is the collision module's); `metric_drvts` default "stored"
  (`z4c/fastflow.cpp:89`) and `ah_exc_factor` default -1 (`particles/nrpic.cpp:118`): as
  stated.
- **WRONG: block counts beyond M/16.** The model adds 56 MeshBlocks per halving of dx_min
  (`scoping_estimates.py`, `nest_blocks`). The release executable's own tree (`-m`), run
  `D-20261115-171953-908afff`, with the calibration input's refined region (|x| < 1.5 M):
  344, 400, **3200, 4712** MeshBlocks for M/8, M/16, M/32, M/64 (model: 344, 400, 456, 512).
  From level 7 on, 2:1 nesting turns every coarser level into a shell of 448 blocks. With
  |x| < 2 M at M/64 (needed to keep the horizon on the finest level, below) it is 7848.
  With the model's own rates [JUDGEMENT, arithmetic]: D-pre-4 at M/32 for 250 M costs
  12.6 card-hours (SCOPE: 2.0); the G2 vacuum bubble at eps = 0.03, a x 2 costs 0.27 +
  3.1 + 9.1 (|x| < 1.5 M) or 14.9 (|x| < 2 M) card-hours at M/16, M/32, M/64 (SCOPE: 0.27 +
  0.59 + 1.29 = 2.2). The block counts also exceed the 2280 blocks per card used so far
  (TESTLOG:2037), so one card may not hold them.
- Horizon against the finest level: the horizon's coordinate radius grows from 1.34 M
  (t = 50 M) to 1.67 M (t = 500 M) at both resolutions (C2 run). At M/16 the finest level
  ends at |x| = 2 M (5 cells of margin at 500 M); at M/64 with the calibration region it
  ends at 1.5 M, which the horizon crosses at t = 144 M (run `D-20261115-171545-d7e01a7`).

## 2. The three weakest points of the plan

1. **The noise floor and the null test are measured in different set-ups.** The G2
   criterion compares the vacuum-bubble drift with "the D-pre-4 floor for the same
   resolution and duration", but D-pre-4 is a lone puncture in a +-128 M box with a
   precollapsed lapse, while the bubble runs have a table plus puncture, a dust ball, a
   different initial lapse and (by the model) a larger domain. The floor I measured has a
   part that does not converge (excursions of 5e-5 to 1e-4 at the same times at M/8 and
   M/16) and a finder offset that changes sign with resolution. A floor taken from another
   set-up can be smaller or larger than the bubble run's own; the comparison then proves
   little. Remedy: measure the floor in the bubble set-up itself (same mesh, domain, gauge,
   finder, with the dust removed and the puncture alone, or with the dust kept far
   outside), and fix the domain size before calling a number a floor.
2. **The convergence ladder M/16, M/32, M/64 is priced an order of magnitude too low.** The
   block count jumps from 400 to 3200 and 4712 (7848 with the horizon kept on the finest
   level): SCOPE's G2 vacuum-bubble set at eps = 0.03 is 12-18 card-hours instead of 2.2,
   the D-pre-4 M/32 run 12.6 instead of 2.0, and the current G2 budget of `REPORT.md`
   section 7 (about 19 of 30) becomes about 28 of 30 because its M/32 matter run costs
   about 12 instead of 2.86, before retries and the model's factor 1.5. G3's "three-way
   convergence" needs a different ladder (e.g. M/12, M/16, M/24, refined regions sized to
   the horizon) or several cards per run, and the 3200-7848 blocks exceed the 2280 per
   card used so far. The finest region must also grow with the horizon's coordinate radius
   (1.67 M at 500 M).
3. **Several G1 numbers are not the numbers an exact calculation gives.** The D-pre-3
   criterion "slope -9/4 +- 0.05 between 2 dx and r_ta/2" fails for the self-similar
   solution itself (-2.35 over 0.002-0.5 r_ta); the D-pre-2 criterion "peak ratio 3, 15
   percent" fails for the exact constant-f spike (2.59, 9.2 percent; the track's own run
   found the same); the capture threshold is 6-11 percent below 4M/r. Each is a criterion
   that a correct code would fail, or a judgement built on a rounded number; G1 should be
   restated against the computed references (m(lambda) of the self-similar solution, the
   digitised SFW curve), not against power laws or prose.

Smaller points: no D-pre-1 data set exists at the G2 eps; the M/8 drift run's t0 = 50 M
lies in its gauge transient; the "0.12-0.25" tangential speeds should be 0.11-0.22; the
McVittie leading-order drift is 25 percent short at eps = 0.1.

## 3. Comparison with the track's own review

Read after sections 1 and 2 were written: `stage/G0/STAGE_REPORT.md`, `EVIDENCE.md`,
`OPEN.md`, `REPORT.md` (sections 1, 4, 7, 8 and the reference table), `stage/G1/STATUS.md`,
`analysis/lead_checks/README.md`, the lead's `JOURNAL.md` and `puncture_drift/JOURNAL.md`
(by search). There is no `REVIEW.md`; the lead's re-checks L1-L6 and the note helper's
claims check (`note/tables/claims.md`, summarised in STAGE_REPORT) are the track's review.

Agreements (the track found it too):
- D-pre-1 met: same Misner-Sharp mass, a, m_p, fourth-order residuals, t = 0 code orders.
- D-pre-4 drift: +2.95e-4 (M/8) and +3.67e-5 (M/16) from 50 to 490 M, identical to mine;
  the excursions of equal size and timing at both resolutions, the boundary attribution
  untested, the floor belonging to a different set-up than the Einstein-Straus run (risks
  R3, R4; matched control V-1 planned); M/32 judged not to lower the floor
  (`puncture_drift/JOURNAL.md:273-277`).
- D-pre-2: the track's own run finds 2.59 and 9.2 percent and says so (`REPORT.md:115`).
- D-pre-3: the track's G1 status already says "r^(-9/4) only below lambda ~ 1e-4".
- Capture: `REPORT.md:44` already says "0.1-0.2 c" (SCOPE.md still says 0.12-0.25).

Differences (what this verification adds or contradicts):
1. **MeshBlock counts beyond M/16 (new, C8).** No track document checks the 56-blocks-per-
   level rule. The release executable gives 3200 and 4712 (7848) blocks at M/32 and M/64;
   the track's budget "about 19 of 30 card-hours to G2" (`REPORT.md` section 7) contains
   "G2 (b) matter, eps = 0.03, a x 4, M/16 + M/32: 4.2". With 3200 blocks the M/32 part
   alone is about 12 card-hours by the model's own rates [JUDGEMENT, arithmetic:
   3200 x 4096 x 19915 cycles / 6.4e6 + 1e6 x 19915 x 1.2e-7 s], so G2 as planned is about
   28 of 30 before retries and before the factor-1.5 model uncertainty, and the block count
   is above the 2280 per card used so far. The first runs (ES-1, V-1 at M/8 and M/16) are
   not affected.
2. **G1 criteria still carry the rounded numbers (C4, C6).** The track knows both facts but
   the criteria text was not updated: `scope/SCOPE.md:186-187` still asks for "peak ratio
   to Gondolo-Silk 3 and ... 15 percent above"; `scope/SCOPE.md:192-193` and `REPORT.md:97`
   still ask the AthenaK Newtonian mode for "slope -9/4 +- 0.05 on [2 dx, r_ta/2]", which
   the track's own self-similar solution fails (-2.35 over 0.002-0.5 r_ta).
3. **Independent normalisation of the self-similar solution (new, C4).** The track's
   self-similar m(lambda) had no independent check (the shell runs of `shells.py` are by
   the same helper). My shell code converges towards it (median deviation 7 percent at
   N = 16000, falling about as 1/N).
4. **Release executable (new, C1).** The track lists "format-2 reader only on
   core/id-extrinsic" as risk R7 and the merge as a precondition of ES-1; the release
   processor executable reproduces the wave-1 t = 0 dumps bit for bit, so R7 is closed for
   the start-time data (not for the evolution, which I did not run).
5. **D-pre-4 details (C2).** The track quotes the M/16 floor as 2.0-2.5e-5 for windows that
   end before 210 M; I add that the finder offset changes sign between M/8 (+1.35e-3) and
   M/16 (-2.6e-4), so the absolute horizon mass has no convergence order from these two
   runs, and that the M/8 run is still in its transient at t0 = 50 M. The track's ES-1
   prediction "M_AH(100 M) - M = +1.5e-3 +- 3e-4 at M/8" rests on the M/8 offset only.
6. **McVittie drift (C7).** The track does not recheck the -12 (mH)^2 coefficient; it holds
   to leading order and is 25 percent short at eps = 0.1. For the null test with matter
   (G2 (b)) the definitional term over a x 4 at eps = 0.03 is about 3.5e-3 in ln M
   (4 h^2 (1 - (a_i/a_f)^3)), below the 1-percent-of-accretion tolerance of the G2
   criterion but far above the vacuum floor; SCOPE 3.6's sentence ("no change ... beyond
   the matter that crosses the horizon") holds only after this term is subtracted or
   bounded.
7. The stage report's "D-pre-4 floor (2.0-2.5e-5 at M/16)" and my "about 7e-5
   instantaneous" are the same data read two ways (window before 210 M against the whole
   run); neither is a floor for the bubble set-up.

Items that `OPEN.md` item 3 asked a verifier to look at: SCOPE section 3 wording (checked:
restrained and consistent with 2302.07878 `:132` as quoted; see difference 6 for the matter
case); DERIVATION sections 3-4, conditions on f and a < 1 (checked on the data set: no
anti-trapped row, throat at R = 2.00003 M with W = 0 to grid accuracy, a = 0.9766 < 1; the
general proofs not re-derived); the LTB mapping with the over-massive hole (JOURNAL L5):
NOT CHECKED.
